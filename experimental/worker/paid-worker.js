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
 openPanel=tab=>{active=tab;workerPreparePanel(tab);workerEffect('panel-open',{panel:tab});};
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
