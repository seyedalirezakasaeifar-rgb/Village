"""Synchronous-baseline refusal side effects; disposable real storage origin + spies."""
from pathlib import Path
import sys,json,hashlib,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path(os.environ.get('CAPACITY_CANDIDATE_JS',str(ROOT/'assets/game.js'))).read_text()
probe=r'''
const capacitySignature=()=>({day:G.day,treasury:G.treasury,region:G.region,total:totalMoney(),debt:G.debt,rng:rngState,people:G.people.length,households:G.households.length,firms:G.firms.length,buildings:G.buildings.length,projects:G.projects.length,loans:G.loans.length,nextLoanId:G.nextLoanId||0,nextId:G.nextId});
const capacityDecoded=text=>{const value=JSON.parse(text);return value?.format==='TownLedgerInactivePeople'?parseArchiveWithInactiveCodec(text).data:value;};
const capacityPayloadSignature=text=>{const g=capacityDecoded(text);return {day:g.day,treasury:g.treasury,region:g.region,debt:g.debt,people:g.people.length,firms:g.firms.length,buildings:g.buildings.length};};
const capacityFindSite=()=>{for(let y=2;y<T-2;y++)for(let x=2;x<T-2;x++)if(canPlace(x,y,true,'grocer'))return {x,y};throw Error('No site');};
let capacityRefuse=()=>{const site=capacityFindSite(),create=createFirm;let error='';try{createFirm=()=>null;construct('grocer',site.x,site.y);}catch(e){error=e.message;}finally{createFirm=create;}return error;};
window.__capacityEffects={
 queuedPersistence:async()=>{
  __townTest.reset('settlement',42);await saveWrites;saveStoreReady=true;
  const write=writeIndexedDB,events=[],before=capacitySignature(),originalPayload=archivePayload(),originalModel=JSON.parse(archiveLogicalPayload()),originalTown=G,originalRng=rngState;let release;
  const originalEpoch=saveEpoch;const originalSet=Storage.prototype.setItem;
  Storage.prototype.setItem=function(key,value){if(key==='townledger-v6')events.push({kind:'local-primary',signature:capacityPayloadSignature(JSON.parse(value).payload)});return originalSet.call(this,key,value);};
  let count=0;writeIndexedDB=(envelope,epoch)=>{events.push({kind:'idb-issued',epoch,revision:envelope.revision,signature:capacityPayloadSignature(envelope.payload)});return ++count===1?new Promise(resolve=>{release=resolve;}):Promise.resolve(true);};
  let committedSave,badSave,error,current,local,chronology;
  try{
   committedSave=save();error=capacityRefuse();badSave=save();
   // Deliberately restore authoritative fields only, simulating a late rollback.
   // This is a witness of external effects, not a proposed rollback algorithm.
   G=originalModel;rngState=originalRng;current=capacitySignature();
   release(true);await committedSave;await badSave;await saveWrites;
   local=readSaveEnvelope(localStorage.getItem('townledger-v6'));chronology={sameEpoch:saveEpoch===originalEpoch,revision:saveRevision,order:saveOrder};
  }finally{writeIndexedDB=write;Storage.prototype.setItem=originalSet;if(release)release(true);}
  const localSignature=capacityPayloadSignature(local.payload),badIssued=events.filter(e=>e.signature.treasury!==before.treasury);
  return {kind:'Controlled null creator refusal plus deliberate model-only rollback, with real localStorage and delayed IDB spy',before,current,local:localSignature,error,events,badExternalWrites:badIssued.length,chronology,oldTownObjectWasReplaced:originalTown!==G,restoredModelMatchesOriginal:archivePayload()===originalPayload,forbiddenPartialCommit:localSignature.treasury!==current.treasury};
 },
 deferredStartupSave:async()=>{
  __townTest.reset('settlement',42);await saveWrites;const original=archivePayload(),originalModel=JSON.parse(archiveLogicalPayload()),oldRng=rngState,oldReady=saveStoreReady,oldPromise=saveStorePromise,oldWaiting=waitingSave,persist=persistSnapshot;let release,seen=[],error='';
  try{saveStoreReady=false;waitingSave=null;saveStorePromise=new Promise(resolve=>{release=resolve;});persistSnapshot=payload=>{seen.push(payload);return Promise.resolve(true);};error=capacityRefuse();const queued=save();if(seen.length)throw Error('Deferred save serialized before store readiness');G=originalModel;rngState=oldRng;saveStoreReady=true;release();await queued;}finally{persistSnapshot=persist;saveStoreReady=oldReady;saveStorePromise=oldPromise;waitingSave=oldWaiting;if(release)release();}
  return {kind:'Ordinary startup-read save deferral, controlled model rollback before serialization',error,serializedCount:seen.length,serializedRestoredCommittedModel:seen.length===1&&seen[0]===original};
 },
 queuedUI:async()=>{
  __townTest.reset('settlement',42);await saveWrites;saveStoreReady=true;
  const before=capacitySignature(),notes=[],sequence=[],native=[],originalToast=toast,originalWrite=writeIndexedDB,originalBridge=window.AndroidArchive;let error='';
  toast=message=>{notes.push({text:message,signature:capacitySignature()});return originalToast(message);};writeIndexedDB=()=>Promise.resolve(true);window.AndroidArchive={writeBackup:payload=>native.push(capacityPayloadSignature(payload))};
  try{
   openPanel('treasury');const borrow=document.querySelector('#borrow');if(!borrow)throw Error('Real borrow control missing');
   const tasks=[
    ()=>{sequence.push('refused-construction');error=capacityRefuse();if(error)window.dispatchEvent(new ErrorEvent('error',{message:error,error:new Error(error)}));},
    ()=>{sequence.push('borrow-control');borrow.click();},
    ()=>{sequence.push('save-control');openPanel('settings');const button=document.querySelector('#saveNow');if(!button)throw Error('Real save control missing');button.click();},
    ()=>{sequence.push('native-export');exportSave();}
   ];
   await new Promise((resolve,reject)=>{const channel=new MessageChannel();channel.port1.onmessage=()=>{try{const task=tasks.shift();if(task)task();if(tasks.length)channel.port2.postMessage(0);else{channel.port1.close();channel.port2.close();resolve();}}catch(e){channel.port1.close();channel.port2.close();reject(e);}};channel.port2.postMessage(0);});await saveWrites;await Promise.resolve();
  }finally{toast=originalToast;writeIndexedDB=originalWrite;if(originalBridge===undefined)delete window.AndroidArchive;else window.AndroidArchive=originalBridge;}
  const after=capacitySignature();return {kind:'Ordered browser tasks on synchronous baseline, actual borrow/save controls, native-export bridge spy',before,after,error,sequence,notifications:notes,nativeExports:native,borrowAppliedExactlyOnce:after.debt-before.debt===5000,expectedTreasuryAfterBorrow:before.treasury+5000,forbiddenPartialFinancialCommit:after.total!==before.total,nativeExposedPartialFinancialState:native.some(e=>e.treasury!==before.treasury+5000),saveSuccessAfterPartialFailure:notes.some(e=>e.text==='Village saved on this device.')};
 },
 metadata:()=>{__townTest.reset('settlement',42);G.loans=Array.from({length:10000},(_,i)=>({id:i+1,bankId:0,ownerType:'household',ownerId:0,original:1,balance:1,rate:.1,term:360,created:1,arrears:0,status:'default',paid:0}));G.nextLoanId=10000;const before=capacitySignature(),old=archivePayload(),result=bankLoan('household',0,1000),fresh=archivePayload();return {before,after:capacitySignature(),refused:result===null,decision:G.households[0].creditDecision,persistentByteGrowth:new Blob([fresh]).size-new Blob([old]).size,ordinaryMetadataOnly:true,forbiddenFinancialCommit:totalMoney()!==before.total};}
};
'''
control=os.environ.get('CAPACITY_REFUSAL_CONTROL')=='precommit'
if control:probe+="\ncapacityRefuse=()=>{toast('Controlled refusal before mutation');return 'Controlled precommit refusal';};"
root_prototype=os.environ.get('CAPACITY_ROOT_PROTOTYPE')=='1'
if root_prototype:probe=(ROOT/'experiments/paid-root-admission.js').read_text()+'\n'+probe+"\n__paidRootPrototype.enable(true,()=>({ok:false,reason:'Controlled root refusal; grant provider not implemented'}));"
transactions=os.environ.get('CAPACITY_ROOT_TRANSACTIONS')=='1'
if transactions:
 bootstrap=(ROOT/'experiments/root-capacity-api.js').read_text()+'\n'+(ROOT/'experiments/game-capacity-root-adapter.js').read_text()+'\n'+(ROOT/'experiments/paid-command-root.js').read_text()+"\nwindow.__installGameCapacityRoot({oracleOnly:true});const rootAdmission=window.__installPaidCommandLayer();\n"
 probe=bootstrap+probe
 probe=probe.replace("__townTest.reset('settlement',42);","rootAdmission.enable(false);__townTest.reset('settlement',42);__inactivePersonCodec.enable(true);rootAdmission.enable(true);")
