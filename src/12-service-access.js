// Road catchments and shared facility capacity. No clinic/school can count its
// same places twice when catchments overlap. Derived data is never save authority.
const serviceAccessCaches=new Map();
function serviceAccess(kind,extraSite=null){
 const standard=CIVIC_STANDARDS[kind],net=graph(),limit=kind==='health'?60:40;
 const facilities=G.buildings.filter(b=>b.kind===standard.building&&isPublicFacility(b));if(extraSite)facilities.push(extraSite);const homes=G.households.map(h=>({id:h.id,home:h.home,residents:h.people.filter(id=>G.people[id]&&!G.people[id].deceased&&!G.people[id].movedAway).length})).filter(h=>h.residents);
 const key=facilities.map(b=>b.id).join(',')+'|'+homes.map(h=>h.id+':'+h.home+':'+h.residents).join(',');
 const old=extraSite?null:serviceAccessCaches.get(kind);if(old&&old.town===G&&old.net===net&&old.key===key)return old.result;
 const totalNodes=facilities.length+homes.length+2,sink=totalNodes-1,edges=Array.from({length:totalNodes},()=>[]),homeEdges=[],distances=[],facilityEdges=[],connections=[];
 const link=(a,b,capacity)=>{const edge={to:b,capacity,reverse:edges[b].length};edges[a].push(edge);edges[b].push({to:a,capacity:0,reverse:edges[a].length-1});return edge;};
 facilities.forEach((facility,i)=>{
  facilityEdges.push(link(0,i+1,standard.capacity));connections.push([]);const distance=new Map(),queue=[];
  const start=facility===extraSite?extraSite.port:net.portals.get(facility.id);if(start!=null){distance.set(start,0);queue.push(start);}
  for(let n=0;n<queue.length;n++){const id=queue[n],d=distance.get(id);if(d>=limit)continue;for(const next of net.neighbors.get(id)||[])if(!distance.has(next)){distance.set(next,d+1);queue.push(next);}}
  distances.push(distance);
 });
 homes.forEach((h,j)=>{const node=1+facilities.length+j;homeEdges.push(link(node,sink,h.residents));const port=net.portals.get(h.home);facilities.forEach((_,i)=>{if(port!=null&&distances[i].has(port))connections[i].push({home:j,edge:link(i+1,node,h.residents)});});});
 let served=0;
 // Seed a proportional allocation before augmenting residual paths. Shared
 // shortages therefore do not automatically exclude the last household ID.
 for(let round=0;round<12;round++){
  const offers=[],totals=homes.map(()=>0);
  connections.forEach((links,i)=>{const demand=links.reduce((n,c)=>n+homeEdges[c.home].capacity,0),supply=facilityEdges[i].capacity;if(demand<1e-8||supply<1e-8)return;
   for(const c of links){const amount=Math.min(1,supply/demand)*homeEdges[c.home].capacity;if(amount>1e-8){offers.push({i,c,amount});totals[c.home]+=amount;}}});
  const scales=totals.map((offered,j)=>offered?Math.min(1,homeEdges[j].capacity/offered):0);let moved=0;
  for(const {i,c,amount} of offers){const value=amount*scales[c.home];if(value<1e-8)continue;const homeNode=1+facilities.length+c.home,sourceEdge=facilityEdges[i],sinkEdge=homeEdges[c.home];
   sourceEdge.capacity-=value;edges[i+1][sourceEdge.reverse].capacity+=value;c.edge.capacity-=value;edges[homeNode][c.edge.reverse].capacity+=value;sinkEdge.capacity-=value;edges[sink][sinkEdge.reverse].capacity+=value;moved+=value;}
  served+=moved;if(moved<1e-8)break;
 }

 // Residual paths also reassign an earlier place when another household has
 // fewer alternatives, avoiding order-dependent greedy catchment allocation.
 for(;;){const parents=Array(totalNodes).fill(null),queue=[0];parents[0]=[-1,-1];
  for(let n=0;n<queue.length&&!parents[sink];n++){const at=queue[n];for(let e=0;e<edges[at].length;e++){const edge=edges[at][e];if(edge.capacity>1e-8&&!parents[edge.to]){parents[edge.to]=[at,e];queue.push(edge.to);}}}
  if(!parents[sink])break;let amount=Infinity;
  for(let at=sink;at!==0;){const [from,index]=parents[at];amount=Math.min(amount,edges[from][index].capacity);at=from;}
  for(let at=sink;at!==0;){const [from,index]=parents[at],edge=edges[from][index];edge.capacity-=amount;edges[at][edge.reverse].capacity+=amount;at=from;}served+=amount;
 }
 // Household membership is authoritative at this point in the daily tick.
 // G.stats.population is a published aggregate that can still describe the
 // prior tick while births, arrivals, or archive restoration have changed the
 // household rows. Clamping to that stale aggregate poisons this cache entry
 // and makes same-day civic training differ after save/load.
 const population=homes.reduce((n,h)=>n+h.residents,0);
 const result={kind,limit,served:Math.min(served,population),population,coverage:population?Math.min(1,served/population):0,households:homes.map((h,j)=>{const port=net.portals.get(h.home),reachable=distances.map(d=>d.get(port)).filter(d=>d!=null),row={...h,served:clamp(h.residents-homeEdges[j].capacity,0,h.residents),distance:reachable.length?Math.min(...reachable):null};if(extraSite)row.siteDistance=port==null?null:distances[facilities.length-1].get(port)??null;return row;})};
 if(!extraSite)serviceAccessCaches.set(kind,{town:G,net,key,result});return result;
}
// Prospective civic-site routing reuses the live catchment allocator without
// adding a building, touching town state, or reserving any service capacity.
let placementServicePreviewCache=null;
function schoolPlacementPreview(x,y){
 const key=[G.day,roadsVersion,G.buildings.length,G.nextId,G.stats.population,x,y,G.treasury,G.policy.educationBudget].join(':');if(placementServicePreviewCache?.town===G&&placementServicePreviewCache.key===key)return placementServicePreviewCache.value;
 const cost=buildCost.school;if(!canPlace(x,y,true,'school'))return {valid:false,cost,affordable:G.treasury>=cost,treasury:G.treasury};
 const net=graph(),choices=[];for(const id of footprintFor(x,y,'school')){const xx=id%T,yy=id/T|0;for(const [dx,dy]of roadOffsets){const ax=xx+dx,ay=yy+dy;if(ax>=0&&ax<T&&ay>=0&&ay<T){const road=roadId(ax,ay);if(G.tiles[road]===1)choices.push(road);}}}
 const port=choices.find(id=>net.parts[id]===net.mainPart)??choices[0]??null,current=serviceAccess('school'),projected=serviceAccess('school',{id:-1,x,y,port});
 const currentReach=new Set(current.households.filter(h=>h.distance!=null).map(h=>h.id)),newlyReachable=projected.households.filter(h=>h.distance!=null&&!currentReach.has(h.id)).reduce((n,h)=>n+h.residents,0),incrementalPlaces=Math.max(0,projected.served-current.served),siteServed=projected.households.filter(h=>h.siteDistance!=null),siteResidents=siteServed.reduce((n,h)=>n+h.residents,0),siteMeanDistance=siteResidents?siteServed.reduce((n,h)=>n+h.siteDistance*h.residents,0)/siteResidents:null,siteBeyondLimit=projected.households.filter(h=>h.siteDistance==null).reduce((n,h)=>n+h.residents,0),population=projected.population,full=population*CIVIC_STANDARDS.school.staff/CIVIC_STANDARDS.school.capacity*Math.max(24,G.policy.minWage)/.65,reachableNeed=full*projected.coverage,provision=G.serviceProvision?.school,staffing=provision?.staffing,staffEligibleHomes=new Set(projected.households.filter(h=>h.distance!=null).map(h=>h.id)),neededLocal=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.age>=18&&p.age<=70&&p.job<0&&qualifiedForService(p,'school')&&staffEligibleHomes.has(p.hh)).length;
 const value={valid:true,cost,affordable:G.treasury>=cost,treasury:G.treasury,afterBuild:G.treasury-cost,limit:projected.limit,population,existingReach:current.served,projectedReach:projected.served,newlyReachable,incrementalPlaces,siteMeanDistance,siteBeyondLimit,educationBudget:Math.max(0,G.policy.educationBudget||0),reachableNeed,actualPaid:provision?.paid??null,actualCoverage:provision?.coverage??null,eligibleLocalStaff:neededLocal,staffing:staffing?{local:staffing.local,regional:staffing.regional,needed:staffing.needed,pending:staffing.pending}:null};placementServicePreviewCache={town:G,key,value};return value;
}
function schoolPlacementHint(x,y){
 const p=schoolPlacementPreview(x,y);if(!p.valid)return 'School siting · no vacant road-adjacent public site here';
 const current=p.actualCoverage==null?'not yet measured':Math.round(p.actualCoverage*100)+'% funded coverage · '+money(p.actualPaid||0)+'/day paid';
 const staff=p.staffing?Math.round(p.staffing.local+p.staffing.regional)+'/'+Math.ceil(p.staffing.needed)+' current staff-equivalents':'not yet measured';
 return 'School · '+money(p.cost)+' build'+(p.affordable?' · ':' (over budget) · ')+money(p.afterBuild)+' left · road trip '+(p.siteMeanDistance==null?'no homes':Math.round(p.siteMeanDistance)+' segments avg')+'; '+p.siteBeyondLimit+' residents >'+p.limit+' · new reach +'+p.newlyReachable+' residents · shared places +'+Math.min(260,Math.round(p.incrementalPlaces))+'/260 · education '+money(p.educationBudget)+'/day vs ~'+money(p.reachableNeed)+'/day need · '+current+' · '+p.eligibleLocalStaff+' eligible local staff · '+staff+' · estimate, no service promise';
}
function drawServiceAccess(g){
 if(!['healthAccess','schoolAccess'].includes(overlay))return;g.save();const access=serviceAccess(overlay==='healthAccess'?'health':'school'),byHome=new Map();
 for(const h of access.households){const entry=byHome.get(h.home)||{served:0,residents:0};entry.served+=h.served;entry.residents+=h.residents;byHome.set(h.home,entry);}
 for(const [id,h] of byHome){const b=readBuild(id);if(!b)continue;const p=iso(b.x,b.y);if(Math.abs(p[0]-cam.x)>cw/(2*cam.zoom)+72||Math.abs(p[1]-cam.y)>ch/(2*cam.zoom)+72)continue;g.globalAlpha=.55;diamond(g,b.x,b.y,h.served>=h.residents-1e-6?'#a4d09b':h.served?'#e0c076':'#ce8069');if(cam.zoom>.45){const x=p[0],y=p[1]+21,r=6/cam.zoom;g.globalAlpha=1;g.beginPath();g.arc(x,y,r,0,Math.PI*2);g.fillStyle='#f5f0dc';g.fill();g.strokeStyle='#20382d';g.lineWidth=1.6/cam.zoom;g.stroke();g.font=`bold ${9/cam.zoom}px Arial`;g.textAlign='center';g.textBaseline='middle';g.lineWidth=1/cam.zoom;g.fillStyle='#172d25';g.fillText(h.served>=h.residents-1e-6?'+':h.served>0?'!':'X',x,y+.3/cam.zoom);}}
 g.restore();
}

function householdServiceReport(id){
 return head('Local service access')+['health','school'].map(kind=>{const access=serviceAccess(kind),h=access.households.find(h=>h.id===id),provision=G.serviceProvision?.[kind];if(!h)return '';const effective=provision&&access.coverage?h.served/h.residents*provision.coverage/access.coverage:null;
 return strip(kind==='health'?'Medical access':'School access',h.distance==null?'No facility within road catchment':h.distance+' road segments · '+policyNumber(h.served)+'/'+h.residents+' reachable places')+(effective==null?'':strip('Latest funded coverage',Math.round(effective*100)+'%'));}).join('');
}

function localCivicCoverage(kind,id){
 const access=serviceAccess(kind),h=access.households.find(h=>h.id===id),provision=G.serviceProvision?.[kind];
 return h&&provision&&access.coverage?clamp(h.served/h.residents*provision.coverage/access.coverage,0,1):0;
}
