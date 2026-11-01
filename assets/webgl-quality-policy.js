// Rich and diagnostic overrides stay explicit. Adaptive fallback never rewrites preferences.
export function qualityPlan(preference,override,backend,runtimeTier){
 const accepted=['economy','low','balanced','reference','high','unshadowed'];
 if(accepted.includes(override))return {quality:override,automatic:false,reason:'Explicit renderer override'};
 if(preference==='high')return {quality:'reference',automatic:false,reason:'Rich detail selected'};
 if(preference==='low')return {quality:'economy',automatic:true,reason:'Performance selected; measured frame guard active'};
 if(runtimeTier)return {quality:runtimeTier,automatic:true,reason:'Observed slow rendering'};
 const software=/swiftshader|llvmpipe|softpipe|software|microsoft basic/i.test(backend||''),identified=/adreno|mali|apple|intel|nvidia|radeon|powervr|amd/i.test(backend||'');
 if(software||!identified)return {quality:'canvas',automatic:true,reason:software?'Software renderer capability':'Unclassified renderer capability'};
 return {quality:'balanced',automatic:true,reason:'Identified GPU; measured frame guard active'};
}
export function qualityDecision(plan,intervals,hidden=false,busy=false){
 if(!plan.automatic||hidden||busy||intervals.length<3)return null;const a=intervals.slice(-3);if(!a.every(v=>Number.isFinite(v)&&v>0))return null;const median=a.slice().sort((a,b)=>a-b)[1];
 if(plan.quality==='balanced'&&median>100)return {quality:'economy',medianMs:median};
 if(plan.quality==='economy'&&median>400)return {quality:'canvas',medianMs:median};return null;
}
