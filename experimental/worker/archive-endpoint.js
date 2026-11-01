// Request coordination only. Validation/payment/root/persistence stay with owners.
function createWorkerArchiveEndpoint(owner){
 const session=typeof owner.session==='function'?owner.session():null;let lastId=0,tail=Promise.resolve();const active=new Map();
 function submit(request){
  if(!request||!Number.isSafeInteger(request.id)||request.id<=lastId)return {accepted:false,error:'DUPLICATE_OR_INVALID_ID'};
  if(session!==null&&request.session!==session)return {accepted:false,error:'STALE_SESSION'};
  lastId=request.id;
  if(active.size>=4)return {accepted:false,error:'ARCHIVE_QUEUE_FULL'};
  if(request.epoch!==owner.epoch())return {accepted:false,error:'STALE_EPOCH'};
  if(!['export','save','restore','found'].includes(request.op))return {accepted:false,error:'UNSUPPORTED_OPERATION'};
  const record={cancelled:false,admitted:false};active.set(request.id,record);
  const check=()=>{if(record.cancelled)throw Error('CANCELLED');if(request.epoch!==owner.epoch())throw Error('STALE_EPOCH');};
  const commit=()=>{check();record.admitted=true;};
  const run=async()=>{let reply;try{check();let result;
   if(request.op==='export'){result=await owner.export();check();}
   if(request.op==='save'){commit();result=await owner.save();}
   if(request.op==='found')result=await owner.found({scenario:request.scenario,seed:request.seed},commit);
   if(request.op==='restore'){if(typeof request.archive!=='string')throw Error('INVALID_ARCHIVE');result=await owner.restore(request.archive,commit);}
   reply={session,id:request.id,op:request.op,ok:true,epoch:owner.epoch(),admitted:record.admitted,committed:!!(result?.restored||result?.founded||result?.persisted),result};
  }catch(error){reply={session,id:request.id,op:request.op,ok:false,epoch:owner.epoch(),admitted:record.admitted,committed:false,outcome:record.admitted?'UNKNOWN_OR_FAILED_OWNER_OPERATION':'NOT_ADMITTED',error:String(error.message||error)};}
  active.delete(request.id);try{owner.complete(reply);}catch(error){/* Completion delivery cannot undo an already committed owner operation. */}return reply;};
  tail=tail.then(run,run);return {accepted:true,id:request.id,session};
 }
 return Object.freeze({submit,cancel:(id,requestSession)=>{if(session!==null&&requestSession!==session)return {cancelled:false,reason:'STALE_SESSION'};const record=active.get(id);if(!record||record.admitted)return {cancelled:false,reason:record?'ALREADY_ADMITTED':'NOT_PENDING'};record.cancelled=true;return {cancelled:true};},status:()=>({session,pending:active.size,lastId,epoch:owner.epoch()})});
}
