"""Same archive/camera, old renderer versus clean street/specialized hooks.
Common current architectural assets are deliberately shared by both variants."""
from pathlib import Path
import subprocess,json,statistics,hashlib,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews/webgl-material-quality-8';OUT.mkdir(parents=True,exist_ok=True);source=(ROOT/'assets/game.js').read_text();probe="window.__denseLots=()=>{let started=0;for(let y=19;y<=33&&started<18;y++)for(let x=19;x<=33&&started<18;x++){if(G.treasury<15000)break;if(!nearRoad(x,y)||!canPlace(x,y,false,'home'))continue;const n=G.buildings.length+G.projects.length;construct('home',x,y,true);if(G.buildings.length+G.projects.length>n)started++;}__townTest.step(50);return {started,completedHomes:G.buildings.filter(b=>b.kind==='home').length,day:G.day,projects:G.projects.length};};";script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
server=subprocess.Popen(['python','-m','http.server','8802','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def stats(a):
 a=sorted(a);return {'n':len(a),'medianMs':statistics.median(a),'p95Ms':a[int((len(a)-1)*.95)],'maxMs':max(a)}
try:
 results=[];canonical=(ROOT/'docs/previews/webgl-lot-streetscape-8/town.json').read_text()
 with sync_playwright()as w:
  browser=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for mode in ['low-before','low-after','high-after']:
   c=browser.new_context(viewport={'width':1280,'height':720});p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   p.route('**/game.js',lambda r:r.fulfill(body=script,content_type='application/javascript'))
   p.goto('http://127.0.0.1:8802/index.html?cityArt=webgl&cityQuality='+('reference' if mode=='high-after' else 'low')+'&cityBenchmark=1&cityMaterials='+('off' if mode=='low-before' else 'on'));p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();
   if False:canonical=None;print('density',p.evaluate('__denseLots()'),flush=True)
   canonical=canonical or p.evaluate('__townTest.save()');(OUT/('dense-town.json' if mode.startswith('dense') else 'town.json')).write_text(canonical);assert p.evaluate('(s)=>__townTest.load(s)',canonical);p.wait_for_function('window.__webglTaste&&__webglTaste.sceneRevision===__cityVisualRevision()',timeout=90000);p.evaluate('__webglTaste.focus(27,27,1.8)');p.wait_for_function('__webglTaste.lod==="near"&&__webglTaste.samples.length>=28',timeout=120000);before=p.evaluate('__townTest.save()');r=p.evaluate('()=>({calls:__webglTaste.drawCalls,triangles:__webglTaste.triangles,materials:__webglTaste.materialCount,programs:__webglTaste.programs,memory:__webglTaste.memory(),buildMs:__webglTaste.buildMs,cpu:__webglTaste.samples,raf:__webglTaste.rafSamples,backend:__webglTaste.renderer})');r['cpu']=stats(r['cpu'][8:]);r['raf']=stats(r['raf'][8:]);r['mode']=mode;r['sourceModuleHashes']={str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in [ROOT/'assets/game.js',*sorted((ROOT/'assets').glob('webgl*.js')),*sorted((ROOT/'assets').glob('newfoundland*.js'))]};r['archiveDigest']=hashlib.sha256(before.encode()).hexdigest();p.evaluate('__townTest.capture()');p.screenshot(path=str(OUT/(mode+'.png')));assert p.evaluate('__townTest.save()')==before;assert p.evaluate('__cityVisualSave()');assert not errors;r['errors']=errors;results.append(r);(OUT/'paired.json').write_text(json.dumps(results,indent=2)+'\n');print({k:r[k]for k in ['mode','calls','triangles','materials','programs','buildMs','raf']},flush=True);c.close()
  browser.close()
 assert results[0]['archiveDigest']==results[1]['archiveDigest'];assert results[1]['archiveDigest']==results[2]['archiveDigest']
finally:server.terminate()
