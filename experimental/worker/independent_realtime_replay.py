"""Actual live worker clock and paid UI, replayed by the untouched existing model.
Only the oracle uses __townTest.step with the actually admitted completed-day count.
No financial field projection, RNG adjustment or second simulation implementation.
"""
from pathlib import Path
import json,gzip,hashlib,subprocess,sys
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
ref='87811c52cdb9aecd13cd23beebd52f6475c6dd9c';original=subprocess.check_output(['git','show',ref+':assets/game.js']).decode();source=Path('assets/game.js').read_text();bridge=Path('experimental/worker/real-view.generated.js').read_text();worker=Path('experimental/worker/model.generated.js').read_text();archive=gzip.decompress(Path('experimental/worker/fixtures/market-ordinary-current.json.gz').read_bytes()).decode();probe=subprocess.check_output(['git','show','856f944:tools/fixtures/realtime-player-journey-probe.js']).decode();hook='''window.liveReplay={load:a=>{if(!hydrateSave(a))throw Error('Original old-save restore rejected');paused=true;active='';$('welcome').style.display='none';return archivePayload();},archive:()=>archivePayload(),replay:n=>{__townTest.step(n);return archivePayload();},close:()=>closePanel()};''';rows=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for candidate,src,origin in [(False,original,'http://replay-oracle.test/'),(True,source,'http://replay-worker.test/')]:
  p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.route(origin+'**',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto(origin);p.add_script_tag(content=src.replace('// SOURCE: 99-instrumentation.js',(bridge if candidate else '')+probe+hook+'\n// SOURCE: 99-instrumentation.js'));pages.append(p)
 oracle,p=pages;canonical=oracle.evaluate('a=>liveReplay.load(a)',archive);p.evaluate('''async a=>window.real=await __workerRealView.enable(a.worker,a.archive,{realtime:true,startPaused:true,initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'worker':worker,'archive':canonical});p.evaluate('liveReplay.close()');p.evaluate('real.settlePanels()')
 def settle():p.evaluate('async()=>{await real.settleRealtime();await real.settlePanels();await real.settleSaves();await real.settleRealtime();}')
 def exact(label):
  actual=p.evaluate('real.command({type:"export"})');expected=json.loads(oracle.evaluate('liveReplay.archive()'))
  if actual['model']!=expected:Path('/tmp/independent-live-replay-diff.json').write_text(json.dumps({'label':label,'actual':actual['model'],'expected':expected}));print('DIFF',label,[k for k in set(actual['model'])|set(expected) if actual['model'].get(k)!=expected.get(k)],flush=True)
  assert actual['model']==expected,label;assert actual['rng']==expected['rngState'];rows.append({'label':label,'day':actual['day'],'rng':actual['rng'],'requested':p.evaluate('real.realtimeStatus().requested')});return actual
 exact('old-save-initial-complete-state')
 for rate in [8,16]:
  for page in [oracle,p]:page.locator('#speedRange').fill(str([1,2,4,8,16,32,64].index(rate)));page.locator('#speedRange').dispatch_event('change')
  settle();start=p.evaluate('real.realtimeStatus().committedDay');p.locator('#pause').click();p.wait_for_function('d=>real.realtimeStatus().committedDay>=d+3',arg=start,timeout=30000);p.locator('#pause').click();settle();status=p.evaluate('real.realtimeStatus()');days=status['committedDay']-start;assert days>=3 and status['paused'];oracle.evaluate('n=>liveReplay.replay(n)',days);r=exact('live-'+str(rate)+'x-admitted-'+str(days)+'-days');p.wait_for_timeout(250);assert p.evaluate('real.realtimeStatus().committedDay')==status['committedDay'];rows[-1].update(admittedDays=days,owedPreserved=status['owedDays'],pausedStable=True)
  if rate==8:
   site=oracle.evaluate('__playerJourney.site("park")');assert site
   for page in [oracle,p]:
    page.locator('#tabs [data-panel="construction"]').click()
    if page==p:settle()
    button=page.locator('[data-build="park"]').first;button.evaluate('(b)=>{for(let d=b.parentElement;d;d=d.parentElement)if(d.tagName==="DETAILS")d.open=true;}');button.click();page.evaluate('v=>__townTest.capture(v)',page.evaluate('v=>__playerJourney.world(v.x,v.y)',site));point=page.evaluate('v=>__playerJourney.point(v.x,v.y)',site);page.mouse.click(point['x'],point['y'])
    if page==p:settle()
    page.keyboard.press('Escape')
   settle();exact('paid-park-after-live-boundary')
 assert not errors,errors
 Path('experimental/worker/independent-realtime-replay.json').write_text(json.dumps({'candidateCommit':'a649a55ccb752b6f1fd170e9f0689edb92dff34c','oracleCommit':ref,'oracleSha256':hashlib.sha256(original.encode()).hexdigest(),'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'bridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'actualWorkerUiClockAndConstruction':True,'oracleUsesExistingModelWithActualAdmittedCounts':True,'excludedFields':[],'notPerformanceBenchmark':True,'rows':rows,'pageErrors':errors},indent=2)+'\n');print('PASS exact full-state/RNG actual live day replay and intervening paid park',rows,flush=True);b.close()
