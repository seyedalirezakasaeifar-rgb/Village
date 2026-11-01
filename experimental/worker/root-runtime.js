// Composition hook only: never creates a controller, root, journal or save fence.
let workerRootOwner=null;
function registerWorkerRootRuntime(owner){
 if(workerRootOwner)throw Error('Worker root runtime already registered');
 if(!owner?.shared||typeof owner.registerRuntime!=='function')throw Error('Shared paid-root owner registry required');
 if(owner.shared.isActive()||owner.shared.status().enabled)throw Error('Register worker runtime while shared root is disabled and idle');
 owner.registerRuntime({capture:()=>({outbox:workerOutbox,effectSerial:workerEffectSerial,eventSerial:workerEventSerial,version:workerVersion,prepared:workerSavePrepared}),restore:s=>{workerEffectSerial=s.effectSerial;workerEventSerial=s.eventSerial;workerVersion=s.version;workerSavePrepared=s.prepared;}});
 workerRootOwner=owner;return owner.shared;
}
