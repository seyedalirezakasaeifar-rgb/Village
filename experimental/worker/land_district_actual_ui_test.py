"""Actual UI council/ack/write gate. Pending candidate, never production enable.
Requires published composed worker bundle, host source and bridge directory.
No owner or financial implementation is injected by this runner.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();oracle=subprocess.check_output(['git','show','01eeda3:assets/game.js']).decode();worker=Path('experimental/worker/model.generated.js').read_text();bridge='\n'.join(Path('experimental/worker',n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js']);probe=Path('tools/fixtures/paid-ui-acceptance-probe.js').read_text();bindings=json.loads(Path('experimental/worker/route-bindings.generated.json').read_text())
probe+="\nwindow.landUiFixture=()=>{chosenScenario='settlement';seed(42);G.autoBuild=false;paused=true;active='';pendingEvent=null;$('welcome').style.display='none';return archivePayload();};\n"
out={'sourceCommit':'97b761e current01eeda hooks plus completed land module','oracleSha256':hashlib.sha256(oracle.encode()).hexdigest(),'hostSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'bridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'referenceDryRun':False,'productionEnabled':False,'nativeDurability':False,'checks':{}}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=b.new_context(viewport={'width':1000,'height':800});errors=[]
 def page(origin,code):
  p=context.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.route(origin+'/**',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto(origin+'/paid-ui-acceptance');p.add_script_tag(content=code.replace('// SOURCE: 99-instrumentation.js',probe+'\n'+(bridge if origin.endswith('127.0.0.1') else '')+'\n// SOURCE: 99-instrumentation.js'));return p
 p=page('http://localhost',oracle);q=page('http://127.0.0.1',source);archive=p.evaluate('landUiFixture()');q.evaluate('''async v=>window.real=await __workerRealView.enable(v.code,v.archive,{routeBindings:v.bindings,initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':worker,'archive':archive,'bindings':bindings});status=q.evaluate('real.command({type:"paid-status"})')
 assert status['configured'] and status['enabled'] and not status['referenceTestOwner']
 q.evaluate('__paidUiProbe.attach(real.worker)')
 for page in [p,q]:
  page.locator('#tabs [data-panel="construction"]').click()
  page.locator('#charterOffice>summary').click()
 q.evaluate('real.settlePanels()');q.evaluate('real.settleSaves()')
 for page in [p,q]:page.locator('[data-parcel-buy="east-meadow"]').click()
 q.wait_for_function('document.querySelector("#eventDialog").style.display==="flex"');q.evaluate('real.settlePanels()');q.evaluate('real.settleSaves()');assert p.locator('#eventTitle').inner_text()==q.locator('#eventTitle').inner_text()
 before=q.evaluate('__paidUiProbe.snapshot()');beforeModel=q.evaluate('__paidUiProbe.canonical()');q.evaluate('__paidUiProbe.writerMode("hold");__paidUiProbe.holdCommit(true)');p.locator('#eventChoices button').first.click();button=q.locator('#eventChoices [data-worker-choice]').first;box=button.bounding_box();button.click();q.wait_for_function('__paidUiProbe.snapshot().heldReplies===1');held=q.evaluate('__paidUiProbe.snapshot()')
 out['checks']['visiblePendingBeforeAcknowledgment']=bool(held['busyMarkers']);out['checks']['oldFrozenModelUntilAcknowledgment']=held['frozen'] and q.evaluate('__paidUiProbe.canonical()')==beforeModel
 q.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2);q.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2)
 during=q.evaluate('__paidUiProbe.snapshot()');out['checks']['duplicateTapsSubmitOneChoice']=sum(x['type']=='choice' for x in during['posted'])-sum(x['type']=='choice' for x in before['posted'])==1
 out['checks']['noWriteBeforeCommitAcknowledgment']=len(during['writes'])==len(before['writes']);q.evaluate('__paidUiProbe.releaseCommit()');q.wait_for_function('__paidUiProbe.snapshot().heldWrites>0');q.evaluate('real.settlePanels()');committed=q.evaluate('__paidUiProbe.snapshot()');actual=json.loads(q.evaluate('__paidUiProbe.canonical()'));expected=json.loads(p.evaluate('__paidUiProbe.canonical()'));out['checks']['entireCurrentOracleModelAndRng']=actual==expected
 out['checks']['noDurableAckBeforeWriter']=sum(x['type']=='save-ack' for x in committed['posted'])==sum(x['type']=='save-ack' for x in before['posted']);out['checks']['modelCommittedWhileWritePending']=committed['heldWrites']>0 and committed['frozen']
 q.evaluate('__paidUiProbe.writerMode("normal");__paidUiProbe.releaseWrites(true)');q.evaluate('real.settleSaves()');final=q.evaluate('__paidUiProbe.snapshot()');stored=q.evaluate('__paidUiProbe.decodedStored()');out['checks']['originalWebWriterReadbackExact']=stored==actual;out['checks']['tokenAckAfterVerifiedWriter']=sum(x['type']=='save-ack' for x in final['posted'])>sum(x['type']=='save-ack' for x in before['posted']);out['checks']['noUncaughtPageErrors']=not errors
 
 # A second real deed commits once even if the original storage writer refuses.
 for page in [p,q]:
  button=page.locator('[data-parcel-buy="county-ridge"]')
  while button.evaluate('(b)=>{for(let p=b.parentElement;p;p=p.parentElement)if(p.tagName==="DETAILS"&&!p.open)return true;return false;}'):
   button.evaluate('(b)=>{let closed=[];for(let p=b.parentElement;p;p=p.parentElement)if(p.tagName==="DETAILS"&&!p.open)closed.push(p);closed[closed.length-1].querySelector(":scope > summary").click();}')
  button.click()
 q.wait_for_function('document.querySelector("#eventDialog").style.display==="flex"');q.evaluate('real.settlePanels()');q.evaluate('real.settleSaves()');prior=q.evaluate('__paidUiProbe.snapshot()');saved_first=q.evaluate('__paidUiProbe.decodedStored()');q.evaluate('__paidUiProbe.writerMode("fail")');p.locator('[data-event-choice="0"]').click();q.locator('[data-worker-choice="0"]').click();q.wait_for_function('document.querySelector("#eventDialog").style.display==="none"');q.evaluate('real.settlePanels()');q.evaluate('real.settleSaves()');failed=q.evaluate('__paidUiProbe.snapshot()');failed_model=json.loads(q.evaluate('__paidUiProbe.canonical()'))
 out['checks']['failedWriterKeepsCommittedSecondDeedExact']=failed_model==json.loads(p.evaluate('__paidUiProbe.canonical()'))
 out['checks']['failedWriterPreservesPriorVerifiedSave']=q.evaluate('__paidUiProbe.decodedStored()')==saved_first
 out['checks']['failedWriterDoesNotAck']=sum(x['type']=='save-ack' for x in failed['posted'])==sum(x['type']=='save-ack' for x in prior['posted'])
 choices_before=sum(x['type']=='choice' for x in failed['posted']);p.locator('#tabs [data-panel="settings"]').click();q.evaluate('__paidUiProbe.writerMode("normal")');q.locator('#tabs [data-panel="settings"]').click();q.evaluate('real.settlePanels()');q.locator('#saveNow').click();q.evaluate('real.settleSaves()');retried=q.evaluate('__paidUiProbe.snapshot()')
 retry_model=json.loads(q.evaluate('__paidUiProbe.canonical()'));retry_oracle=json.loads(p.evaluate('__paidUiProbe.canonical()'));out['checks']['actualSaveNowRetryWritesCommittedModel']=q.evaluate('__paidUiProbe.decodedStored()')==retry_model and retry_model==retry_oracle
 out['checks']['actualSaveNowRetryDoesNotReplayPayment']=all(retry_model[k]==failed_model[k] for k in ['treasury','region','charter','cumulative','construction','nextId']) and sum(x['type']=='choice' for x in retried['posted'])==choices_before
 out['checks']['retryDurableAckAfterWriter']=sum(x['type']=='save-ack' for x in retried['posted'])>sum(x['type']=='save-ack' for x in failed['posted'])
 out['pendingMarkers']=held['busyMarkers'];out['errors']=errors;out['checks']['productionCommandOwner']=q.evaluate('real.command({type:"paid-status"})').get('referenceTestOwner') is False;out['oracleCommit']='01eeda3d2ff09822b9422721f75e97fabbc9958a';out['currentPublicModelPortAccepted']=out['checks']['entireCurrentOracleModelAndRng'];out['scope']='actual two-deed bindings, pending/duplicate/ACK, original writer failure and actual Save Now retry only';out['allChecksPass']=all(out['checks'].values());out['blockedOrFailingChecks']=[k for k,v in out['checks'].items() if not v];b.close()
path=ROOT/'experimental/worker/land_district_actual_ui_proof.json';path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));sys.exit(0 if out['allChecksPass'] else 1)
