"""d2b7086 actual bridge/removal controls. Host test owner, NOT production composition."""
from pathlib import Path
import ast,json,hashlib,sys,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();tree=ast.parse((ROOT/'tests/test_road_bridge.py').read_text());fixture=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
names=['root-capacity-api.js','paid-command-root.js'];bootstrap='\n'.join((ROOT/'experiments'/n).read_text() for n in names)+'\n'+(ROOT/'tools/fixtures/current-paid-owner.js').read_text()+"\nconst currentOwner=window.__installCurrentPaidTestOwner();const rootAdmission=window.__installPaidCommandLayer(currentOwner);\n"
probe=r'''
window.__current={
 domHook:()=>{let calls=0,ran=false;const phases=[];currentOwner.deferDOM=()=>{calls++;phases.push(rootAdmission.active());};const committed=rootAdmission.run({kind:'test-dom-boundary'},()=>rootAdmission.deferUI(()=>{ran=true;throw Error('Browser DOM closure executed');}));const rejected=rootAdmission.run({kind:'test-dom-refusal'},()=>{rootAdmission.deferUI(()=>{ran=true;});rootAdmission.refuse('Controlled presentation refusal');});delete currentOwner.deferDOM;if(!committed.ok||rejected.ok||ran||calls!==1||phases.some(Boolean))throw Error('DOM-free presentation boundary failed');return {commitPublicationOnce:true,rejectedPublicationDiscarded:true,browserClosureNeverExecuted:true};},
 drain:async()=>{await saveStorePromise;for(let i=0;i<30;i++){await Promise.resolve();await saveWrites;if(!__capacityAdmissionProtocol.shared.status().pendingSaveGenerations&&!savePendingWrite&&!saveWriteRunning)return;await new Promise(r=>setTimeout(r,0));}throw Error('Save work did not drain');},
 prepare:async(action,enabled)=>{window.__currentAction=action;rootAdmission.enable(false);window.__denyCurrent=false;await __current.drain();__bridgeTest.setup();paused=true;active='';__townTest.step(1);const receipt=JSON.stringify(G.serviceCashEvidence);for(let i=0;i<2;i++)if(!hydrateSave(archivePayload()))throw Error('Current normalized fixture rejected');if(JSON.stringify(G.serviceCashEvidence)!==receipt)throw Error('Completed-day receipt changed on initial reload');
  if(action!=='bridge-build'){const q=bridgeCandidateFromBank(roadId(63,15)),r=commitRoadBridge(q.bank,q.key);if(!r.ok)throw Error(r.reason);}
  if(action==='bridge-repair'){G.bridges[0].condition=40;G.bridgeRevision++;invalidateRoads();recompute();}
  await __current.drain();rootAdmission.enable(enabled);window.__currentReceipt=JSON.stringify(G.serviceCashEvidence);openPanel('construction');return {bridgeId:G.bridges?.[0]?.id,bank:roadId(63,15)};
 },
 point:(x,y)=>{const p=iso(x,y),r=cv.getBoundingClientRect();cam={x:p[0],y:p[1]+TH/2,zoom:1};dirty=true;draw();return {x:r.left+cw/2,y:r.top+ch/2};},
 capture:async deny=>{await __current.drain();window.__denyCurrent=deny;window.__before={json:JSON.stringify(G),G,rng:rngState,bridges:G.bridges,firstBridge:G.bridges?.[0],people:G.people,treasury:G.treasury,region:G.region,epoch:saveEpoch,order:saveOrder,revision:saveRevision,failed:simulationTickFailed,tick:simulationTickActive,pending:pendingEvent,dialog:$('eventDialog').innerHTML,metrics:currentOwner.metrics()};window.__writes=[];writeIndexedDB=e=>{const data=JSON.parse(e.payload);__writes.push({active:rootAdmission.active(),treasury:data.treasury,bridges:data.bridges?.length||0});return Promise.resolve(true);};},
 mutate:kind=>{if(kind==='stale'){G.treasury--;G.region++;}if(kind==='noop'){let r;if(__currentAction==='bridge-build'){const q=bridgeCandidateFromBank(roadId(63,15));r=commitRoadBridge(q.bank,q.key);}else if(__currentAction==='bridge-remove'){const q=bridgeRemovalQuote(G.bridges[0].id);r=decommissionBridge(q.b.id,q.key);}else if(__currentAction==='road-remove'){const q=roadRemovalQuote(75,15);r=retireRoadTile(75,15,q.key);}else{G.bridges[0].condition=100;G.bridgeRevision++;r={ok:true};}if(!r.ok)throw Error('No-op fixture setup failed '+r.reason);}if(kind==='failed')simulationTickFailed=true;},
 result:async(reject,enabled)=>{await __current.drain();const b=window.__before,status=rootAdmission.status(),unchanged=JSON.stringify(G)===b.json&&G===b.G&&rngState===b.rng&&G.bridges===b.bridges&&G.bridges?.[0]===b.firstBridge&&G.people===b.people&&saveEpoch===b.epoch&&saveOrder===b.order&&saveRevision===b.revision&&simulationTickFailed===b.failed&&simulationTickActive===b.tick;if(JSON.stringify(G.serviceCashEvidence)!==window.__currentReceipt)throw Error('Paid control rewrote completed-day service payments');if(reject&&(!unchanged||status.last?.ok||__writes.length||pendingEvent!==b.pending||$('eventDialog').innerHTML!==b.dialog))throw Error('Rejected current road work was not atomic '+JSON.stringify({unchanged,status,writes:__writes}));if(!reject&&enabled&&(!status.last?.ok||__writes.length!==1||__writes.some(w=>w.active||w.treasury!==G.treasury)))throw Error('Protected road work did not publish one complete save');const model=archivePayload(),rng=rngState;let normalized=null;if(!reject){if(!hydrateSave(model))throw Error('Accepted current command failed actual hydrateSave');const once=archivePayload();if(!hydrateSave(once))throw Error('Second normalized reload failed');normalized=archivePayload();if(normalized!==once)throw Error('Normalized export is not a fixed point');if(JSON.stringify(G.serviceCashEvidence)!==window.__currentReceipt)throw Error('Reload rewrote completed payment receipt');}return {model,rng,normalized,unchanged,reject,status,writes:__writes,completedReceiptPreserved:true};},
 packet:async(dto,context)=>{await __current.drain();const before=JSON.stringify(G),town=G,rng=rngState,captures=currentOwner.metrics().captures,writes=__writes.length,result=rootAdmission.dispatchSerializable(dto,context);await __current.drain();return {result,unchanged:G===town&&JSON.stringify(G)===before&&rngState===rng,captures:currentOwner.metrics().captures-captures,writes:__writes.length-writes};},
 workerReview:id=>{pendingEvent.workerId=id;},
 dto:(epoch,reviewToken,index=0)=>({version:1,kind:'council-choice',requestId:42,epoch,reviewToken,index}),dispatch:(dto,context)=>rootAdmission.dispatchSerializable(dto,context),
 invalidateRemoved:()=>{const q=roadRemovalQuote(75,15);return {ok:q.ok,reason:q.reason};}
};
'''
out={'base':'d2b7086187621ae8c3c147fc3c04764efaadf49d','source_sha256':hashlib.sha256(source.encode()).hexdigest(),'runtime_sha256':{n:hashlib.sha256((ROOT/'experiments'/n).read_bytes()).hexdigest() for n in names},'hostTestOwnerOnly':True,'productionComposition':False,'native':False,'enabledByDefault':False,'cases':[]}
with sync_playwright() as pw:
 canonical={}
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 def page():
  p=b.new_page(viewport={'width':1000,'height':800});p.route('http://current-paid.test/**',lambda r:r.fulfill(status=200,content_type='text/html',body=html));p.goto('http://current-paid.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bootstrap+fixture+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__current.drain()');return p
 def review(p,action,enabled):
  r=p.evaluate('x=>__current.prepare(x.action,x.enabled)',{'action':action,'enabled':enabled})
  if action in ['bridge-build','road-remove']:
   p.locator('[data-bridge-build]' if action=='bridge-build' else '[data-road-remove-tool]').click();point=p.evaluate('v=>__current.point(v.x,v.y)',{'x':63 if action=='bridge-build' else 75,'y':15});p.mouse.click(**point)
  else:p.locator('[data-bridge-repair="'+str(r['bridgeId'])+'"]' if action=='bridge-repair' else '[data-bridge-remove="'+str(r['bridgeId'])+'"]').click()
  assert p.locator('#eventDialog').is_visible();return r
 for action in ['bridge-build','bridge-repair','bridge-remove','road-remove']:
  if os.environ.get('CURRENT_ACTION') and action!=os.environ['CURRENT_ACTION']:continue
  values=[]
  for enabled in [False,True]:
   p=page();review(p,action,enabled);p.evaluate('__current.capture(false)');p.locator('#eventChoices button').first.click();r=p.evaluate('e=>__current.result(false,e)',enabled);values.append((r['model'],r['rng'],r['normalized']));p.close()
  canonical[action]=values[1]
  assert values[0]==values[1],('Baseline full model/RNG/normalized mismatch',action)
  refusals=[]
  for why in ['capacity','stale','failed','noop']:
   p=page();review(p,action,True)
   if why!='capacity':p.evaluate('kind=>__current.mutate(kind)',why)
   p.evaluate('d=>__current.capture(d)',why=='capacity');p.locator('#eventChoices button').first.click();r=p.evaluate('__current.result(true,true)');r.pop('model');refusals.append({'reason':why,**r});p.close()
  out['cases'].append({'action':action,'exactFullModelRngAndNormalizedReload':True,'refusals':refusals});print('PASS',action,flush=True)
 p=page();review(p,'bridge-build',True);p.evaluate('__current.capture(false)');dto=p.evaluate('__current.dto(5,9)');dto=json.loads(json.dumps(dto));ctx={'requestId':42,'epoch':5,'reviewToken':9};rejected=[]
 for bad in [{**ctx,'epoch':6},{**ctx,'reviewToken':10},{**ctx,'requestId':41}]:
  r=p.evaluate('x=>__current.packet(x.dto,x.ctx)',{'dto':dto,'ctx':bad});assert not r['result']['ok'] and r['unchanged'] and r['captures']==0 and r['writes']==0;rejected.append(r)
 p.evaluate('__current.workerReview(10)');wrong_local=p.evaluate('x=>__current.packet(x.dto,x.ctx)',{'dto':dto,'ctx':ctx});assert not wrong_local['result']['ok'] and wrong_local['unchanged'] and wrong_local['captures']==0 and wrong_local['writes']==0;rejected.append(wrong_local);p.evaluate('__current.workerReview(9)')
 accepted=p.evaluate('x=>__current.packet(x.dto,x.ctx)',{'dto':dto,'ctx':ctx});assert accepted['result']['ok'] and accepted['result']['requestId']==42 and not accepted['result']['provisional'] and accepted['writes']==1
 duplicate=p.evaluate('x=>__current.packet(x.dto,x.ctx)',{'dto':dto,'ctx':ctx});assert not duplicate['result']['ok'] and duplicate['unchanged'] and duplicate['writes']==0
 r=p.evaluate('__current.result(false,true)');out['domFreeBoundary']=p.evaluate('__current.domHook()');assert 'bridge-build' not in canonical or (r['model'],r['rng'],r['normalized'])==canonical['bridge-build'];out['dto']={'hostSyntheticAdmissionContext':True,'productionWorkerComposition':False,'jsonRoundTrip':True,'matchedTrustedControl':True,'staleIdentityRejections':rejected,'accepted':accepted,'duplicate':duplicate};p.close();b.close()
(ROOT/'reports/current-paid-roads.json').write_text(json.dumps(out,indent=2));print('PASS current road controls')
