// Explicit presentation/persistence boundary. No dummy DOM exists in this realm.
const workerOutbox=[];let workerVersion=0,workerEventSerial=0;
function workerEffect(type,payload){workerOutbox.push({type,day:G?.day,version:workerVersion,payload});}
refreshAmbience=()=>workerEffect("ambience-refresh",{});
toast=(text)=>workerEffect('notification',{text});
save=()=>{workerEffect('save-request',{});return true;};
renderPanel=(panel)=>workerEffect('panel-invalidated',{panel});
updateHeader=()=>workerEffect('header-invalidated',{});
showCustomEvent=(type,title,text,choices)=>{pendingEvent={type,title,text,choices,workerId:++workerEventSerial};workerEffect('council-event',{id:pendingEvent.workerId,type,title,text,choices:choices.map((c,index)=>({index,title:c.title,desc:c.desc,cost:c.cost||0}))});};
function workerSnapshot(){G.rngState=rngState;return {version:workerVersion,day:G.day,rng:rngState,model:JSON.parse(JSON.stringify(G)),outbox:workerOutbox.splice(0)};}
function workerRequest(m){
 if(m.type==='load'){G=JSON.parse(m.archive);rngState=G.rngState;visualState=G.visualState;workerVersion=0;pendingEvent=null;invalidateRoads();return workerSnapshot();}
 if(m.type==='policy'){const d=defs.find(d=>d[0]===m.key);if(!d||!Number.isFinite(m.value)||m.value<d[2]||m.value>d[3])throw Error('Invalid policy');const old=G.policy[m.key];G.policy[m.key]=m.value;journalPolicy(m.key,old,m.value);recompute();return workerSnapshot();}
 if(m.type==='choice'){if(!pendingEvent||m.id!==pendingEvent.workerId)throw Error('Stale council event');throw Error('Council settlement dispatcher not yet extracted');}
 if(m.type==='step'){for(let i=0;i<m.days;i++){if(pendingEvent)break;tick();workerVersion++;}return workerSnapshot();}
 if(m.type==='export'){const snapshot=workerSnapshot();return {...snapshot,archive:JSON.stringify(snapshot.model)};}
 throw Error('Unknown request');
}
self.onmessage=e=>{try{self.postMessage({id:e.data.id,ok:true,result:workerRequest(e.data)});}catch(error){self.postMessage({id:e.data.id,ok:false,error:String(error),stack:error.stack});}};
