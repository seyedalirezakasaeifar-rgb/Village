// Isolated research prototype. Not assembled into game.js or connected to tick.
// First proof deliberately supports primitive writes to an existing plain-data
// tree only. Container replacement/aliasing needs a separate ownership protocol.
function createPhaseCowStore(initial){
 const owned=new WeakSet(),auditNodes=[],auditStart=performance.now();let root=initial,active=null;
 function audit(value){if(value===null||typeof value!=='object')return;if(owned.has(value))throw Error('COW tree audit: shared container or cycle');const proto=Object.getPrototypeOf(value);if(proto!==Object.prototype&&proto!==Array.prototype)throw Error('COW tree audit: non-plain container');owned.add(value);auditNodes.push(value);for(const key of Object.keys(value))audit(value[key]);}
 audit(root);for(const value of auditNodes)Object.freeze(value);auditNodes.length=0;const auditMs=performance.now()-auditStart;
 function begin({faultAfter=Infinity,onWrite=null}={}){
  if(active)throw Error('Transaction already active');const states=new WeakMap(),metrics={reads:0,writes:0,copies:0,copiedSlots:0};let open=true;
  const guard=()=>{if(!open)throw Error('Draft is no longer active');};
  function state(base,parent=null,key=null){
   const prior=states.get(base);if(prior){if(prior.parent!==parent||prior.key!==key)throw Error('Draft alias detected');return prior;}
   if(!owned.has(base))throw Error('Unowned container');const s={base,parent,key,copy:null,children:new Map(),proxy:null};states.set(base,s);
   function mark(){if(s.copy)return;s.copy=Array.isArray(base)?base.slice():{...base};metrics.copies++;metrics.copiedSlots+=Object.keys(base).length;if(parent)parent.mark();}
   s.mark=mark;
   const current=()=>s.copy||base;
   const read=(key,receiver)=>{guard();metrics.reads++;const value=Reflect.get(current(),key,receiver);if(value&&typeof value==='object'&&Object.prototype.hasOwnProperty.call(current(),key)){const child=state(value,s,key);s.children.set(key,child);return child.proxy;}return value;};
   const write=(key,value)=>{guard();if(value!==null&&(typeof value==='object'||typeof value==='function'))throw Error('Unsupported container replacement at '+String(key));mark();s.copy[key]=value;metrics.writes++;onWrite?.(metrics);if(metrics.writes>=faultAfter)throw Error('Injected phase fault');return true;};
   s.proxy=new Proxy(Array.isArray(base)?[]:{},{get:(_,key,receiver)=>read(key,receiver),set:(_,key,value)=>write(key,value),deleteProperty:(_,key)=>{guard();mark();delete s.copy[key];return true;},has:(_,key)=>{guard();return key in current();},ownKeys:()=>{guard();return Reflect.ownKeys(current());},getOwnPropertyDescriptor:(_,key)=>{guard();if(Array.isArray(base)&&key==='length')return {value:current().length,writable:true,enumerable:false,configurable:false};const d=Object.getOwnPropertyDescriptor(current(),key);return d?{value:read(key,s.proxy),writable:true,enumerable:d.enumerable,configurable:true}:undefined;},getPrototypeOf:()=>Object.getPrototypeOf(base),setPrototypeOf:()=>{throw Error('Prototype mutation forbidden');},defineProperty:(_,key,d)=>{if(!('value'in d))throw Error('Accessor mutation forbidden');return write(key,d.value);},preventExtensions:()=>{throw Error('Draft freezing forbidden');}});
   return s;
  }
  const top=state(root);
  function finish(s){if(!s.copy)return s.base;for(const [key,child]of s.children)if(s.copy[key]===child.base)s.copy[key]=finish(child);owned.add(s.copy);return Object.freeze(s.copy);}
  active={draft:top.proxy,metrics,commit(){guard();const start=performance.now();root=finish(top);open=false;active=null;return {root,commitMs:performance.now()-start,metrics:{...metrics}};},rollback(){guard();open=false;active=null;return root;}};return active;
 }
 return {begin,get current(){return root;},auditMs};
}
