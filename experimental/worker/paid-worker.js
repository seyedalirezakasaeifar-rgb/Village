// Trusted execution context is supplied to the one paid owner, never read from a packet.
let workerExecutionMode='unowned',workerScope='idle';
function workerExecutionContext(){return Object.freeze({version:1,mode:workerScope,epoch:workerEpoch,command:workerCommand,stepping:workerStepping});}
function workerInScope(mode,work){if(workerScope!=='idle')throw Error('A trusted worker scope is already active');workerScope=mode;try{return work();}finally{workerScope='idle';}}
// Explicit view DTO; never accepts source, callbacks or arbitrary globals.
const WORKER_MODEL_PANELS=['overview','economy','agenda','community','policies','treasury','banking','citizens','businesses','construction','journal','inspect'];
function workerViewContext(m){
 if(!WORKER_MODEL_PANELS.includes(m.panel))throw Error('Unsupported model panel');
 const c=m.context;if(!c||typeof c!=='object'||Array.isArray(c))throw Error('Invalid view context');
 if(!['all','struggling','jobless','lowcash','wealthy'].includes(c.people)||!['all','open','closed','losing','rich','poor'].includes(c.firms)||typeof c.query!=='string'||c.query.length>512||!['all','housing','commerce','production','waterfront','services'].includes(c.category))throw Error('Invalid view filters');
 if(c.selected!==null&&(!Number.isSafeInteger(c.selected)||!readBuild(c.selected)))throw Error('Unknown selected building');
 if(!c.draft||typeof c.draft!=='object'||Array.isArray(c.draft))throw Error('Invalid view draft');
 for(const [key,value] of Object.entries(c.draft)){const d=defs.find(d=>d[0]===key);if(key==='imports'?typeof value!=='boolean':!d||!Number.isFinite(value)||value<d[2]||value>d[3])throw Error('Invalid view policy draft');}
 active=m.panel;selected=c.selected===null?null:{id:c.selected};filterPeople=c.people;filterFirms=c.firms;citizenQuery=c.query;constructionCategory=c.category;draftPolicy={...c.draft};
 if(c.transitRoute!==null){if(!Number.isSafeInteger(c.transitRoute))throw Error('Invalid inspector route');transitInspectorReport={town:G,id:c.transitRoute,report:transitRouteReport(c.transitRoute)};}else transitInspectorReport=null;
 workerPreparePanel(active);return {__workerReply:true};
}
// Public paid7233d8d composition only. Never creates a competing controller.
function workerPreparePanel(tab){const html=panelContents(tab);if(html.includes('Panel error:'))throw Error('Headless panel boundary incomplete: '+tab);workerEffect('panel-render',{panel:tab,title:names[tab]||'TownLedger',html,supplierSelection:tab==='economy'?{...supplierSelection}:undefined,inspector:transitInspectorReport?.town===G&&G.transit?.routes.some(r=>r.id===transitInspectorReport.id)?{id:transitInspectorReport.id,report:transitInspectorReport.report}:null});}
function workerInstallPaidOwner(owner){
 const execution=owner.workerExecution;
 if(execution){if(execution.version!==1||execution.mode!=='paid-command'||typeof execution.bind!=='function'||typeof execution.readyForOrdinaryDay!=='function')throw Error('Unsupported explicit paid-command execution contract');}
 else if(owner.testOnly!==true)throw Error('Production owner must declare paid-command execution scope');
 if(owner.shared!==window.__capacityAdmissionProtocol.shared)throw Error('The published shared controller is required');
 if(workerRootOwner)throw Error('Paid owner already installed');
 workerExecutionMode=execution?'paid-command':'reference-test';if(execution)execution.bind(workerExecutionContext);
 owner.shared.configure({generation:()=>workerEpoch});
 owner.deferDOM=()=>workerEffect('view-invalidated',{});
 registerWorkerRootRuntime(owner);
 // No document/canvas shim. Model-side preview calls run original panelContents.
 renderPanel=workerPreparePanel;
 openPanel=tab=>{active=tab;workerEffect('panel-open',{panel:tab,selected:selected?.id??null});workerPreparePanel(tab);};
 closeCouncilDialog=defer=>{closeCouncilDialogState(defer);if(active==='agenda')workerPreparePanel(active);save();workerEffect('council-closed',{});};
 playSfx=name=>workerEffect('sound',{name});
 const layer=__installPaidCommandLayer(owner);if(typeof workerBindRouteModules==='function')workerBindRouteModules(owner);return layer;
}
async function workerDrainPaidSaves(){for(let i=0;i<16;i++){await Promise.resolve();if(!__rootAdmission.shared.status().pendingSaveGenerations)return;}throw Error('Committed saver did not drain');}
async function workerPaidDispatch(dto,context){
 if(workerStepping)throw Error('Paid commands wait for the completed-day batch');
 if(!workerRootOwner||!window.__rootAdmission?.enabled())throw Error('Shared paid dispatcher is not configured');
 if(__rootAdmission.shared.isActive())throw Error('Outer-root owner must finish before a transport reply');
 const result=workerInScope('paid-command',()=>__rootAdmission.dispatchSerializable(dto,context));
 if(result.provisional||__rootAdmission.shared.isActive())throw Error('Provisional paid work cannot be acknowledged');
 await workerDrainPaidSaves();
 if(!result.ok)throw Error(result.reason||'Paid operation refused');
 // Construct only after committed saver microtasks have appended save intents.
 return {__workerReply:true,paid:{...result,committed:true}};
}
function workerExecutePaidChoice(m){if(pendingEvent?.workerRoute){const tag=pendingEvent.workerRoute;return workerPaidDispatch({version:1,kind:'route-command',module:tag.module,operation:'$choice',requestId:m.command,epoch:m.epoch,reviewToken:m.eventId,index:m.index,payload:m.choicePayload??{}},{requestId:workerCommand,epoch:workerEpoch});}const reviewToken=pendingEvent?.workerId;if(!Number.isSafeInteger(reviewToken)||m.eventId!==reviewToken)throw Error('Stale council event');return workerPaidDispatch({version:1,kind:'council-choice',requestId:m.command,epoch:m.epoch,reviewToken:m.eventId,index:m.index},{requestId:workerCommand,epoch:workerEpoch,reviewToken});}
function workerExecutePaidProvider(m){return workerPaidDispatch({version:1,kind:'private-provider',requestId:m.command,epoch:m.epoch,providerKind:m.providerKind},{requestId:workerCommand,epoch:workerEpoch});}

