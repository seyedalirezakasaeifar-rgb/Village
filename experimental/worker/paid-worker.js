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
function workerPreparePanel(tab){const html=panelContents(tab);if(html.includes('Panel error:'))throw Error('Headless panel boundary incomplete: '+tab);workerEffect('panel-render',{panel:tab,title:names[tab]||'TownLedger',html});}
function workerInstallPaidOwner(owner){
 if(owner.shared!==window.__capacityAdmissionProtocol.shared)throw Error('The published shared controller is required');
 if(workerRootOwner)throw Error('Paid owner already installed');
 owner.shared.configure({generation:()=>workerEpoch});
 owner.deferDOM=()=>workerEffect('view-invalidated',{});
 registerWorkerRootRuntime(owner);
 // No document/canvas shim. Model-side preview calls run original panelContents.
 renderPanel=workerPreparePanel;
 openPanel=tab=>{active=tab;workerEffect('panel-open',{panel:tab,selected:selected?.id??null});workerPreparePanel(tab);};
 closeCouncilDialog=defer=>{closeCouncilDialogState(defer);if(active==='agenda')workerPreparePanel(active);save();workerEffect('council-closed',{});};
 playSfx=name=>workerEffect('sound',{name});
 return __installPaidCommandLayer(owner);
}
async function workerDrainPaidSaves(){for(let i=0;i<16;i++){await Promise.resolve();if(!__rootAdmission.shared.status().pendingSaveGenerations)return;}throw Error('Committed saver did not drain');}
async function workerPaidDispatch(dto,context){
 if(!workerRootOwner||!window.__rootAdmission?.enabled())throw Error('Shared paid dispatcher is not configured');
 if(__rootAdmission.shared.isActive())throw Error('Outer-root owner must finish before a transport reply');
 const result=__rootAdmission.dispatchSerializable(dto,context);
 if(result.provisional||__rootAdmission.shared.isActive())throw Error('Provisional paid work cannot be acknowledged');
 await workerDrainPaidSaves();
 if(!result.ok)throw Error(result.reason||'Paid operation refused');
 // Construct only after committed saver microtasks have appended save intents.
 return {__workerReply:true,paid:{...result,committed:true}};
}
function workerExecutePaidChoice(m){const reviewToken=pendingEvent?.workerId;if(!Number.isSafeInteger(reviewToken)||m.eventId!==reviewToken)throw Error('Stale council event');return workerPaidDispatch({version:1,kind:'council-choice',requestId:m.command,epoch:m.epoch,reviewToken:m.eventId,index:m.index},{requestId:workerCommand,epoch:workerEpoch,reviewToken});}
function workerExecutePaidProvider(m){return workerPaidDispatch({version:1,kind:'private-provider',requestId:m.command,epoch:m.epoch,providerKind:m.providerKind},{requestId:workerCommand,epoch:workerEpoch});}

function workerTickCommittedDay(){if(!workerRootOwner||!window.__rootAdmission?.enabled()){tick();return;}let result;try{result=__rootAdmission.run({kind:'day'},()=>{tick();});}catch(error){simulationTickFailed=true;throw error;}if(!result.ok)throw Error(result.reason||'Completed day refused');}

// These presentation boundaries are also installed in non-paid experimental builds.
renderPanel=workerPreparePanel;
openPanel=tab=>{active=tab;workerEffect('panel-open',{panel:tab,selected:selected?.id??null});workerPreparePanel(tab);};
