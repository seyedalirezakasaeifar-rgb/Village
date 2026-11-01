"""Normal renderer: imports before/after town, zero paused GPU submissions."""
from pathlib import Path
import subprocess,json
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'docs/previews/webgl-normal-idle-8';O.mkdir(parents=True,exist_ok=True);server=subprocess.Popen(['python','-m','http.server','8801','--bind','127.0.0.1'],cwd=R/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);rows=[]
  for mode in ['pre-town','post-town']:
   p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   if mode=='post-town':p.route('**/webgl-entry.js',lambda r:r.fulfill(body="window.__startLate=()=>import('./webgl-taste.js');",content_type='application/javascript'))
   p.goto('http://127.0.0.1:8801/index.html?cityArt=webgl&cityQuality=low');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click()
   if mode=='post-town':assert p.locator('#webglTaste').count()==0;p.evaluate('__startLate()')
   p.wait_for_function('window.__webglTaste&&__webglTaste.samples.length>=3',timeout=90000);p.evaluate('()=>{window.__idleCalls=0;const f=__cityVisualActors;window.__cityVisualActors=(...a)=>{__idleCalls++;return f(...a)}}');a=p.evaluate('({frame:__webglTaste.frameId,save:__townTest.save()})');p.wait_for_timeout(3000);z=p.evaluate('({frame:__webglTaste.frameId,save:__townTest.save(),actors:__idleCalls})');assert a['frame']==z['frame']and a['save']==z['save']and z['actors']==0;p.locator('#zoomIn').click();p.wait_for_function('(n)=>__webglTaste.frameId>n',arg=a['frame']);assert p.evaluate('__cityVisualSave()');assert not errors,errors;rows.append({'mode':mode,'pausedExtraDraws':z['frame']-a['frame'],'pausedActorQueries':z['actors'],'archiveInvariant':True,'zoomRedraw':True,'save':True,'errors':errors});p.close()
  b.close();(O/'checks.json').write_text(json.dumps(rows,indent=2));print(rows)
finally:server.terminate()
