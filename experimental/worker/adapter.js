// Explicit presentation/persistence boundary. No dummy DOM exists in this realm.
const workerOutbox=[];let workerVersion=0,workerEventSerial=0,workerEpoch=0,workerCommand=0,workerStepping=false;
function workerEffect(type,payload){workerOutbox.push({type,day:G?.day,version:workerVersion,payload});}
refreshAmbience=()=>workerEffect("ambience-refresh",{});
toast=(text)=>workerEffect('notification',{text});
save=()=>{workerEffect('save-request',{});return true;};
renderPanel=(panel)=>workerEffect('panel-invalidated',{panel});
updateHeader=()=>workerEffect('header-invalidated',{});
showCustomEvent=(type,title,text,choices)=>{pendingEvent={type,title,text,choices,workerId:++workerEventSerial};workerEffect('council-event',{id:pendingEvent.workerId,type,title,text,choices:choices.map((c,index)=>({index,title:c.title,desc:c.desc,cost:c.cost||0}))});};
function workerSnapshot(){G.rngState=rngState;return {epoch:workerEpoch,command:workerCommand,version:workerVersion,day:G.day,rng:rngState,model:JSON.parse(JSON.stringify(G)),outbox:workerOutbox.splice(0)};}
function workerRequest(m){
 if(m.type!=='load'&&m.epoch!==workerEpoch)throw Error('Stale model epoch');
 if(['policy','choice','review'].includes(m.type)){if(!Number.isInteger(m.command)||m.command<=workerCommand)throw Error('Repeated command');workerCommand=m.command;}
 if(m.type==='load'){workerEpoch++;workerCommand=0;workerOutbox.length=0;G=JSON.parse(m.archive);rngState=G.rngState;visualState=G.visualState;workerVersion=0;pendingEvent=null;invalidateRoads();return workerSnapshot();}
 if(m.type==='policy'){const d=defs.find(d=>d[0]===m.key);if(!d||!Number.isFinite(m.value)||m.value<d[2]||m.value>d[3])throw Error('Invalid policy');const old=G.policy[m.key];G.policy[m.key]=m.value;journalPolicy(m.key,old,m.value);recompute();return workerSnapshot();}
 if(m.type==='review'){reviewCouncilInbox(m.index);return workerSnapshot();}
 if(m.type==='choice'){
 if(!pendingEvent||m.eventId!==pendingEvent.workerId)throw Error('Stale council event');
 const evt=pendingEvent,c=evt.choices[m.index];if(!c)throw Error('Invalid choice');
 if(evt.type==='TOWN ARCHIVE'||evt.type==='LAND PURCHASE'||directTransactionDialog(evt.type))throw Error('Unsupported direct transaction');
 if(c.cost&&G.treasury<c.cost)throw Error('Insufficient treasury');
 const goodsBefore=stockTotals(),fundsBefore=totalMoney();if(c.cost){G.treasury-=c.cost;G.region+=c.cost;G.cumulative.spending+=c.cost;}
 c.apply();
 const goodsAfter=stockTotals();for(const k of Object.keys(goods)){const delta=goodsAfter[k]-goodsBefore[k];goodsEntry(k,delta>=0?'imports':'consumed',Math.abs(delta));}
 const regionalFunding=totalMoney()-fundsBefore;G.region-=regionalFunding;if(Math.abs(regionalFunding)>.001)book(regionalFunding>0?'Regional capital':'Council settlement',regionalFunding>0?'Council decision beneficiaries':'Regional capital',Math.abs(regionalFunding),'Explicit council programme settlement');
 G.journal.push({day:G.day,name:evt.title,message:c.title+'. '+(c.desc||''),baseline:{...G.stats,treasury:G.treasury}});
 story('COUNCIL DECISION: '+c.title+' — '+evt.title,'neutral');G.councilInbox=(G.councilInbox||[]).filter(e=>e.title!==evt.title);pendingEvent=null;workerEffect('council-closed',{});recompute();updateHeader();save();dirty=true;return workerSnapshot();}

 if(m.type==='step'){if(workerStepping)throw Error('Step already active');if(!Number.isInteger(m.days)||m.days<0||m.days>360)throw Error('Invalid day count');const epoch=workerEpoch;workerStepping=true;return (async()=>{try{for(let i=0;i<m.days;i++){if(epoch!==workerEpoch)throw Error('Step interrupted by load');if(pendingEvent)break;tick();workerVersion++;await new Promise(resolve=>setTimeout(resolve,0));}if(epoch!==workerEpoch)throw Error('Step interrupted by load');return workerSnapshot();}finally{workerStepping=false;}})();}
 if(m.type==='export'){const snapshot=workerSnapshot();return {...snapshot,archive:JSON.stringify(snapshot.model)};}
 throw Error('Unknown request');
}
self.onmessage=async e=>{try{self.postMessage({id:e.data.id,ok:true,result:await workerRequest(e.data)});}catch(error){self.postMessage({id:e.data.id,ok:false,error:String(error),stack:error.stack});}};
