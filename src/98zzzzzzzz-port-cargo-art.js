// Real owned consignments have their own bounded boat actors, separate from
// legacy spot-export manifests. Distant zoom/reduced motion exits before queries.
const portWaterActorsBase=waterfrontActors;
waterfrontActors=function(visible){
 const actors=portWaterActorsBase(visible);if(!visualDetailBudget().boats||gameOptions.reducedMotion)return actors;
 const cap=fastRenderEnabled()?2:gameOptions.quality==='high'?10:6;
 for(const o of portCargoPoses()){
  if(actors.length>=cap)break;const f=G.firms[o.port];if(!f)continue;
  const progress=clamp((G.day-o.started)/Math.max(1,o.duration),0,1),span=o.path.length-1,pose=waterRoutePose(o.path,(o.inbound?1-progress:progress)*span,o.inbound);
  if(!visible(pose.x,pose.y,30))continue;actors.push({kind:'boat',id:900000+o.id,f,...pose,cargo:o.good,quantity:o.qty,path:o.path,travel:progress*span,active:!paused,returning:false,consignment:o.id});
 }
 return actors;
};
