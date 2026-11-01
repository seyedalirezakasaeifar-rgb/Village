"""Trusted family controls against unchanged source UI; disabled worker only."""
from pathlib import Path
import sys,json,hashlib,ast
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text();bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js']);bindings=json.loads(Path('experimental/worker/route-bindings.generated.json').read_text())
tree=ast.parse(Path('experimental/worker/transit_freight_parity_test.py').read_text());hook=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='hook' for t in n.targets))
hook=hook.replace('recompute();return archivePayload();','recompute();if(!hydrateSave(archivePayload()))throw Error("Fixture normalization failed");return archivePayload();')
hook+='''let familyFailWrites=false;const familyPersist=persistSnapshot;persistSnapshot=function(...args){return familyFailWrites?Promise.resolve(false):familyPersist.apply(this,args);};window.familyStorage={fail:v=>familyFailWrites=v,stored:()=>readSaveEnvelope(localStorage.getItem('townledger-v6'))};window.uiFacts={overlay:()=>overlay,step:()=>tick(),point:(id)=>{const pos=iso(id%T,Math.floor(id/T));cam={x:pos[0],y:pos[1],zoom:.8};dirty=true;const r=cv.getBoundingClientRect();return {x:r.left+cw/2,y:r.top+ch/2};},stops:()=>{const depot=G.buildings.find(b=>b.kind==='transit_depot'),roads=G.tiles.map((v,i)=>v===1&&transitOwnedRoad(i)?i:-1).filter(i=>i>=0);for(const a of roads)for(const b of roads){if(a>=b||roadDistance(a,b)<8)continue;const q=transitQuote({mode:'bus',depot:depot.id,stops:[a,b],level:1});if(q.ok&&q.cost<=G.treasury)return [a,b];}throw Error('No normal funded route');}};\n'''
def clean(g):
 for k in ['visualState','trafficState']:g.pop(k,None)
 return g
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[];errors=[]
 for worker in [False,True]:
  p=b.new_page(viewport={'width':1000,'height':800});p.set_default_timeout(8000);p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://ui.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://ui.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',(bridge if worker else '')+hook+'// SOURCE: 99-instrumentation.js'));pages.append(p)
 oracle,q=pages;archive=oracle.evaluate('parity.setup()');targets=oracle.evaluate('targets');stops=oracle.evaluate('uiFacts.stops()');q.evaluate('''async a=>window.real=await __workerRealView.enable(a.code,a.archive,{routeBindings:a.bindings,initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':code,'archive':archive,'bindings':bindings});oracle.evaluate('a=>parity.load(a)',q.evaluate('real.command({type:"export"})')['archive'])
 for p in pages:p.evaluate("document.getElementById('welcome').style.display='none'")
 initialMoney=oracle.evaluate('parity.check().money');rows=[]
 def settle():q.evaluate('real.settlePanels()');q.evaluate('real.settleSaves()')
 def check(name):
  settle();expected=clean(oracle.evaluate('parity.state()'));actual=clean(q.evaluate('real.command({type:"export"})')['model'])
  
  if actual!=expected:Path('/tmp/transit-ui-diff.json').write_text(json.dumps({'expected':expected,'actual':actual},indent=2))
  assert actual==expected,[(name,k) for k in set(actual)|set(expected) if actual.get(k)!=expected.get(k)];rows.append(name)
 def panel(name):
  for p in pages:p.locator('#tabs [data-panel="'+name+'"]').click()
  settle()
 panel('construction')
 for p in pages:p.locator('[data-transit-action="new-bus"]').click()
 check('new bus draft')
 for p in pages:p.locator('[data-transit-action="map"]').click()
 settle()
 for stop in stops:
  for p in pages:
   point=p.evaluate('id=>uiFacts.point(id)',stop);p.mouse.click(point['x'],point['y'])
  settle()
 panel('construction')
 for value in ['2','1']:
  for p in pages:p.locator('#transitLevel').select_option(value)
  check('draft configuration '+value)
 for p in pages:p.locator('[data-transit-action="undo"]').click()
 check('draft undo')
 for p in pages:p.locator('[data-transit-action="map"]').click()
 settle()
 for p in pages:
  point=p.evaluate('id=>uiFacts.point(id)',stops[-1]);p.mouse.click(point['x'],point['y'])
 settle();panel('construction')
 for p in pages:p.locator('[data-transit-action="quote"]').click()
 check('trusted map stops and authoritative quote')
 oracle.evaluate('uiFacts.step()');q.evaluate('real.command({type:"step",days:1})');check('ordinary day invalidates quote')
 for p in pages:p.locator('[data-transit-action="build"]').click()
 check('stale build refusal no payment')
 for p in pages:p.locator('[data-transit-action="quote"]').click()
 check('refreshed transit quote')
 for p in pages:p.locator('[data-transit-action="build"]').click()
 check('paid route build')
 presentation_before=clean(q.evaluate('real.command({type:"export"})')['model'])
 report_id=q.evaluate('real.command({type:"export"})')['model']['transit']['routes'][-1]['id']
 for p in pages:
  button=p.locator('[data-transit-action="report"][data-route="'+str(report_id)+'"]');button.evaluate('(e)=>e.closest("details").open=true');button.click()
 check('route demand report actual UI')
 assert clean(q.evaluate('real.command({type:"export"})')['model'])==presentation_before
 for p in pages:assert p.locator('[data-transit-report="'+str(report_id)+'"]').count()==1
 for p in pages:p.locator('[data-transit-action="hide-report"]').click()
 check('hide demand report actual UI')
 assert clean(q.evaluate('real.command({type:"export"})')['model'])==presentation_before
 for p in pages:assert p.locator('[data-transit-report]').count()==0
 for ix in range(2):
  for p in pages:p.locator('[data-transit-action="overlay"]').click()
  check('transit overlay toggle '+str(ix))
  assert clean(q.evaluate('real.command({type:"export"})')['model'])==presentation_before
  assert oracle.evaluate('uiFacts.overlay()')==q.evaluate('uiFacts.overlay()')
 for p in pages:p.locator('[data-transit-action="new-bus"]').click()
 check('second draft start')
 for p in pages:p.locator('[data-transit-action="cancel"]').click()
 check('draft cancellation')
 route=q.evaluate('real.command({type:"export"})')['model']['transit']['routes'][-1]
 for level in [0,1]:
  for p in pages:
   p.locator('details.entry').filter(has=p.locator('[data-transit-action="retire"][data-route="'+str(route['id'])+'"]')).evaluate('(e)=>e.open=true')
   p.locator('[data-transit-level="'+str(route['id'])+':'+str(level)+'"]').click()
  check('service level '+str(level))
 before_failed=q.evaluate('familyStorage.stored()');q.evaluate('familyStorage.fail(true)')
 for p in pages:
  p.locator('[data-transit-action="retire"][data-route="'+str(route['id'])+'"]').evaluate('(e)=>e.closest("details").open=true')
  p.locator('[data-transit-action="retire"][data-route="'+str(route['id'])+'"]').click()
 check('paid route retirement')
 assert q.evaluate('real.recoveryStatus().unsaved');assert q.evaluate('familyStorage.stored()')==before_failed
 committed=q.evaluate('real.command({type:"export"})')['model'];q.evaluate('familyStorage.fail(false)');q.evaluate('window.workerRealLastSaveAck=null');q.locator('[data-worker="save"]').click();q.wait_for_function('window.workerRealLastSaveAck?.persisted===true');assert not q.evaluate('real.recoveryStatus().unsaved');assert q.evaluate('real.command({type:"export"})')['model']==committed
 for p in pages:
  target=p.locator('[data-transit-action="remove-site"][data-site="'+str(targets['site'])+'"]')
  target.evaluate('(e)=>e.closest("details").open=true');target.click()
 check('paid unused depot removal actual UI')
 panel('economy')
 for p in pages:p.locator('#logisticsOffice summary').click()
 for p in pages:p.locator('#logisticsRelief').click()
 settle()
 oracle.locator('[data-event-choice="0"]').click();q.locator('[data-worker-choice]').first.click()
 check('extra shift authorization actual UI')
 panel('treasury');panel('economy')
 for p in pages:
  if not p.locator('#logisticsOffice').evaluate('(e)=>e.open'):p.locator('#logisticsOffice summary').click()
  p.locator('#logisticsReliefStop').click()
 check('stop extra shifts actual UI')
 for kind,value in [('priority','essentials'),('routing','river')]:
  for p in pages:
   if not p.locator('#logisticsOffice').evaluate('(e)=>e.open'):p.locator('#logisticsOffice summary').click()
   p.locator('[data-logistics-'+kind+'="'+value+'"]').click()
  check('freight '+kind)
 for p in pages:
  if not p.locator('#logisticsOffice').evaluate('(e)=>e.open'):p.locator('#logisticsOffice summary').click()
  p.locator('[data-logistics-cancel="'+str(targets['cargo'])+'"]').click()
 settle()
 oracle.locator('[data-event-choice="0"]').click();q.locator('[data-worker-choice]').first.click()
 check('paid import recall actual controls')
 accounting=oracle.evaluate('parity.check()');assert accounting['valid']['ok'];assert abs(accounting['money']-initialMoney)<.001;assert max(abs(x['error']) for x in accounting['goods'])<.001
 assert not errors,errors
 Path('experimental/worker/transit-freight-ui-proof.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'accounting':accounting,'normalResources':True,'actualUiFullModelRng':rows,'presentationNoAuthorityMutation':True,'saveBarriers':True,'writerFailureThenRetryWithoutEconomicReplay':True,'nativeDurability':False,'pageErrors':errors},indent=2)+'\n');print('PASS',rows);b.close()
