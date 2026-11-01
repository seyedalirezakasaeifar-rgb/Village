"""Injected official shader-error callback and late-build error: clean Canvas."""
from pathlib import Path
import subprocess,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews/webgl-night-overlays-8';OUT.mkdir(parents=True,exist_ok=True)
renderer=(ROOT/'assets/webgl-taste.js').read_text();server=subprocess.Popen(['python','-m','http.server','8793','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);rows=[]
  for mode in ['shader-callback','late-build']:
   p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));code=renderer.replace('renderer.render(scene,camera);','renderer.debug.onShaderError();renderer.render(scene,camera);')if mode=='shader-callback'else renderer.replace('annotationLayer=mapOverlay(state,canvas,loadedBuildings);','annotationLayer=mapOverlay(state,canvas,loadedBuildings);throw Error("Injected build failure");');p.route('**/webgl-taste.js',lambda r:r.fulfill(body=code,content_type='application/javascript'));p.goto('http://127.0.0.1:8793/index.html?cityArt=webgl&cityQuality=low');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.wait_for_function('window.__webglTasteFailure&&!document.querySelector("#webglTaste")&&!document.querySelector("#webglMapOverlay")',timeout=60000);assert p.locator('#view').is_visible();assert p.evaluate('__cityVisualSave()');assert not errors,errors;rows.append({'mode':mode,'failure':p.evaluate('__webglTasteFailure'),'noPartialCleanup':p.evaluate('!window.__webglPartialCleanup'),'canvasVisible':True,'save':True,'errors':errors});p.close()
  b.close();(OUT/'driver-fallback.json').write_text(json.dumps(rows,indent=2)+'\n');print('PASS injected drivercallback/latebuild failures restore saveableCanvas without orphanoverlay')
finally:server.terminate()
