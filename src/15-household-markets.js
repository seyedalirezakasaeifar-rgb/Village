let householdMarketCache=null;
function householdMarket(){
 const net=graph();if(householdMarketCache?.town===G&&householdMarketCache.net===net&&householdMarketCache.day===G.day)return householdMarketCache;
 const shops=G.firms.filter(f=>!f.closed&&f.kind==='grocer'),homes=G.households.filter(h=>h.people.length),key=shops.map(f=>f.id).join(',')+'|'+homes.map(h=>h.home+':'+h.people.length).join(',');
 if(householdMarketCache?.town===G&&householdMarketCache.net===net&&householdMarketCache.key===key){householdMarketCache.day=G.day;return householdMarketCache;}
 const population=new Map(),counts=new Map(),stores=new Map();
 for(const h of homes){const port=net.portals.get(h.home);if(port!=null){const part=net.parts[port];population.set(part,(population.get(part)||0)+h.people.length);}}
 for(const f of shops){const port=net.portals.get(f.building);if(port!=null){const part=net.parts[port];counts.set(part,(counts.get(part)||0)+1);}}
 for(const f of shops){const port=net.portals.get(f.building),distance=new Map(),queue=[];if(port!=null){distance.set(port,0);queue.push(port);}
  for(let n=0;n<queue.length;n++)for(const next of net.neighbors.get(queue[n])||[])if(!distance.has(next)){distance.set(next,distance.get(queue[n])+1);queue.push(next);}
  const part=port==null?null:net.parts[port];stores.set(f.id,{distance,demand:part==null?0:(population.get(part)||0)*1.6/Math.max(1,counts.get(part)||0)});
 }
 return householdMarketCache={town:G,net,key,day:G.day,stores};
}
function reachableRetailDemand(f){return householdMarket().stores.get(f.id)?.demand||0;}
function groceryChoices(h,home,grocers){
 const market=householdMarket(),port=home&&market.net.portals.get(home.id),need=Math.max(1,h.people.length*1.6),discount=1-clamp(G.policy.transitBudget*(G.actualServiceFunding?.transit||0)/280,0,.65),choices=[];
 for(const f of grocers){const distance=market.stores.get(f.id)?.distance.get(port);if(distance==null)continue;
  const destination=readBuild(f.building),journey=transitJourney(home,destination,2),publicTransit=journey&&journey.time<=90&&journey.fare*2<distance*.035*2*discount&&journey.routes.every(id=>{const s=G.transit.routes.find(r=>r.id===id).stats;return s.reserved+2<=s.capacity;})?journey:null,roadFare=distance*.035*2*discount,metro=G.metro?.operating&&hasMetroCommute(home,destination)&&G.metro.fare*2<roadFare,travel=publicTransit?publicTransit.fare*2:metro?G.metro.fare*2:roadFare;
  choices.push({f,distance,travel,metro:!publicTransit&&metro,transit:publicTransit,score:f.price*(1+G.policy.foodTax/100)+travel/need});
 }
 return choices.sort((a,b)=>a.score-b.score||a.f.id-b.f.id);
}
function sharesRoadNetwork(a,b){if(!a||!b)return false;const net=graph(),x=net.portals.get(a.id),y=net.portals.get(b.id);return x!=null&&y!=null&&net.parts[x]===net.parts[y];}
function workerCanCommute(person,firm){const h=G.households[person.hh],home=h&&readBuild(h.home),work=readBuild(firm.building);if(!sharesRoadNetwork(home,work))return false;if(!G.transit?.routes.length)return true;if(person.transitTrip?.day===G.day||hasMetroCommute(home,work))return true;const net=graph();return roadDistance(net.portals.get(home.id),net.portals.get(work.id))<=60+(G.transit?.routes.length?0:(G.policy.transitBudget||0)/8);}
function workingStaff(f){return f.attendingWorkers||f.workers;}

function regionalUtilityAccess(home){if(!home)return false;const net=graph(),port=net.portals.get(home.id);return port!=null&&net.parts[port]===net.mainPart;}
