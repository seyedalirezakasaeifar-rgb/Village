// Disabled, unassembled automatic-day candidate. Requires root-capacity-api.js.
(function(){
 const protocol=window.__capacityAdmissionProtocol,controller=protocol.shared;
 let installed=false,bridge=null,stoppedEpoch=null,lastCertificate=null,baseTick=null;
 const adapters=[];
 const bindings={
  active:{get:()=>active,set:v=>active=v},
  civicProjectSurveyTarget:{get:()=>civicProjectSurveyTarget,set:v=>civicProjectSurveyTarget=v},
  saveEpoch:{get:()=>saveEpoch,set:v=>saveEpoch=v},
  saveOrder:{get:()=>saveOrder,set:v=>saveOrder=v},
  saveRevision:{get:()=>saveRevision,set:v=>saveRevision=v},
  saveTown:{get:()=>saveTown,set:v=>saveTown=v},
  saveWarningEpoch:{get:()=>saveWarningEpoch,set:v=>saveWarningEpoch=v},
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
  const extra=adapters.map(a=>a.capture());
  return {town:G,runtime,values,extra,journal:protocol.graphSnapshot([G,runtime,...Object.keys(values).filter(k=>!['councilOpener','panelOpener'].includes(k)).map(k=>values[k]),serviceAccessCaches,civicCandidateSets,...extra])};
 }
 function restore(s){protocol.graphRestore(s.journal);G=s.town;restoreArchiveRuntime(s.runtime);for(const key of Object.keys(bindings))bindings[key].set(s.values[key]);adapters.forEach((a,i)=>a.restore(s.extra[i]));}
 // Bounds cover all fields written by beginVehicle, spawnPurposeTrip,
 // trafficUpdate and detour. Existing opaque fields remain in measured base.
 const vehicleNumbers=['id','segment','fraction','speed','wait','age','from','to','person','shipment','rerouted','plannedStep'];
 const visualBytes=value=>new Blob([JSON.stringify(value)]).size;
 function visualReserve(){
  const roads=G.tiles.reduce((n,t)=>n+(t===1?1:0),0),digits=String(G.tiles.length-1).length;
  for(const n of [frameClock,trafficElapsed,vehicleSerial,visualState])if(!Number.isFinite(n))throw Error('Visual clocks and counters must be finite numbers');
  for(const v of traffic){
   if(!v||!Array.isArray(v.path)||v.path.some(n=>!Number.isInteger(n)||n<0||n>=G.tiles.length))throw Error('Invalid visual path');
   for(const k of vehicleNumbers)if(owns(v,k)&&!Number.isFinite(v[k]))throw Error('Visual numeric field is not finite: '+k);
  }
  for(const [key,value]of intersectionGates)if(!Number.isInteger(key)||key<0||key>=G.tiles.length||!Number.isFinite(value))throw Error('Invalid visual junction gate');
  let personBytes=2,firmBytes=2,goodBytes=2;
  for(const p of G.people){if(typeof p.name!=='string')throw Error('Visual person name must be a string');personBytes=Math.max(personBytes,visualBytes(p.name));}
  for(const f of G.firms){if(typeof f.name!=='string')throw Error('Visual firm name must be a string');firmBytes=Math.max(firmBytes,visualBytes(f.name));}
  for(const good of Object.keys(goods))goodBytes=Math.max(goodBytes,visualBytes(good));
  // Every finite Number's canonical JSON token is below 32 bytes, including
  // negative subnormal/exponent values. Cargo toFixed(0) contributes <=32.
  const reasonBytes=Math.max(personBytes+firmBytes+visualBytes(' commuting to '),personBytes+visualBytes(' returning home'),32+goodBytes+firmBytes+visualBytes('  → '));
  const shape={};for(const k of vehicleNumbers)shape[k]=0;
  Object.assign(shape,{path:[],style:'pedestrian',color:'#ffffff',emergency:false,finished:false,reason:''});
  const actorBytes=visualBytes(shape)+vehicleNumbers.length*32+roads*(digits+1)+reasonBytes;
  const actorNodes=1+vehicleNumbers.length+1+roads+5;
  // A junction has one numeric tile key and one finite numeric timestamp.
  // Existing gates/unknown fields are already charged in the measured archive.
  return {roads,actorCount:80,reasonBytes,actorBytes,bytes:80*(actorBytes+1)+roads*(digits+32+4)+512,nodes:80*actorNodes+roads*3+32};
 }
 function logicalCandidate(){return JSON.stringify({...G,rngState,trafficState:{vehicles:traffic,clock:frameClock,elapsed:trafficElapsed,gates:[...intersectionGates],serial:vehicleSerial},visualState});}
 function certify(){
  try{
   if(!inactivePersonCodecEnabled)return {ok:false,reason:'The reviewed identity codec must be explicitly enabled first'};
   if(traffic.length>80)return {ok:false,reason:'Existing visual fleet exceeds the supported reserved count'};
   // Actual wire certification enforces all identity, cell, depth and size limits.
   const logicalText=logicalCandidate(),wire=encodeInactiveLogicalArchive(logicalText),logical=JSON.parse(logicalText);
   // Execute precisely the same candidate normalization/initialization as import,
   // on a private parsed town. Restore the live graph directly, never via hydrate.
   const snapshot=capture();let normalizedText,visual;
   try{const candidate=prepareArchiveCandidate(wire);if(!candidate)throw Error('Completed town fails its own import validation');initializeArchiveCandidate(candidate);normalizedText=logicalCandidate();visual=visualReserve();}
   finally{restore(snapshot);}
   const normalized=JSON.parse(normalizedText),normalizedWire=encodeInactiveLogicalArchive(normalizedText);
   const roads=visual.roads,reserveBytes=visual.bytes,reserveNodes=visual.nodes;
   const count=value=>{let n=0;const stack=[value];while(stack.length){const v=stack.pop();n++;if(v&&typeof v==='object')for(const k of Object.keys(v))stack.push(v[k]);}return n;};
   const rawBytes=new Blob([wire]).size,normalizedBytes=new Blob([normalizedWire]).size;
   const bytes=Math.max(rawBytes,normalizedBytes),logicalBytes=Math.max(inactiveCodecBudget(logical),inactiveCodecBudget(normalized)),nodes=Math.max(count(logical),count(normalized));
   lastCertificate={bytes,logicalBytes,nodes,reserveBytes,reserveNodes,roads,visual,rawBytes,normalizedBytes,normalizationGrowth:normalizedBytes-rawBytes};
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
  const baseDialog=showCustomEvent;showCustomEvent=function(type,title,text,choices){
   if(window.__rootAdmission||!controller.isActive())return baseDialog(type,title,text,choices);
   // Stage logical correspondence now, including save requests. Choices remain
   // callbacks and execute only through the separately owned paid-command path.
   const event={type,title,text,choices};pendingEvent=event;
   if(type!=='TOWN ARCHIVE'&&COUNCIL_EVENTS.some(e=>e.title===title)){G.councilInbox=G.councilInbox||[];if(!G.councilInbox.some(e=>e.title===title))G.councilInbox.unshift({title,day:G.day});save();}
   controller.afterCommit('automatic-dialog',()=>{if(pendingEvent!==event)return;councilOpener=document.activeElement;paintDialog(event);});
  };
  const baseVehicle=beginVehicle;beginVehicle=function(...args){if(controller.status().enabled&&traffic.length>=80)return null;return baseVehicle(...args);};
  return api;
 }
 function paintDialog({type,title,text,choices}){
  $('eventEyebrow').textContent=type;$('eventTitle').textContent=title;$('eventText').textContent=text;
  $('eventChoices').innerHTML=choices.map((c,i)=>`<button data-event-choice="${i}" ${c.cost>0?'data-sound="coin"':''} ${c.cost&&G.treasury<c.cost?'disabled':''}><strong>${esc(c.title)}</strong><small>${esc(c.desc||'')}${c.cost?' · Cost: '+money(c.cost):''}</small></button>`).join('');
  $('eventDialog').style.display='flex';$('eventDefer').textContent=(type==='TOWN ARCHIVE'||type==='LAND PURCHASE'||directTransactionDialog(type))?'CANCEL':'DECIDE LATER';$('eventChoices').querySelector('button:not([disabled])')?.focus();
 }
 function advance(expectedEpoch){if(expectedEpoch!==saveEpoch)return false;if(!controller.status().enabled)return baseTick();if(stoppedEpoch===saveEpoch||!G||pendingEvent)return false;return controller.run('day',()=>baseTick(),{epoch:expectedEpoch}).ok;}
 const api=Object.freeze({shared:controller,metrics:()=>({last:lastCertificate}),registerRuntime:a=>{if(controller.status().enabled||controller.isActive())throw Error('Register runtime only while disabled and idle');if(!a||typeof a.capture!=='function'||typeof a.restore!=='function')throw Error('Invalid runtime adapter');adapters.push(a);},install,step:epoch=>{install();return advance(epoch);},enable:()=>{install();stoppedEpoch=null;return controller.setEnabled(true);},disable:()=>controller.setEnabled(false),retry:()=>{stoppedEpoch=null;return certify();},certificate:()=>lastCertificate,visualReserve,status:()=>controller.status(),productionAssembled:false});
 window.__automaticDayAdmission=api;
})();
