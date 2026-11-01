// Unassembled experiment: load explicitly in a disposable harness only.
// Refusal-boundary proof, not a complete admission provider or rollout candidate.
(function(){
 const originalConstruct=construct,originalCompletion=completeDevelopmentProjects;
 let enabled=false,provider=null,last=null;
 function refused(operation,args){
  if(!enabled)return false;
  const command=Object.freeze({operation,args:Object.freeze(Array.from(args)),town:G,day:G?.day,rng:rngState});
  const result=provider?provider(command):null;
  // Grants require the missing authoritative reservation/outer-effects contract.
  // Never pretend an arbitrary callback has supplied that proof.
  last=Object.freeze({operation,refused:true,reason:result?.reason||'No integrated paid-command reservation provider',grantNotImplemented:result?.ok===true});
  return true;
 }
 construct=function(){if(refused('construct',arguments))return false;return originalConstruct.apply(this,arguments);};
 completeDevelopmentProjects=function(){if(refused('completeDevelopmentProjects',arguments))return false;return originalCompletion.apply(this,arguments);};
 window.__paidRootPrototype=Object.freeze({
  enable:(value=false,readOnlyProvider=null)=>{enabled=value===true;provider=typeof readOnlyProvider==='function'?readOnlyProvider:null;last=null;return enabled;},
  status:()=>({enabled,last,scope:'refusal-boundary-only',productionAssembled:false,grantsImplemented:false})
 });
})();
