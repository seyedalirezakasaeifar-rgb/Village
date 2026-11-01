// Explicit presentation/persistence boundary. No dummy DOM exists in this realm.
const workerOutbox=[];let workerVersion=0,workerEventSerial=0,workerEpoch=0,workerCommand=0,workerStepping=false;
const workerYieldChannel=new MessageChannel(),workerYieldQueue=[];
workerYieldChannel.port1.onmessage=()=>workerYieldQueue.shift()?.();
function workerYield(mode){return new Promise(resolve=>{if(mode==='timer')setTimeout(resolve,0);else{workerYieldQueue.push(resolve);workerYieldChannel.port2.postMessage(0);}});}
let workerSavePrepared=null,workerSaveSerial=0;
function workerEffect(type,payload){workerOutbox.push({type,day:G?.day,version:workerVersion,payload});}
refreshAmbience=()=>workerEffect("ambience-refresh",{});
toast=(text)=>workerEffect('notification',{text});
save=()=>{workerEffect('save-request',{});return true;};
renderPanel=(panel)=>workerEffect('panel-invalidated',{panel});
updateHeader=()=>workerEffect('header-invalidated',{});
showCustomEvent=(type,title,text,choices)=>{pendingEvent={type,title,text,choices,workerId:++workerEventSerial};if(type!=='TOWN ARCHIVE'&&(COUNCIL_EVENTS.some(e=>e.title===title)||isHousingRetentionTitle(title))){G.councilInbox=G.councilInbox||[];if(!G.councilInbox.some(e=>e.title===title))G.councilInbox.unshift({title,day:G.day});save();}workerEffect('council-event',{id:pendingEvent.workerId,type,title,text,choices:choices.map((c,index)=>({index,title:c.title,desc:c.desc,cost:c.cost||0}))});};
const workerProfile={tickMs:0,snapshotMs:0,snapshots:0,stringifyMs:0,parseMs:0,postMs:0};
function workerFullSnapshot(){let t=performance.now();const text=JSON.stringify(G);workerProfile.stringifyMs+=performance.now()-t;t=performance.now();const model=JSON.parse(text);workerProfile.parseMs+=performance.now()-t;return model;}
function workerSnapshot(projection=false){const started=performance.now();G.rngState=rngState;const model=projection?{policy:{minWage:G.policy.minWage},stats:{population:G.stats.population,employment:G.stats.employment},treasury:G.treasury,buildings:G.buildings.map(b=>({id:b.id,x:b.x,y:b.y,kind:b.kind}))}:workerFullSnapshot();workerProfile.snapshotMs+=performance.now()-started;workerProfile.snapshots++;return {profile:{...workerProfile},projection,epoch:workerEpoch,command:workerCommand,version:workerVersion,day:G.day,rng:rngState,model,outbox:workerOutbox.splice(0)};}
const workerRuntimeStatus=workerRuntimeArithmetic();
function workerRequest(m){
 if(m.type==='prepare-founding'||m.type==='validate-restore'){if(!workerRuntimeStatus.ok)throw Error('UNSUPPORTED_INTEGER_RUNTIME');if(G!==null)throw Error('RESTORE_VALIDATION_REQUIRES_ISOLATED_REALM');const reset=resetTownTransientUI,center=centerTownCamera;resetTownTransientUI=()=>{pendingEvent=null;cancelTransitDraft();resetTransitForecasts();transitTopologyCache=null;transitDailyCache=null;};centerTownCamera=()=>workerEffect('camera-center',{});try{if(m.type==='prepare-founding'){if(!['settlement','hardtimes','frontier','industrial','regional'].includes(m.scenario)||!Number.isSafeInteger(m.seed)||m.seed<0||m.seed>4294967295)throw Error('Invalid founding scenario or unsigned seed');chosenScenario=m.scenario;seed(m.seed);const valid=validateTown();if(!valid.ok)throw Error('Founded town validation failed');}else if(!hydrateSave(m.archive))throw Error('Archive validation refused');G.rngState=rngState;return {epoch:workerEpoch,validated:true,archive:m.type==='prepare-founding'?archivePayload():JSON.stringify(G),outbox:workerOutbox.splice(0)};}finally{resetTownTransientUI=reset;centerTownCamera=center;}}
 if(m.type==='runtime-status')return {epoch:workerEpoch,...workerRuntimeStatus};
 if(!workerRuntimeStatus.ok)throw Error('UNSUPPORTED_INTEGER_RUNTIME: model admission blocked; archive unchanged');
 const reply=()=>workerSnapshot(m.projection===true);
 if(m.type!=='load'&&m.epoch!==workerEpoch)throw Error('Stale model epoch');
 if(['policy','choice','review','build','policy-package','visit-panel','climate','mayor-guide','calendar-cancel','convene','defer','district-initial-focus'].includes(m.type)){if(!Number.isInteger(m.command)||m.command<=workerCommand)throw Error('Repeated command');workerCommand=m.command;}
 if(m.type==='load'){workerEpoch++;workerCommand=0;workerSavePrepared=null;for(const key of Object.keys(workerProfile))workerProfile[key]=0;workerOutbox.length=0;G=JSON.parse(m.archive);crewDay=-1;crewsUsed=new Map();regionalCrews=0;cancelTransitDraft();resetTransitForecasts();transitTopologyCache=null;transitDailyCache=null;cacheBuildingsFor=null;rngState=G.rngState;visualState=G.visualState;workerVersion=0;pendingEvent=null;invalidateRoads();return reply();}
 if(m.type==='cargo-report'){if(!Number.isSafeInteger(m.shipment))throw Error('Invalid shipment identifier');const cargo=ensureRegionalTrade().shipments.find(o=>o.id===m.shipment);if(!cargo)throw Error('Consignment is no longer active');return {...reply(),cargo:JSON.parse(JSON.stringify(cargo))};}
 if(m.type==='transit-report'){if(!Number.isSafeInteger(m.route))throw Error('Invalid route identifier');const report=transitRouteReport(m.route);return {...reply(),report};}
 if(m.type==='district-initial-focus'){if(!ANNEX_PARCELS.some(p=>p.id===m.parcel)||!G.charter?.owned.includes(m.parcel)||!owns(DISTRICT_FOCI,m.focus))throw Error('Invalid owned district charter');if(G.districtProgrammes?.[m.parcel])throw Error('PAID_REZONING_REQUIRES_SHARED_DISPATCH');if(G.treasury<0)throw Error('District charter is unavailable');if(!chooseDistrictFocus(m.parcel,m.focus))throw Error('District charter refused');return {...reply(),chartered:true};}
 if(m.type==='district-report'){const parcel=ANNEX_PARCELS.find(p=>p.id===m.parcel);if(!parcel)throw Error('Unknown district');const survey=parcelSurvey(parcel),metrics=G.charter.owned.includes(parcel.id)?districtMetrics(parcel.id):null;return {...reply(),report:{parcel:parcel.id,survey,metrics}};}
 if(m.type==='calendar-report'){const report={calendar:civicCalendarView(),venues:civicGatheringVenues().map(v=>({id:v.b.id,name:v.name}))};return {...reply(),report};}
 if(m.type==='convene'){if(pendingEvent||G.day-G.lastEventDay<12)throw Error('Council meeting is not available yet');offerCouncilEvent(true);return reply();}
 if(m.type==='defer'){if(!pendingEvent||pendingEvent.workerId!==m.eventId)throw Error('Stale council event');const event=pendingEvent;pendingEvent=null;if(event.type!=='TOWN ARCHIVE'&&(COUNCIL_EVENTS.some(e=>e.title===event.title)||isHousingRetentionTitle(event.title))){G.councilInbox=G.councilInbox||[];if(!G.councilInbox.some(e=>e.title===event.title))G.councilInbox.unshift({title:event.title,day:G.day});}workerEffect('council-closed',{});save();return reply();}
 if(m.type==='calendar-cancel'){

if(!Number.isSafeInteger(m.eventId)||!cancelCivicGathering(m.eventId))throw Error('Calendar entry is no longer cancellable');recompute();updateHeader();save();return {...reply(),cancelled:true};}
 if(m.type==='climate'){if(!['seasons','weather'].includes(m.key)||typeof m.value!=='boolean')throw Error('Invalid climate preference');gameOptions[m.key]=m.value;if(m.key==='seasons')G.climateSeasons=m.value;else{G.climateWeather=m.value;if(!m.value)G.weather='clear';refreshAmbience();}save();return reply();}
 if(m.type==='mayor-guide'){if(typeof m.visible!=='boolean')throw Error('Invalid guide state');ensureMayorJourney().guide=m.visible;save();return reply();}
 if(m.type==='visit-panel'){
if(!owns(names,m.panel))throw Error('Unknown panel');const journey=ensureMayorJourney();if(!journey.visited.includes(m.panel)){journey.visited.push(m.panel);save();}return reply();}
 if(m.type==='inspect'){const b=readBuild(m.building);if(!b)throw Error('Unknown building');return {...reply(),inspection:JSON.parse(JSON.stringify(b))};}
 if(m.type==='build'){if(!Number.isInteger(m.x)||!Number.isInteger(m.y)||!types[m.kind]||m.kind==='inspect')throw Error('Invalid building command');const before=G.construction;construct(m.kind,m.x,m.y);return {...reply(),built:G.construction>before};}
 if(m.type==='policy-package'){if(!m.values||typeof m.values!=='object'||Array.isArray(m.values))throw Error('Invalid policy package');for(const [key,value] of Object.entries(m.values)){if(key==='imports'){if(typeof value!=='boolean')throw Error('Invalid import policy');continue;}const d=defs.find(d=>d[0]===key);if(!d||!Number.isFinite(value)||value<d[2]||value>d[3])throw Error('Invalid policy value: '+key);}draftPolicy={...m.values};const before=G.journal.length;enactPolicyPackage();return {...reply(),enacted:G.journal.length>before};}
 if(m.type==='policy'){const d=defs.find(d=>d[0]===m.key);if(!d||!Number.isFinite(m.value)||m.value<d[2]||m.value>d[3])throw Error('Invalid policy');const old=G.policy[m.key];G.policy[m.key]=m.value;journalPolicy(m.key,old,m.value);recompute();return reply();}
 if(m.type==='review'){reviewCouncilInbox(m.index);return reply();}
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
 story('COUNCIL DECISION: '+c.title+' — '+evt.title,'neutral');G.councilInbox=(G.councilInbox||[]).filter(e=>e.title!==evt.title);pendingEvent=null;workerEffect('council-closed',{});recompute();updateHeader();save();dirty=true;return reply();}

 if(m.type==='step'){if(workerStepping)throw Error('Step already active');if(!Number.isInteger(m.days)||m.days<0||m.days>360)throw Error('Invalid day count');const epoch=workerEpoch;workerStepping=true;return (async()=>{try{for(let i=0;i<m.days;i++){if(epoch!==workerEpoch)throw Error('Step interrupted by load');if(pendingEvent)break;const tickStart=performance.now();tick();workerProfile.tickMs+=performance.now()-tickStart;workerVersion++;await workerYield(m.yieldMode);}if(epoch!==workerEpoch)throw Error('Step interrupted by load');return reply();}finally{workerStepping=false;}})();}
 if(m.type==='save-prepare'){if(workerSavePrepared)throw Error('Save already prepared');G.rngState=rngState;const archive=JSON.stringify(G),token=workerEpoch+':'+(++workerSaveSerial);workerSavePrepared={token,epoch:workerEpoch,version:workerVersion,command:workerCommand,day:G.day,checksum:checksum(archive)};return {...workerSavePrepared,archive};}
 if(m.type==='save-ack'){if(!workerSavePrepared||m.token!==workerSavePrepared.token||m.checksum!==workerSavePrepared.checksum)throw Error('Stale or mismatched save acknowledgement');const receipt=workerSavePrepared;workerSavePrepared=null;return {...receipt,persisted:true};}
 if(m.type==='save-abort'){if(!workerSavePrepared||m.token!==workerSavePrepared.token)throw Error('Stale save abort');workerSavePrepared=null;return {epoch:workerEpoch,aborted:true};}
 if(m.type==='snapshot')return reply();
 if(m.type==='export'){const snapshot=workerSnapshot();return {...snapshot,archive:JSON.stringify(snapshot.model)};}
 throw Error('Unknown request');
}
self.onmessage=async e=>{try{const requestStarted=performance.now();const result=await workerRequest(e.data);result.requestMs=performance.now()-requestStarted;result.workerSentAt=performance.timeOrigin+performance.now();const started=performance.now();self.postMessage({id:e.data.id,ok:true,result});workerProfile.postMs+=performance.now()-started;}catch(error){self.postMessage({id:e.data.id,ok:false,error:String(error),stack:error.stack});}};
