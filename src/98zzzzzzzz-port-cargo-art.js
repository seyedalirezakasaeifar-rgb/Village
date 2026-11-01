// Real owned river loads are bounded visual samples, separate from legacy
// manifests. Presentation cannot settle cargo, dispatch boats or pay handling.
const portWaterActorsBase=waterfrontActors;
function paidPortBoatPose(o){
 // Match the economy's current simulation day plus its frozen subday remainder.
 // Day-only sampling previously teleported a boat at every settlement tick.
 const progress=clamp((G.day-o.started+clamp(acc/1.65,0,1))/Math.max(1,o.duration),0,1),span=o.path.length-1;
 if(span<1)return null;
 const pose=waterRoutePose(o.path,(o.inbound?1-progress:progress)*span,o.inbound),length=Math.hypot(pose.dx,pose.dy)||1;
 // Opposing directions keep to opposite sides of the same navigable ribbon.
 pose.x-=pose.dy/length*4;pose.y+=pose.dx/length*4;
 return {...pose,progress,opacity:o.inbound?clamp(progress/.035,0,1):clamp((1-progress)/.035,0,1)};
}
waterfrontActors=function(visible,presentation=null){
 const actors=portWaterActorsBase(visible,presentation);if(!(presentation?.budget||visualDetailBudget()).boats||gameOptions.reducedMotion)return actors;
 const cap=presentation?.cap??(fastRenderEnabled()?2:gameOptions.quality==='high'?10:6);
 for(const o of portCargoPoses()){
  if(actors.length>=cap)break;const f=G.firms[o.port];if(!f)continue;const pose=paidPortBoatPose(o);if(!pose||G.tiles[roadId(Math.floor(pose.gx),Math.floor(pose.gy))]===1||!visible(pose.x,pose.y,35))continue;
  // Same-day bulk orders can share an identical local itinerary. Render one
  // sampled vessel at that position instead of stacking six hulls on one pixel.
  const cohort=actors.find(a=>a.consignment&&a.f.id===o.port&&a.inbound===o.inbound&&Math.hypot(a.x-pose.x,a.y-pose.y)<25);
  if(cohort){cohort.sampledLoads++;continue;}
  actors.push({kind:'boat',id:900000+o.id,f,...pose,cargo:o.good,quantity:o.qty,path:o.path,travel:pose.progress*(o.path.length-1),active:true,returning:false,inbound:o.inbound,stage:o.stage,consignment:o.id,sampledLoads:1});
 }
 return actors;
};
const paidPortBoatPainterBase=paintWaterBoat;
paintWaterBoat=function(g,a,clock){g.save();if(a.consignment)g.globalAlpha=a.opacity??1;paidPortBoatPainterBase(g,a,clock);g.restore();};
// Paid consignment inspection must not pick up a legacy voyage for the same
// wharf, whose ownership and delivery state follow a different contract.
const paidPortInspectBase=inspectWaterTripAt;
inspectWaterTripAt=function(x,y){
 const radius=22/Math.max(.32,cam.zoom),a=waterfrontActors(()=>true).filter(a=>a.consignment&&Math.hypot(a.x-x,a.y-y)<radius).sort((a,b)=>Math.hypot(a.x-x,a.y-y)-Math.hypot(b.x-x,b.y-y))[0];
 if(!a)return paidPortInspectBase(x,y);
 selectedWaterTrip={firm:a.f.id,consignment:a.consignment,cargo:a.cargo,quantity:a.quantity,path:a.path.slice(),returning:false};selected={id:a.f.building};openPanel('inspect');dirty=true;return true;
};
const paidPortSelectedInfoBase=selectedWaterInfo;
selectedWaterInfo=function(){
 if(!selectedWaterTrip?.consignment)return paidPortSelectedInfoBase();
 const labels={'outside':'Regional voyage','origin-loading':'Supplier preparing cargo','collecting':'Freight collection','loading':'Freight loading','departing':'Leaving the loading site','unloading':'Freight unloading','delivering':'Last-mile delivery','awaiting-payment':'Buyer payment pending','returning':'Returning to owner'};
 const id=selectedWaterTrip.consignment,o=G.regionalTrade?.shipments.find(o=>o.id===id),recent=G.regionalTrade?.recent.find(o=>o.id===id),record=o||recent;
 return {cargo:record?.good||selectedWaterTrip.cargo,quantity:record?.qty||selectedWaterTrip.quantity,journey:o?(o.stage==='return-outside'?'Owned cargo returning toward recovery':o.direction==='import'?'Owned import · '+(labels[o.stage]||'In transit'):'Owned export · '+(labels[o.stage]||'In transit')):recent?'Consignment completed · '+(recent.status||'see accounts'):'Previously selected owned consignment'};
};

const paidPortRouteBase=drawSelectedWaterRoute;
drawSelectedWaterRoute=function(g){
 if(!selectedWaterTrip?.consignment){paidPortRouteBase(g);return;}
 if(!selected||readBuild(selected.id)?.firm!==selectedWaterTrip.firm){selectedWaterTrip=null;return;}
 const o=G.regionalTrade?.shipments.find(o=>o.id===selectedWaterTrip.consignment),path=o?(o.mode==='river'?o.waterPath:o.activePath):selectedWaterTrip.path;if(!path?.length)return;g.save();g.strokeStyle='#f2d492';g.lineWidth=2/Math.max(.32,cam.zoom);g.setLineDash([5/cam.zoom,4/cam.zoom]);g.beginPath();path.forEach((id,i)=>{const q=iso(id%T+.5,(id/T|0)+.5);i?g.lineTo(...q):g.moveTo(...q)});g.stroke();g.restore();
};
