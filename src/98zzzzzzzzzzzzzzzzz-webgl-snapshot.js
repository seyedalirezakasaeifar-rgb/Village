// Committed read projection and existing-action adapter for an opt-in renderer.
// Context is read from model descriptors once per revision, never recomputed by
// mesh construction or inferred from decorative colours.
let cityVisualContextCache=null;
// Observe the accepted model's transaction-boundary invalidation in O(1).
// This epoch is transient, never archived, and does not compute demographics.
let cityVisualUrbanEpoch=0;
const cityVisualInvalidateUrban=invalidateUrban;
invalidateUrban=function(...args){const result=cityVisualInvalidateUrban.apply(this,args);cityVisualUrbanEpoch++;return result;};
function cityVisualContext(){
 const revision=window.__cityVisualRevision();if(cityVisualContextCache?.town===G&&cityVisualContextCache.revision===revision)return cityVisualContextCache;
 const districts={},properties=new Map(),households=new Map(),gatherings=new Map((typeof civicGatheringCues==='function'?civicGatheringCues():[]).map(e=>[e.venue,e]));
 for(const h of G.households){const residents=h.people.filter(id=>G.people[id]&&!G.people[id].deceased&&!G.people[id].movedAway).length;if(!residents)continue;const q=households.get(h.home)||{residents:0,afterTaxIncome:0,rent:0};q.residents+=residents;q.afterTaxIncome+=Math.max(0,(h.income||0)-(h.tax||0));q.rent+=h.rent||0;households.set(h.home,q);}
 const mapHomes=new Map(),crime=new Map();
 if(['healthAccess','schoolAccess'].includes(overlay))for(const h of serviceAccess(overlay==='healthAccess'?'health':'school').households){const q=mapHomes.get(h.home)||{served:0,residents:0};q.served+=h.served;q.residents+=h.residents;mapHomes.set(h.home,q);}
 if(overlay==='crime')for(const e of G.cases||[])if(Number.isInteger(e.bid)&&G.day-e.day>=0&&G.day-e.day<30)crime.set(e.bid,(crime.get(e.bid)||0)+1);
 const roadNetwork=overlay==='roads'?graph():null;
 const cue=(b,f)=>{const h=G.households[b.hh],a=mapHomes.get(b.id);if(overlay==='roads')return roadNetwork.portals.has(b.id)?{label:'+',shape:'circle',color:'#86b796'}:{label:'X',shape:'square',color:'#c58b73'};if(overlay==='business'&&f)return f.closed?{label:'X',shape:'triangle',color:'#bf826c'}:f.profit>0?{label:'+',shape:'circle',color:'#8db38b'}:{label:'=',shape:'square',color:'#c6af73'};if(overlay==='hardship'&&h)return h.stress>50?{label:'!',shape:'triangle',color:'#c58b73'}:{label:'.',shape:'circle',color:'#8db38b'};if(overlay==='land')return b.value>90000?{label:'^',shape:'triangle',color:'#c39372'}:b.value>45000?{label:'=',shape:'square',color:'#c6af73'}:{label:'.',shape:'circle',color:'#8db38b'};if(a)return a.served>=a.residents-1e-6?{label:'+',shape:'circle',color:'#8db38b'}:a.served?{label:'!',shape:'triangle',color:'#c6af73'}:{label:'X',shape:'square',color:'#bf826c'};if(crime.has(b.id))return {label:String(Math.min(9,crime.get(b.id))),shape:crime.get(b.id)>1?'square':'circle',color:'#c6af73'};if(['transit','metro'].includes(overlay)&&['metro_station','elevated_station','transit_depot'].includes(b.kind))return {label:b.kind==='transit_depot'?'D':'M',shape:b.kind==='transit_depot'?'square':'circle',color:'#84aaa9'};return null;};
 const lamps=[],occupied=new Set(G.buildings.flatMap(footprintOf));
 if(gameOptions.decor&&gameOptions.quality!=='low')for(let y=2;y<T-2;y++)for(let x=2;x<T-2;x++){const id=roadId(x,y);if(id%3||G.tiles[id]!==0||occupied.has(id)||G.landUse?.[id]||hash(id+G.worldSeed)%13!==0)continue;if([roadId(x-1,y),roadId(x+1,y),roadId(x,y-1),roadId(x,y+1)].some(roadSurface))lamps.push({x,y,id});}
 for(const b of G.buildings){
  const key=typeof urbanBlockKey==='function'?urbanBlockKey(b.x,b.y):'';
  // Avoid ensureUrban() mutating a legacy/uninitialized archive during a draw.
  if(G.urban&&typeof urbanDescriptor==='function'&&!districts[key])districts[key]={...urbanDescriptor(b.x,b.y)};
  const f=G.firms[b.firm],project=G.projects.find(p=>p.id===b.id);let waterDistance=null;
  if(['home','farm','wharf','fishery'].includes(b.kind))for(let radius=1;radius<=4&&waterDistance==null;radius++)for(let dy=-radius;dy<=radius;dy++)for(let dx=-radius;dx<=radius;dx++){if(Math.abs(dx)+Math.abs(dy)!==radius)continue;const x=b.x+dx,y=b.y+dy;if(x>=0&&y>=0&&x<T&&y<T&&[2,4].includes(G.tiles[roadId(x,y)]))waterDistance=radius;}
  properties.set(b.id,{mapCue:cue(b,f),districtKey:key,architecture:G.urban&&typeof urbanBuildingDescriptor==='function'?urbanBuildingDescriptor(b):null,waterDistance,appearance:typeof propertyAppearance==='function'?{...propertyAppearance(b)}:null,tenure:{owner:b.owner,title:b.title?{...b.title}:null,municipalRehousing:!!b.municipalRehousing,relocationReserve:!!b.relocationReserve},household:households.get(b.id)||null,provider:typeof providerVisualState==='function'?providerVisualState(b):null,retailCentre:!!b.retailCentre,gathering:gatherings.get(b.id)||null,firm:f?{id:f.id,kind:f.kind,stock:{...f.stock},closed:!!f.closed,production:f.production||0,scale:f.scale||1,workersAssigned:f.workers.length}:null,stage:{redevelopment:!!b.redevelopment,project:project?{kind:project.kind,remaining:project.remaining,duration:project.duration??null,stalledDays:project.stalledDays||0}:null}});
 }
 return cityVisualContextCache={town:G,revision,districts,properties,lamps};
}
function cityVisualPath(path){if(path.length<3)return path.slice();const out=[path[0]];for(let i=1;i<path.length-1;i++)if(path[i]-path[i-1]!==path[i+1]-path[i])out.push(path[i]);out.push(path[path.length-1]);return out;}
window.__cityVisualSnapshot=()=>{if(!G||simulationBusy||roadBatchDirty)return null;const hall=G.buildings.find(b=>b.kind==='townhall')||{x:28,y:28},context=cityVisualContext();return {revision:window.__cityVisualRevision(),paused,night:nightMode,overlay,options:{fps:gameOptions.fps,quality:gameOptions.quality,decor:gameOptions.decor,largeText:gameOptions.largeText},lamps:context.lamps,charterBase:CHARTER_BASE,parcelFocus,parcels:ANNEX_PARCELS.map(p=>({id:p.id,name:p.name,x:p.x,y:p.y,w:p.w,h:p.h,owned:!!G.charter?.owned.includes(p.id)})),plans:Object.entries(G.urban?.zones||{}).map(([key,q])=>({key,x:Number(key.split(':')[0])*URBAN_BLOCK,y:Number(key.split(':')[1])*URBAN_BLOCK,w:URBAN_BLOCK,h:URBAN_BLOCK,plan:q.plan})),districtSemanticsAccepted:true,day:G.day,population:G.stats.population,treasury:G.treasury,total:totalMoney(),rng:rngState,size:T,center:{x:hall.x,y:hall.y},tiles:G.tiles.slice(),landUse:{...(G.landUse||{})},fieldOwner:{...(G.fieldOwner||{})},districts:context.districts,buildings:G.buildings.map(b=>({id:b.id,x:b.x,y:b.y,kind:b.kind,condition:b.condition,footprint:footprintOf(b).slice(),...context.properties.get(b.id)})),metro:{operating:!!G.metro?.operating,lines:(G.metro?.lines||[]).map(l=>({...l,ready:!l.readyDay||l.readyDay<=G.day}))},airport:G.airport?{building:G.airport.building,runway:G.airport.runway.slice(),completed:readBuild(G.airport.building)?.kind==='airport',operating:!!G.airport.operating}:null,transit:{tracks:(G.transit?.tracks||[]).slice(),routes:(G.transit?.routes||[]).map(r=>({id:r.id,mode:r.mode,color:r.color,operating:!!r.stats?.operating,path:r.path.slice(),renderPath:cityVisualPath(r.path),stops:r.stops.slice()}))},bridges:typeof bridgeRenderSnapshot==='function'?bridgeRenderSnapshot():[]};};
window.__cityVisualSave=()=>save();
window.__cityVisualRevision=()=>G&&!simulationBusy&&!roadBatchDirty?[cityVisualUrbanEpoch,G.day,G.construction,roadsVersion,G.bridgeRevision||0,G.transit?.revision||0,G.urban?.revision||0,G.regionalTrade?.serial||0,G.regionalTrade?.shipments?.length||0,nightMode,overlay,gameOptions.quality,gameOptions.decor,gameOptions.largeText,gameOptions.fps,G.charter?.revision||0,parcelFocus].join(':'):'';
window.__cityVisualTap=(x,y)=>{if(!G||simulationBusy||!Number.isInteger(x)||!Number.isInteger(y)||x<0||y<0||x>=T||y>=T)return false;const p=roadCenter(roadId(x,y)),r=cv.getBoundingClientRect();onTap(r.left+cw/2+(p[0]-cam.x)*cam.zoom,r.top+ch/2+(p[1]-cam.y)*cam.zoom);return true;};
// Live presentation bridge. Cooperative partial days are never inspected.
window.__cityVisualMotionState=()=>G?{paused,busy:simulationBusy||roadBatchDirty,clock:frameClock,reduced:gameOptions.reducedMotion}:null;
let cityVisualOrderCache=null;
window.__cityVisualActors=(detail,bounds)=>{
 window.__cityVisualActorWork={sources:0,positions:0};
 if(!G||simulationBusy||roadBatchDirty||detail==='far'||gameOptions.reducedMotion||!gameOptions.traffic)return [];
 const work=window.__cityVisualActorWork,actors=[],near=detail==='near';
 const project=(p,elevation=0)=>({x:(p.x-RW/2)/TW+(p.y+elevation-32-TH/2)/TH,z:(p.y+elevation-32-TH/2)/TH-(p.x-RW/2)/TW,dx:p.dx/TW+p.dy/TH,dz:p.dy/TH-p.dx/TW});
 const visible=p=>!bounds||p.x>=bounds.minX&&p.x<=bounds.maxX&&p.z>=bounds.minZ&&p.z<=bounds.maxZ;
 const add=(id,kind,p,color,elevation=0)=>{work.positions++;const q=project(p,elevation);if(kind==='bus'||kind==='train'){const length=Math.hypot(q.dx,q.dz)||1,lane=kind==='train'?.15:.13;q.x+=q.dz/length*lane;q.z-=q.dx/length*lane;}if(visible(q)&&actors.length<64)actors.push({id,kind,...q,color,opacity:p.opacity??1});};
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

// Existing visit commands retain their original legal/tool behavior, then move
// the active camera. No UI command or property selection is reimplemented.
const cityVisualProjectVisit=civicProjectVisit;civicProjectVisit=function(x,y,...args){cityVisualProjectVisit(x,y,...args);window.__webglTaste?.focus(x,y,1.5);};
window.__cityVisualCameraChanged=({x,z,zoom,height})=>{document.body.classList.toggle('surveying-region',overlay==='charter');$('gameRoot').classList.toggle('building-map',!!buildMode);if(typeof updateRegionSurvey==='function')updateRegionSurvey();const p=iso(x,z);cam.x=p[0];cam.y=p[1];cam.zoom=clamp(zoom*height/1018.23,.025,1.7);if(typeof updateRegionLocator==='function')updateRegionLocator();if(typeof updateMapOverlayKey==='function')updateMapOverlayKey();if(overlay==='transit'&&$('mapStatusOverlayKey'))$('mapStatusOverlayKey').textContent='TRANSIT · solid bus · dashed elevated · route ID labels · dim means inactive';if(overlay==='neighbourhoods'&&$('mapStatusOverlayKey'))$('mapStatusOverlayKey').textContent='PLANS · A agriculture · C civic · R residential · E employment · M market-led';};
document.addEventListener('click',e=>{const target=e.target.closest('[data-inspect],[data-house],[data-firm]');if(!target||!window.__webglTaste)return;setTimeout(()=>{const b=readBuild(selected?.id);if(b)window.__webglTaste?.focus(b.x,b.y,1.5);},0);});
window.__cityVisualTool=()=>buildMode;
window.__cityVisualRoadStroke=(points,finish=false)=>{if(!G||simulationBusy)return false;if(finish){flushRoadBatch();return true;}if(buildMode!=='road')return false;for(const p of points.slice(0,512))if(Number.isInteger(p.x)&&Number.isInteger(p.y)&&p.x>=0&&p.y>=0&&p.x<T&&p.y<T)construct('road',p.x,p.y,true);return true;};
window.__cityVisualPlacementMode=()=>buildMode==='road'||buildMode==='repair'||!!(types[buildMode]?.build&&buildMode!=='inspect');

window.__cityVisualInspectBuilding=id=>{if(!G||simulationBusy)return false;const b=readBuild(id);if(!b)return false;if(buildMode||transitDraft||overlay==='charter')return window.__cityVisualTap(b.x,b.y);selected={id};openPanel('inspect');dirty=true;return true;};
window.__cityVisualInspectActor=id=>{
 if(!G||simulationBusy||buildMode||transitDraft)return false;const [kind,key]=id.split(':'),n=Number(key);
 if(kind==='road'){const v=traffic.find(v=>v.id===n);if(!v)return false;inspectedTrip={...v,path:v.path.slice()};openPanel('trip');}
 else if(kind==='cargo'){const o=G.regionalTrade?.shipments.find(o=>o.id===n);if(!o)return false;inspectedTrip={regional:o.id,path:(o.activePath?.length?o.activePath:o.path).slice()};openPanel('trip');}
 else if(kind==='transit'){if(!G.transit?.routes.some(r=>r.id===n))return false;showTransitDemandReport(n);}
 else if(kind==='vessel'){const a=waterfrontActors(()=>true).find(a=>a.id===n);if(!a)return false;selectedWaterTrip={firm:a.f.id,token:a.lastToken,consignment:a.consignment,cargo:a.cargo,quantity:a.quantity,path:a.path.slice(),returning:a.returning};selected={id:a.f.building};openPanel('inspect');}
 else return false;dirty=true;return true;
};

const cityVisualParcelPreview=previewParcel;previewParcel=function(id){cityVisualParcelPreview(id);const p=ANNEX_PARCELS.find(p=>p.id===id);if(p)window.__webglTaste?.focus(p.x+p.w/2,p.y+p.h/2,Math.max(.2,18/Math.max(p.w,p.h)));};
window.__cityVisualClearCharter=()=>{if(overlay==='charter'){overlay='none';parcelFocus=null;dirty=true;}};
document.addEventListener('click',e=>{const b=e.target.closest('[data-charter-home],[data-charter-overview]');if(!b||!window.__webglTaste)return;if(b.hasAttribute('data-charter-overview'))window.__webglTaste.overview();else{const h=G.buildings.find(b=>b.kind==='townhall');if(h)window.__webglTaste.focus(h.x,h.y,1);}});

const cityVisualNavigateDistrict=navigateDistrict;navigateDistrict=function(which){cityVisualNavigateDistrict(which);if(!window.__webglTaste||!G)return;const list=which==='farms'?G.buildings.filter(b=>b.kind==='farm'):which==='main'?G.buildings.filter(b=>b.firm>=0&&!['farm','forestry','quarry'].includes(b.kind)):G.buildings;if(list.length)window.__webglTaste.focus(list.reduce((n,b)=>n+b.x,0)/list.length,list.reduce((n,b)=>n+b.y,0)/list.length,which==='all'?.65:1.5);};

window.__cityVisualQualityNotice=text=>toast(text);
