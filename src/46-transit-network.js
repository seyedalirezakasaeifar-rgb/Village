// Public buses and elevated metro: authoritative daily capacity; independent visual samples.
const TRANSIT_MODES={bus:{name:'Bus',seats:32,vehicle:6200,tile:0,minutes:1.15,staff:2,upkeep:12,fare:.65},elevated:{name:'Elevated metro',seats:110,vehicle:36000,tile:950,minutes:.42,staff:4,upkeep:40,fare:1.25}};
const TRANSIT_LEVELS=[{name:'Suspended',vehicles:0},{name:'Local',vehicles:1},{name:'Frequent',vehicles:2},{name:'High frequency',vehicles:4}];
const TRANSIT_COLORS=['#f0ad56','#51b9c3','#c385b9','#8abf77','#ef8175','#8ba6e9'];
let transitTopologyCache=null,transitDailyCache=null,transitReservationVersion=0;
function ensureTransit(){if(!G.transit)G.transit={version:1,revision:0,next:1,routes:[],tracks:[],capital:0,fares:0,expenses:0,lastDay:0,daily:{rides:0,denied:0,revenue:0,expenses:0,staff:0}};return G.transit;}
function transitChanged(){ensureTransit().revision++;transitReservationVersion++;for(const p of G.people)p.transitTrip=null;transitTopologyCache=null;transitDailyCache=null;householdMarketCache=null;dirty=true;staticDirty=true;}
function transitStopRoad(mode,id,net=graph()){return mode==='bus'?id:net.portals.get(id);}
function transitOwnedRoad(id){return Number.isInteger(id)&&id>=0&&id<G.tiles.length&&G.tiles[id]===1&&charterOwns(id%T,id/T|0);}
function transitWalkTree(start,limit=5,net=graph()){
 const distances=new Map();if(start==null||!net.neighbors.has(start))return distances;distances.set(start,0);const queue=[start];
 for(let i=0;i<queue.length;i++){const at=queue[i],d=distances.get(at);if(d>=limit)continue;for(const n of net.neighbors.get(at)||[])if(!distances.has(n)){distances.set(n,d+1);queue.push(n);}}
 return distances;
}
function transitRoadPath(a,b,net=graph()){
 if(!transitOwnedRoad(a)||!transitOwnedRoad(b))return [];
 const parent=new Map([[a,-1]]),queue=[a];for(let i=0;i<queue.length;i++){const at=queue[i];if(at===b)break;for(const next of net.neighbors.get(at)||[])if(!parent.has(next)&&transitOwnedRoad(next)){parent.set(next,at);queue.push(next);}}
 if(!parent.has(b))return [];const result=[];for(let at=b;at!==-1;at=parent.get(at))result.push(at);return result.reverse();
}
function transitPaths(mode,stops,net=graph()){
 const legs=[],path=[],offsets=[0];for(let i=1;i<stops.length;i++){const leg=transitRoadPath(transitStopRoad(mode,stops[i-1],net),transitStopRoad(mode,stops[i],net),net);if(leg.length<2)return null;legs.push(leg);path.push(...(i===1?leg:leg.slice(1)));offsets.push(path.length-1);}
 return {legs,path,offsets};
}
// Expansion integration: map tile indices only; institution IDs and stop offsets are stable.
// Pure archive transform: never touches G, caches, tickets, fares or the input.
function remapTransitState(state,mapTile){
 if(state==null)return state;if(typeof mapTile!=='function')throw Error('Transit remapping needs a tile mapper');
 const mapped=JSON.parse(JSON.stringify(state)),tile=id=>{const next=mapTile(id);if(!Number.isSafeInteger(next)||next<0)throw Error('Invalid remapped transit tile');return next;};
 mapped.tracks=mapped.tracks.map(tile);
 for(const r of mapped.routes){r.path=r.path.map(tile);if(r.mode==='bus')r.stops=r.stops.map(tile);}
 return mapped;
}
function remapTransitTiles(mapTile){if(!G.transit)return;const mapped=remapTransitState(G.transit,mapTile);G.transit=mapped;transitChanged();}
function transitRightOfWay(id){return !!G.transit?.tracks.includes(id);}
function removeUnusedGuideway(){
 const state=ensureTransit(),used=new Set(state.routes.filter(r=>r.mode==='elevated').flatMap(r=>r.path)),retired=state.tracks.filter(id=>!used.has(id));if(!retired.length)return false;
 const salvage=Math.min(G.region,retired.length*TRANSIT_MODES.elevated.tile*.15);G.region-=salvage;G.treasury+=salvage;state.tracks=state.tracks.filter(id=>used.has(id));book('Regional material salvagers','Municipal treasury',salvage,'Decommissioned unused elevated guideway');transitChanged();return true;
}
function transitDepotLoad(id,except=-1){return ensureTransit().routes.filter(r=>r.depot===id&&r.id!==except).reduce((n,r)=>n+r.vehicles*(r.mode==='elevated'?2:1),0);}
function transitQuote(spec,editing=-1){
 const state=ensureTransit(),mode=spec?.mode,depot=readBuild(spec?.depot),stops=spec?.stops,level=spec?.level,definition=TRANSIT_MODES[mode];
 if(!definition||!depot||depot.kind!=='transit_depot'||!Array.isArray(stops)||stops.length<2||stops.length>16||new Set(stops).size!==stops.length||!Number.isInteger(level)||level<1||level>3)return {ok:false,reason:'Choose a depot, service level and 2–16 distinct stops.'};
 if(state.routes.length>=48&&editing<0)return {ok:false,reason:'Network limit: 48 routes. Extend or replace existing corridors.'};
 if(stops.some(id=>mode==='bus'?!transitOwnedRoad(id):readBuild(id)?.kind!=='elevated_station'))return {ok:false,reason:'Bus stops need owned streets; elevated stops need completed elevated stations.'};
 const vehicles=TRANSIT_LEVELS[level].vehicles;if(transitDepotLoad(depot.id,editing)+vehicles*(mode==='elevated'?2:1)>8)return {ok:false,reason:'Depot has eight vehicle bays; each metro set needs two. Build another depot or lower service.'};
 const net=graph(),route=transitPaths(mode,stops,net),port=net.portals.get(depot.id),first=transitStopRoad(mode,stops[0],net);
 if(!route||!transitRoadPath(port,first,net).length)return {ok:false,reason:'All stops and the depot must connect through owned streets. Water and private plots cannot be crossed.'};
 const existing=state.routes.find(r=>r.id===editing),newVehicles=Math.max(0,vehicles-(existing?.vehicles||0)),newTrack=mode==='elevated'?[...new Set(route.path)].filter(id=>!state.tracks.includes(id)):[];
 if(existing&&existing.mode!==mode)return {ok:false,reason:'Retire the old route before changing transport mode.'};
 const cost=newVehicles*definition.vehicle+newTrack.length*definition.tile+(editing<0?900:0),cycle=2*(route.path.length-1)*definition.minutes+stops.length*2;
 const operating=vehicles*definition.staff*Math.max(24,G.policy.minWage)+vehicles*definition.upkeep+route.path.length*(mode==='bus'?.11:.28);
 const token=[state.revision,roadsVersion,G.policy.minWage,mode,depot.id,stops.join(','),level,editing,cost].join('|');
 return {ok:true,mode,depot:depot.id,stops:stops.slice(),level,vehicles,path:route.path,offsets:route.offsets,newTrack,cost,cycle,headway:cycle/vehicles,capacity:Math.floor(vehicles*definition.seats*120/cycle),operating,token};
}
function buildTransitRoute(spec,quote,editing=-1){
 const current=transitQuote(spec,editing);if(!current.ok||!quote||quote.token!==current.token||G.treasury<current.cost)return false;
 const state=ensureTransit(),existing=state.routes.find(r=>r.id===editing);if(editing>=0&&!existing)return false;
 G.treasury-=current.cost;G.region+=current.cost;G.cumulative.spending+=current.cost;state.capital+=current.cost;book('Municipal transit capital','Regional vehicle and guideway suppliers',current.cost,'Public '+TRANSIT_MODES[spec.mode].name+' route');
 const id=existing?.id||state.next++,route={id,name:existing?.name||TRANSIT_MODES[spec.mode].name+' '+id,mode:spec.mode,depot:spec.depot,stops:spec.stops.slice(),level:spec.level,vehicles:current.vehicles,path:current.path,offsets:current.offsets,color:existing?.color||TRANSIT_COLORS[(id-1)%TRANSIT_COLORS.length],built:existing?.built||G.day,capital:(existing?.capital||0)+current.cost,stats:{operating:false,capacity:0,reserved:0,boardings:0,demand:0,denied:0,staff:[],required:0,headway:0,reliability:0,expenses:0,status:'Service begins next day'}};
 if(existing){const salvage=Math.min(G.region,Math.max(0,existing.vehicles-current.vehicles)*TRANSIT_MODES[existing.mode].vehicle*.4);G.region-=salvage;G.treasury+=salvage;book('Regional used vehicle buyers','Municipal treasury',salvage,'Route fleet resized',existing.id);state.routes[state.routes.indexOf(existing)]=route;}else state.routes.push(route);
 state.tracks=[...new Set(state.tracks.concat(current.newTrack))];transitChanged();return route;
}
function setTransitLevel(id,level){const r=ensureTransit().routes.find(r=>r.id===id);if(!r||!Number.isInteger(level)||level<0||level>3)return false;if(level===r.level)return false;if(level===0){r.level=0;r.stats.operating=false;r.stats.status='Suspended by council';transitChanged();return true;}const q=transitQuote({...r,level},id);return q.ok&&!!buildTransitRoute({...r,level},q,id);}
function deleteTransitRoute(id){
 const state=ensureTransit(),route=state.routes.find(r=>r.id===id);if(!route)return false;
 const refund=Math.min(G.region,route.vehicles*TRANSIT_MODES[route.mode].vehicle*.4);G.region-=refund;G.treasury+=refund;state.routes=state.routes.filter(r=>r!==route);book('Regional used vehicle buyers','Municipal treasury',refund,'Retired route vehicle resale',id);transitChanged();return true;
}
function buildTransitFacility(kind,x,y){
 if(!['transit_depot','elevated_station'].includes(kind)||!Number.isInteger(x)||!Number.isInteger(y)||!canPlace(x,y,true,kind)||G.treasury<buildCost[kind])return false;
 const cost=buildCost[kind],b={id:G.nextId++,kind,x,y,value:cost,condition:100,owner:-1,firm:-1,hh:-1,title:{kind:'municipal',id:-1},footprint:footprintFor(x,y,kind)};
 G.treasury-=cost;G.region+=cost;G.cumulative.spending+=cost;G.buildings.push(b);reserveFootprint(b);G.construction++;ensureTransit().capital+=cost;transitChanged();return b;
}
function transitInfrastructureInUse(id){return !!G.transit?.routes.some(r=>r.depot===id||r.mode==='elevated'&&r.stops.includes(id));}
function removeTransitFacility(id){
 const b=readBuild(id),state=ensureTransit();if(!b||!['transit_depot','elevated_station'].includes(b.kind)||transitInfrastructureInUse(id))return false;
 const refund=Math.min(G.region,buildCost[b.kind]*.15);G.region-=refund;G.treasury+=refund;G.buildings=G.buildings.filter(a=>a!==b);invalidateBuildingIndex();invalidateRoads(false);transitChanged();return true;
}
function transitTopology(){
 const state=ensureTransit(),net=graph();if(transitTopologyCache?.town===G&&transitTopologyCache.net===net&&transitTopologyCache.revision===state.revision)return transitTopologyCache;
 const routes=[],walks=new Map();for(const r of state.routes){const route=r.mode==='elevated'?{path:r.path,offsets:r.offsets}:transitPaths(r.mode,r.stops,net),depotPort=net.portals.get(r.depot),start=transitStopRoad(r.mode,r.stops[0],net);
  const valid=!!route&&!!readBuild(r.depot)&&route.path.every(transitOwnedRoad)&&(r.mode!=='elevated'||r.stops.every((id,i)=>route.path[route.offsets[i]]===transitStopRoad(r.mode,id,net)))&&r.stops.every(id=>r.mode==='bus'||readBuild(id)?.kind==='elevated_station')&&net.parts[depotPort]>=0&&net.parts[depotPort]===net.parts[start];
  const runtime={...r,...(route||{}),valid,stopRoads:r.stops.map(id=>transitStopRoad(r.mode,id,net))};routes.push(runtime);
  for(const stop of runtime.stopRoads)if(!walks.has(stop))walks.set(stop,transitWalkTree(stop,5,net));
 }
 return transitTopologyCache={town:G,net,revision:state.revision,routes,walks,records:new Map(state.routes.map(r=>[r.id,r])),depotWalks:new Map()};
}
// Heap keeps many-household routing bounded; no shortest-path work occurs per frame.
function transitHeapPush(heap,value){heap.push(value);let i=heap.length-1;while(i){const p=(i-1)>>1;if(heap[p][0]<=value[0])break;heap[i]=heap[p];i=p;}heap[i]=value;}
function transitHeapPop(heap){const first=heap[0],last=heap.pop();if(heap.length){let i=0;while(i*2+1<heap.length){let j=i*2+1;if(j+1<heap.length&&heap[j+1][0]<heap[j][0])j++;if(heap[j][0]>=last[0])break;heap[i]=heap[j];i=j;}heap[i]=last;}return first;}
function transitRouting(){
 const topology=transitTopology(),state=ensureTransit();
 if(transitDailyCache?.town===G&&transitDailyCache.topology===topology&&transitDailyCache.service===state.lastDay)return transitDailyCache;
 const signature=topology.routes.map(r=>r.valid&&r.stats?.operating?r.id+':'+r.stats.headway:'').join('|');
 // Geometry and timetable determine routing costs. Day, fares and ridership do not.
 if(transitDailyCache?.town===G&&transitDailyCache.topology===topology&&transitDailyCache.signature===signature){transitDailyCache.service=state.lastDay;return transitDailyCache;}
 const nodes=[],edges=[],roadNodes=new Map(),access=new Map(),patterns=new Map();for(const route of topology.routes){if(!route.valid||!route.stats?.operating)continue;const base=nodes.length,patternKey=route.mode+'|'+route.stopRoads.join(',')+'|'+route.offsets.join(',');if(!patterns.has(patternKey))patterns.set(patternKey,patterns.size);const pattern=patterns.get(patternKey);
  for(let i=0;i<route.stops.length;i++){const road=route.stopRoads[i],id=nodes.length;nodes.push({route:route.id,index:i,road,pattern,headway:route.stats.headway,mode:route.mode});edges.push([]);if(!roadNodes.has(road))roadNodes.set(road,[]);roadNodes.get(road).push(id);
   for(const [walkRoad,distance] of topology.walks.get(road)||[]){if(!access.has(walkRoad))access.set(walkRoad,[]);access.get(walkRoad).push([id,distance]);}
   if(i){const time=(route.offsets[i]-route.offsets[i-1])*TRANSIT_MODES[route.mode].minutes+1;edges[id-1].push([id,time]);edges[id].push([id-1,time]);}}
  route.nodeBase=base;
 }
 // A same-stop switch between identical ride patterns adds a wait without a new destination.
 // Keep cross-stop walks/transfers: these can bridge a real shortcut or another corridor.
 for(let i=0;i<nodes.length;i++){const a=nodes[i];for(const [road,distance] of topology.walks.get(a.road)||[])if(distance<=3)for(const j of roadNodes.get(road)||[])if(nodes[j].route!==a.route&&(nodes[j].pattern!==a.pattern||nodes[j].index!==a.index))edges[i].push([j,distance*2+nodes[j].headway/2+2]);}
 return transitDailyCache={town:G,topology,signature,service:state.lastDay,nodes,edges,access,homes:new Map(),journeys:new Map(),capacity:new Map()};
}
function transitCapacityMask(routing,units){
 if(!units)return {blocked:new Set(),key:''};
 let cached=routing.capacity.get(units);if((units===1||units===2)&&cached?.version===transitReservationVersion)return cached;
 const blocked=new Set(ensureTransit().routes.filter(r=>r.stats.reserved+units>r.stats.capacity).map(r=>r.id));
 cached={blocked,key:[...blocked].join(','),version:transitReservationVersion};routing.capacity.set(units,cached);return cached;
}
function transitJourney(home,destination,capacityUnits=0){
 if(!home||!destination||!G.transit?.routes.length)return null;const routing=transitRouting(),net=routing.topology.net,origin=net.portals.get(home.id),goal=net.portals.get(destination.id);if(origin==null||goal==null||origin===goal||!routing.nodes.length)return null;
 const {blocked,key}=transitCapacityMask(routing,capacityUnits),treeKey=origin+'|'+key,tripKey=origin+'>'+goal+'|'+key,copy=trip=>trip?{...trip,routes:trip.routes.slice()}:null;
 const cached=routing.journeys.get(tripKey);if(cached!==undefined)return copy(cached);
 const finish=trip=>{if(routing.journeys.size>=4096)routing.journeys.delete(routing.journeys.keys().next().value);routing.journeys.set(tripKey,trip);return copy(trip);};
 let tree=routing.homes.get(treeKey);if(!tree){const count=routing.nodes.length,distance=new Array(count).fill(Infinity),parent=new Array(count).fill(-1),heap=[];
  for(const [i,walk] of routing.access.get(origin)||[]){const node=routing.nodes[i];if(!blocked.has(node.route)){distance[i]=walk*2+node.headway/2;transitHeapPush(heap,[distance[i],i]);}}
  while(heap.length){const [cost,i]=transitHeapPop(heap);if(cost!==distance[i])continue;for(const [j,time] of routing.edges[i])if(!blocked.has(routing.nodes[j].route)&&cost+time<distance[j]){distance[j]=cost+time;parent[j]=i;transitHeapPush(heap,[distance[j],j]);}}
  tree={distance,parent};if(routing.homes.size>=512)routing.homes.delete(routing.homes.keys().next().value);routing.homes.set(treeKey,tree);
 }
 let best=-1,time=Infinity;for(const [i,walk] of routing.access.get(goal)||[]){const node=routing.nodes[i];if(!blocked.has(node.route)&&tree.distance[i]+walk*2<time){best=i;time=tree.distance[i]+walk*2;}}
 if(best<0)return finish(null);const chain=[];for(let at=best;at>=0;at=tree.parent[at])chain.push(at);chain.reverse();
 // Cache immutable route templates. Paid tickets always receive their own object/route list.
 const routeIds=[];for(let i=1;i<chain.length;i++)if(routing.nodes[chain[i]].route===routing.nodes[chain[i-1]].route){const id=routing.nodes[chain[i]].route;if(!routeIds.includes(id))routeIds.push(id);}
 if(!routeIds.length||routeIds.length>3)return finish(null);
 return finish({routes:routeIds,time,fare:Math.max(...routeIds.map(id=>TRANSIT_MODES[routing.topology.records.get(id).mode].fare)),transfers:routeIds.length-1});
}
function transitAccess(home,destination){const journey=transitJourney(home,destination);return !!journey&&journey.time<=90;}
function transitReserve(journey,units=1){
 if(!journey)return false;const records=transitTopology().records,routes=journey.routes.map(id=>records.get(id));if(routes.some(r=>!r?.stats.operating||r.stats.reserved+units>r.stats.capacity))return false;
 for(const r of routes){const before=r.stats.capacity-r.stats.reserved;r.stats.reserved+=units;const after=before-units;if(before>=2&&after<2||before>=1&&after<1)transitReservationVersion++;}return true;
}
function transitDemand(journey,denied=false,units=1){if(!journey)return;for(const id of journey.routes){const s=transitTopology().records.get(id)?.stats;if(s){s.demand+=units;if(denied)s.denied+=units;}}}
function transitCollectFare(h,journey,units=1){
 if(journey.settled)return 0;journey.settled=true;
 const due=journey.fare*units,paid=Math.min(h.cash,due);h.cash-=paid;h.travel+=paid;h.travelDue+=due;G.treasury+=paid;const state=ensureTransit();state.fares+=paid;state.daily.revenue+=paid;state.daily.rides+=units;
 for(const id of journey.routes){const s=transitTopology().records.get(id)?.stats;if(s)s.boardings+=units;}return paid;
}
function transitOperatingCommitment(){return (G.transit?.routes.length?transitTopology().routes:[]).reduce((sum,r)=>{if(!r.level)return sum;const d=TRANSIT_MODES[r.mode],vehicles=TRANSIT_LEVELS[r.level].vehicles;return sum+vehicles*d.staff*Math.max(24,G.policy.minWage)+vehicles*d.upkeep+r.path.length*(r.mode==='bus'?.11:.28);},0);}
function transitOperatingDay(){
 const state=ensureTransit();if(state.lastDay===G.day)return;state.lastDay=G.day;state.daily={rides:0,denied:0,revenue:0,expenses:0,staff:0};
 const topology=transitTopology(),driverPool=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.age>=18&&p.age<=70&&p.job<0&&!p.publicWork&&!(p.publicIncome>0)&&(!p.previousPublicRole||p.previousPublicRole==='transit')&&p.skill>=.3).sort((a,b)=>(a.previousPublicRole==='transit'?0:1)-(b.previousPublicRole==='transit'?0:1)||a.id-b.id);
 for(const route of topology.routes){const r=topology.records.get(route.id),definition=TRANSIT_MODES[r.mode],required=r.level?TRANSIT_LEVELS[r.level].vehicles*definition.staff:0;
  const previous=r.stats;r.stats={operating:false,capacity:0,reserved:0,boardings:0,demand:0,denied:0,staff:[],required,status:!r.level?'Suspended by council':!route.valid?'Street, station or depot disconnected':'Insufficient budget or drivers',headway:0,reliability:0,expenses:0,lastDemand:previous?.demand||0,lastDenied:previous?.denied||0};route.stats=r.stats;
  if(!required||!route.valid)continue;
  const depotPort=topology.net.portals.get(r.depot),wage=Math.max(24,G.policy.minWage),vehicles=TRANSIT_LEVELS[r.level].vehicles;
  let local=topology.depotWalks.get(r.depot);if(!local){local=transitWalkTree(depotPort,60,topology.net);topology.depotWalks.set(r.depot,local);}
  const candidates=[];for(const p of driverPool){if(!p.publicWork&&local.has(topology.net.portals.get(G.households[p.hh]?.home)))candidates.push(p);if(candidates.length>=required)break;}
  const maintenance=vehicles*definition.upkeep+route.path.length*(r.mode==='bus'?.11:.28),staff=Math.min(required,candidates.length,Math.max(0,Math.floor((G.treasury-maintenance)/wage)));
  if(staff<definition.staff)continue;const actualVehicles=Math.min(vehicles,Math.floor(staff/definition.staff)),actualStaff=actualVehicles*definition.staff,cost=actualStaff*wage+maintenance;
  G.treasury-=cost;G.cumulative.spending+=cost;G.region+=maintenance;
  for(const p of candidates.slice(0,actualStaff)){const h=G.households[p.hh],tax=wage*G.policy.incomeTax/100;h.cash+=wage-tax;h.income+=wage;h.wages+=wage;h.tax+=tax;h.incomeTax+=tax;transferTreasury(tax,'incomeTax');p.publicWork=true;p.publicIncome=wage;p.publicRole='transit';r.stats.staff.push(p.id);}
  let reliability=1;if(r.mode==='bus'){const wear=route.path.reduce((sum,id)=>sum+(G.roadWear?.[id]??100),0)/route.path.length;reliability=clamp(.65+wear*.0035,.65,1);}
  const cycle=2*(route.path.length-1)*definition.minutes+r.stops.length*2;r.stats.operating=true;r.stats.reliability=reliability;r.stats.headway=cycle/actualVehicles/reliability;r.stats.capacity=Math.floor(actualVehicles*definition.seats*120/cycle*reliability);r.stats.expenses=cost;r.stats.status=actualVehicles<vehicles?'Reduced: driver or budget shortage':'Operating';state.daily.expenses+=cost;state.daily.staff+=actualStaff;state.expenses+=cost;
 }
 transitReservationVersion++;
 // Deterministic daily allocation rotates priority, rather than giving low IDs perpetual first access.
 const commuters=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.job>=0),offset=commuters.length?G.day%commuters.length:0;
 for(const p of commuters)p.transitTrip=null;
 if(!topology.routes.some(r=>r.valid&&r.stats.operating))return;
 for(const p of commuters.slice(offset).concat(commuters.slice(0,offset))){const h=G.households[p.hh],home=readBuild(h?.home),work=readBuild(G.firms[p.job]?.building);if(!home||!work)continue;
  const distance=roadDistance(topology.net.portals.get(home.id),topology.net.portals.get(work.id));if(distance<8)continue;const journey=transitJourney(home,work);if(!journey||journey.time>90||journey.time>=distance*2)continue;
  if(h.cash<journey.fare)continue;let chosen=journey,boarded=transitReserve(chosen);if(!boarded){const alternative=transitJourney(home,work,1);if(alternative&&alternative.time<=90&&alternative.time<distance*2&&h.cash>=alternative.fare){chosen=alternative;boarded=transitReserve(chosen);}}transitDemand(chosen);if(boarded){p.transitTrip={...chosen,day:G.day};transitCollectFare(h,p.transitTrip);}else{state.daily.denied++;for(const id of journey.routes){const s=topology.records.get(id).stats;s.denied++;}}
 }
}
function transitRenderSnapshot(){const state=ensureTransit(),topology=transitTopology();return {revision:state.revision,routes:topology.routes.map(r=>({id:r.id,name:r.name,mode:r.mode,color:r.color,path:r.path,stops:r.stops,valid:r.valid,...r.stats})),stations:G.buildings.filter(b=>b.kind==='elevated_station').map(b=>({id:b.id,x:b.x,y:b.y,kind:b.kind})),depots:G.buildings.filter(b=>b.kind==='transit_depot').map(b=>({id:b.id,x:b.x,y:b.y,kind:b.kind}))};}
function transitVehiclePoses(time=frameClock,zoom=cam.zoom){
 if(zoom<.38||!G.transit?.routes.length)return [];const result=[];for(const r of transitTopology().routes){if(!r.valid||!r.stats?.operating||!r.path?.length)continue;const count=Math.min(4,r.stats.staff.length/TRANSIT_MODES[r.mode].staff),span=r.path.length-1;
  for(let i=0;i<count;i++){const phase=(time*(r.mode==='bus'?.48:.85)+i*span*2/count)%(span*2),forward=phase<span,position=forward?phase:span*2-phase,segment=Math.min(span-1,Math.floor(position)),fraction=position-segment,a=roadCenter(r.path[segment]),b=roadCenter(r.path[segment+1]),elevation=r.mode==='elevated'?28:0;result.push({kind:'transit',mode:r.mode,route:r.id,color:r.color,x:a[0]+(b[0]-a[0])*fraction,y:a[1]+(b[1]-a[1])*fraction-elevation,dx:(b[0]-a[0])*(forward?1:-1),dy:(b[1]-a[1])*(forward?1:-1),elevation,load:r.stats.boardings/Math.max(1,r.stats.capacity)});}
 }return result;
}
function validateTransit(data){
 const s=data.transit;if(s==null)return true;const finite=n=>Number.isFinite(n)&&n>=0,integer=n=>Number.isSafeInteger(n)&&n>=0,cell=n=>integer(n)&&n<data.tiles.length;
 if(!s||s.version!==1||!integer(s.revision)||!integer(s.next)||s.next<1||!Array.isArray(s.routes)||s.routes.length>48||!Array.isArray(s.tracks)||s.tracks.length>data.tiles.length||new Set(s.tracks).size!==s.tracks.length||!s.tracks.every(cell)||!['capital','fares','expenses'].every(k=>finite(s[k]))||!integer(s.lastDay)||s.lastDay>data.day)return false;
 const ids=new Set(),builds=new Map(data.buildings.map(b=>[b.id,b])),loads=new Map(),staff=new Set();
 for(const r of s.routes){if(!r||!integer(r.id)||r.id<1||r.id>=s.next||ids.has(r.id)||!owns(TRANSIT_MODES,r.mode)||builds.get(r.depot)?.kind!=='transit_depot'||typeof r.name!=='string'||r.name.length>80||!TRANSIT_COLORS.includes(r.color)||!integer(r.level)||r.level>3||![1,2,4].includes(r.vehicles)||r.level>0&&r.vehicles!==TRANSIT_LEVELS[r.level].vehicles||!finite(r.capital)||!integer(r.built)||r.built>data.day)return false;ids.add(r.id);
  if(!Array.isArray(r.stops)||r.stops.length<2||r.stops.length>16||new Set(r.stops).size!==r.stops.length||r.stops.some(id=>r.mode==='bus'?!cell(id):builds.get(id)?.kind!=='elevated_station'))return false;
  if(!Array.isArray(r.path)||r.path.length<2||r.path.length>data.tiles.length*16||!r.path.every(cell)||r.path.some((id,i)=>i&&Math.abs(id%T-r.path[i-1]%T)+Math.abs((id/T|0)-(r.path[i-1]/T|0))!==1)||!Array.isArray(r.offsets)||r.offsets.length!==r.stops.length||r.offsets[0]!==0||fromEnd(r.offsets)!==r.path.length-1||r.offsets.some((v,i)=>!integer(v)||v>=r.path.length||i&&v<=r.offsets[i-1]))return false;
  if(r.mode==='elevated'&&r.path.some(id=>!s.tracks.includes(id)))return false;
  const st=r.stats;if(!st||typeof st.status!=='string'||st.status.length>128||typeof st.operating!=='boolean'||!['capacity','reserved','boardings','demand','denied','required','headway','reliability','expenses'].every(k=>finite(st[k]??0))||!Array.isArray(st.staff||[])||new Set(st.staff||[]).size!==(st.staff||[]).length||(st.staff||[]).some(id=>!integer(id)||!data.people[id]||staff.has(id))||st.reliability>1||['capacity','reserved','boardings','demand','denied','required'].some(k=>!integer(st[k]))||st.capacity<st.reserved||st.capacity<st.boardings||st.staff.length>16||st.operating&&(!r.level||st.staff.length<TRANSIT_MODES[r.mode].staff||!st.capacity||!st.headway))return false;
  for(const id of st.staff||[])staff.add(id);loads.set(r.depot,(loads.get(r.depot)||0)+r.vehicles*(r.mode==='elevated'?2:1));
 }
 for(const p of data.people){const trip=p.transitTrip;if(trip==null)continue;if(!trip||!integer(trip.day)||trip.day<1||trip.day>data.day||!finite(trip.time)||trip.time>90||![.65,1.25].includes(trip.fare)||!Array.isArray(trip.routes)||!trip.routes.length||trip.routes.length>3||new Set(trip.routes).size!==trip.routes.length||trip.routes.some(id=>!ids.has(id))||trip.transfers!==trip.routes.length-1||trip.settled!==true)return false;}
 if([...loads.values()].some(n=>n>8)||!s.daily||!['rides','denied','revenue','expenses','staff'].every(k=>finite(s.daily[k])))return false;
 return true;
}
