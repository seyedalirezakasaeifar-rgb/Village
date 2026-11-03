"""Material detail keeps picking, paused state and GPU resource disposal bounded."""
from pathlib import Path
import subprocess,json
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'docs/previews/webgl-material-quality-8';O.mkdir(parents=True,exist_ok=True);s=subprocess.Popen(['python','-m','http.server','8803','--bind','127.0.0.1'],cwd=R/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:8803/index.html?cityArt=webgl&cityQuality=low');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.wait_for_function('window.__webglTaste&&__webglTaste.samples.length>=3',timeout=90000);before=p.evaluate('__townTest.save()');rows=[]
  for x,y,z in [(26,26,1.8),(45,26,.9),(80,80,.25),(26,26,1.8)]*2:
   p.evaluate('(v)=>__webglTaste.focus(...v)',[x,y,z]);p.wait_for_timeout(400);p.wait_for_function('window.__webglTaste&&__webglTaste.samples.length>=3',timeout=90000);rows.append(p.evaluate('({lod:__webglTaste.lod,memory:__webglTaste.memory()})'))
  p.evaluate('__webglTaste.focus(26,26,1.8)');p.wait_for_timeout(600);point=p.evaluate('__webglTaste.project(26,26)');assert p.evaluate('(q)=>__webglTaste.pick(q.x,q.y)',point)['building']==1;frame=p.evaluate('__webglTaste.frameId');p.wait_for_timeout(1000);assert p.evaluate('__webglTaste.frameId')==frame;assert p.evaluate('__townTest.save()')==before;assert rows[0]['memory']==rows[-1]['memory'];assert p.evaluate('__cityVisualSave()');p.evaluate('window.__oldMaterialAPI=__webglTaste;__webglTaste.dispose()');memory=p.evaluate('__oldMaterialAPI.memory()');assert memory['geometries']==0 and memory['textures']==0,memory;assert p.locator('#view').is_visible();assert not errors,errors;(O/'resources.json').write_text(json.dumps({'samples':rows,'disposed':memory,'pickHall':True,'pausedNoExtraDraws':True,'archiveInvariant':True,'save':True,'errors':errors},indent=2));print('PASS8 camera changes, bounded textures, actual pick, idle/state/save and zero GPU resources after fallback');b.close()
finally:s.terminate()
