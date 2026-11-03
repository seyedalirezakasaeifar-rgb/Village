// Existing capital in authored starts is funded before the opening balance sheet.
function initializeScenario(){
 if(chosenScenario!=='regional')return;
 G.scenario='regional';Object.assign(G.policy,{incomeTax:13,profitTax:14,zoningRestriction:20,transitBudget:160,policeBudget:300,defenseBudget:220,healthBudget:180,educationBudget:220,aidBudget:250});
 const kinds=Object.entries({factory:7,office:12,warehouse:7,grocer:6,bakery:3,farm:2,mill:2,forestry:2,sawmill:4,quarry:1,contractor:3,tavern:7,college:2}).flatMap(([kind,count])=>Array(count).fill(kind));
 // Reserve actual employment sites before bidding housing onto the remaining land.
 for(let n=0;n<kinds.length;n++){
  if(creatorCapacityReason(0,0,1,true))break;
  const kind=kinds[n%kinds.length];let site=buildableCandidates('business').find(p=>canPlace(p.x,p.y,true,kind));
  if(!site){privatelyBuiltRoads({...cityDemand(),homeDemand:100,businessDemand:100,freeLots:0});site=buildableCandidates('business').find(p=>canPlace(p.x,p.y,true,kind));}if(!site)continue;
  const cost=types[kind].cost,capital=21000;if(G.region<cost+capital+50000)break;
  financeConstruction(cost);G.region-=capital;const f=createFirm(kind,site.x,site.y);if(!f)throw Error('Scenario investment lost its parcel');
  f.cash=capital;f.jobs=kind==='college'?4:(SECTOR_WORKERS[kind]||4);f.wage=32;f.age=90;
  book('Regional capital',f.name,capital,'Opening enterprise equity',f.building);
 }
 for(let n=0;n<150&&G.stats.population<650;n++){
  const site=buildableCandidates('housing').find(p=>canPlace(p.x,p.y,true,'apartment'));
  if(!site){privatelyBuiltRoads({...cityDemand(),homeDemand:100,businessDemand:100,freeLots:0});continue;}
  const cost=39000;if(!financeConstruction(cost))break;
  const b={id:G.nextId++,kind:'apartment',x:site.x,y:site.y,value:175000,baseValue:175000,condition:93,owner:-2,firm:-1,hh:-1,units:[],title:{kind:'investor',id:0},footprint:footprintFor(site.x,site.y,'apartment')};
  for(const id of b.footprint)if(G.tiles[id]===3)G.tiles[id]=0;G.buildings.push(b);invalidateBuildingIndex();invalidateRoads(false);
  for(let k=0;k<4;k++){const h=addHouseholdAt(b,2500);if(h)migrationRegisterTenancy(h,b);}b.hh=b.units[0]??-1;
  G.development.privateSpend=(G.development.privateSpend||0)+cost;recompute();
 }
 for(const h of G.households.filter(h=>h.id>=67)){for(let j=0;j<h.people.length;j++){const person=G.people[h.people[j]];person.age=h.id%5===0?Math.round(rn(71,79)):j===0?Math.round(rn(27,57)):h.id%3===0?Math.round(rn(7,15)):Math.round(rn(24,56));}}
 assignJobs();recompute();G.journal.push({day:1,name:'Market Cross opening balance sheet',message:'An established regional borough. Apartment owners and employers funded their land, buildings and working capital before this council took office.',baseline:{...G.stats,treasury:G.treasury}});
 story('Market Cross inherits dense housing, manufacturing and services. Transport investors will judge whether new infrastructure pays.','neutral');
}
