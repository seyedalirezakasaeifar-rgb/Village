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
  const destination=readBuild(f.building),roadFare=distance*.035*2*discount,metro=G.metro?.operating&&hasMetroCommute(home,destination)&&G.metro.fare*2<roadFare,travel=metro?G.metro.fare*2:roadFare;
  choices.push({f,distance,travel,metro,score:f.price*(1+G.policy.foodTax/100)+travel/need});
 }
 return choices.sort((a,b)=>a.score-b.score||a.f.id-b.f.id);
}
function sharesRoadNetwork(a,b){if(!a||!b)return false;const net=graph(),x=net.portals.get(a.id),y=net.portals.get(b.id);return x!=null&&y!=null&&net.parts[x]===net.parts[y];}
function workerCanCommute(person,firm){const h=G.households[person.hh];return sharesRoadNetwork(h&&readBuild(h.home),readBuild(firm.building));}
function workingStaff(f){return f.attendingWorkers||f.workers;}
