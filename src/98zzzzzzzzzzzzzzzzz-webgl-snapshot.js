// Committed read projection and existing-action adapter for an opt-in renderer.
// Context is read from model descriptors once per revision, never recomputed by
// mesh construction or inferred from decorative colours.
let cityVisualContextCache=null;
function cityVisualContext(){
 const revision=window.__cityVisualRevision();if(cityVisualContextCache?.town===G&&cityVisualContextCache.revision===revision)return cityVisualContextCache;
 const districts={},properties=new Map(),households=new Map();
 for(const h of G.households){if(!h.people.length)continue;const q=households.get(h.home)||{residents:0,afterTaxIncome:0,rent:0};q.residents+=h.people.length;q.afterTaxIncome+=Math.max(0,(h.income||0)-(h.tax||0));q.rent+=h.rent||0;households.set(h.home,q);}
 for(const b of G.buildings){
  const key=typeof urbanBlockKey==='function'?urbanBlockKey(b.x,b.y):'';
  // Avoid ensureUrban() mutating a legacy/uninitialized archive during a draw.
  if(G.urban&&typeof urbanDescriptor==='function'&&!districts[key])districts[key]={...urbanDescriptor(b.x,b.y)};
  const f=G.firms[b.firm],project=G.projects.find(p=>p.id===b.id);let waterDistance=null;
  if(['home','farm','wharf','fishery'].includes(b.kind))for(let radius=1;radius<=4&&waterDistance==null;radius++)for(let dy=-radius;dy<=radius;dy++)for(let dx=-radius;dx<=radius;dx++){if(Math.abs(dx)+Math.abs(dy)!==radius)continue;const x=b.x+dx,y=b.y+dy;if(x>=0&&y>=0&&x<T&&y<T&&[2,4].includes(G.tiles[roadId(x,y)]))waterDistance=radius;}
  properties.set(b.id,{districtKey:key,architecture:G.urban&&typeof urbanBuildingDescriptor==='function'?urbanBuildingDescriptor(b):null,waterDistance,appearance:typeof propertyAppearance==='function'?{...propertyAppearance(b)}:null,tenure:{owner:b.owner,title:b.title?{...b.title}:null,municipalRehousing:!!b.municipalRehousing,relocationReserve:!!b.relocationReserve},household:households.get(b.id)||null,provider:typeof providerVisualState==='function'?providerVisualState(b):null,retailCentre:!!b.retailCentre,firm:f?{kind:f.kind,closed:!!f.closed,production:f.production||0,scale:f.scale||1,workersAssigned:f.workers.length}:null,stage:{redevelopment:!!b.redevelopment,project:project?{kind:project.kind,remaining:project.remaining,duration:project.duration??null,stalledDays:project.stalledDays||0}:null}});
 }
 return cityVisualContextCache={town:G,revision,districts,properties};
}
window.__cityVisualSnapshot=()=>{if(!G||simulationBusy)return null;const hall=G.buildings.find(b=>b.kind==='townhall')||{x:28,y:28},context=cityVisualContext();return {revision:window.__cityVisualRevision(),paused,day:G.day,population:G.stats.population,treasury:G.treasury,total:totalMoney(),rng:rngState,size:T,center:{x:hall.x,y:hall.y},tiles:G.tiles.slice(),landUse:{...(G.landUse||{})},districts:context.districts,buildings:G.buildings.map(b=>({id:b.id,x:b.x,y:b.y,kind:b.kind,condition:b.condition,footprint:footprintOf(b).slice(),...context.properties.get(b.id)})),transit:{tracks:(G.transit?.tracks||[]).slice(),routes:(G.transit?.routes||[]).map(r=>({id:r.id,mode:r.mode,color:r.color,operating:!!r.stats?.operating,path:r.path.slice(),stops:r.stops.slice()}))},bridges:typeof bridgeRenderSnapshot==='function'?bridgeRenderSnapshot():[]};};
window.__cityVisualSave=()=>save();
window.__cityVisualRevision=()=>G&&!simulationBusy?[G.day,G.construction,roadsVersion,G.bridgeRevision||0,G.transit?.revision||0,G.urban?.revision||0].join(':'):'';
window.__cityVisualTap=(x,y)=>{if(!G||simulationBusy||!Number.isInteger(x)||!Number.isInteger(y)||x<0||y<0||x>=T||y>=T)return false;const p=roadCenter(roadId(x,y)),r=cv.getBoundingClientRect();onTap(r.left+cw/2+(p[0]-cam.x)*cam.zoom,r.top+ch/2+(p[1]-cam.y)*cam.zoom);return true;};
// Live presentation bridge. Cooperative partial days are never inspected.
window.__cityVisualMotionState=()=>G?{paused,busy:simulationBusy,clock:frameClock,reduced:gameOptions.reducedMotion}:null;
let cityVisualOrderCache=null;
window.__cityVisualActors=(detail,bounds)=>{
 window.__cityVisualActorWork={sources:0,positions:0};
 if(!G||simulationBusy||detail==='far'||gameOptions.reducedMotion||!gameOptions.traffic)return [];
 const work=window.__cityVisualActorWork,actors=[],near=detail==='near';
 const project=(p,elevation=0)=>({x:(p.x-RW/2)/TW+(p.y+elevation-32-TH/2)/TH,z:(p.y+elevation-32-TH/2)/TH-(p.x-RW/2)/TW,dx:p.dx/TW+p.dy/TH,dz:p.dy/TH-p.dx/TW});
 const visible=p=>!bounds||p.x>=bounds.minX&&p.x<=bounds.maxX&&p.z>=bounds.minZ&&p.z<=bounds.maxZ;
 const add=(id,kind,p,color,elevation=0)=>{work.positions++;const q=project(p,elevation);if(visible(q)&&actors.length<64)actors.push({id,kind,...q,color});};
 for(const v of traffic){work.sources++;if(v.style==='pedestrian'&&!near)continue;add('road:'+v.id,v.style==='pedestrian'?'pedestrian':v.style==='truck'||v.style==='tractor'?'truck':'car',vehiclePosition(v),v.color);}
 const revision=window.__cityVisualRevision();if(cityVisualOrderCache?.town!==G||cityVisualOrderCache.revision!==revision)cityVisualOrderCache={town:G,revision,orders:(G.regionalTrade?.shipments||[]).filter(o=>regionalShipmentVisualState(o)?.visible!==false).slice(0,16)};
 for(const o of cityVisualOrderCache.orders){work.sources++;const p=shipmentVisualPose(o);if(p)add('cargo:'+o.id,'truck',p,o.direction==='import'?'#698e89':'#b48c58');}
 const ordinals=new Map();for(const p of transitArtActors(()=>true,frameClock,1)){work.sources++;const ordinal=ordinals.get(p.route)||0;ordinals.set(p.route,ordinal+1);add('transit:'+p.route+':'+ordinal,p.mode==='elevated'?'train':'bus',p,p.color,p.elevation);}
 if(gameOptions.effects&&gameOptions.quality!=='low')for(const p of waterfrontActors((x,y)=>visible(project({x,y,dx:1,dy:0})))){work.sources++;add('vessel:'+p.id,'boat',p,p.consignment?'#b18b57':'#648778');}
 return actors;
};
const cityVisualCanvasBudget=visualDetailBudget;
visualDetailBudget=function(){const v=window.__webglTaste;if(!v)return cityVisualCanvasBudget();return {traffic:v.lod!=='far'&&gameOptions.traffic&&!gameOptions.reducedMotion,people:v.lod==='near'&&gameOptions.effects&&!gameOptions.reducedMotion,boats:v.lod!=='far'&&gameOptions.traffic&&gameOptions.effects&&!gameOptions.reducedMotion&&gameOptions.quality!=='low'};};
const cityVisualCanvasDraw=draw;
draw=function(){if(window.__webglTaste){dirty=false;return;}cityVisualCanvasDraw();};

window.__cityVisualResumeCanvas=()=>{staticDirty=true;dirty=true;draw();};
