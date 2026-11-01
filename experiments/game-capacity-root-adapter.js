// Reference game hooks for the ONE shared protocol. Unassembled; no policy by default.
(function(){
 window.__installGameCapacityRoot=function(options={}){
  if(window.__gameCapacityRoot){if(Object.keys(options).length)throw Error('One game hook owner is already installed; do not replace its reservation policy');return window.__gameCapacityRoot;}
  const protocol=window.__capacityAdmissionProtocol,shared=protocol.shared,adapters=[],metrics={captures:0,certificates:0,restores:0,last:null};
  let activeSnapshot=null,phaseStart=0;const bridge=protocol.installFences(shared);
 function capture(){return {base:captureArchiveRuntime(),extra:{marketOpen,householdMarketCache,charterOwnershipCache,waterNetworkTown,waterNetworkRoads,waterNetworkCache,waterDayTown,waterDayNumber,operatingWharves,regionalRouteCache,privatePublicSchoolCache,privatePublicFireCache,migrationReportOwner,migrationRecent,migrationObservedDay,migrationSessionCounts,civicBlueprintCacheTown,civicBlueprintCache,civicWatchCache,brownfieldPermit,placementServicePreviewCache,serviceBudgetErrorTown,serviceBudgetInputErrors,civicProjectSurveyTarget},ui:{pendingEvent,active,buildMode,selected,panelOpener},money:{saveEpoch,saveOrder,saveRevision,saveTown,saveWarningEpoch},adapters:adapters.map(a=>a.capture())};}
 function restore(s){restoreArchiveRuntime(s.base);({marketOpen,householdMarketCache,charterOwnershipCache,waterNetworkTown,waterNetworkRoads,waterNetworkCache,waterDayTown,waterDayNumber,operatingWharves,regionalRouteCache,privatePublicSchoolCache,privatePublicFireCache,migrationReportOwner,migrationRecent,migrationObservedDay,migrationSessionCounts,civicBlueprintCacheTown,civicBlueprintCache,civicWatchCache,brownfieldPermit,placementServicePreviewCache,serviceBudgetErrorTown,serviceBudgetInputErrors,civicProjectSurveyTarget}=s.extra);({pendingEvent,active,buildMode,selected,panelOpener}=s.ui);({saveEpoch,saveOrder,saveRevision,saveTown,saveWarningEpoch}=s.money);adapters.forEach((a,i)=>a.restore(s.adapters[i]));}

 shared.configure({
  capture:info=>{const start=performance.now(),runtime=capture(),town=G,graph=protocol.graphSnapshot([town,runtime.base,runtime.extra,runtime.ui.pendingEvent,runtime.ui.selected,serviceAccessCaches,civicCandidateSets,...runtime.adapters]);metrics.captures++;metrics.last={kind:info.kind,intent:info.intent?.kind,checkpointMs:performance.now()-start,objects:graph.length,properties:graph.reduce((n,row)=>n+row.keys.length,0),typedViews:graph.filter(row=>row.kind==='view').length,typedIndicesEnumerated:graph.filter(row=>row.kind==='view').reduce((n,row)=>n+(row.object.length||0),0),bufferBytes:graph.filter(row=>row.kind==='buffer').reduce((n,row)=>n+row.bytes.length,0)};return {town,runtime,graph};},
  restore:snapshot=>{const start=performance.now();protocol.graphRestore(snapshot.graph);G=snapshot.town;restore(snapshot.runtime);metrics.restores++;metrics.last.restoreMs=performance.now()-start;},
  enter:snapshot=>{activeSnapshot=snapshot;simulationBusy=true;phaseStart=performance.now();},
  leave:(snapshot,result)=>{simulationBusy=snapshot.runtime.base.simulationBusy;activeSnapshot=null;metrics.last.committed=result.committed;},
  certify:info=>{const start=performance.now();metrics.certificates++;if(metrics.last&&info.kind!=='initial')metrics.last.modelMs=start-phaseStart;
   try{if(!G||!inactivePersonCodecEnabled)return {ok:false,reason:'The common codec certifier is not enabled.'};if(activeSnapshot&&G!==activeSnapshot.town)return {ok:false,reason:'Town adoption is outside this root.'};
    if(!validateArchiveRecords(G))return {ok:false,reason:'This operation would create invalid property or identity records. No changes were committed.'};
    const payload=info.kind==='initial'?encodeInactiveLogicalArchive(JSON.stringify(G)):bridge.serializeCandidate(),encodedBytes=new Blob([payload]).size;
    let decision;if(typeof options.certifyReservations==='function')decision=options.certifyReservations({kind:info.kind,intent:info.intent,model:G,encodedBytes});else decision=options.oracleOnly===true?{ok:true,oracleOnly:true}:{ok:false,reason:'Future financial and visual reservations are not configured.'};
    if(metrics.last){metrics.last.certifyMs=performance.now()-start;metrics.last.encodedBytes=encodedBytes;metrics.last.oracleOnly=options.oracleOnly===true;}return decision;
   }catch(error){if(metrics.last)metrics.last.certifyMs=performance.now()-start;return {ok:false,reason:/budget|capacity/.test(error.message)?'Archive capacity reached. No changes were committed.':'The completed archive was rejected: '+error.message};}
  },
  generation:()=>saveEpoch,
  onRefusal:(reason,kind)=>{if(metrics.last)metrics.last.reason=reason;if(options.onRefusal)options.onRefusal(reason,kind);},
  onFatal:error=>{paused=true;simulationBusy=false;if(options.onFatal)options.onFatal(error);}
 });
 const api=Object.freeze({shared,bridge,oracleOnly:options.oracleOnly===true,metrics:()=>({...metrics,last:metrics.last?{...metrics.last}:null}),registerRuntime:adapter=>{if(shared.status().enabled||shared.isActive())throw Error('Register runtime while disabled and idle');if(!adapter||typeof adapter.capture!=='function'||typeof adapter.restore!=='function')throw Error('Invalid runtime adapter');adapters.push(adapter);}});
 window.__gameCapacityRoot=api;return api;
 };
})();
