from pathlib import Path
import json
from playwright.sync_api import sync_playwright
guard=Path('experimental/worker/runtime-guard.js').read_text();worker=Path('experimental/worker/model.generated.js').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.add_script_tag(content=guard)
 page=p.evaluate('workerRuntimeArithmetic()');assert page['ok'],page
 setup='''code=>{window.guardWorker=new Worker(URL.createObjectURL(new Blob([code],{type:'application/javascript'})));let serial=0;window.askGuard=m=>new Promise(resolve=>{const id=++serial;const h=e=>{if(e.data.id===id){guardWorker.removeEventListener('message',h);resolve(e.data);}};guardWorker.addEventListener('message',h);guardWorker.postMessage({...m,id});});}'''
 p.evaluate(setup,worker);status=p.evaluate("askGuard({type:'runtime-status'})");assert status['ok'] and status['result']['ok'];p.evaluate('guardWorker.terminate()')
 faulty=worker.replace('const workerRuntimeStatus=workerRuntimeArithmetic();',"const workerRuntimeStatus={ok:false,checks:[{op:'injected-test-failure'}]};")
 p.evaluate(setup,faulty);rejected=p.evaluate("askGuard({type:'load',archive:'not JSON'})");assert not rejected['ok'] and 'UNSUPPORTED_INTEGER_RUNTIME' in rejected['error']
 after=p.evaluate("askGuard({type:'runtime-status'})");assert after['result']['epoch']==0
 choices=p.evaluate("[workerRuntimeFallback({ok:true},{ok:false}),workerRuntimeFallback({ok:false},{ok:true}),workerRuntimeFallback({ok:true},{ok:true})]");assert choices==['synchronous','unsupported-runtime','worker']
 receipt={'page':page,'worker':status['result'],'faultInjectedLoadRejectedBeforeParse':True,'rejectedEpochUnchanged':True,'fallbackModes':choices,'limitations':['Host Chromium only','Injected failure tests rejection, not emulator acceptance','No saved RNG algorithm changed']}
 Path('experimental/worker/runtime-guard-proof.json').write_text(json.dumps(receipt,indent=2));print('PASS dynamic arithmetic self-test; failed worker refuses model admission; safe fallback selection');b.close()
