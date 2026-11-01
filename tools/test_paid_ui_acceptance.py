"""Actual UI council/ack/write gate. Pending candidate, never production enable.
Requires published composed worker bundle, host source and bridge directory.
No owner or financial implementation is injected by this runner.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--worker-code',required=True);ap.add_argument('--host-source',required=True);ap.add_argument('--bridge-dir',required=True);ap.add_argument('--init-type');ap.add_argument('--oracle-commit',default='669c908706af997375680674390e46fd132a970a');ap.add_argument('--reference-dry-run',action='store_true');args=ap.parse_args()
source=Path(args.host_source).read_text();oracle=subprocess.check_output(['git','show',args.oracle_commit+':assets/game.js'],text=True);worker=Path(args.worker_code).read_text();directory=Path(args.bridge_dir);bridge='\n'.join((directory/n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js']);probe=(ROOT/'tools/fixtures/paid-ui-acceptance-probe.js').read_text()
out={'oracleCommit':args.oracle_commit,'oracleSha256':hashlib.sha256(oracle.encode()).hexdigest(),'hostSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'bridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'referenceDryRun':args.reference_dry_run,'productionEnabled':False,'nativeDurability':False,'checks':{}}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=b.new_context(viewport={'width':1000,'height':800});errors=[]
 def page(origin,code):
  p=context.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.route(origin+'/**',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto(origin+'/paid-ui-acceptance');p.add_script_tag(content=code.replace('// SOURCE: 99-instrumentation.js',probe+'\n'+(bridge if origin.endswith('127.0.0.1') else '')+'\n// SOURCE: 99-instrumentation.js'));return p
 p=page('http://localhost',oracle);q=page('http://127.0.0.1',source);archive=p.evaluate('__paidUiProbe.prepareOracle()');q.evaluate('async v=>window.real=await __workerRealView.enable(v.code,v.archive)',{'code':worker,'archive':archive});status=q.evaluate('real.command({type:"paid-status"})')
 if not status['configured']:
  if not args.init_type:raise RuntimeError('BLOCKED: candidate owner not installed; supply its published finite init command')
  q.evaluate('t=>real.command({type:t})',args.init_type)
 q.evaluate('__paidUiProbe.attach(real.worker)')
 for page in [p,q]:page.locator('#tabs [data-panel="agenda"]').click()
 q.evaluate('real.settlePanels()');q.evaluate('real.settleSaves()')
 for page in [p,q]:page.locator('[data-inbox="0"]').first.click()
 q.wait_for_function('document.querySelector("#eventDialog").style.display==="flex"');q.evaluate('real.settlePanels()');q.evaluate('real.settleSaves()');assert p.locator('#eventTitle').inner_text()==q.locator('#eventTitle').inner_text()
 before=q.evaluate('__paidUiProbe.snapshot()');beforeModel=q.evaluate('__paidUiProbe.canonical()');q.evaluate('__paidUiProbe.writerMode("hold");__paidUiProbe.holdCommit(true)');p.locator('#eventChoices button').first.click();button=q.locator('#eventChoices [data-worker-choice]').first;box=button.bounding_box();button.click();q.wait_for_function('__paidUiProbe.snapshot().heldReplies===1');held=q.evaluate('__paidUiProbe.snapshot()')
 out['checks']['visiblePendingBeforeAcknowledgment']=bool(held['busyMarkers']);out['checks']['oldFrozenModelUntilAcknowledgment']=held['frozen'] and q.evaluate('__paidUiProbe.canonical()')==beforeModel
 q.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2);q.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2)
 during=q.evaluate('__paidUiProbe.snapshot()');out['checks']['duplicateTapsSubmitOneChoice']=sum(x['type']=='choice' for x in during['posted'])-sum(x['type']=='choice' for x in before['posted'])==1
 out['checks']['noWriteBeforeCommitAcknowledgment']=len(during['writes'])==len(before['writes']);q.evaluate('__paidUiProbe.releaseCommit()');q.wait_for_function('__paidUiProbe.snapshot().heldWrites>0');q.evaluate('real.settlePanels()');committed=q.evaluate('__paidUiProbe.snapshot()');actual=json.loads(q.evaluate('__paidUiProbe.canonical()'));expected=json.loads(p.evaluate('__paidUiProbe.canonical()'));out['checks']['entireCurrentOracleModelAndRng']=actual==expected
 out['checks']['noDurableAckBeforeWriter']=sum(x['type']=='save-ack' for x in committed['posted'])==sum(x['type']=='save-ack' for x in before['posted']);out['checks']['modelCommittedWhileWritePending']=committed['heldWrites']>0 and committed['frozen']
 q.evaluate('__paidUiProbe.writerMode("normal");__paidUiProbe.releaseWrites(true)');q.evaluate('real.settleSaves()');final=q.evaluate('__paidUiProbe.snapshot()');stored=q.evaluate('__paidUiProbe.decodedStored()');out['checks']['originalWebWriterReadbackExact']=stored==actual;out['checks']['tokenAckAfterVerifiedWriter']=sum(x['type']=='save-ack' for x in final['posted'])>sum(x['type']=='save-ack' for x in before['posted']);out['checks']['noUncaughtPageErrors']=not errors
 out['pendingMarkers']=held['busyMarkers'];out['errors']=errors;out['checks']['productionCommandOwner']=not args.reference_dry_run and q.evaluate('real.command({type:"paid-status"})').get('referenceTestOwner') is False;out['currentModelCovered']=args.oracle_commit=='669c908706af997375680674390e46fd132a970a';out['allChecksPass']=all(out['checks'].values());out['blockedOrFailingChecks']=[k for k,v in out['checks'].items() if not v];b.close()
path=ROOT/'reports/current-paid-worker-audit/actual-ui-acceptance.json';path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));sys.exit(0 if out['allChecksPass'] else 1)
