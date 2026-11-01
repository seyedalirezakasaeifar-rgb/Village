"""Actual paid route, water-backed bridge, motion budgets and paused pixels."""
from pathlib import Path
import subprocess,json,re,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews/webgl-live-8';OUT.mkdir(parents=True,exist_ok=True)
source=(ROOT/'assets/game.js').read_text();old=(ROOT/'tests/test_road_bridge_art.py').read_text();probe=old.split("probe=r'''",1)[1].split("'''",1)[0].replace("$('toast').style.display='none';",'').replace("$('placementHint').style.display='none';",'')
probe+=r'''
window.__webglLiveTest={
 positionCargo:()=>{paused=true;let o=G.regionalTrade.shipments.find(o=>o.qty===60);for(let i=0;i<30&&o&&!['delivering','outbound'].includes(o.stage);i++){__townTest.step(1);o=G.regionalTrade.shipments.find(s=>s.id===o.id);}if(!o)throw Error('cargo settled before road phase');const v=regionalShipmentVisualState(o);if(!v?.visible||!v.path?.length)throw Error('no road phase: '+o.stage);const index=v.path.indexOf(G.bridges[0].cells[2]);if(index<0)throw Error('actual current path misses span');const fraction=.055+.89*(index/(v.path.length-1)),desired=fraction*v.travelDays;for(let i=0;i<Math.floor(desired);i++)__townTest.step(1);acc=(desired%1)*1.65;return {id:o.id,stage:o.stage,path:v.path,pose:shipmentVisualPose(o),bridge:bridgeRenderSnapshot()[0]};},
 close:()=>{G.bridges[0].condition=20;G.bridgeRevision++;},
 sample:()=>({save:__townTest.save(),rng:rngState,day:G.day,total:totalMoney(),clock:frameClock}),
 actors:(detail,bounds)=>__cityVisualActors(detail,bounds),
 busyGuard:()=>{simulationBusy=true;try{return __cityVisualActors('near',{minX:0,maxX:127,minZ:0,maxZ:127})}finally{simulationBusy=false;}}
};
'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js');server=subprocess.Popen(['python','-m','http.server','8784','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':720});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=script));page.goto('http://127.0.0.1:8784/index.html?cityArt=webgl&cityQuality=low');page.locator('#newTown').click();page.locator('#pause').click();page.locator('#panelClose').click();page.wait_for_function('window.__webglTaste',timeout=60000);page.evaluate('__bridgeArtTest.setup()');cargo=page.evaluate('__webglLiveTest.positionCargo()');page.evaluate('__webglTaste.focus(66,15,2.1)');page.wait_for_function('window.__webglTaste.sceneRevision===__cityVisualRevision()&&__webglTaste.actorStats.poses.some(p=>p.id.startsWith("cargo:"))',timeout=60000);page.wait_for_timeout(3000)
  before=page.evaluate('__webglLiveTest.sample()');poses=page.evaluate('__webglTaste.actorStats');onspan=[a for a in poses['poses'] if a['id']=='cargo:'+str(cargo['id'])];assert onspan and abs(onspan[0]['z']-15)<.5 and abs(onspan[0]['base']-.46)<1e-6,onspan
  frame1=page.locator('#webglTaste').screenshot();page.wait_for_timeout(400);frame2=page.locator('#webglTaste').screenshot();assert frame1==frame2,'paused frame changed';page.screenshot(path=str(OUT/'bridge-open-paid-freight.png'));assert page.evaluate('__webglLiveTest.sample()')==before
  far=page.evaluate('__webglLiveTest.actors("far",{})');assert far==[];assert page.evaluate('__cityVisualActorWork')=={'sources':0,'positions':0};assert page.evaluate('__webglLiveTest.busyGuard()')==[];page.evaluate('__webglLiveTest.close()');page.wait_for_function('__webglTaste.sceneRevision===__cityVisualRevision()',timeout=30000);page.screenshot(path=str(OUT/'bridge-closed-stress.png'));assert page.evaluate('__cityVisualSnapshot().bridges[0].closed')
  assert page.evaluate('__cityVisualSave()');assert not errors,errors;result={'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'fixture':'real purchased East Meadow/paid60grain import; closed view directly stresses condition20','cargo':cargo,'actors':poses,'pausedPixelsIdentical':True,'projectionStateInvariant':True,'farAgentWork':0,'busyGuard':True,'save':True,'errors':errors};(OUT/'bridge.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS actual paid cargo atop water-backed deck, frozen pixels/state, farzero/busy budgets,closed/save');browser.close()
finally:server.terminate()
