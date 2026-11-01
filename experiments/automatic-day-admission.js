// Disabled, unassembled automatic-day candidate. Requires root-capacity-api.js.
(function(){
 const protocol=window.__capacityAdmissionProtocol,controller=protocol.shared;
 let installed=false,bridge=null,stoppedEpoch=null,lastCertificate=null,baseTick=null;
 const bindings={
  marketOpen:{get:()=>marketOpen,set:v=>marketOpen=v},
  householdMarketCache:{get:()=>householdMarketCache,set:v=>householdMarketCache=v},
  regionalRouteCache:{get:()=>regionalRouteCache,set:v=>regionalRouteCache=v},
  waterNetworkTown:{get:()=>waterNetworkTown,set:v=>waterNetworkTown=v},
  waterNetworkRoads:{get:()=>waterNetworkRoads,set:v=>waterNetworkRoads=v},
  waterNetworkCache:{get:()=>waterNetworkCache,set:v=>waterNetworkCache=v},
  waterDayTown:{get:()=>waterDayTown,set:v=>waterDayTown=v},
  waterDayNumber:{get:()=>waterDayNumber,set:v=>waterDayNumber=v},
  operatingWharves:{get:()=>operatingWharves,set:v=>operatingWharves=v},
  migrationReportOwner:{get:()=>migrationReportOwner,set:v=>migrationReportOwner=v},
  migrationRecent:{get:()=>migrationRecent,set:v=>migrationRecent=v},
  migrationObservedDay:{get:()=>migrationObservedDay,set:v=>migrationObservedDay=v},
  migrationSessionCounts:{get:()=>migrationSessionCounts,set:v=>migrationSessionCounts=v},
  civicBlueprintCacheTown:{get:()=>civicBlueprintCacheTown,set:v=>civicBlueprintCacheTown=v},
  civicBlueprintCache:{get:()=>civicBlueprintCache,set:v=>civicBlueprintCache=v},
  civicWatchCache:{get:()=>civicWatchCache,set:v=>civicWatchCache=v},
  privatePublicSchoolCache:{get:()=>privatePublicSchoolCache,set:v=>privatePublicSchoolCache=v},
  privatePublicFireCache:{get:()=>privatePublicFireCache,set:v=>privatePublicFireCache=v},
  charterOwnershipCache:{get:()=>charterOwnershipCache,set:v=>charterOwnershipCache=v},
  serviceBudgetErrorTown:{get:()=>serviceBudgetErrorTown,set:v=>serviceBudgetErrorTown=v},
  serviceBudgetInputErrors:{get:()=>serviceBudgetInputErrors,set:v=>serviceBudgetInputErrors=v},
  brownfieldPermit:{get:()=>brownfieldPermit,set:v=>brownfieldPermit=v},
  previousDailyCash:{get:()=>previousDailyCash,set:v=>previousDailyCash=v},
  autoSaveOK:{get:()=>autoSaveOK,set:v=>autoSaveOK=v},
  pendingEvent:{get:()=>pendingEvent,set:v=>pendingEvent=v},
  councilOpener:{get:()=>councilOpener,set:v=>councilOpener=v},
  panelOpener:{get:()=>panelOpener,set:v=>panelOpener=v},
  selected:{get:()=>selected,set:v=>selected=v},
  parcelFocus:{get:()=>parcelFocus,set:v=>parcelFocus=v},
  inspectedTrip:{get:()=>inspectedTrip,set:v=>inspectedTrip=v},
  buildMode:{get:()=>buildMode,set:v=>buildMode=v},
  placementServicePreviewCache:{get:()=>placementServicePreviewCache,set:v=>placementServicePreviewCache=v}
 };
 function capture(){
  const runtime=captureArchiveRuntime(),values={};for(const key of Object.keys(bindings))values[key]=bindings[key].get();
  return {town:G,runtime,values,journal:protocol.graphSnapshot([G,runtime,values,serviceAccessCaches,civicCandidateSets])};
 }
 function restore(s){protocol.graphRestore(s.journal);G=s.town;restoreArchiveRuntime(s.runtime);for(const key of Object.keys(bindings))bindings[key].set(s.values[key]);}
 function certify(){
  try{
   if(!inactivePersonCodecEnabled)return {ok:false,reason:'The reviewed identity codec must be explicitly enabled first'};
   if(traffic.length>80)return {ok:false,reason:'Existing visual fleet exceeds the supported reserved count'};
   // Actual wire certification enforces all identity, cell, depth and size limits.
   const wire=bridge?bridge.serializeCandidate():archivePayload(),logical=JSON.parse(archiveLogicalPayload());
   const roads=G.tiles.reduce((n,t)=>n+(t===1?1:0),0),actors=80;
   // Reserve a complete maximum fleet, not just today's free actor slots.
   // Each simple road path has at most tile-count nodes; IDs are bounded by atlas.
   const pathNodes=Math.max(roads,...traffic.map(v=>v.path.length),1);
   const reserveBytes=roads*64+actors*(pathNodes*12+2048)+(G.people.length+G.households.length+G.firms.length)*512+65536;
   const reserveNodes=roads*4+actors*(pathNodes+40)+(G.people.length+G.households.length+G.firms.length)*64+2048;
   let nodes=0;const stack=[logical];while(stack.length){const v=stack.pop();nodes++;if(v&&typeof v==='object')for(const k of Object.keys(v))stack.push(v[k]);}
   const bytes=new Blob([wire]).size,logicalBytes=inactiveCodecBudget(logical);
   lastCertificate={bytes,logicalBytes,nodes,reserveBytes,reserveNodes,roads};
   return {ok:bytes+reserveBytes<=INACTIVE_CODEC_LIMITS.bytes&&logicalBytes+reserveBytes<=INACTIVE_CODEC_LIMITS.logicalBytes&&nodes+reserveNodes<=INACTIVE_CODEC_LIMITS.nodes,reason:'Town capacity requires reserved room for complete days, initialization and visual traffic. Export this town before continuing.'};
  }catch(e){return {ok:false,reason:String(e.message||e)};}
 }
 function install(){
  if(installed)return api;installed=true;
  controller.configure({capture,restore,enter:()=>{simulationBusy=true;},leave:s=>{simulationBusy=s.runtime.simulationBusy;},certify,generation:()=>saveEpoch,onRefusal:(reason,kind)=>{if(kind==='day'){stoppedEpoch=saveEpoch;paused=true;acc=0;}toast(reason);},onFatal:()=>{paused=true;acc=0;}});
  bridge=protocol.installFences(controller);
  baseTick=tick;tick=function(){return advance(saveEpoch);};
  // These effects have no model writes; authoritative inbox/events remain in root.
  const baseToast=toast;toast=function(...args){return controller.afterCommit('toast',()=>baseToast(...args));};
  const baseAudio=refreshAmbience;refreshAmbience=function(...args){return controller.afterCommit('ambience',()=>baseAudio(...args));};
  const baseSfx=playSfx;playSfx=function(...args){return controller.afterCommit(null,()=>baseSfx(...args));};
  // Dialog creation mixes DOM and logical state. Until split, refuse the complete
  // day rather than display an event from a rolled-back model.
  const baseDialog=showCustomEvent;showCustomEvent=function(...args){if(controller.isActive()&&controller.status().kind==='day')controller.refuse('This automatic event requires a committed dialog boundary');return baseDialog(...args);};
  const baseVehicle=beginVehicle;beginVehicle=function(...args){if(controller.status().enabled&&traffic.length>=80)return null;return baseVehicle(...args);};
  return api;
 }
 function advance(expectedEpoch){if(expectedEpoch!==saveEpoch)return false;if(!controller.status().enabled)return baseTick();if(stoppedEpoch===saveEpoch)return false;return controller.run('day',()=>baseTick(),{epoch:expectedEpoch}).ok;}
 const api=Object.freeze({install,step:epoch=>{install();return advance(epoch);},enable:()=>{install();stoppedEpoch=null;return controller.setEnabled(true);},disable:()=>controller.setEnabled(false),retry:()=>{stoppedEpoch=null;return certify();},certificate:()=>lastCertificate,status:()=>controller.status(),productionAssembled:false});
 window.__automaticDayAdmission=api;
})();
