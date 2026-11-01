"""Remaining land families against untouched public01eeda actual UI.
Ordinary funded source archives, same paid owner and original writer. No wallet injection.
"""
from pathlib import Path
import json,gzip,hashlib,subprocess,sys
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
original=subprocess.check_output(['git','show','01eeda3:assets/game.js']).decode();source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text();bridge=''.join(Path('experimental/worker',n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js']);bindings=json.loads(Path('experimental/worker/route-bindings.generated.json').read_text());observer=Path('tools/fixtures/paid-ui-acceptance-probe.js').read_text()
hook=r'''paused=true;window.landFinal={load:a=>{if(!hydrateSave(a))throw Error('Fixture rejected');paused=true;pendingEvent=null;$('welcome').style.display='none';return archivePayload();},archive:()=>{if(!Object.isFrozen(G)){frameClock=G.trafficState.clock;trafficElapsed=G.trafficState.elapsed;return archivePayload();}return JSON.stringify(G);},plan:()=>districtFollowthroughPlan(G.civicProjects?.active.district),offer:()=>publicPlaceOffer(),runtime:()=>({active,overlay,tool:buildMode,cam:{...cam}})};'''
rows=[];saved_rows=[];negative=[];errors=[];state_receipts=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);pages=[]
 for worker,src in [(False,original),(True,source)]:
  p=b.new_page(viewport={'width':1200,'height':850});p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://land-final.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://land-final.test/');p.add_script_tag(content=src.replace('// SOURCE: 99-instrumentation.js',(bridge+observer if worker else '')+hook+'\n// SOURCE: 99-instrumentation.js'));pages.append(p)
 oracle,p=pages
 def init(name):
  archive=gzip.decompress(Path('experimental/worker/fixtures',name).read_bytes()).decode();canonical=oracle.evaluate('a=>landFinal.load(a)',archive)
  p.evaluate('''async a=>{if(window.real){await real.load(a.archive);return;}window.real=await __workerRealView.enable(a.code,a.archive,{routeBindings:a.bindings,initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Actual owner unavailable');}});__paidUiProbe.attach(real.worker);window.landChoicePosts=[];const send=real.worker.postMessage.bind(real.worker);real.worker.postMessage=function(m,...rest){if(m.type==='choice')landChoicePosts.push({eventId:m.eventId,index:m.index,choicePayload:m.choicePayload});return send(m,...rest);};}''',{'code':code,'archive':canonical,'bindings':bindings});
  for page in [oracle,p]:
   if page.locator('#panel').evaluate('e=>e.classList.contains("show")'):
    page.locator('#tabs button.active').click();page.wait_for_function('!document.querySelector("#panel").classList.contains("show")')
  p.evaluate('real.settlePanels()');p.evaluate('real.settleSaves()');return canonical
 def settle():p.evaluate('real.settlePanels()');p.evaluate('real.settleSaves()')
 def panel(tab):
  for page in [oracle,p]:
   button=page.locator('#tabs [data-panel="'+tab+'"]')
   if page.evaluate('landFinal.runtime().active')!=tab or not page.locator('#panel').evaluate('e=>e.classList.contains("show")'):button.click()
  settle()
 def reveal(page,selector):
  button=page.locator(selector).first
  button.evaluate('(b)=>{let a=[];for(let d=b.parentElement;d;d=d.parentElement)if(d.tagName==="DETAILS"&&!d.open)a.push(d);for(const d of a.reverse())d.querySelector(":scope>summary").click();}')
  return button
 def click(selector):
  for page in [oracle,p]:reveal(page,selector).click()
  p.wait_for_function('document.querySelector("#eventDialog").style.display==="flex"');settle();assert oracle.locator('#eventTitle').inner_text()==p.locator('#eventTitle').inner_text();assert oracle.locator('#eventText').inner_text()==p.locator('#eventText').inner_text()
 def choice(index):
  oracle.locator('[data-event-choice="'+str(index)+'"]').click();p.locator('[data-worker-choice="'+str(index)+'"]').click();p.wait_for_function('document.querySelector("#eventDialog").style.display==="none"');settle()
 def exact(label,require_saved=True):
  expected=json.loads(oracle.evaluate('landFinal.archive()'));actual=json.loads(p.evaluate('real.command({type:"export"})')['archive'])
  if actual!=expected:
   Path('/tmp/land-final-ui-diff.json').write_text(json.dumps({'label':label,'actual':actual,'expected':expected}));print('DIFF',label,[k for k in set(actual)|set(expected) if actual.get(k)!=expected.get(k)],flush=True)
  assert actual==expected,label;assert actual['rngState']==expected['rngState']
  stored=p.evaluate('__paidUiProbe.decodedStored()');assert not require_saved or stored==actual,label+' stored writer/readback mismatch';rows.append(label);saved_rows.extend([label] if require_saved else []);state_receipts.append({'label':label,'day':actual['day'],'treasury':actual['treasury'],'nextId':actual['nextId']});return actual
 init('district-ordinary-current.json.gz');panel('agenda');plan=oracle.evaluate('landFinal.plan()');home_index=next(i for i,s in enumerate(plan['sites']) if s['kind']=='home');before=json.loads(oracle.evaluate('landFinal.archive()'));click('[data-district-finish="'+str(home_index)+'"]');assert p.locator('.civic-project-survey').count()>0;choice(0);built=exact('district-finish-home-actual-ui');assert len(built['people'])==len(before['people']);assert before['treasury']-built['treasury']==20000
 home=next(h['building'] for h in oracle.evaluate('landFinal.plan()')['housing']['homes'] if h['available']>0 and not h['reserved']);click('[data-district-admission="'+str(home)+'"]');assert 'not actual applicants' in p.locator('#eventText').inner_text();choice(0);exact('district-admission-business-forecast-actual-ui')
 panel('agenda');click('[data-district-admission="'+str(home)+'"]');choice(2);exact('district-admission-actual-address-visit');assert p.evaluate('landFinal.runtime().active')=='';assert p.evaluate('landFinal.runtime().overlay')=='none'
 # Business entries delegate to the original civic blueprint/road/build review.
 panel('agenda');plan=oracle.evaluate('landFinal.plan()');business_index=next(i for i,s in enumerate(plan['sites']) if s.get('business'));click('[data-district-finish="'+str(business_index)+'"]');choice(0);exact('district-finish-business-delegation-actual-ui')
 init('district-unconnected-ordinary-current.json.gz');panel('agenda');plan=oracle.evaluate('landFinal.plan()');business_index=next(i for i,s in enumerate(plan['sites']) if s.get('business'));before=json.loads(oracle.evaluate('landFinal.archive()'));click('[data-district-finish="'+str(business_index)+'"]');choice(0);connected=exact('district-finish-paid-road-delegation-actual-ui');assert connected['treasury']<before['treasury'];assert len(connected['people'])==len(before['people'])
 panel('agenda');before=json.loads(oracle.evaluate('landFinal.archive()'))
 for page in [oracle,p]:reveal(page,'[data-district-budget="educationBudget"]').click()
 settle();budget=exact('district-budget-authorization-navigation-only',require_saved=False);assert budget['policy']==before['policy'];assert p.locator('[data-policy="educationBudget"]').count()>0
 for selector,tool in [('[data-road-remove-tool]','road_remove'),('[data-bridge-build]','road_bridge'),('[data-urban-clear-tool]','urban_clearance')]:
  panel('construction')
  for page in [oracle,p]:reveal(page,selector).click()
  settle();assert p.evaluate('landFinal.runtime().active')=='' and p.evaluate('landFinal.runtime().tool')==tool;assert oracle.evaluate('landFinal.runtime().active')=='' and oracle.evaluate('landFinal.runtime().tool')==tool;exact('actual-map-tool-'+tool,require_saved=False)
 for kind in ['square','warehouse']:
  init('market-ordinary-current.json.gz');panel('agenda');assert oracle.evaluate('landFinal.offer()') is not None,'No populated market offer in ordinary fixture';click('[data-public-place="'+kind+'"]');assert p.locator('#publicPlaceName').count()==1 and p.locator('.civic-project-survey').count()>0
  # Opaque choice retains a real form; invalid name refuses before any charge.
  before=p.evaluate('real.command({type:"export"})')['archive'];obs=p.evaluate('__paidUiProbe.snapshot()');p.locator('#publicPlaceName').fill('   ');p.locator('[data-worker-choice="0"]').click();p.wait_for_function('document.querySelector("#eventDialog").style.display==="flex" && /refused/i.test(document.querySelector("#workerRealStatus").textContent)');settle();assert p.evaluate('real.command({type:"export"})')['archive']==before;post=p.evaluate('__paidUiProbe.snapshot()');assert len(post['writes'])==len(obs['writes']);negative.append(kind+'-blank-name-atomic-no-write')
  name='Harbour Élan '+kind
  for page in [oracle,p]:page.locator('#publicPlaceName').fill(name)
  choice(0);model=exact('named-'+kind+'-typed-form-purchase-actual-ui');assert model['publicPlaces']['places'][-1]['name']==name and model['publicPlaces']['places'][-1]['kind']==kind
  before=p.evaluate('real.command({type:"export"})')['archive'];obs=p.evaluate('__paidUiProbe.snapshot()');replay=p.evaluate('''()=>{const m=landChoicePosts[landChoicePosts.length-1];return real.command({type:'choice',...m}).then(()=>false,e=>e.message);}''');assert replay;settle();assert p.evaluate('real.command({type:"export"})')['archive']==before;assert len(p.evaluate('__paidUiProbe.snapshot().writes'))==len(obs['writes']);negative.append(kind+'-duplicate-opaque-choice-no-write')
 assert not errors,errors
 Path('experimental/worker/land_district_final_ui_proof.json').write_text(json.dumps({'productionEnabled':False,'oracleCommit':'01eeda3d2ff09822b9422721f75e97fabbc9958a','oracleSha256':hashlib.sha256(original.encode()).hexdigest(),'hostSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'moduleSha256':hashlib.sha256(Path('experimental/worker/routes/land-district.js').read_bytes()).hexdigest(),'bindingSha256':hashlib.sha256(Path('experimental/worker/route-ui/land-district.json').read_bytes()).hexdigest(),'originalUiFundedFixtures':True,'actualPaidButtonsAndTypedName':True,'exactCompleteModelRng':rows,'originalWriterReadback':saved_rows,'negative':negative,'states':state_receipts,'pageErrors':errors,'nativeDurability':False,'remainingUnsupportedAssignedControls':[]},indent=2)+'\n');print('PASS',rows,negative,flush=True);b.close()
