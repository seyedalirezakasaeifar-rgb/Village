// Disabled command-only transaction adapter. NOT global archive capacity admission.
(function(){
 window.__installPaidCommandOwner=function(options={}){
  const p=__capacityAdmissionProtocol,s=p.shared;
  if(s.status().enabled||s.isActive()||s.status().pendingSaveGenerations)throw Error('Install command owner disabled, idle and drained');
  if(window.__paidCommandOwner)throw Error('Command owner already installed');
  const registry=[],samples=[],allowed=new Set(['council-choice','private-provider','panel-control','construction','road-stroke','route-command']);let scope='idle',refusal=null,activeSnapshot=null,readContext=null,completionScopeReady=false;
  const creator=options.automaticCreators,creatorReady=!!(creator&&creator.version===1&&creator.sourceCommit==='c91475af7dd079a51a72eb89b413673adae886c1'&&typeof creatorCapacityReason==='function'&&creator.preflight===creatorCapacityReason);
  const context=()=>readContext?readContext():{version:1,mode:scope};
  const mode=()=>context().mode;
  const now=()=>performance.now();
  function structural(){
   if(!G||![2,3].includes(G.version)||!Array.isArray(G.people)||G.people.length>8000||!Array.isArray(G.households)||G.households.length>3000||!Array.isArray(G.firms)||G.firms.length>3000||G.loans!=null&&(!Array.isArray(G.loans)||G.loans.length>10000))return {ok:false,reason:'Legacy identity or debt record limit reached'};
   const cash=totalMoney();
   if(!Number.isFinite(G.treasury)||!Number.isFinite(G.region)||G.region<0||!Number.isFinite(G.debt)||G.debt<0||!Number.isFinite(cash)||!validateArchiveRecords(G)||!validateBridgeArchive(G))return {ok:false,reason:'Current command structure or finances are invalid'};
   return {ok:true,cash};
  }
  // Reuses the selected shared fence, never an additional controller or saver.
  p.installFences(s);
  s.configure({
   capture:meta=>{
    if(meta.kind!=='command'||mode()!=='paid-command'||!allowed.has(meta.intent?.kind))throw Error('Unsupported command-only execution scope');
    if(meta.intent.kind==='route-command'&&!window.__workerRouteAuthority?.authorize(meta.intent))throw Error('Unregistered route scope');
    if(meta.intent.kind==='council-choice'){const choice=pendingEvent?.choices.find(c=>c.title===meta.intent.choiceTitle);if(!choice||!COUNCIL_EVENTS.some(e=>e.title===pendingEvent.title&&e.choices.includes(choice)))throw Error('Only authored council callbacks are admitted');}
    const start=now(),runtime=registry.map(r=>r.capture()),town=G,busy=simulationBusy,money=totalMoney();
    const graph=p.graphSnapshot([town,...runtime]);
    const sample={intent:meta.intent.kind,captureMs:now()-start,rows:graph.length,restoreMs:0,checkMs:0};samples.push(sample);if(samples.length>64)samples.shift();
    return {town,busy,money,runtime,graph,sample};
   },
   restore:x=>{const start=now();p.graphRestore(x.graph);G=x.town;registry.forEach((r,i)=>r.restore(x.runtime[i]));x.sample.restoreMs=now()-start;},
   enter:x=>{activeSnapshot=x;simulationBusy=true;},leave:x=>{simulationBusy=x.busy;activeSnapshot=null;},
   certify:meta=>{const start=now(),decision=structural();if(meta.kind==='initial')return decision;
    if(meta.kind!=='command'||mode()!=='paid-command'||!allowed.has(meta.intent?.kind))return {ok:false,reason:'Unsupported paid command'};
    if(decision.ok&&(!activeSnapshot||Math.abs(decision.cash-activeSnapshot.money)>.001))return {ok:false,reason:'Paid command changed total cash'};
    const sample=samples[samples.length-1];if(sample)sample.checkMs=now()-start;
    return decision;
   },
   generation:()=>saveEpoch,
   onRefusal:reason=>{refusal=reason;},
   onFatal:()=>{simulationTickFailed=true;paused=true;simulationBusy=false;}
  });
  function enterScope(value,work){if(!s.status().enabled||s.isHalted())throw Error('Paid owner is not enabled');if(typeof work!=='function'||work.constructor?.name==='AsyncFunction')throw Error('Trusted synchronous scope required');if(scope!=='idle'||s.isActive())throw Error('Execution scope already active');scope=value;try{const result=work();if(result&&typeof result.then==='function')throw Error('Execution scope cannot yield');return result;}finally{scope='idle';}}
  const owner={shared:s,scope:'paid-command',
   registerRuntime:r=>{if(scope!=='idle'||s.status().enabled||s.isActive())throw Error('Register disabled and idle');if(typeof r.capture!=='function'||typeof r.restore!=='function')throw Error('Invalid runtime registry');registry.push(r);},
   withPaidCommand:work=>enterScope('paid-command',work),
   withOrdinaryTick:work=>{throw Error('Worker must use the trusted ordinary-day execution contract');},
   automaticCompletion:work=>{const c=context();if(!creatorReady||!readContext||c.version!==1||c.mode!=='ordinary-day'||!c.stepping||s.isActive())throw Error('Automatic completion creator/scope safety is not composed');return work();},
   workerExecution:{version:1,mode:'paid-command',bind:reader=>{if(readContext||s.status().enabled||s.isActive()||typeof reader!=='function')throw Error('Bind trusted execution once while disabled');const c=reader();if(!c||c.version!==1||c.mode!=='idle')throw Error('Invalid trusted execution context');readContext=reader;},readyForOrdinaryDay:()=>!!(creatorReady&&readContext&&completionScopeReady)},
   registerAutomaticCompletionWrapper:version=>{if(version!==1||completionScopeReady||s.status().enabled||s.isActive())throw Error('Register completion wrapper once before enabling');completionScopeReady=true;},
   executionScope:()=>mode(),
   metrics:()=>({last:samples.length?{...samples[samples.length-1]}:null,samples:samples.map(x=>({...x})),refusal,scope,registeredRuntime:registry.length}),
   structuralChecksOnly:true,globalCapacityCertified:false,productionEnabled:false
  };
  return window.__paidCommandOwner=owner;
 };
})();