result={}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for name in ['queuedPersistence','deferredStartupSave','queuedUI','metadata']:
  p=b.new_page();p.route('http://capacity-review.test/**',lambda route:route.fulfill(status=200,content_type='text/html',body=html));p.goto('http://capacity-review.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result[name]=p.evaluate('__capacityEffects.'+name+'()');p.close()
 b.close()
atomic=os.environ.get('CAPACITY_EXPECT_ATOMIC')=='1'
checks={
 'queuedControlsExactlyOnce':result['queuedUI']['borrowAppliedExactlyOnce'] and len(result['queuedUI']['sequence'])==4,
 'startupDeferralUsesCommittedModel':result['deferredStartupSave']['serializedRestoredCommittedModel'],
 'rollbackModelExact':result['queuedPersistence']['restoredModelMatchesOriginal'],
 'metadataFinanciallyConserved':result['metadata']['refused'] and not result['metadata']['forbiddenFinancialCommit'],
}
if atomic:
 checks.update({'noPartialExternalCommit':not result['queuedPersistence']['forbiddenPartialCommit'] and result['queuedPersistence']['badExternalWrites']==0,'queuedFinancialConservation':not result['queuedUI']['forbiddenPartialFinancialCommit'],'nativeCommittedFinancialState':not result['queuedUI']['nativeExposedPartialFinancialState']})
 before,after=result['queuedUI']['before'],result['queuedUI']['after'];expected=dict(before);expected['treasury']+=5000;expected['region']-=5000;expected['debt']+=5000
 checks['exactQueuedFinancialAndWorldSignature']=after==expected
else:
 checks.update({'baselinePartialWriteWitness':result['queuedPersistence']['forbiddenPartialCommit'] and result['queuedPersistence']['badExternalWrites']>=2,'baselineQueuedPartialWitness':result['queuedUI']['forbiddenPartialFinancialCommit'] and result['queuedUI']['nativeExposedPartialFinancialState'],'baselineMetadataGrowth':result['metadata']['persistentByteGrowth']>0})
out={'fixtureBaseline':'6c02aadf293513d022f7a3868b52abe050202880','candidateBase':'f4f094d5c3bd7fe025a9f2a463fa795f2caf36c8','source_sha256':hashlib.sha256(source.encode()).hexdigest(),'candidateOverride':bool(os.environ.get('CAPACITY_CANDIDATE_JS')),'testOnlyPrecommitControl':control,'rootRefusalPrototype':root_prototype,'rootTransactionsEnabled':transactions,'expectation':'atomic-candidate' if atomic else 'baseline-witness','hostChromium':True,'physicalAndroid':False,'faultInjectionOnly':True,'productionGuardsEnabled':False,'prototypeGuardsInstalled':transactions or root_prototype,'checks':checks,'result':result};(ROOT/('reports/root-transaction-side-effects.json' if transactions else 'reports/paid-root-side-effects.json' if root_prototype else 'reports/capacity-side-effects-positive-control.json' if control else 'reports/capacity-side-effects-atomic.json' if atomic else 'reports/capacity-side-effects.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert all(checks.values()),'Refusal side-effect contract failed: '+','.join(k for k,v in checks.items() if not v)
