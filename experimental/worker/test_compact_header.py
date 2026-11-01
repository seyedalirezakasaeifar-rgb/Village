"""Synthetic branch inputs test presentation equivalence, not economic play."""
from pathlib import Path
import sys,json,subprocess,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();worker=Path('experimental/worker/model.generated.js').read_text();bridge=Path('experimental/worker/real-view.generated.js').read_text()
hook='''window.headerTest={seed:()=>{seed(42);paused=true;pendingEvent=null;return archivePayload();},case:(text,n)=>{G=JSON.parse(text);rngState=G.rngState;const inputs=[{foodDisconnected:2,unmetFood:0,hardship:0,employment:99},{foodDisconnected:0,unmetFood:G.stats.population,hardship:0,employment:99},{foodDisconnected:0,unmetFood:0,hardship:70,employment:99},{foodDisconnected:0,unmetFood:0,hardship:0,employment:30},{foodDisconnected:0,unmetFood:0,hardship:0,employment:99}][n];Object.assign(G.market,inputs);Object.assign(G.stats,{hardship:inputs.hardship,employment:inputs.employment});liveStatusTown=null;updateHeader();return {archive:archivePayload(),expected:[$('marketHeadline').textContent,$('marketDetail').textContent]};},read:()=>{const before=JSON.stringify([G,rngState]);liveStatusTown=null;updateHeader();if(JSON.stringify([G,rngState])!==before)throw Error('Header mutated model/RNG');return [$('marketHeadline').textContent,$('marketDetail').textContent];}};'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[];errors=[]
 for i in range(2):
  p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://header.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://header.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',(bridge if i else '')+hook+'// SOURCE: 99-instrumentation.js'));pages.append(p)
 original,q=pages;base=original.evaluate('headerTest.seed()');cases=[]
 for i in range(5):
  case=original.evaluate('v=>headerTest.case(v.text,v.n)',{'text':base,'n':i})
  if i==0:q.evaluate('''async a=>window.real=await __workerRealView.enable(a.code,a.archive,{initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':worker,'archive':case['archive']})
  else:q.evaluate('a=>real.load(a)',case['archive'])
  actual=q.evaluate('headerTest.read()');assert actual==case['expected'],(i,actual,case['expected']);cases.append(actual)
 assert not errors,errors
 Path('experimental/worker/compact-header-proof.json').write_text(json.dumps({'syntheticPresentationBranchInputs':True,'economicPlayClaim':False,'modelRngUnchanged':True,'headlineAndDetailExact':True,'cases':cases,'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'bridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'pageErrors':errors},indent=2)+'\n');print('PASS five header branches, exact displayed text, unchanged model/RNG');b.close()
