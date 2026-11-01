import os
"""Current public civic controls versus combined worker, actual trusted UI."""
from pathlib import Path
import sys,json,hashlib,subprocess
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
oracleCommit=os.environ.get('WORKER_ORACLE_COMMIT','87811c52cdb9aecd13cd23beebd52f6475c6dd9c');original=subprocess.check_output(['git','show',oracleCommit+':assets/game.js']).decode();source=Path('assets/game.js').read_text();worker=Path('experimental/worker/model.generated.js').read_text();bridge=Path('experimental/worker/real-view.generated.js').read_text()
hook='''paused=true;window.civicUI={fixture:()=>{seed(42);paused=true;for(let i=0;i<30;i++)tick();pendingEvent=null;active='';$('welcome').style.display='none';return archivePayload();},load:a=>{G=JSON.parse(a);rngState=G.rngState;traffic=[];intersectionGates.clear();const metrics=G.roadMetrics;invalidateRoads(false);restoreTransport();G.roadMetrics=metrics;pendingEvent=null;active='';$('welcome').style.display='none';},model:()=>JSON.parse(archivePayload()),lot:k=>{const before=JSON.stringify([G,rngState]);let best=null,score=-Infinity;for(let y=0;y<56;y++)for(let x=0;x<56;x++)if(canPlace(x,y,true,k)){const n=G.households.reduce((n,h)=>{const b=readBuild(h.home);return n+(b?h.people.length/(1+Math.abs(x-b.x)+Math.abs(y-b.y)):0);},0);if(n>score){score=n;best={x,y};}}if(before!==JSON.stringify([G,rngState]))throw Error('Site probe changed authority');return best;},point:p=>{const pos=iso(p.x,p.y);cam={x:pos[0],y:pos[1],zoom:.8};dirty=true;const r=cv.getBoundingClientRect();return {x:r.left+cw/2,y:r.top+ch/2};}};\n'''
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
  if actual!=expected:Path('/tmp/civic-ui-mismatch.json').write_text(json.dumps({'name':name,'actual':actual,'expected':expected},indent=2))
  assert actual==expected,name;rows.append(name);print('PASS',name,flush=True)
 panel('agenda');both('[data-mayor-direction]');choose();check('direction')
 both('[data-mayor-baseline]');check('baseline');both('[data-mayor-baseline]');choose();check('baseline replace')
 both('[data-civic-project-review="food"]');choose();check('food project')
 both('[data-civic-project-replan="food"]');choose(1);check('food replan')
 both('[data-civic-project-withdraw="food"]');choose();check('withdraw')
 both('[data-civic-project-decline="food"]');check('decline');both('[data-civic-project-restore]');check('restore offers')
 both('[data-civic-project-review="district"]');check('district form');both('#projectDistrictAdopt');check('district adopt')
 both('[data-civic-project-review="skills"]');choose();check('skills project');both('[data-civic-project-budget]');choose();check('school budget proposal')
 panel('construction');lot=oracle.evaluate('civicUI.lot("square")');assert lot
 both('[data-build="square"]')
 for p in pages:
  point=p.evaluate('p=>civicUI.point(p)',lot);p.mouse.click(point['x'],point['y'])
 settle();check('square purchase')
 panel('agenda');both('[data-gathering-review]');check('gathering preview');choose();check('gathering funded')
 both('[data-gathering-cancel]');choose();check('gathering cancel')
 assert not errors,errors
 Path('experimental/worker/civic-actual-ui-proof.json').write_text(json.dumps({'productionEnabled':False,'oracleCommit':oracleCommit,'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'generatedBridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'checkpoints':rows,'fullModelRngEquality':True,'excludedFields':[],'fixture':'seed42 after30 original complete days; no resource injection','pageErrors':errors},indent=2)+'\n');b.close()
