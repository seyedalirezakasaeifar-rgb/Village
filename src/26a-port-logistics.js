// Start only the cargo counters here. Fishery allowances retain their original
// after-payroll preparation, so freight cannot freeze yesterday's fishing crews.
function beginPortHandlingDay(){const state=ensureWaterfront();state.todayCargo=0;state.todayFees=0;for(const f of G.firms)if(f.kind==='wharf'){f.cargoToday=0;f.handlingFees=0;}}
// Greyhaven is the named ocean-facing counterparty. River consignments use the
// existing owned-stock, prepaid-carriage and delayed-settlement state machine.
function portLogisticsDepots(){
 const ready=waterDayTown===G&&waterDayNumber===G.day;
 // A UI quote must not reset daily receipts or initialize fishing allowances.
 // Actual handling uses the engine's prepared shared objects; pre-day quotes
 // use temporary geometry/capacity descriptors without authoritative writes.
 const wharves=ready?operatingWharves:G.firms.filter(f=>f.kind==='wharf'&&!f.closed).map(f=>{const b=readBuild(f.building),site=b&&waterfrontSite(b.x,b.y,'wharf'),path=site?waterOutletPath(site.id):[],capacity=workingStaff(f).length*600*(1+((f.scale||1)-1)*.25);return {f,b,site,path,remaining:capacity,capacity};}).filter(w=>w.path.length&&w.remaining>0);
 return wharves.filter(w=>!w.f.closed&&workingStaff(w.f).length).map(w=>({id:w.f.id,name:w.f.name,capacity:ready?w.f.cargoCapacity:w.capacity,port:graph().portals.get(w.b.id),fee:.10,wharf:w}));
}

const portRoadQuote=regionalQuote;
regionalQuote=function(f,m,good,direction,forcedDepot=null){
 const road=portRoadQuote(f,m,good,direction,forcedDepot),s=ensureRegionalTrade();
 if(m?.id!=='port'||s.routePreference==='interchange')return road;
 const source=graph().portals.get(f.building),quality=clamp((G.stats.roadCondition||85)/100,.4,1),options=road?[road]:[];
 for(const d of portLogisticsDepots()){
  if(forcedDepot!=null&&d.id!==forcedDepot)continue;
  const path=logisticsPath(source,d.port);if(!path.length||!d.capacity)continue;
  const waterPath=d.wharf.path,riverDays=Math.max(1,Math.ceil((waterPath.length-1)/32)),outsideDays=m.days+riverDays,pickupDays=path.length>1?Math.ceil((path.length-1)/(24*quality)):0,wait=logisticsQueue(d.id)/d.capacity;
  // River line haul moves bulk cheaply; road collection and paid dock handling
  // remain real costs. A longer voyage ties up inventory and working capital.
  const price=regionalMarketQuote(m,good,direction==='import'?'imports':'exports'),freight=d.fee+(path.length-1)*.003+(waterPath.length-1)*.0005+m.days*.008;
  options.push({m,mode:'river',waterPath:waterPath.slice(),outsideDays,path,price,freight,days:pickupDays+outsideDays+2+Math.ceil(wait),capacity:regionalCapacity(m,good,direction),depot:d.id,depotIndex:path.length-1,pickupDays,gatewayDays:0,handlingFee:d.fee,queueDays:wait,score:freight+wait*price*.012});
 }
 const selected=s.routePreference==='river'&&options.some(q=>q.mode==='river')?options.filter(q=>q.mode==='river'):options;return selected.sort((a,b)=>a.score-b.score||a.depot-b.depot)[0]||null;
};
function regionalShipmentRouteAvailable(o,f,m){
 if(o.mode!=='river')return !!regionalRoadPath(f,m).length;
 const dock=G.firms[o.depot],b=dock&&readBuild(dock.building),site=b&&waterfrontSite(b.x,b.y,'wharf');
 return !!(dock&&!dock.closed&&site&&waterOutletPath(site.id).length&&logisticsPath(graph().portals.get(f.building),graph().portals.get(b.id)).length);
}
const portQueueBase=handleLogisticsQueue;
handleLogisticsQueue=function(o,depots,s){
 if(o.mode!=='river')return portQueueBase(o,depots,s);
 const d=depots.find(d=>d.id===o.depot&&d.wharf);if(!d)return false;
 const before=o.handled,limited={...d,capacity:(s.handling.used[d.id]||0)+d.wharf.remaining},done=portQueueBase(o,[limited],s),units=o.handled-before;
 if(units>0){const w=d.wharf,state=ensureWaterfront(),fees=units*o.handlingFee;w.remaining-=units;w.f.cargoToday+=units;w.f.handlingFees+=fees;state.todayCargo+=units;state.todayFees+=fees;state.fees+=fees;}
 return done;
};
const portTradeValidator=validateRegionalTrade;
validateRegionalTrade=function(data){
 if(!portTradeValidator(data))return false;
 return [...(data.regionalTrade?.shipments||[]),...(data.regionalTrade?.recent||[])].every(o=>{
  if(o.mode==null)return data.firms[o.depot]?.kind!=='wharf'&&o.waterPath==null&&o.outsideDays==null;if(o.mode!=='river'||o.market!=='port'||!Number.isInteger(o.depot)||!['import','export'].includes(o.direction)||data.firms[o.depot]?.kind!=='wharf'||!Number.isInteger(o.outsideDays)||o.outsideDays<1||o.outsideDays>T*T||!Array.isArray(o.waterPath)||!o.waterPath.length||o.waterPath.length>T*T)return false;
  const b=data.buildings.find(b=>b.id===data.firms[o.depot].building),start=o.waterPath[0];if((!b&&(!data.firms[o.depot].demolished||(data.regionalTrade.shipments||[]).includes(o)))||(b&&(Math.abs(start%T-b.x)>1||Math.abs((start/T|0)-b.y)>1))||![0,T-1].includes(o.waterPath[o.waterPath.length-1]/T|0))return false;
  return o.waterPath.every((id,i)=>Number.isInteger(id)&&id>=0&&id<T*T&&(data.tiles[id]===2||data.tiles[id]===4||data.tiles[id]===1&&(id%T<5+Math.sin((id/T|0)*.2)*1.7||id%T===5&&(id/T|0)%4===0))&&(!i||Math.abs(id%T-o.waterPath[i-1]%T)+Math.abs((id/T|0)-(o.waterPath[i-1]/T|0))===1));
 });
};
// Read-only cargo pose contract. Exactly one actor per outside river consignment;
// no economic settlement, stock or payments are performed by presentation.
function portCargoPoses(){
 const poses=[];for(const o of G.regionalTrade?.shipments||[]){
  if(o.mode!=='river'||!['outside','return-outside'].includes(o.stage))continue;
  const seaDays=OUTSIDE_MARKETS.find(m=>m.id===o.market).days,inbound=o.direction==='import'&&o.stage==='outside'||o.direction==='export'&&o.stage==='return-outside',duration=Math.max(1,o.outsideDays-seaDays),started=o.stageStarted+(inbound?seaDays:0);
  // Hide the vessel while it is beyond the river outlet on the sea leg.
  if(G.day<started||G.day>=started+duration)continue;
  poses.push({id:o.id,port:o.depot,good:o.good,qty:o.qty,path:o.waterPath,started,duration,inbound,stage:o.stage});
 }return poses;
}
const portArrivalBase=settleRegionalArrival;
settleRegionalArrival=function(o){const done=portArrivalBase(o);if(done&&o.mode==='river'&&o.direction==='export')ensureWaterfront().exports+=o.qty;return done;};
