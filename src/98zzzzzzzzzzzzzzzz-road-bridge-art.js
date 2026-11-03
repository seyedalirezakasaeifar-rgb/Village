// A bridge is still water to the river graph, but its road deck occupies a
// raised plane. Keep the art derived from the bridge's public render snapshot.
function bridgeArtItems(visible){
 if(typeof bridgeRenderSnapshot!=='function')return [];
 const result=[];
 for(const b of bridgeRenderSnapshot()){
  const first=roadCenter(b.banks[0]),last=roadCenter(b.banks[1]),cells=b.cells.map(id=>roadCenter(id));
  const mid=[(first[0]+last[0])/2,(first[1]+last[1])/2-9];
  const dx=last[0]-first[0],dy=last[1]-first[1],length=Math.hypot(dx,dy)||1;
  const pad=14,nx=-dy/length*pad,ny=dx/length*pad;
  const points=[[first[0]+nx,first[1]-17+ny],[last[0]+nx,last[1]-17+ny],[last[0]-nx,last[1]-17-ny],[first[0]-nx,first[1]-17-ny]];
  const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
  const item={kind:'roadBridge',bridge:b,first,last,cells,cellSet:new Set(b.cells),mid,axis:b.axis,
   bounds:[Math.min(...xs)-5,Math.min(...ys)-9,Math.max(...xs)+5,Math.max(...ys)+16],
   _paintBounds:[Math.min(...xs)-5,Math.min(...ys)-9,Math.max(...xs)+5,Math.max(...ys)+16],
   x:mid[0],y:mid[1],condition:b.condition,closed:b.closed};
  const margin=Math.max(item.x-item.bounds[0],item.bounds[2]-item.x,item.y-item.bounds[1],item.bounds[3]-item.y);
  if(visible(item.x,item.y,margin))result.push(item);
 }
 return result;
}
function bridgePointDistance(item,x,y){
 const a=item.first,b=item.last,dx=b[0]-a[0],dy=b[1]-a[1],l2=dx*dx+dy*dy||1;
 const t=clamp(((x-a[0])*dx+(y-a[1])*dy)/l2,-.04,1.04),px=a[0]+dx*t,py=a[1]+dy*t;
 return {distance:Math.hypot(x-px,y-py),t};
}
function bridgeTrafficLift(actor){
 if(actor.kind==='boat'||actor.kind==='transitArt'&&actor.mode==='elevated')return null;
 const v=actor.v,path=v?.path;
 if(!Array.isArray(path)||path.length<2)return null;
 for(const item of viewBuildings){
  if(item.kind!=='roadBridge')continue;
  const p=bridgePointDistance(item,actor.x,actor.y);
  if(p.distance>=28||p.t<=.02||p.t>=.98)continue;
  const segment=Number.isInteger(v.segment)?clamp(v.segment,0,path.length-2):null,fraction=clamp(v.fraction??actor.fraction??0,0,1);
  let rise=0;
  if(segment!=null){
   const a=path[segment],b=path[segment+1];
   if(item.cellSet.has(a))rise=item.cellSet.has(b)?1:1-fraction;
   else if(item.cellSet.has(b))rise=fraction;
  }else{
   // Cargo and bus actors carry route identity but not a simulation segment.
   // Search only this tiny span, and only when the actor is spatially nearby.
   const center=item.cells.find((q,i)=>item.cellSet.has(item.bridge.cells[i])&&path.includes(item.bridge.cells[i])&&Math.hypot(actor.x-q[0],actor.y-q[1])<25);
   if(center)rise=1;
  }
  if(!rise&&p.distance<18){
   const nearby=segment==null?path: path.slice(Math.max(0,segment-1),Math.min(path.length,segment+3));
   if(nearby.some(id=>item.cellSet.has(id)))rise=.65;
  }
  if(rise>0)return {item,rise};
 }
 return null;
}
function bridgePaint(g,item){
 const {first,last,bridge}=item,dx=last[0]-first[0],dy=last[1]-first[1],length=Math.hypot(dx,dy)||1,
  ux=dx/length,uy=dy/length,nx=-uy*13,ny=ux*13,raise=17;
 const A=[first[0],first[1]-raise],B=[last[0],last[1]-raise],leftA=[A[0]+nx,A[1]+ny],leftB=[B[0]+nx,B[1]+ny],rightA=[A[0]-nx,A[1]-ny],rightB=[B[0]-nx,B[1]-ny];
 // Water-side piers remain below the slab; sparse spans leave the current
 // river texture visible through both sides and between supports.
 const count=Math.max(1,Math.floor(bridge.cells.length/2));
 for(let i=1;i<=count;i++){
  const t=i/(count+1),x=A[0]+dx*t,y=A[1]+dy*t;
  const footY=y+19;
  segment(g,[x-5,y+3],[x-4,footY],'#52665e',5);segment(g,[x+5,y+3],[x+4,footY],'#52665e',5);
  segment(g,[x-4,footY-2],[x+4,footY-2],'#867f65',2);
 }
 // Tapered landward approaches connect the higher deck to each bank road.
 for(const [bank,deck,sign] of [[first,A,1],[last,B,-1]]){
  const end=[bank[0]+ux*sign*13,bank[1]+uy*sign*13];
  segment(g,[bank[0],bank[1]-2],end,'#9b9279',27);
  segment(g,[bank[0],bank[1]-3],end,'#616f68',21);
  for(const side of [-1,1]){
   const x=bank[0]+nx*side*.72,y=bank[1]+ny*side*.72-raise*.45;
   segment(g,[x,y],[deck[0]+nx*side*.72,deck[1]+ny*side*.72],'#6f8274',2);
  }
 }
 // Concrete fascia and a muted asphalt deck, with a readable center dash.
 segment(g,[leftA[0],leftA[1]+4],[leftB[0],leftB[1]+4],'#45574f',7);
 segment(g,[rightA[0],rightA[1]+4],[rightB[0],rightB[1]+4],'#45574f',7);
 segment(g,A,B,'#b9ad8d',29);segment(g,A,B,bridge.closed?'#625f55':'#515f58',23);
 if(!bridge.closed){g.setLineDash([8,8]);segment(g,[A[0],A[1]-1],[B[0],B[1]-1],'#d4c797',1.25);g.setLineDash([]);}
 for(const side of [-1,1]){
  const p=side===1?leftA:rightA,q=side===1?leftB:rightB;
  segment(g,[p[0],p[1]-6],[q[0],q[1]-6],bridge.closed?'#766c56':'#708278',2.4);
  segment(g,[p[0],p[1]-2],[q[0],q[1]-2],bridge.closed?'#857b63':'#aeb69a',1.1);
  const posts=Math.max(2,bridge.cells.length);
  for(let i=0;i<=posts;i++){
   const t=i/posts,x=p[0]+(q[0]-p[0])*t,y=p[1]+(q[1]-p[1])*t;
   segment(g,[x,y+3],[x,y-7],bridge.closed?'#665e4c':'#536d64',1.4);
  }
 }
 if(bridge.closed){
  for(const [x,y] of [A,B]){
   segment(g,[x-6,y-11],[x+6,y-4],'#c27a4e',3);
   segment(g,[x-6,y-4],[x+6,y-11],'#c27a4e',3);
  }
 }else if(bridge.condition<60){
  // Real condition is expressed as restrained repair patches, not fake damage.
  const t=.35,x=A[0]+dx*t,y=A[1]+dy*t;
  segment(g,[x-4,y-2],[x+3,y+2],'#98886a',2);
 }
}
function paintRoadBridgeLayers(g){for(const item of viewBuildings)if(item.kind==='roadBridge')bridgePaint(g,item);}
const bridgeTransitActorsBase=transitArtActors;
transitArtActors=function(visible){
 const result=bridgeTransitActorsBase(visible),routes=new Map((G.transit?.routes||[]).map(r=>[r.id,r]));
 for(const actor of result){const route=routes.get(actor.route);if(!route?.path?.length)continue;
  actor.v={path:route.path,style:route.mode==='bus'?'bus':'metro'};
 }
 return result;
};

const bridgePaintSceneLayerBase=paintSceneLayer;
paintSceneLayer=function(g,a){
 if(a.kind==='roadBridge'){bridgePaint(g,a);return;}
 const lift=bridgeTrafficLift(a);
 if(!lift){bridgePaintSceneLayerBase(g,a);return;}
 g.save();g.translate(0,-17*lift.rise);bridgePaintSceneLayerBase(g,a);g.restore();
};
const bridgeSceneActorPaintYBase=sceneActorPaintY;
sceneActorPaintY=function(a,bridges){
 const base=bridgeSceneActorPaintYBase(a,bridges),lift=bridgeTrafficLift(a);
 if(lift)return Math.max(base,lift.item.y+3);
 for(const item of viewBuildings)if(item.kind==='roadBridge'){
  const p=bridgePointDistance(item,a.x,a.y);
  if(p.distance<23&&p.t>.02&&p.t<.98)return Math.min(base,item.y-1);
 }
 return base;
};
