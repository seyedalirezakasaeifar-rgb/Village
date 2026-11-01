from pathlib import Path
import subprocess,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews/webgl-night-overlays-8';OUT.mkdir(parents=True,exist_ok=True)
server=subprocess.Popen(['python','-m','http.server','8792','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1000,'height':700});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:8792/index.html?cityArt=webgl&cityQuality=low');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.wait_for_function('window.__webglTaste');before=p.evaluate('__townTest.save()');rows=[]
  for width,height in [(1000,700),(390,844),(568,320)]:
   p.set_viewport_size({'width':width,'height':height});p.evaluate('__webglTaste.overview()');p.wait_for_function('__webglTaste.lod==="far"');r=p.evaluate('()=>{const rect=document.querySelector("#webglTaste").getBoundingClientRect(),corners=[];for(const x of[0,127])for(const z of[0,127]){const p=__webglTaste.project(x,z);corners.push({x,z,screen:p,inside:p.x>=rect.left&&p.x<=rect.right&&p.y>=rect.top&&p.y<=rect.bottom,pick:__webglTaste.pick(p.x,p.y)});}return {camera:__webglTaste.cameraInfo(),corners,actorWork:__webglTaste.actorWork}}');assert all(q['inside']and q['pick']['x']==q['x']and q['pick']['y']==q['z']for q in r['corners']),r;rows.append(r);p.screenshot(path=str(OUT/f'full-atlas-{width}.png'));assert p.evaluate('__townTest.save()')==before
  assert not errors;(OUT/'overview.json').write_text(json.dumps({'cases':rows,'archiveInvariant':True,'errors':errors},indent=2)+'\n');print('PASS actual full128atlas corner pick/navigation in3viewports');b.close()
finally:server.terminate()
