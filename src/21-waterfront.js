// Water has physical catchments and outlets. Cargo title passes to the regional
// buyer on collection; manifests describe that buyer's paid journey, not town stock.
let waterNetworkTown=null,waterNetworkRoads=null,waterNetworkCache=null,waterDayTown=null,waterDayNumber=-1,operatingWharves=[];
function waterNetwork(){
 const roads=graph();if(waterNetworkTown===G&&waterNetworkRoads===roads)return waterNetworkCache;
 const nodes=new Set(),parts=new Int32Array(T*T).fill(-1),components=[],toGateway=new Int32Array(T*T).fill(-1);
 for(let id=0;id<T*T;id++){const x=id%T,y=id/T|0;
  // A road across the natural river is a bridge, not an artificial dam.
  if(G.tiles[id]===2||G.tiles[id]===1&&(x<5+Math.sin(y*.2)*1.7||x===5&&y%4===0))nodes.add(id);
 }
 const adjacent=id=>{const x=id%T,y=id/T|0;return roadOffsets.map(([dx,dy])=>[x+dx,y+dy]).filter(([x,y])=>x>=0&&y>=0&&x<T&&y<T).map(([x,y])=>y*T+x).filter(n=>nodes.has(n));};
 for(const start of nodes){if(parts[start]>=0)continue;const index=components.length,cells=[start],gates=[];parts[start]=index;
  for(let i=0;i<cells.length;i++){const at=cells[i],x=at%T,y=at/T|0;if(y===0||y===T-1)gates.push(at);for(const n of adjacent(at))if(parts[n]<0){parts[n]=index;cells.push(n);}}
  components.push({id:index,cells,gates,catchCapacity:cells.length*1.2});
  const queue=gates.slice();for(const gate of gates)toGateway[gate]=gate;
  for(let i=0;i<queue.length;i++)for(const n of adjacent(queue[i]))if(toGateway[n]<0){toGateway[n]=queue[i];queue.push(n);}
 }
 waterNetworkTown=G;waterNetworkRoads=roads;waterNetworkCache={nodes,parts,components,toGateway,adjacent};waterDayTown=null;return waterNetworkCache;
}
function waterfrontSite(x,y,kind='fishery'){
 const water=waterNetwork(),choices=[];
 for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const xx=x+dx,yy=y+dy;if(xx<0||yy<0||xx>=T||yy>=T)continue;const id=roadId(xx,yy),part=water.parts[id],area=water.components[part];if(area&&area.cells.length>=8&&(kind!=='wharf'||area.gates.length))choices.push({id,part,distance:Math.abs(dx)+Math.abs(dy)});}
 choices.sort((a,b)=>a.distance-b.distance||a.id-b.id);return choices[0]||null;
}
function waterOutletPath(start){const w=waterNetwork(),path=[];let at=start;for(let i=0;i<T*T&&at>=0;i++){path.push(at);const next=w.toGateway[at];if(next===at)return path;at=next;}return [];}
function ensureWaterfront(){
 if(!G.waterway)G.waterway={version:1,serial:0,manifests:[],exports:0,fees:0};
 return G.waterway;
}
function prepareWaterfrontDay(live=G.firms.filter(f=>!f.closed)){
 const network=waterNetwork(),state=ensureWaterfront();if(waterDayTown===G&&waterDayNumber===G.day)return;
 waterDayTown=G;waterDayNumber=G.day;operatingWharves=[];state.manifests=state.manifests.filter(m=>m.started+m.duration>=G.day);state.todayCargo=0;state.todayFees=0;
 for(const f of G.firms){if(f.kind==='wharf'){f.cargoToday=0;f.handlingFees=0;f.cargoCapacity=0;}if(f.kind==='fishery'){f.fishingAllowance=0;f.fishingWaterLimit=false;}}
 const groups=new Map();for(const f of live){f.shippingToday=0;if(f.kind==='fishery'){f.fishingAllowance=0;const b=readBuild(f.building),site=b&&waterfrontSite(b.x,b.y);f.waterPart=site?.part??-1;
   if(site&&workingStaff(f).length){const capacity=formulas.fishery.qty*workingStaff(f).length/SECTOR_WORKERS.fishery*(.82+workingStaff(f).reduce((n,id)=>n+(G.people[id]?.skill||.5),0)/workingStaff(f).length*.25+G.education*.0015)*(1+(f.scale-1)*.25);if(!groups.has(site.part))groups.set(site.part,[]);groups.get(site.part).push({f,capacity});}
  }else if(f.kind==='wharf'){f.cargoToday=0;f.handlingFees=0;const b=readBuild(f.building),site=b&&waterfrontSite(b.x,b.y,'wharf'),path=site?waterOutletPath(site.id):[];const capacity=workingStaff(f).length*600*(1+((f.scale||1)-1)*.25);f.cargoCapacity=capacity;
   if(path.length&&capacity>0)operatingWharves.push({f,b,site,path,remaining:capacity});
  }
 }
 for(const [part,list] of groups){const available=network.components[part].catchCapacity,total=list.reduce((n,v)=>n+v.capacity,0);for(const {f,capacity} of list){f.fishingAllowance=capacity*Math.min(1,available/Math.max(1,total));f.fishingWaterLimit=total>available;}}
}
function roadExportDistance(f){const net=graph(),from=net.portals.get(f.building);if(from==null||net.parts[from]!==net.mainPart)return Infinity;
 // The original eastern High Street border is the regional haulage interchange.
 let gate=roadId(49,27);if(!net.neighbors.has(gate)||net.parts[gate]!==net.mainPart)gate=[...net.neighbors.keys()].find(id=>net.parts[id]===net.mainPart);return gate==null?Infinity:roadDistance(from,gate);
}
function exportRoutes(f){
 if(waterDayTown!==G||waterDayNumber!==G.day)prepareWaterfrontDay();
 const net=graph(),port=net.portals.get(f.building),distance=roadExportDistance(f),routes=[];
 if(Number.isFinite(distance))routes.push({mode:'road',unit:.08+distance*.004,capacity:Infinity});
 if(port!=null)for(const wharf of operatingWharves){if(wharf.remaining<=0||wharf.f.closed||!workingStaff(wharf.f).length)continue;const wp=net.portals.get(wharf.b.id);if(wp==null||net.parts[port]!==net.parts[wp])continue;const lastMile=roadDistance(port,wp);if(!Number.isFinite(lastMile))continue;
  routes.push({mode:'river',unit:.10+lastMile*.001+wharf.path.length*.0005,capacity:wharf.remaining,wharf,lastMile});
 }
 return routes.sort((a,b)=>a.unit-b.unit||(a.wharf?.f.id??-1)-(b.wharf?.f.id??-1));
}
function settleRegionalExport(f,good,requested,price){
 let remaining=requested,sold=0;const state=ensureWaterfront();
 for(const route of exportRoutes(f)){const quantity=Math.max(0,Math.min(remaining,route.capacity,G.region/Math.max(price,.01)));if(quantity<=0||route.unit>=price)continue;
  const gross=quantity*price,freight=quantity*route.unit;takeInventory(f,good,quantity,true);goodsEntry(good,'exports',quantity);G.region-=gross;f.cash+=gross;f.revenue+=gross;if(G.market)G.market.externalSales+=gross;
  // The carrier is paid from the actual sale. Handling income belongs to the
  // wharf; the regional haulier receives only the residual, once.
  f.cash-=freight;f.expenses+=freight;f.shippingToday=(f.shippingToday||0)+freight;G.cumulative.freight=(G.cumulative.freight||0)+freight;
  if(route.mode==='river'){const w=route.wharf,handling=quantity*.10;enterpriseRevenue(w.f,handling);G.region+=freight-handling;w.remaining-=quantity;w.f.cargoToday+=quantity;w.f.handlingFees+=handling;state.todayCargo+=quantity;state.todayFees+=handling;state.exports+=quantity;state.fees+=handling;
   const last=state.manifests.find(m=>m.started===G.day&&m.port===w.f.id&&m.good===good);if(last)last.qty+=quantity;else{state.serial++;state.manifests.push({id:state.serial,port:w.f.id,good,qty:quantity,path:w.path.slice(),started:G.day,duration:Math.max(2,Math.ceil(w.path.length/8)),ownership:'regional'});if(state.manifests.length>48)state.manifests.shift();}
  }else G.region+=freight;
  remaining-=quantity;sold+=quantity;if(remaining<.00001)break;
 }
 return sold;
}
function waterfrontDemand(){const active=G.firms.filter(f=>f.kind==='wharf'&&!f.closed);return active.length?0:Math.min(80,G.stats.population/5);}
function initializeWaterfrontStart(){
 // New settlements inherit a paid, privately capitalised landing. Existing
 // archives are never given free firms, roads or title changes during migration.
 for(let x=5;x<=8;x++){const id=roadId(x,27);if(!buildingAt(x,27)){G.tiles[id]=1;G.roadClasses[id]='local';G.streetNames[id]='Landing Lane';}}
 const side=roadId(5,26);if(!buildingAt(5,26)&&G.tiles[side]!==2){G.tiles[side]=1;G.roadClasses[side]='local';G.streetNames[side]='Landing Lane';}invalidateRoads();
 for(const [kind,x,y] of [['fishery',4,27],['wharf',4,26]]){if(!canPlace(x,y,true,kind)||G.region<25000)continue;const f=createFirm(kind,x,y);if(!f)continue;G.region-=f.cash;privateContract(types[kind].cost);f.name=kind==='fishery'?'Vale Net & Line':'Vale River Landing';f.owner=G.households.length?0:-1;}
 assignJobs();ensureWaterfront();
}
function validateWaterfrontArchive(data){
 const w=data.waterway;if(w==null)return true;if(w.version!==1||['todayCargo','todayFees'].some(k=>w[k]!=null&&(!Number.isFinite(w[k])||w[k]<0))||!Number.isSafeInteger(w.serial)||w.serial<0||!Array.isArray(w.manifests)||w.manifests.length>48||!Number.isFinite(w.exports)||w.exports<0||!Number.isFinite(w.fees)||w.fees<0)return false;
 const ids=new Set();return w.manifests.every(m=>{if(!m||!Number.isInteger(m.id)||m.id<1||m.id>w.serial||ids.has(m.id)||!Number.isInteger(m.port)||data.firms[m.port]?.kind!=='wharf'||!owns(goods,m.good)||!Number.isFinite(m.qty)||m.qty<=0||m.ownership!=='regional'||!Number.isInteger(m.started)||m.started<1||m.started>data.day||!Number.isInteger(m.duration)||m.duration<1||m.duration>T*T||!Array.isArray(m.path)||m.path.length<1||m.path.length>T*T)return false;ids.add(m.id);const b=data.buildings.find(b=>b.id===data.firms[m.port].building),start=m.path[0],end=m.path[m.path.length-1];if(!b||Math.abs(start%T-b.x)>1||Math.abs((start/T|0)-b.y)>1||![0,T-1].includes(end/T|0))return false;
  return m.path.every((id,i)=>Number.isInteger(id)&&id>=0&&id<T*T&&(data.tiles[id]===2||data.tiles[id]===1&&(id%T<5+Math.sin((id/T|0)*.2)*1.7||id%T===5&&(id/T|0)%4===0))&&(!i||Math.abs(id%T-m.path[i-1]%T)+Math.abs((id/T|0)-(m.path[i-1]/T|0))===1));});
}
function waterfrontFirmReport(f){
 if(f.kind==='fishery'){const b=readBuild(f.building),site=waterfrontSite(b.x,b.y),area=site&&waterNetwork().components[site.part];return head('Working water')+strip('Fishing water',area?(area.gates.length?'Connected river':'Inland lake')+' · '+area.cells.length+' water tiles':'No usable fishing water')+strip('Catch today',policyNumber(f.production||0)+' food units')+strip('Shared daily catch limit',area?policyNumber(area.catchCapacity):'0')+tip('Crews land food for the existing grocery and regional markets. Fisheries sharing water share its finite catch capacity; extra equipment cannot create fish.');}
 if(f.kind==='wharf'){const b=readBuild(f.building),site=waterfrontSite(b.x,b.y,'wharf');return head('Working waterfront')+strip('Regional water route',site?'Open river outlet':'No navigable regional outlet')+strip('Cargo handled today',policyNumber(f.cargoToday||0)+' units')+strip('Crew handling capacity',f.closed?'Unavailable · business closed':policyNumber(f.cargoCapacity||0)+' units / day')+strip('Handling receipts',money(f.handlingFees||0))+strip('Loading capacity used',policyNumber((f.cargoToday||0)/Math.max(1,f.cargoCapacity||0)*100)+'%')+strip('Cargo needed to cover today’s costs',policyNumber((f.expenses||0)/.10)+' units')+tip('Exporters choose the lowest delivered freight quote. Each attending worker handles 600 units daily; the wharf earns $0.10 per unit actually loaded. Road collection and the river journey are included. No cargo means no handling revenue.');}
 return (f.shippingToday||0)>0?strip('Regional freight paid today',money(f.shippingToday)):'';
}

