// Persistence chronology is separate from simulated days and deterministic exports.
// A new founding/import is a new timeline; logical order survives clock changes.
let saveEpoch=0,saveOrder=0,saveRevision=0,saveTown='',saveStoreReady=false;
let saveStorePromise=Promise.resolve(),saveWrites=Promise.resolve(),saveCandidates=[],saveWarningEpoch=0;
function beginSaveTimeline(){saveEpoch++;saveRevision=0;autoSaveOK=false;try{saveTown=Array.from(crypto.getRandomValues(new Uint32Array(4)),n=>n.toString(16)).join('-')}catch(_){saveTown='session-'+saveEpoch+'-'+Math.random().toString(36).slice(2)}return saveEpoch;}
function saveEnvelope(payload){
 if(!saveTown)beginSaveTimeline();
 if(saveOrder>=Number.MAX_SAFE_INTEGER-1)throw Error('Save chronology exhausted');
 const e={format:1,order:++saveOrder,town:saveTown,revision:++saveRevision,payload};
 e.checksum=checksum([e.format,e.order,e.town,e.revision,payload].join('|'));return e;
}
function promoteSaveEnvelope(e,minimum){
 const previous=e.checksum;saveOrder=Math.max(saveOrder,minimum);if(saveOrder>=Number.MAX_SAFE_INTEGER-1)throw Error('Save chronology exhausted');e.order=++saveOrder;e.checksum=checksum([e.format,e.order,e.town,e.revision,e.payload].join('|'));
 // Only update the matching local snapshot, never a later revision/town.
 try{const current=readSaveEnvelope(localStorage.getItem('townledger-v6'));if(current?.checksum===previous)localStorage.setItem('townledger-v6',JSON.stringify(e))}catch(_){}
}
function readSaveEnvelope(value){
 try{const e=typeof value==='string'?JSON.parse(value):value;if(!e||typeof e.payload!=='string'||typeof e.checksum!=='string')return null;
  if(e.format==null)return e.checksum===checksum(e.payload)?{...e,order:0,town:'',revision:0}:null;
  if(e.format!==1||!Number.isSafeInteger(e.order)||e.order<1||!Number.isSafeInteger(e.revision)||e.revision<1||typeof e.town!=='string'||!e.town||e.town.length>160)return null;
  return e.checksum===checksum([e.format,e.order,e.town,e.revision,e.payload].join('|'))?e:null;
 }catch(_){return null;}
}
function localSaveCandidates(){const out=[];for(const key of ['townledger-v6','townledger-v6-backup'])try{const e=readSaveEnvelope(localStorage.getItem(key));if(e)out.push(e)}catch(_){}return out;}
function observeSaveOrder(e){if(e)saveOrder=Math.max(saveOrder,e.order||0);}
function persistSnapshot(payload,epoch){
 if(epoch!==saveEpoch)return Promise.resolve(false);
 let e;try{for(const v of localSaveCandidates())observeSaveOrder(v);e=saveEnvelope(payload)}catch(_){autoSaveOK=false;return Promise.resolve(false)}
 let localOK=false;const text=JSON.stringify(e),key='townledger-v6';
 try{const previous=localStorage.getItem(key);if(readSaveEnvelope(previous)){try{localStorage.setItem(key+'-backup',previous)}catch(_){/* A full backup slot must not prevent updating the primary. */}}localStorage.setItem(key,text);localOK=true;try{localStorage.removeItem('townledger-village-founder-3')}catch(_){}}catch(_){}
 autoSaveOK=localOK;
 // Queue transactions in invocation order; callbacks from a replaced town cannot write.
 const write=saveWrites.catch(()=>false).then(()=>epoch===saveEpoch?writeIndexedDB(e,epoch):false);
 saveWrites=write;
 return write.then(idbOK=>{const ok=localOK||idbOK;if(epoch===saveEpoch&&e.order===saveOrder){autoSaveOK=ok;if(ok)saveWarningEpoch=0;else if(saveWarningEpoch!==epoch){saveWarningEpoch=epoch;toast('On-device saving is unavailable. Export a backup before leaving.')}}return ok;});
}
function save(){
 if(!G||simulationBusy)return Promise.resolve(false);
 let payload;try{payload=archivePayload()}catch(_){autoSaveOK=false;return Promise.resolve(false)}
 const epoch=saveEpoch;
 return saveStoreReady?persistSnapshot(payload,epoch):saveStorePromise.then(()=>persistSnapshot(payload,epoch));
}
function restoreSaveEnvelope(e){observeSaveOrder(e);if(!hydrateSave(e.payload))return false;saveTown=e.town||saveTown;saveRevision=e.revision||0;autoSaveOK=true;return true;}
function load(){
 const candidates=localSaveCandidates().concat(saveCandidates).map((e,i)=>({e,i}));
 candidates.sort((a,b)=>(b.e.order-a.e.order)||(a.i-b.i));
 for(const {e} of candidates)if(restoreSaveEnvelope(e))return true;
 for(const key of ['townledger-village-founder-3','townledger-village-civic-2'])try{const raw=localStorage.getItem(key);if(raw&&hydrateSave(raw))return true}catch(_){}
 return false;
}
