"""Exact archived benchmark towns, refreshing the actual HUD after test-only load."""
from pathlib import Path
import subprocess,json,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'docs/previews/webgl-lot-streetscape-8';server=subprocess.Popen(['python','-m','http.server','8799','--bind','127.0.0.1'],cwd=R/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);rows=[]
  for mode in ['town-off','town-on','dense-close-off','dense-close-on']:
   p=b.new_page(viewport={'width':1280,'height':720});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:8799/index.html?cityArt=webgl&cityQuality=low&cityLots='+('off'if mode.endswith('off')else'on'));p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();assert p.evaluate('(s)=>__townTest.load(s)',(O/('dense-town.json'if mode.startswith('dense')else'town.json')).read_text());p.evaluate('__townTest.capture()');p.wait_for_function('window.__webglTaste&&__webglTaste.sceneRevision===__cityVisualRevision()',timeout=90000)
   if mode.startswith('dense'):v=json.loads((O/'dense-close.json').read_text())[0]['view'];p.evaluate('(v)=>__webglTaste.focus(v.x,v.y,2.6)',v)
   else:p.evaluate('__webglTaste.focus(27,27,1.8)')
   p.wait_for_timeout(1500);before=p.evaluate('__townTest.save()');p.screenshot(path=str(O/(mode+'.png')));p.locator('#webglTaste').screenshot(path=str(O/(mode+'-world.png')));assert p.evaluate('__townTest.save()')==before;assert not errors,errors;rows.append({'mode':mode,'archiveDigest':hashlib.sha256(before.encode()).hexdigest(),'header':p.locator('header').inner_text()if p.locator('header').count()else'', 'stateInvariant':True,'errors':errors});p.close()
  assert rows[0]['archiveDigest']==rows[1]['archiveDigest'];assert rows[2]['archiveDigest']==rows[3]['archiveDigest'];(O/'captures.json').write_text(json.dumps(rows,indent=2));b.close();print('PASS actual same-archive pairs, refreshed HUD, unchanged model')
finally:server.terminate()
