// Read-only physical district surveys. Existing placement and accounting stay authoritative.
const CIVIC_BLUEPRINT_KINDS={industry:['factory','warehouse'],neighbourhood:['grocer','bakery'],waterfront:['fishery','wharf']};
function civicBlueprintInside(p,x,y){return x>=p.x&&x<p.x+p.w&&y>=p.y&&y<p.y+p.h;}
function civicBlueprintExisting(parcel,kind){return G.firms.filter(f=>!f.closed&&f.kind===kind).map(f=>({f,b:readBuild(f.building)})).find(v=>v.b&&civicBlueprintInside(parcel,v.b.x,v.b.y));}
function civicBlueprintRoadAllowed(id,blocked){
 const x=id%T,y=id/T|0;if(x<0||x>=T||y<0||y>=T||blocked.has(id))return false;
 return charterOwns(x,y)&&[0,1,3].includes(G.tiles[id])&&!buildingAt(x,y)&&!G.landUse?.[id];
}
function civicBlueprintNeighbours(id){const x=id%T,y=id/T|0,result=[];for(const [dx,dy]of roadOffsets){const xx=x+dx,yy=y+dy;if(xx>=0&&xx<T&&yy>=0&&yy<T)result.push(roadId(xx,yy));}return result;}
function civicBlueprintPathToLot(site,roads,blocked){
 const targets=new Set();for(const id of site.footprint)for(const n of civicBlueprintNeighbours(id))if(!site.footprint.includes(n)&&civicBlueprintRoadAllowed(n,blocked))targets.add(n);
 const prev=new Int32Array(T*T);prev.fill(-2);const queue=[];
 for(const id of roads){if(blocked.has(id))continue;prev[id]=-1;queue.push(id);}
 let end=null;for(let n=0;n<queue.length;n++){const id=queue[n];if(targets.has(id)){end=id;break;}for(const next of civicBlueprintNeighbours(id)){if(prev[next]!==-2||!civicBlueprintRoadAllowed(next,blocked))continue;prev[next]=id;queue.push(next);}}
 if(end==null)return null;const path=[];for(let id=end;id>=0;id=prev[id])path.push(id);path.reverse();return path;
}
function civicBlueprintRoadDistances(roads,blocked=new Set()){const distance=new Int32Array(T*T);distance.fill(-1);const queue=[];for(const id of roads){distance[id]=0;queue.push(id);}for(let n=0;n<queue.length;n++){const id=queue[n];for(const next of civicBlueprintNeighbours(id))if(distance[next]<0&&civicBlueprintRoadAllowed(next,blocked)){distance[next]=distance[id]+1;queue.push(next);}}return distance;}
function civicBlueprintCandidates(parcel,kind,roads,blocked=new Set(),preferred=null){
 const distance=civicBlueprintRoadDistances(roads,blocked),center={x:parcel.x+parcel.w/2,y:parcel.y+parcel.h/2},result=[];
 for(let y=parcel.y;y<parcel.y+parcel.h;y++)for(let x=parcel.x;x<parcel.x+parcel.w;x++){
  if(!canPlace(x,y,false,kind))continue;const footprint=footprintFor(x,y,kind);
  if(footprint.some(id=>blocked.has(id)||roads.has(id)||!civicBlueprintInside(parcel,id%T,id/T|0)))continue;
  const adjacent=footprint.flatMap(civicBlueprintNeighbours).filter(id=>!footprint.includes(id)),reach=Math.min(...adjacent.filter(id=>distance[id]>=0).map(id=>distance[id]));if(!Number.isFinite(reach))continue;
  result.push({kind,x,y,footprint,score:reach+Math.abs(x-center.x)*(kind==='fishery'||kind==='wharf'?.35:2)+Math.abs(y-center.y)*2,preferred:!!preferred&&preferred.x===x&&preferred.y===y});
 }
 result.sort((a,b)=>Number(b.preferred)-Number(a.preferred)||a.score-b.score||a.y-b.y||a.x-b.x);return result.slice(0,8);
}
let civicBlueprintCacheTown=null,civicBlueprintCache=new Map();
function civicDistrictBlueprint(project,fresh=false){
 const parcel=ANNEX_PARCELS.find(p=>p.id===project.target),kinds=CIVIC_BLUEPRINT_KINDS[project.branch];if(!parcel||!kinds)return {ok:false,reason:'No supported district purpose is selected.'};
 if(!G.charter.owned.includes(parcel.id))return {ok:false,reason:'Acquire this district’s development rights before commissioning its roads.'};
 if(G.districtProgrammes?.[parcel.id]?.focus!==project.branch)return {ok:false,reason:'Record the intended district charter before commissioning its physical plan.'};
 if(civicBlueprintCacheTown!==G){civicBlueprintCacheTown=G;civicBlueprintCache=new Map();}
 const net=graph(),key=parcel.id+':'+project.branch,existing=kinds.map(kind=>civicBlueprintExisting(parcel,kind)),revision=[roadsVersion,G.urban?.revision||0,G.charter.revision,G.buildings.length,Object.keys(G.landUse||{}).length,existing.map(v=>v?.f.id??'-').join(','),(project.sitePlans||[]).map(s=>s.kind+':'+s.x+','+s.y).join('|')].join('/'),cached=civicBlueprintCache.get(key);
 if(!fresh&&cached?.net===net&&cached.revision===revision)return cached.plan;
 const roads=new Set([...net.neighbors.keys()].filter(id=>net.parts[id]===net.mainPart)),fixed=existing.filter(Boolean).map(v=>({kind:v.f.kind,x:v.b.x,y:v.b.y,footprint:footprintOf(v.b),existing:v.b.id,firm:v.f.id})),fixedCells=new Set(fixed.flatMap(s=>s.footprint));
 const preferred=kind=>(project.sitePlans||[]).find(s=>s.kind===kind),firsts=existing[0]?[fixed.find(s=>s.kind===kinds[0])]:civicBlueprintCandidates(parcel,kinds[0],roads,fixedCells,preferred(kinds[0]));let best=null;
 for(const first of firsts){
  const blocked=new Set([...fixedCells,...first.footprint]),path=civicBlueprintPathToLot(first,roads,blocked);if(!path)continue;
  const connected=new Set([...roads,...path]),roadCells=path.filter(id=>G.tiles[id]!==1),seconds=existing[1]?[fixed.find(s=>s.kind===kinds[1])]:civicBlueprintCandidates(parcel,kinds[1],connected,blocked,preferred(kinds[1]));
  for(const second of seconds){const both=new Set([...blocked,...second.footprint]),path2=civicBlueprintPathToLot(second,connected,both);if(!path2)continue;const cells=[...new Set([...roadCells,...path2.filter(id=>G.tiles[id]!==1)])],candidate={ok:true,parcel:parcel.id,focus:project.branch,roads:cells,sites:[first,second],cost:cells.length*buildCost.road};if(!best||cells.length<best.roads.length)best=candidate;break;}
  if(best?.cost===0)break;
 }
 const plan=best||{ok:false,parcel:parcel.id,focus:project.branch,reason:'No pair of legally vacant, connected sites fits this purpose without crossing existing buildings, reservations or water. Review another tract or draw an alternative street connection.'};civicBlueprintCache.set(key,{net,revision,plan});return plan;
}
function civicBlueprintSignature(plan){return plan.ok?plan.roads.join(',')+'|'+plan.sites.map(s=>s.kind+':'+s.x+','+s.y+':'+(s.existing||0)).join('|'):'';}

function civicBlueprintSites(plan){return plan.sites.map(s=>({kind:s.kind,x:s.x,y:s.y}));}
function validateCivicSitePlans(project){
 if(project.sitePlans==null)return true;if(!Array.isArray(project.sitePlans)||project.sitePlans.length>2||project.kind!=='district')return false;const cells=new Set();
 return project.sitePlans.every((s,i,a)=>s&&CIVIC_BLUEPRINT_KINDS[project.branch]?.includes(s.kind)&&a.findIndex(v=>v.kind===s.kind)===i&&Number.isInteger(s.x)&&Number.isInteger(s.y)&&s.x>=2&&s.y>=2&&s.x<T-2&&s.y<T-2&&footprintFor(s.x,s.y,s.kind).every(id=>{const p=ANNEX_PARCELS.find(p=>p.id===project.target);if(!p||!civicBlueprintInside(p,id%T,id/T|0)||cells.has(id))return false;cells.add(id);return true;}));
}
