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
window.__cityVisualSnapshot=()=>{if(!G||simulationBusy)return null;const hall=G.buildings.find(b=>b.kind==='townhall')||{x:28,y:28},context=cityVisualContext();return {revision:window.__cityVisualRevision(),paused,day:G.day,population:G.stats.population,treasury:G.treasury,total:totalMoney(),rng:rngState,size:T,center:{x:hall.x,y:hall.y},tiles:G.tiles.slice(),landUse:{...(G.landUse||{})},districts:context.districts,buildings:G.buildings.map(b=>({id:b.id,x:b.x,y:b.y,kind:b.kind,condition:b.condition,footprint:footprintOf(b).slice(),...context.properties.get(b.id)})),bridges:typeof bridgeRenderSnapshot==='function'?bridgeRenderSnapshot():[]};};
window.__cityVisualSave=()=>save();
window.__cityVisualRevision=()=>G&&!simulationBusy?[G.day,G.construction,roadsVersion,G.bridgeRevision||0].join(':'):'';
window.__cityVisualTap=(x,y)=>{if(!G||simulationBusy||!Number.isInteger(x)||!Number.isInteger(y)||x<0||y<0||x>=T||y>=T)return false;const p=roadCenter(roadId(x,y)),r=cv.getBoundingClientRect();onTap(r.left+cw/2+(p[0]-cam.x)*cam.zoom,r.top+ch/2+(p[1]-cam.y)*cam.zoom);return true;};
