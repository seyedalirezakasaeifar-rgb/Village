from pathlib import Path
import sys,json,gzip,subprocess
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode()
bridge=Path('experimental/worker/runtime-guard.js').read_text()+Path('experimental/worker/archive-endpoint.js').read_text()+Path('experimental/worker/real-view-bridge.js').read_text()+'''window.bridgeProbe={state:()=>({day:G.day,wage:G.policy.minWage,pop:G.stats.population,frozen:Object.isFrozen(G),construction:G.construction}),lot:()=>buildableCandidates('park').find(p=>canPlace(p.x,p.y,true,'park')),savePair:async()=>{const before=saveRevision,results=await Promise.all([save(),save()]);return {before,after:saveRevision,results};},failSave:async()=>{const owner=persistSnapshot;persistSnapshot=()=>Promise.resolve(false);try{return await save();}finally{persistSnapshot=owner;}},saved:()=>readSaveEnvelope(localStorage.getItem('townledger-v6')).payload,clear:()=>localStorage.removeItem('worker-prototype-test-slot')};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(e.stack));p.route('http://worker-real.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://worker-real.test/');p.add_script_tag(content=Path('assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js',bridge+'// SOURCE: 99-instrumentation.js'))
 p.evaluate('''async args=>{window.real=await __workerRealView.enable(args.code,args.archive);}''',{'code':Path('experimental/worker/model.generated.js').read_text(),'archive':archive})
 initial=p.evaluate('bridgeProbe.state()');assert initial['frozen']
 p.locator('[data-worker="step"]').click();p.wait_for_function('bridgeProbe.state().day===41682')
 p.locator('[data-worker="policy"]').click();p.wait_for_function('v=>bridgeProbe.state().wage===v',arg=initial['wage']+1)
 p.locator('#tabs [data-panel="policies"]').click();field=p.locator('[data-policy="minWage"]');field.evaluate('e=>{for(let d=e.closest("details");d;d=d.parentElement.closest("details"))d.open=true;}');field.focus();field.press('ArrowRight');p.locator('#enactPolicy').click();p.wait_for_function('v=>bridgeProbe.state().wage===v',arg=initial['wage']+2)
 lot=p.evaluate('bridgeProbe.lot()');assert lot
 built=p.evaluate('p=>real.command({type:"build",kind:"park",x:p.x,y:p.y})',lot);assert built['built']
 bid=built['model']['buildings'][-1]['id'];inspection=p.evaluate('id=>real.inspect(id)',bid);assert inspection['inspection']['kind']=='park'
 p.locator('[data-worker="council"]').click();p.locator('[data-worker-choice]').last.click();p.wait_for_function("document.getElementById('eventDialog').style.display==='none'")
 p.locator('[data-worker="save"]').click();p.wait_for_function("window.workerRealLastSaveAck?.persisted===true");saved=p.evaluate("JSON.parse(bridgeProbe.saved())");assert saved['day']==41682
 pair=p.evaluate('bridgeProbe.savePair()');assert pair['results']==[True,True] and pair['after']==pair['before']+1,pair
 assert p.evaluate('bridgeProbe.failSave()') is False
 # Unsupported production action is visibly rejected rather than mutating stale G.
 before=p.evaluate('bridgeProbe.state()');p.locator('#tabs [data-panel="settings"]').click();p.locator('#restart').click();assert p.evaluate('bridgeProbe.state()')==before
 # Real async export/restore and existing persistence owner, with explicit completion events.
 p.evaluate("window.archiveReplies=[];document.addEventListener('worker-archive-result',e=>archiveReplies.push(e.detail))")
 admitted=p.evaluate("__workerArchiveAsync.submit({id:1,epoch:__workerArchiveAsync.status().epoch,op:'export'})");assert admitted['accepted'];p.wait_for_function('archiveReplies.length===1');exported=p.evaluate('archiveReplies[0]');assert exported['ok'] and json.loads(exported['result']['archive'])['day']==41682
 prior=p.evaluate('bridgeProbe.state()');p.evaluate("__workerArchiveAsync.submit({id:2,epoch:__workerArchiveAsync.status().epoch,op:'restore',archive:'invalid JSON'})");p.wait_for_function('archiveReplies.length===2');assert not p.evaluate('archiveReplies[1].ok') and p.evaluate('bridgeProbe.state()')==prior
 cancelled=p.evaluate("()=>{const q=__workerArchiveAsync;const a=q.submit({id:3,epoch:q.status().epoch,op:'restore',archive:'cancelled'});return q.cancel(3);}");assert cancelled['cancelled'];p.wait_for_function('archiveReplies.length===3');assert p.evaluate('bridgeProbe.state()')==prior
 p.evaluate("text=>{const q=__workerArchiveAsync,epoch=q.status().epoch;q.submit({id:4,epoch,op:'restore',archive:text});q.submit({id:5,epoch,op:'save'});}",exported['result']['archive']);p.wait_for_function('archiveReplies.length===5');assert p.evaluate('archiveReplies[3].ok') and not p.evaluate('archiveReplies[4].ok')
 p.evaluate("__workerArchiveAsync.submit({id:6,epoch:__workerArchiveAsync.status().epoch,op:'save'})");p.wait_for_function('archiveReplies.length===6');assert p.evaluate('archiveReplies[5].result.persisted')
 async_receipt=p.evaluate('archiveReplies.map(r=>({id:r.id,ok:r.ok,epoch:r.epoch,admitted:r.admitted,committed:r.committed,error:r.error||null}))');Path('experimental/worker/real-archive-proof.json').write_text(json.dumps({'actualExportRestoreSave':True,'invalidAndCancelledRestorePreserveTown':True,'queuedOldSaveRejected':True,'completions':async_receipt,'nativeJavaCallbackIntegration':False},indent=2))
 p.evaluate('bridgeProbe.clear()');assert not errors,errors
 Path('experimental/worker/real-view-proof.json').write_text(json.dumps({'realRendererFrozenSnapshot':True,'trustedStepPolicyCouncilSaveButtons':True,'actualConstructionAndInspection':True,'unsupportedRestartBlocked':True,'sourceEpochLoadAvailable':True,'productionEnvelopeReadback':True,'concurrentSaveCallersOneRevision':True,'failedOwnerWriteNotAcknowledged':True,'actualPolicyPackageControl':True,'day':saved['day'],'errors':errors,'limitations':['Paused opt-in integration only','Real build function tested via bridge command, not pointer placement trace','Full view snapshots currently required; projection schema incomplete','Unsupported controls explicitly blocked; not a release candidate','Uses actual persistSnapshot/saveEnvelope on isolated browser origin; native restore/export blocked pending async contract']},indent=2));print('PASS real readonly map, day/policy controls, build/inspect and acknowledged test save');b.close()