function waterfrontSitingReason(x,y,kind){
 if(!charterOwns(x,y))return 'Purchase this district before developing its shore.';
 if(![0,3].includes(cityCell(x,y))||buildingAt(x,y)||G.landUse?.[roadId(x,y)])return 'Choose vacant land on the shore; the pier extends over adjacent water.';
 if(!waterfrontSite(x,y,'fishery'))return 'Choose a shore beside at least eight connected water tiles.';
 if(kind==='wharf'&&!waterfrontSite(x,y,'wharf'))return 'This water has no regional outlet. Build a fishery here, or choose the open river for a cargo wharf.';
 if(!nearRoad(x,y))return 'The shore needs an adjoining road for crews and cargo collection.';
 return 'Choose a vacant, chartered shore with adjoining road access.';
}

function waterfrontPlacementMessage(x,y,kind){
 if(G.treasury<buildCost[kind])return 'Treasury shortfall: '+money(buildCost[kind]-G.treasury)+'. Keep funds for construction and operating commitments.';
 if(!canPlace(x,y,true,kind))return waterfrontSitingReason(x,y,kind);
 const road=roadOffsets.map(([dx,dy])=>roadId(x+dx,y+dy)).find(id=>graph().parts[id]===graph().mainPart);
 return road!=null?'Ready: vacant shore with a connected road. Crews and orders are still required.':'Shore site available, but this road is isolated. Connect it to town before crews can work.';
}
