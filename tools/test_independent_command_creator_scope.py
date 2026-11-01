"""Independent actual worker/owner creator scope test; test hooks never shipped."""
from pathlib import Path
import sys,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();base=(ROOT/'experimental/worker/model.generated.js').read_text();commit='f77ceddbba004d120a1f40ea90a9ac5037b061f2';paid_commit='e13a21b80efb80561b60ec41cda7a1c938cca5e1'
original=subprocess.check_output(['git','show',commit+':experiments/paid-command-root.js'],text=True);paid=subprocess.check_output(['git','show',paid_commit+':experiments/paid-command-root.js'],text=True);owner=subprocess.check_output(['git','show',paid_commit+':experiments/paid-command-owner.js'],text=True);assert original in base
instrumentedOwner=owner.replace('certify:meta=>{','certify:meta=>{globalThis.__integrityCertificates=(globalThis.__integrityCertificates||0)+1;',1)
code=base.replace(original,paid)+'\n'+instrumentedOwner
hook=r'''
const independentBaseHandler=self.onmessage,independentCreator=createFirm,independentWork=constructionWork;
let independentFault=false;
createFirm=function(){if(independentFault)return null;return independentCreator.apply(this,arguments);};
constructionWork=function(p){return p.integrityProbe===true?true:false;};
self.onmessage=e=>{const m=e.data;try{
 if(m.type==='integrity-init'){const o=__installPaidCommandOwner({automaticCreators:{version:1,sourceCommit:'c91475af7dd079a51a72eb89b413673adae886c1',preflight:creatorCapacityReason}});workerInstallPaidOwner(o);if(!__rootAdmission.enable(true))throw Error('Owner enable refused');self.postMessage({id:m.id,ok:true,result:{epoch:workerEpoch,ready:o.workerExecution.readyForOrdinaryDay()}});return;}
 if(m.type==='integrity-fault'){independentFault=m.value;self.postMessage({id:m.id,ok:true,result:{epoch:workerEpoch}});return;}
 if(m.type==='integrity-metrics'){self.postMessage({id:m.id,ok:true,result:{epoch:workerEpoch,metrics:__paidCommandOwner.metrics(),certificates:globalThis.__integrityCertificates||0,scope:workerExecutionContext()}});return;}
 if(m.type==='integrity-phase'){
  const before=archivePayload(),rng=rngState,money=totalMoney(),ids=G.nextId;workerStepping=true;simulationTickActive=true;try{workerInScope('ordinary-day',()=>{if(m.phase==='completion')completeDevelopmentProjects();else if(m.phase==='people'){birthsAndGenerations();migrationFamilyArrivalDay();}else if(m.phase==='households'){householdFormation();for(const b of G.buildings)if(b.kind==='home')addHouseholdAt(b);}});}finally{workerStepping=false;simulationTickActive=false;}
  self.postMessage({id:m.id,ok:true,result:{epoch:workerEpoch,exact:archivePayload()===before,rngExact:rng===rngState,moneyExact:money===totalMoney(),idsExact:ids===G.nextId}});return;
 }
 }catch(error){self.postMessage({id:m.id,ok:false,error:String(error)});return;}return independentBaseHandler(e);};
'''
code+='\n'+hook
fixture=r'''
save=()=>true;window.__integrityFixture=kind=>{
 chosenScenario='settlement';seed(42);paused=true;for(let n=0;n<30;n++)tick();pendingEvent=null;active='';
 const estate=()=>({id:G.firms.length,building:-1,kind:'grocer',name:'Synthetic retained estate',closed:true,demolished:true,cash:0,stock:{},jobs:0,workers:[],wage:30,price:5,owner:-1,deposits:{},history:[],age:100,debt:0,revenue:0,expenses:0,profit:0,tax:0});
 if(kind==='competition'){
  const pending=G.projects.filter(p=>p.kind==='firm'||p.kind==='airport').length;while(G.firms.length<2998-pending)G.firms.push(estate());
  for(let n=0;n<2;n++){let site;for(let y=2;y<T-2&&!site;y++)for(let x=2;x<T-2;x++)if(canPlace(x,y,true,'grocer')){site={x,y};break;}const b=startDevelopmentProject('firm',site,100,1,{firmKind:'grocer',capital:100,integrityProbe:true});if(!b)throw Error('Subject site not admitted');}
  while(G.firms.length<2999)G.firms.push(estate());
 }
 if(kind==='people') {while(G.people.length<8000)G.people.push({id:G.people.length,name:'Synthetic retained person',age:90,skill:.1,health:0,hh:0,job:-1,deceased:true,last:[]});G.day=90;}
 if(kind==='households'){while(G.households.length<3000)G.households.push({id:G.households.length,name:'Synthetic retained estate',people:[],cash:0,deposits:{},home:-1,owner:-1,stress:0});G.day=90;}
 G.rngState=rngState;G.visualState=visualState;return archivePayload();
};
'''
out={'workerCommit':commit,'paidCommit':paid_commit,'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'baseWorkerSha256':hashlib.sha256(base.encode()).hexdigest(),'instrumentedWorkerSha256':hashlib.sha256(code.encode()).hexdigest(),'ownerSha256':hashlib.sha256(owner.encode()).hexdigest(),'instrumentedOwnerSha256':hashlib.sha256(instrumentedOwner.encode()).hexdigest(),'certificateCounterOnlyInstrumentation':True,'controlledConstructionReadiness':True,'stubCreatorOnlyInExplicitFault':True,'productionActivation':False,'nativeStorageTested':False,'cases':{}}
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.evaluate('window.requestAnimationFrame=()=>0');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',fixture+'\n// SOURCE: 99-instrumentation.js'))
 fixtures={kind:p.evaluate('kind=>__integrityFixture(kind)',kind) for kind in ['small','competition','people','households']}
 p.evaluate('''()=>{let serial=0;window.epoch=0;window.createIntegrityWorker=code=>{window.iw?.terminate();window.epoch=0;window.iw=new Worker(URL.createObjectURL(new Blob([code])));};window.askIntegrity=m=>new Promise((resolve,reject)=>{const id=++serial,w=iw,t=setTimeout(()=>{w.removeEventListener('message',h);reject(Error('Timeout '+m.type));},45000);const h=e=>{if(e.data.id!==id)return;clearTimeout(t);w.removeEventListener('message',h);if(e.data.ok&&e.data.result.epoch!==undefined)epoch=e.data.result.epoch;resolve(e.data);};w.addEventListener('message',h);w.postMessage({id,command:id,epoch,...m});});}''')
 def ask(**m):return p.evaluate('m=>askIntegrity(m)',m)
 def good(**m):
  r=ask(**m);assert r['ok'],r;return r['result']
 def fresh(kind):
  p.evaluate('code=>createIntegrityWorker(code)',code);good(type='load',epoch=0,archive=fixtures[kind]);assert good(type='integrity-init')['ready'];return good(type='export')
 before=fresh('competition');baseline=good(type='integrity-metrics');completed=good(type='step',days=1);after=good(type='export');g=json.loads(after['archive']);subject=[x for x in g['projects'] if x.get('integrityProbe')];assert len(g['firms'])==3000 and len(subject)==1 and subject[0]['remaining']==1 and 'capacity' in subject[0]['reason'];assert not good(type='integrity-metrics')['metrics']['samples'];assert good(type='integrity-metrics')['certificates']==baseline['certificates'];
 blocked=good(type='integrity-phase',phase='completion');assert all(blocked[k] for k in ['exact','rngExact','moneyExact','idsExact']);assert not good(type='integrity-metrics')['metrics']['samples'];out['cases']['competition']={'actualStepOneSlotExactlyOneCompletion':True,'oldOverbookedProjectPreserved':True,'blockedPhaseExactArchiveMoneyIdsRng':True,'ordinaryCaptureSamples':0,'ordinaryCertificateDelta':0,'scopeIdleAfterStep':good(type='integrity-metrics')['scope']['mode']=='idle'}
 # Forced null after legitimate funding: only the failure fence may claim safety.
 prior=fresh('competition');prepared=good(type='save-prepare');assert prepared['archive']==prior['archive'];good(type='integrity-fault',value=True);failed=ask(type='step',days=1);assert not failed['ok'];fences={}
 for kind in ['export','save-prepare','step']:
  r=ask(type=kind,**({'days':1} if kind=='step' else {}));assert not r['ok'],r;fences[kind]=r.get('error')
 good(type='integrity-fault',value=False);restored=good(type='load',archive=prepared['archive']);assert restored['model']==prior['model'];recovered=good(type='step',days=1);assert recovered['model']==completed['model'];assert not good(type='integrity-metrics')['metrics']['samples'];out['cases']['forcedCreatorFailure']={'failure':failed.get('error'),'noPartialSuccess':True,'fences':fences,'lastCompletedArchiveRecoveryExact':True,'recoveredDayExactAgainstUninterrupted':True,'fullDayRollbackClaim':False,'actualNativeWriteClaim':False}
 for kind in ['people','households']:
  fresh(kind);r=good(type='integrity-phase',phase=kind);assert all(r[k] for k in ['exact','rngExact','moneyExact','idsExact']);assert not good(type='integrity-metrics')['metrics']['samples'];out['cases'][kind]={'capRefusalExactArchiveMoneyIdsRng':True,'snapshots':0}
 # Restore a supported lower-history archive in the same enabled owner/worker.
 good(type='load',archive=fixtures['small']);low=good(type='export');assert len(json.loads(low['archive'])['households'])<3000 and len(json.loads(low['archive'])['people'])<8000;resumed=good(type='step',days=1);assert resumed['day']==low['day']+1;assert not good(type='integrity-metrics')['metrics']['samples'];out['cases']['lowerHistoryRecovery']={'sameEnabledOwnerAndWorker':True,'restoredSupportedArchive':True,'ordinaryDayResumes':True,'snapshots':0,'noInTownHistoryPruning':True}
 b.close()
path=ROOT/'reports/independent-command-creator-scope.json';path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
