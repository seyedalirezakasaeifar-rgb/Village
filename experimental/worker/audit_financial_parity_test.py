import os,gzip
"""Current public civic controls versus combined worker, actual trusted UI."""
from pathlib import Path
import sys,json,hashlib,subprocess
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
oracleCommit=os.environ.get('WORKER_ORACLE_COMMIT','87811c52cdb9aecd13cd23beebd52f6475c6dd9c');original=subprocess.check_output(['git','show',oracleCommit+':assets/game.js']).decode();source=Path('assets/game.js').read_text();worker=Path('experimental/worker/model.generated.js').read_text();bridge=Path('experimental/worker/real-view.generated.js').read_text()
hook='''paused=true;window.civicUI={fixture:()=>{seed(42);paused=true;for(let i=0;i<0;i++)tick();pendingEvent=null;active='';$('welcome').style.display='none';return archivePayload();},load:a=>{G=JSON.parse(a);rngState=G.rngState;traffic=[];intersectionGates.clear();const metrics=G.roadMetrics;invalidateRoads(false);restoreTransport();G.roadMetrics=metrics;pendingEvent=null;active='';selected=null;buildMode='';supplierSelection={market:'port',good:'food',firm:null};$('welcome').style.display='none';},model:()=>JSON.parse(archivePayload()),lot:k=>{const before=JSON.stringify([G,rngState]);let best=null,score=-Infinity;for(let y=0;y<56;y++)for(let x=0;x<56;x++)if(canPlace(x,y,true,k)){const n=G.households.reduce((n,h)=>{const b=readBuild(h.home);return n+(b?h.people.length/(1+Math.abs(x-b.x)+Math.abs(y-b.y)):0);},0);if(n>score){score=n;best={x,y};}}if(before!==JSON.stringify([G,rngState]))throw Error('Site probe changed authority');return best;},retailFixture:()=>{seed(42);paused=true;pendingEvent=null;for(const h of G.households)for(let j=0;j<18;j++){const p={id:G.people.length,name:'Review fixture resident',age:29,skill:.7,health:90,hh:h.id,job:-1,life:70,last:[]};G.people.push(p);h.people.push(p.id);}G.stats.marketConfidence=75;active='';selected=null;return archivePayload();},point:p=>{const pos=iso(p.x,p.y);cam={x:pos[0],y:pos[1],zoom:.8};dirty=true;const r=cv.getBoundingClientRect();return {x:r.left+cw/2,y:r.top+ch/2};}};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[];errors=[]
 for kind,src in [('oracle',original),('worker',source)]:
  p=b.new_page(viewport={'width':1100,'height':850});p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://civic-ui.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://civic-ui.test/');p.add_script_tag(content=src.replace('// SOURCE: 99-instrumentation.js',(bridge if kind=='worker' else '')+hook+'// SOURCE: 99-instrumentation.js'));pages.append(p)
 oracle,q=pages;archive=oracle.evaluate('civicUI.fixture()');oracle.evaluate('a=>civicUI.load(a)',archive);q.evaluate('''async a=>window.real=await __workerRealView.enable(a.worker,a.archive,{initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'worker':worker,'archive':archive});rows=[]
 def settle():q.evaluate('real.settleSaves()');q.evaluate('real.settlePanels()');q.evaluate('real.settleSaves()')
 def click(p,sel):
  target=p.locator(sel).first
  if not target.count():raise AssertionError('Absent actual control '+sel)
  for _ in range(8):
   if target.is_visible():break
   index=target.evaluate('e=>{let outer=null;for(let a=e.parentElement;a;a=a.parentElement)if(a.tagName==="DETAILS"&&!a.open)outer=a;return outer?[...document.querySelectorAll("details")].indexOf(outer):-1;}')
   if index<0:break
   p.locator('details').nth(index).locator(':scope > summary').click()
  target.click()
 def both(sel):
  for p in pages:click(p,sel)
  settle()
 def panel(tab):both('#tabs [data-panel="'+tab+'"]')
 def choose(index=0):
  oracle.locator('#eventChoices [data-event-choice]').nth(index).click();q.locator('#eventChoices [data-worker-choice]').nth(index).click();settle()
 def check(name):
  expected=oracle.evaluate('civicUI.model()');actual=q.evaluate('real.command({type:"export"})')['model']
  if actual!=expected:
   Path('/tmp/audit-error-detail.json').write_text(json.dumps(q.evaluate('({toast:document.querySelector("#toast").textContent,status:real.recoveryStatus(),title:document.querySelector("#eventTitle").textContent})'),indent=2))
   Path('/tmp/civic-ui-mismatch.json').write_text(json.dumps({'name':name,'actual':actual,'expected':expected},indent=2))
  assert actual==expected,name;rows.append(name);print('PASS',name,flush=True)
 panel('overview');both('#firstFoodOrder');check('food preview')
 choose();check('food paid enterprise delivery')
 panel('construction');both('[data-urban-land-plan]');check('vacant land tool')
 for p in pages:
  point=p.evaluate('p=>civicUI.point(p)',{'x':28,'y':28});p.mouse.click(point['x'],point['y'])
 settle();check('vacant land quote');choose();check('vacant land planning payment')
 # Existing adversarial source-unit fixture; no ordinary population/play claim.
 for p in pages:
  if p.locator('#panel').evaluate('e=>e.classList.contains("show")'):click(p,'#panelClose')
 settle()
 synthetic=oracle.evaluate('civicUI.retailFixture()');oracle.evaluate('a=>civicUI.load(a)',synthetic);q.evaluate('a=>real.load(a)',synthetic)
 panel('construction');both('[data-urban-retail]');check('synthetic funded retail proposal')
 assert oracle.locator('#eventDialog').is_visible(),'Synthetic source-unit fixture did not produce a mall offer'
 choose();check('synthetic privately funded retail settlement')
 for p in pages:
  if p.locator('#panel').evaluate('e=>e.classList.contains("show")'):click(p,'#panelClose')
 settle()
 funded=gzip.decompress(Path('docs/previews/growth-journey/regional-42-planned.json.gz').read_bytes()).decode();oracle.evaluate('a=>civicUI.load(a)',funded);q.evaluate('a=>real.load(a)',funded)
 panel('construction');both('[data-parcel-outlook="east-meadow"]');check('growth outlook exact quote')
 assert 'Visit Cottage site' in oracle.locator('#eventChoices').inner_text()
 choose();check('growth outlook site selection')
 assert oracle.evaluate('civicUI.model()')['treasury']==q.evaluate('real.command({type:"export"})')['model']['treasury']
 for p in pages:
  point=p.evaluate('p=>civicUI.point(p)',{'x':59,'y':14});p.mouse.click(point['x'],point['y'])
 settle();check('growth outlook real cottage purchase')
 for p in pages:
  if p.locator('#panel').evaluate('e=>e.classList.contains("show")'):click(p,'#panelClose')
 settle();oracle.evaluate('a=>civicUI.load(a)',funded);q.evaluate('a=>real.load(a)',funded);panel('economy')
 for selector in ['#supplierMarket','#supplierGood','#supplierFirm']:
  current=oracle.locator(selector).input_value();values=oracle.locator(selector+' option').evaluate_all('(nodes)=>nodes.filter(n=>!n.disabled).map(n=>n.value)');other=next(v for v in values if v!=current)
  for p in pages:
   p.locator('#alternativeSuppliers').evaluate('e=>e.open=true');p.locator(selector).select_option(other)
  settle();assert all(p.locator(selector).input_value()==other for p in pages);check('supplier retained '+selector)
 offer='#alternativeSuppliers [data-trade-offer]:not([disabled])'
 if oracle.locator(offer).count():
  both(offer);check('selected supplier actual contract quote');choose();check('selected supplier funded agreement')
 before=q.evaluate('real.command({type:"export"})')['model']
 for field,value in [('market','unknown-buyer'),('good','unknown-good'),('firm','999999')]:
  error=q.evaluate('''async p=>{try{await real.command({type:'route',module:'audit-completion',operation:'supplier',payload:p});return null;}catch(e){return String(e);}}''',{'field':field,'value':value});assert error;assert q.evaluate('real.command({type:"export"})')['model']==before
 check('invalid supplier DTOs preserve complete model')
 assert not errors,errors
 Path('experimental/worker/audit-financial-parity-proof.json').write_text(json.dumps({'productionEnabled':False,'oracleCommit':oracleCommit,'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'generatedBridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'checkpoints':rows,'fullModelRngEquality':True,'excludedFields':[],'fixtures':['generated seed42 founding','existing controlled retail source-unit fixture adds household members; not ordinary play','unchanged generated day1081 regional QA archive'],'syntheticRetailCase':True,'pageErrors':errors},indent=2)+'\n');b.close()
