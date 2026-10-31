// Road catchments and shared facility capacity. No clinic/school can count its
// same places twice when catchments overlap. Derived data is never save authority.
const serviceAccessCaches=new Map();
function serviceAccess(kind){
 const standard=CIVIC_STANDARDS[kind],net=graph(),limit=kind==='health'?60:40;
 const facilities=G.buildings.filter(b=>b.kind===standard.building),homes=G.households.map(h=>({id:h.id,home:h.home,residents:h.people.filter(id=>G.people[id]&&!G.people[id].deceased&&!G.people[id].movedAway).length})).filter(h=>h.residents);
 const key=facilities.map(b=>b.id).join(',')+'|'+homes.map(h=>h.id+':'+h.home+':'+h.residents).join(',');
 const old=serviceAccessCaches.get(kind);if(old&&old.town===G&&old.net===net&&old.key===key)return old.result;
 const totalNodes=facilities.length+homes.length+2,sink=totalNodes-1,edges=Array.from({length:totalNodes},()=>[]),homeEdges=[],distances=[],facilityEdges=[],connections=[];
 const link=(a,b,capacity)=>{const edge={to:b,capacity,reverse:edges[b].length};edges[a].push(edge);edges[b].push({to:a,capacity:0,reverse:edges[a].length-1});return edge;};
 facilities.forEach((facility,i)=>{
  facilityEdges.push(link(0,i+1,standard.capacity));connections.push([]);const port=net.portals.get(facility.id),distance=new Map(),queue=[];
  if(port!=null){distance.set(port,0);queue.push(port);}
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
 const result={kind,limit,served:Math.min(served,G.stats.population),population:G.stats.population,coverage:G.stats.population?Math.min(1,served/G.stats.population):0,households:homes.map((h,j)=>{const port=net.portals.get(h.home),reachable=distances.map(d=>d.get(port)).filter(d=>d!=null);return {...h,served:clamp(h.residents-homeEdges[j].capacity,0,h.residents),distance:reachable.length?Math.min(...reachable):null};})};
 serviceAccessCaches.set(kind,{town:G,net,key,result});return result;
}
function drawServiceAccess(g){
 if(!['healthAccess','schoolAccess'].includes(overlay))return;const access=serviceAccess(overlay==='healthAccess'?'health':'school'),byHome=new Map();
 for(const h of access.households){const entry=byHome.get(h.home)||{served:0,residents:0};entry.served+=h.served;entry.residents+=h.residents;byHome.set(h.home,entry);}
 for(const [id,h] of byHome){const b=readBuild(id);if(!b)continue;const p=iso(b.x,b.y);if(Math.abs(p[0]-cam.x)>cw/(2*cam.zoom)+72||Math.abs(p[1]-cam.y)>ch/(2*cam.zoom)+72)continue;g.globalAlpha=.55;diamond(g,b.x,b.y,h.served>=h.residents-1e-6?'#a4d09b':h.served?'#e0c076':'#ce8069');if(cam.zoom>.65){g.globalAlpha=1;g.font=`bold ${10/cam.zoom}px Arial`;g.textAlign='center';g.fillStyle='#173c2c';g.fillText(h.served>=h.residents-1e-6?'+':h.served>0?'!':'×',p[0],p[1]+21);}}g.globalAlpha=1;
}

function householdServiceReport(id){
 return head('Local service access')+['health','school'].map(kind=>{const access=serviceAccess(kind),h=access.households.find(h=>h.id===id),provision=G.serviceProvision?.[kind];if(!h)return '';const effective=provision&&access.coverage?h.served/h.residents*provision.coverage/access.coverage:null;
 return strip(kind==='health'?'Medical access':'School access',h.distance==null?'No facility within road catchment':h.distance+' road segments · '+policyNumber(h.served)+'/'+h.residents+' reachable places')+(effective==null?'':strip('Latest funded coverage',Math.round(effective*100)+'%'));}).join('');
}

function localCivicCoverage(kind,id){
 const access=serviceAccess(kind),h=access.households.find(h=>h.id===id),provision=G.serviceProvision?.[kind];
 return h&&provision&&access.coverage?clamp(h.served/h.residents*provision.coverage/access.coverage,0,1):0;
}
