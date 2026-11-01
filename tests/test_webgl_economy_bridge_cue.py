"""Controlled paid-bridge fixture: actual closed state remains visible at coarse LOD."""
from pathlib import Path
import subprocess,json,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'docs/previews/webgl-economy-8';old=(R/'tests/test_road_bridge_art.py').read_text();probe=old.split("probe=r'''",1)[1].split("'''",1)[0].replace("$('toast').style.display='none';",'').replace("$('placementHint').style.display='none';",'');probe+='window.__closeBridgeCue=()=>{G.bridges[0].condition=20;G.bridgeRevision++;};';script=(R/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js');renderer=(R/'assets/webgl-taste.js').read_text();server=subprocess.Popen(['python','-m','http.server','8810','--bind','127.0.0.1'],cwd=R/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 rows=[]
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for mode in ['before','after']:
   p=b.new_page(viewport={'width':1280,'height':720});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(body=script,content_type='application/javascript'))
   if mode=='before':p.route('**/webgl-taste.js',lambda r:r.fulfill(body=renderer.replace('if(!semantic&&lod','if(lod'),content_type='application/javascript'))
   p.goto('http://127.0.0.1:8810/index.html?cityArt=webgl&cityQuality=economy');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.evaluate('__townTest.reset("settlement",42);__bridgeArtTest.setup();__closeBridgeCue();__townTest.capture()');p.wait_for_function('window.__webglTaste&&__webglTaste.sceneRevision===__cityVisualRevision()',timeout=90000);p.evaluate('__webglTaste.focus(66,15,1.8)');p.wait_for_timeout(700);assert p.evaluate('__webglTaste.lod==="far"&&__cityVisualSnapshot().bridges[0].closed');state=p.evaluate('__townTest.save()');p.screenshot(path=str(O/('closed-bridge-'+mode+'.png')));assert p.evaluate('__townTest.save()')==state;assert not errors,errors;rows.append({'mode':mode,'archiveSHA256':hashlib.sha256(state.encode()).hexdigest(),'controlledFixture':True,'closedState':True,'farLOD':True,'renderInvariant':True,'errors':errors});p.close()
  b.close();assert rows[0]['archiveSHA256']==rows[1]['archiveSHA256'];(O/'closed-bridge-cue.json').write_text(json.dumps(rows,indent=2));print('PASS same seeded closed-bridge state; before/after coarse cue captures, no render mutation')
finally:server.terminate()
