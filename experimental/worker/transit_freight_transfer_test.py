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
hook+='window.commerce={setup:()=>{__townTest.reset(\'settlement\',42);G.autoBuild=false;const s=ensureRegionalTrade();s.routePreference=\'interchange\';const warehouse=G.firms.find(f=>f.kind===\'warehouse\'),grocer=G.firms.find(f=>f.kind===\'grocer\'),market=OUTSIDE_MARKETS[0],total=totalMoney();for(let day=0;day<4;day++){if(day)G.day++;for(let i=0;i<4;i++)dispatchRegional(warehouse,\'stone\',120,\'import\',regionalQuote(warehouse,market,\'stone\',\'import\'));}dispatchRegional(grocer,\'food\',60,\'import\',regionalQuote(grocer,market,\'food\',\'import\'));const food=s.shipments.at(-1);G.day+=6;regionalFreightDay();recompute();if(!hydrateSave(archivePayload()))throw Error("Normalize");return archivePayload();},state:()=>JSON.parse(archivePayload())};'
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
 for p in pages:p.locator('#logisticsOffice summary').click()
 transfer=q.locator('[data-logistics-transfer]');assert transfer.count()>0
 cargo=transfer.first.get_attribute('data-logistics-transfer')
 for p in pages:p.locator('[data-logistics-transfer="'+cargo+'"]').click()
 settle()
 for p,selector in [(oracle,'[data-event-choice="0"]'),(q,'[data-worker-choice]')]:p.locator(selector).first.click()
 check('paid depot transfer actual UI')
 accounting=oracle.evaluate('parity.check()');assert accounting['valid']['ok'];assert abs(accounting['money']-initialMoney)<.001;assert max(abs(x['error']) for x in accounting['goods'])<.001
 assert not errors,errors
 Path('experimental/worker/transit-freight-transfer-proof.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'accounting':accounting,'normalResources':True,'fixture':'existing paid peak-arrival fixture; time advanced to create backlog; no grants','transferCandidates':transfer.count(),'actualUiFullModelRng':rows,'saveBarriers':True,'nativeDurability':False,'pageErrors':errors},indent=2)+'\n');print('PASS',rows);b.close()
