// Deterministic model services. Presentation has its own hash-based randomness.
const RELEASE=Object.freeze({"version":"8.0.0","code":22,"edition":"A Trading Town","schema":8,"package":"org.townledger.vale"});
let rngState=42,visualState=918273,simulationBusy=false;
const perfStats={frames:[],ticks:[],effective:1,backlog:0,days:0,elapsed:0,errors:[]};
function random(){rngState=(rngState+0x6D2B79F5)>>>0;let t=rngState;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;}
function visualRandom(){visualState=(Math.imul(visualState,1664525)+1013904223)>>>0;return visualState/4294967296;}
function hash(n){n=Math.imul((n^0x9e3779b9)>>>0,0x85ebca6b);n^=n>>>13;return (Math.imul(n,0xc2b2ae35)^(n>>>16))>>>0;}
function book(from,to,amount,reason,entity=-1){if(!(amount>0))return;G.transactions=G.transactions||[];G.transactions.push({day:G.day,from,to,amount,reason,entity});if(G.transactions.length>800)G.transactions.splice(0,G.transactions.length-800);}
function ensureSystems(){
 if(!G)return;
 if(G.airport?.runway)for(const id of G.airport.runway)if(G.tiles[id]===3)G.tiles[id]=0;
 G.climateSeasons=G.climateSeasons===true;G.climateWeather=G.climateWeather===true;if(!G.climateWeather)G.weather='clear';G.nextLoanId=G.nextLoanId??0;G.schema=RELEASE.schema;G.release=RELEASE.version;G.development={fields:0,redevelopments:0,towers:0,airfields:0,...G.development};
 G.investors=G.investors||[{id:0,name:'Vale Property Partnership',cash:0,invested:0,spending:0}];
 G.transactions=G.transactions||[];G.observations=G.observations||[];G.policyExperiments=G.policyExperiments||[];
 G.transport=G.transport||{journeys:[],next:1,arrived:0,delayed:0,cancelled:0};
 G.accounts=G.accounts||{baseline:totalMoney(),maxError:0};
 G.scenarioSeed=G.scenarioSeed||G.worldSeed||42;ensureGoodsAccounts();
 G.housingMarket=G.housingMarket||{rentIndex:1,landIndex:1,transactions:0};
 G.councilArchive=G.councilArchive||[];
 for(const b of G.buildings){if(!b.title)b.title={kind:b.owner>=0?'household':'regional',id:b.owner};if(b.baseValue==null)b.baseValue=b.value;}
}
function propertyInvestor(){if(!G.investors?.length)ensureSystems();return G.investors[0];}
function financeConstruction(cost,entity=-1){
 if(!Number.isFinite(cost)||cost<=0)return false;
 const investor=propertyInvestor();
 if(investor.cash<cost){const injection=cost-investor.cash;if(G.region<injection)return false;G.region-=injection;investor.cash+=injection;investor.invested+=injection;book('Regional capital',investor.name,injection,'Equity subscription',entity);}
 const contractors=G.firms.filter(f=>f.kind==='contractor'&&!f.closed);
 const local=contractors.length?cost*.44:0;
 investor.cash-=cost;investor.spending+=cost;
 if(local){const c=contractors[G.day%contractors.length];c.cash+=local;c.pendingRevenue=(c.pendingRevenue||0)+local;book(investor.name,c.name,local,'Construction labour and margin',entity);}
 G.region+=cost-local;book(investor.name,'Regional suppliers',cost-local,'Building materials and external construction',entity);
 return true;
}
function developmentQuote(place,kind,demand){
 const central=clamp(1-(Math.abs(place.x-27)+Math.abs(place.y-27))/50,.12,1),housing=kind==='home';
 const cost=(housing?buildCost.home:types[kind]?.cost||5000)+(housing?G.policy.zoningRestriction*9:G.policy.permitFee);
 const rent=housing?2.5*(3.1+G.policy.zoningRestriction*.035)*G.housingMarket.rentIndex:0;
 const annualNet=housing?rent*360*.66:Math.max(0,(demand.applicants[kind]||0)*4.5)*(1-G.policy.profitTax/100)*12;
 const land=Math.round(700+central*1350+Math.max(0,demand.housingPressure-45)*16);
 const hurdle=.055+G.policy.lendingRules*.00035+(100-demand.confidence)*.0004;
 return {cost,land,rent,annualNet,yield:annualNet/(cost+land),hurdle,central,expected:annualNet-(cost+land)*hurdle};
}
function explainDevelopment(b,q,use){b.investment={day:G.day,use,...q};b.title={kind:'investor',id:0};b.owner=-2;const investor=G.investors[0];if(G.region>=q.land){G.region-=q.land;investor.cash+=q.land;investor.invested+=q.land;book('Regional capital',investor.name,q.land,'Equity for land purchase',b.id);investor.cash-=q.land;G.region+=q.land;book(investor.name,'Regional landowner',q.land,'Parcel title acquired',b.id);}}
function housingMarketDay(force=false){
 const living=G.households.filter(h=>h.people.length),stock=G.buildings.filter(b=>['home','apartment','tower'].includes(b.kind));
 const units=stock.reduce((n,b)=>n+(b.kind==='tower'?9:b.kind==='apartment'?4:1),0);
 const occupied=G.households.filter(h=>h.people.length&&readBuild(h.home)).length;
 const vacancy=Math.max(0,units-occupied),target=clamp(.88+(1-vacancy/Math.max(1,units))* .28+G.policy.zoningRestriction*.002, .65,1.5);
 G.housingMarket.rentIndex=G.housingMarket.rentIndex*.985+target*.015;
 if(G.day%30!==0&&!force)return;
 for(const b of stock){
  const access=graph().portals.has(b.id),central=clamp(1-(Math.abs(b.x-27)+Math.abs(b.y-27))/55,.1,1);
  const want=b.baseValue*G.housingMarket.rentIndex*(.73+central*.23+(access?.10:-.20))*(.7+b.condition*.003);
  b.value=b.value*.88+want*.12;b.marketRent=(b.kind==='tower'?9:b.kind==='apartment'?4:1)*8*G.housingMarket.rentIndex;
 }
 const median=stock.map(b=>b.value).sort((a,b)=>a-b)[Math.floor(stock.length/2)]||0;
 G.housingMarket={...G.housingMarket,units,occupied,vacancy,medianValue:median,landIndex:median/50000};
 // Voluntary acquisitions use existing savings; no occupant is removed.
 const listing=stock.find(b=>b.owner===-2&&b.kind==='home'&&!b.redevelopment);
 if(listing){const price=listing.value*.92,buyer=living.find(h=>h.home===listing.id&&householdLiquidity(h)>price+5000)||living.find(h=>householdLiquidity(h)>price+5000);
  if(buyer){if(buyer.cash<price)for(const [id,amount] of Object.entries(buyer.deposits||{})){withdrawal(buyer,G.banks[+id],Math.min(amount,price-buyer.cash));if(buyer.cash>=price)break;}if(buyer.cash<price)return;buyer.cash-=price;G.investors[0].cash+=price;listing.owner=buyer.id;listing.title={kind:'household',id:buyer.id};G.housingMarket.transactions++;book(buyer.name+' household',G.investors[0].name,price,'Property title purchase; tenancy preserved',listing.id);}}
}
function expireCouncilLetters(){
 const keep=[];for(const item of G.councilInbox||[]){if(G.day-item.day>120){G.councilArchive.unshift({...item,closed:G.day,response:'No council action; existing policy retained'});}else keep.push(item);}
 G.councilInbox=keep;G.councilArchive=G.councilArchive.slice(0,40);
}
function recordObservation(){
 const hm=G.housingMarket||{},fs=G.firms.filter(f=>!f.closed),incomes=G.households.filter(h=>h.people.length).map(h=>(h.income-h.tax)/h.people.length).sort((a,b)=>a-b);
 const obs={day:G.day,population:G.stats.population,employment:G.stats.employment,hardship:G.stats.hardship,treasury:G.treasury,businesses:fs.length,construction:G.projects.length,rentIndex:hm.rentIndex,medianValue:hm.medianValue||0,vacancy:hm.vacancy||0,privateSpend:G.development.privateSpend||0,profit:fs.reduce((n,f)=>n+(f.netProfit||0),0),medianIncome:incomes[Math.floor(incomes.length/2)]||0,medicalCoverage:G.serviceProvision?.health?.coverage||0,schoolCoverage:G.actualServiceFunding?.school||0,trainingCompletions:G.civicTrainingCompletions||0,unmetFood:G.market?.unmetFood||0,bankLiquidity:G.banks.reduce((n,b)=>n+b.cash,0),debt:G.loans.filter(l=>l.status==='active').reduce((n,l)=>n+l.balance,0)};
 G.observations.push(obs);if(G.observations.length>1200)G.observations.shift();
 for(const e of G.policyExperiments){if(!e.after&&G.day-e.day>=180)e.after={...obs};}
}
function validateTown(){
 const issues=[],claimed=new Set(),members=new Set(),workers=new Set();
 for(const b of G.buildings)for(const id of footprintOf(b)){if(claimed.has(id)||G.tiles[id]===1||G.tiles[id]===2||G.landUse?.[id])issues.push('Occupied footprint collision '+b.id+':'+id);claimed.add(id);}
 const cropCounts={};for(const [key,code] of Object.entries(G.landUse||{})){const id=Number(key);if(!Number.isInteger(id)||id<0||id>=T*T||![1,2,3].includes(code)||G.tiles[id]!==0||claimed.has(id))issues.push('Reserved land collision '+key);if(code===1){const owner=G.fieldOwner?.[key];if(!Number.isInteger(owner)||G.firms[owner]?.kind!=='farm')issues.push('Invalid crop title '+key);else cropCounts[owner]=(cropCounts[owner]||0)+1;}}
 for(const f of G.firms)if(f.kind==='farm'&&(G.fieldCount?.[f.id]||0)!==(cropCounts[f.id]||0))issues.push('Crop count mismatch '+f.id);
 for(const h of G.households){if(!Number.isFinite(h.cash)||h.cash<-.01)issues.push('Invalid household cash '+h.id);for(const id of h.people){if(members.has(id)||G.people[id]?.hh!==h.id||G.people[id]?.deceased||G.people[id]?.movedAway)issues.push('Household membership '+id);members.add(id);}}
 for(const p of G.people)if(!p.deceased&&!p.movedAway&&!members.has(p.id))issues.push('Unhoused identity '+p.id);
 for(const f of G.firms){if(!Number.isFinite(f.cash)||f.cash<-.01)issues.push('Invalid business cash '+f.id);for(const id of f.workers){if(workers.has(id)||G.people[id]?.job!==f.id)issues.push('Employment ownership '+id);workers.add(id);}}
 for(const b of G.banks)if(!Number.isFinite(b.cash)||b.cash<-.01)issues.push('Bank balance '+b.id);
 for(const v of traffic)for(let i=0;i<v.path.length;i++){if(G.tiles[v.path[i]]!==1)issues.push('Vehicle off road '+v.id);if(i&&Math.abs(v.path[i]%T-v.path[i-1]%T)+Math.abs((v.path[i]/T|0)-(v.path[i-1]/T|0))!==1)issues.push('Invalid route '+v.id);}
 for(const f of G.firms)for(const [k,n] of Object.entries(f.stock))if(!Number.isFinite(n)||n<-.0001)issues.push('Invalid commodity stock '+f.id+':'+k);
 for(const row of goodsBalance())if(!Number.isFinite(row.error)||Math.abs(row.error)>.02)issues.push('Commodity accounting '+row.good+':'+row.error);
 return {ok:issues.length===0,issues,total:totalMoney(),population:G.stats.population,day:G.day};
}
function capitalCirculationDay(){
 if(G.day%30!==0)return;
 // The partnership's regional subscribers receive distributions from actual rent
 // receipts. Retaining unlimited rent while regional demand runs out creates an
 // artificial permanent liquidity trap, not meaningful firm competition.
 // Corporate treasuries retain operating liquidity, then distribute surplus to
 // their actual shareholders. Founding regional owners must receive dividends
 // too; owner=-1 is not permission to sterilise all accumulated earnings.
 for(const f of G.firms){if(f.closed)continue;
  const debt=G.loans.filter(l=>l.status==='active'&&l.ownerType==='firm'&&l.ownerId===f.id).reduce((n,l)=>n+l.balance,0),recipe=formulas[f.kind];
  const inputs=recipe?.inp?Math.max(1,f.salesTrend)*(recipe.amount/Math.max(1,recipe.qty))*marketPrice(recipe.inp)*14:0;
  const reserve=15000+workerIncome(f)*Math.max(1,f.jobs)*90+inputs+debt;
  const distribution=Math.max(0,f.cash-reserve)*.12;if(distribution<=.01)continue;
  f.cash-=distribution;f.distributed=(f.distributed||0)+distribution;
  const owner=G.households[f.owner];if(owner){owner.cash+=distribution;owner.income+=distribution;owner.dividends=(owner.dividends||0)+distribution;}else G.region+=distribution;
  book(f.name,owner?owner.name+' household':'Regional shareholders',distribution,'Corporate treasury distribution above operating and debt reserves',f.building);
 }
 const investor=propertyInvestor(),reserve=Math.max(120000,G.projects.length*12000);
 const distribution=Math.max(0,investor.cash-reserve)*.08;
 if(distribution>0){investor.cash-=distribution;G.region+=distribution;investor.distributed=(investor.distributed||0)+distribution;book(investor.name,'Regional shareholders',distribution,'Distribution of retained property earnings');}
 // Empty households hold an estate for one year, then external heirs receive
 // cash and redeemed deposits. No unrelated local family inherits their balance.
 for(const h of G.households){if(h.people.length){delete h.estateSince;continue;}
  h.estateSince=h.estateSince??G.day;if(G.day-h.estateSince<360)continue;
  for(const [id,amount] of Object.entries(h.deposits||{}))if(amount>0)withdrawal(h,G.banks[+id],amount);
  if(h.cash>0){G.region+=h.cash;h.estatePaid=(h.estatePaid||0)+h.cash;h.cash=0;}
 }
}
function systemsDay(){
 ensureSystems();capitalCirculationDay();housingMarketDay();municipalProcurement();householdFormation();occupyVacantHousing();birthsAndGenerations();expireCouncilLetters();commodityPriceReview();
 if(G.day%30===0){const error=Math.abs(totalMoney()-G.accounts.baseline);G.accounts.maxError=Math.max(G.accounts.maxError,error);}
 G.rngState=rngState;
}
function checksum(text){let h=2166136261;for(let i=0;i<text.length;i++){h^=text.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0).toString(16);}
function archivePayload(){G.rngState=rngState;G.trafficState={vehicles:traffic,clock:frameClock,elapsed:trafficElapsed,gates:[...intersectionGates],serial:vehicleSerial};G.visualState=visualState;return JSON.stringify(G);}
function percentile(a,p){if(!a.length)return 0;const b=a.slice().sort((x,y)=>x-y);return b[Math.min(b.length-1,Math.floor(b.length*p))];}
