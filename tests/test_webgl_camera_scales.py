"""Bounded actual WebGL close/mid/far and portrait resize/pick/save checks."""
from pathlib import Path
import subprocess,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews/newfoundland-workplaces-8';OUT.mkdir(parents=True,exist_ok=True)
server=subprocess.Popen(['python','-m','http.server','8782','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1000,'height':700});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8782/index.html?cityArt=webgl&cityQuality=low');page.locator('#newTown').click();page.locator('#pause').click();page.locator('#panelClose').click();page.wait_for_function('window.__webglTaste&&__webglTaste.frameId>=89',timeout=120000);before=page.evaluate('__townTest.save()');rows=[]
  for label,zoom,viewport in [('near',2.1,{'width':1000,'height':700}),('mid',1,{'width':1000,'height':700}),('far',.6,{'width':1000,'height':700}),('portrait',1.3,{'width':390,'height':844})]:
   page.set_viewport_size(viewport);frame=page.evaluate('__webglTaste.frameId');page.evaluate('(z)=>{const c=__webglTaste.center;__webglTaste.focus(c.x,c.y,z)}',zoom);page.wait_for_function('(n)=>__webglTaste.frameId>n',arg=frame,timeout=15000);row=page.evaluate('()=>{const c=__webglTaste.center,p=__webglTaste.project(c.x,c.y);return {camera:__webglTaste.cameraInfo(),pick:__webglTaste.pick(p.x,p.y),calls:__webglTaste.drawCalls,triangles:__webglTaste.triangles,materials:__webglTaste.materialCount,programs:__webglTaste.programs,memory:__webglTaste.memory()}}');assert row['pick']['building']==1,row;row['label']=label;rows.append(row);page.screenshot(path=str(OUT/('camera-'+label+'.png')))
  assert json.loads(before)==json.loads(page.evaluate('__townTest.save()'));assert page.evaluate('__cityVisualSave()');assert not errors; (OUT/'camera-scales.json').write_text(json.dumps({'cases':rows,'archiveInvariant':True,'save':True,'errors':errors},indent=2)+'\n');print(rows);browser.close()
finally:server.terminate()
