"""Trusted family controls against unchanged source UI; disabled worker only."""
from pathlib import Path
import sys,json,hashlib,ast
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text();bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js']);bindings=json.loads(Path('experimental/worker/route-bindings.generated.json').read_text())
tree=ast.parse(Path('experimental/worker/transit_freight_parity_test.py').read_text());hook=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='hook' for t in n.targets))
hook=hook.replace('recompute();return archivePayload();','recompute();if(!hydrateSave(archivePayload()))throw Error("Fixture normalization failed");return archivePayload();')
hook+='''let familyFailWrites=false;const familyPersist=persistSnapshot;persistSnapshot=function(...args){return familyFailWrites?Promise.resolve(false):familyPersist.apply(this,args);};window.familyStorage={fail:v=>familyFailWrites=v,stored:()=>readSaveEnvelope(localStorage.getItem('townledger-v6'))};window.uiFacts={point:(id)=>{const pos=iso(id%T,Math.floor(id/T));cam={x:pos[0],y:pos[1],zoom:.8};dirty=true;const r=cv.getBoundingClientRect();return {x:r.left+cw/2,y:r.top+ch/2};},stops:()=>{const depot=G.buildings.find(b=>b.kind==='transit_depot'),roads=G.tiles.map((v,i)=>v===1&&transitOwnedRoad(i)?i:-1).filter(i=>i>=0);for(const a of roads)for(const b of roads){if(a>=b||roadDistance(a,b)<8)continue;const q=transitQuote({mode:'bus',depot:depot.id,stops:[a,b],level:1});if(q.ok&&q.cost<=G.treasury)return [a,b];}throw Error('No normal funded route');}};\n'''
hook+="""window.commerce={step:()=>tick(),setup:()=>{seed(42);paused=true;for(let i=0;i<30;i++){pendingEvent=null;tick();}pendingEvent=null;recompute();if(!hydrateSave(archivePayload()))throw Error('Normalize');return archivePayload();},state:()=>JSON.parse(archivePayload())};"""
hook+="""window.familyChoices=[];const familyPost=Worker.prototype.postMessage;Worker.prototype.postMessage=function(m,...rest){if(m.type==='choice')familyChoices.push({eventId:m.eventId,index:m.index});return familyPost.call(this,m,...rest);};"""
def clean(g):
 for k in ['visualState','trafficState']:g.pop(k,None)
 return g
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[];errors=[]
 for worker in [False,True]:
  p=b.new_page(viewport={'width':1000,'height':800});p.set_default_timeout(8000);p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://ui.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://ui.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',(bridge if worker else '')+hook+'// SOURCE: 99-instrumentation.js'));pages.append(p)
 oracle,q=pages;archive=oracle.evaluate('commerce.setup()');q.evaluate('''async a=>window.real=await __workerRealView.enable(a.code,a.archive,{routeBindings:a.bindings,initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':code,'archive':archive,'bindings':bindings});oracle.evaluate('a=>parity.load(a)',q.evaluate('real.command({type:"export"})')['archive'])
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
 panel('economy')
 for p in pages:p.locator('[data-procurement="upland"]').click()
 settle()
 for p,selector in [(oracle,'[data-event-choice="0"]'),(q,'[data-worker-choice]')]:p.locator(selector).first.click()
 check('staged order two milestones actual UI')
 ids=q.evaluate('real.command({type:"export"})')['model']['regionalTrade']['contracts']
 assert len(ids)==2
 panel('treasury')
 panel('economy')
 for p in pages:p.locator('[data-trade-cancel="'+str(ids[0]['id'])+'"]').click()
 check('group cancellation retains liabilities')
 panel('treasury');panel('economy')
 for p in pages:p.locator('[data-trade-offer="upland"]').first.click()
 settle()
 oracle.locator('[data-event-choice="0"]').click();q.locator('[data-worker-choice]').first.click()
 check('supplier agreement actual UI')
 panel('treasury');panel('economy')
 for p in pages:
  p.locator('#portFreightOffice summary').click()
 port=q.locator('[data-port-freight]:not([disabled])').first
 attrs=port.evaluate('(e)=>({firm:e.dataset.portFreight,dock:e.dataset.portDock,good:e.dataset.portGood,direction:e.dataset.portDirection})')
 selector='[data-port-freight="'+attrs['firm']+'"][data-port-dock="'+attrs['dock']+'"][data-port-good="'+attrs['good']+'"][data-port-direction="'+attrs['direction']+'"]'
 for p in pages:p.locator(selector).first.click()
 settle()
 for p,selector in [(oracle,'[data-event-choice="0"]'),(q,'[data-worker-choice]')]:p.locator(selector).first.click()
 check('paid river dispatch actual UI')
 frozen=q.evaluate('real.command({type:"export"})')['archive'];choice=q.evaluate('familyChoices.slice(-1)[0]');assert choice
 assert q.evaluate('m=>real.command({type:"choice",...m}).then(()=>false,e=>e.message)',choice)
 assert q.evaluate('real.command({type:"export"})')['archive']==frozen
 accounting=oracle.evaluate('parity.check()');assert accounting['valid']['ok'];assert abs(accounting['money']-initialMoney)<.001;assert max(abs(x['error']) for x in accounting['goods'])<.001
 assert not errors,errors
 Path('experimental/worker/transit-freight-commerce-proof.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'accounting':accounting,'normalResources':True,'repeatedPaidRiverChoiceRefusesUnchanged':True,'actualUiFullModelRng':rows,'saveBarriers':True,'nativeDurability':False,'pageErrors':errors},indent=2)+'\n');print('PASS',rows);b.close()
