"""Seeded, bounded zoom/pan streaming and model refresh acceptance over HTTP."""
from pathlib import Path
import subprocess,json,time,os,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/os.environ.get('CITY_TOUR_OUT','docs/previews/webgl-streaming-8');OUT.mkdir(parents=True,exist_ok=True)
server=subprocess.Popen(['python','-m','http.server','8783','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1000,'height':700});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8783/index.html?cityArt=webgl&cityQuality=low');page.locator('#newTown').click();page.locator('#pause').click();page.locator('#panelClose').click();page.wait_for_function('window.__webglTaste&&__webglTaste.samples.length>=3',timeout=60000);before=page.evaluate('__townTest.save()');rows=[];cdp=page.context.new_cdp_session(page);cdp.send('HeapProfiler.collectGarbage');heapStart=cdp.send('Runtime.getHeapUsage')['usedSize']
  sequence=[(26,26,2.1),(26,26,1),(26,26,.6),(65,15,1.8),(110,110,1),(2,2,.6),(126,2,1.8),(26,26,1)]*2
  for i,(x,z,zoom) in enumerate(sequence):
   if i in [7,15]:page.set_viewport_size({'width':390 if i==7 else 1000,'height':844 if i==7 else 700})
   frame=page.evaluate('__webglTaste.frameId');page.evaluate('(v)=>__webglTaste.focus(...v)',[x,z,zoom]);page.wait_for_function('(n)=>__webglTaste.frameId>n',arg=frame,timeout=30000);page.wait_for_timeout(80);r=page.evaluate('()=>({lod:__webglTaste.lod,selected:__webglTaste.selected,loaded:__webglTaste.loadedBuildings.length,calls:__webglTaste.drawCalls,triangles:__webglTaste.triangles,buildMs:__webglTaste.buildMs,memory:__webglTaste.memory(),canvasCount:document.querySelectorAll("#webglTaste").length})');assert r['canvasCount']==1;assert all(0<=r['selected'][k]<128 for k in ['minX','maxX','minZ','maxZ']);rows.append(r)
   if i<8:page.screenshot(path=str(OUT/f'tour-{i:02}.png'))
  assert json.loads(before)==json.loads(page.evaluate('__townTest.save()'));assert page.evaluate('__cityVisualSave()');assert not errors,errors;assert len({r['lod'] for r in rows})==3;assert min(r['loaded'] for r in rows)<max(r['loaded'] for r in rows);assert max(r['memory']['geometries'] for r in rows)<30;assert max(r['memory']['textures'] for r in rows)<=2
  cdp.send('HeapProfiler.collectGarbage');heapEnd=cdp.send('Runtime.getHeapUsage')['usedSize'];result={'heapStartBytes':heapStart,'heapEndBytes':heapEnd,'sourceModules':{str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest()for q in [ROOT/'assets/game.js',*sorted((ROOT/'assets').glob('webgl*.js')),*sorted((ROOT/'assets').glob('newfoundland*.js'))]},'steps':rows,'archiveInvariant':True,'save':True,'errors':errors};(OUT/'tour.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS16stream transitions,3LOD bands,portrait,stableIDs/resourcebounds/archive/save');browser.close()
finally:server.terminate()
