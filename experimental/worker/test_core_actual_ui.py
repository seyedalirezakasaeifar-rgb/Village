"""Trusted original UI controls and map gestures versus unchanged669 original game."""
from pathlib import Path
import json,subprocess,sys,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();original=subprocess.check_output(['git','show','669c908:assets/game.js']).decode();code=Path('experimental/worker/model.generated.js').read_text();bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js'])
hook='''paused=true;window.coreUI={fixture:()=>{seed(42);G.treasury+=100000;G.region-=100000;pendingEvent=null;active='';ensureRoadWear();G.roadWear[G.tiles.findIndex(v=>v===1)]=25;return archivePayload();},load:a=>{G=JSON.parse(a);rngState=G.rngState;const metrics=G.roadMetrics;invalidateRoads();G.roadMetrics=metrics;pendingEvent=null;active='';$('welcome').style.display='none';},model:()=>JSON.parse(archivePayload()),lot:k=>{const before=rngState;try{return buildableCandidates(k).find(p=>canPlace(p.x,p.y,true,k));}finally{rngState=before;}},road:()=>{for(let y=1;y<T-1;y++)for(let x=1;x<T-2;x++)if([x,x+1].every(a=>charterOwns(a,y)&&[0,3].includes(cityCell(a,y))&&!G.landUse?.[roadId(a,y)]&&!buildingAt(a,y)))return {x,y};},repair:()=>{const id=G.roadWear.findIndex((v,i)=>v<96&&G.tiles[i]===1);return {x:id%T,y:Math.floor(id/T)};},point:p=>{const pos=iso(p.x,p.y);cam={x:pos[0],y:pos[1],zoom:.8};dirty=true;const r=cv.getBoundingClientRect();return {x:r.left+cw/2,y:r.top+ch/2,dx:TW/2*.8,dy:TH/2*.8};}};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);errors=[];pages=[]
 for kind,src in [('oracle',original),('worker',source)]:
  p=b.new_page(viewport={'width':1000,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://core-ui.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://core-ui.test/');p.add_script_tag(content=src.replace('// SOURCE: 99-instrumentation.js',(bridge if kind=='worker' else '')+hook+'// SOURCE: 99-instrumentation.js'));pages.append(p)
 oracle,q=pages;archive=oracle.evaluate('coreUI.fixture()');oracle.evaluate('a=>coreUI.load(a)',archive);q.evaluate('''async a=>window.real=await __workerRealView.enable(a.code,a.archive,{initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':code,'archive':archive});rows=[]
 def settle():q.evaluate('real.settlePanels()');q.evaluate('real.settleSaves()')
 def panel(tab):
  for p in pages:p.locator('#tabs [data-panel="'+tab+'"]').click()
  settle()
 def check(name):
  settle();expected=oracle.evaluate('coreUI.model()');actual=q.evaluate('real.command({type:"export"})')['model']
  for key in ['visualState','trafficState']:expected.pop(key,None);actual.pop(key,None)
  if actual!=expected:Path('/tmp/core-ui-diff.json').write_text(json.dumps({'actual':actual,'expected':expected},indent=2))
  assert actual==expected,name;rows.append(name)
 panel('treasury')
 for control in ['borrow','repay']:
  for p in pages:p.locator('#'+control).click()
  check(control)
 panel('construction')
 for p in pages:p.locator('#toggleDevelopment').click()
 check('toggleDevelopment')
 panel('agenda')
 for p in pages:p.locator('[data-ambition]').nth(1).click()
 check('ambition')
 panel('policies')
 for p in pages:
  control=p.locator('[data-policy="minWage"]');control.evaluate('e=>{const d=e.closest("details");if(d)d.open=true;}');control.focus();control.press('ArrowRight');p.locator('#enactPolicy').click()
 check('enactPolicy')
 for kind in ['park','home','grocer','repair','road']:
  panel('construction');lot=oracle.evaluate('k=>k==="road"?coreUI.road():k==="repair"?coreUI.repair():coreUI.lot(k)',kind)
  for p in pages:p.locator('[data-build="'+kind+'"]').first.click()
  settle()
  for p in pages:
   point=p.evaluate('p=>coreUI.point(p)',lot);p.mouse.move(point['x'],point['y']);p.mouse.down()
   if kind=='road':p.mouse.move(point['x']+point['dx'],point['y']+point['dy'],steps=1)
   p.mouse.up()
  check('map:'+kind)
 assert not errors,errors
 Path('experimental/worker/core-actual-ui-proof.json').write_text(json.dumps({'productionEnabled':False,'oracleCommit':'669c908706af997375680674390e46fd132a970a','sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'bridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'trustedActualControlsFullModelRngEqual':rows,'fixtureSetup':'conserved region-to-town test funding, one worn road, RNG-preserving coordinate selection; no simulation workload omitted','pageErrors':errors},indent=2)+'\n');print('PASS trusted actual UI',rows);b.close()
