"""Source-matched CSS picking/overview across mobile DPR1–3; host only."""
from pathlib import Path
import subprocess,json,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews/webgl-economy-8';OUT.mkdir(parents=True,exist_ok=True)
server=subprocess.Popen(['python','-m','http.server','8812','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);canonical=None;rows=[]
  for width,height,dpr in [(1280,720,1),(390,844,2),(844,390,3)]:
   c=b.new_context(viewport={'width':width,'height':height},device_scale_factor=dpr,has_touch=True);p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:8812/index.html?cityArt=webgl&cityQuality=economy');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();canonical=canonical or p.evaluate('__townTest.save()');assert p.evaluate('(s)=>__townTest.load(s)',canonical);p.wait_for_function('window.__webglTaste&&__webglTaste.sceneRevision===__cityVisualRevision()');before=p.evaluate('__townTest.save()');frames=[]
   for zoom in [1.8,1,.5]:
    previous=p.evaluate('__webglTaste.frameId');p.evaluate('(z)=>__webglTaste.focus(26,26,z)',zoom);p.wait_for_function('(f)=>__webglTaste.frameId>f',arg=previous,timeout=30000);r=p.evaluate('()=>{const q=__webglTaste.project(26,26);return {lod:__webglTaste.lod,pick:__webglTaste.pick(q.x,q.y),backing:__webglTaste.backingSize,memory:__webglTaste.memory(),overlayCount:document.querySelectorAll("#webglMapOverlay").length,actorWork:__webglTaste.actorWork}}');assert r['pick'].get('building')==1,r;assert r['overlayCount']==1;assert max(r['backing'])<=384;frames.append(r)
   p.evaluate('__webglTaste.overview()');p.wait_for_function('__webglTaste.lod==="far"');assert p.evaluate('__townTest.save()')==before;assert p.evaluate('__cityVisualSave()');assert not errors;rows.append({'viewport':[width,height],'deviceDPR':dpr,'frames':frames,'archiveInvariant':True,'save':True,'errors':errors});p.screenshot(path=str(OUT/f'atlas-dpr{dpr}.png'));c.close()
  b.close();(OUT/'dpr.json').write_text(json.dumps({'gameSha256':hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest(),'cases':rows},indent=2)+'\n');print('PASS9LOD/CSSpick cases atDPR1–3,fullatlas/save/model/overlaycleanup')
finally:server.terminate()
