// TownLedger's original illustrated freight and neighbourhood kit. All state in
// this file is presentation-only. Shipment ownership/settlement stays in trade.
const FREIGHT_LIVERIES={upland:['#5c8270','#d6bf83'],port:['#537f91','#d2c9a4'],ridge:['#a16e52','#d2b378']};
function regionalRoadExtension(m,id){
 const x=id%T,y=id/T|0;
 // Existing archives can have an interior gateway. Never draw a fake highway
 // through somebody's title: an extension requires an actual regional boundary.
 const boundary=m.direction==='north'?y===0:m.direction==='south'?y===55||y===T-1:x===55||x===T-1;
 const p=roadCenter(id),delta=m.direction==='north'?[36,-18]:m.direction==='south'?[-36,18]:[36,18];
 return {p,delta,boundary,end:[p[0]+delta[0]*3,p[1]+delta[1]*3]};
}
// Weak keys release geometry as consignments settle or an archive is replaced.
const shipmentGeometry=new WeakMap();
function shipmentVisualPose(order){
 if(!order.path?.length)return null;
 const m=OUTSIDE_MARKETS.find(m=>m.id===order.market);if(!m)return null;
 const elapsed=clamp((G.day-order.started+Math.min(1,acc/1.65))/Math.max(1,order.travelDays),0,.999999);
 const gate=order.direction==='import'?order.path[0]:fromEnd(order.path),extension=regionalRoadExtension(m,gate);
 let geometry=shipmentGeometry.get(order);
 if(!geometry||geometry.path!==order.path||geometry.direction!==order.direction){
  const centers=order.path.map(roadCenter);
  if(extension.boundary){if(order.direction==='import')centers.unshift(extension.end);else centers.push(extension.end);}
  geometry={path:order.path,direction:order.direction,centers};shipmentGeometry.set(order,geometry);
 }
 const centers=geometry.centers;
 // Loading and inspection occupy a small part of the actual consignment's
 // journey. Smooth corners stay within the road ribbon, including map edges.
 const travel=clamp((elapsed-.055)/.89,0,1),at=travel*(centers.length-1),i=Math.min(centers.length-2,Math.floor(at)),t=at-i;
 if(i<0){const p=centers[0];return {x:p[0],y:p[1],dx:1,dy:.5,loading:true};}
 const a=centers[i],b=centers[i+1],previous=centers[Math.max(0,i-1)],next=centers[Math.min(centers.length-1,i+2)],r=.16;
 let p=[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t],heading=[b[0]-a[0],b[1]-a[1]],corner,u;
 if(t<r&&i>0){corner=[previous,a,b];u=(t+r)/(2*r);}else if(t>1-r&&i+2<centers.length){corner=[a,b,next];u=(t-1+r)/(2*r);}
 if(corner){const [before,c,after]=corner,start=c.map((v,k)=>v-(v-before[k])*r),end=c.map((v,k)=>v+(after[k]-v)*r);p=c.map((v,k)=>(1-u)*(1-u)*start[k]+2*(1-u)*u*v+u*u*end[k]);heading=c.map((v,k)=>2*(1-u)*(v-start[k])+2*u*(end[k]-v));}
 return {x:p[0],y:p[1],dx:heading[0],dy:heading[1],loading:elapsed<.055||elapsed>.945,phase:elapsed};
}
regionalCargoActors=function(){
 if(!visualDetailBudget().traffic)return [];
 const result=[],cap=fastRenderEnabled()?3:12;
 for(const o of G.regionalTrade?.shipments||[]){if(result.length>=cap)break;const pose=shipmentVisualPose(o);if(!pose)continue;result.push({kind:'vehicle',...pose,v:{style:'truck',color:FREIGHT_LIVERIES[o.market]?.[0]||'#708c80',id:o.id,path:o.path,regional:o.id,cargo:o.good,market:o.market,direction:o.direction,loading:pose.loading}});}
 return result;
};
const worldVehiclePaint=vehiclePaint;
vehiclePaint=function(g,v,p,clock){
 if(v.style!=='truck'||!v.regional){worldVehiclePaint(g,v,p,clock);return;}
 const colors=FREIGHT_LIVERIES[v.market]||['#708c80','#c9b581'],m=Math.hypot(p.dx,p.dy)||1;
 g.save();g.translate(p.x,p.y);g.transform(p.dx/m,p.dy/m,-p.dy/m*1.35,p.dx/m*.45,0,0);
 g.fillStyle='#263d3840';g.fillRect(-19,-4,40,13);
 for(const x of [-13,-8,12])for(const y of [-7,4]){g.fillStyle='#293c38';g.fillRect(x-2,y,5,3);g.fillStyle='#a9ad99';g.fillRect(x,y+1,2,1);}
 g.fillStyle='#4e6257';g.fillRect(-18,-4,36,9);g.fillStyle=tone(colors[0],.72);g.fillRect(7,-6,12,9);g.fillStyle=colors[0];g.fillRect(7,-9,12,9);
 g.fillStyle='#b9d5ca';g.fillRect(14,-9,4,8);g.fillStyle='#496c72';g.fillRect(14,-8,3,6);g.fillStyle=colors[1];g.fillRect(7,-9,3,8);
 if(v.cargo==='logs'||v.cargo==='timber'){
  for(let j=0;j<4;j++){g.fillStyle=j%2?'#b69c6b':'#967b54';g.fillRect(-17,-8+j*2,23,2);g.fillStyle='#d8bc85';g.fillRect(4,-8+j*2,2,2);}for(const x of [-12,0]){g.fillStyle='#5b6958';g.fillRect(x,-9,2,9);}
 }else if(v.cargo==='stone'){
  g.fillStyle='#9b9d89';g.fillRect(-18,-7,24,7);for(let j=0;j<6;j++)polygon(g,[[-17+j*4,-7],[-15+j*4,-11-j%2],[-12+j*4,-7]],j%2?'#b9b7a0':'#858f80');
 }else{
  g.fillStyle=colors[1];g.fillRect(-18,-11,24,10);g.fillStyle=tone(colors[1],.73);g.fillRect(-18,-1,24,3);g.fillStyle=tone(colors[1],1.12);g.fillRect(-17,-11,22,1);
  for(let x=-15;x<6;x+=4){g.fillStyle=tone(colors[1],.84);g.fillRect(x,-10,1,9);}g.fillStyle=colors[0];g.fillRect(-13,-8,12,3);g.fillStyle='#ebe3bc';g.fillRect(-12,-7,3,1);
  if(v.cargo==='food'){g.fillStyle='#dae0cb';g.fillRect(-18,-10,3,8);g.fillStyle='#627f79';g.fillRect(-17,-8,1,4);}
 }
 g.fillStyle='#f4dca1';g.fillRect(18,-6,2,2);g.fillRect(18,0,2,2);g.fillStyle='#b35e46';g.fillRect(-19,-5,2,2);g.fillRect(-19,1,2,2);
 if(v.loading){g.fillStyle=Math.floor(clock*2)%2?'#d7aa5a':'#a98146';g.fillRect(9,-11,3,2);}
 g.restore();
};
drawRegionalGates=function(g,visible){
 if(!G.regionalTrade)return;
 for(const m of OUTSIDE_MARKETS){const id=regionalGateway(m);if(id==null)continue;const ext=regionalRoadExtension(m,id),p=ext.p;if(!visible(p[0],p[1],180))continue;
 const delta=ext.delta,l=Math.hypot(...delta),ux=delta[0]/l,uy=delta[1]/l,nx=-uy,ny=ux,colors=FREIGHT_LIVERIES[m.id];
 g.save();
 if(ext.boundary){segment(g,p,ext.end,'#a6a58b',29);segment(g,p,ext.end,'#626f69',24);for(const side of [-1,1]){const a=[p[0]+nx*10*side,p[1]+ny*10*side],b=[ext.end[0]+nx*10*side,ext.end[1]+ny*10*side];segment(g,a,b,'#cdc8a5',1);}g.setLineDash([7,7]);segment(g,p,ext.end,'#dfcb89',1);g.setLineDash([]);}
 // A roadside inspection lay-by, route shield and directional gantry share the
 // highway's actual heading. No arbitrary buildings or economic capacity added.
 for(const side of [-1,1]){const x=p[0]+nx*17*side,y=p[1]+ny*17*side;segment(g,[x,y],[x,y-28],'#687b6c',2);segment(g,[x-2,y],[x+3,y],'#b7b79a',2);}
 const left=[p[0]-nx*19,p[1]-ny*19-28],right=[p[0]+nx*19,p[1]+ny*19-28];segment(g,left,right,colors[0],10);segment(g,[left[0],left[1]-5],[right[0],right[1]-5],colors[1],1);
 if(cam.zoom>.58){g.save();g.translate(p[0],p[1]-29);let angle=Math.atan2(ny,nx);if(angle>Math.PI/2||angle<-Math.PI/2)angle+=Math.PI;g.rotate(angle);g.fillStyle='#f0e6c4';g.font='bold 5px Arial';g.textAlign='center';g.fillText(m.direction==='north'?'UPLAND ↑':m.direction==='east'?'GREYHAVEN ↑':'IRONRIDGE ↑',0,2);g.restore();}
 if(gameOptions.decor){for(let j=0;j<3;j++){const x=p[0]+ux*j*10+nx*19,y=p[1]+uy*j*10+ny*19;segment(g,[x,y],[x,y-4],'#d6c79e',2);g.fillStyle=colors[0];g.fillRect(x-1,y-4,2,2);}}
 g.restore();
 }
};
function neighbourhoodMaterial(b){
 const p=parcelForTile(b.x,b.y),palette={
  'east-meadow':['#8eaa8b','#d4c7a1'],'county-ridge':['#9b8f7b','#cbbba0'],
  'river-reach':['#719795','#c6bb8e'],'orchard-downs':['#9ba66a','#d6c797'],
  'high-common':['#8b95a1','#d4c9ae']};
 return p?palette[p.id]:['#889b7f','#cbbd99'];
}
const worldArchitecturalIdentity=architecturalIdentity;
architecturalIdentity=function(g,b,w,d){
 worldArchitecturalIdentity(g,b,w,d);
 if(!gameOptions.decor||gameOptions.quality==='low'||b.kind==='worksite'||b.redevelopment)return;
 const colors=neighbourhoodMaterial(b),front=d*.36,u=-w*.365;
 if(['home','apartment','office','grocer','bakery','tavern','school','clinic','college'].includes(b.kind)){
  // Stone coping, layered planting and a street-facing address tile create
  // coherent neighbourhoods without adding parcels, services or random props.
  for(const side of [-1,1]){const x=side*w*.36;box(g,x-.045,front-.06,.09,.10,0,3,colors[1]);const q=point(x,front-.015,6);g.fillStyle=colors[0];g.beginPath();g.ellipse(q[0],q[1],3,2,0,0,Math.PI*2);g.fill();}
  const q=point(w*.20,front+.015,10);g.fillStyle=colors[1];g.fillRect(q[0]-2,q[1]-2,4,3);g.fillStyle='#647361';g.fillRect(q[0]-1,q[1]-1,2,1);
 }
 if(['school','college','clinic','townhall','courthouse'].includes(b.kind)){
  // Human-scale civic entrance furniture and glazed door transom.
  box(g,-.14,front+.018,.28,.018,12,4,'#749b96');
  for(const side of [-1,1]){const x=side*w*.26;slab(g,x-.10,front-.05,.20,.10,5,'#aa9067');for(const leg of [-.07,.07])segment(g,point(x+leg,front,0),point(x+leg,front,5),'#627361',1);}
 }
 if(['warehouse','factory','sawmill','mill'].includes(b.kind)){
  // A deep, recessed rolling door, bumper, warning corners and loading canopy.
  box(g,-w*.22,front+.006,w*.34,.018,1,13,'#4b625b');
  for(let z=3;z<14;z+=3)segment(g,point(-w*.22,front+.03,z),point(w*.12,front+.03,z),'#829084');
  slab(g,-w*.25,front-.02,w*.40,.13,16,'#a8b5a0');segment(g,point(-w*.24,front+.10,0),point(w*.15,front+.10,0),'#566b5c',3);
  for(const x of [-w*.24,w*.14]){box(g,x,front+.05,.03,.035,0,5,'#d6ba6e');segment(g,point(x,front+.09,1),point(x+.03,front+.09,4),'#5b6657');}
 }
 if(b.kind==='home'){
  // Individual gutters and masonry courses remain subtle at neighbourhood zoom.
  const h=[22,28,20,32,21,26,19,24][b.id%8];
  if(b.id%8!==3&&b.id%8!==4)segment(g,point(u+.05,front-.025,h),point(u+w*.65,front-.025,h),'#6d7a6a',1);
 }
};
const worldConstructionProgress=drawConstructionProgress;
drawConstructionProgress=function(g,visible){
 worldConstructionProgress(g,visible);
 if(!gameOptions.decor||cam.zoom<.55||gameOptions.quality==='low')return;
 for(const project of G.projects){
  const item=buildingItemsById.get(project.id);if(!item||!visible(item.x,item.y,65))continue;
  const progress=clamp(1-project.remaining/Math.max(1,project.duration||30),0,1),w=item.w*.7,d=item.d*.7;
  g.save();g.translate(item.x,item.y);
  // Real funded progress changes the site's silhouette. No new worker or
  // speculative building is invented by the renderer.
  if(progress<.22){for(let j=0;j<3;j++)slab(g,-w*.4+j*w*.25,-d*.3,w*.18,d*.6,0,'#8c795b');}
  else {
   const h=6+Math.floor(progress*4)*6;
   for(const x of [-w*.40,w*.40])for(const y of [-d*.35,d*.35])segment(g,point(x,y,0),point(x,y,h),'#b49a6e',2);
   for(let z=6;z<=h;z+=6){segment(g,point(-w*.4,d*.35,z),point(w*.4,d*.35,z),'#ceb283',2);segment(g,point(w*.4,-d*.35,z),point(w*.4,d*.35,z),'#a08961',2);}
   if(progress>.68){slab(g,-w*.42,-d*.37,w*.84,d*.74,h,'#b6a281');for(let j=0;j<3;j++)segment(g,point(-w*.35+j*w*.3,-d*.3,h+1),point(-w*.35+j*w*.3,d*.3,h+1),'#8a7c5c');}
  }
  const q=point(-w*.34,d*.35,0);g.fillStyle='#d3b77b';g.fillRect(q[0]-4,q[1]-7,8,5);g.fillStyle='#6d745a';g.fillRect(q[0]-2,q[1]-5,4,1);
  g.restore();
 }
};
