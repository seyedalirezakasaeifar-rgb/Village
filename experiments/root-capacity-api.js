// Unassembled, disabled protocol prototype. Load inside the game closure only.
// Hooks must cover the complete model/runtime and separate logical UI from paint.
(function(){
 function graphSnapshot(roots){
  if(!Array.isArray(roots))throw Error('Snapshot roots must be an array');
  const seen=new Set(),rows=[],stack=roots.slice();
  while(stack.length){const object=stack.pop();if(!object||typeof object!=='object'||seen.has(object))continue;seen.add(object);
   const proto=Object.getPrototypeOf(object),row={object,proto,fixedKeys:Object.isFrozen(object),keys:[],values:[],flags:[]};
   if(object instanceof Map){row.kind='map';row.entries=Array.from(object.entries());for(const pair of row.entries)stack.push(pair[0],pair[1]);}
   else if(object instanceof Set){row.kind='set';row.entries=Array.from(object.values());for(const value of row.entries)stack.push(value);}
   else if(object instanceof Date){row.kind='date';row.time=Date.prototype.getTime.call(object);}
   else if(object instanceof ArrayBuffer){row.kind='buffer';row.bytes=new Uint8Array(object).slice();}
   else if(ArrayBuffer.isView(object)){row.kind='view';stack.push(object.buffer);}
   else if(Array.isArray(object)){row.kind='array';row.length=object.length;row.lengthWritable=Object.getOwnPropertyDescriptor(object,'length').writable;}
   else if(proto===Object.prototype||proto===null)row.kind='object';
   else throw Error('Unsupported snapshot object');
   if(!Object.isExtensible(object)&&!row.fixedKeys)throw Error('Non-extensible mutable snapshots are unsupported');
   for(const key of Reflect.ownKeys(object)){
    if(row.kind==='array'&&key==='length'||row.kind==='view'&&typeof key==='string'&&/^(0|[1-9]\d*)$/.test(key))continue;
    const d=Object.getOwnPropertyDescriptor(object,key);if(!owns(d,'value'))throw Error('Snapshot accessors are unsupported');if(!d.configurable&&!row.fixedKeys)throw Error('Snapshot requires mutable data properties or frozen containers');
    row.keys.push(key);row.values.push(d.value);row.flags.push((d.writable?1:0)|(d.enumerable?2:0)|(d.configurable?4:0));if(d.value&&typeof d.value==='object')stack.push(d.value);
   }
   rows.push(row);
  }
  return rows;
 }
 function graphRestore(rows){
  for(let n=rows.length-1;n>=0;n--){const r=rows[n],object=r.object,keys=new Set(r.keys);
   if(Object.getPrototypeOf(object)!==r.proto)Object.setPrototypeOf(object,r.proto);
   const currentKeys=Reflect.ownKeys(object).filter(key=>!(r.kind==='array'&&key==='length'||r.kind==='view'&&typeof key==='string'&&/^(0|[1-9]\d*)$/.test(key)));
   // Recreate mutable own fields in their original order, including a deleted
   // middle field. Refuse irreversible changes before deleting this object's data.
   for(const key of currentKeys)if((!r.fixedKeys||!keys.has(key))&&!Object.getOwnPropertyDescriptor(object,key).configurable)throw Error('Snapshot cannot remove an irreversible property');
   for(const key of currentKeys)if((!r.fixedKeys||!keys.has(key))&&!Reflect.deleteProperty(object,key))throw Error('Snapshot cannot remove an irreversible property');
   for(let i=0;i<r.keys.length;i++){const flags=r.flags[i];Object.defineProperty(object,r.keys[i],{value:r.values[i],writable:!!(flags&1),enumerable:!!(flags&2),configurable:!!(flags&4)});}
   if(r.kind==='array')Object.defineProperty(object,'length',{value:r.length,writable:r.lengthWritable});
   else if(r.kind==='map'){Map.prototype.clear.call(object);for(const pair of r.entries)Map.prototype.set.call(object,pair[0],pair[1]);}
   else if(r.kind==='set'){Set.prototype.clear.call(object);for(const value of r.entries)Set.prototype.add.call(object,value);}
   else if(r.kind==='date')Date.prototype.setTime.call(object,r.time);
   else if(r.kind==='buffer')new Uint8Array(object).set(r.bytes);
  }
 }
 function create(initial={}){
  let hooks={},enabled=false,halted=false,root=null,last=null,checking=false;
  const refusals=new WeakSet(),pendingSaves=new Map(),required=['capture','restore','enter','leave','certify','generation','save','onRefusal','onFatal'];
  const asyncValue=value=>value&&typeof value.then==='function';
  function invalid(message){const e=Error(message);if(root&&!root.poison)root.poison=e;return e;}
  function refusal(reason){const e=Error(reason||'Archive capacity is unavailable');refusals.add(e);if(root&&!root.poison)root.poison=e;return e;}
  function invokeSync(fn,...args){const value=fn(...args);if(asyncValue(value))throw invalid('Admission hooks and model work must be synchronous');return value;}
  function settle(frame,value){for(const resolve of frame.saveWaiters)resolve(value);frame.saveWaiters=[];}
  function report(hook,...args){try{hooks[hook](...args);}catch(e){if(last)(last.effectErrors||(last.effectErrors=[])).push(String(e.message||e));}}
  function scheduleSave(frame){
   if(!frame.saveWaiters.length)return;
   let group=pendingSaves.get(frame.generation);
   if(!group){group={generation:frame.generation,waiters:[]};pendingSaves.set(frame.generation,group);
    Promise.resolve().then(()=>{pendingSaves.delete(group.generation);
     let value=false;try{if(!halted&&hooks.generation()===group.generation)value=hooks.save();}catch(e){if(last)(last.effectErrors||(last.effectErrors=[])).push(String(e.message||e));value=false;}
     Promise.resolve(value).then(result=>{for(const done of group.waiters)done(result);},()=>{for(const done of group.waiters)done(false);});
    });
   }
   for(const done of frame.saveWaiters)group.waiters.push(done);frame.saveWaiters=[];
  }
  const api={
   configure:next=>{if(root||enabled||checking||pendingSaves.size)throw invalid('Configure admission only while disabled, idle and drained');for(const key of Object.keys(next)){if(!required.includes(key)||typeof next[key]!=='function'||key!=='save'&&next[key].constructor?.name==='AsyncFunction')throw invalid('Invalid admission hook '+key);}hooks={...hooks,...next};return api;},
   setEnabled:value=>{if(root||checking)throw invalid('Cannot toggle an active admission root');if(value!==true){enabled=false;return false;}if(halted)throw invalid('Admission is halted; reload a verified complete town');if(enabled)return true;for(const key of required)if(typeof hooks[key]!=='function')throw invalid('Missing admission hook '+key);
    checking=true;let decision;try{decision=invokeSync(hooks.certify,{kind:'initial',intent:null});}finally{checking=false;}
    if(!decision||decision.ok!==true){last={kind:'initial',ok:false,reason:decision?.reason||'Initial capacity is not certified'};report('onRefusal',last.reason,'initial');return false;}enabled=true;return true;},
   run:(kind,work,intent=null)=>{
    if(kind!=='day'&&kind!=='command')throw invalid('Unsupported admission root '+kind);
    if(typeof work!=='function'||work.constructor?.name==='AsyncFunction')throw invalid('Model work must be a trusted synchronous function');
    if(checking)throw invalid('A capacity certificate cannot start model work');
    if(halted)return {ok:false,reason:'Admission halted; reload a verified complete town'};
    if(!enabled)return {ok:true,joined:false,value:work()};
    if(root){if(root.poison)throw root.poison;try{return {ok:true,joined:true,value:invokeSync(work)};}catch(e){root.poison=root.poison||e;throw e;}}
    const frame={kind,intent,generation:hooks.generation(),snapshot:null,captured:false,effects:[],effectKeys:new Map(),saveWaiters:[],poison:null,phase:'capture'};root=frame;let committedValue;
    try{
     frame.snapshot=invokeSync(hooks.capture,{kind,intent});if(frame.snapshot==null)throw invalid('A root requires a complete snapshot');frame.captured=true;
     frame.phase='enter';invokeSync(hooks.enter,frame.snapshot,{kind,intent});frame.phase='work';committedValue=invokeSync(work);
     if(frame.poison)throw frame.poison;if(hooks.generation()!==frame.generation)throw refusal('Town changed before the root committed');
     frame.phase='certify';const decision=invokeSync(hooks.certify,{kind,intent});if(!decision||decision.ok!==true)throw refusal(decision?.reason||'Archive capacity is not certified');if(frame.poison)throw frame.poison;
     frame.phase='leave';invokeSync(hooks.leave,frame.snapshot,{kind,committed:true});root=null;last={kind,ok:true,effectErrors:[]};
    }catch(e){
     try{if(frame.captured){invokeSync(hooks.restore,frame.snapshot,{kind});invokeSync(hooks.leave,frame.snapshot,{kind,committed:false});}}
     catch(fatal){root=null;enabled=false;halted=true;settle(frame,false);last={kind,ok:false,reason:'Rollback failed',effectErrors:[String(fatal.message||fatal)]};report('onFatal',fatal);throw fatal;}
     root=null;settle(frame,false);last={kind,ok:false,reason:String(e.message||e),effectErrors:[]};
     if(e&&typeof e==='object'&&refusals.has(e)){report('onRefusal',last.reason,kind);return {ok:false,reason:last.reason};}throw e;
    }
    for(const effect of frame.effects)try{const result=effect();if(asyncValue(result))throw invalid('Outbox presentation effects must be synchronous');}catch(e){last.effectErrors.push(String(e.message||e));}
    try{scheduleSave(frame);}catch(e){settle(frame,false);last.effectErrors.push(String(e.message||e));}
    return {ok:true,joined:false,value:committedValue};
   },
   refuse:reason=>{throw refusal(reason);},
   assertIdle:operation=>{if(checking)throw invalid('A certificate cannot change the town');if(root)throw refusal('Cannot '+operation+' before the current root commits');return true;},
   afterCommit:(key,effect)=>{if(checking)throw invalid('A certificate cannot queue UI effects');if(typeof effect!=='function'||effect.constructor?.name==='AsyncFunction')throw invalid('Outbox effects must be synchronous presentation only');if(!root)return effect();if(key==null)root.effects.push(effect);else if(root.effectKeys.has(key))root.effects[root.effectKeys.get(key)]=effect;else{root.effectKeys.set(key,root.effects.length);root.effects.push(effect);}},
   requestSave:()=>{if(checking)return Promise.resolve(false);if(typeof hooks.save!=='function')throw invalid('Missing committed saver');if(halted)return Promise.resolve(false);if(!root)return hooks.save();return new Promise(resolve=>root.saveWaiters.push(resolve));},
   isActive:()=>!!root,isHalted:()=>halted,phase:()=>root?.phase||(checking?'certify':'idle'),
   status:()=>({enabled,halted,active:!!root,kind:root?.kind||null,phase:api.phase(),last,pendingSaveGenerations:pendingSaves.size})
  };
  api.configure(initial);return Object.freeze(api);
 }
 let fence=null;
 const shared=create();
 function installFences(controller=shared){
  if(fence){if(fence.controller===controller)return fence.bridge;throw Error('Admission fences already have an owner');}
  const original={save,archivePayload,hydrateSave,seed};controller.configure({save:original.save});
  const wrapped={save:()=>controller.requestSave(),archivePayload:()=>{if(controller.isActive())controller.refuse('No archive may be exported before a complete root commits');if(controller.isHalted())throw Error('No verified complete archive is available');return original.archivePayload();},hydrateSave:function(...args){controller.assertIdle('restore a town');return original.hydrateSave.apply(this,args);},seed:function(...args){controller.assertIdle('found a town');return original.seed.apply(this,args);}};
  save=wrapped.save;archivePayload=wrapped.archivePayload;hydrateSave=wrapped.hydrateSave;seed=wrapped.seed;
  const bridge=Object.freeze({serializeCandidate:()=>{if(controller.isActive()&&controller.phase()!=='certify')controller.refuse('Only a completed model can be certified');return original.archivePayload();},uninstall:()=>{if(controller.isActive()||controller.status().enabled||controller.isHalted()||controller.status().pendingSaveGenerations)throw Error('Disable healthy admission before removing fences');if(save!==wrapped.save||archivePayload!==wrapped.archivePayload||hydrateSave!==wrapped.hydrateSave||seed!==wrapped.seed)throw Error('Admission entrypoints changed');save=original.save;archivePayload=original.archivePayload;hydrateSave=original.hydrateSave;seed=original.seed;fence=null;}});
  fence={controller,bridge};return bridge;
 }
 window.__capacityAdmissionProtocol=Object.freeze({create,shared,graphSnapshot,graphRestore,installFences,productionAssembled:false});
})();