function workerTickCommittedDay(){
 if(workerRootOwner?.shared.isHalted()){simulationTickFailed=true;throw Error('ROOT_HALTED_RECREATE_WORKER: recover a verified archive in a fresh realm');}
 if(workerRootOwner&&workerExecutionMode==='paid-command'&&!workerRootOwner.shared.status().enabled)throw Error('Paid-command owner is disabled; no day advanced');
 if(!workerRootOwner||!window.__rootAdmission?.enabled()){try{workerInScope('ordinary-day',()=>tick());}catch(error){simulationTickFailed=true;throw error;}return;}
 if(workerExecutionMode==='paid-command'){
  // Readiness is the paid owner's explicit assertion that its completion wrapper
  // and the capacity owner's local creator preflights are actually composed.
  if(workerRootOwner.workerExecution.readyForOrdinaryDay()!==true)throw Error('Ordinary-day local creator safety is not composed; no day advanced');
  try{workerInScope('ordinary-day',()=>tick());}catch(error){simulationTickFailed=true;throw error;}return;
 }
 if(workerExecutionMode!=='reference-test')throw Error('Unsupported model execution mode');
 // Historical reference-owner oracle only. Never select this for production.
 let result;try{result=workerInScope('reference-day',()=>__rootAdmission.run({kind:'day'},()=>{tick();}));}catch(error){simulationTickFailed=true;throw error;}
 if(!result.ok)throw Error(result.reason||'Completed day refused');
}

// These presentation boundaries are also installed in non-paid experimental builds.
renderPanel=workerPreparePanel;
openPanel=tab=>{active=tab;workerEffect('panel-open',{panel:tab,selected:selected?.id??null});workerPreparePanel(tab);};
