// Experimental scheduler. Never persisted or enabled by an ordinary founding/load.
const COOPERATIVE_DAY_DEFAULT=false;
let cooperativeEnabled=COOPERATIVE_DAY_DEFAULT,cooperativeJob=null,cooperativeToken=0,cooperativeReplaying=false;
const cooperativeEffects=new Map(),cooperativeCommands=[],cooperativeSamples={slices:[],days:[],commands:[],errors:[]};
const cooperativeChannel=new MessageChannel();
function cooperativeDayBusy(){return !!cooperativeJob;}
function cooperativeLastCommittedDay(){return cooperativeJob?.day??G?.day;}
function cooperativeEffect(name,fn,args){if(!cooperativeJob)return fn(...args);cooperativeEffects.set(name,()=>fn(...args));}
function afterCommittedDay(fn){if(!cooperativeJob){try{return Promise.resolve(fn());}catch(e){return Promise.reject(e);}}return new Promise((resolve,reject)=>cooperativeJob.waiters.push({fn,resolve,reject,town:G}));}
function cooperativeBanner(){let el=$('cooperativeStatus');if(!el){el=document.createElement('div');el.id='cooperativeStatus';el.setAttribute('role','status');el.style.cssText='position:fixed;top:76px;left:50%;transform:translateX(-50%);z-index:11000;max-width:90vw;padding:6px 12px;background:#203e34;color:#fff3d5;border:1px solid #d4b873;font:12px sans-serif;pointer-events:none';document.body.appendChild(el);}el.hidden=!cooperativeJob;if(cooperativeJob)el.textContent='Finishing day '+(cooperativeJob.day+1)+' · last completed day '+cooperativeJob.day+(cooperativeCommands.length?' · '+cooperativeCommands.length+' input events queued':'');}
function cooperativePost(){cooperativeChannel.port2.postMessage(cooperativeJob?.token);}
cooperativeChannel.port1.onmessage=e=>{if(cooperativeJob&&e.data===cooperativeJob.token)cooperativePump(false);};
function beginCooperativeDay(){
 if(cooperativeJob||!G||pendingEvent||pointer.down||touches.size)return false;
 // Recovery/export authority is a completed-day snapshot; never a suspended generator.
 const began=performance.now(),snapshot=JSON.stringify({...G,rngState,trafficState:{vehicles:traffic,clock:frameClock,elapsed:trafficElapsed,gates:[...intersectionGates],serial:vehicleSerial},visualState});
 cooperativeJob={town:G,day:G.day,previousBusy:simulationBusy,token:++cooperativeToken,iterator:stagedTick(),snapshot,rng:rngState,transients:{marketOpen,crewDay,crewsUsed:new Map(crewsUsed),regionalCrews,transitReservationVersion,trafficClock,migrationOwned:migrationReportOwner===G,migrationRecent:migrationRecent.slice(),migrationObservedDay,migrationSessionCounts:{...migrationSessionCounts},civicCandidates:new Map([...civicCandidateSets].map(([k,v])=>[k,new Set(v)]))},started:began,cpu:performance.now()-began,stage:'begin',waiters:[]};simulationBusy=true;cooperativeBanner();cooperativePost();return true;
}
function cooperativePump(synchronous=false){
 const job=cooperativeJob;if(!job)return;const start=performance.now(),deadline=start+4;let done=false;
 try{do{const next=job.iterator.next();job.stage=next.value||'commit';if(next.done){done=true;break;}}while(synchronous||performance.now()<deadline);}
 catch(error){job.cpu+=performance.now()-start;cooperativeFail(job,error);return;}
 const spent=performance.now()-start;job.cpu+=spent;cooperativeSamples.slices.push({day:job.day+1,stage:job.stage,ms:spent});if(cooperativeSamples.slices.length>1000)cooperativeSamples.slices.shift();
 if(done)cooperativeCommit(job);else if(!synchronous)cooperativePost();
}
function cooperativeCommit(job){
 if(cooperativeJob!==job)return;cooperativeJob=null;simulationBusy=job.previousBusy;cooperativeToken++;cooperativeSamples.days.push({day:G.day,cpuMs:job.cpu,elapsedMs:performance.now()-job.started});if(cooperativeSamples.days.length>240)cooperativeSamples.days.shift();
 if(typeof cooperativeClockCommit==='function')cooperativeClockCommit(job.cpu);cooperativeClearPreview();cooperativeBanner();
 for(const fn of cooperativeEffects.values())try{fn();}catch(e){console.error(e);}cooperativeEffects.clear();
 cooperativeFlushCommands();for(const w of job.waiters){try{w.resolve(w.town===G?w.fn():false);}catch(e){w.reject(e);}}
}
function cooperativeFail(job,error){
 cooperativeJob=null;simulationBusy=job.previousBusy;cooperativeToken++;G=JSON.parse(job.snapshot);rngState=job.rng;marketOpen=job.transients.marketOpen;crewDay=job.transients.crewDay;crewsUsed=job.transients.crewsUsed;regionalCrews=job.transients.regionalCrews;transitReservationVersion=job.transients.transitReservationVersion;restoreTransport();trafficClock=job.transients.trafficClock;migrationReportOwner=job.transients.migrationOwned?G:null;migrationRecent=job.transients.migrationRecent;migrationObservedDay=job.transients.migrationObservedDay;migrationSessionCounts=job.transients.migrationSessionCounts;civicCandidateSets.clear();for(const [k,v]of job.transients.civicCandidates)civicCandidateSets.set(k,v);roadsVersion++;roadNetwork=null;transitTopologyCache=null;transitDailyCache=null;cacheBuildingsFor=null;staticDirty=true;dirty=true;paused=true;acc=0;cooperativeEnabled=false;
 cooperativeClearPreview();pointer.down=false;pointer.activeId=null;touches.clear();roadPainted.clear();cooperativeSamples.errors.push(String(error));cooperativeEffects.clear();const declined=cooperativeCommands.length;for(const c of cooperativeCommands)c.reject?.(error);cooperativeCommands.length=0;cooperativeBanner();for(const w of job.waiters)w.reject(error);updateHeader();toast('Experimental scheduler stopped and restored completed day '+G.day+'. '+declined+' queued input events were declined; review them again.');console.error(error);
}
function finishCooperativeDaySync(reason='explicit barrier'){if(!cooperativeJob)return;cooperativeToken++;cooperativeJob.token=cooperativeToken;cooperativePump(true);}
function cooperativeQueueCommand(command){command.town=G;cooperativeCommands.push(command);cooperativeBanner();}
function cooperativeFlushCommands(){
 cooperativeReplaying=true;try{while(cooperativeCommands.length&&!cooperativeJob){const c=cooperativeCommands.shift();try{if(c.town!==G)throw Error('The town was replaced; review this action in the current town.');c.run();cooperativeSamples.commands.push({label:c.label,status:'replayed',day:G?.day});}catch(e){c.reject?.(e);cooperativeSamples.commands.push({label:c.label,status:'declined',day:G?.day,reason:String(e)});toast('Queued '+c.label+' needs renewed review: '+e.message);}}}finally{cooperativeReplaying=false;}
 if(cooperativeSamples.commands.length>200)cooperativeSamples.commands.splice(0,cooperativeSamples.commands.length-200);
}
function setCooperativeSimulation(enabled){return afterCommittedDay(()=>{cooperativeEnabled=!!enabled;acc=0;return cooperativeEnabled;});}
