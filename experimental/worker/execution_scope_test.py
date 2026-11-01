"""Actual model, trusted scope hook, default refusal and completed-batch barriers."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text()
# Test controls are appended only to this in-memory test bundle.
code+='''
const scopeOriginal=self.onmessage;let scopeRelease=null,scopeRead=null,scopeOwner=null,scopeCaptures=[];
self.onmessage=e=>{const m=e.data;
if(m.type==='scope-install'){const owner=__installCurrentPaidTestOwner();owner.workerExecution={version:1,mode:'paid-command',bind:read=>{scopeRead=read;},readyForOrdinaryDay:()=>false};owner.registerRuntime({capture:()=>{scopeCaptures.push(scopeRead().mode);return {};},restore:()=>{}});workerInstallPaidOwner(owner);__rootAdmission.enable(true);scopeOwner=owner;self.postMessage({id:m.id,ok:true,result:{epoch:workerEpoch}});return;}
if(m.type==='scope-info'){self.postMessage({id:m.id,ok:true,result:{epoch:workerEpoch,context:workerExecutionContext(),metrics:scopeOwner?.metrics(),captures:scopeCaptures}});return;}
if(m.type==='scope-invalid'){try{workerInstallPaidOwner({shared:__capacityAdmissionProtocol.shared,registerRuntime:()=>{}});throw Error('Accepted undeclared scope');}catch(error){self.postMessage({id:m.id,ok:true,result:{epoch:workerEpoch,error:String(error)}});}return;}
if(m.type==='scope-hold'){workerYield=()=>new Promise(r=>scopeRelease=r);self.postMessage({id:m.id,ok:true,result:{epoch:workerEpoch}});return;}
if(m.type==='scope-release'){scopeRelease();self.postMessage({id:m.id,ok:true,result:{epoch:workerEpoch}});return;}
scopeOriginal(e);};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',"window.scopeFixture=()=>{seed(42);paused=true;for(let i=0;i<19;i++)tick();return archivePayload();};\n// SOURCE: 99-instrumentation.js"));archive=p.evaluate('scopeFixture()')
 p.evaluate('''code=>{let serial=0,epoch=0;window.w=new Worker(URL.createObjectURL(new Blob([code])));window.ask=m=>new Promise(r=>{let id=++serial;setTimeout(()=>r({ok:false,error:'Test request timeout: '+m.type}),10000);const h=e=>{if(e.data.id!==id)return;w.removeEventListener('message',h);if(e.data.ok)epoch=e.data.result.epoch;r(e.data);};w.addEventListener('message',h);w.postMessage({id,command:id,epoch,...m});});}''',code)
 def good(m):
  print('request',m['type'],flush=True);r=p.evaluate('m=>ask(m)',m);assert r['ok'],r;return r['result']
 good({'type':'load','archive':archive});invalid=good({'type':'scope-invalid'});assert 'must declare' in invalid['error'];good({'type':'scope-hold'});p.evaluate('()=>{window.held=ask({type:"step",days:1});return true;}');p.wait_for_timeout(30)
 rejected=[]
 for kind,extra in [('choice',{'eventId':1,'index':0}),('private-provider',{'providerKind':'school'}),('convene',{}),('load',{'archive':archive}),('policy',{'key':'minWage','value':12})]:
  r=p.evaluate('m=>ask(m)',{'type':kind,**extra});assert not r['ok'] and 'completed-day batch' in r['error'],r;rejected.append(kind)
 heldExport=good({'type':'export'});good({'type':'scope-release'});done=p.evaluate('held');assert done['ok'];assert done['result']['model']==heldExport['model']
 good({'type':'scope-install'});before=good({'type':'export'});stats=good({'type':'scope-info'});denied=p.evaluate('ask({type:"step",days:1})');assert not denied['ok'] and 'local creator safety' in denied['error'];after=good({'type':'export'});assert before['model']==after['model'];unchanged=good({'type':'scope-info'});assert unchanged['metrics']['captures']==stats['metrics']['captures']==0;assert unchanged['metrics']['certificates']==stats['metrics']['certificates'];assert unchanged['context']['mode']=='idle'
 review=good({'type':'convene'});event=next(e['payload'] for e in review['outbox'] if e['type']=='council-event');index=next(c['index'] for c in event['choices'] if c['cost']<=review['model']['treasury']);choice=good({'type':'choice','eventId':event['id'],'index':index});assert choice['paid']['committed'];scoped=good({'type':'scope-info'});assert scoped['captures']==['paid-command'];assert scoped['metrics']['captures']==1;assert scoped['context']['mode']=='idle'
 Path('experimental/worker/execution-scope-proof.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'instrumentedWorkerSha256':hashlib.sha256(code.encode()).hexdigest(),'testOwnerOnly':True,'undeclaredOwnerRefused':True,'batchRejectedKinds':rejected,'completedBoundaryExportUnchanged':True,'missingAutomaticSafetyRefusesBeforeDay':True,'refusedDayZeroSnapshotsCertificates':True,'initialEnableCertificates':stats['metrics']['certificates'],'refusedDayCertificateDelta':unchanged['metrics']['certificates']-stats['metrics']['certificates'],'paidCommandCaptureScopes':scoped['captures'],'trustedScopeRestoresIdle':True,'productionOwnerInstalled':False,'automaticCompletionSafetyClaimed':False},indent=2)+'\n');print('PASS trusted paid scope, failclosed ordinary-day readiness and batch command barriers');b.close()
