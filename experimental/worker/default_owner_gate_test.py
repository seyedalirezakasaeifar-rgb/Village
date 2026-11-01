"""Default experimental bundle never claims command admission or writes an empty town."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text();assert 'window.__installPaidCommandOwner=function' not in code and 'window.__installCurrentPaidTestOwner=function' not in code
bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js'])+'window.emptySave=()=>save();\n'
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.route('http://empty-owner.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://empty-owner.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bridge+'// SOURCE: 99-instrumentation.js'));p.evaluate('async code=>{window.real=await __workerRealView.enable(code,null);return true;}',code);status=p.evaluate('real.command({type:"paid-status"})');assert not status['configured'] and not status['enabled'] and not status['productionAdmissionCertified'];assert p.evaluate('emptySave()') is False
 reply=p.evaluate('''async()=>{const api=__workerArchiveAsync,s=api.status();return await new Promise((resolve,reject)=>{const handler=e=>{document.removeEventListener('worker-archive-result',handler);resolve(e.detail);};document.addEventListener('worker-archive-result',handler);const accepted=api.submit({session:s.session,id:1,epoch:s.epoch,op:'save'});if(!accepted.accepted)reject(Error(accepted.error));});}''');assert reply['ok'] and not reply['committed'] and reply['result']['empty'] and not reply['result']['persisted'];assert p.evaluate('localStorage.getItem("townledger-v6")') is None
 Path('experimental/worker/default-owner-gate-proof.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'defaultWorkerSha256':hashlib.sha256(code.encode()).hexdigest(),'bothOwnersAbsent':True,'noAdmissionClaim':True,'emptySaveNotPersistedOrCommitted':True,'emptySaveDoesNotWrite':True},indent=2)+'\n');print('PASS default bundle no admission claim and no false empty-save acknowledgment');b.close()
