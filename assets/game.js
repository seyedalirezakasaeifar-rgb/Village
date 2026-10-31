// SOURCE: 00-foundation.js
'use strict';
// TownLedger: offline small-town economic policy laboratory. Separate Android WebView adaptation.
(function(){
// Negative indexing without requiring a recent Android WebView Array.at.
function fromEnd(values,offset=1){return values[values.length-offset];}
function owns(object,key){return Object.prototype.hasOwnProperty.call(object,key);}
const ART_DATA={};
const $=id=>document.getElementById(id), clamp=(x,a,b)=>Math.max(a,Math.min(b,x)),money=x=>(x<0?'−':'')+'$'+Math.round(Math.abs(x)).toLocaleString('en-CA');
const fmt=x=>Number(x||0).toLocaleString('en-CA',{maximumFractionDigits:1});
const esc=x=>String(x==null?'':x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const rn=(a,b)=>a+random()*(b-a),pick=a=>a[random()*a.length|0];
const first=['Arthur','Alice','Thomas','Eleanor','Henry','Margaret','Jack','Edith','Charles','Emily','George','Rose','William','Florence','James','Clara','Robert','Agnes','Daniel','Ivy','Samuel','Hannah','Oliver','Mabel','Edward','Beatrice','Frederick','Ada','Joseph','Grace','Peter','Julia','Benjamin','Isabel'];
const surnames=['Bennett','Parker','Sutton','Miller','Hughes','Clarke','Foster','Wright','Carter','Howard','Taylor','Moore','Campbell','Ward','Russell','Harris','Reed','Turner','Hill','Smith','Brooks','Davies','Morgan','Baker','Wilson','Grant'];
const T=80, TW=72, TH=36, RW=T*TW+140,RH=T*TH+120;
const types={
 bank:{n:'Bank Branch',cost:0,col:'#a3b0a6',jobs:0},
 worksite:{n:'Private Construction Site',cost:0,col:'#c0a076',jobs:0},
 apartment:{n:'Apartment House',cost:0,col:'#b7ab91',jobs:0},
 tower:{n:'High-rise Residences',cost:0,col:'#a0afb1',jobs:0},
 factory:{n:'Manufacturing Works',cost:9800,col:'#879398',jobs:14,build:'Factory'},
 warehouse:{n:'Freight Depot',cost:12000,col:'#927b65',jobs:10,build:'Freight Depot'},
 office:{n:'Commercial Offices',cost:14200,col:'#a5a69b',jobs:13,build:'Office'},
 college:{n:'Private College',cost:18000,col:'#a9a088',jobs:8,build:'College'},
 airport:{n:'Regional Airfield',cost:0,col:'#879c9e',jobs:18},
 metro_station:{n:'Underground Station',cost:18000,col:'#496a7a',jobs:0,build:'Private Underground'},
 repair:{n:'Resurface road',cost:135,col:'#a0a28b',jobs:0,build:'Repair'},
 home:{n:'Cottage',cost:20000,col:'#cbaf75',jobs:0,build:'Home'},
 grocer:{n:'Grocer',cost:4300,col:'#a96d49',jobs:7,build:'Grocer'},
 bakery:{n:'Bakery',cost:3600,col:'#b77b56',jobs:7,build:'Bakery'},
 mill:{n:'Flour Mill',cost:4800,col:'#869888',jobs:8,build:'Flour Mill'},
 farm:{n:'Farm',cost:3100,col:'#ad9d54',jobs:9,build:'Farm'},
 forestry:{n:'Forestry',cost:3000,col:'#6c8d65',jobs:8,build:'Forestry'},
 sawmill:{n:'Sawmill',cost:4100,col:'#ac865e',jobs:8,build:'Sawmill'},
 quarry:{n:'Quarry',cost:3900,col:'#92928d',jobs:8,build:'Quarry'},
 contractor:{n:'Construction Co.',cost:4400,col:'#b2a38e',jobs:8,build:'Contractor'},
 townhall:{n:'Town Hall',cost:0,col:'#d6c6a4',jobs:0},
 police:{n:'Constabulary',cost:7600,col:'#6588a7',jobs:5,build:'Police Station'},
 fire:{n:'Fire Brigade',cost:6900,col:'#bb745b',jobs:5,build:'Fire Brigade'},
 clinic:{n:'Clinic',cost:8000,col:'#bdb7a3',jobs:6,build:'Clinic'},
 park:{n:'Public Green',cost:550,col:'#6c987a',jobs:0,build:'Park'},
 school:{n:'Village School',cost:6900,col:'#ac9372',jobs:0,build:'School'},
 courthouse:{n:'Magistrates Court',cost:8400,col:'#9a9887',jobs:0,build:'Court'},
 watchtower:{n:'Watchtower',cost:4900,col:'#879089',jobs:0,build:'Watchtower'},
 square:{n:'Market Square',cost:2500,col:'#aca486',jobs:0,build:'Market Square'},
 wharf:{n:'River Cargo Wharf',cost:7600,col:'#819b98',jobs:2,build:'Cargo wharf'},
 fishery:{n:'River Fishery',cost:3500,col:'#75a5a2',jobs:7,build:'Fishery'},
 tavern:{n:'Village Tavern',cost:3200,col:'#b28c56',jobs:6,build:'Tavern'},
};
const goods={grain:2,flour:3,food:3.3,logs:2,timber:4,stone:3,manufactures:8.5};
const formulas={farm:{out:'grain',qty:140,inp:null,amount:0},mill:{out:'flour',qty:175,inp:'grain',amount:105},bakery:{out:'food',qty:200,inp:'flour',amount:105},grocer:{out:null,qty:0,inp:'food',amount:0},forestry:{out:'logs',qty:170},sawmill:{out:'timber',qty:130,inp:'logs',amount:100},quarry:{out:'stone',qty:125},fishery:{out:'food',qty:130},factory:{out:'manufactures',qty:85,inp:'timber',amount:58}};
const buildIcons={metro_station:'Ⓜ',repair:'↻',road:'═',home:'⌂',grocer:'▣',bakery:'♨',mill:'◈',farm:'❖',forestry:'♣',sawmill:'▥',quarry:'◆',contractor:'⚒',police:'♜',fire:'♨',clinic:'✚',park:'♣',school:'✎',courthouse:'⚖',watchtower:'♜',square:'◉',wharf:'⚓',fishery:'≈',tavern:'♨',factory:'⚙',warehouse:'▤',office:'▦',college:'♜'};
const buildCost={metro_station:18000,road:150,repair:135,home:20000,grocer:4300,bakery:3600,mill:4800,farm:3100,forestry:3000,sawmill:4100,quarry:3900,contractor:4400,police:7600,fire:6900,clinic:8000,park:550,school:6900,courthouse:8400,watchtower:4900,square:2500,wharf:7600,fishery:3500,tavern:3200,factory:9800,warehouse:12000,office:14200,college:18000};
const defs=[
 ['pensionDaily','Retirement pension / person / day',0,40,1,'$','Treasury-funded income for residents over 70. Benefits are shared proportionally if funds fall short; an ageing population raises the fiscal cost.'],
 ['policyRate','Policy interest rate (annual)',0,20,.25,'%','Benchmark set by the monetary authority. Bank funding, new and variable-rate credit, savings and investment hurdles adjust with a lag. Higher rates restrain borrowing and demand; lower rates do not make insolvent projects viable.'],
 ['incomeTax','Income tax',0,40,1,'%','Share of earnings paid by working residents to the town.'],
 ['profitTax','Business profit tax',0,45,1,'%','Tax on positive net operating profit of private businesses.'],
 ['propertyTax','Property tax (annual)',0,5,.1,'%','Tax on property values, charged to owners daily in annualized instalments.'],
 ['foodTax','Food sales tax',0,30,1,'%','Collected from purchases at local grocers; reduces food affordability.'],
 ['utilityTax','Domestic energy levy',0,30,1,'%','Levied on actual household heating and electricity bills. Raises funds, increases living costs.'],
 ['commercialRate','Business property rate (annual)',0,8,.25,'%','Annual tax on privately operating premises, payable even in years with weak profits.'],
 ['minWage','Minimum daily wage',10,90,1,'$','Raises pay but also raises labour costs for small firms.'],
 ['permitFee','Business entry permit',0,3000,25,'$','Fee charged when an investor opens a new enterprise.'],
 ['policeBudget','Constabulary budget / day',0,800,10,'$','Fund patrols, investigators and public safety. Stations improve coverage.'],
 ['defenseBudget','Fire and civil defence / day',0,800,10,'$','Maintains emergency preparedness. Stations improve response.'],
 ['aidBudget','Housing assistance / day',0,600,10,'$','Direct household transfers, prioritized by hardship and low savings.'],
 ['energyAidBudget','Heating assistance / day',0,400,10,'$','Pays energy bills for low-cash households, especially in winter.'],
 ['transitBudget','Commuter transit / day',0,250,10,'$','Supports journeys to work and improves access to jobs across the borough.'],
 ['outreachBudget','Community outreach / day',0,300,10,'$','Local support services that reduce isolation and some risk factors.'],
 ['employmentSubsidy','Wage subsidy / worker / day',0,15,1,'$','Town reimburses employers per filled job, subject to available funds.'],
 ['importTariff','Import tariff',0,40,1,'%','Adds costs to imported food and industrial materials, producing revenue.'],
 ['healthBudget','Clinic & public health / day',0,500,10,'$','Fund preventive treatment, clinic equipment and household health.'],
 ['educationBudget','School & training / day',0,500,10,'$','Raises worker skill and increases business productivity gradually.'],
 ['roadBudget','Road maintenance / day',0,250,10,'$','Upkeep for roads and local access; poor service lowers trade efficiency.'],
 ['zoningRestriction','Building restrictions',0,100,5,'%','Higher restrictions slow private homebuilding, reducing housing supply.'],
 ['businessRegulation','Business compliance rules',0,100,5,'%','Safeguards can lower workplace incidents but add costs to local firms.'],
 ['militiaBudget','Civil defence volunteers / day',0,400,10,'$','Reserve volunteers who help manage exceptional floods and regional emergencies.'],
 ['bankReserve','Bank minimum reserve',5,35,1,'%','Bank cash reserves against deposits. Higher levels lower lending capacity and help meet withdrawals.'],
 ['lendingRules','Credit underwriting standards',0,100,5,'%','Strict standards constrain risky borrowing but reduce investment and consumption credit.'],
 ['depositGuarantee','Deposit insurance coverage',0,100,5,'%','When a bank fails, cover this share of otherwise lost deposits using available municipal funds.'],
 ['treasuryInvestment','Regional reserve investment share',0,100,5,'%','Share of surplus municipal cash available to buy outside-region securities when trade liquidity is low.']
];
const defaults={policyRate:3,pensionDaily:16,incomeTax:12,profitTax:12,propertyTax:1.1,foodTax:4,utilityTax:2,commercialRate:.6,energyAidBudget:35,transitBudget:35,minWage:28,permitFee:250,policeBudget:180,defenseBudget:140,aidBudget:100,outreachBudget:40,employmentSubsidy:0,importTariff:0,healthBudget:70,educationBudget:90,roadBudget:25,zoningRestriction:25,businessRegulation:25,militiaBudget:25,bankReserve:12,lendingRules:35,depositGuarantee:0,treasuryInvestment:60,imports:true};
let hostSuspended=false;
let G=null,active='',buildMode='',selected=null,paused=false,speed=1,toastTimeout=0,chosenScenario='settlement',draftPolicy={},overlay='none',pendingEvent=null,previousDailyCash=0,autoSaveOK=true,filterPeople='all',filterFirms='all',citizenQuery='',constructionCategory='all',showTutorial=true,roadPainted=new Set(),roadBatchDirty=false;
let bitmap=document.createElement('canvas');bitmap.width=RW;bitmap.height=RH;let bg=bitmap.getContext('2d',{alpha:false,willReadFrequently:false});
const cv=$('view'),ctx=cv.getContext('2d',{alpha:false});let cw=1000,ch=600,dpr=1,cam={x:RW/2,y:RH/2,zoom:.68};let dirty=true,staticDirty=true;let vehicles=[];
// FINANCIAL ECONOMY: banks are separate cash-holding agents. Deposits are
// liabilities, NOT additional currency in the conservation check. Loans move
// actual reserves to borrowers and return principal + interest on repayment.
const FIN_BANK_NAMES=['Vale Mutual Savings','Mercantile & County Bank','First Borough Credit'];

// SOURCE: 05-systems.js
// Deterministic model services. Presentation has its own hash-based randomness.
const RELEASE=Object.freeze({"version":"7.1.0","code":20,"edition":"The Working City","schema":6,"package":"org.townledger.vale"});
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
 const obs={day:G.day,population:G.stats.population,employment:G.stats.employment,hardship:G.stats.hardship,treasury:G.treasury,businesses:fs.length,construction:G.projects.length,rentIndex:hm.rentIndex,medianValue:hm.medianValue||0,vacancy:hm.vacancy||0,privateSpend:G.development.privateSpend||0,profit:fs.reduce((n,f)=>n+(f.netProfit||0),0),medianIncome:incomes[Math.floor(incomes.length/2)]||0,medicalCoverage:G.serviceProvision?.health?.coverage||0,schoolCoverage:G.serviceProvision?.school?.coverage||0,trainingCompletions:G.civicTrainingCompletions||0,unmetFood:G.market?.unmetFood||0,bankLiquidity:G.banks.reduce((n,b)=>n+b.cash,0),debt:G.loans.filter(l=>l.status==='active').reduce((n,l)=>n+l.balance,0)};
 G.observations.push(obs);if(G.observations.length>1200)G.observations.shift();
 for(const e of G.policyExperiments){if(!e.after&&G.day-e.day>=180)e.after={...obs};}
}
function validateTown(){
 const issues=[],claimed=new Set(),members=new Set(),workers=new Set();
 for(const b of G.buildings)for(const id of footprintOf(b)){if(claimed.has(id)||G.tiles[id]===1||G.tiles[id]===2||G.landUse?.[id])issues.push('Occupied footprint collision '+b.id+':'+id);claimed.add(id);}
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

// SOURCE: 07-options.js
// Presentation preferences persist independently. Climate rules travel with the town archive.
const OPTION_DEFAULTS={quality:'balanced',fps:30,traffic:true,effects:true,decor:true,seasons:false,weather:false,largeText:false,reducedMotion:false,autoSave:30,showHints:true,streetNames:true};
let gameOptions={...OPTION_DEFAULTS};
try{const old=JSON.parse(localStorage.getItem('townledger-options')||'{}');for(const k of Object.keys(OPTION_DEFAULTS))if(typeof old[k]===typeof OPTION_DEFAULTS[k])gameOptions[k]=old[k];}catch(_){}
if(!['low','balanced','high'].includes(gameOptions.quality))gameOptions.quality='balanced';
if(![20,30,60].includes(gameOptions.fps))gameOptions.fps=30;
if(![15,30,60,120].includes(gameOptions.autoSave))gameOptions.autoSave=30;
function seasonsEnabled(){return G?.climateSeasons===true;}
function weatherEnabled(){return G?.climateWeather===true;}
function visualMonth(){return seasonsEnabled()?G.month:5;}
function applyPresentationOptions(){
 document.body.classList.toggle('large-text',gameOptions.largeText);document.body.classList.toggle('hide-hints',!gameOptions.showHints);
 if(typeof atlas!=='undefined'){atlas.clear();atlasBytes=0;}if(typeof fit==='function')fit();staticDirty=true;dirty=true;
}
// Apply classes now; renderer initialization follows in the ordered bundle.
document.body.classList.toggle('large-text',gameOptions.largeText);document.body.classList.toggle('hide-hints',!gameOptions.showHints);

// SOURCE: 08-market-model.js
let marketOpen=false;
function policyNumber(value){return Number(value||0).toLocaleString('en-CA',{maximumFractionDigits:2});}
// A stock-flow consistent operating model. Inventory purchases are assets;
// cost of goods becomes expense when sold, rather than when a warehouse fills.
function householdLiquidity(h){return h.cash+Object.values(h.deposits||{}).reduce((n,v)=>n+Math.max(0,v),0);}
const SECTOR_WORKERS={farm:4,fishery:3,wharf:2,mill:3,bakery:3,grocer:2,forestry:3,sawmill:3,quarry:3,contractor:4,tavern:3,factory:7,warehouse:4,office:6,college:5,airport:6};
function ensureMarketModel(){
 if(!G.market)G.market={version:2,cpi:100,inflation:0,baseFoodPrice:5.2,unmetFood:0,consumedFood:0,externalSales:0,imports:0,privateRestartCapital:0};
 G.market.version=2;for(const p of G.people)if(p.age>70&&p.job>=0){p.job=-1;p.retired=true;}
 for(const f of G.firms){
  f.workers=f.workers.filter(id=>G.people[id]?.job===f.id&&!G.people[id]?.deceased&&!G.people[id]?.movedAway);
  f.unitCost=f.unitCost||Object.fromEntries(Object.keys(goods).map(k=>[k,marketPrice(k)]));f.ask=f.ask||{};f.operating=f.operating||{};
  if(!Number.isFinite(f.salesTrend))f.salesTrend=formulas[f.kind]?.qty*.65||30;
  if(!Number.isFinite(f.revenueTrend))f.revenueTrend=Math.max(1,workerIncome(f)*f.workers.length*1.3);
  if(!Number.isFinite(f.marginTrend))f.marginTrend=.12;f.marginTrend=clamp(f.marginTrend,-1,1);
  f.scale=f.scale||1;f.workingCapitalRaised=f.workingCapitalRaised||0;
 }
}
function foodRetailTarget(f){
 const staff=Math.max(1,workingStaff(f).length),volume=Math.max(15,Math.min(reachableRetailDemand(f),staff*80)),cost=f.unitCost?.food||marketPrice('food');
 return (cost+workerIncome(f)*staff/volume+.12)*(1.10+G.policy.businessRegulation*.0004);
}
function recordInventoryPurchase(f,good,qty,total){
 const held=(f.stock[good]||0)+pendingGoods(f,good);f.unitCost=f.unitCost||{};
 f.unitCost[good]=((f.unitCost[good]||marketPrice(good))*held+total)/Math.max(.001,held+qty);
 f.purchases=(f.purchases||0)+total;f.cashFlow=(f.cashFlow||0)-total;
}
function takeInventory(f,good,qty,sold=false){
 qty=Math.min(Math.max(0,qty),f.stock[good]||0);f.stock[good]=(f.stock[good]||0)-qty;
 const cost=qty*(f.unitCost?.[good]??marketPrice(good));
 if(sold){if(marketOpen){f.cogs=(f.cogs||0)+cost;f.salesQty=(f.salesQty||0)+qty;}else{f.pendingCogs=(f.pendingCogs||0)+cost;f.pendingSalesQty=(f.pendingSalesQty||0)+qty;}}
 return cost;
}
function marketOutputPrice(f,good){return f.ask?.[good]||marketPrice(good);}
function planEnterprise(f){
 if(f.closed)return;
 const wage=workerIncome(f),base=SECTOR_WORKERS[f.kind]||4,recipe=formulas[f.kind]?.out?formulas[f.kind]:null;
 if(f.kind==='grocer'){const target=foodRetailTarget(f);f.price=f.age<3?target:f.price*.93+target*.07;}
 if(recipe){
  const unitInputs=recipe.inp?(recipe.amount/recipe.qty)*(f.unitCost[recipe.inp]||marketPrice(recipe.inp)):0;
  const efficiency=recipe.qty/base*(f.kind==='farm'?1+Math.min(.9,(G.fieldCount?.[f.id]||0)*.035):1);
  const breakEven=unitInputs+wage/Math.max(1,efficiency)+.10;
  const target=Math.max(marketPrice(recipe.out)*.94,breakEven*1.16);
  f.ask[recipe.out]=(f.ask[recipe.out]||target)*.96+target*.04;
 }
 if(G.day%14!==0||f.age<28)return;
 // Inventories and realized orders guide labour demand; losses are not a dice roll.
 let desired=f.jobs;
 if(f.kind==='airport')desired=4+Math.ceil((G.airport?.dailyFlights||1)*1.5);
 else if(recipe){const perWorker=recipe.qty/base*(.88+G.education*.0015)*(f.kind==='farm'?1+Math.min(.9,(G.fieldCount?.[f.id]||0)*.035):1);
  desired=Math.ceil(Math.max(1,f.salesTrend)*1.12/Math.max(1,perWorker));
 }else if(f.kind==='grocer')desired=Math.ceil(Math.max(1,f.salesTrend)/65);
 else desired=Math.ceil(Math.max(0,f.revenueTrend-f.cogs*.2)/(wage*1.45));
 desired=clamp(desired,1,Math.ceil(base*f.scale*2));
 if(f.marginTrend<-.18&&f.cash<wage*Math.max(1,f.jobs)*60)desired=Math.min(desired,Math.max(1,f.jobs-1));
 if(desired>f.jobs&&f.cash<wage*(desired-f.jobs)*35+1800)desired=f.jobs;
 if(desired!==f.jobs){f.jobs+=Math.sign(desired-f.jobs);while(f.workers.length>f.jobs){const blocked=f.workers.findIndex(id=>!workerCanCommute(G.people[id],f)),id=f.workers.splice(blocked<0?f.workers.length-1:blocked,1)[0];if(G.people[id])G.people[id].job=-1;}}
 if((f.kind!=='fishery'||!f.fishingWaterLimit)&&f.workers.some(id=>workerCanCommute(G.people[id],f))&&!f.pendingEquipment&&f.marginTrend>.16&&f.cash>wage*f.jobs*100&&f.scale<2.2&&(recipe?f.ratedOutput>0&&f.salesTrend*1.12>=f.ratedOutput&&(!recipe.inp||(f.stock[recipe.inp]||0)+pendingGoods(f,recipe.inp)>=recipe.amount*f.workers.length/base):f.jobs>=Math.ceil(base*f.scale*2)&&f.workers.length>=f.jobs)){const cost=1500+base*130,annualGain=f.revenueTrend*.015*360*(1-G.policy.profitTax/100);if(f.cash>cost+6000&&annualGain>cost*((G.policy.policyRate||0)/100+.08)){f.cash-=cost;G.region+=cost;f.pendingEquipment={gain:.06,cost,ordered:G.day,ready:G.day+30};f.capex=(f.capex||0)+cost;}}
 const unemployment=G.stats.unemployment||0;
 if(f.marginTrend>.18&&unemployment<9)f.wage=Math.min(80,f.wage*1.0015);
 else if(f.marginTrend<0)f.wage=Math.max(G.policy.minWage,f.wage*.998);
}
function enterpriseRevenue(f,amount){f.cash+=amount;if(marketOpen)f.revenue+=amount;else f.pendingRevenue=(f.pendingRevenue||0)+amount;}
function serviceSales(f,amount){
 amount=Math.min(Math.max(0,G.region),Math.max(0,amount));G.region-=amount;f.cash+=amount;f.revenue+=amount;G.market.externalSales+=amount;return amount;
}
function fundedPublicPayroll(amount,share=.65,eligible=null,role=''){
 const paid=Math.max(0,Math.min(G.treasury,amount));G.treasury-=paid;G.cumulative.spending+=paid;
 let payroll=paid*share,spent=0,wage=Math.max(24,G.policy.minWage);
 const available=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.age>=18&&p.age<=70&&p.job<0&&(p.publicIncome||0)<wage&&(eligible?eligible(p):!p.previousPublicRole));
 for(const p of available){if(payroll<.001)break;const h=G.households[p.hh];if(!h?.people.length)continue;const pay=Math.min(payroll,wage-(p.publicIncome||0));const tax=pay*G.policy.incomeTax/100;h.cash+=pay-tax;h.income+=pay;h.wages=(h.wages||0)+pay;h.tax+=tax;h.incomeTax+=tax;transferTreasury(tax,'incomeTax');p.publicIncome=(p.publicIncome||0)+pay;p.publicWork=p.publicIncome>=wage*.5;if(role)p.publicRole=role;payroll-=pay;spent+=pay;}
 G.region+=paid-spent;return amount>0?paid/amount:0;
}
// Explicit operating standards, expressed in the same resident capacities used
// by the existing facilities. Five clinic teams cover 350 residents; ten school
// staff cover 260. The public wage and existing 65% payroll share price the work;
// remaining purchases pay regional staff/suppliers, including when locals work.
const CIVIC_STANDARDS={health:{building:'clinic',capacity:350,staff:5},school:{building:'school',capacity:260,staff:10}};
function purchaseCivicService(kind,authorized){
 const standard=CIVIC_STANDARDS[kind],population=Math.max(0,G.stats.population),facilities=G.buildings.filter(b=>b.kind===standard.building).length;
 const wage=Math.max(24,G.policy.minWage),required=population*standard.staff/standard.capacity*wage/.65;
 const facilityCoverage=population?Math.min(1,facilities*standard.capacity/population):0;
 const access=serviceAccess(kind),staffing=civicStaffCapacity(kind,authorized,access),requested=Math.min(Math.max(0,authorized),required*Math.min(access.coverage,staffing.coverage)),paid=requested*fundedPublicPayroll(requested,.65,p=>qualifiedForService(p,kind)&&civicCandidateSets.get(kind).has(p.id),kind);
 const coverage=required?Math.min(access.coverage,paid/required):0;
 const result={day:G.day,authorized,required,requested,paid,unspent:Math.max(0,authorized-paid),population,facilities,facilityCoverage,accessCoverage:access.coverage,accessLimit:access.limit,accessibleResidents:access.served,staffing,coverage,wage};
 if(!G.serviceProvision)G.serviceProvision={};G.serviceProvision[kind]=result;
 return coverage;
}
function restartViableEnterprise(){
 if(G.day%30!==0||G.region<70000)return;
 const open=G.firms.filter(f=>!f.closed),population=G.stats.population;
 const desired={grocer:Math.ceil(population/100),farm:Math.ceil(population/100),mill:Math.ceil(population/220),bakery:Math.ceil(population/140),office:Math.ceil(population/120),factory:Math.ceil(population/240),contractor:Math.ceil(population/180),tavern:Math.ceil(population/160),forestry:1,sawmill:1,quarry:1,warehouse:Math.ceil(population/300)};
 const counts={};for(const f of open)counts[f.kind]=(counts[f.kind]||0)+1;
 for(const f of G.firms){if(!f.closed||!readBuild(f.building)||G.day-(f.closedDay||0)<120||(counts[f.kind]||0)>=(desired[f.kind]||1))continue;
  // An investment must clear a return hurdle and afford the actual legal payroll.
  const base=SECTOR_WORKERS[f.kind]||3,wage=Math.max(G.policy.minWage,28),recipe=formulas[f.kind]?.out?formulas[f.kind]:null;
  const perWorkerRevenue=recipe?recipe.qty/base*marketPrice(recipe.out)-(recipe.amount||0)/base*marketPrice(recipe.inp):f.kind==='grocer'?65*(foodRetailTarget({...f,jobs:2})-marketPrice('food')):48;
  const expected=perWorkerRevenue-wage*(1+G.policy.businessRegulation*.003);
  const capital=6000+wage*base*45+G.policy.permitFee;
  if(expected*base*360*(1-G.policy.profitTax/100)<=capital*((G.policy.policyRate||0)/100+.08)||G.policy.permitFee>1600)continue;
  if(G.region<capital+50000)continue;
  const owner=G.households[f.owner];if(owner)owner.cash+=f.cash;else G.region+=f.cash;
  G.region-=capital;f.cash=capital-G.policy.permitFee;transferTreasury(G.policy.permitFee,'permits');f.closed=false;f.closedDay=0;f.strain=0;f.lossDays=0;f.jobs=base;f.wage=wage;f.marginTrend=.1;f.reopenedDay=G.day;f.workingCapitalRaised+=capital;G.market.privateRestartCapital+=capital;
  story('Investors reopened '+f.name+' after a demand and operating-margin review.','good',f.building);assignJobs();return;
 }
}

// SOURCE: 10-finance.js
function ensureFinance(){
 if(!G)return;
 if(!Array.isArray(G.banks))G.banks=[];
 if(!Array.isArray(G.loans))G.loans=[];
 if(!G.finance)G.finance={failures:0,businessDefaults:0,householdDefaults:0,creditIssued:0,depositLosses:0,insuredPayouts:0,foreclosures:0,downzonings:0,insolvencies:0,bankRuns:0};
 for(const h of G.households){if(!h.deposits||typeof h.deposits!=='object'||Array.isArray(h.deposits))h.deposits={};if(!Number.isFinite(h.creditScore))h.creditScore=.65;}
 for(const f of G.firms){if(!Number.isFinite(f.creditScore))f.creditScore=.68;if(!Number.isFinite(f.lossDays))f.lossDays=0;}
}
function seedBanks(){
 ensureFinance();if(G.banks.length)return;
 const capital=[34000,29000,26000],depositAPY=[.016,.024,.031],loanAPY=[.071,.085,.109];
 for(let i=0;i<3;i++){const equity=Math.min(capital[i],Math.max(0,G.region-50000));G.region-=equity;
  G.banks.push({id:i,name:FIN_BANK_NAMES[i],cash:equity,depositAPY:depositAPY[i],loanAPY:loanAPY[i],closed:false,runDays:0,losses:0,interestEarned:0,interestPaid:0,loansOriginated:0});
 }
 // Voluntary deposits: cash leaves household wallets and enters bank vaults.
 for(const h of G.households){const b=G.banks[h.id%3];const amount=Math.max(0,Math.min(h.cash,Math.round(h.cash*(.08+(h.id%5)*.055))));
  h.cash-=amount;b.cash+=amount;h.deposits[b.id]=amount;
 }
}
function bankDeposits(bankId){let n=0;for(const h of G.households)n+=Math.max(0,h.deposits?.[bankId]||0);for(const f of G.firms)n+=Math.max(0,f.deposits?.[bankId]||0);return n}
function bankLoans(bankId){return G.loans.filter(l=>l.bankId===bankId&&l.status==='active').reduce((n,l)=>n+l.balance,0)}
function bankEquity(b){return b.cash+(b.regionCredit||0)+bankLoans(b.id)-bankDeposits(b.id)}
function availableBank(b){const reserve=Math.max(bankDeposits(b.id)*((G.policy.bankReserve??12)/100),Math.max(0,bankEquity(b))*.30);return Math.max(0,b.cash-reserve)}
function bestBank(loan=false){return G.banks.filter(b=>!b.closed&&availableBank(b)>3500&&bankEquity(b)>1000).sort((a,b)=>loan?a.loanAPY-b.loanAPY:b.depositAPY-a.depositAPY)[0]||null}
function bankLoan(kind,id,amount,term=360){
 ensureFinance();if(!['firm','household'].includes(kind)||!Number.isFinite(amount)||amount<=0||!Number.isInteger(term)||term<30||term>3600)return null;let owner=kind==='firm'?G.firms[id]:G.households[id];if(!owner||owner.closed)return null;const decline=reason=>{owner.creditDecision={day:G.day,requested:amount,approved:false,reason};return null;};
 if(G.loans.some(l=>l.status==='active'&&l.ownerType===kind&&l.ownerId===id))return decline('An active loan already finances this borrower');
 const strict=(G.policy.lendingRules??35)/100;const score=clamp(owner.creditScore??.65,.05,.99);
 const ratio=kind==='firm'?amount/Math.max(1,owner.cash+1500):amount/Math.max(1,owner.cash+(owner.deposits?Object.values(owner.deposits).reduce((a,v)=>a+v,0):0));
 if(amount<100)return decline('Requested advance is below the lending minimum');if(score<.32+strict*.25)return decline('Credit standing does not meet current lending standards');if(ratio>7.8-strict*3.2)return decline('Request exceeds the borrower liquidity limit');
 const b=G.banks.filter(b=>!b.closed&&availableBank(b)>=amount*1.20&&bankEquity(b)>amount*.08).sort((a,b)=>a.loanAPY-b.loanAPY)[0];if(!b)return decline('No bank has sufficient lendable reserves and equity');
 const rate=b.loanAPY+strict*.022+(1-score)*.055;const assessment=assessCredit(kind,owner,amount,term,rate);owner.creditDecision={day:G.day,requested:amount,...assessment};if(!assessment.approved)return null;
 b.cash-=amount;owner.cash+=amount;
 const loan={id:(G.nextLoanId= Math.max(G.nextLoanId||0,G.loans.length)+1),bankId:b.id,ownerType:kind,ownerId:id,original:amount,balance:amount,rate,spread:Math.max(.02,rate-(G.policy.policyRate||0)/100),fixedRate:false,term,created:G.day,arrears:0,status:'active',paid:0};
 G.loans.push(loan);b.loansOriginated++;G.finance.creditIssued+=amount;
 if(kind==='firm')owner.debt=(owner.debt||0)+amount;
 return loan;
}
function loanPayments(loans=G.loans){
 for(const l of loans){if(l.status!=='active'||l.balance<=0||l.lastPaymentDay===G.day)continue;l.lastPaymentDay=G.day;
  const owner=l.ownerType==='firm'?G.firms[l.ownerId]:G.households[l.ownerId];if(!owner){l.status='default';l.defaultedDay=G.day;continue;}
  const lender=l.bankId<0?null:G.banks[l.bankId];
  if(G.day%30===0&&l.fixedRate!==true){const benchmark=(G.policy.policyRate||0)/100,spread=l.spread??Math.max(.025,l.rate-.03);l.spread=spread;l.rate=l.rate*.75+(benchmark+spread)*.25;}
  const interest=l.balance*l.rate/360;
  const minPrincipal=Math.min(l.balance,l.original/Math.max(30,l.term));
  const due=minPrincipal+interest;l.scheduledDue=due;owner.debtDue=(owner.debtDue||0)+due;
  // Borrowers cannot pay more than cash. Failed firms cannot create repayment funds.
  if(l.ownerType==='household'&&owner.cash<due)for(const [id,deposit] of Object.entries(owner.deposits||{})){withdrawal(owner,G.banks[+id],Math.min(deposit,due-owner.cash));if(owner.cash>=due)break;}
  const paid=Math.min(Math.max(0,owner.cash),due);
  const paidInterest=Math.min(paid,interest),paidPrincipal=Math.max(0,paid-paidInterest);
  owner.cash-=paid;if(l.ownerType==='household')owner.debtService=(owner.debtService||0)+paid;if(lender&&!lender.closed){lender.cash+=paid;lender.interestEarned+=paidInterest}else G.region+=paid;
  l.paidToday=paid;
  l.balance=Math.max(0,l.balance-paidPrincipal+(interest-paidInterest));l.paid+=paid;
  if(l.ownerType==='firm'){owner.debt=Math.max(0,(owner.debt||0)-paidPrincipal+(interest-paidInterest));owner.expenses=(owner.expenses||0)+interest;}
  if(paid<due*.8){l.arrears++;owner.creditScore=clamp(owner.creditScore-.004,.08,.99);}else {l.arrears=Math.max(0,l.arrears-1);owner.creditScore=clamp(owner.creditScore+.0004,.08,.99);}
  if(l.balance<.01){l.balance=0;l.status='repaid';if(l.ownerType==='firm')owner.debt=0;}
  else if(l.arrears>=95||owner.closed&&l.arrears>=12){
   l.status='default';l.defaultedDay=G.day;if(l.ownerType==='firm'){owner.debt=Math.max(0,(owner.debt||0)-l.balance);G.finance.businessDefaults++;}
   else G.finance.householdDefaults++;
   if(lender&&!lender.closed)lender.losses+=l.balance;
   owner.creditScore=clamp(owner.creditScore-.22,.05,.99);
   story((l.ownerType==='firm'?owner.name:'The '+owner.name+' household')+' defaulted on a bank loan of '+money(l.balance)+'.','bad',l.ownerType==='firm'?owner.building:owner.home);
  }
 }
}
function depositTransfer(h,b,amount){
 if(!b||b.closed||amount<=0)return 0;amount=Math.max(0,Math.min(h.cash,amount));h.cash-=amount;b.cash+=amount;h.deposits[b.id]=(h.deposits[b.id]||0)+amount;return amount;
}
function withdrawal(h,b,amount){
 if(!b||b.closed||amount<=0)return 0;
 // Redeem the bank's own marketable securities at par before denying cash withdrawals.
 const requested=Math.min(amount,h.deposits?.[b.id]||0),redeem=Math.min(Math.max(0,requested-b.cash),b.regionCredit||0,Math.max(0,G.region));
 if(redeem>0){G.region-=redeem;b.cash+=redeem;b.regionCredit-=redeem;}
 amount=Math.min(requested,b.cash);
 h.deposits[b.id]-=amount;b.cash-=amount;h.cash+=amount;return amount;
}
function liquidateBank(b,reason='Insolvent balance sheet'){
 if(b.closed)return;const claims=bankDeposits(b.id);
 b.closed=true;G.finance.failures++;
 // A failed bank's loan assets are sold to regional creditors for a conservative
 // haircut; the cash price funds the receivership. Region receives loan rights.
 let transferred=0;for(const l of G.loans){if(l.bankId!==b.id||l.status!=='active')continue;
  const purchase=Math.min(G.region,Math.max(0,l.balance*.35));G.region-=purchase;b.cash+=purchase;
  l.bankId=-1;transferred++;
 }
 if((b.regionCredit||0)>0){const value=b.regionCredit;const sale=Math.min(G.region,value*.83);G.region-=sale;b.cash+=sale;b.regionCredit=0;}
 const liquidCash=Math.max(0,b.cash),uninsured=clamp(G.policy.depositGuarantee??0,0,100)/100;
 const recovery=claims>0?Math.min(1,liquidCash/claims):1;
 let losses=0,payout=0;
 for(const entity of [...G.households,...G.firms]){
  if(!entity.deposits)continue;const claim=Math.max(0,entity.deposits[b.id]||0);if(!claim)continue;
  const recovered=claim*recovery,shortfall=claim-recovered;
  entity.cash+=recovered;b.cash-=recovered;payout+=recovered;entity.deposits[b.id]=0;
  // A deposit guarantee pays against a quantified loss from municipal funds,
  // not freshly invented reserves. Insufficient budget leaves uncovered losses.
  const insured=Math.min(shortfall*uninsured,G.treasury);
  G.treasury-=insured;entity.cash+=insured;G.finance.insuredPayouts+=insured;
  losses+=shortfall-insured;
 }
 G.finance.depositLosses+=losses;
 G.region+=Math.max(0,b.cash);b.cash=0;
 story(b.name+' entered receivership: '+reason+'. Depositor losses '+money(losses)+', '+transferred+' loans sold to regional lenders.','bad');
}
function regionalCapitalMarket(){
 // Depositor-backed private investment and municipal savings purchase bonds
 // in the outside trading region. Bonds remain assets on lender balance sheets;
 // cash actually moves to the region to finance demand for local exports.
 if(!G||!G.banks)return;
 G.publicReserve=Number.isFinite(G.publicReserve)?G.publicReserve:0;
 for(const b of G.banks){if(b.closed)continue;
  const due=(b.regionCredit||0)*.037/360;
  const paid=Math.min(due,Math.max(0,G.region));
  G.region-=paid;b.cash+=paid;b.interestEarned+=paid;
  if(paid+1e-6<due)b.regionArrears=(b.regionArrears||0)+(due-paid);
  else b.regionArrears=Math.max(0,(b.regionArrears||0)-paid*.15);
 }
 const publicInterest=Math.min(G.region,G.publicReserve*.024/360);
 G.region-=publicInterest;G.treasury+=publicInterest;
 if(G.day%30!==0)return;
 const targetRegion=3500000;
 // Local savings reach external borrowers only when credit is required.
 if(G.region<targetRegion){
  const fraction=clamp((G.policy.treasuryInvestment??60)/100,0,1);
  const invest=Math.max(0,Math.min(210000,(G.treasury-240000)*.30*fraction,targetRegion-G.region));
  if(invest>200){G.treasury-=invest;G.region+=invest;G.publicReserve+=invest;}
  for(const b of G.banks){if(b.closed)continue;
   const claims=bankDeposits(b.id);
   const minimumCash=Math.max(9000,claims*.42);
   const limit=Math.max(0,claims*.54-(b.regionCredit||0));
   const amount=Math.max(0,Math.min(180000,b.cash-minimumCash,limit,targetRegion-G.region));
   if(amount>1000&&bankEquity(b)>claims*.015){b.cash-=amount;b.regionCredit=(b.regionCredit||0)+amount;G.region+=amount;}
  }
 }else if(G.region>targetRegion+1200000){
  // Bond market repayments are actual transfers, not asset write-offs.
  for(const b of G.banks){if(b.closed||!b.regionCredit)continue;
   const redeem=Math.min(b.regionCredit*.10,G.region-(targetRegion+500000));
   if(redeem>0){b.regionCredit-=redeem;G.region-=redeem;b.cash+=redeem;}
  }
 }
 if(G.treasury<25000&&G.publicReserve>0&&G.region>75000){
  const redeem=Math.min(G.publicReserve,85000,G.region-50000);G.publicReserve-=redeem;G.region-=redeem;G.treasury+=redeem;
 }
}
function bankCompetition(){
 if(G.day%15!==0)return;
 // Rates are quoted independently. Liquidity, credit demand, regulation and
 // default histories affect spreads, allowing depositors and borrowers to shop.
 for(const b of G.banks){if(b.closed)continue;
  const deposits=bankDeposits(b.id),liquid=deposits>0?b.cash/deposits:1;
  const stress=Math.max(0,1.25-liquid);
  const demand=clamp((G.stats.businesses||20)/80,0,.6);
  const risk=clamp((G.policy.lendingRules??35)/100,0,1);
  const exposure=G.loans.filter(l=>l.bankId===b.id),active=exposure.filter(l=>l.status==='active'),arrears=active.reduce((n,l)=>n+l.balance*clamp(l.arrears/95,0,1),0),recentLoss=exposure.filter(l=>l.status==='default'&&l.defaultedDay>=(b.createdDay||0)&&G.day-l.defaultedDay<360).reduce((n,l)=>n+l.balance,0);
  const creditRisk=clamp((arrears+recentLoss)/Math.max(1,active.reduce((n,l)=>n+l.balance,0)+recentLoss),0,1);b.creditRisk=creditRisk;
  const targetLoan=clamp((G.policy.policyRate||0)/100+.022+(b.id%3)*.004+risk*.018+stress*.025+demand*.008+creditRisk*.04,.018,.34);
  b.loanAPY=b.loanAPY*.72+targetLoan*.28;
  const targetDeposit=clamp((G.policy.policyRate||0)/100*.78+.002+(b.id%3)*.001+stress*.004,.001,.18);
  b.depositAPY=b.depositAPY*.75+targetDeposit*.25;
 }
}
function bankMarketEntry(){
 if(G.day%90!==0||G.region<100000)return false;
 const operating=G.banks.filter(b=>!b.closed);
 const population=G.stats.population||0;
 if(operating.length>=3&&(population<700||operating.length>=4))return false;
 if(operating.length>=2&&(G.stats.marketConfidence||50)<36)return false;
 const initial=25000+Math.min(15000,Math.max(0,population-350)*14);
 if(G.region<initial+50000)return false;
 G.region-=initial;
 const retired=G.banks.find(b=>b.closed);const id=retired?retired.id:G.banks.length;
 const names=['Riverside Savings & Loan','County Agricultural Credit','Broadway Commercial Bank','East Bank Mutual','Cooperative Industrial Bank','Western Exchange Bank'];
 const bank={id,name:names[((G.finance.failures||0)+id)%names.length],cash:initial,depositAPY:.027,loanAPY:.081,closed:false,runDays:0,losses:0,interestEarned:0,interestPaid:0,loansOriginated:0,createdDay:G.day};
 if(retired)G.banks[id]=bank;else G.banks.push(bank);
 let branch=G.buildings.find(b=>b.kind==='bank'&&(b.bankId===retired?.id||G.banks[b.bankId]?.closed));
 if(!branch){const candidates=buildableCandidates('business');let place=candidates[0];if(place){branch={id:G.nextId++,kind:'bank',x:place.x,y:place.y,value:75000,condition:100,owner:-1,firm:-1,hh:-1};G.buildings.push(branch);invalidateRoads(false);}}
 if(branch)branch.bankId=id;
 staticDirty=true;dirty=true;
 story(bank.name+' opened after raising '+money(initial)+' in subscribed regional capital. Depositors now have another choice.','good',branch?.id||0);
 return true;
}
function bankDaily(){
 ensureFinance();loanPayments(G.loans.filter(l=>l.ownerType==='firm'||!G.households[l.ownerId]?.people.length));regionalCapitalMarket();bankCompetition();bankMarketEntry();
 // Keep fulfilled and defaulted loan history bounded; active loans are never discarded.
 if(G.loans.length>2500){const past=G.loans.filter(l=>l.status!=='active');const removable=new Set(past.slice(0,Math.max(0,G.loans.length-1800)).map(l=>l.id));if(removable.size)G.loans=G.loans.filter(l=>!removable.has(l.id));}

 // Overnight funds deposited with the regional clearing market earn a floating yield.
 // Every dollar of interest is paid by that counterparty; no currency is minted.
 for(const b of G.banks){if(b.closed)continue;const yieldRate=clamp((G.policy.policyRate||0)/100*.85,.001,.17);const earnings=Math.min(G.region,b.cash*yieldRate/360);G.region-=earnings;b.cash+=earnings;b.interestEarned+=earnings;}
 for(const bank of G.banks){if(bank.closed)continue;const expense=Math.min(bank.cash,4+G.loans.filter(l=>l.bankId===bank.id&&l.status==='active').length*.22);bank.cash-=expense;const beneficiaries=G.households.filter(h=>h.people.length>0);if(beneficiaries.length){let worker=beneficiaries[(G.day+bank.id*17)%beneficiaries.length];worker.cash+=expense*.7;worker.income+=expense*.7;worker.serviceReceipts=(worker.serviceReceipts||0)+expense*.7;G.region+=expense*.3;}else G.region+=expense;}
 for(const b of G.banks){if(b.closed)continue;
  // Interest accrues daily to depositors as a claim on bank assets.
  // It is capped by the bank's non-impaired equity to avoid uncontrolled negative values.
  const claims=bankDeposits(b.id),cap=Math.max(0,bankEquity(b));
  const interest=Math.min(claims*b.depositAPY/360,cap*.012);
  if(interest>0&&claims>0){for(const entity of [...G.households,...G.firms]){const bal=entity.deposits?.[b.id]||0;if(bal>0)entity.deposits[b.id]+=interest*bal/claims;}
   b.interestPaid+=interest;}
 }
 // Withdrawal/deposit decisions are monthly rather than per-frame.
 if(G.day%30===0){
  for(const h of G.households){if(!h.people.length)continue;const deposited=Object.values(h.deposits||{}).reduce((a,v)=>a+v,0);
   const need=Math.max(0,Math.min(deposited,h.people.length*30-h.cash));
   if(need>0){let remaining=need;const balances=Object.entries(h.deposits).sort((a,b)=>b[1]-a[1]);for(const [id] of balances){if(remaining<=.001)break;remaining-=withdrawal(h,G.banks[+id],remaining);}}
   else if(h.cash>Math.max(900,h.people.length*600)){
    const bank=G.banks.filter(b=>!b.closed&&bankEquity(b)>0).sort((a,b)=>b.depositAPY-a.depositAPY)[0];
    if(bank)depositTransfer(h,bank,(h.cash-h.people.length*500)*.18);
   }
  }
  for(const b of G.banks){if(b.closed)continue;
   // Defaults deteriorate solvency. A reserve shortage generates withdrawals
   // only if confidence is already low, making runs endogenous, not arbitrary.
   const claims=bankDeposits(b.id);
   // A solvent institution first sells liquid regional assets, then seeks private equity.
   const redemption=Math.min(Math.max(0,claims*.25-b.cash),b.regionCredit||0,G.region);
   if(redemption>0){b.regionCredit-=redemption;G.region-=redemption;b.cash+=redemption;}
   const capital=bankEquity(b);
   const liquid=claims>0?b.cash/claims:1;
   const requiredEquity=Math.max(2200,claims*.035);
   if(capital>=0&&capital<requiredEquity&&liquid>.25&&G.region>requiredEquity+50000){
    const issue=Math.min(50000,requiredEquity-capital+1500,G.region*.05);
    G.region-=issue;b.cash+=issue;b.equityRaised=(b.equityRaised||0)+issue;
    if(G.day%360===0)story(b.name+' raised '+money(issue)+' in new private equity to strengthen depositor protection.','neutral');
   }
   if(capital<0||liquid<(G.policy.bankReserve??12)/180){b.runDays++;
    const panic=clamp((.16-liquid)*.4+(claims*.03-capital)/Math.max(1,claims)*.5,0,.15);
    if(panic>.005){for(const h of G.households){const d=h.deposits?.[b.id]||0;if(d>0)withdrawal(h,b,d*panic);}
     G.finance.bankRuns++;}
   }else b.runDays=Math.max(0,b.runDays-1);
   if(bankEquity(b)<-100||(b.runDays>=12&&b.cash<claims*.06)||claims>0&&b.cash<1&&b.runDays>=4)liquidateBank(b,capital<0?'Loan losses exceeded capital':'Sustained deposit withdrawals');
  }
 }
 // Struggling companies can apply for a genuinely funded line of credit.
 if(G.day%60===0){
  const candidate=G.households.filter(h=>h.people.length>0&&h.cash<120&&h.creditScore>.6&&h.worklessness<20).sort((a,b)=>a.cash-b.cash).slice(0,2);
  for(const h of candidate)bankLoan('household',h.id,Math.round(400+h.people.length*210),150);
 }
 if(G.day%35===0){const s=G.firms.filter(f=>!f.closed&&f.cash<2800&&f.age>35&&f.lossDays<14&&f.profit> -45&&f.strain<18&&f.creditScore>.56)
   .sort((a,b)=>a.cash-b.cash).slice(0,Math.max(2,Math.ceil(G.firms.length*.08)));
  for(const f of s){const loan=bankLoan('firm',f.id,Math.round(clamp(6800-f.cash,2300,6500)),420);
   if(loan)story(f.name+' received '+money(loan.original)+' of working-capital credit from '+G.banks[loan.bankId].name+'.','neutral',f.building);
  }
 }
}
function liquidateFirm(f,reason){
 // Insolvent companies dispose of stock/equipment, pay secured creditors, and
 // distribute only the residual to shareholders. Assets cannot pay twice.
 if(!f||f.closed)return false;
 const site=readBuild(f.building);
 const stockValue=Object.entries(f.stock||{}).reduce((n,[key,value])=>n+Math.max(0,value)*(goods[key]||1),0);
 const salvage=Math.max(0,Math.min(G.region,stockValue*.18+(site?.value||0)*.015));
 G.region-=salvage;f.cash+=salvage;
 for(const l of G.loans){if(l.ownerType!=='firm'||l.ownerId!==f.id||l.status!=='active')continue;
  const amount=Math.min(Math.max(0,f.cash),Math.max(0,l.balance));
  f.cash-=amount;l.balance=Math.max(0,l.balance-amount);l.paid+=amount;
  const bank=l.bankId>=0?G.banks[l.bankId]:null;
  if(bank&&!bank.closed)bank.cash+=amount;else G.region+=amount;
  if(l.balance<.01){l.balance=0;l.status='repaid';}
  else {l.status='default';l.defaultedDay=G.day;G.finance.businessDefaults++;if(bank&&!bank.closed)bank.losses+=l.balance;f.creditScore=clamp((f.creditScore||.6)-.20,.05,.99);}
 }
 const residual=Math.max(0,f.cash);f.cash=0;f.debt=0;
 const shareholder=G.households[f.owner];if(shareholder)shareholder.cash+=residual;else G.region+=residual;
 for(const [good,qty] of Object.entries(f.stock))goodsEntry(good,'exports',qty);
 f.stock={};f.closed=true;f.closedDay=G.day;G.finance.insolvencies++;
 for(const id of f.workers)if(G.people[id])G.people[id].job=-1;
 f.workers=[];
 story(f.name+' entered liquidation: '+reason+'. Creditors received asset proceeds before shareholders.','bad',f.building);
 return true;
}
function liquidityStress(){
 // Firms go bankrupt after actual negative operating history and persistent
 // inability to satisfy creditors, not from a random destruction roll.
 for(const f of G.firms){if(f.closed)continue;
  if(f.profit<0&&f.cash<3000)f.lossDays++;else f.lossDays=Math.max(0,(f.lossDays||0)-2);
  if(f.lossDays>68&&f.cash<360)liquidateFirm(f,f.lossDays+' consecutive financially weak days');
 }
}
function outwardMigration(){
 if(G.day%30!==0)return 0;
 const hardship=G.stats.hardship||0,unemployment=G.stats.unemployment||0;
 if(hardship<25&&unemployment<26&&(G.regionalDemand||1)>.68)return 0;
 const chance=clamp(.035+Math.max(0,hardship-25)*.004+Math.max(0,unemployment-26)*.003,0,.27);
 if(random()>chance)return 0;
 const choices=G.households.filter(h=>h.home>=0&&h.people.length>0&&h.stress>42&&h.cash<Math.max(550,h.people.length*260))
  .sort((a,b)=>(b.stress-a.stress)+(a.cash-b.cash)*.005);
 if(!choices.length)return 0;
 const h=choices[0],oldHome=readBuild(h.home),departures=h.people.slice();
 for(const id of departures){const p=G.people[id];if(!p)continue;p.movedAway=true;p.job=-1;
  for(const f of G.firms)if(f.workers.includes(id))f.workers=f.workers.filter(n=>n!==id);
 }
 h.people=[];
 // External migrants take cash with them. Their remaining bank deposits are
 // still real liabilities to external depositors, not municipal residents.
 G.region+=Math.max(0,h.cash);h.cash=0;
 story('The '+h.name+' family left town after persistent hardship and weak job prospects, leaving a vacant home.','bad',oldHome?.id||0);
 recompute();return departures.length;
}
function reverseRedevelopment(){
 if(G.day%60!==0||!G.autoBuild)return false;
 const d=cityDemand();
 // Building owners react to actual vacancy and declining values. A tower will
 // not be razed while families still depend on its units.
 if(d.housingPressure>42||d.homeDemand>12)return false;
 const towers=G.buildings.filter(b=>['tower','apartment'].includes(b.kind)&&!b.redevelopment&&
   !G.projects.some(p=>p.id===b.id));
 for(const b of towers){
  const occupied=(b.units||[]).map(id=>G.households[id]).filter(h=>h&&h.home===b.id&&h.people.some(id=>!G.people[id]?.deceased&&G.people[id]?.movedAway!==true));
  if(occupied.length>1)continue;
  if((G.day-(b.lastRedeveloped||0))<480)continue;
  const cost=b.kind==='tower'?48000:19000;
  if(G.region<cost+30000)continue;
  // Owner pays demolition and conversion; no residents disappear.
  privateContract(cost);
  const sole=occupied[0];const formerUnits=(b.units||[]).slice();b.kind='home';b.footprint=[roadId(b.x,b.y)];invalidateBuildingIndex();invalidateRoads(false);b.units=[];b.hh=sole?.id??-1;b.value=Math.max(35000,Math.round(b.value*.28));b.replacedKind='tower';b.lastRedeveloped=G.day;
  for(const hid of formerUnits){const household=G.households[hid];if(household&&household.id!==sole?.id&&household.home===b.id)household.home=-1;}
  if(sole){sole.home=b.id;if(!G.homes.includes(b.id))G.homes.push(b.id)}
  G.finance.downzonings++;G.development.downzonings=(G.development.downzonings||0)+1;
  staticDirty=true;dirty=true;
  story('Vacancy and falling land values led a developer to replace an underused high-rise with a single residence.','neutral',b.id,b.hh);
  return true;
 }
 return false;
}
function financePanel(){
 ensureFinance();const active=G.loans.filter(l=>l.status==='active');
 const deposits=G.banks.reduce((n,b)=>n+bankDeposits(b.id),0),credit=active.reduce((n,l)=>n+l.balance,0);
 return head('Banking and credit markets')+tip('Banks compete for deposits and make loans from actual available cash. Firms can fail after losses and debt defaults; banks can enter receivership following asset losses and withdrawals. Deposits are liabilities, not extra money.')+
 `<div class="statgrid">${stat('Household deposits',money(deposits))}${stat('Outstanding credit',money(credit))}${stat('Operating banks',G.banks.filter(b=>!b.closed).length+' / '+G.banks.length)}${stat('Bank failures',G.finance.failures)}${stat('Business insolvencies',G.finance.insolvencies)}${stat('Loan defaults',G.finance.businessDefaults+G.finance.householdDefaults)}${stat('Depositor losses',money(G.finance.depositLosses))}${stat('Converted towers',G.finance.downzonings)}</div>`+
 head('Competing institutions')+G.banks.map(b=>`<div class="council-card"><h3>${esc(b.name)} · ${b.closed?'IN RECEIVERSHIP':'OPEN'}</h3>${strip('Deposits owed',money(bankDeposits(b.id)))}${strip('Cash reserves',money(b.cash))}${strip('Loan portfolio',money(bankLoans(b.id)))}${strip('Regional securities',money(b.regionCredit||0))}${strip('Equity after impairments',money(bankEquity(b)))}${strip('Savings interest',Math.round(b.depositAPY*10000)/100+'% annual')}${strip('Base lending rate',Math.round(b.loanAPY*10000)/100+'% annual')}</div>`).join('')+
 head('Current debtors')+active.slice(0,24).map(l=>{const owner=l.ownerType==='firm'?G.firms[l.ownerId]:G.households[l.ownerId];return `<div class="entry"><strong>${esc(owner?.name||'Unknown debtor')}</strong><small> ${money(l.balance)} outstanding · ${(100*l.rate).toFixed(1)}% interest · ${esc(G.banks[l.bankId]?.name||'Regional creditor')}</small></div>`}).join('')+
 head('Municipal savings')+strip('Public regional-bond holdings',money(G.publicReserve||0))+strip('Liquid municipal cash',money(G.treasury))+head('Financial history')+miniChart('deposits')+tip('Council policies influence reserve requirements, credit standards and whether public funds insure part of the deposits lost in a bank liquidation. Bank failures are possible without being guaranteed.');
}


// SOURCE: 12-service-access.js
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

// SOURCE: 13-civic-staffing.js
const civicCandidateSets=new Map();
function qualifiedForService(p,kind){return !p.deceased&&!p.movedAway&&p.age>=18&&p.age<=70&&p.health>=60&&p.skill>=(kind==='health'?.7:.55)&&(!p.previousPublicRole||p.previousPublicRole===kind);}
function civicStaffCapacity(kind,authorized,access){
 const standard=CIVIC_STANDARDS[kind],wage=Math.max(24,G.policy.minWage),needed=G.stats.population*standard.staff/standard.capacity;
 const reachable=new Set(access.households.filter(h=>h.distance!=null).map(h=>h.id)),candidates=G.people.filter(p=>p.job<0&&qualifiedForService(p,kind)&&reachable.has(p.hh));civicCandidateSets.set(kind,new Set(candidates.map(p=>p.id)));
 const local=candidates.reduce((n,p)=>n+Math.max(0,1-(p.publicIncome||0)/wage),0);
 const demand=Math.min(needed*access.coverage,Math.max(0,authorized)*.65/wage),target=Math.max(0,demand-local);
 if(!G.civicStaffing)G.civicStaffing={};let contract=G.civicStaffing[kind];
 // Founding/migrated services inherit their operating arrangements. Subsequent
 // expansion must recruit, but regional contracts allow recovery without locals.
 if(!contract)contract=G.civicStaffing[kind]={ready:target,pending:null};
 if(contract.pending&&G.day>=contract.pending.day){contract.ready=contract.pending.target;contract.pending=null;}
 if(!contract.pending&&Math.abs(contract.ready-target)>.01)contract.pending={target,day:G.day+30};
 const available=Math.min(needed*access.coverage,local+contract.ready);
 return {local,regional:contract.ready,needed,coverage:needed?available/needed:0,pending:contract.pending?{...contract.pending}:null,qualification:kind==='health'?.7:.55};
}
function civicTrainingDay(coverage){
 if(G.civicTrainingLastDay===G.day)return;G.civicTrainingLastDay=G.day;
 if(!G.civicTraining)G.civicTraining=[];
 G.civicTraining=G.civicTraining.filter(c=>{const p=G.people[c.person];return p&&!p.deceased&&!p.movedAway&&p.age>=18&&p.age<=70;});
 const places=G.buildings.filter(b=>b.kind==='school').length*2;
 if(coverage>0&&G.serviceProvision?.school?.paid>0){
  for(const course of G.civicTraining.slice(0,places)){course.days+=localCivicCoverage('school',G.people[course.person].hh);if(course.days>=120){const p=G.people[course.person];p.skill=Math.min(1.3,p.skill+.1);course.complete=true;G.civicTrainingCompletions=(G.civicTrainingCompletions||0)+1;story(p.name+' completed a funded adult-training term. Qualification grows through sustained teaching, not an instant grant.','good',0,p.hh);}}
  G.civicTraining=G.civicTraining.filter(c=>!c.complete);
  const enrolled=new Set(G.civicTraining.map(c=>c.person));
  const access=serviceAccess('school'),reachable=new Set(access.households.filter(h=>h.served>0).map(h=>h.id));
  const candidates=G.people.filter(p=>reachable.has(p.hh)&&!p.deceased&&!p.movedAway&&p.age>=18&&p.age<=60&&p.skill<.7&&!enrolled.has(p.id)).sort((a,b)=>(a.job>=0)-(b.job>=0)||b.skill-a.skill||a.id-b.id);
  while(G.civicTraining.length<places&&candidates.length)G.civicTraining.push({person:candidates.shift().id,days:0,started:G.day});
 }
}
function validateCivicState(data){
 if(data.civicStaffing!=null){if(typeof data.civicStaffing!=='object'||Array.isArray(data.civicStaffing))return false;
  for(const [kind,c] of Object.entries(data.civicStaffing)){if(!['health','school'].includes(kind)||!c||!Number.isFinite(c.ready)||c.ready<0||c.ready>1000)return false;
   if(c.pending&&(!Number.isFinite(c.pending.target)||c.pending.target<0||c.pending.target>1000||!Number.isInteger(c.pending.day)||c.pending.day<1||c.pending.day>data.day+30))return false;}}
 if(data.civicTraining!=null){if(!Array.isArray(data.civicTraining)||data.civicTraining.length>data.people.length)return false;const seen=new Set();
  for(const c of data.civicTraining){if(!c||!Number.isInteger(c.person)||!data.people[c.person]||seen.has(c.person)||!Number.isFinite(c.days)||c.days<0||c.days>=120||!Number.isInteger(c.started)||c.started<1||c.started>data.day)return false;seen.add(c.person);}}
 if(data.civicTrainingLastDay!=null&&(!Number.isInteger(data.civicTrainingLastDay)||data.civicTrainingLastDay>data.day||data.civicTrainingLastDay<1))return false;
 return data.people.every(p=>[p.publicRole,p.previousPublicRole].every(role=>role==null||['','health','school'].includes(role)));
}
function civicTrainingPanel(){
 const courses=G.civicTraining||[];return head('Local qualifications and training')+tip('Each operating school offers two adult-training places. A term needs 120 equivalent funded teaching days and adds 10 skill points; partial coverage progresses more slowly. Regional staffing contracts provide a recovery path when no local qualified worker is available.')+(courses.length?courses.map(c=>{const p=G.people[c.person];return `<div class="entry"><strong>${esc(p.name)}</strong><small>${Math.floor(c.days)} / 120 funded days · Skill ${Math.round(p.skill*100)}/100</small><button data-house="${p.hh}">Inspect household</button></div>`;}).join(''):tip('No adult course is active. Fund reachable schools to open places.'));
}

// SOURCE: 14-credit-decisions.js
function foodPriceEstimate(){const shops=G.firms.filter(f=>!f.closed&&f.kind==='grocer'&&f.price>0);return shops.length?shops.reduce((n,f)=>n+f.price,0)/shops.length:(G.market?.baseFoodPrice||5.2);}
function openingHouseholdIncome(h){return h.people.reduce((sum,id)=>{const p=G.people[id];if(!p||p.deceased||p.movedAway)return sum;if(p.age>70)return sum+(G.policy.pensionDaily||0);const f=G.firms[p.job];return sum+(f&&!f.closed&&!p.commuteBlocked?workerIncome(f)*(1-G.policy.incomeTax/100):0);},0);}
function expectedHouseholdEssentials(h){
 if(Number.isFinite(h.essentialDueTrend))return h.essentialDueTrend;
 const home=readBuild(h.home),rent=home?.owner===h.id||h.temporaryHousing?0:h.people.length*(3.1+G.policy.zoningRestriction*.035)*(G.housingMarket?.rentIndex||1);
 const property=G.buildings.filter(b=>b.owner===h.id&&['home','apartment','tower'].includes(b.kind)).reduce((n,b)=>n+b.value*G.policy.propertyTax/100/360,0);
 return rent+property+h.people.length*(1.6*foodPriceEstimate()*(1+G.policy.foodTax/100)+2.25*(1+G.policy.utilityTax/100));
}
function assessCredit(kind,owner,amount,term,rate){
 const strict=clamp((G.policy.lendingRules||0)/100,0,1),stressRate=rate+.02,scheduled=amount/term+amount*rate/360,stressed=amount/term+amount*stressRate/360;
 let recurring,essential,buffer;
 if(kind==='household'){
  recurring=Number.isFinite(owner.netIncomeTrend)?Math.max(0,owner.netIncomeTrend-Math.sqrt(owner.incomeVariance||0)):openingHouseholdIncome(owner);
  essential=expectedHouseholdEssentials(owner);buffer=Math.max(0,householdLiquidity(owner)-essential*90)/term;
 }else{recurring=Math.max(0,(owner.revenueTrend||0)*Math.max(0,owner.marginTrend||0));essential=0;buffer=Math.max(0,owner.cash-workerIncome(owner)*Math.max(1,owner.jobs)*45)/term;}
 const capacity=Math.max(0,recurring-essential)/(1.25+strict)+buffer;
 return {approved:stressed<=capacity,reason:stressed<=capacity?'Payment fits observed surplus and reserves':'Stressed payment exceeds income surplus and usable reserves',scheduled,stressed,capacity,recurring,essential};
}
function updateCreditObservations(){
 for(const h of G.households){if(!h.people.length)continue;const income=Math.max(0,h.income-h.incomeTax),old=h.netIncomeTrend??income;h.netIncomeTrend=old*.95+income*.05;h.incomeVariance=(h.incomeVariance||0)*.95+(income-old)*(income-old)*.05;h.essentialDueTrend=(h.essentialDueTrend??h.essentialDue??0)*.95+(h.essentialDue||0)*.05;}
}
function completeEquipmentOrders(){for(const f of G.firms){const order=f.pendingEquipment;if(!order||G.day<order.ready)continue;f.scale=Math.min(2.2,(f.scale||1)+order.gain);f.equipmentCommissioned=(f.equipmentCommissioned||0)+order.cost;f.pendingEquipment=null;dirty=true;}}
function validateCreditState(data){
 for(const p of data.people){if(p.commuteBlocked!=null&&typeof p.commuteBlocked!=='boolean')return false;if(p.commuteBlockedDays!=null&&(!Number.isInteger(p.commuteBlockedDays)||p.commuteBlockedDays<0||p.commuteBlockedDays>30))return false;}
 for(const f of data.firms)if(f.attendingWorkers!=null&&(!Array.isArray(f.attendingWorkers)||new Set(f.attendingWorkers).size!==f.attendingWorkers.length||f.attendingWorkers.some(id=>!Number.isInteger(id)||!data.people[id])))return false;
 for(const owner of [...data.households,...data.firms])if(owner.creditDecision){const c=owner.creditDecision;if(typeof c.approved!=='boolean'||!Number.isInteger(c.day)||c.day<1||c.day>data.day||!Number.isFinite(c.requested)||c.requested<0||typeof c.reason!=='string'||c.reason.length>500)return false;for(const key of ['scheduled','stressed','capacity','recurring','essential'])if(c[key]!=null&&(!Number.isFinite(c[key])||c[key]<0))return false;}

 const fields=['netIncomeTrend','incomeVariance','essentialDueTrend','essentialDue','travelDue'];
 for(const h of data.households)if(h.utilityConnected!=null&&typeof h.utilityConnected!=='boolean')return false;
 for(const h of data.households)for(const key of fields)if(h[key]!=null&&(!Number.isFinite(h[key])||h[key]<0))return false;
 for(const f of data.firms)if(f.pendingEquipment){const o=f.pendingEquipment;if(!Number.isFinite(o.cost)||o.cost<=0||!Number.isFinite(o.gain)||o.gain<=0||o.gain>1.2||!Number.isInteger(o.ordered)||o.ordered<1||o.ordered>data.day||o.ready!==o.ordered+30)return false;}
 for(const l of data.loans||[])for(const key of ['lastPaymentDay','defaultedDay'])if(l[key]!=null&&(!Number.isInteger(l[key])||l[key]<1||l[key]>data.day))return false;
 return true;
}
function creditDecisionReport(owner){
 const c=owner.creditDecision;if(!c)return tip('A new credit application will be assessed against observed income, essential costs, working capital and a stressed repayment. Low interest alone does not make an unaffordable loan viable.');
 return `<div class="credit-decision"><strong>Latest credit review · day ${fmt(c.day)} · ${c.approved?'APPROVED':'NOT APPROVED'}</strong><p class="desc">${esc(c.reason)}</p>${Number.isFinite(c.capacity)?strip('Stressed payment / day',money(c.stressed))+strip('Assessed payment capacity / day',money(c.capacity)):''}</div>`;
}
const creditEconomyBase=renderEconomy;
renderEconomy=function(){const active=G.loans.filter(l=>l.status==='active'),orders=G.firms.filter(f=>f.pendingEquipment);return head('Credit and investment pipeline')+strip('Active household / enterprise loans',active.filter(l=>l.ownerType==='household').length+' / '+active.filter(l=>l.ownerType==='firm').length)+strip('Loans with missed payments',active.filter(l=>l.arrears>0).length)+strip('Funded equipment orders',orders.length)+tip('Debt service reduces spendable household income. Banks price impaired portfolios and assess a rate-stressed repayment. Equipment is paid for at order and becomes productive after commissioning; credit cannot replace demand or missing inputs.')+creditEconomyBase();};

// SOURCE: 15-household-markets.js
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

function regionalUtilityAccess(home){if(!home)return false;const net=graph(),port=net.portals.get(home.id);return port!=null&&net.parts[port]===net.mainPart;}

// SOURCE: 18-region-charter.js
// The original 56×56 town keeps every existing right. Five real outer districts
// extend the region to 80×80; undeveloped regional land requires a mayoral deed.
const CHARTER_BASE=56;
let parcelFocus=null;
const ANNEX_PARCELS=[
 {id:'east-meadow',name:'East Meadow',x:56,y:2,w:22,h:26,description:'A large eastern tract with woodland and lake frontage.'},
 {id:'county-ridge',name:'County Ridge',x:56,y:28,w:22,h:28,description:'Eastern upland for a new connected district.'},
 {id:'river-reach',name:'Lower River Reach',x:2,y:56,w:26,h:22,description:'New southern riverbank, suitable for working waterfronts.'},
 {id:'orchard-downs',name:'Orchard Downs',x:28,y:56,w:28,h:22,description:'A substantial southern tract for homes, farms and civic sites.'},
 {id:'high-common',name:'High Common',x:56,y:56,w:22,h:22,description:'The far southeastern common, reached through an adjoining district.'}
];
function newCharter(){return {version:1,owned:[],deeds:[],revision:0};}
function regionalTerrain(x,y,seedValue){
 if(x<5+Math.sin(y*.2)*1.7||x===5&&y%4===0)return 2;
 if(x>=56&&((x-66)*(x-66)/36+(y-22)*(y-22)/64)<1)return 2;
 return hash((y*T+x)^((seedValue||42)>>>0))%100<31?3:0;
}
function parcelForTile(x,y){return ANNEX_PARCELS.find(p=>x>=p.x&&x<p.x+p.w&&y>=p.y&&y<p.y+p.h)||null;}
function charterOwns(x,y){if(x<0||y<0||x>=T||y>=T)return false;if(x<CHARTER_BASE&&y<CHARTER_BASE)return true;const p=parcelForTile(x,y);return !!p&&!!G.charter?.owned.includes(p.id);}
function charterFootprint(x,y,kind){return footprintFor(x,y,kind).every(id=>charterOwns(id%T,id/T|0));}
function charterRoadCount(){const privateSet=new Set(G.privateRoads||[]);return [...graph().neighbors.keys()].filter(id=>!privateSet.has(id)&&charterOwns(id%T,id/T|0)).length;}
function parcelSurvey(p){let land=0,water=0,forest=0,roads=0;for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++){const cell=G.tiles[roadId(x,y)];if(cell===2)water++;else{land++;if(cell===3)forest++;if(cell===1)roads++;}}return {land,water,forest,roads,area:p.w*p.h,price:12000+land*42+roads*75};}
function parcelAdjacent(p){const owned=G.charter?.owned||[];return p.x===56&&p.y<56||p.y===56&&p.x<56||ANNEX_PARCELS.some(q=>owned.includes(q.id)&&((q.x+q.w===p.x||p.x+p.w===q.x)&&Math.max(q.y,p.y)<Math.min(q.y+q.h,p.y+p.h)||(q.y+q.h===p.y||p.y+p.h===q.y)&&Math.max(q.x,p.x)<Math.min(q.x+q.w,p.x+p.w)));}
function purchaseParcel(id,quotedPrice){
 const p=ANNEX_PARCELS.find(p=>p.id===id);if(!p||!G.charter||G.charter.owned.includes(id)||!parcelAdjacent(p))return false;const quote=parcelSurvey(p);if(!Number.isFinite(quotedPrice)||quotedPrice!==quote.price||G.treasury<quote.price)return false;
 G.treasury-=quote.price;G.region+=quote.price;G.charter.owned.push(id);G.charter.deeds.push({id,price:quote.price,day:G.day});G.charter.revision++;G.cumulative.landPurchases=(G.cumulative.landPurchases||0)+quote.price;
 book('Municipal land budget','Regional land authority',quote.price,'Annexation deed: '+p.name);G.journal.push({day:G.day,name:'District annexed',message:p.name+': '+quote.area+' new regional tiles, '+quote.land+' land tiles. Development rights purchased for '+money(quote.price)+'. Existing private titles are unchanged.',baseline:{...G.stats,treasury:G.treasury}});
 story('The mayor acquired '+p.name+'. Roads and service coverage must still be developed.','good');invalidateRoads(false);staticDirty=true;dirty=true;updateHeader();save();return true;
}
function validateCharter(data){
 const c=data.charter;if(!c||c.version!==1||!Array.isArray(c.owned)||new Set(c.owned).size!==c.owned.length||c.owned.some(id=>!ANNEX_PARCELS.some(p=>p.id===id))||!Array.isArray(c.deeds)||c.deeds.length!==c.owned.length||!Number.isInteger(c.revision)||c.revision!==c.owned.length)return false;
 const seen=new Set();for(const d of c.deeds){if(!d||seen.has(d.id)||!c.owned.includes(d.id)||!Number.isInteger(d.day)||d.day<1||d.day>data.day||!Number.isFinite(d.price)||d.price<12000||d.price>100000)return false;seen.add(d.id);}
 const ownsTile=(id)=>{const x=id%T,y=id/T|0;if(x<CHARTER_BASE&&y<CHARTER_BASE)return true;const p=parcelForTile(x,y);return !!p&&c.owned.includes(p.id);};
 if(data.tiles.some((type,id)=>type===1&&!ownsTile(id)))return false;
 if(data.buildings.some(b=>(b.footprint||[b.y*T+b.x]).some(id=>!ownsTile(id))))return false;
 if(Object.keys(data.landUse||{}).some(id=>!ownsTile(+id))||(data.privateRoads||[]).some(id=>!ownsTile(id)))return false;
 if(c.owned.includes('high-common')&&!c.owned.some(id=>id==='county-ridge'||id==='orchard-downs'))return false;
 return true;
}
function normalizeRegionArchive(input){
 if(!input||!Array.isArray(input.tiles))return input;
 if(input.tiles.length===T*T){if(input.gridSize!==T)return null;return input;}
 if(input.tiles.length!==CHARTER_BASE*CHARTER_BASE||(input.gridSize!=null&&input.gridSize!==CHARTER_BASE))return null;
 const data=JSON.parse(JSON.stringify(input)),oldSize=CHARTER_BASE,count=oldSize*oldSize;
 const tile=id=>{if(!Number.isInteger(+id)||+id<0||+id>=count)throw Error('Invalid legacy regional tile');return (+id/oldSize|0)*T+(+id%oldSize);};
 const list=a=>a.map(tile),map=object=>Object.fromEntries(Object.entries(object||{}).map(([id,v])=>[tile(id),v]));
 const tiles=Array.from({length:T*T},(_,id)=>regionalTerrain(id%T,id/T|0,data.worldSeed||data.scenarioSeed));for(let y=0;y<oldSize;y++)for(let x=0;x<oldSize;x++)tiles[y*T+x]=data.tiles[y*oldSize+x];data.tiles=tiles;
 for(const b of data.buildings||[])if(Array.isArray(b.footprint))b.footprint=list(b.footprint);
 for(const key of ['roadClasses','streetNames','landUse','fieldOwner'])if(data[key])data[key]=map(data[key]);
 if(Array.isArray(data.roadWear)){const wear=new Array(T*T).fill(100);for(let id=0;id<Math.min(count,data.roadWear.length);id++)wear[tile(id)]=data.roadWear[id];data.roadWear=wear;}
 if(Array.isArray(data.privateRoads))data.privateRoads=list(data.privateRoads);
 for(const p of data.projects||[])for(const key of ['plots','runway'])if(Array.isArray(p[key]))p[key]=list(p[key]);
 if(data.airport?.runway)data.airport.runway=list(data.airport.runway);
 for(const s of data.freight||[])if(Array.isArray(s.path))s.path=list(s.path);
 for(const v of data.trafficState?.vehicles||[])if(Array.isArray(v.path))v.path=list(v.path);
 if(data.trafficState)data.trafficState.gates=[];
 data.gridSize=T;data.charter=newCharter();return data;
}
function centerTownCamera(zoom=.95){const hall=G.buildings.find(b=>b.kind==='townhall')||{x:28,y:28};const p=iso(hall.x+1,hall.y+1);cam={x:p[0],y:p[1]+28,zoom};dirty=true;}

// SOURCE: 19-street-plan.js
// A connected street hierarchy: through routes, collectors, and short local streets.
// No nested decorative rings. Imported towns retain their existing parcels and streets.
function foundingStreetPlan(){
 const classes={},names={};
 const line=(x1,y1,x2,y2,kind,name)=>{const dx=Math.sign(x2-x1),dy=Math.sign(y2-y1);let x=x1,y=y1;for(let i=0;i<100;i++){const id=y*T+x;classes[id]=kind;names[id]=name;if(x===x2&&y===y2)break;x+=dx;y+=dy;}};
 line(8,27,49,27,'arterial','High Street');line(27,7,27,49,'arterial','Station Road');
 line(15,9,15,45,'collector','River Road');line(43,13,43,48,'collector','County Road');
 line(9,13,43,13,'collector','North Avenue');line(15,21,47,21,'collector','Market Street');line(9,35,47,35,'collector','Orchard Avenue');line(15,43,47,43,'collector','South Avenue');
 line(21,13,21,35,'local','Church Lane');line(35,13,35,43,'local','Mill Street');
 line(15,31,27,31,'local','Garden Street');line(35,31,40,31,'local','Foundry Close');line(21,39,35,39,'local','School Street');line(21,35,21,43,'local','School Lane');
 return {classes,names};
}

// SOURCE: 20-world.js
function seed(seedValue=42){
 beginSaveTimeline();
 resetTownTransientUI();
 crewDay=-1;crewsUsed=new Map();regionalCrews=0;rngState=(Number(seedValue)>>>0)||42;visualState=918273;traffic=[];trafficClock=0;frameClock=0;trafficElapsed=0;vehicleSerial=0;intersectionGates.clear();
 draftPolicy={};roadBatchDirty=false;
 const tiles=new Array(T*T).fill(0),streets=foundingStreetPlan();
 for(let y=0;y<CHARTER_BASE;y++)for(let x=0;x<CHARTER_BASE;x++){
   let road=streets.classes[y*T+x]!=null;
   if(road)tiles[y*T+x]=1;
   else if(x<5+Math.sin(y*.2)*1.7 || x===5 && y%4===0)tiles[y*T+x]=2;
   else if((x<11||x>46||y<11||y>46)&&random()<.39)tiles[y*T+x]=3;
   else if(random()<.085)tiles[y*T+x]=3;
 }
 for(let y=0;y<T;y++)for(let x=0;x<T;x++)if(x>=CHARTER_BASE||y>=CHARTER_BASE)tiles[y*T+x]=regionalTerrain(x,y,seedValue);
 G={gridSize:T,charter:newCharter(),roadClasses:streets.classes,streetNames:streets.names,climateSeasons:gameOptions.seasons,climateWeather:gameOptions.weather,version:3,day:1,year:1,month:1,tiles,buildings:[],homes:[],people:[],households:[],firms:[],policy:{...defaults},
    treasury:90000,debt:0,publicReserve:0,region:15000000,projects:[],metro:{cash:0,stations:[],lines:[],fare:2.75,rides:0,revenue:0,expenses:0,dailyRides:0,daysInDeficit:0,operating:false,invested:0},development:{homes:0,firms:0,roads:0,stations:0,lastReport:null,decisions:[]},privateRoads:[],landUse:{},fieldOwner:{},fieldCount:{},airport:null,autoBuild:true,nextId:1,history:[],events:[],journal:[],records:[],stats:{},cumulative:{incomeTax:0,profitTax:0,propertyTax:0,foodTax:0,utilityTax:0,commercialRate:0,permits:0,tariffs:0,spending:0,crime:0,fires:0,welfare:0},cases:[],speed:1,scenario:chosenScenario,achievements:[],council:{approval:65,elections:0,confidence:65,factions:{workers:60,merchants:62,homeowners:60,public:66},lastApproval:65},ambition:chosenScenario==='regional'?'education':chosenScenario==='hardtimes'?'families':'balanced',ambitionDays:{},lastMonth:{},crisesHandled:0,policyOutcomes:[],construction:0,worldSeed:Math.floor(random()*99999999),weather:'clear',season:0,regionalDemand:1,neighborhoods:[],lastEventDay:1,unrest:0,education:46,health:74,historyLong:[]};
 const add=(kind,x,y,opt={})=>{if(G.tiles[roadId(x,y)]===1||G.tiles[roadId(x,y)]===2)throw Error('Founding structure overlaps a roadway or river');G.tiles[roadId(x,y)]=0;let b={id:G.nextId++,kind,x,y,value:Math.round(types[kind].cost*10),condition:100,owner:-1,firm:-1,hh:-1,...opt};G.buildings.push(b);return b};
 add('townhall',26,26,{value:150000});add('police',24,26,{value:90000});add('fire',29,26,{value:80000});add('clinic',28,29,{value:74000});add('school',25,28,{value:70000});add('square',28,26,{value:15000});
 const firms=['grocer','grocer','grocer','bakery','bakery','mill','mill','farm','farm','farm','farm','forestry','forestry','sawmill','quarry','contractor','contractor','grocer','bakery','farm','tavern','office','factory','warehouse'];
 let slots=[];
 for(let y=7;y<49;y++)for(let x=7;x<49;x++)if(canPlace(x,y,true))slots.push([x,y]);
 // Draw jitter once per lot. A random comparator is non-transitive and consumes
 // different RNG counts in different engines, changing the entire founding town.
 slots=slots.filter(([x,y])=>Math.abs(x-27)+Math.abs(y-27)<35).map(([x,y])=>({lot:[x,y],rank:Math.abs(x-27)+Math.abs(y-27)+rn(-1,1),id:y*T+x})).sort((a,b)=>a.rank-b.rank||a.id-b.id).map(item=>item.lot);
 slots=slots.filter(([x,y])=>{let h=(x*331+y*113)%11;return h!==2&&h!==4});
 for(let i=0;i<3;i++){const spot=slots.shift();if(spot)add('bank',...spot,{value:75000,bankId:i});}
 for(const kind of firms){
   // At founding, farms and major works already occupy actual land, not a tiny
   // decorative square. Keep candidate lots in sync with newly claimed plots.
   const idx=slots.findIndex(([x,y])=>canPlace(x,y,true,kind)&&(kind!=='farm'||Math.abs(x-27)+Math.abs(y-27)>=18));
   const pos=idx>=0?slots.splice(idx,1)[0]:slots.shift();
   if(pos){const large=LANDMARK_SIZE[kind]&&canPlace(pos[0],pos[1],true,kind);
    const f=createFirm(kind,...pos,true,add);
    if(large&&f){const b=G.buildings.find(b=>b.id===f.building);reserveFootprint(b,kind);}
    slots=slots.filter(([x,y])=>!buildingAt(x,y));
   }
 }
 // Neighbourhoods grow along existing roads, rather than a single wall of
 // identical cottages around the town hall. Preserve each household's address.
 const quarters=[[20,22],[34,22],[21,34],[35,34],[16,27],[39,27]];
 for(let i=0;i<(chosenScenario==='frontier'?32:67)&&slots.length;i++){
   const q=quarters[i%quarters.length];let index=-1,best=Infinity;
   for(let k=0;k<slots.length;k++){
    const [sx,sy]=slots[k];if(!canPlace(sx,sy,true,'home'))continue;
    const d=Math.abs(sx-q[0])+Math.abs(sy-q[1]);
    let crowd=0;for(const building of G.buildings){const reach=Math.abs(sx-building.x)+Math.abs(sy-building.y);
      if(reach<=2)crowd+=building.kind==='home'?1.45:building.kind==='farm'?3.8:building.firm>=0?1.1:.45;
    }
    const score=d*1.7+crowd*1.5+Math.abs(sx-27)*.045+random()*.5;
    if(score<best){best=score;index=k}
   }
   if(index<0)break;
   const p=slots.splice(index,1)[0];const b=add('home',...p,{value:Math.round(rn(35000,70000))});
   const family={id:G.households.length,name:pick(surnames),cash:Math.round(rn(180,3500)),home:b.id,owner:-1,people:[],income:0,rent:0,food:0,tax:0,aid:0,crimeLoss:0,stress:rn(10,30),security:rn(75,100),last:[],worklessness:0};
   G.households.push(family);G.region-=family.cash;G.homes.push(b.id);b.hh=family.id;
 }
 for(let i=0;i<G.households.length;i++){
   const hh=G.households[i];const count=i<35?3:2;
   for(let j=0;j<count;j++){
     let p={id:G.people.length,name:pick(first)+' '+hh.name,age:Math.round(i%6===0&&j<2?rn(71,80):j<2?rn(26,58):rn(6,15)),skill:rn(.3,1),health:rn(65,100),hh:hh.id,job:-1,life:rn(45,82),last:[]};
     G.people.push(p);hh.people.push(p.id)
   }
 }
 // The five founding farmsteads own actual surrounding wheat or maize fields.
 // Reserve farmland after town lots are allocated so crops never invade roads
 // or homes. Cropland is not itself a decorative building or a cash subsidy.
 for(const f of G.firms.filter(f=>f.kind==='farm')){
  const plots=fieldLotsNear(f,5);let planted=0;
  for(const plot of plots){if(G.tiles[plot.id]!==0||G.landUse[plot.id]||buildingAt(plot.x,plot.y))continue;
    G.landUse[plot.id]=1;G.fieldOwner[plot.id]=f.id;planted++;
  }
  G.fieldCount[f.id]=planted;G.development.fields=(G.development.fields||0)+planted;
 }
 for(let b of G.buildings)if(b.kind==='home')b.owner=(random()<.35?b.hh:random()*G.households.length|0);
 assignJobs();recompute();const counts={population:G.people.length,employment:G.stats.employment,hardship:G.stats.hardship,safety:G.stats.safety,businesses:G.firms.length,treasury:G.treasury};
 G.journal.push({day:1,name:'Village founded',message:'Town hall records open. Follow real people, employers and policy consequences.',baseline:counts});
 G.events.push({day:1,text:'A new council has taken responsibility for the prosperity of the Vale.',type:'neutral'});setupScenario();seedBanks();ensureSystems();initializeScenario();initializeWaterfrontStart();ensureMarketModel();G.scenarioSeed=seedValue;G.accounts={baseline:totalMoney(),maxError:0};housingMarketDay(true);recordObservation();initializeScenarioProgramme();save();
 staticDirty=true;dirty=true;
}
function cityCell(x,y){return x>=0&&x<T&&y>=0&&y<T?G.tiles[y*T+x]:-1}
// A site owns every square in its footprint. Legacy saves without a footprint
// retain their one-square plot; newly built landmarks reserve all their land.
const LANDMARK_SIZE={farm:[2,2],factory:[2,2],warehouse:[2,2],college:[2,2],
 airport:[2,2],metro_station:[2,2],tower:[2,2],apartment:[2,2],school:[2,2]};
function footprintFor(x,y,kind){const [w,h]=LANDMARK_SIZE[kind]||[1,1];const result=[];
 for(let dy=0;dy<h;dy++)for(let dx=0;dx<w;dx++)result.push((y+dy)*T+x+dx);
 return result;}
function footprintOf(b){return Array.isArray(b.footprint)&&b.footprint.length?b.footprint:[roadId(b.x,b.y)];}
let cacheBuildingsFor=null,cacheBuildingsCount=-1,cacheFootprintRevision=0,indexFootprintRevision=-1,
 buildingsByTile=new Map(),buildingsById=new Map();
function invalidateBuildingIndex(){cacheFootprintRevision++;cacheBuildingsCount=-1;}
function refreshBuildingIndex(){if(cacheBuildingsFor===G&&cacheBuildingsCount===G.buildings.length&&indexFootprintRevision===cacheFootprintRevision)return;
 cacheBuildingsFor=G;cacheBuildingsCount=G.buildings.length;indexFootprintRevision=cacheFootprintRevision;
 buildingsByTile=new Map();buildingsById=new Map();
 for(const b of G.buildings){buildingsById.set(b.id,b);for(const id of footprintOf(b))if(!buildingsByTile.has(id))buildingsByTile.set(id,b);}
}
function buildingAt(x,y){if(x<0||x>=T||y<0||y>=T)return null;refreshBuildingIndex();return buildingsByTile.get(y*T+x)||null;}
function nearRoad(x,y){return roadOffsets.some(d=>cityCell(x+d[0],y+d[1])===1)}
function canPlace(x,y,roads=true,kind='home',ignore=null){
 const dims=LANDMARK_SIZE[kind]||[1,1];if(x<2||y<2||x+dims[0]>T-2||y+dims[1]>T-2)return false;
 let access=false;
 for(let dy=0;dy<dims[1];dy++)for(let dx=0;dx<dims[0];dx++){
  const ax=x+dx,ay=y+dy,id=roadId(ax,ay),owner=buildingAt(ax,ay);if(!charterOwns(ax,ay))return false;
  if(![0,3].includes(G.tiles[id])||G.landUse?.[id]||(owner&&owner.id!==ignore?.id))return false;
  if(nearRoad(ax,ay))access=true;
 }
 if((kind==='fishery'||kind==='wharf')&&!waterfrontSite(x,y,kind))return false;
 return !roads||access;
}
function reserveFootprint(b,kind=b.kind){b.footprint=footprintFor(b.x,b.y,kind);for(const id of b.footprint)if(G.tiles[id]===3)G.tiles[id]=0;invalidateBuildingIndex();invalidateRoads(false);staticDirty=true;}
function findLandmarkLot(kind,candidates){return candidates.find(v=>canPlace(v.x,v.y,true,kind))||null;}
function getFootprintIssues(){const occupied=new Map(),issues=[];
 for(const b of G.buildings){for(const id of footprintOf(b)){
  if(!Number.isInteger(id)||id<0||id>=T*T){issues.push('invalid footprint '+b.id);continue;}
  if(G.tiles[id]===1)issues.push('structure on roadway '+b.id+' at '+id);
  if(G.tiles[id]===2)issues.push('structure in water '+b.id+' at '+id);
  if(G.landUse?.[id])issues.push('structure overlapping reserved land '+b.id+' at '+id);
  if(occupied.has(id)&&occupied.get(id)!==b.id)issues.push('overlapping structures '+b.id+' / '+occupied.get(id));
  occupied.set(id,b.id);
 }}return issues;}
function createFirm(kind,x,y,setup=false,addFn=null){
 if(!setup&&!canPlace(x,y,true,kind))return null;
 const b=addFn?addFn(kind,x,y):{id:G.nextId++,kind,x,y,value:Math.round(types[kind].cost*10),condition:100,owner:-1,firm:-1,hh:-1};
 if(!addFn){G.tiles[y*T+x]=0;G.buildings.push(b);if(LANDMARK_SIZE[kind]&&!setup)reserveFootprint(b,kind);}
 const f={id:G.firms.length,building:b.id,name:(kind==='grocer'?'Village Stores':kind==='bakery'?'Baker & Sons':types[kind].n)+' '+pick(['& Co.','Ltd.','Works','Trading','of '+pick(['Oakford','Hawthorn','Eastmead'])]),kind,
 cash:Math.round(rn(10000,24000)),stock:{grain:40,flour:40,food:80,logs:30,timber:30,stone:30},jobs:SECTOR_WORKERS[kind]||3,workers:[],wage:Math.round(rn(26,37)),price:rn(4,7),debt:0,revenue:0,expenses:0,profit:0,tax:0,theft:0,age:0,strain:0,history:[],owner:G.households.length?random()*G.households.length|0:-1};
 if(G.goodsAccounts)for(const [good,qty] of Object.entries(f.stock))goodsEntry(good,'imports',qty);
 G.firms.push(f);b.firm=f.id;if(!setup)invalidateRoads();return f;
}
function assignJobs(){
 if(!G||!G.people)return;
 const free=G.people.filter(p=>!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=70&&p.job<0&&!p.publicWork&&!p.previousPublicRole&&(p.searchAfter||0)<=G.day);
 const net=graph(),maxJourney=60+(G.policy.transitBudget||0)/8;
 const vacancies=G.firms.filter(f=>!f.closed&&f.workers.length<f.jobs).sort((a,b)=>(b.wage-a.wage));
 for(const f of vacancies){let workplace=readBuild(f.building),port=net.portals.get(f.building);
  if(!workplace||port==null)continue;
  while(f.workers.length<f.jobs&&free.length){let best=-1,score=Infinity;
   for(let i=0;i<free.length;i++){const candidate=free[i],hh=G.households[candidate.hh],home=hh&&readBuild(hh.home);
    if(!home)continue;const hport=net.portals.get(home.id);if(hport==null||net.parts[hport]!==net.parts[port])continue;
    const distance=roadDistance(hport,port);
    if(distance>maxJourney&&!hasMetroCommute(home,workplace))continue;
    const mismatch=Math.abs(candidate.skill-.7)*3,rank=distance*.74+mismatch+candidate.id*.00001;
    if(rank<score){score=rank;best=i}
   }
   if(best<0)break;const person=free.splice(best,1)[0];person.job=f.id;person.commuteBlockedDays=0;person.commuteBlocked=false;f.workers.push(person.id);
  }
 }
}
function readBuild(id){refreshBuildingIndex();return buildingsById.get(id)}
function workerIncome(f){return Math.max(G.policy.minWage,f.wage)}
function credit(h,amount){h.cash+=amount}
function transferBudget(to,amount,cat){let paid=Math.max(0,Math.min(G.treasury,amount));G.treasury-=paid;to.cash+=paid;G.cumulative.spending+=paid;return paid}
function story(text,type='neutral',bid=-1,hid=-1){G.events.unshift({day:G.day,text,type,bid,hid});if(G.events.length>160)G.events.length=160}
function transferTreasury(amount,cat){const pay=Math.max(0,amount);G.treasury+=pay;G.cumulative[cat]=(G.cumulative[cat]||0)+pay;return pay}
function regionBuy(f,good,amount,price=marketPrice(good)){if(!f||!G.region)return 0;const portal=graph().portals.get(f.building);const linked=portal!=null&&graph().parts[portal]===graph().mainPart;const access=linked?1:0;const regionalDemand=(1+G.buildings.filter(b=>b.kind==='square').length*.025+G.firms.filter(f=>f.kind==='warehouse'&&!f.closed).length*.065+(G.airport?.operating ? .13 : 0))*(G.scenario==='hardtimes'&&G.day<540?.52:G.scenario==='frontier'&&G.day<280?.78:1);const qty=Math.max(0,Math.min(f.stock[good]||0,amount*access*regionalDemand*clamp(G.regionalDemand||1,.30,1.3),G.region/Math.max(price,1)));return settleRegionalExport(f,good,qty,price)}
function regionImport(f,good,qty){if(!G.policy.imports)return 0;const net=graph(),port=net.portals.get(f.building);if(port==null||net.parts[port]!==net.mainPart)return 0;const tariff=G.policy.importTariff/100;const unit=marketPrice(good)*(1+tariff);let n=Math.max(0,Math.min(qty,Math.floor(f.cash/unit)));if(n<=0)return 0;
 const total=n*unit,levy=total*tariff/(1+tariff);recordInventoryPurchase(f,good,n,total);f.cash-=total;f.stock[good]=(f.stock[good]||0)+n;goodsEntry(good,'imports',n);G.region+=total-levy;if(G.market)G.market.imports+=total-levy;transferTreasury(levy,'tariffs');return n;
}
function trade(f,good,units){units=Math.max(0,units-pendingGoods(f,good));if(units<=0)return 0;
 const net=graph(),buyer=readBuild(f.building),sourceRoad=net.portals.get(f.building);
 const sources=G.firms.filter(v=>!v.closed&&(v.stock[good]||0)>0&&v.id!==f.id&&(formulas[v.kind]?.out===good||v.kind==='warehouse')).map(v=>{
  const b=readBuild(v.building),port=net.portals.get(v.building);
  const linked=port!=null&&sourceRoad!=null&&net.parts[port]===net.parts[sourceRoad];
  const distance=b&&buyer?roadDistance(sourceRoad,port):Infinity;
  return {f:v,linked,distance,shipping:linked?(0.008+distance*.0009)*clamp(1.42-G.policy.roadBudget/220,.65,1.42):Infinity}
 }).filter(s=>s.linked).sort((a,b)=>a.shipping-b.shipping);
 let left=units;for(const source of sources){const seller=source.f,price=marketOutputPrice(seller,good),unit=price*(1+source.shipping);
  const wear=(G.stats.roadCondition||85),carriageRate=source.shipping*(1+Math.max(0,75-wear)/110);
  let n=Math.min(seller.stock[good],left,Math.floor(f.cash/(price*(1+carriageRate))));if(n<=0)continue;
  const amt=n*price,carriage=n*price*carriageRate;
  recordInventoryPurchase(f,good,n,amt+carriage);takeInventory(seller,good,n,true);enterpriseRevenue(seller,amt);f.cash-=amt+carriage;G.region+=carriage;G.cumulative.freight=(G.cumulative.freight||0)+carriage;
  dispatchGoods(seller,f,good,n,routeBetween(readBuild(seller.building),readBuild(f.building)));left-=n;if(left<=0)break
 }
 if(left>0)regionImport(f,good,left);
 return units-left;
}

// SOURCE: 21-waterfront.js
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

// SOURCE: 25-scenarios.js
// Existing capital in authored starts is funded before the opening balance sheet.
function initializeScenario(){
 if(chosenScenario!=='regional')return;
 G.scenario='regional';Object.assign(G.policy,{incomeTax:13,profitTax:14,zoningRestriction:20,transitBudget:160,policeBudget:300,defenseBudget:220,healthBudget:180,educationBudget:220,aidBudget:250});
 const kinds=Object.entries({factory:7,office:12,warehouse:7,grocer:6,bakery:3,farm:2,mill:2,forestry:2,sawmill:4,quarry:1,contractor:3,tavern:7,college:2}).flatMap(([kind,count])=>Array(count).fill(kind));
 // Reserve actual employment sites before bidding housing onto the remaining land.
 for(let n=0;n<kinds.length;n++){
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
  for(let k=0;k<4;k++){const h=addHouseholdAt(b,2500);if(h)b.units.push(h.id);}b.hh=b.units[0]??-1;
  G.development.privateSpend=(G.development.privateSpend||0)+cost;recompute();
 }
 for(const h of G.households.filter(h=>h.id>=67)){for(let j=0;j<h.people.length;j++){const person=G.people[h.people[j]];person.age=h.id%5===0?Math.round(rn(71,79)):j===0?Math.round(rn(27,57)):h.id%3===0?Math.round(rn(7,15)):Math.round(rn(24,56));}}
 assignJobs();recompute();G.journal.push({day:1,name:'Market Cross opening balance sheet',message:'An established regional borough. Apartment owners and employers funded their land, buildings and working capital before this council took office.',baseline:{...G.stats,treasury:G.treasury}});
 story('Market Cross inherits dense housing, manufacturing and services. Transport investors will judge whether new infrastructure pays.','neutral');
}

// SOURCE: 30-economy.js
function dailyEconomy(){
 ensureMarketModel();marketOpen=true;const P=G.policy,live=G.firms.filter(f=>!f.closed),counts={};
 for(const f of live)counts[f.kind]=(counts[f.kind]||0)+1;
 for(const f of G.firms){f.revenue=f.pendingRevenue||0;f.pendingRevenue=0;f.expenses=0;f.debtDue=0;f.cogs=f.pendingCogs||0;f.pendingCogs=0;f.purchases=0;f.payroll=0;f.nonSalesIncome=0;f.recoveries=0;f.salesQty=f.pendingSalesQty||0;f.pendingSalesQty=0;f.production=0;f.profit=0;f.tax=0;f.age++;}
 for(const p of G.people){p.previousPublicRole=p.publicWork?(p.publicRole||''):'';p.publicRole='';p.publicWork=false;p.publicIncome=0;p.commuteBlocked=false;}
 for(const h of G.households){h.income=0;h.crimeLossToday=0;h.recoveredLosses=0;h.serviceReceipts=0;h.wages=0;h.pension=0;h.rentalIncome=0;h.dividends=0;h.debtService=0;h.debtDue=0;h.propertyPaid=0;h.propertyMaintenance=0;h.rent=0;h.food=0;h.tax=0;h.incomeTax=0;h.energyTax=0;h.aid=0;h.utilities=0;h.energyRebate=0;h.travel=0;h.travelDue=0;h.shoppingTravel=0;h.discretionary=0;h.last=[];}
 G.market.unmetFood=0;G.market.consumedFood=0;G.market.externalSales=0;G.market.imports=0;G.market.foodDisconnected=0;G.market.blockedCommutes=0;
 for(const f of live){planEnterprise(f);f.attendingWorkers=f.workers.filter(id=>workerCanCommute(G.people[id],f));const attending=new Set(f.attendingWorkers);if(!attending.size)f.ratedOutput=0;
  const wage=workerIncome(f);for(const id of f.workers.slice()){const person=G.people[id],h=G.households[person?.hh];if(!h)continue;if(!attending.has(id)){person.commuteBlocked=true;person.commuteBlockedDays=(person.commuteBlockedDays||0)+1;G.market.blockedCommutes++;if(person.commuteBlockedDays>=30){person.job=-1;person.commuteBlockedDays=0;person.searchAfter=G.day+1;f.workers=f.workers.filter(p=>p!==id);}continue;}person.commuteBlockedDays=0;
   const gross=Math.min(wage,f.cash),tax=gross*P.incomeTax/100;f.cash-=gross;f.expenses+=gross;f.payroll+=gross;h.cash+=gross-tax;h.income+=gross;h.wages+=gross;h.incomeTax+=tax;h.tax+=tax;transferTreasury(tax,'incomeTax');if(gross<wage*.9){f.strain++;person.unpaidDays=(person.unpaidDays||0)+1;}else person.unpaidDays=0;if(person.unpaidDays>=7){person.job=-1;person.searchAfter=G.day+7;f.workers=f.workers.filter(v=>v!==id);}}
  const subsidy=Math.min(G.treasury,workingStaff(f).length*P.employmentSubsidy);G.treasury-=subsidy;f.cash+=subsidy;f.revenue+=subsidy;f.nonSalesIncome+=subsidy;G.cumulative.spending+=subsidy;
  const site=readBuild(f.building),due=(site?.value||0)*(P.commercialRate||0)/100/360,rate=Math.min(f.cash,due);f.cash-=rate;f.expenses+=rate;transferTreasury(rate,'commercialRate');
  const overhead=Math.min(f.cash,2+f.workers.length*(.6+P.businessRegulation*.035));f.cash-=overhead;f.expenses+=overhead;G.region+=overhead;
 }
 prepareWaterfrontDay(live);
 if(G.day%7===0)assignJobs();
 const exportPool={grain:250+G.stats.population*.45,flour:70+G.stats.population*.18,food:100+G.stats.population*.30,logs:100+G.stats.population*.20,timber:65+G.stats.population*.18,stone:70+G.stats.population*.12,manufactures:35+G.stats.population*.15};
 const producerCounts={};if(G.scenario==='regional')exportPool.manufactures*=6;else if(G.scenario==='industrial')exportPool.manufactures*=2.5;
 for(const f of live){const out=formulas[f.kind]?.out;if(out)producerCounts[out]=(producerCounts[out]||0)+1;}
 // Production is bounded by employed labour, anticipated sales and inventories.
 for(const kind of ['farm','fishery','forestry','quarry','mill','sawmill','bakery','factory'])for(const f of live){
  if(f.kind!==kind||!workingStaff(f).length)continue;const recipe=formulas[kind],base=SECTOR_WORKERS[kind];
  const skill=workingStaff(f).reduce((a,id)=>a+(G.people[id]?.skill||.5),0)/workingStaff(f).length;
  let capacity=recipe.qty*workingStaff(f).length/base*(.82+skill*.25+G.education*.0015)*(1+(f.scale-1)*.25);
  if(kind==='farm'){capacity*=1+Math.min(.9,(G.fieldCount?.[f.id]||0)*.035);if(seasonsEnabled())capacity*=[.85,1.15,1.35,.65][Math.floor((G.month-1)/3)];if(G.weather==='drought')capacity*=.72;}
  if(kind==='fishery')capacity=Math.min(capacity,f.fishingAllowance||0);
  f.ratedOutput=capacity;
  const expectedOrders=Math.max(1,f.salesTrend,(exportPool[recipe.out]||0)/Math.max(1,producerCounts[recipe.out])*(G.regionalDemand||1)*.8),target=expectedOrders*4.5,inventory=f.stock[recipe.out]||0;
  let quantity=Math.max(0,Math.min(capacity,target-inventory));
  if(recipe.inp){const ratio=recipe.amount/recipe.qty,need=quantity*ratio;
   if((f.stock[recipe.inp]||0)+pendingGoods(f,recipe.inp)<need*3)trade(f,recipe.inp,need*4-(f.stock[recipe.inp]||0));
   quantity=Math.min(quantity,(f.stock[recipe.inp]||0)/ratio);}
  quantity=Math.floor(quantity);if(quantity<=0)continue;
  let inputCost=0;if(recipe.inp){const used=quantity*recipe.amount/recipe.qty;inputCost=takeInventory(f,recipe.inp,used);goodsEntry(recipe.inp,'consumed',used);}
  const old=f.stock[recipe.out]||0;f.unitCost[recipe.out]=((f.unitCost[recipe.out]||0)*old+inputCost)/Math.max(1,old+quantity);
  f.stock[recipe.out]=old+quantity;f.production=quantity;goodsEntry(recipe.out,'produced',quantity);
 }
 // The external market has finite sector orders and a downward-sloping demand curve.

 const exportOffset=live.length?G.day%live.length:0;for(const f of live.slice(exportOffset).concat(live.slice(0,exportOffset))){const out=formulas[f.kind]?.out;if(out&&workingStaff(f).length){
  const ask=marketOutputPrice(f,out),relative=ask/Math.max(.1,marketPrice(out));
  const orders=exportPool[out]/producerCounts[out]*Math.pow(clamp(1/relative,.25,1.7),1.7);
  const keep=Math.max(10,f.salesTrend*.8);regionBuy(f,out,Math.max(0,Math.min(orders,(f.stock[out]||0)-keep)),ask);
 }}
 // Externally traded services require staff and share a finite pool of contracts.
 const servicePools={office:480+G.stats.population*2.4,warehouse:240+G.stats.population*.9,contractor:170+G.stats.population*.65,tavern:100+G.stats.population*.45,college:100+G.stats.population*.20};
 if(G.scenario==='regional'){servicePools.office*=1.8;servicePools.warehouse*=2;servicePools.tavern*=2.5;}
 for(const f of live){if(servicePools[f.kind]&&workingStaff(f).length){const capacity=clamp(workingStaff(f).length/(SECTOR_WORKERS[f.kind]||3),0,1.8);serviceSales(f,servicePools[f.kind]/counts[f.kind]*Math.min(1.4,capacity)*(G.regionalDemand||1));}}
 // Retailers order inventory to cover a few days of expected household demand.
 const grocers=live.filter(f=>f.kind==='grocer');
 for(const f of grocers){const daily=Math.max(15,reachableRetailDemand(f),f.salesTrend),target=daily*5;
  if((f.stock.food||0)+pendingGoods(f,'food')<daily*3)trade(f,'food',Math.max(0,target-(f.stock.food||0)));
  f.retailCapacity=workingStaff(f).length*80;}
 // A public employee cannot be counted six times across six service budgets.
 G.actualServiceFunding={police:fundedPublicPayroll(P.policeBudget),fire:fundedPublicPayroll(P.defenseBudget),outreach:fundedPublicPayroll(P.outreachBudget),transit:fundedPublicPayroll(P.transitBudget||0)};
 const retirees=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.age>70),pensionDue=retirees.length*(P.pensionDaily||0),pensionPaid=Math.min(G.treasury,pensionDue);G.treasury-=pensionPaid;G.cumulative.spending+=pensionPaid;G.cumulative.pensions=(G.cumulative.pensions||0)+pensionPaid;for(const p of retirees){const h=G.households[p.hh],amount=pensionPaid/Math.max(1,retirees.length);h.cash+=amount;h.income+=amount;h.pension+=amount;}G.market.pensionFunding=pensionDue>0?pensionPaid/pensionDue:1;
 fundCivicServices();
 const householdLoans=new Map();for(const l of G.loans)if(l.status==='active'&&l.ownerType==='household'){if(!householdLoans.has(l.ownerId))householdLoans.set(l.ownerId,[]);householdLoans.get(l.ownerId).push(l);}
 const propertyDue=new Map();for(const b of G.buildings)if(['home','apartment','tower'].includes(b.kind)&&b.owner>=0)propertyDue.set(b.owner,(propertyDue.get(b.owner)||0)+b.value*P.propertyTax/100/360);
 const living=G.households.filter(h=>h.people.length),consumerSuppliers=live.filter(f=>['tavern','office','contractor','factory','college'].includes(f.kind)&&workingStaff(f).length>0);
 for(const h of living){
  // Withdraw only existing deposits; cash scarcity does not manufacture credit.
  const target=h.people.length*25;if(h.cash<target)for(const [id,amount] of Object.entries(h.deposits||{})){withdrawal(h,G.banks[+id],Math.min(amount,target-h.cash));if(h.cash>=target)break;}
  const home=readBuild(h.home),owner=home?.owner;
  const rent=(h.temporaryHousing||owner===h.id)?0:h.people.length*(3.1+P.zoningRestriction*.035)*(G.housingMarket?.rentIndex||1);
  const paid=Math.min(h.cash,rent);h.cash-=paid;h.rent=paid;h.rentDue=rent;
  if(owner===-2)propertyInvestor().cash+=paid;else if(G.households[owner]){const landlord=G.households[owner];landlord.cash+=paid;landlord.income+=paid;landlord.rentalIncome+=paid;}else G.region+=paid;
 }
 const shoppingOffset=living.length?hash(G.day+G.worldSeed)%living.length:0,shoppingOrder=living.slice(shoppingOffset).concat(living.slice(0,shoppingOffset)),retailReference=foodPriceEstimate();
 for(const h of shoppingOrder){
  const home=readBuild(h.home);
  let need=h.people.length*1.6,remaining=need;
  const reachable=groceryChoices(h,home,grocers),shops=reachable.filter(o=>o.f.stock.food>0&&o.f.retailCapacity>0);if(!reachable.length)G.market.foodDisconnected+=h.people.length;
  for(const {f,travel,metro} of shops){const unit=f.price*(1+P.foodTax/100),q=Math.min(remaining,f.stock.food,f.retailCapacity,Math.max(0,h.cash-travel)/unit);if(q<=0)continue;
   h.cash-=travel;h.travel+=travel;h.travelDue+=travel;h.shoppingTravel+=travel;if(metro){G.metro.cash+=travel;G.metro.dailyRides+=2;G.metro.rides+=2;G.metro.revenue+=travel;}else G.region+=travel;
   const net=q*f.price,tax=net*P.foodTax/100;h.cash-=net+tax;h.food+=net+tax;f.cash+=net;f.revenue+=net;takeInventory(f,'food',q,true);f.retailCapacity-=q;goodsEntry('food','consumed',q);transferTreasury(tax,'foodTax');remaining-=q;if(remaining<.001)break;}

  G.market.consumedFood+=need-remaining;G.market.unmetFood+=remaining;
  h.stress=clamp(h.stress+(remaining>.1?remaining*.30:-.20),0,100);
  const cold=seasonsEnabled()&&(G.month>=10||G.month<=2),bill=h.people.length*(2.25+(cold?1.8:0))*(1+P.utilityTax/100),energy=regionalUtilityAccess(home)?Math.min(h.cash,bill):0,levy=energy-energy/(1+P.utilityTax/100);
  h.utilityConnected=regionalUtilityAccess(home);h.utilityDue=bill;h.cash-=energy;h.utilities=energy;h.energyTax=levy;G.region+=energy-levy;transferTreasury(levy,'utilityTax');if(energy<bill*.8)h.stress=clamp(h.stress+.35,0,100);
  for(const id of h.people){const person=G.people[id];if(person.job<0||person.commuteBlocked)continue;const firm=G.firms[person.job],work=firm&&readBuild(firm.building);if(!work||!home)continue;const dist=Math.abs(home.x-work.x)+Math.abs(home.y-work.y),metro=hasMetroCommute(home,work)&&G.metro?.operating;
   const fareDue=metro?G.metro.fare:dist*.035*(1-clamp(P.transitBudget*(G.actualServiceFunding?.transit||0)/280,0,.65)),fare=Math.min(h.cash,fareDue);h.travelDue+=fareDue;h.cash-=fare;h.travel+=fare;if(metro){G.metro.cash+=fare;G.metro.dailyRides++;G.metro.rides++;G.metro.revenue+=fare;}else G.region+=fare;}
  loanPayments(householdLoans.get(h.id)||[]);
  const propertyReserve=propertyDue.get(h.id)||0;h.essentialDue=(h.rentDue||0)+need*(reachable[0]?.f.price||retailReference)*(1+P.foodTax/100)+bill+h.travelDue+propertyReserve;
  const disposable=Math.max(0,h.income-h.incomeTax-h.food-h.rent-h.utilities-h.travel-h.debtService-propertyReserve),wealth=h.cash+Object.values(h.deposits||{}).reduce((a,v)=>a+v,0);
  h.normalDisposable=(h.normalDisposable??disposable)*.96+disposable*.04;
  // Lower rates modestly reduce desired cash saving; income remains the main budget.
  let budget=Math.min(Math.max(0,h.cash-propertyReserve),Math.max(0,h.normalDisposable*.55+(wealth-h.people.length*500)*.0006)*clamp(1.08-(P.policyRate||0)*.018,.65,1.1));
  const suppliers=consumerSuppliers.filter(f=>sharesRoadNetwork(home,readBuild(f.building)));
  for(let j=0;j<Math.min(3,suppliers.length)&&budget>.01;j++){const f=suppliers[(h.id*7+G.day+j*11)%suppliers.length],amount=budget/(3-j);let actual=amount;
   if(f.kind==='factory'){const q=Math.min(f.stock.manufactures||0,amount/(marketPrice('manufactures')*1.25));actual=q*marketPrice('manufactures')*1.25;takeInventory(f,'manufactures',q,true);goodsEntry('manufactures','consumed',q);}
   h.cash-=actual;h.discretionary+=actual;f.cash+=actual;f.revenue+=actual;budget-=actual;}
 }
 if(P.propertyTax>0)for(const b of G.buildings.filter(b=>['home','apartment','tower'].includes(b.kind))){const owner=b.owner===-2?propertyInvestor():G.households[b.owner];if(!owner)continue;const pay=Math.min(owner.cash,b.value*P.propertyTax/100/360);owner.cash-=pay;owner.propertyPaid=(owner.propertyPaid||0)+pay;transferTreasury(pay,'propertyTax');}
 const poor=living.slice().sort((a,b)=>a.cash/a.people.length-b.cash/b.people.length);
 for(const [budgetKey,limit] of [['aidBudget',30],['energyAidBudget',8]]){let left=Math.min(P[budgetKey]||0,G.treasury);for(const h of poor){if(left<.01||h.cash/h.people.length>300)break;const amount=Math.min(left,limit);h.cash+=amount;h.aid+=amount;G.treasury-=amount;left-=amount;G.cumulative.welfare+=amount;G.cumulative.spending+=amount;}}
 for(const h of living){const workers=h.people.some(id=>(G.people[id]?.job>=0&&!G.people[id]?.commuteBlocked)||G.people[id]?.publicWork);h.worklessness=workers?0:(h.worklessness||0)+1;h.stress=clamp(h.stress+(h.cash<h.people.length*50?.12:workers?-.06:.02),0,100);}
 const foodPrice=grocers.length?grocers.reduce((a,f)=>a+f.price,0)/grocers.length:G.market.baseFoodPrice,previous=G.market.cpi;
 G.market.cpi=100*(.55*foodPrice/G.market.baseFoodPrice+.25*(G.housingMarket?.rentIndex||1)+.20);G.market.inflation=(G.market.cpi/Math.max(1,previous)-1)*360*100;
 restartViableEnterprise();
}
function finalizeMarketBooks(){
 for(const f of G.firms){if(f.closed)continue;f.profit=f.revenue-(f.cogs||0)-f.expenses;f.tax=Math.min(f.cash,Math.max(0,f.profit)*G.policy.profitTax/100);f.cash-=f.tax;transferTreasury(f.tax,'profitTax');f.netProfit=f.profit-f.tax;
  f.salesTrend=f.salesTrend*.965+(f.salesQty||0)*.035;f.revenueTrend=f.revenueTrend*.965+Math.max(0,f.revenue-f.recoveries)*.035;f.marginTrend=f.marginTrend*.965+clamp(f.netProfit/Math.max(1,f.revenue,f.revenueTrend),-1,1)*.035;
  f.operating={sales:Math.max(0,f.revenue-f.nonSalesIncome),otherIncome:f.nonSalesIncome,costOfGoods:f.cogs||0,payroll:f.payroll||0,otherCosts:Math.max(0,f.expenses-(f.payroll||0)),profitTax:f.tax,netProfit:f.netProfit,purchases:f.purchases||0,inventoryValue:Object.entries(f.stock).reduce((n,[k,q])=>n+q*(f.unitCost[k]??marketPrice(k)),0)};
  if(f.cash<Math.max(100,workerIncome(f)*f.jobs*2))f.strain++;else f.strain=Math.max(0,f.strain-2);
  if((f.netProfit<0||f.revenue<1)&&f.cash<1000)f.lossDays++;else f.lossDays=Math.max(0,f.lossDays-1);
  if(f.lossDays>75&&f.cash<workerIncome(f)*Math.max(1,f.workers.length)*3)liquidateFirm(f,'persistent operating losses after capacity adjustments');
  const owner=G.households[f.owner];if(owner&&f.netProfit>0&&f.cash>workerIncome(f)*f.jobs*60){const dividend=Math.min(f.cash*.002,f.netProfit*.20);f.cash-=dividend;owner.cash+=dividend;owner.income+=dividend;owner.dividends=(owner.dividends||0)+dividend;}
  f.history.push(f.cash);if(f.history.length>45)f.history.shift();
 }
 updateCreditObservations();marketOpen=false;
}
function policePower(){const b=G.buildings.filter(b=>b.kind==='police').length,court=G.buildings.filter(b=>b.kind==='courthouse').length;const funded=G.actualServiceFunding?.police??1;return clamp(.035+funded*((G.policy.policeBudget/(G.stats.population*.7+1))*.48 + b*.10+court*.05),.035,.95)}
function defensePower(){const b=G.buildings.filter(b=>b.kind==='fire').length;const funded=G.actualServiceFunding?.fire??1;return clamp(.025+funded*((G.policy.defenseBudget/(G.stats.population*.65+1))*.50+b*.1),.025,.96)}
function incidents(){
 const unemployment=1-G.people.filter(p=>!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=70&&((p.job>=0&&!p.commuteBlocked)||p.publicWork)).length/Math.max(1,G.people.filter(p=>!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=70).length);
 const residentHouseholds=G.households.filter(h=>h.people.length>0);
 const hardship=residentHouseholds.filter(h=>h.stress>60||householdLiquidity(h)<150).length/Math.max(1,residentHouseholds.length);
 const danger=(.075+unemployment*.11+hardship*.07)*G.stats.population/300*(1-policePower()*.7)*(1-Math.min(.4,G.policy.outreachBudget*(G.actualServiceFunding?.outreach??1)/400)*.24);
 if(random()<danger){let b=pick(G.buildings.filter(b=>['home','grocer','bakery','mill','farm','sawmill','quarry','contractor'].includes(b.kind)));
    if(b){let loss=0,hid=-1;const police=closestRoadBuilding(b.x,b.y,'police');const distance=police?roadServiceDistance(b,police):80;const localCoverage=clamp(1-distance/60,0,1)*policePower();
      if(b.kind==='home'){const h=G.households[b.hh];if(!h?.people.length)return;if(h){hid=h.id;loss=Math.min(h.cash,rn(45,340)*(1-localCoverage*.38));h.cash-=loss;h.crimeLoss+=loss;h.crimeLossToday=(h.crimeLossToday||0)+loss;h.security=clamp(h.security-rn(5,14),0,100);h.stress=clamp(h.stress+2,0,100);}}
      else{const f=G.firms[b.firm];if(f){loss=Math.min(f.cash,rn(130,600)*(1-localCoverage*.38));f.cash-=loss;f.theft+=loss;f.expenses=(f.expenses||0)+loss}}
      // stolen cash is redistributed among agents; cannot disappear without a counterparty
      const suspects=G.households.filter(h=>h.id!==hid&&h.people.length);
      const offender=suspects.length?pick(suspects):null;if(offender)offender.cash+=loss;else G.region+=loss;
      let item={day:G.day,offender:offender?.id??-1,loss,resolved:false,text:(b.kind==='home'?'Burglary at '+G.households[b.hh].name+' cottage':'Theft at '+G.firms[b.firm].name)+'; reported loss '+money(loss)+'.',type:'bad',bid:b.id,hid};
      G.cases.unshift(item);G.cases.length=Math.min(G.cases.length,100);emergencyDispatch(b,'police');G.cumulative.crime+=1;story(item.text,'bad',b.id,hid);
    }
 }
 if(random()<.025*G.stats.population/300){const b=pick(G.buildings.filter(b=>b.kind!=='road'));if(b){const station=closestRoadBuilding(b.x,b.y,'fire');const distance=station?roadServiceDistance(b,station):80;const localResponse=clamp(1-distance/58,0,1)*defensePower();let damage=rn(1,16)*(1-localResponse*.78);emergencyDispatch(b,'fire');
     b.condition=clamp(b.condition-damage,0,100);G.cumulative.fires++;
     const recovery=Math.max(0,damage)*b.value/2500;let owner=b.kind==='home'?G.households[b.owner]:G.firms[b.firm];
     if(owner&&owner.cash){let paid=Math.min(owner.cash,recovery);owner.cash-=paid;if(b.kind==='home')owner.propertyMaintenance=(owner.propertyMaintenance||0)+paid;else owner.expenses=(owner.expenses||0)+paid;G.region+=paid;b.condition=clamp(b.condition+paid*2500/b.value,0,100)}
     story('A fire damaged '+(types[b.kind]?types[b.kind].n:'property')+'; estimated '+fmt(damage)+' condition points lost.','bad',b.id)
 }}
}
function recompute(){
 let people=G.people.filter(p=>!p.deceased&&p.movedAway!==true).length,working=G.people.filter(p=>!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=70),employed=working.filter(p=>(p.job>=0&&!p.commuteBlocked)||p.publicWork).length,poor=G.households.filter(h=>h.people.length>0&&(householdLiquidity(h)/Math.max(1,h.people.length)<150||h.stress>65)).length;
 const safety=clamp(Math.round(60+policePower()*34+G.policy.outreachBudget*(G.actualServiceFunding?.outreach??1)/30-poor/Math.max(1,G.households.filter(h=>h.people.length>0).length)*28),0,100);
 const businessCount=G.firms.filter(f=>!f.closed).length;
 const oldStats=G.stats||{};
 G.stats={population:people,employed,workforce:working.length,employment:working.length?Math.round(employed/working.length*100):100,unemployment:working.length?Math.round((working.length-employed)/working.length*100):0,
   hardship:Math.round(poor/Math.max(1,G.households.filter(h=>h.people.length>0).length)*100),safety,preparedness:Math.round(defensePower()*100),businesses:businessCount,
   cash:G.households.reduce((s,h)=>s+h.cash,0),businessCash:G.firms.reduce((s,f)=>s+f.cash,0),dailyCrime:G.cases.filter(c=>c.day>G.day-30).length,
   income:G.households.reduce((s,h)=>s+h.income,0),townBalance:G.treasury+(G.publicReserve||0)-G.debt};
 for(let k of ['health','education','wellbeing','marketConfidence','roadCondition','roadService','militia','realWages','prosperity','avgCash','compliance','propertyCosts','airPollution'])if(oldStats[k]!=null&&Number.isFinite(oldStats[k]))G.stats[k]=oldStats[k];
 G.stats.health=Math.round(G.health??74);G.stats.education=Math.round(G.education??46);if(G.day%10===1||!G.roadMetrics)G.roadMetrics=roadMetrics();G.stats.roadAccess=G.roadMetrics.totalFirms?Math.round(G.roadMetrics.connectedFirms/G.roadMetrics.totalFirms*100):100;
 if(G.stats.wellbeing==null)G.stats.wellbeing=72;if(G.stats.marketConfidence==null)G.stats.marketConfidence=60;
}
// === MARKET CITY: ENDOGENOUS PRIVATE URBAN DEVELOPMENT ===
// Municipal policy affects the expected returns. Construction itself is paid
// by investors or existing firms, not awarded to the player for free.

// SOURCE: 35-goods-accounts.js
function stockTotals(){
 const totals=Object.fromEntries(Object.keys(goods).map(k=>[k,0]));
 for(const f of G.firms)for(const k of Object.keys(goods))totals[k]+=Number(f.stock[k])||0;
 for(const s of G.freight||[])totals[s.good]=(totals[s.good]||0)+s.qty;
 return totals;
}
function ensureGoodsAccounts(){
 if(!G.goodsAccounts){const opening=stockTotals();G.goodsAccounts=Object.fromEntries(Object.keys(goods).map(k=>[k,{opening:opening[k],produced:0,consumed:0,imports:0,exports:0}]));}
 const missing=Object.keys(goods).filter(k=>!G.goodsAccounts[k]);if(missing.length){const opening=stockTotals();for(const k of missing)G.goodsAccounts[k]={opening:opening[k],produced:0,consumed:0,imports:0,exports:0};}
 G.goodsPrices=G.goodsPrices||{...goods};
}
function goodsEntry(good,category,qty){if(!(qty>0)||!G.goodsAccounts?.[good])return;
 // Preserve low-order increments across decades of paid fractional deliveries.
 // This is numerical carry, never a balancing entry or a change to stock/cash.
 G.goodsCompensation=G.goodsCompensation||{};const carry=G.goodsCompensation[good]||(G.goodsCompensation[good]={}),a=G.goodsAccounts[good],adjusted=qty-(carry[category]||0),total=a[category]+adjusted;carry[category]=(total-a[category])-adjusted;a[category]=total;
}
function expectedCommodityStock(good,a){
 const c=G.goodsCompensation?.[good]||{},terms=[a.opening,a.produced,a.imports,-a.consumed,-a.exports,-(c.produced||0),-(c.imports||0),c.consumed||0,c.exports||0];let sum=0,carry=0;
 for(const value of terms){const next=sum+value;carry+=Math.abs(sum)>=Math.abs(value)?(sum-next)+value:(value-next)+sum;sum=next;}return sum+carry;
}
function validateGoodsAccounting(data){
 if(data.goodsAccounts!=null){if(typeof data.goodsAccounts!=='object'||Array.isArray(data.goodsAccounts))return false;for(const [good,a] of Object.entries(data.goodsAccounts)){if(!owns(goods,good)||!a||['opening','produced','consumed','imports','exports'].some(k=>!Number.isFinite(a[k])||a[k]<0))return false;}}
 if(data.goodsCompensation!=null){if(typeof data.goodsCompensation!=='object'||Array.isArray(data.goodsCompensation))return false;for(const [good,c] of Object.entries(data.goodsCompensation)){if(!owns(goods,good)||!data.goodsAccounts?.[good]||!c||typeof c!=='object'||Array.isArray(c))return false;for(const [category,value] of Object.entries(c))if(!['produced','consumed','imports','exports'].includes(category)||!Number.isFinite(value)||Math.abs(value)>Math.max(1,data.goodsAccounts[good][category])*Number.EPSILON*2)return false;}}
 return true;
}
function marketPrice(good){return G?.goodsPrices?.[good]||goods[good]||1;}
function goodsBalance(){
 const stocks=stockTotals();
 return Object.entries(G.goodsAccounts||{}).map(([good,a])=>({good,...a,stock:stocks[good],error:stocks[good]-expectedCommodityStock(good,a),price:marketPrice(good)}));
}
function commodityPriceReview(){
 if(G.day%30!==0)return;
 const stocks=stockTotals(),demand={grain:0,flour:0,food:G.stats.population*1.6,logs:0,timber:0,stone:G.projects.length*4,manufactures:G.stats.population*.12};
 for(const f of G.firms){if(f.closed)continue;const recipe=formulas[f.kind];if(recipe?.inp)demand[recipe.inp]+=(recipe.amount||0)*Math.max(.15,f.workers.length/Math.max(1,f.jobs));}
 for(const k of Object.keys(goods)){const cover=stocks[k]/Math.max(20,demand[k]),scarcity=clamp(1-cover/5,-1,1),target=goods[k]*(1+scarcity*.22)*Math.pow(clamp(G.regionalDemand,.4,1.3),.10);G.goodsPrices[k]=clamp(G.goodsPrices[k]*.88+target*.12,goods[k]*.65,goods[k]*1.55);}
}

// SOURCE: 40-development.js
function cityDemand(){
 const residents=G.people.reduce((n,p)=>n+Number(!p.deceased&&p.movedAway!==true),0);
 const open=G.firms.filter(f=>!f.closed);
 const jobs=open.reduce((n,f)=>n+f.jobs,0);
 const employed=G.people.reduce((n,p)=>n+Number(!p.deceased&&p.movedAway!==true&&p.job>=0),0);
 const jobVacancy=Math.max(0,jobs-employed);
 const homes=G.buildings.reduce((n,b)=>n+(b.kind==='home'?1:b.kind==='apartment'?4:b.kind==='tower'?9:0),0)+(G.projects||[]).filter(p=>p.kind==='home').length;
 const residentHouseholds=G.households.filter(h=>h.people.length>0);
 const viable=residentHouseholds.filter(h=>householdLiquidity(h)>Math.max(180,h.people.length*125)).length;
 const incomes=residentHouseholds.length?viable/residentHouseholds.length:0;
 const hardship=G.stats.hardship||0;
 const demandJobs=clamp(jobVacancy/Math.max(1,jobs),0,1);
 const regulation=G.policy.zoningRestriction/100;
 const confidence=G.stats.marketConfidence||50;
 const targetPop=residents+clamp(jobVacancy*.42,0,45)+Math.max(0,residents*.018);
 const targetHomes=Math.ceil(targetPop/2.2);
 const housingPressure=clamp((targetHomes-homes)/Math.max(1,homes)*100+50+(incomes-.7)*15,0,100);
 const housingDemand=clamp((targetHomes-homes)*6+jobVacancy*.7+(confidence-50)*.32-hardship*.45-regulation*16,0,100);
 const kinds={};
 for(const f of open)kinds[f.kind]=(kinds[f.kind]||0)+1;
 const ratio=(kind,ideal)=>Math.max(0,Math.min(100,(residents/ideal/(kinds[kind]||.55)-1)*75));
 let applicants={
  grocer:ratio('grocer',45),bakery:ratio('bakery',76),farm:ratio('farm',90),
  mill:ratio('mill',130),forestry:ratio('forestry',170),sawmill:ratio('sawmill',190),
  contractor:ratio('contractor',105),quarry:ratio('quarry',135),tavern:ratio('tavern',145),
  fishery:ratio('fishery',245),wharf:waterfrontDemand(),factory:residents>=190?ratio('factory',280):0,warehouse:residents>=220?ratio('warehouse',290):0,office:residents>=240?ratio('office',310):0,college:residents>=320?ratio('college',600):0
 };
 const foodShort=G.firms.filter(f=>!f.closed&&f.kind==='grocer').some(f=>(f.stock.food||0)<35);
 if(foodShort){applicants.farm+=12;applicants.bakery+=10;applicants.grocer+=5}
 const businessDemand=Math.round(clamp(Math.max(...Object.values(applicants))*.75+(confidence-50)*.25-hardship*.17-G.policy.permitFee*.007-G.policy.businessRegulation*.11,0,100));
 const freeLots=G.buildings.length<T*T?countBuildableLots(15):0;
 return {residents,homes,jobs,jobVacancy,homeDemand:Math.round(housingDemand),housingPressure:Math.round(housingPressure),businessDemand,applicants,freeLots,confidence,hardship,auto:G.autoBuild!==false};
}
function countBuildableLots(radius){
 let n=0;for(let y=5;y<T-5;y++)for(let x=5;x<T-5;x++)if(Math.abs(x-27)+Math.abs(y-27)<radius&&canPlace(x,y))n++;
 return n;
}
function buildableCandidates(focus='housing'){
 const net=graph(),places=[];
 for(let y=3;y<T-3;y++)for(let x=3;x<T-3;x++){
  if(!canPlace(x,y))continue;
  const adjacent=roadOffsets.map(([dx,dy])=>roadId(x+dx,y+dy)).filter(id=>net.parts[id]===net.mainPart);
  if(!adjacent.length)continue;
  let houses=0,work=0,competition=0;
  for(const b of G.buildings){const d=Math.abs(b.x-x)+Math.abs(b.y-y);
   if(d>10)continue;
   if(b.kind==='home')houses+=1/(1+d*.3);
   if(b.firm>=0&&!G.firms[b.firm]?.closed)work+=1/(1+d*.3);
   if(focus==='business'&&b.kind==='grocer')competition+=1/(1+d*.35);
  }
  const edge=Math.abs(x-27)+Math.abs(y-27);
  const score=(focus==='housing'?work*2.2+houses*.65:houses*2.4+work*.75-competition*.15)-edge*.05+random()*1.7;
  places.push({x,y,score});
 }
 places.sort((a,b)=>b.score-a.score);
 return places;
}
function privateContract(cost){return financeConstruction(cost);}
function privatelyBuiltRoads(demand){
 if(G.region<40000||G.policy.zoningRestriction>=90||demand.residents<145||demand.freeLots>75||(demand.homeDemand<20&&demand.businessDemand<25))return false;
 const net=graph(),plans=[];
 for(const [id,links] of net.neighbors){if(net.parts[id]!==net.mainPart)continue;const x=id%T,y=id/T|0;
  for(const [dx,dy] of roadOffsets){if(links.includes(roadId(x+dx,y+dy)))continue;
   const cells=[];let connects=false,valid=true;
   for(let k=1;k<=8;k++){const xx=x+dx*k,yy=y+dy*k,n=roadId(xx,yy);
    if(xx<5||xx>T-6||yy<5||yy>T-6){valid=false;break;}
    if(G.tiles[n]===1){connects=k>=5;break;}
    if(!charterOwns(xx,yy)||![0,3].includes(G.tiles[n])||G.landUse?.[n]||buildingAt(xx,yy)){valid=false;break;}
    // No one-lot parallel strips; leave space for real blocks and legal plots.
    if(k>2&&roadOffsets.some(([ax,ay])=>(ax*dx+ay*dy===0)&&cityCell(xx+ax,yy+ay)===1)){valid=false;break;}
    cells.push(n);
   }
   if(!valid||cells.length<5)continue;
   const end=fromEnd(cells),score=(connects?10:0)+cells.length+Math.min(8,Math.abs(end%T-27)+Math.abs((end/T|0)-27))*.12;
   plans.push({cells,score});
  }
 }
 plans.sort((a,b)=>b.score-a.score);const plan=plans[0];if(!plan)return false;
 const cost=plan.cells.length*buildCost.road;if(!privateContract(cost))return false;
 G.roadClasses=G.roadClasses||{};G.streetNames=G.streetNames||{};const name=['Elm','Westgate','Cedar','Victoria','Meadow','Foundry'][(G.development.roads||0)%6]+' Street';
 for(const id of plan.cells){G.tiles[id]=1;G.privateRoads.push(id);G.roadClasses[id]='local';G.streetNames[id]=name;ensureRoadWear();G.roadWear[id]=100;}
 G.development.roads+=plan.cells.length;G.development.privateSpend=(G.development.privateSpend||0)+cost;G.construction+=plan.cells.length;invalidateRoads(false);staticDirty=true;dirty=true;
 story('A funded '+name+' extension opened a connected block for development.','good');return true;
}
function startDevelopmentProject(kind,place,value,days,extra={}){
 const target=kind==='firm'?extra.firmKind:kind;
 if(!canPlace(place.x,place.y,true,target))return null;
 const b={id:G.nextId++,kind:'worksite',x:place.x,y:place.y,value,condition:100,owner:-1,firm:-1,hh:-1,developer:true,footprint:footprintFor(place.x,place.y,target)};
 for(const id of b.footprint)if(G.tiles[id]===3)G.tiles[id]=0;
 G.buildings.push(b);
 G.projects.push({id:b.id,kind,remaining:days,duration:days,start:G.day,...extra});
 staticDirty=true;dirty=true;
 G.development.started=(G.development.started||0)+1;
 return b;
}
function completeDevelopmentProjects(){
 if(!G.projects?.length)return;
 let changed=false;
 for(let i=G.projects.length-1;i>=0;i--){
  const p=G.projects[i];if(!constructionWork(p))continue;p.remaining--;
  if(p.remaining>0)continue;
  if(p.kind==='fields'){G.projects.splice(i,1);completeFarmFields(p);changed=true;continue;}
  const b=readBuild(p.id);
  G.projects.splice(i,1);
  if(!b)continue;
  if(p.kind==='public'){b.kind=p.publicKind;b.title={kind:'municipal',id:0};b.owner=-1;story(types[b.kind].n+' opened after publicly financed construction.','good',b.id);
  }else if(p.kind==='home'){
   b.kind='home';b.value=p.value;b.baseValue=p.value;b.developer=true;b.owner=-2;b.title={kind:'investor',id:0};
   b.hh=-1;if(!G.homes.includes(b.id))G.homes.push(b.id);G.development.homes++;
   story('Cottage construction finished. The home is available to local households and workers with job prospects.','good',b.id);
  }else if(p.kind==='redevelop'){
   completeRedevelopment(b,p);
  }else if(p.kind==='airport'){
   completeAirfield(b,p);
  }else if(p.kind==='firm'){
   b.kind=p.firmKind;b.value=types[b.kind].cost*10;
   const capital=Math.min(p.capital,Math.max(0,G.region-1000));
   const fee=Math.min(G.policy.permitFee,Math.max(0,G.region-capital));
   G.region-=capital+fee;
   const f=createFirm(b.kind,b.x,b.y,true,()=>b);
   f.cash=capital;transferTreasury(fee,'permits');
   if(G.policy.lendingRules<70&&(G.stats.marketConfidence||50)>48&&G.day%3===0){const loan=bankLoan('firm',f.id,Math.round(Math.min(2400,capital*.17)),480);if(loan)f.jobs=Math.min(18,f.jobs+1)}
   G.development.firms++;
   story('New private enterprise completed: '+f.name+' opened its doors.','good',b.id);
  }
  G.construction++;changed=true;
 }
 if(changed){invalidateRoads(false);recompute();assignJobs();staticDirty=true;dirty=true}
}
function privatelyBuiltHome(demand){
 if(demand.homeDemand<9||demand.hardship>57||demand.confidence<22||G.region<35000||demand.residents>=2000||G.policy.zoningRestriction>=94)return false;
 const approval=clamp(1-G.policy.zoningRestriction/125-G.policy.propertyTax/18,0,1);
 if(random()>approval)return false;
 const lots=buildableCandidates('housing');if(!lots.length)return false;
 const place=lots[0],quote=developmentQuote(place,'home',demand),cost=quote.cost;
 if(quote.expected<=0){G.development.lastRejected={day:G.day,reason:'Expected housing yield below funding hurdle',...quote};return false;}
 const savings=clamp(Math.round(rn(1250,3900)),500,4500);
 if(G.region<cost+savings+10000)return false;
 const value=Math.round(38000+demand.housingPressure*240);
 const site=startDevelopmentProject('home',place,value,18+Math.round(rn(0,14)),{value,savings});
 if(!site)return false;privateContract(cost);explainDevelopment(site,quote,'housing');
 G.development.privateSpend=(G.development.privateSpend||0)+cost;
 story('A housing developer broke ground for a privately financed cottage.','good',site.id);
 return true;
}
function privatelyBuiltFirm(demand){
 if(demand.businessDemand<17||demand.hardship>70||G.region<120000||G.policy.permitFee>2800||G.policy.zoningRestriction>=90)return false;
 const capacity=G.people.filter(p=>!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=70&&p.job<0).length;
 if(capacity<3&&!(demand.confidence>48&&demand.homeDemand>15&&G.region>250000))return false;
 const ranked=Object.entries(demand.applicants).sort((a,b)=>b[1]-a[1]);
 const approval=clamp(.65+(demand.confidence-50)/160-G.policy.businessRegulation/180-G.policy.profitTax/130,0.07,.95);
 if(random()>approval)return false;
 const candidates=buildableCandidates('business');
 let kind=null,place=null;
 for(const [choice,score] of ranked){
  if(score<13)break;
  const competitors=G.firms.filter(f=>f.kind===choice&&!f.closed&&f.age>45);
  if(competitors.length>=2&&competitors.filter(f=>f.netProfit< -75).length>competitors.length*.55)continue;
  const spot=candidates.find(v=>canPlace(v.x,v.y,true,choice));
  if(spot){kind=choice;place=spot;break}
 }
 if(!kind||!place)return false;
 const quote=developmentQuote(place,kind,demand);if(quote.expected<=0){G.development.lastRejected={day:G.day,reason:'Expected enterprise yield below funding hurdle',...quote};return false;}
 const capital=11500+Math.round(rn(0,7000));
 const fee=G.policy.permitFee,buildingCost=types[kind].cost;
 if(G.region<capital+fee+buildingCost+25000)return false;
 const site=startDevelopmentProject('firm',place,types[kind].cost*10,24+Math.round(rn(0,20)),{firmKind:kind,capital});
 if(!site)return false;privateContract(buildingCost);explainDevelopment(site,quote,kind);
 G.development.privateSpend=(G.development.privateSpend||0)+buildingCost+capital;
 story('Private investors started building a '+types[kind].n.toLowerCase()+' after evaluating market demand.','good',site.id);
 return true;
}
function stationHubs(){
 const candidates=buildableCandidates('business').filter(c=>canPlace(c.x,c.y,true,'metro_station'));
 return candidates.map(c=>{let residents=0,workplaces=0;
  for(const b of G.buildings){const d=Math.abs(b.x-c.x)+Math.abs(b.y-c.y);if(d<=7){if(b.kind==='home')residents+=8-d;if(b.firm>=0&&!G.firms[b.firm]?.closed)workplaces+=10-d;}}
  return {...c,demand:residents+workplaces*1.35};
 }).sort((a,b)=>b.demand-a.demand);
}
function stationBuilding(place){
 if(!canPlace(place.x,place.y,true,'metro_station'))return null;
 const b={id:G.nextId++,kind:'metro_station',x:place.x,y:place.y,value:180000,condition:100,owner:-1,firm:-1,hh:-1,private:true,footprint:footprintFor(place.x,place.y,'metro_station')};
 G.buildings.push(b);G.metro.stations.push(b.id);G.development.stations++;return b;
}
function connectMetro(a,b,newStations=0){
 const len=Math.abs(a.x-b.x)+Math.abs(a.y-b.y);
 const price=buildCost.metro_station*newStations+len*1100;
 // The two station buildings have already been created before this function is called.
 if(G.metro.cash<price)return false;
 G.metro.cash-=price;
 const share=price*.24;
 const constructors=G.firms.filter(f=>f.kind==='contractor'&&!f.closed);
 if(constructors.length){const c=constructors[G.day%constructors.length];c.cash+=share;c.revenue+=share;G.region+=price-share;}
 else G.region+=price;
 G.metro.lines.push({from:a.id,to:b.id,length:len,built:G.day,readyDay:G.day+85,color:['#e4ba67','#7cb5ba','#b78cb9','#cf887d'][G.metro.lines.length%4]});
 G.metro.invested+=price;G.development.privateSpend=(G.development.privateSpend||0)+price;
 return true;
}
function metroExpansion(demand){
 if(!G.metro||G.policy.zoningRestriction>=92||demand.residents<350||G.region<160000)return false;
 if(demand.confidence<40||demand.hardship>45)return false;
 const hubs=stationHubs();if(hubs.length<2)return false;
 const metro=G.metro;
 // Private shareholders subscribe equity; the franchise pays its construction bills.
 if(!metro.stations.length){
  const a=hubs[0],b=hubs.find(p=>Math.abs(p.x-a.x)+Math.abs(p.y-a.y)>=11&&p.demand>10);
  if(!b)return false;
  const route=Math.abs(a.x-b.x)+Math.abs(a.y-b.y),cost=2*buildCost.metro_station+route*1100;
  if(G.region<cost+100000)return false;
  const shares=cost+36000;
  G.region-=shares;metro.cash+=shares;
  const aa=stationBuilding(a),bb=stationBuilding(b);
  if(!aa||!bb)throw Error('Metro land reservation failed');
  if(!connectMetro(aa,bb,2))throw Error('Underground capital budget mismatch');
  metro.operating=false;G.construction+=2;staticDirty=true;dirty=true;
  story('Private investors opened the Vale Underground: a two-station railway financed from subscribed shares and fares. Inspect the rail network in the map overlays.','good',aa.id);
  return true;
 }
 // Extensions need an observed passenger market and sufficient retained earnings.
 if(demand.residents<540+metro.stations.length*90||metro.cash<70000||metro.stations.length>=8||metro.rides<250)return false;
 const existing=metro.stations.map(id=>readBuild(id)).filter(Boolean);
 const outer=hubs.find(c=>existing.every(s=>Math.abs(s.x-c.x)+Math.abs(s.y-c.y)>=9)&&c.demand>18);
 if(!outer)return false;
 const near=existing.slice().sort((a,b)=>Math.abs(a.x-outer.x)+Math.abs(a.y-outer.y)-Math.abs(b.x-outer.x)-Math.abs(b.y-outer.y))[0];
 const cost=buildCost.metro_station+(Math.abs(near.x-outer.x)+Math.abs(near.y-outer.y))*1100;
 if(metro.cash<cost+18000)return false;
 const station=stationBuilding(outer);
 if(!station)return false;
 if(!connectMetro(near,station,1))throw Error('Underground extension budget mismatch');
 G.construction++;staticDirty=true;dirty=true;
 story('The privately owned Vale Underground extended its railway to a new neighbourhood.','good',station.id);
 return true;
}
function hasMetroCommute(home,work){
 const metro=G?.metro;
 if(!home||!work||!metro?.operating||!metro.lines?.length)return false;
 if(Math.abs(home.x-work.x)+Math.abs(home.y-work.y)<7)return false;
 // Stops within walking distance of the origin and destination, plus connected lines.
 const start=metro.stations.filter(id=>{const b=readBuild(id);return b&&Math.abs(b.x-home.x)+Math.abs(b.y-home.y)<=6;});
 const goal=new Set(metro.stations.filter(id=>{const b=readBuild(id);return b&&Math.abs(b.x-work.x)+Math.abs(b.y-work.y)<=6;}));
 if(!start.length||!goal.size)return false;
 const visited=new Set(start),queue=start.slice();
 for(let i=0;i<queue.length;i++){
  const at=queue[i];if(goal.has(at))return true;
  for(const line of metro.lines){if(line.readyDay>G.day)continue;const next=line.from===at?line.to:line.to===at?line.from:null;
   if(next!=null&&!visited.has(next)){visited.add(next);queue.push(next)}
  }
 }
 return false;
}
function metroOperatingDay(){
 const metro=G?.metro;if(!metro?.stations?.length)return;
 const openLines=metro.lines.filter(line=>!line.readyDay||line.readyDay<=G.day);if(!openLines.length){metro.operating=false;return;}
 const cost=5+metro.stations.length*3+metro.lines.length*5+metro.dailyRides*.025;
 const paid=Math.min(metro.cash,cost);
 metro.cash-=paid;G.region+=paid;metro.expenses+=paid;
 metro.operating=metro.cash>=cost;
 if(metro.revenue-paid<0)metro.daysInDeficit++;
 else metro.daysInDeficit=Math.max(0,metro.daysInDeficit-1);
 if(!metro.operating&&G.day%30===0)story('The private underground suspended trains after its operating reserve ran out.','bad');
 metro.dailyRides=0;
}
function drawMetroOverlay(g,subdued=false){
 if(!G.metro?.lines?.length)return;
 g.save();g.lineWidth=5;g.globalAlpha=subdued?.28:.90;
 for(let i=0;i<G.metro.lines.length;i++){
  const line=G.metro.lines[i],a=readBuild(line.from),b=readBuild(line.to);
  if(!a||!b)continue;
  const p=iso(a.x,a.y),q=iso(b.x,b.y);
  g.strokeStyle='#17232c';g.lineWidth=9;g.beginPath();g.moveTo(p[0],p[1]);g.lineTo(q[0],q[1]);g.stroke();
  g.strokeStyle=line.color;g.lineWidth=4;g.setLineDash([10,5]);g.beginPath();g.moveTo(p[0],p[1]);g.lineTo(q[0],q[1]);g.stroke();g.setLineDash([]);
  if(G.metro.operating&&(!line.readyDay||line.readyDay<=G.day)){
   const phase=(frameClock*.115+i*.21)%2,t=phase<=1?phase:2-phase;
   const xx=p[0]+(q[0]-p[0])*t,yy=p[1]+(q[1]-p[1])*t;
   g.save();g.translate(xx,yy);g.rotate(Math.atan2(q[1]-p[1],q[0]-p[0]));
   g.fillStyle='#f2e8c7';g.strokeStyle='#182c32';g.lineWidth=1.3;
   for(let wagon=-1;wagon<=1;wagon++){g.fillRect(wagon*12-5,-4,10,8);g.strokeRect(wagon*12-5,-4,10,8);
    g.fillStyle=line.color;g.fillRect(wagon*12-3,-3,6,3);g.fillStyle='#f2e8c7';}
   g.restore();
  }
 }
 if(!subdued)for(const id of G.metro.stations){const s=readBuild(id);if(!s)continue;let [x,y]=iso(s.x,s.y);
  g.fillStyle='#17232c';g.beginPath();g.arc(x,y,14,0,Math.PI*2);g.fill();g.fillStyle='#f6d17c';g.beginPath();g.arc(x,y,10,0,Math.PI*2);g.fill();g.fillStyle='#203035';g.font='bold 13px sans-serif';g.textAlign='center';g.fillText('M',x,y+4);
 }
 g.restore();
}
// Regional economy. Decisions are derived from physical land, capital and
// observable demand. The city player sets rules; agents invest their own funds.
function regionalIndustryDay(){
 if(!G)return;
 let factories=0,depots=0;
 for(const f of G.firms){
  if(f.closed)continue;
  if(f.kind==='factory')factories++;
  if(f.kind==='warehouse'){
   depots++;
   const freight=Math.min(G.region,290+Math.min(300,G.firms.filter(v=>!v.closed).length*3));
   G.region-=freight;f.cash+=freight;f.revenue+=freight;
  }else if(f.kind==='office'){
   const services=Math.min(G.region,390+Math.max(0,G.stats.marketConfidence-40)*3);
   G.region-=services;f.cash+=services;f.revenue+=services;
  }else if(f.kind==='college'){
   const students=G.households.filter(h=>h.cash>900&&h.people.some(id=>{const p=G.people[id];return p&&!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=28})).slice(0,36);
   for(const h of students){const fee=Math.min(h.cash,8.5);h.cash-=fee;h.educationExpense=(h.educationExpense||0)+fee;f.cash+=fee;f.revenue+=fee;const candidate=h.people.map(id=>G.people[id]).find(p=>p&&!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=28);
    if(candidate)candidate.skill=clamp(candidate.skill+.00007,0,1.1);
   }
   const research=Math.min(G.region,200);G.region-=research;f.cash+=research;f.revenue+=research;
   G.education=clamp(G.education+.002,0,100);
  }
 }
 G.stats.airPollution=clamp(factories*6+depots*1.5+(G.airport?.operating?4:0)-G.buildings.filter(b=>b.kind==='park').length*.6,0,100);
 // Pollution affects specific nearby families rather than a free-floating score.
 if(factories&&G.day%10===0){const plants=G.firms.filter(f=>f.kind==='factory'&&!f.closed).map(f=>readBuild(f.building)).filter(Boolean);
  for(const h of G.households){const home=readBuild(h.home);if(!home)continue;
   if(plants.some(b=>Math.abs(b.x-home.x)+Math.abs(b.y-home.y)<=4))h.stress=clamp(h.stress+.18,0,100);
  }
 }
}
function fieldLotsNear(farm,limit=6){
 const site=readBuild(farm.building);if(!site)return [];
 const result=[];
 for(let radius=1;radius<=6;radius++)for(let dy=-radius;dy<=radius;dy++)for(let dx=-radius;dx<=radius;dx++){
  if(Math.abs(dx)+Math.abs(dy)!==radius)continue;
  const x=site.x+dx,y=site.y+dy,id=roadId(x,y);
  if(!charterOwns(x,y)||x<3||y<3||x>=T-3||y>=T-3||G.tiles[id]!==0||G.landUse?.[id]||buildingAt(x,y))continue;
  // Grow a continuous farm belt, not isolated strips inside the central square.
  const civicDistance=Math.abs(x-27)+Math.abs(y-27);
  if(civicDistance<8)continue;
  result.push({id,x,y,score:(civicDistance>17?4:0)+(Math.abs(dx)+Math.abs(dy))*-.22+(G.tiles[roadId(x-1,y)]===3?.3:0)});
 }
 result.sort((a,b)=>b.score-a.score);
 return result.slice(0,limit);
}
function farmDistrictExpansion(demand){
 if(demand.residents<115||G.policy.zoningRestriction>=95||G.region<25000)return false;
 const farms=G.firms.filter(f=>f.kind==='farm'&&!f.closed&&f.cash>300);
 if(!farms.length)return false;
 const shortages=G.firms.filter(f=>f.kind==='mill'&&!f.closed).some(f=>(f.stock.grain||0)<70);
 let chosen=null,lots=[];
 for(const f of farms.sort((a,b)=>(G.fieldCount?.[a.id]||0)-(G.fieldCount?.[b.id]||0))){
  if((G.fieldCount?.[f.id]||0)>=15)continue;
  if(G.projects.some(p=>p.kind==='fields'&&p.firmId===f.id))continue;
  const possible=fieldLotsNear(f,4+Math.round(demand.residents/500));
  if(possible.length>=2){chosen=f;lots=possible;break}
 }
 if(!chosen)return false;
 if(!shortages&&(G.development.fields||0)>demand.residents*.14&&random()<.65)return false;
 const investment=lots.length*480;
 if(G.region<investment+10000)return false;
 G.landUse=G.landUse||{};G.fieldOwner=G.fieldOwner||{};G.projects=G.projects||[];
 for(const item of lots){G.landUse[item.id]=2;G.fieldOwner[item.id]=chosen.id;}
 const id=G.nextId++;
 G.projects.push({id,kind:'fields',firmId:chosen.id,plots:lots.map(v=>v.id),remaining:16+Math.ceil(lots.length/2),start:G.day});
 privateContract(investment);
 G.development.privateSpend=(G.development.privateSpend||0)+investment;
 staticDirty=true;dirty=true;
 story('A farmers’ cooperative cleared and planted '+lots.length+' plots of cropland outside town.','good',chosen.building);
 return true;
}
function completeFarmFields(project){
 G.fieldCount=G.fieldCount||{};
 let planted=0;
 for(const id of project.plots||[]){
  if(G.landUse?.[id]!==2||G.fieldOwner?.[id]!==project.firmId)continue;
  G.landUse[id]=1;planted++;
 }
 G.fieldCount[project.firmId]=(G.fieldCount[project.firmId]||0)+planted;
 G.development.fields=(G.development.fields||0)+planted;
 G.construction+=planted;
 story('Harvest fields established: '+planted+' new plots are producing crops.','good',G.firms[project.firmId]?.building||-1);
 staticDirty=true;dirty=true;
}
function ownerCompensation(building){
 if(building.owner===-2)return 0;
 const seller=G.households[building.owner],price=building.value*1.05,investor=propertyInvestor();
 if(G.region<price)return 0;
 G.region-=price;investor.cash+=price;investor.invested+=price;book('Regional capital',investor.name,price,'Equity subscription for property acquisition',building.id);
 investor.cash-=price;if(seller)seller.cash+=price;else G.region+=price;
 book(investor.name,seller?seller.name+' household':'Regional landowner',price,'Property acquisition with protected tenancy',building.id);
 building.owner=-2;building.title={kind:'investor',id:0};return price;
}
function urbanRedevelopment(demand){
 if(demand.residents<290||demand.confidence<33||demand.hardship>65||G.policy.zoningRestriction>=78)return false;
 if(G.projects.some(p=>p.kind==='redevelop'))return false;
 const taller=demand.residents>=620&&G.policy.zoningRestriction<=53&&demand.housingPressure>=37;
 const target=taller?'tower':'apartment',maxUnits=taller?9:4;
 if(demand.homeDemand<12&&demand.housingPressure<58)return false;
 let candidates=G.buildings.filter(b=>b.kind==='home'||(taller&&b.kind==='apartment'));
 candidates=candidates.filter(b=>!b.redevelopment&&nearRoad(b.x,b.y)&&Math.abs(b.x-27)+Math.abs(b.y-27)<(taller?22:27)&&
  (footprintOf(b).length>=4||canPlace(b.x,b.y,true,target,b)));
 candidates.sort((a,b)=>{
  const av=(Math.abs(a.x-27)+Math.abs(a.y-27))*1.4+(a.kind==='apartment'?2:0)+(a.units?.length||1)*2;
  const bv=(Math.abs(b.x-27)+Math.abs(b.y-27))*1.4+(b.kind==='apartment'?2:0)+(b.units?.length||1)*2;
  return av-bv;
 });
 const b=candidates[0];if(!b)return false;
 const cost=target==='tower'?155000:39000;
 if(G.region<cost+b.value*1.05+80000)return false;
 ownerCompensation(b);
 b.redevelopment={kind:target,started:G.day,remaining:target==='tower'?75:38};
 const occupants=b.units||[b.hh];for(const id of occupants){const h=G.households[id];if(h?.people.length)h.temporaryHousing={project:b.id,since:G.day,provider:'Prepaid regional relocation contract'};}
 if(footprintOf(b).length<4)reserveFootprint(b,target);
 G.projects.push({id:b.id,kind:'redevelop',target,remaining:b.redevelopment.remaining,duration:b.redevelopment.remaining,start:G.day,formerValue:b.value,priorKind:b.kind,units:maxUnits});
 privateContract(cost);
 G.development.privateSpend=(G.development.privateSpend||0)+cost;
 staticDirty=true;dirty=true;
 story('A private developer acquired planning approval to replace '+(b.kind==='apartment'?'an older apartment house':'a cottage')+' with a '+(taller?'residential tower':'four-unit apartment block')+'.','neutral',b.id,b.hh);
 return true;
}
function addHouseholdAt(building,capital=1700){
 if(G.day>1){const vacancies=G.firms.filter(f=>!f.closed).reduce((n,f)=>n+Math.max(0,f.jobs-f.workers.length),0),seekers=Math.max(0,G.stats.workforce-G.stats.employed);if(vacancies-seekers<2||G.stats.employment<88)return null;}

 if(G.people.filter(p=>!p.deceased&&p.movedAway!==true).length>=2000)return null;
 const cash=Math.min(G.region,capital);if(cash<500)return null;
 G.region-=cash;
 const h={id:G.households.length,name:pick(surnames),cash,home:building.id,owner:-1,people:[],income:0,rent:0,food:0,tax:0,incomeTax:0,energyTax:0,utilities:0,travel:0,aid:0,crimeLoss:0,stress:27,security:86,last:[],worklessness:0};
 G.households.push(h);
 const occupants=Math.min(2,2000-G.people.filter(p=>!p.deceased&&p.movedAway!==true).length);
 for(let j=0;j<occupants;j++){
  const p={id:G.people.length,name:pick(first)+' '+h.name,age:Math.floor(rn(20,54)),skill:rn(.35,1),health:rn(65,97),hh:h.id,job:-1,life:rn(45,80),last:[]};G.people.push(p);h.people.push(p.id);
 }
 if(G.day>1){assignJobs();recompute();}return h;
}
function completeRedevelopment(b,p){
 const existing=b.kind==='apartment'?(b.units||[]).slice():(b.hh>=0?[b.hh]:[]);
 for(const id of existing){if(G.households[id])delete G.households[id].temporaryHousing;}
 b.replacedKind=p.priorKind||b.kind;b.kind=p.target;b.owner=-2;b.title={kind:'investor',id:0};b.redevelopment=null;b.lastRedeveloped=G.day;
 b.value=p.target==='tower'?560000:175000;
 b.units=existing;
 for(let k=b.units.length;k<p.units;k++){
  const h=addHouseholdAt(b,1800+Math.round(rn(0,2500)));
  if(!h)break;b.units.push(h.id);
 }
 if(b.units.length)b.hh=b.units[0];
 G.development.redevelopments=(G.development.redevelopments||0)+1;
 if(p.target==='tower')G.development.towers=(G.development.towers||0)+1;
 story('A '+(p.target==='tower'?'high-rise':'mid-rise apartment block')+' opened where older housing once stood. Existing residents retained homes; vacant units are offered subject to local demand.','good',b.id,b.hh);
}
function airfieldCandidate(){
 const net=graph();const options=[];
 const vectors=[[1,0],[0,1]];
 for(let y=7;y<T-7;y++)for(let x=7;x<T-7;x++){
  if(!canPlace(x,y,true,'airport'))continue;
  const adjoining=roadOffsets.map(([dx,dy])=>roadId(x+dx,y+dy)).find(id=>net.parts[id]===net.mainPart);
  if(adjoining==null)continue;
  const distance=Math.abs(x-27)+Math.abs(y-27);
  if(distance<12||distance>36)continue;
  for(const [dx,dy] of vectors){const runway=[];
   for(let i=2;i<=7;i++)for(let w=0;w<2;w++){
    const xx=x+dx*i+(dy?w:0),yy=y+dy*i+(dx?w:0),id=roadId(xx,yy);
    if(!charterOwns(xx,yy)||xx<3||yy<3||xx>=T-3||yy>=T-3||![0,3].includes(cityCell(xx,yy))||G.landUse?.[id]||buildingAt(xx,yy)){runway.length=0;break}
    runway.push(id);
   }
   if(runway.length!==12)continue;
   options.push({x,y,runway,score:distance*.22+random()*1.2});
  }
 }
 options.sort((a,b)=>b.score-a.score);
 return options[0];
}
function airfieldInvestment(demand){
 if(G.airport||demand.residents<520||demand.confidence<38||G.policy.zoningRestriction>=72||G.region<850000)return false;
 const site=airfieldCandidate();if(!site)return false;
 const outlay=225000;
 const terminal=startDevelopmentProject('airport',site,450000,120,{runway:site.runway});
 if(!terminal)return false;
 G.airport={building:terminal.id,firm:null,runway:site.runway,operating:false,passengers:0,freight:0,flights:0,initialCost:outlay,started:G.day};
 G.landUse=G.landUse||{};
 for(const id of site.runway){G.landUse[id]=2;if(G.tiles[id]===3)G.tiles[id]=0;}
 privateContract(outlay);
 G.development.privateSpend=(G.development.privateSpend||0)+outlay;
 staticDirty=true;dirty=true;
 story('A regional aviation company began constructing an airfield and runway with subscribed private capital.','good',terminal.id);
 return true;
}
function completeAirfield(b,p){
 if(!G.airport||G.airport.building!==b.id)return;
 b.kind='airport';b.value=780000;b.private=true;
 for(const id of p.runway||[])if(G.landUse?.[id]===2)G.landUse[id]=3;
 const capital=Math.min(G.region,140000);G.region-=capital;
 const f=createFirm('airport',b.x,b.y,true,()=>b);
 f.cash=capital;f.wage=36;f.jobs=6;f.kind='airport';
 G.airport.firm=f.id;G.airport.operating=true;
 G.development.airfields=(G.development.airfields||0)+1;
 story('The privately financed regional airfield opened. Tickets, freight and visitors now support its operation.','good',b.id);
}
function airfieldOperatingDay(){
 const a=G.airport;if(!a||a.firm==null)return;
 const f=G.firms[a.firm];if(!f||f.closed){a.operating=false;return}
 const residents=G.people.reduce((n,p)=>n+Number(!p.deceased&&p.movedAway!==true),0);
 if(f.workers.length<3){a.operating=false;a.dailyFlights=0;return;}
 const visitors=Math.max(0,Math.min(76,Math.floor((residents*.015+(G.stats.marketConfidence||55)*.05)*(G.regionalDemand||1))));
 const flights=Math.max(1,Math.ceil(visitors/19)),receipts=Math.min(G.region,visitors*42+flights*95);
 G.region-=receipts;f.cash+=receipts;f.revenue+=receipts;if(G.market)G.market.externalSales+=receipts;
 const fuel=Math.min(f.cash,flights*110+45);f.cash-=fuel;f.expenses+=fuel;G.region+=fuel;
 a.passengers+=visitors;a.freight+=flights*.4;a.flights+=flights;a.dailyFlights=flights;a.seats=19;a.loadFactor=visitors/(flights*19);
 a.operating=f.cash>1000;
 if(!a.operating&&G.day%30===0)story('The airfield faces a cash crisis; scheduled flights are suspended.','bad',a.building);
}
function paintDenseBuilding(g,b,x,y){
 const tower=b.kind==='tower',floors=tower?9:4,width=tower?31:27,h=floors*10;
 const by=y+TH/2+8;
 g.fillStyle='#1b2525aa';g.beginPath();g.ellipse(x+6,by+10,width,11,0,0,Math.PI*2);g.fill();
 g.fillStyle=tower?'#758b93':'#ad9c86';g.fillRect(x-width/2,by-h,width,h);
 g.fillStyle=tower?'#536973':'#846f5e';g.beginPath();g.moveTo(x+width/2,by-h);g.lineTo(x+width/2+15,by-h-7);g.lineTo(x+width/2+15,by-7);g.lineTo(x+width/2,by);g.fill();
 g.fillStyle=tower?'#a3bac0':'#dbcead';g.fillRect(x-width/2-2,by-h-6,width+4,6);
 for(let floor=0;floor<floors;floor++){
  for(let col=0;col<3;col++){
   g.fillStyle=((b.id+floor*3+col)%5===0)?'#e5c67b':tower?'#aec8cc':'#d7c19e';
   g.fillRect(x-width/2+4+col*(width-7)/3,by-h+7+floor*10,Math.max(3,(width-13)/3),5);
  }
 }
 g.fillStyle='#303d3d';g.fillRect(x-4,by-14,8,14);
 if(b.redevelopment){g.strokeStyle='#dcb86e';g.lineWidth=1.5;for(let i=-width/2;i<width/2;i+=12){g.beginPath();g.moveTo(x+i,by);g.lineTo(x+i,by-h+3);g.stroke()}}
}
function paintAirfieldTerminal(g,b,x,y){
 const by=y+TH/2+8;
 g.fillStyle='#26383b';g.fillRect(x-33,by-12,66,17);
 g.fillStyle='#afc5c0';g.fillRect(x-31,by-28,62,18);
 g.fillStyle='#506872';for(let i=-25;i<=23;i+=12)g.fillRect(x+i,by-23,8,10);
 g.fillStyle='#ebd49a';g.fillRect(x-34,by-32,68,5);
 g.fillStyle='#f2e5c4';g.font='bold 10px sans-serif';g.fillText('AIR',x-12,by-15);
 g.fillStyle='#dde8e3';g.beginPath();g.moveTo(x-17,by+2);g.lineTo(x+10,by-1);g.lineTo(x+19,by+3);g.lineTo(x+3,by+5);g.lineTo(x,by+10);g.lineTo(x-4,by+5);g.closePath();g.fill();
}

function autonomousDevelopment(){
 if(!G||!G.development)return;
 const demand=cityDemand();
 G.development.lastReport={day:G.day,homeDemand:demand.homeDemand,businessDemand:demand.businessDemand,freeLots:demand.freeLots,jobVacancy:demand.jobVacancy};
 if(!G.autoBuild)return;
 let built=[];
 if(privatelyBuiltRoads(demand))built.push('roads');
 if(privatelyBuiltHome(demand))built.push('housing');
 if(privatelyBuiltFirm(demand))built.push('business');
 if(metroExpansion(demand))built.push('underground');
 if(farmDistrictExpansion(demand))built.push('fields');
 if(urbanRedevelopment(demand))built.push('redevelopment');
 if(airfieldInvestment(demand))built.push('airfield');
 if(reverseRedevelopment())built.push('downzoning');
 if(built.length){
  G.development.decisions.push({day:G.day,kind:built.join(', '),demand:demand.homeDemand,commercial:demand.businessDemand});
  if(G.development.decisions.length>120)G.development.decisions.shift();
  recompute();assignJobs();
 }
}
function developmentPanel(){
 const d=G.development||{},p=d.lastReport||cityDemand(),m=G.metro||{stations:[],lines:[],cash:0,rides:0};
 const status=G.autoBuild?'Investors respond to demand automatically.':'Private construction paused by player.';
 return `<div class="statgrid">${stat('Housing demand',p.homeDemand+'/100')}${stat('Business demand',p.businessDemand+'/100')}${stat('Private road lots',d.roads||0)}${stat('Projects under construction',G.projects?.length||0)}${stat('Private road tolls',money(d.privateRoadTolls||0))}${stat('Private homes',d.homes||0)}${stat('New enterprises',d.firms||0)}${stat('Underground stations',m.stations.length)}${stat('Subway rides',fmt(m.rides||0))}${stat('Rail operator cash',money(m.cash||0))}${stat('Agricultural district plots',d.fields||0)}${stat('Apartment redevelopments',d.redevelopments||0)}${stat('Residential towers',d.towers||0)}${stat('Private airfields',d.airfields||0)}${stat('Downzoned properties',d.downzonings||0)}${stat('Regional passengers',fmt(G.airport?.passengers||0))}${stat('Industrial employers',G.firms.filter(f=>!f.closed&&['factory','warehouse','office'].includes(f.kind)).length)}</div>`+
 `<p class="desc">${esc(status)} Road developers finance extensions from regional capital; housing developers choose lots near jobs, and merchants enter underserved markets. Underground investors evaluate population and density, then fund stations and tunnels. Farmers acquire field plots and raise grain output; factory owners and freight depots respond to supply and demand; landlords may replace cottages with apartments or towers after assembling a site; and airport investors require a major regional market, a clear runway, and long-term operating capital. The railway pays ongoing costs from fares. Income, profit and property taxes, zoning and business rules influence investment.</p>`+
 `<p class="desc">${m.stations.length?esc('Vale Underground — '+(m.lines?.some(line=>line.readyDay>G.day)?'construction in progress':m.operating?'operating':'service suspended')+' · '+m.lines.length+' line(s) · '+money(m.fare)+' fare · '+money(m.revenue||0)+' lifetime receipts'):'No subway yet. Investors usually require at least 350 residents, sufficient density and financial confidence.'}</p>`;
}


// SOURCE: 42-construction.js
// A day of work requires a crew and materials; elapsed time alone cannot finish a site.
let crewDay=-1,crewsUsed=new Map(),regionalCrews=0;
function constructionWork(project){
 if(project.kind==='fields')return true;
 if(crewDay!==G.day){crewDay=G.day;crewsUsed=new Map();regionalCrews=0;}
 const builders=G.firms.filter(f=>f.kind==='contractor'&&!f.closed&&f.workers.length>=2&&f.cash>50);
 const builder=builders.find(f=>(crewsUsed.get(f.id)||0)<Math.max(1,Math.floor(f.workers.length/2)));
 if(!builder){
  // External crews are part of the already-paid regional construction contract.
  if(!G.policy.imports||regionalCrews>=2){project.stalledDays=(project.stalledDays||0)+1;project.reason='No funded construction crew available';return false;}
  regionalCrews++;project.builder='Regional construction service';project.workedDay=G.day;project.reason='Paid external crew working';return true;
 }
 crewsUsed.set(builder.id,(crewsUsed.get(builder.id)||0)+1);
 const scale=project.kind==='airport'?5:project.target==='tower'?3:project.kind==='redevelop'?2:1;
 const timber=.6*scale,stone=.35*scale;
 if((builder.stock.timber||0)<timber*4)trade(builder,'timber',timber*10-(builder.stock.timber||0));
 if((builder.stock.stone||0)<stone*4)trade(builder,'stone',stone*10-(builder.stock.stone||0));
 project.builder=builder.name;
 if((builder.stock.timber||0)<timber||(builder.stock.stone||0)<stone){project.stalledDays=(project.stalledDays||0)+1;project.reason='Waiting for paid timber or stone deliveries';return false;}
 builder.pendingCogs=(builder.pendingCogs||0)+takeInventory(builder,'timber',timber)+takeInventory(builder,'stone',stone);goodsEntry('timber','consumed',timber);goodsEntry('stone','consumed',stone);
 project.workedDay=G.day;project.reason='Crew and materials available';return true;
}
function birthsAndGenerations(){
 if(G.day%90!==0||G.stats.population>=2000)return;
 let count=0;
 for(const h of G.households){
  if(!h.people.length||h.people.length>=6||h.stress>48||G.day-(h.lastBirth||-720)<720)continue;
  const people=h.people.map(id=>G.people[id]).filter(p=>!p.deceased&&!p.movedAway),adults=people.filter(p=>p.age>=20&&p.age<=42);
  if(!adults.length||people.filter(p=>p.age<16).length>=2||!people.some(p=>p.job>=0))continue;
  const savings=h.cash+Object.values(h.deposits||{}).reduce((n,a)=>n+a,0);
  const security=clamp((savings/Math.max(1,h.people.length)-400)/3500,0,1),cost=clamp(1-(G.housingMarket.rentIndex-1)*.5,.35,1.15);
  if(random()>.085*security*cost)continue;
  const id=G.people.length,p={id,name:pick(first)+' '+h.name,age:0,skill:.05,health:94,hh:h.id,job:-1,life:80,last:[]};
  G.people.push(p);h.people.push(id);h.lastBirth=G.day;count++;if(G.stats.population+count>=2000)break;
 }
 if(count)story(count+' '+(count===1?'child was':'children were')+' born in local households. Family finances, housing and confidence influence household formation.','good');
}

// SOURCE: 45-public-services.js
// Councils authorize service budgets; procurement chooses sites and finances works.
function municipalProcurement(){
 if(G.day%30!==0||G.projects.some(p=>p.kind==='public'))return;
 const services=[['school',260,G.policy.educationBudget],['clinic',350,G.policy.healthBudget],['police',400,G.policy.policeBudget],['fire',450,G.policy.defenseBudget]];
 for(const [kind,capacity,budget] of services){
  const count=G.buildings.filter(b=>b.kind===kind).length;
  if(G.stats.population<=count*capacity||budget<60)continue;
  const cost=buildCost[kind],programmes=['policeBudget','defenseBudget','educationBudget','healthBudget','aidBudget','roadBudget'].reduce((n,k)=>n+G.policy[k],0);
  if(G.treasury<cost+programmes*45)continue;
  const candidates=buildableCandidates('housing').filter(p=>canPlace(p.x,p.y,true,kind));
  const site=candidates[0];if(!site)return;
  const b=startDevelopmentProject('public',site,cost*10,45,{publicKind:kind,duration:45});if(!b)return;
  b.footprint=footprintFor(site.x,site.y,kind);b.title={kind:'municipal',id:0};
  const contractors=G.firms.filter(f=>!f.closed&&f.kind==='contractor'),local=contractors.length?cost*.44:0;
  G.treasury-=cost;G.cumulative.spending+=cost;
  if(local){const f=contractors[G.day%contractors.length];f.cash+=local;f.pendingRevenue=(f.pendingRevenue||0)+local;book('Municipal capital budget',f.name,local,'Public '+types[kind].n+' contract',b.id);}
  G.region+=cost-local;book('Municipal capital budget','Regional suppliers',cost-local,'Public construction materials',b.id);
  story('Funded service expansion: the council commissioned a '+types[kind].n.toLowerCase()+'. The site opens after construction.','good',b.id);return;
 }
}
function householdFormation(){
 if(G.day%90!==0)return;
 const vacant=G.buildings.find(b=>b.kind==='home'&&!b.redevelopment&&(!G.households[b.hh]||G.households[b.hh].people.length===0));if(!vacant)return;
 const young=G.people.find(p=>!p.deceased&&!p.movedAway&&p.age>=20&&p.age<31&&p.job>=0&&G.households[p.hh].people.length>2&&G.households[p.hh].cash>3600);if(!young)return;
 const prior=G.households[young.hh],cash=Math.min(1800,prior.cash*.25),h={...prior,id:G.households.length,name:fromEnd(young.name.split(' ')),cash,home:vacant.id,owner:-1,people:[young.id],deposits:{},income:0,rent:0,food:0,tax:0,aid:0,stress:25,last:[]};
 prior.cash-=cash;prior.people=prior.people.filter(id=>id!==young.id);young.hh=h.id;G.households.push(h);vacant.hh=h.id;
 book(prior.name+' household',h.name+' household',cash,'Savings divided on household formation',vacant.id);
 story(young.name+' formed a household and rented an existing vacant cottage.','good',vacant.id,h.id);
}

function occupyVacantHousing(){
 if(G.day%30!==0||G.stats.employment<88||G.stats.population>=2000)return;
 const vacancy=G.buildings.find(b=>b.kind==='home'&&!b.redevelopment&&(!G.households[b.hh]?.people.length))||G.buildings.find(b=>['apartment','tower'].includes(b.kind)&&!b.redevelopment&&(b.units||[]).filter(id=>G.households[id]?.people.length).length<(b.kind==='tower'?9:4));
 if(!vacancy)return;const h=addHouseholdAt(vacancy,2500);if(!h)return;
 if(vacancy.kind==='home')vacancy.hh=h.id;else{vacancy.units=(vacancy.units||[]).filter(id=>G.households[id]?.people.length);vacancy.units.push(h.id);vacancy.hh=vacancy.units[0];}
 story('The '+h.name+' household moved into a vacant home after finding local job opportunities.','good',vacancy.id,h.id);
}

// SOURCE: 49-persistence.js
// Persistence chronology is separate from simulated days and deterministic exports.
// A new founding/import is a new timeline; logical order survives clock changes.
let saveEpoch=0,saveOrder=0,saveRevision=0,saveTown='',saveStoreReady=false;
let saveStorePromise=Promise.resolve(),saveWrites=Promise.resolve(),saveCandidates=[],saveWarningEpoch=0;
function beginSaveTimeline(){saveEpoch++;saveRevision=0;autoSaveOK=false;try{saveTown=Array.from(crypto.getRandomValues(new Uint32Array(4)),n=>n.toString(16)).join('-')}catch(_){saveTown='session-'+saveEpoch+'-'+Math.random().toString(36).slice(2)}return saveEpoch;}
function saveEnvelope(payload){
 if(!saveTown)beginSaveTimeline();
 if(saveOrder>=Number.MAX_SAFE_INTEGER-1)throw Error('Save chronology exhausted');
 const e={format:1,order:++saveOrder,town:saveTown,revision:++saveRevision,payload};
 e.checksum=checksum([e.format,e.order,e.town,e.revision,payload].join('|'));return e;
}
function promoteSaveEnvelope(e,minimum){
 const previous=e.checksum;saveOrder=Math.max(saveOrder,minimum);if(saveOrder>=Number.MAX_SAFE_INTEGER-1)throw Error('Save chronology exhausted');e.order=++saveOrder;e.checksum=checksum([e.format,e.order,e.town,e.revision,e.payload].join('|'));
 // Only update the matching local snapshot, never a later revision/town.
 try{const current=readSaveEnvelope(localStorage.getItem('townledger-v6'));if(current?.checksum===previous)localStorage.setItem('townledger-v6',JSON.stringify(e))}catch(_){}
}
function readSaveEnvelope(value){
 try{const e=typeof value==='string'?JSON.parse(value):value;if(!e||typeof e.payload!=='string'||typeof e.checksum!=='string')return null;
  if(e.format==null)return e.checksum===checksum(e.payload)?{...e,order:0,town:'',revision:0}:null;
  if(e.format!==1||!Number.isSafeInteger(e.order)||e.order<1||!Number.isSafeInteger(e.revision)||e.revision<1||typeof e.town!=='string'||!e.town||e.town.length>160)return null;
  return e.checksum===checksum([e.format,e.order,e.town,e.revision,e.payload].join('|'))?e:null;
 }catch(_){return null;}
}
function localSaveCandidates(){const out=[];for(const key of ['townledger-v6','townledger-v6-backup'])try{const e=readSaveEnvelope(localStorage.getItem(key));if(e)out.push(e)}catch(_){}return out;}
function observeSaveOrder(e){if(e)saveOrder=Math.max(saveOrder,e.order||0);}
function persistSnapshot(payload,epoch){
 if(epoch!==saveEpoch)return Promise.resolve(false);
 let e;try{for(const v of localSaveCandidates())observeSaveOrder(v);e=saveEnvelope(payload)}catch(_){autoSaveOK=false;return Promise.resolve(false)}
 let localOK=false;const text=JSON.stringify(e),key='townledger-v6';
 try{const previous=localStorage.getItem(key);if(readSaveEnvelope(previous)){try{localStorage.setItem(key+'-backup',previous)}catch(_){/* A full backup slot must not prevent updating the primary. */}}localStorage.setItem(key,text);localOK=true;try{localStorage.removeItem('townledger-village-founder-3')}catch(_){}}catch(_){}
 autoSaveOK=localOK;
 // Queue transactions in invocation order; callbacks from a replaced town cannot write.
 const write=saveWrites.catch(()=>false).then(()=>epoch===saveEpoch?writeIndexedDB(e,epoch):false);
 saveWrites=write;
 return write.then(idbOK=>{const ok=localOK||idbOK;if(epoch===saveEpoch&&e.order===saveOrder){autoSaveOK=ok;if(ok)saveWarningEpoch=0;else if(saveWarningEpoch!==epoch){saveWarningEpoch=epoch;toast('On-device saving is unavailable. Export a backup before leaving.')}}return ok;});
}
function save(){
 if(!G||simulationBusy)return Promise.resolve(false);
 let payload;try{payload=archivePayload()}catch(_){autoSaveOK=false;return Promise.resolve(false)}
 const epoch=saveEpoch;
 return saveStoreReady?persistSnapshot(payload,epoch):saveStorePromise.then(()=>persistSnapshot(payload,epoch));
}
function restoreSaveEnvelope(e){observeSaveOrder(e);if(!hydrateSave(e.payload))return false;saveTown=e.town||saveTown;saveRevision=e.revision||0;autoSaveOK=true;return true;}
function load(){
 const candidates=localSaveCandidates().concat(saveCandidates).map((e,i)=>({e,i}));
 candidates.sort((a,b)=>(b.e.order-a.e.order)||(a.i-b.i));
 for(const {e} of candidates)if(restoreSaveEnvelope(e))return true;
 for(const key of ['townledger-village-founder-3','townledger-village-civic-2'])try{const raw=localStorage.getItem(key);if(raw&&hydrateSave(raw))return true}catch(_){}
 return false;
}

// SOURCE: 50-clock.js
function tick(){if(!G||pendingEvent)return;ensureSystems();ensureMarketModel();G.day++;if(G.day%30===0){G.month++;if(G.month>12){G.month=1;G.year++}};
 freightDay();completeEquipmentOrders();completeDevelopmentProjects();dailyEconomy();bankDaily();metroOperatingDay();airfieldOperatingDay();incidents();investigateCases();extendedCivicDay();maintainRoads();finalizeMarketBooks();if(G.day%30===0&&G.debt>0){const interest=G.debt*((G.policy.policyRate||0)/100+.015)/12,paid=Math.min(G.treasury,interest);G.treasury-=paid;G.region+=paid;G.debt+=interest-paid;story('Interest on municipal borrowing: '+money(interest)+'.')}if(G.day%10===0)assignJobs();if(G.day%30===0)privateInvestmentAndHousing();

 if(G.day%30===0){outwardMigration();autonomousDevelopment();}
 if(G.day%45===0&&G.stats.population<2000){let success=G.stats.employment>88&&G.stats.hardship<35&&G.firms.some(f=>!f.closed&&f.workers.length<f.jobs);
   if(success&&G.homes.length>0&&random()<.5){let h=pick(G.households);if(h.people.length<4){let p={id:G.people.length,name:pick(first)+' '+h.name,age:Math.round(rn(18,42)),skill:rn(.3,1),health:rn(60,100),hh:h.id,job:-1,life:60,last:[]};G.people.push(p);h.people.push(p.id);story('A newcomer joined the '+h.name+' household.','good',h.home,h.id)}}
 }
 recompute();updateCouncilAndMissions();systemsDay();
 if(G.day%30===0)monthlyReview();
 if(G.day%360===0){yearlyDemographics();electionReview();}
 if(!pendingEvent&&G.day%45===0&&G.day-G.lastEventDay>=37)offerCouncilEvent();
 // Publish and save one canonical end-of-day snapshot after demographic and civic changes.
 recompute();G.stats.approval=Math.round(G.council.approval);G.rngState=rngState;
 updateScenarioProgramme();if(G.day%10===0)recordObservation();
 G.history.push({day:G.day,employment:G.stats.employment,hardship:G.stats.hardship,safety:G.stats.safety,treasury:Math.round(G.treasury),businesses:G.stats.businesses,deposits:(G.banks||[]).reduce((n,b)=>n+bankDeposits(b.id),0),crime:G.stats.dailyCrime,approval:G.council.approval,education:G.education,health:G.health});if(G.history.length>240)G.history.shift();
 if(G.day%60===0){const signal=marketSignal();if(signal.kind!=='normal'&&signal.title!==G.lastEconomicSignal){story(signal.title+'. '+signal.description,signal.kind==='good'?'good':'bad');G.lastEconomicSignal=signal.title;}}
 // Autosaves are scheduled in wall time by the frame controller.
 dirty=true;
}

function resetTownTransientUI(){
 clearTimeout(toastTimeout);toastTimeout=0;$('toast').style.display='none';pendingEvent=null;$('eventDialog').style.display='none';councilOpener=null;panelOpener=null;parcelFocus=null;selected=null;inspectedTrip=null;buildMode='';pointer.down=false;pointer.activeId=null;pointer.hover=null;touches.clear();roadPainted.clear();$('placementHint').style.display='none';$('hint').textContent='DRAG TO PAN · TAP TO INSPECT · PINCH TO ZOOM';
}
function toast(msg){const el=$('toast');el.textContent=msg;el.style.display='block';clearTimeout(toastTimeout);toastTimeout=setTimeout(()=>el.style.display='none',3300)}

// SOURCE: 60-renderer.js
function headerText(id,value){const el=$(id),text=String(value);if(el&&el.textContent!==text)el.textContent=text;}
function headerMoney(value){return Math.abs(value)>=1000000?(value<0?'−':'')+'$'+(Math.abs(value)/1000000).toLocaleString('en-CA',{maximumFractionDigits:1})+'m':money(value);}
function updateHeader(){
 if(!G)return;headerText('pop',fmt(G.stats.population));headerText('funds',headerMoney(G.treasury));if($('funds').title!==money(G.treasury))$('funds').title=money(G.treasury);headerText('jobs',G.stats.employment+'%');headerText('safety',G.stats.safety+'/100');headerText('approval',Math.round(G.council.approval)+'%');headerText('date','YEAR '+G.year+' · MONTH '+G.month+' · DAY '+G.day);
 headerText('season',(seasonsEnabled()?['SPRING IN THE VALE','SUMMER IN THE VALE','AUTUMN IN THE VALE','WINTER IN THE VALE'][Math.floor((G.month-1)/3)]:'THE WORKING CITY')+(weatherEnabled()&&G.weather&&G.weather!=='clear'?' · '+G.weather.toUpperCase():''));
 headerText('pause',paused?'►':'Ⅱ');const pause=$('pause'),label=paused?'Resume simulation':'Pause simulation',title=paused?'Resume':'Pause';if(pause.getAttribute('aria-label')!==label)pause.setAttribute('aria-label',label);if(pause.title!==title)pause.title=title;
 if($('liveEconomy')&&(G.day%5===1||G.day<5)){const m=marketSignal(),care=G.serviceProvision?.health?.coverage,school=G.serviceProvision?.school?.coverage;headerText('marketHeadline',m.title);headerText('marketDetail',Number.isFinite(care)&&Number.isFinite(school)?Math.round(care*100)+'% care · '+Math.round(school*100)+'% school · '+m.m.open+' firms':m.m.open+' firms · '+m.m.projects+' projects · '+G.stats.hardship+'% hardship');}
 headerText('speed',speed+'×');headerText('effectiveSpeed',!paused&&speed>=8?'Actual '+perfStats.effective.toFixed(0)+'×':'');const range=$('speedRange'),value=String(SPEED_PRESETS.indexOf(speed)>=0?SPEED_PRESETS.indexOf(speed):0);if(range&&range.value!==value)range.value=value;$('pauseBanner').style.display=paused?'block':'none';updateObjectiveMini();
}
// ----- Town map renderer. Geometry is cached; only vehicles need a dynamic redraw.
function iso(x,y){return [(x-y)*TW/2+RW/2,(x+y)*TH/2+32]}
function diamond(g,x,y,fill,stroke){let p=iso(x,y);g.beginPath();g.moveTo(p[0],p[1]);g.lineTo(p[0]+TW/2,p[1]+TH/2);g.lineTo(p[0],p[1]+TH);g.lineTo(p[0]-TW/2,p[1]+TH/2);g.closePath();g.fillStyle=fill;g.fill();g.strokeStyle=fill;g.lineWidth=.7;g.stroke();if(stroke){g.strokeStyle=stroke;g.lineWidth=.6;g.stroke()}}
let roadNetwork=null,roadsVersion=0,roadVersionBuilt=-1,roadGraphOwner=null,roadBuildingVersion=-1,traffic=[],trafficClock=0,frameClock=0,renderSprites=[],spritesVersion=-1,vehicleSerial=0;
const roadOffsets=[[-1,0],[1,0],[0,-1],[0,1]];
function ensureRoadWear(){if(!G.roadWear||!Array.isArray(G.roadWear)||G.roadWear.length!==T*T){G.roadWear=new Array(T*T).fill(100)}}
function maintainRoads(){
 ensureRoadWear();
 const net=graph(),privateSet=new Set(G.privateRoads||[]);
 const publicCount=Math.max(1,charterRoadCount());
 const publicBudget=clamp(G.policy.roadBudget,0,250)*(G.actualServiceFunding?.roads??1);
 const publicRepair=publicBudget/publicCount*.23;
 // Private lanes are maintained by locally subscribed user charges, not the
 // municipal road grant. If shops cannot pay, pavement gradually deteriorates.
 const commercial=G.firms.filter(f=>!f.closed&&f.cash>2&&net.portals.has(f.building));
 let privateFees=0;
 if(privateSet.size&&commercial.length){
  const due=Math.min(.22,privateSet.size*.13/commercial.length);
  for(const f of commercial){const paid=Math.min(f.cash,due);f.cash-=paid;f.expenses+=paid;G.region+=paid;privateFees+=paid}
 }
 if(G.development)G.development.privateRoadTolls=(G.development.privateRoadTolls||0)+privateFees;
 const privateRepair=privateFees/Math.max(1,privateSet.size)*.85;
 let total=0,n=0;
 for(const id of net.neighbors.keys()){
  const old=G.roadWear[id];
  const repair=privateSet.has(id)?privateRepair:charterOwns(id%T,id/T|0)?publicRepair:.045;
  G.roadWear[id]=clamp(old-.045-(G.weather==='storm'?.065:0)+repair,25,100);
  total+=G.roadWear[id];n++;
 }
 G.stats.roadCondition=Math.round(total/Math.max(1,n));
 // Road wear is an economic measure, not a reason to repaint the terrain.
}
const roadId=(x,y)=>y*T+x;
function invalidateRoads(resetTraffic=true){roadsVersion++;roadNetwork=null;if(resetTraffic){traffic.length=0;trafficClock=0;intersectionGates.clear()}if(G)G.roadMetrics=null;dirty=true;}
function flushRoadBatch(){if(!roadBatchDirty)return;roadBatchDirty=false;invalidateRoads();staticDirty=true;if(G){recompute();updateHeader();save()}}
function graph(){
 if(roadNetwork&&roadVersionBuilt===roadsVersion&&roadGraphOwner===G&&roadBuildingVersion===G.buildings.length)return roadNetwork;
 const neighbors=new Map(),parts=new Int32Array(T*T).fill(-1),portals=new Map(),connected=[];
 for(let i=0;i<G.tiles.length;i++)if(G.tiles[i]===1){
  const x=i%T,y=i/T|0,ns=[];
  for(const [dx,dy] of roadOffsets){const xx=x+dx,yy=y+dy;if(xx>=0&&xx<T&&yy>=0&&yy<T&&G.tiles[roadId(xx,yy)]===1)ns.push(roadId(xx,yy))}
  neighbors.set(i,ns);
 }
 let part=0,maxSize=0,mainPart=-1;
 for(const id of neighbors.keys())if(parts[id]===-1){
  const q=[id];parts[id]=part;for(let k=0;k<q.length;k++)for(const n of neighbors.get(q[k]))if(parts[n]===-1){parts[n]=part;q.push(n)}
  if(q.length>maxSize){maxSize=q.length;mainPart=part}part++;
 }
 const anchor=G.buildings.find(b=>b.kind==='townhall');
 if(anchor){for(const [dx,dy] of roadOffsets){let x=anchor.x+dx,y=anchor.y+dy;if(x>=0&&x<T&&y>=0&&y<T&&parts[roadId(x,y)]>=0){mainPart=parts[roadId(x,y)];break}}}
 for(const b of G.buildings){
  const choices=[];for(const id of footprintOf(b)){const xx=id%T,yy=id/T|0;for(const [dx,dy] of roadOffsets){const ax=xx+dx,ay=yy+dy;if(ax>=0&&ax<T&&ay>=0&&ay<T&&G.tiles[roadId(ax,ay)]===1)choices.push(roadId(ax,ay))}}
  if(choices.length){let entry=choices.find(id=>parts[id]===mainPart)??choices[0];portals.set(b.id,entry);if(parts[entry]===mainPart)connected.push(b)}
 }
 roadNetwork={neighbors,parts,portals,connected,mainPart,partsCount:part,maxSize};roadVersionBuilt=roadsVersion;roadGraphOwner=G;roadBuildingVersion=G.buildings.length;return roadNetwork;
}
function routeBetween(a,b){
 const net=graph(),start=typeof a==='number'?a:net.portals.get(a?.id),finish=typeof b==='number'?b:net.portals.get(b?.id);
 if(start==null||finish==null||net.parts[start]!==net.parts[finish])return [];
 if(start===finish)return [start];
 net.routeTrees=net.routeTrees||new Map();let prev=net.routeTrees.get(start);
 if(!prev){prev=new Int32Array(T*T).fill(-1);const queue=[start];prev[start]=start;
  for(let i=0;i<queue.length;i++)for(const n of net.neighbors.get(queue[i])||[]){if(prev[n]!==-1)continue;prev[n]=queue[i];queue.push(n);}
  // 96 trees at 56² Int32 cells use at most 1.2 MiB.
  if(net.routeTrees.size>=96)net.routeTrees.delete(net.routeTrees.keys().next().value);net.routeTrees.set(start,prev);
 }
 if(prev[finish]===-1)return [];const path=[finish];let at=finish;
 while(at!==start){at=prev[at];path.push(at);}return path.reverse();
}

function roadMetrics(){
 const net=graph(),firms=G.firms.filter(f=>!f.closed),reachable=firms.filter(f=>{let node=net.portals.get(f.building);return node!=null&&net.parts[node]===net.mainPart}).length;
 const eligible=G.households.filter(h=>{let node=net.portals.get(h.home);return node!=null&&net.parts[node]===net.mainPart}).length;
 let routes=0,length=0;for(let i=0;i<Math.min(10,net.connected.length-1);i++){
  const a=net.connected[i],b=net.connected[(i*7+19)%net.connected.length];if(a===b)continue;let path=routeBetween(a,b);if(path.length>1){routes++;length+=path.length-1}
 }
 return {connectedFirms:reachable,totalFirms:firms.length,connectedHomes:eligible,totalHomes:G.households.length,roadTiles:net.neighbors.size,roadClusters:net.partsCount,averageJourney:routes?Math.round(length/routes):0,quality:Math.round(G.stats.roadCondition??75)};
}
function roadCenter(id){const pos=iso(id%T,id/T|0);return [pos[0],pos[1]+TH/2]}
function roadDistance(a,b){
 if(a==null||b==null)return Infinity;
 if(a===b)return 0;
 const net=graph();if(net.parts[a]!==net.parts[b])return Infinity;
 if(!net.distCache)net.distCache=new Map();
 const key=a<b?a*T*T+b:b*T*T+a;
 if(net.distCache.has(key))return net.distCache.get(key);
 const dist=routeBetween(a,b).length-1;
 if(net.distCache.size>3000)net.distCache.clear();
 net.distCache.set(key,dist);
 return dist;
}
function beginVehicle(source=null,target=null,emergency=false){
 const net=graph();if(net.connected.length<2)return null;
 let from=source||visualPick(net.connected.filter(b=>b.firm>=0&&G.firms[b.firm]&&!G.firms[b.firm].closed));
 if(!from)return null;
 const src=net.portals.get(from.id);if(src==null)return null;if(traffic.some(v=>v.path[v.segment]===src&&v.fraction<.8))return null;
 let destinations=net.connected.filter(b=>b.id!==from.id&&net.parts[net.portals.get(b.id)]===net.parts[src]);
 if(!destinations.length)return null;
 // Goods vehicles favour another business, while smaller cars visit homes and civic premises.
 const commercial=destinations.filter(b=>b.firm>=0),residential=destinations.filter(b=>b.kind==='home');
 let pool=visualRandom()<.58?commercial:residential;
 let to=target||visualPick(pool.length?pool:destinations);
 if(target&&(!net.portals.has(target.id)||net.parts[net.portals.get(target.id)]!==net.parts[src]))return null;
 if(!to||net.parts[net.portals.get(to.id)]!==net.parts[src])to=visualPick(destinations);
 let path=routeBetween(from,to);if(path.length<2)return null;
 const n=traffic.length,color=emergency?'#c24c3e':['#b98051','#e4c58b','#536e7c','#7b8b71','#9b5f54','#c6bd9e'][((from.id*7+n*3)%6)];
 let style=emergency?'emergency':from.kind==='farm'?'tractor':visualRandom()<.28?'pedestrian':visualRandom()<.48?'truck':'car';let v={id:++vehicleSerial,path,segment:0,fraction:0,speed:emergency?4.3:style==='pedestrian'?.53:style==='tractor'?.68:1+visualRandom()*.4,style,color,emergency,wait:0,age:0,from:from.id,to:to.id};traffic.push(v);return v;
}
function roadServiceDistance(site,station){if(!site||!station)return Infinity;const net=graph(),a=net.portals.get(site.id),b=net.portals.get(station.id);if(a==null||b==null||net.parts[a]!==net.parts[b])return Infinity;return roadDistance(a,b);}
function closestRoadBuilding(x,y,kind){const net=graph(),site=buildingAt(x,y);if(!site)return null;let best=null,d=Infinity;for(const b of net.connected){if(kind&&b.kind!==kind)continue;const distance=roadServiceDistance(site,b);if(distance<d){best=b;d=distance}}return best}
function emergencyDispatch(site,kind){if(!site)return;const service=closestRoadBuilding(site.x,site.y,kind);if(service){const v=beginVehicle(service,site,true);if(v){v.speed=5.5;return}}}
let trafficElapsed=0,intersectionGates=new Map();
function trafficUpdate(dt){
 if(paused||pendingEvent||!G)return;
 const target=Math.min(42,Math.round(5+Math.sqrt(G.stats.population)*1.25));
 trafficElapsed+=dt;trafficClock+=dt;
 let tries=0;
 while(trafficClock>.72&&traffic.length<target&&tries++<3){trafficClock-=.72;spawnPurposeTrip()}
 if(traffic.length>=target)trafficClock=Math.min(.72,trafficClock);
 const quality=clamp(.52+(G.stats.roadCondition??75)/130,.45,1.25);
 // Reserve occupied DIRECTED ROAD SEGMENTS rather than whole intersections.
 // A vehicle crossing a junction never blocks everyone who is merely
 // travelling on a different segment through that same road tile.
 const edges=new Map();
 for(const v of traffic){let a=v.path[v.segment],b=v.path[v.segment+1];if(b!=null)edges.set(a+'>'+b,v)}
 const ready=[],approved=new Set(),gateTaken=new Set(),network=graph();
 for(const v of traffic){
   v.age=(v.age||0)+dt;
   const step=Math.min(.34,dt*v.speed*quality);
   v.plannedStep=step;
   if(v.path[v.segment+1]==null){v.finished=true;continue}
   if(v.fraction+step<1){const leader=traffic.filter(c=>c!==v&&c.path[c.segment]===v.path[v.segment]&&c.path[c.segment+1]===v.path[v.segment+1]&&c.fraction>v.fraction).sort((a,b)=>a.fraction-b.fraction)[0];const next=leader?Math.min(v.fraction+step,Math.max(v.fraction,leader.fraction-.26)):v.fraction+step;if(next<=v.fraction+.00001)v.wait=(v.wait||0)+dt;else v.wait=0;v.fraction=next;continue;}
   ready.push(v);
 }
 ready.sort((a,b)=>(b.wait-a.wait)||Number(b.emergency)-Number(a.emergency)||(a.id-b.id));
 for(const v of ready){
   const junction=v.path[v.segment+1],after=v.path[v.segment+2];
   const valence=network.neighbors.get(junction)?.length||0;
   const leader=after==null?null:edges.get(junction+'>'+after);
   const entryBlocked=leader&&leader!==v&&leader.fraction<.45;
   const crossing=valence>=3;
   const last=intersectionGates.get(junction)||-99;
   const signalBlocked=crossing&&(trafficElapsed-last<.16||gateTaken.has(junction));
   if(entryBlocked||signalBlocked){v.fraction=Math.min(.96,v.fraction);v.wait=(v.wait||0)+dt;continue}
   approved.add(v.id);
   if(crossing){gateTaken.add(junction);intersectionGates.set(junction,trafficElapsed)}
 }
 for(const v of ready){
  if(!approved.has(v.id))continue;
  v.segment++;
  v.fraction=clamp(v.fraction+v.plannedStep-1,0,.34);
  v.wait=0;
 }
 // Max-duration safeguard protects against malformed saved routes, not
 // normal congestion. Ordinary traffic should make forward progress.
 for(let i=traffic.length-1;i>=0;i--){const v=traffic[i];if(v.finished||v.segment>=v.path.length-1){
    // A sampled commuter is not an economically delivered consignment.
    traffic.splice(i,1);
  }}
 for(const v of traffic)if(v.wait>4&&v.fraction<.001)detour(v);
 if(intersectionGates.size>450){for(const [k,t] of intersectionGates)if(trafficElapsed-t>3)intersectionGates.delete(k)}
 if(traffic.length||G.airport?.operating||G.metro?.operating||G.buildings.some(b=>b.kind==='factory'||b.kind==='mill'||b.kind==='worksite')||overlay==='metro')dirty=true;
}

function vehiclePosition(v){
 const i=v.segment,t=clamp(v.fraction,0,1),t2=t*t,t3=t2*t;
 const a=roadCenter(v.path[Math.max(0,i-1)]),p=roadCenter(v.path[i]);
 const q=roadCenter(v.path[Math.min(v.path.length-1,i+1)]),b=roadCenter(v.path[Math.min(v.path.length-1,i+2)]);
 // Catmull–Rom cornering has continuous position and heading at junctions.
 // With one-tile spacing, rounded turns remain within adjoining road tiles.
 const curve=(k)=>.5*(2*p[k]+(-a[k]+q[k])*t+(2*a[k]-5*p[k]+4*q[k]-b[k])*t2+(-a[k]+3*p[k]-3*q[k]+b[k])*t3);
 const tangent=(k)=>.5*((-a[k]+q[k])+2*(2*a[k]-5*p[k]+4*q[k]-b[k])*t+3*(-a[k]+3*p[k]-3*q[k]+b[k])*t2);
 let x=curve(0),y=curve(1),dx=tangent(0),dy=tangent(1);
 const length=Math.hypot(dx,dy)||1,side=v.style==='pedestrian'?(G.roadClasses?.[v.path[i]]==='arterial'?20:G.roadClasses?.[v.path[i]]==='collector'?17:13):4.3;
 return {x:x-dy/length*side,y:y+dx/length*side,dx,dy};
}

// SOURCE: 65-landscape.js
// Original code-native pixel art. One unit = one owned 72 × 36 isometric tile.
// All architectural forms use the same projection, anchor and sunlight direction.
let nightMode=false,displayItems=[],buildingItemsById=new Map(),atlas=new Map(),atlasBytes=0,sceneSignature='',lastSceneMonth=0,landscapeRevision=0;
const viewRaster=document.createElement('canvas'),viewBackgroundRaster=document.createElement('canvas');let viewRasterKey='',viewBackgroundKey='',viewBuildings=[];
const SEASONS=[{grass:['#8f9b69','#929f6d','#96a36f','#9ba773','#9da875'],dark:'#788b58',leaf:['#536c41','#69844a','#809650'],water:'#6b9895'},
 {grass:['#7c994f','#819e52','#86a558','#8aaa5e','#8eaa60'],dark:'#6b7f48',leaf:['#315b3c','#4e7d42','#83a34e'],water:'#4c9297'},
 {grass:['#a4a070','#a7a272','#aba676','#ada877','#b0a97b'],dark:'#8c905d',leaf:['#885e40','#b28144','#ceab5a'],water:'#759593'},
 {grass:['#d4d8cc','#d8dbd0','#dce0d4','#dfe2d9','#e1e4db'],dark:'#c0cdc2',leaf:['#627a6b','#8c9e88','#c9d4c3'],water:'#86a5a6'}];
function seasonPalette(){return SEASONS[Math.floor((visualMonth()-1)/3)%4];}
function visualPick(a){return a[Math.floor(visualRandom()*a.length)];}
function point(u,v,z=0){return [Math.round((u-v)*36),Math.round((u+v)*18-z)];}
function polygon(g,points,color,stroke=null){g.fillStyle=color;g.beginPath();points.forEach((p,i)=>i?g.lineTo(...p):g.moveTo(...p));g.closePath();g.fill();if(stroke){g.strokeStyle=stroke;g.lineWidth=1;g.stroke();}}
function segment(g,a,b,color,width=1){g.strokeStyle=color;g.lineWidth=width;g.beginPath();g.moveTo(...a);g.lineTo(...b);g.stroke();}
function tone(c,m){const rgb=c.slice(1).match(/../g).map(x=>Math.max(0,Math.min(255,Math.round(parseInt(x,16)*m))));return '#'+rgb.map(x=>x.toString(16).padStart(2,'0')).join('');}
function slab(g,u,v,w,d,z,color){polygon(g,[point(u,v,z),point(u+w,v,z),point(u+w,v+d,z),point(u,v+d,z)],color);}
function box(g,u,v,w,d,z,h,c,top){
 polygon(g,[point(u+w,v,z),point(u+w,v+d,z),point(u+w,v+d,z+h),point(u+w,v,z+h)],tone(c,.79));
 polygon(g,[point(u,v+d,z),point(u+w,v+d,z),point(u+w,v+d,z+h),point(u,v+d,z+h)],c);
 if(gameOptions.decor&&gameOptions.quality!=='low'){
  for(const side of ['front','side']){g.save();g.beginPath();const verts=side==='front'?[point(u,v+d,z),point(u+w,v+d,z),point(u+w,v+d,z+h),point(u,v+d,z+h)]:[point(u+w,v,z),point(u+w,v+d,z),point(u+w,v+d,z+h),point(u+w,v,z+h)];verts.forEach((p,i)=>i?g.lineTo(...p):g.moveTo(...p));g.closePath();g.clip();
   for(let row=1;row<h/5;row++){const zz=z+row*5;segment(g,side==='front'?point(u,v+d,zz):point(u+w,v,zz),point(u+w,v+d,zz),tone(c,side==='front'?.94:.73));
    for(let col=0;col<Math.ceil((side==='front'?w:d)*5);col++){let t=(col+(row%2)*.5)/5;if(t>(side==='front'?w:d))continue;segment(g,side==='front'?point(u+t,v+d,zz):point(u+w,v+t,zz),side==='front'?point(u+t,v+d,zz+4):point(u+w,v+t,zz+4),tone(c,side==='front'?.90:.70));}
   }g.restore();
  }
 }
 slab(g,u,v,w,d,z+h,top||tone(c,1.12));
 segment(g,point(u,v+d,z),point(u+w,v+d,z),tone(c,.64));
}
function windowPane(g,u,v,z,side,lit=false,w=.115,h=7){
 const du=side==='front'?w:0,dv=side==='side'?w:0;
 const p=[point(u,v,z),point(u+du,v+dv,z),point(u+du,v+dv,z+h),point(u,v,z+h)];
 polygon(g,p,'#e2d1ac');
 const inset=.018;polygon(g,[point(u+du*.15,v+dv*.15,z+1),point(u+du*.85,v+dv*.85,z+1),point(u+du*.85,v+dv*.85,z+h-1),point(u+du*.15,v+dv*.15,z+h-1)],lit?'#efc676':'#6b8782');
 segment(g,point(u+du*.5,v+dv*.5,z+1),point(u+du*.5,v+dv*.5,z+h-1),'#c7c3aa');
 if(gameOptions.decor){segment(g,point(u-du*.12,v-dv*.12,z-1),point(u+du*1.12,v+dv*1.12,z-1),'#ebe0b8',2);for(const t of [-.25,1.12]){const q=point(u+du*t,v+dv*t,z);g.fillStyle='#49634d';g.fillRect(q[0]-1,q[1]-h,2,h);}}

}
function door(g,u,v,z=0,w=.15){polygon(g,[point(u,v,z),point(u+w,v,z),point(u+w,v,z+13),point(u,v,z+13)],'#574c3d');const p=point(u+w*.8,v,z+6);g.fillStyle='#d5b46e';g.fillRect(p[0],p[1],1,2);}
function gable(g,u,v,w,d,z,rise,color){
 const ridge=v+d/2;
 polygon(g,[point(u-.04,v-.04,z),point(u+w+.04,v-.04,z),point(u+w+.04,ridge,z+rise),point(u-.04,ridge,z+rise)],tone(color,.83));
 polygon(g,[point(u-.04,ridge,z+rise),point(u+w+.04,ridge,z+rise),point(u+w+.04,v+d+.05,z),point(u-.04,v+d+.05,z)],color);
 polygon(g,[point(u+w,v,z),point(u+w,v+d,z),point(u+w,ridge,z+rise)],tone(color,.66));
 for(let t=.2;t<1;t+=.2)segment(g,point(u-.02,ridge+(d/2+.04)*t,z+rise*(1-t)),point(u+w+.04,ridge+(d/2+.04)*t,z+rise*(1-t)),tone(color,.91));
 if(gameOptions.decor&&gameOptions.quality!=='low'){
  for(let row=1;row<6;row++){const t=row/6,yy=ridge+(d/2+.04)*t,zz=z+rise*(1-t);for(let col=0;col<Math.ceil(w*11);col++){const xx=u+col/11+(row%2)/22;if(xx>u+w)continue;segment(g,point(xx,yy,zz),point(xx,yy+(d/2+.04)/6,zz-rise/6),tone(color,col%3?1.09:.84));}}
 }
 segment(g,point(u-.05,ridge,z+rise),point(u+w+.05,ridge,z+rise),tone(color,1.28),1.3);
}
function chimney(g,u,v,z){box(g,u,v,.075,.09,z,11,'#aa856b','#cbb698');}
function tree(g,u,v,id,scale=1){
 const p=point(u,v),s=seasonPalette(),r=hash(id);g.save();g.translate(...p);g.scale(scale,scale);
 polygon(g,[[-2,2],[15,5],[23,1],[6,-2]],'#56654938');
 g.fillStyle='#6a5842';g.fillRect(-2,-18,4,22);g.fillStyle='#8f7655';g.fillRect(-1,-18,1,22);
 if(r%4===0){for(let j=0;j<4;j++){polygon(g,[[0,-53+j*9],[-15+j,-27+j*8],[15-j,-27+j*8]],s.leaf[j%3]);segment(g,[-8+j,-30+j*8],[0,-45+j*9],tone(s.leaf[1],1.12));}}
 else{const crowns=[[-6,-31,12], [5,-36,12],[-10,-23,11],[7,-24,13],[0,-19,11]];for(let k=0;k<crowns.length;k++){let [x,y,n]=crowns[k];polygon(g,[[x-n,y-4],[x-n+4,y-10],[x+2,y-12],[x+n,y-5],[x+n-1,y+4],[x+4,y+9],[x-n+3,y+6]],s.leaf[k%3]);}
  g.fillStyle=tone(s.leaf[2],1.08);for(let i=0;i<13;i++){let n=hash(r+i*713);g.fillRect((n%21)-10,-41+(n>>>9)%21,3,2);}}
 if(gameOptions.decor&&gameOptions.quality!=='low'&&r%4!==0){for(let k=0;k<20;k++){const n=hash(id*319+k*71),x=n%27-14,y=-43+(n>>>7)%23;g.fillStyle=k%4===0?tone(s.leaf[2],1.18):tone(s.leaf[1],1.10);g.fillRect(x,y,3,1);g.fillRect(x+1,y-1,2,1);if(id%7===0&&k%7===0){g.fillStyle='#bc6745';g.fillRect(x,y+3,2,2);}}}
 if(visualMonth()>=10){g.fillStyle='#edf0e6';for(let j=0;j<4;j++)g.fillRect(-10+j*6,-35+(j%2)*5,9,2);}g.restore();
}
function architecture(g,b,w,d){
 const id=b.id,kind=b.redevelopment?'worksite':b.kind,v=id%8,winter=visualMonth()>=10,occupied=(b.hh>=0&&G.households[b.hh]?.people.length)||b.units?.some(id=>G.households[id]?.people.length),closed=b.firm>=0&&G.firms[b.firm]?.closed;
 const stone=['#dbca9e','#d4b78b','#c6c6a0','#e4d0aa'],roofs=['#9f553d','#617b78','#aa6d45','#466c59','#bd884a','#627f8e','#886050','#b0774b'];
 const wall=closed?'#9d9a85':kind==='home'?['#dcc596','#b9c7a4','#b77c59','#9fb6b7','#d7c39a','#cbc5a3','#cfae84','#b6bc8e'][id%8]:kind==='police'?'#a3b5ae':kind==='fire'?'#bf7856':stone[id%4],roof=winter?'#c4cfc1':roofs[id%8],lit=nightMode&&!!occupied;
 const bw=w*.73,bd=d*.70,u=-bw/2,vv=-bd/2;
 slab(g,-w/2+.03,-d/2+.03,w-.06,d-.06,0,kind==='farm'?'#a49b71':'#aaad8c');
 // Garden and footpath are contained by the legal parcel, never painted on roads.
 slab(g,-.07,bd/2,.14,Math.max(.04,(d-bd)/2),1,'#bfb69c');
 if(kind==='home'){
  const heights=[22,28,20,32,21,26,19,24],H=heights[id%8];
  const wide=id%8===2?bw*.95:id%8===3?bw*.67:bw*.85,deep=id%8===5?bd*.7:bd*.9;
  const a=-wide/2,c=-deep/2;
  box(g,a,c,wide,deep,1,H,wall);
  if(id%8===3){box(g,a,c,wide,deep,H+1,8,wall);gable(g,a,c,wide,deep,H+9,10,roof);}
  else if(id%8===4){slab(g,a-.04,c-.04,wide+.08,deep+.08,H+2,tone(roof,.8));box(g,a+.05,c+.05,wide-.10,deep-.10,H+2,6,roof);slab(g,a+.04,c+.04,wide-.08,deep-.08,H+9,tone(roof,1.15));}
  else gable(g,a,c,wide,deep,H+1,id%8===2?8:14,roof);
  for(let i=0;i<2;i++){windowPane(g,a+.07+i*wide*.5,c+deep+.01,H>25?16:10,'front',lit||id%11===0,.12,7);windowPane(g,a+wide+.01,c+.07+i*deep*.45,10,'side',lit,.12,7);}
  door(g,-.05,c+deep+.02,1,.12);
  if(gameOptions.decor){
   // Exposed timber, doorstep and ridge details make individual cottages legible.
   if(id%3===0){for(const x of [a+.02,a+wide-.025])segment(g,point(x,c+deep+.025,1),point(x,c+deep+.025,H),'#7a6849',2);segment(g,point(a,c+deep+.025,H-2),point(a+wide,c+deep+.025,H-2),'#7a6849',2);}
   slab(g,-.09,c+deep+.025,.20,.10,2,'#d5c49d');slab(g,-.11,c+deep+.10,.24,.09,1,'#b1a58a');
   if(id%4===0){box(g,a+wide*.55,c+deep*.45,.18,.18,H+6,8,wall);gable(g,a+wide*.55,c+deep*.45,.18,.18,H+14,5,roof);windowPane(g,a+wide*.56,c+deep*.45+.19,H+7,'front',lit,.13,5);}
  }

  if(id%8===1||id%8===5){box(g,a-.07,c+deep-.10,wide*.45,.24,0,12,tone(wall,.96));gable(g,a-.07,c+deep-.10,wide*.45,.24,12,6,roof);windowPane(g,a-.02,c+deep+.15,4,'front',lit,.12,5);}
  if(id%8===6){slab(g,a-.04,c+deep,wide+.08,.13,14,roof);for(const k of [0,.85])segment(g,point(a+k*wide,c+deep+.1,0),point(a+k*wide,c+deep+.1,14),'#927d59',1);}
  if(id%8===7){for(let f=5;f<H;f+=7)segment(g,point(a,c+deep+.01,f),point(a+wide,c+deep+.01,f),'#9c8d72');}
  chimney(g,a+.10,c+.05,H+8);
  if(id%3===0){for(let t=0;t<5;t++){const p=point(-.43+t*.14,.43);g.fillStyle='#d9c9a5';g.fillRect(p[0],p[1]-7,2,7);}segment(g,point(-.43,.43,3),point(.34,.43,3),'#cfbd96');}
  if(id%3===1){for(let j=0;j<5;j++){const p=point(-.40+j*.065,.27);g.fillStyle=['#c2a45f','#bf8072','#d6cba3'][j%3];g.fillRect(p[0],p[1]-2,2,2);}}
  if(id%5===0)tree(g,-.37,-.36,id,.32);
 }else if(kind==='apartment'||kind==='tower'||kind==='office'){
  const floors=kind==='tower'?11:kind==='office'?5:4,H=floors*12;
  box(g,u,vv,bw,bd,0,H,kind==='tower'?'#aaa995':'#bfac91');
  for(let f=0;f<floors;f++){segment(g,point(u,vv+bd,12*f),point(u+bw,vv+bd,12*f),'#9c927e');for(let i=0;i<4;i++){windowPane(g,u+.08+i*bw*.23,vv+bd+.01,4+f*12,'front',nightMode&&(id+i+f)%3!==0,.16,6);windowPane(g,u+bw+.01,vv+.10+i*bd*.22,4+f*12,'side',nightMode&&(id+f)%4===0,.15,6);}}
  slab(g,u-.03,vv-.03,bw+.06,bd+.06,H+2,'#5c716d');box(g,u+.1,vv+.12,bw*.45,bd*.4,H+2,6,'#8a9587');door(g,-.08,vv+bd+.01,0,.16);
 }else if(kind==='farm'){
  box(g,-.6,-.58,.89,.90,0,31,'#a56f52');gable(g,-.6,-.58,.89,.90,31,21,winter?'#d6d9ca':'#665e54');
  polygon(g,[point(-.38,.33,0),point(.04,.33,0),point(.04,.33,22),point(-.38,.33,22)],'#654f3e');
  segment(g,point(-.38,.34,1),point(.04,.34,22),'#c5b18b',2);segment(g,point(.04,.34,1),point(-.38,.34,22),'#c5b18b',2);
  box(g,.34,-.62,.27,.31,0,43,'#b7b5a0','#dfd4b9');gable(g,.34,-.62,.27,.31,43,9,'#7b8276');
  for(let j=0;j<4;j++)slab(g,.32,-.08+j*.18,.40,.07,1,j%2?'#6e8250':'#b5a05d');
  for(let j=0;j<8;j++){const p=point(-.86+j*.23,.87);segment(g,[p[0],p[1]],[p[0],p[1]-7],'#a28c66',2);}segment(g,point(-.86,.87,4),point(.80,.87,4),'#c6b48b');
 }else if(kind==='worksite'||b.redevelopment){
  slab(g,u,vv,bw,bd,0,'#b8a582');
  // Keep the scaffold sprite stable; a live progress bar is drawn separately.
  // Repainting every visible building whenever a worksite crosses a stage was
  // making large towns miss the 50 ms redraw budget.
  const h=18;box(g,u+.05,vv+.05,bw-.1,bd-.1,0,h,'#bba98a');
  for(let i=0;i<4;i++){const x=u+i*bw/3;segment(g,point(x,vv+bd,0),point(x,vv+bd,h+8),'#927d58',2);}segment(g,point(u,vv+bd,h+5),point(u+bw,vv+bd,h+5),'#d8bd83',2);
  segment(g,point(.28,-.15,0),point(.28,-.15,69),'#bf9e5a',2);segment(g,point(-.35,-.15,66),point(.72,-.15,66),'#d1b16a',2);segment(g,point(.61,-.15,66),point(.61,-.15,40),'#5a6250');
 }else if(kind==='park'||kind==='square'){
  slab(g,-.42,-.42,.84,.84,1,kind==='square'?'#c4bba1':'#79925e');
  if(kind==='square'){box(g,-.12,-.12,.24,.24,2,4,'#b2b59e','#82a4a0');box(g,-.025,-.025,.05,.05,7,13,'#c8c7ad');}
  else{tree(g,-.17,-.17,id,.60);slab(g,-.42,.16,.84,.11,1,'#c9bb93');}
  box(g,.14,.29,.28,.08,2,3,'#8a7351');
 }else if(kind==='factory'||kind==='warehouse'||kind==='sawmill'){
  box(g,u,vv,bw,bd,0,30,'#a99d83');
  for(let j=0;j<3;j++)gable(g,u+j*bw/3,vv,bw/3,bd,31,kind==='factory'?13:6,roof);
  for(let i=0;i<4;i++)windowPane(g,u+.08+i*bw*.22,vv+bd+.01,15,'front',nightMode&&!closed,.19,7);
  box(g,u+.06,vv+.03,.13,.15,27,kind==='factory'?49:26,'#8e7e68');
  box(g,u+bw+.06,vv+.30,.26,.27,0,8,'#b39c73');
  door(g,u+bw*.4,vv+bd+.02,0,.25);
 }else if(kind==='metro_station'){
  slab(g,-.84,-.83,1.68,1.66,1,'#b9b49c');box(g,-.63,-.50,1.06,.70,0,23,'#beb79c');gable(g,-.63,-.50,1.06,.70,23,13,roof);
  for(let j=0;j<4;j++)windowPane(g,-.5+j*.24,.21,7,'front',nightMode,.16,9);
  box(g,.49,-.49,.20,.20,0,17,'#5c766e');const p=point(.50,-.48,21);g.fillStyle='#efdfb4';g.font='bold 7px serif';g.fillText('M',p[0],p[1]);
  slab(g,-.54,.40,.8,.28,1,'#65756d');for(let k=0;k<5;k++)segment(g,point(-.54,.40+k*.05,1),point(.26,.40+k*.05,1),'#aaa88f');
 }else if(kind==='airport'){
  box(g,-.72,-.65,1.2,.65,0,20,'#c2baa0');slab(g,-.76,-.69,1.28,.73,22,roof);for(let j=0;j<5;j++)windowPane(g,-.6+j*.2,.01,7,'front',nightMode,.15,9);
  box(g,.5,-.62,.23,.23,0,48,'#aaa894');box(g,.43,-.69,.37,.37,48,10,'#779795');slab(g,.39,-.73,.45,.45,60,'#5f7470');
 }else if(kind==='wharf'||kind==='fishery'){
  box(g,-.34,-.29,.61,.53,1,kind==='wharf'?20:16,'#a99670');gable(g,-.34,-.29,.61,.53,kind==='wharf'?21:17,9,'#648887');door(g,-.08,.25,1,.15);windowPane(g,.28,-.18,8,'side',nightMode,.14,6);
  for(let j=0;j<3;j++){box(g,-.34+j*.20,.30,.15,.12,0,4,'#b79b63');segment(g,point(-.33+j*.20,.31,4),point(-.20+j*.20,.42,4),'#dcc39a');}
  if(kind==='wharf'){segment(g,point(.32,-.25,0),point(.32,-.25,37),'#8d8159',2);segment(g,point(.32,-.25,35),point(-.30,-.25,35),'#c4ad78',2);segment(g,point(-.26,-.25,35),point(-.26,-.25,9),'#535e51');}else{for(let k=0;k<4;k++)segment(g,point(-.30+k*.13,-.30,4),point(-.30+k*.13,-.30,12),'#c7bea0');}
 }else if(kind==='quarry'){
  slab(g,-.38,-.38,.76,.76,1,'#a4aa95');slab(g,-.29,-.29,.58,.58,2,'#8e9685');slab(g,-.17,-.16,.34,.33,3,'#727e73');box(g,.1,-.4,.2,.17,0,14,'#b8ad86');
 }else if(kind==='forestry'){
  box(g,-.24,-.24,.48,.48,0,15,'#a58c65');gable(g,-.24,-.24,.48,.48,15,8,roof);tree(g,-.35,-.34,id,.45);for(let j=0;j<4;j++)box(g,-.37+j*.17,.32,.13,.10,0,4,'#b2a078');
 }else{
  const civic=['townhall','school','clinic','courthouse','college','bank'].includes(kind),H=civic?32:25;
  box(g,u,vv,bw,bd,0,H,kind==='fire'?'#b4836a':wall);gable(g,u,vv,bw,bd,H+1,civic?13:10,roof);
  const rows=civic?2:1;for(let row=0;row<rows;row++)for(let j=0;j<3;j++){windowPane(g,u+.05+j*bw*.30,vv+bd+.01,5+row*15,'front',nightMode&&!closed,.12,7);}
  for(let j=0;j<2;j++)windowPane(g,u+bw+.01,vv+.1+j*bd*.45,12,'side',nightMode&&!closed,.13,7);
  door(g,-.07,vv+bd+.02,0,.14);
  if(kind==='townhall'||kind==='courthouse'){box(g,-.1,-.12,.20,.22,H+4,20,'#c5b799');gable(g,-.1,-.12,.20,.22,H+24,11,'#5d776e');const p=point(.03,.11,H+15);g.fillStyle='#e6d7b1';g.fillRect(p[0]-3,p[1]-3,6,6);segment(g,[p[0],p[1]],[p[0],p[1]-2],'#49584e');}
  if(kind==='grocer'||kind==='bakery'||kind==='tavern'){
   for(let j=0;j<6;j++)slab(g,u+j*bw/6,vv+bd,bw/6,.17,16,j%2?'#e5d8b2':kind==='grocer'?'#637d65':kind==='tavern'?'#9d7751':'#a5725a');
   const p=point(.04,vv+bd+.03,23);g.fillStyle='#544e3e';g.font='5px monospace';g.textAlign='center';g.fillText(kind==='grocer'?'MARKET':kind==='bakery'?'BAKERY':'THE VALE',p[0],p[1]);
   box(g,u-.03,vv+bd+.18,.18,.12,0,7,'#9e8662');
  }
  if(kind==='mill'){chimney(g,u+.04,vv+.05,H+8);box(g,u+bw+.02,vv+.05,.12,.15,5,23,'#8f8b70');}
  if(kind==='fire'){polygon(g,[point(-.2,vv+bd+.01,0),point(.2,vv+bd+.01,0),point(.2,vv+bd+.01,19),point(-.2,vv+bd+.01,19)],'#725749');}
  if(gameOptions.decor&&['school','college','bank','police'].includes(kind)){
   const ink=kind==='police'?'#335c6c':kind==='bank'?'#725937':'#79694a';
   if(kind==='bank'){for(let j=0;j<4;j++){const x=u+.035+j*bw*.29;box(g,x,vv+bd+.01,.045,.075,0,H-2,'#d9cdab');}slab(g,u-.04,vv+bd-.01,bw+.08,.17,H-1,'#e1d4b0');}
   const sign=point(0,vv+bd+.05,H-1);g.fillStyle=ink;g.fillRect(sign[0]-12,sign[1]-4,24,6);g.fillStyle='#eee1bc';g.font='4px monospace';g.textAlign='center';g.fillText(kind==='police'?'POLICE':kind==='bank'?'BANK':kind==='school'?'SCHOOL':'COLLEGE',sign[0],sign[1]+1);
   if(kind==='school'||kind==='college'){box(g,-.08,-.10,.16,.18,H+7,15,'#d6c49d');gable(g,-.10,-.12,.20,.22,H+22,7,roof);const bell=point(.025,.09,H+12);g.fillStyle='#7c6846';g.fillRect(bell[0]-2,bell[1]-5,4,5);g.fillStyle='#cba657';g.fillRect(bell[0]-1,bell[1]-3,2,3);}
   if(kind==='police'){const flag=point(u-.08,vv+bd,0);segment(g,flag,[flag[0],flag[1]-H-4],'#5f6f61');g.fillStyle='#536c84';g.fillRect(flag[0]+1,flag[1]-H-3,7,4);g.fillStyle='#d9bd74';g.fillRect(flag[0]+3,flag[1]-H-2,2,2);}
  }
  if(gameOptions.decor&&kind==='tavern'){const q=point(u-.06,vv+bd+.06,20);segment(g,q,[q[0]-7,q[1]],'#594a37',2);g.fillStyle='#72563c';g.fillRect(q[0]-10,q[1]+1,8,8);g.fillStyle='#e2bf71';g.fillRect(q[0]-8,q[1]+3,3,4);}
  if(gameOptions.decor&&(kind==='grocer'||kind==='bakery')){for(let j=0;j<3;j++){box(g,u+.1+j*.14,vv+bd+.12,.12,.11,0,4,'#ad8652');const q=point(u+.15+j*.14,vv+bd+.16,4);g.fillStyle=kind==='grocer'?['#b65036','#d0ae4b','#5a7c45'][j]:'#dfbd79';g.fillRect(q[0]-3,q[1]-2,6,2);}}
  if(kind==='clinic'){const p=point(0,vv+bd+.03,H-5);g.fillStyle='#a86e55';g.fillRect(p[0]-3,p[1]-1,7,2);g.fillRect(p[0],p[1]-4,2,8);}
 }
 if(gameOptions.decor&&['home','grocer','bakery','tavern','clinic','school'].includes(kind)){
  // Garden border, stone edging, planted beds and a porch rail fit the parcel.
  for(const side of [-1,1]){const u=side*.39;for(let j=0;j<4;j++){const v=-.36+j*.21,q=point(u,v,0);g.fillStyle='#42643d';g.fillRect(q[0]-3,q[1]-4,6,4);g.fillStyle='#7c9848';g.fillRect(q[0]-2,q[1]-5,4,2);if((id+j)%3){g.fillStyle=['#efc575','#ce8270','#d4cae1'][(id+j)%3];g.fillRect(q[0],q[1]-5,2,2);}}}
  if(kind==='home'){for(let j=0;j<7;j++){const x=-.46+j*.15;if(Math.abs(x)<.13)continue;const q=point(x,.46);segment(g,[q[0],q[1]],[q[0],q[1]-6],'#ded1a5',2);}segment(g,point(-.46,.46,3),point(-.15,.46,3),'#ab966e');segment(g,point(.15,.46,3),point(.46,.46,3),'#ab966e');}
 }
 // Visual decline is tied to property condition and business closure.
 if(closed||b.condition<45){for(let j=0;j<5;j++){const p=point((hash(id+j)%50)/100-.25,.34);g.fillStyle='#6c7853';g.fillRect(p[0],p[1]-3,2,4);}const p=point(0,bd/2+.02,10);g.fillStyle='#a5906d';g.fillRect(p[0]-5,p[1],10,3);}
}
function streetProp(g,kind){
 if(kind===0){box(g,-.05,-.05,.10,.10,0,3,'#7a7c61');segment(g,[0,0],[0,-28],'#586c5a',2);g.fillStyle='#4c5f50';g.fillRect(-4,-30,8,2);g.fillStyle=nightMode?'#f7d482':'#d4c9a1';g.fillRect(-3,-28,6,6);g.fillStyle='#5a6a54';g.fillRect(-4,-22,8,2);polygon(g,[[-5,-30],[0,-34],[5,-30]],'#596b55');}
 else if(kind===1){for(const u of [-.21,.14])box(g,u,.01,.04,.10,0,6,'#5a674d');box(g,-.24,-.07,.48,.18,5,2,'#ad8b59');box(g,-.24,-.07,.48,.025,7,6,'#b19362');segment(g,point(-.24,-.07,10),point(.24,-.07,10),'#ddbf83');}
 else{box(g,-.15,-.12,.30,.24,0,6,'#a3926c');for(let j=0;j<7;j++){const q=point((j%3-1)*.1,Math.floor(j/3)*.07-.06,7);g.fillStyle='#527442';g.fillRect(q[0]-2,q[1]-3,4,4);g.fillStyle=['#d98e77','#e3c77a','#c5b7d2'][j%3];g.fillRect(q[0]-1,q[1]-4,3,2);}}
}
function spriteFor(item){
 const season=Math.floor((visualMonth()-1)/3),b=item.b,variant=b?(b.kind==='home'?b.id%120:b.id%24):0;
 const key=item.kind==='streetprop'?`prop:${item.id%3}:${nightMode}`:item.kind==='tree'?`tree:${season}:${item.id%11}`:`${b.kind}:${variant}:${item.w}:${item.d}:${season}:${nightMode}:${b.condition<45}:${b.firm>=0&&G.firms[b.firm]?.closed}:${b.redevelopment?'renewal':''}:${appearanceKey(b)}`;
 if(atlas.has(key)){const cached=atlas.get(key);atlas.delete(key);atlas.set(key,cached);return cached;}
 // Tight, conservative sprite envelopes avoid uploading acres of transparent
 // pixels whenever a dense viewport changes. Geometry keeps its world anchor.
 const side=item.kind==='building'?Math.ceil((item.w+item.d)*18+20):36,top=item.kind==='building'?(b.kind==='tower'?192:112):72,bottom=item.kind==='building'?Math.ceil((item.w+item.d)*18+24):24;
 const c=document.createElement('canvas');c.width=side*2;c.height=top+bottom;c.anchorX=side;c.anchorY=top;const g=c.getContext('2d');g.translate(c.anchorX,c.anchorY);
 if(item.kind==='streetprop')streetProp(g,item.id%3);else if(item.kind==='tree')tree(g,0,0,item.id%11,.83);else{polygon(g,[point(-item.w*.4,-item.d*.4),point(item.w*.6,-item.d*.4),point(item.w*.9,item.d*.3),point(0,item.d*.7)],'#48523f30');architecture(g,b.kind==='worksite'||b.redevelopment?b:{...b,id:variant},item.w,item.d);parcelDetails(g,b,item.w,item.d);architecturalIdentity(g,b,item.w,item.d);}
 atlas.set(key,c);atlasBytes+=c.width*c.height*4;while(atlas.size>600||atlasBytes>48*1024*1024){const oldest=atlas.keys().next().value,retired=atlas.get(oldest);atlasBytes-=retired.width*retired.height*4;atlas.delete(oldest);}return c;
}
function drawSceneSprite(g,item){const sprite=spriteFor(item);g.drawImage(sprite,Math.round(item.x-sprite.anchorX),Math.round(item.y-sprite.anchorY));}
function prepareScene(){
 displayItems=[];const occupied=new Set(G.buildings.flatMap(b=>footprintOf(b)));
 for(let y=0;y<T;y++)for(let x=0;x<T;x++){const id=roadId(x,y);if(G.tiles[id]===3&&!occupied.has(id)&&!G.landUse?.[id]&&hash(id+G.worldSeed)%4!==0){const [px,py]=iso(x,y);displayItems.push({kind:'tree',id,x:px,y:py+18,w:1,d:1});}}
 for(const b of G.buildings){const fp=footprintOf(b),xs=fp.map(id=>id%T),ys=fp.map(id=>id/T|0),w=Math.max(...xs)-Math.min(...xs)+1,d=Math.max(...ys)-Math.min(...ys)+1;const [x,y]=iso(b.x+(w-1)/2,b.y+(d-1)/2);displayItems.push({kind:'building',id:b.id,b,x,y:y+18,w,d});}
 if(gameOptions.decor&&gameOptions.quality!=='low')for(let y=2;y<T-2;y++)for(let x=2;x<T-2;x++){
  const id=roadId(x,y);if(G.tiles[id]!==0||occupied.has(id)||G.landUse?.[id]||hash(id+G.worldSeed)%13!==0)continue;
  if(![roadId(x-1,y),roadId(x+1,y),roadId(x,y-1),roadId(x,y+1)].some(n=>G.tiles[n]===1))continue;
  const [px,py]=iso(x,y);displayItems.push({kind:'streetprop',id,x:px,y:py+18,w:1,d:1});
 }
 displayItems.sort((a,b)=>a.y-b.y||a.id-b.id);buildingItemsById=new Map(displayItems.filter(item=>item.b).map(item=>[item.id,item]));sceneSignature=G.buildings.length+':'+G.month+':'+G.construction;
}
function fastRenderEnabled(){return !!G&&!paused&&speed>=64&&gameOptions.quality!=='high'}
function diamondFast(g,x,y,fill){const p=iso(x,y);g.beginPath();g.moveTo(p[0],p[1]);g.lineTo(p[0]+TW/2,p[1]+TH/2);g.lineTo(p[0],p[1]+TH);g.lineTo(p[0]-TW/2,p[1]+TH/2);g.closePath();g.fillStyle=fill;g.fill()}
function drawGround(){
 const fastRender=fastRenderEnabled();
 // Uploading a changed full-world bitmap can stall software Canvas. At 64×,
 // retain a half-resolution ground layer; buildings and labels stay independent.
 groundScale=Math.min(fastRender?.5:1,Math.sqrt((fastRender?2200000:9000000)/(RW*RH)));
 const width=Math.round(RW*groundScale),height=Math.round(RH*groundScale);
 if(bitmap.width!==width||bitmap.height!==height){bitmap.width=width;bitmap.height=height;}
 const s=seasonPalette(),net=graph();bg.setTransform(groundScale,0,0,groundScale,0,0);bg.fillStyle='#5d7967';bg.fillRect(0,0,RW,RH);
 const occupied=new Set(G.buildings.flatMap(b=>footprintOf(b)));
 const fastGrass=s.grass.map(c=>tone(c,.92));
 for(let y=0;y<T;y++)for(let x=0;x<T;x++){
  const id=roadId(x,y),type=G.tiles[id],h=hash(id+G.worldSeed),p=iso(x,y),lu=G.landUse?.[id];
  const tileColor=type===2?s.water:type===1?'#b3b09a':lu===1?(visualMonth()>=10?'#c8cbb5':visualMonth()>=7?'#b4a36d':'#99a06a'):lu===2?'#aa9b7b':lu===3?'#7b827a':s.grass[(Math.floor(Math.sin(x*.18+y*.11)*1.4+Math.cos(y*.22)*.8)+7)%5];
  if(fastRender)diamondFast(bg,x,y,!charterOwns(x,y)&&type!==2?(type===3?fastGrass[1]:fastGrass[2]):tileColor);else diamond(bg,x,y,tileColor);
  if(!fastRender&&!charterOwns(x,y)&&type!==2){polygon(bg,[[p[0],p[1]],[p[0]+36,p[1]+18],[p[0],p[1]+36],[p[0]-36,p[1]+18]],'#a5ac8430');}
  if(!fastRender&&type===2){bg.fillStyle='#b5cdc0';if(h%3===0)bg.fillRect(p[0]-12+(h%17),p[1]+16,9,1);if(x<T-1&&G.tiles[id+1]!==2){segment(bg,[p[0]+35,p[1]+18],[p[0],p[1]+35],'#bdbaa0',3);}}
  else if(!fastRender&&type!==1&&!occupied.has(id)&&!lu){for(let j=0;j<3;j++){let k=hash(h+j*37);bg.fillStyle=j===0?s.dark:tone(s.grass[2],1.04);bg.fillRect(p[0]-15+(k%30),p[1]+9+((k>>>8)%16),2+(k%3),1);}if(h%37===0&&visualMonth()<10){bg.fillStyle=visualMonth()<4?'#e2d5ad':'#c9b486';bg.fillRect(p[0]+5,p[1]+21,2,2);}}
  if(!fastRender&&gameOptions.decor&&gameOptions.quality!=='low'&&type===0&&!occupied.has(id)&&!lu){
   // Sparse wildflowers and small blade clusters, arranged by the town seed.
   if(h%9===0){for(let j=0;j<5;j++){const k=hash(h+j*37),xx=p[0]-12+(k%23),yy=p[1]+12+((k>>>7)%11);bg.fillStyle='#597c40';bg.fillRect(xx,yy,1,4);bg.fillStyle=['#e8d38d','#d2b1be','#bdc8df'][h%3];bg.fillRect(xx-1,yy-1,3,2);}}
   if(h%13===0){for(let j=0;j<4;j++){const xx=p[0]-9+j*5,yy=p[1]+19+j%2;bg.fillStyle='#658344';bg.fillRect(xx,yy,1,3);bg.fillRect(xx+1,yy-1,1,2);}}
  }
  if(!fastRender&&type===2&&gameOptions.decor){if(h%4===0){bg.fillStyle='#87b7ad';bg.fillRect(p[0]-10,p[1]+20,13,1);bg.fillStyle='#477f88';bg.fillRect(p[0]+4,p[1]+15,8,1);}}
  livingTerrain(bg,x,y,type,h);
  if(lu===1){for(let j=-2;j<=2;j++){segment(bg,[p[0]-19+j*4,p[1]+17+j*2],[p[0]+9+j*4,p[1]+31+j*2],visualMonth()>=10?'#acb59b':visualMonth()>=7?'#dbc48a':'#677e4e',2);}}
  if(lu===3){segment(bg,[p[0]-25,p[1]+6],[p[0]+25,p[1]+31],'#aeb6a7',1);segment(bg,[p[0]-20,p[1]+12],[p[0]+20,p[1]+32],'#d7d6bc',1);}
 }
 drawAirfieldGround(bg);
 // Streets have sidewalks and a visible hierarchy, with crossings at junctions.
 for(const [id,links] of net.neighbors){const a=roadCenter(id);for(const n of links){if(n<id)continue;const q=roadCenter(n),kind=G.roadClasses?.[id]||'local',width=kind==='arterial'?32:kind==='collector'?26:20;
  segment(bg,a,q,'#c4bfa6',width+9);if(!fastRender)segment(bg,a,q,'#7e8881',width+3);segment(bg,a,q,'#717d77',width);if(!fastRender&&kind!=='local'){bg.setLineDash([4,8]);segment(bg,a,q,'#d5c99d',1);bg.setLineDash([]);}
 }}
 for(const [id,links] of net.neighbors){if(links.length<3)continue;const a=roadCenter(id);bg.fillStyle='#717d77';bg.beginPath();bg.ellipse(...a,17,9,0,0,Math.PI*2);bg.fill();
  if(!fastRender)for(const n of links){const q=roadCenter(n),dx=q[0]-a[0],dy=q[1]-a[1],l=Math.hypot(dx,dy),ux=dx/l,uy=dy/l,nx=-uy,ny=ux;for(let j=0;j<4;j++){const x=a[0]+ux*(21+j*3),y=a[1]+uy*(21+j*3);segment(bg,[x+nx*6,y+ny*6],[x-nx*6,y-ny*6],'#d4d3b8',1.4);}}
 }
}
let groundSignature='',groundRevision=0,groundScale=1;
function drawStatic(){
 const signature=[G.worldSeed,visualMonth(),gameOptions.decor,gameOptions.quality,fastRenderEnabled(),
  G.tiles.join(''),JSON.stringify(G.landUse||{}),JSON.stringify(G.roadClasses||{}),
  JSON.stringify(G.airport?.runway||[]),G.charter?.revision||0].join('|');
 if(signature!==groundSignature){drawGround();groundSignature=signature;groundRevision++;}
 prepareScene();landscapeRevision++;staticDirty=false;lastSceneMonth=visualMonth();
}
let fastRenderMode=false;
function fit(){const bounds=cv.getBoundingClientRect(),fast=fastRenderEnabled();if(fast!==fastRenderMode){fastRenderMode=fast;staticDirty=true;viewRasterKey='';viewBackgroundKey='';}dpr=Math.min(window.devicePixelRatio||1,gameOptions.quality==='high'?1.5:gameOptions.quality==='low'?1:1.25)*(fast?0.75:1);cw=Math.max(1,bounds.width);ch=Math.max(1,bounds.height);cv.width=Math.round(cw*dpr);cv.height=Math.round(ch*dpr);dirty=true;}
function transform(){ctx.setTransform(dpr,0,0,dpr,0,0);ctx.translate(cw/2,ch/2);ctx.scale(cam.zoom,cam.zoom);ctx.translate(-cam.x,-cam.y);}
function vehiclePaint(g,v,p,clock){
 if(v.style==='pedestrian'){
  const facing=p.dx>=0?1:-1,phase=clock*7+v.id,swing=Math.sin(phase)*2,x=Math.round(p.x),y=Math.round(p.y),skin=['#d6b38b','#c79570','#9d7358'][v.id%3];
  g.fillStyle='#324c3c40';g.fillRect(x-3,y+1,7,2);g.fillStyle='#394a42';g.fillRect(x-2,y-1+Math.round(swing),2,3);g.fillRect(x+1,y-1-Math.round(swing),2,3);
  g.fillStyle=v.color;g.fillRect(x-2,y-7,5,6);g.fillStyle=tone(v.color,.75);g.fillRect(x+2,y-6,1,5);g.fillStyle=skin;g.fillRect(x-1,y-11,4,4);g.fillRect(x-3,y-5+Math.round(swing*.5),1,4);g.fillRect(x+3,y-5-Math.round(swing*.5),1,4);g.fillStyle='#63523d';g.fillRect(x-1,y-12,4,2);if(p.dy>=0){g.fillStyle='#384d44';g.fillRect(x+(facing>0?2:0),y-9,1,1);}else{g.fillStyle='#63523d';g.fillRect(x-1,y-11,4,3);}return;
 }
 g.save();g.translate(Math.round(p.x),Math.round(p.y));
 const magnitude=Math.hypot(p.dx,p.dy)||1,dx=p.dx/magnitude,dy=p.dy/magnitude;
 // Project a horizontal vehicle plane. Rotating the body, cab and all four wheels
 // together avoids the old fixed-orientation body with a moving headlight.
 g.transform(dx,dy,-dy*1.35,dx*.45,0,0);
 const truck=v.style==='truck',tractor=v.style==='tractor',L=truck?14:tractor?10:11,W=tractor?5:4;
 g.fillStyle='#283c3644';g.fillRect(-L-1,-W+2,L*2+3,W*2+2);
 for(const x of [-L+3,L-4])for(const y of [-W-2,W-1]){g.fillStyle='#2e3834';g.fillRect(x-2,y,5,3);g.fillStyle='#9b9e86';g.fillRect(x,y+1,2,1);}
 g.fillStyle=tone(v.color,.68);g.fillRect(-L,-W,L*2,W*2+2);g.fillStyle=truck?'#bda77b':v.color;g.fillRect(-L,-W-2,L*2,W*2);
 g.fillStyle=tone(v.color,1.23);g.fillRect(-L+1,-W-2,L*2-2,1);
 if(truck){g.fillStyle='#dccca0';g.fillRect(-L,-W-2,L+2,W*2);g.fillStyle='#826b50';for(let j=-L+3;j<0;j+=3)g.fillRect(j,-W-2,1,W*2);}
 const cab=truck?5:0;g.fillStyle='#d1cdb0';g.fillRect(cab-4,-W-3,8,W*2);g.fillStyle='#5d989d';g.fillRect(cab+2,-W-3,3,W*2);g.fillStyle='#436b6c';g.fillRect(cab-4,-W-3,2,W*2);g.fillStyle=tone(v.color,1.1);g.fillRect(cab-1,-W-3,3,W*2);
 g.fillStyle='#ffe5a0';g.fillRect(L-1,-W,2,2);g.fillRect(L-1,W-3,2,2);g.fillStyle='#b94d39';g.fillRect(-L,-W,2,2);g.fillRect(-L,W-3,2,2);
 if(v.emergency){g.fillStyle=Math.floor(clock*5)%2?'#e79950':'#c94d41';g.fillRect(cab,-W-5,3,2);}g.restore();
}
function atmosphere(g,sx,sy,ww,hh){
 if(!gameOptions.effects||gameOptions.reducedMotion)return;
 const active=(weatherEnabled()&&(G.weather==='rain'||G.weather==='storm'))||visualMonth()>=10;
 if(active)for(let j=0;j<70;j++){const h=hash(j+G.worldSeed),x=sx+(h%1000)/1000*ww,y=sy+(((h>>>10)%1000)/1000*hh+frameClock*(visualMonth()>=10?12:120))%hh;g.strokeStyle=visualMonth()>=10?'#f8f7e399':'#dce3cf66';g.lineWidth=1;g.beginPath();g.moveTo(x,y);g.lineTo(x+(visualMonth()>=10?1:4),y+(visualMonth()>=10?1:9));g.stroke();}
 for(const item of displayItems){if(item.kind!=='building'||item.x<sx-100||item.x>sx+ww+100||item.y<sy-100||item.y>sy+hh+130)continue;const b=item.b;if(b.firm<0||G.firms[b.firm]?.closed||!workingStaff(G.firms[b.firm]).length||!(G.firms[b.firm]?.production>0)||!['factory','mill','bakery','sawmill'].includes(b.kind))continue;for(let j=0;j<3;j++){const t=(frameClock*.30+j*.40+b.id*.13)%1;g.fillStyle=`rgba(224,221,195,${.30*(1-t)})`;g.fillRect(Math.round(item.x-12+t*17),Math.round(item.y-48-t*24),3+Math.floor(t*6),3+Math.floor(t*5));}}
}
function drawConstructionProgress(g,visible){
 for(const project of G.projects){
  const item=buildingItemsById.get(project.id);if(!item||!visible(item.x,item.y,65))continue;
  const duration=Math.max(1,project.duration||30),progress=clamp(1-project.remaining/duration,0,1),x=Math.round(item.x),y=Math.round(item.y-39);
  g.fillStyle='#27372f';g.fillRect(x-15,y-2,30,4);g.fillStyle='#d4b779';g.fillRect(x-14,y-1,Math.round(28*progress),2);
 }
}
function draw(){
 if(!G||!dirty)return;dirty=false;document.body.classList.toggle('surveying-region',overlay==='charter');$('gameRoot').classList.toggle('building-map',!!buildMode);updateRegionSurvey();if(staticDirty||lastSceneMonth!==visualMonth())drawStatic();
 ctx.setTransform(1,0,0,1,0,0);ctx.fillStyle='#6d8774';ctx.fillRect(0,0,cv.width,cv.height);
 const sx=cam.x-cw/(2*cam.zoom),sy=cam.y-ch/(2*cam.zoom),ww=cw/cam.zoom,hh=ch/cam.zoom;
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.imageSmoothingEnabled=false;transform();ctx.imageSmoothingEnabled=false;
 const visible=(x,y,m=120)=>x>=sx-m&&x<=sx+ww+m&&y>=sy-m&&y<=sy+hh+m;
 // Retain the camera's static composition. Moving actors only redraw intersecting
 // foreground objects, preserving depth without repainting every house each frame.
 let states='';for(const a of displayItems)if(a.b)states+=`${a.b.kind}:${a.b.condition<45}:${a.b.firm>=0&&G.firms[a.b.firm]?.closed}:${a.b.redevelopment?1:0}:${appearanceKey(a.b)};`;
 const backgroundKey=[cam.x,cam.y,cam.zoom,cw,ch,dpr,groundRevision].join('|');
 if(backgroundKey!==viewBackgroundKey){
  if(viewBackgroundRaster.width!==cv.width)viewBackgroundRaster.width=cv.width;if(viewBackgroundRaster.height!==cv.height)viewBackgroundRaster.height=cv.height;
  const bgView=viewBackgroundRaster.getContext('2d',{alpha:false});bgView.imageSmoothingEnabled=false;bgView.setTransform(dpr,0,0,dpr,0,0);bgView.fillStyle='#5d7967';bgView.fillRect(0,0,cw,ch);bgView.drawImage(bitmap,sx*groundScale,sy*groundScale,ww*groundScale,hh*groundScale,0,0,cw,ch);viewBackgroundKey=backgroundKey;
 }
 const key=[cam.x,cam.y,cam.zoom,cw,ch,dpr,nightMode,gameOptions.streetNames,landscapeRevision,states].join('|');
 if(key!==viewRasterKey){
  if(viewRaster.width!==cv.width)viewRaster.width=cv.width;if(viewRaster.height!==cv.height)viewRaster.height=cv.height;const vg=viewRaster.getContext('2d',{alpha:false});vg.imageSmoothingEnabled=false;
  // The cached background already has backing-store dimensions. Copy it at
  // identity before applying the logical-pixel transform for world sprites.
  vg.setTransform(1,0,0,1,0,0);vg.drawImage(viewBackgroundRaster,0,0);vg.setTransform(dpr,0,0,dpr,0,0);vg.translate(cw/2,ch/2);vg.scale(cam.zoom,cam.zoom);vg.translate(-cam.x,-cam.y);
  drawStreetNames(vg,sx,sy,ww,hh);
  viewBuildings=displayItems.filter(item=>{
   const building=item.kind==='building',treeItem=item.kind==='tree';
   const xMargin=building?132:treeItem?24:38,topMargin=building?172:treeItem?64:55,bottomMargin=building?84:treeItem?34:28;
   return item.x>=sx-xMargin&&item.x<=sx+ww+xMargin&&item.y>=sy-bottomMargin&&item.y<=sy+hh+topMargin;
  });
  paintCastShadows(vg,viewBuildings);
  for(const item of viewBuildings)drawSceneSprite(vg,item);
  viewRasterKey=key;
 }
 ctx.setTransform(1,0,0,1,0,0);ctx.drawImage(viewRaster,0,0);transform();
 drawConstructionProgress(ctx,visible);drawInspectedRoute(ctx);drawWaterLife(ctx,visible);drawWaterfrontPiers(ctx,visible);drawSelectedWaterRoute(ctx);
 const visibleParcels=viewBuildings.filter(item=>visible(item.x,item.y,0)),actors=[...buildingActivity(visibleParcels),...workdayScenes(visibleParcels),...waterfrontActors(visible)];if(gameOptions.traffic)for(const v of traffic){const p=vehiclePosition(v);if(visible(p.x,p.y,15))actors.push({kind:'vehicle',v,...p});}actors.sort((a,b)=>a.y-b.y);
 if(actors.length){
  // Clip subsequent foreground re-paints to the actors' damage rectangles.
  ctx.save();ctx.beginPath();for(const a of actors)if(a.kind==='boat')ctx.rect(a.x-44,a.y-32,88,64);else ctx.rect(a.x-25,a.y-32,56,52);ctx.clip();
  const layered=[...actors,...viewBuildings.filter(a=>actors.some(v=>a.y>=v.y&&Math.abs(a.x-v.x)<112&&a.y-v.y<220))].sort((a,b)=>a.y-b.y);
  for(const a of layered){if(a.kind==='vehicle')vehiclePaint(ctx,a.v,a,frameClock);else if(a.kind==='boat')paintWaterBoat(ctx,a,frameClock);else if(a.kind==='workday')paintWorkdayScene(ctx,a,frameClock);else drawSceneSprite(ctx,a);}ctx.restore();
 }

 drawCharterBounds(ctx);paintTownLight(ctx);
 atmosphere(ctx,sx,sy,ww,hh);
 drawAviation(ctx);
 if(overlay==='metro')drawMetroOverlay(ctx);
 if(overlay==='roads'||overlay==='business'||overlay==='hardship'||overlay==='crime'||overlay==='land')for(const item of displayItems){if(item.kind!=='building'||!visible(item.x,item.y))continue;const b=item.b,f=G.firms[b.firm],h=G.households[b.hh],net=graph();let color=overlay==='roads'?(net.portals.has(b.id)?'#9ecb95':'#bb7760'):overlay==='business'?(f?(f.closed?'#b66856':f.profit>0?'#a1c67d':'#d6b46c'):null):overlay==='hardship'?(h?(h.stress>50?'#b96c56':'#a9ca87'):null):overlay==='land'?(b.value>90000?'#c38864':b.value>45000?'#d0b776':'#9fc087'):null;if(!color)continue;ctx.globalAlpha=.7;diamond(ctx,b.x,b.y,color);ctx.globalAlpha=1;}
 drawServiceAccess(ctx);
 if(selected?.id){const b=readBuild(selected.id);if(b){const p=iso(b.x,b.y);ctx.strokeStyle='#f4e2a5';ctx.lineWidth=2;ctx.beginPath();ctx.ellipse(p[0],p[1]+18,32,16,0,0,Math.PI*2);ctx.stroke();}}
 if(buildMode&&pointer.hover){const {x,y}=pointer.hover;if(['fishery','wharf'].includes(buildMode))headerText('placementHint',types[buildMode].n+' · '+money(buildCost[buildMode])+' · '+waterfrontPlacementMessage(x,y,buildMode));if(x>=0&&x<T&&y>=0&&y<T){const valid=buildMode==='road'?[0,3].includes(cityCell(x,y))&&charterOwns(x,y)&&!buildingAt(x,y)&&!G.landUse?.[roadId(x,y)]&&G.treasury>=buildCost.road:buildMode==='repair'?cityCell(x,y)===1:canPlace(x,y,true,buildMode);ctx.globalAlpha=.60;for(const id of footprintFor(x,y,buildMode))diamond(ctx,id%T,id/T|0,valid?'#c8dea4':'#c48069');ctx.globalAlpha=1;}}
 if(nightMode){ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#233c6460';ctx.fillRect(0,0,cw,ch);transform();for(const item of displayItems){if(item.kind!=='building'||!visible(item.x,item.y)||item.b.kind==='worksite')continue;const b=item.b;if(b.firm>=0&&G.firms[b.firm]?.closed)continue;const glow=ctx.createRadialGradient(item.x,item.y-12,1,item.x,item.y-12,28);glow.addColorStop(0,'#eac57a36');glow.addColorStop(1,'#eac57a00');ctx.fillStyle=glow;ctx.fillRect(item.x-28,item.y-40,56,56);}}
}

// SOURCE: 66-mobility-art.js
// Direction-aware regional aviation, road markings and pedestrian animation.
function runwayGeometry(){
 const r=G.airport?.runway;if(!r||r.length<4)return null;
 const avg=(a,b)=>{const p=roadCenter(a),q=roadCenter(b);return [(p[0]+q[0])/2,(p[1]+q[1])/2]};
 const a=avg(r[0],r[1]),b=avg(fromEnd(r,2),fromEnd(r)),dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);
 return {a,b,dx,dy,length,nx:-dy/length,ny:dx/length};
}
function drawAirfieldGround(g){
 const r=runwayGeometry();if(!r||!G.airport?.firm&&G.airport?.firm!==0)return;
 const {a,b,dx,dy,length,nx,ny}=r;
 segment(g,a,b,'#bab498',57);segment(g,a,b,'#4d5958',45);segment(g,[a[0]+nx*19,a[1]+ny*19],[b[0]+nx*19,b[1]+ny*19],'#b5b8a0',1);segment(g,[a[0]-nx*19,a[1]-ny*19],[b[0]-nx*19,b[1]-ny*19],'#b5b8a0',1);
 g.setLineDash([8,9]);segment(g,a,b,'#e7e5cc',2);g.setLineDash([]);
 for(const t of [.06,.94])for(const off of [-13,-7,7,13]){const x=a[0]+dx*t+nx*off,y=a[1]+dy*t+ny*off;segment(g,[x-dx/length*6,y-dy/length*6],[x+dx/length*6,y+dy/length*6],'#e7e5cc',3);}
 const terminal=readBuild(G.airport.building);if(terminal){const gate=iso(terminal.x,terminal.y);gate[1]+=64;segment(g,gate,a,'#a39f8b',13);segment(g,gate,a,'#d2ba68',1);}
}
function paintRegionalAircraft(g,x,y,dx,dy,altitude,clock,gear=true){
 const length=Math.hypot(dx,dy)||1,ux=dx/length,uy=dy/length;
 // Shadow stays on the ground while the aeroplane climbs.
 g.save();g.translate(x+altitude*.13,y+8);g.transform(ux,uy,-uy*1.4,ux*.55,0,0);g.globalAlpha=clamp(.30-altitude*.0012,.04,.30);g.fillStyle='#233c36';g.beginPath();g.ellipse(0,0,29,20,0,0,Math.PI*2);g.fill();g.restore();
 g.save();g.translate(Math.round(x),Math.round(y-altitude));g.transform(ux,uy,-uy*1.4,ux*.55,0,0);
 const poly=(p,c)=>polygon(g,p,c);
 // A short-haul high-wing twin turboprop: straight wing, two nacelles, cabin,
 // cockpit, tailplane, fin and landing gear, all sharing one heading.
 if(gear){g.fillStyle='#273e3a';g.fillRect(-3,-10,5,3);g.fillRect(-3,7,5,3);g.fillRect(18,-1,4,3);}
 poly([[-23,-12],[-17,-12],[-13,-3],[-13,3],[-17,12],[-23,12],[-20,0]],'#c8d1c6');
 poly([[7,-29],[-1,-29],[-8,-5],[-8,5],[-1,29],[7,29],[5,6],[5,-6]],'#d8decb');
 segment(g,[5,-27],[5,27],'#91a6a0');
 for(const side of [-1,1]){const v=side*14;poly([[-4,v-3],[9,v-3],[13,v-1],[13,v+1],[8,v+3],[-4,v+3]],'#7e9a97');g.fillStyle='#d4c9a2';g.fillRect(8,v-3,4,6);const turn=clock*27,span=Math.sin(turn)*7;segment(g,[13,v-span],[13,v+span],'#505e5866',2);segment(g,[13-2,v+span*.25],[13+2,v-span*.25],'#b4bdab',1);}
 poly([[-27,-2],[-18,-4],[17,-4],[26,-2],[29,0],[25,3],[17,5],[-18,4],[-27,2]],'#dce1cf');
 poly([[-23,2],[19,2],[26,0],[25,3],[17,5],[-18,4]],'#789a99');
 poly([[19,-3],[25,-1],[25,1],[19,2],[16,0]],'#385d67');
 for(let j=0;j<6;j++){g.fillStyle='#4b7380';g.fillRect(-12+j*4,-3,2,2);g.fillStyle='#e8e2c7';g.fillRect(-12+j*4,-1,2,1);}
 poly([[-23,0],[-22,-11],[-17,-11],[-14,0]],'#789b9a');poly([[-22,-11],[-17,-11],[-17,-7],[-22,-7]],'#c8b56e');
 g.fillStyle='#bc5444';g.fillRect(-1,-29,3,2);g.fillStyle='#6ba57d';g.fillRect(-1,27,3,2);g.restore();
}
function aviationPose(r,gate,phase){
 const a=r.a,b=r.b,lerp=(p,q,t)=>[p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t];let pos,heading=[r.dx,r.dy],alt=0,gear=true;
 const taxi=(p,q,c1,c2,t)=>{const u=1-t;return {pos:[0,1].map(k=>u*u*u*p[k]+3*u*u*t*c1[k]+3*u*t*t*c2[k]+t*t*t*q[k]),heading:[0,1].map(k=>3*u*u*(c1[k]-p[k])+6*u*t*(c2[k]-c1[k])+3*t*t*(q[k]-c2[k]))};};
 if(phase<8){const bend=Math.min(.15,Math.hypot(a[0]-gate[0],a[1]-gate[1])/r.length*.35);({pos,heading}=taxi(gate,a,lerp(gate,a,.35),[a[0]-r.dx*bend,a[1]-r.dy*bend],phase/8));}
 else if(phase<18){const t=(phase-8)/10;pos=lerp(a,b,t*t);alt=Math.max(0,t-.55)*110;}
 else if(phase<32){const u=phase-18;pos=[b[0]+r.dx*(u*.2+u*u*.005),b[1]+r.dy*(u*.2+u*u*.005)];alt=49.5+u*11;gear=false;}
 else if(phase<50)return null;
 else if(phase<66){const t=(phase-50)/16;pos=[a[0]-r.dx*(1-t)*4,a[1]-r.dy*(1-t)*4];alt=(1-t)*(1-t)*140;gear=t>.55;}
 else if(phase<75){const t=(phase-66)/9;pos=lerp(a,b,2.25*t-1.5*t*t+.25*t*t*t);}
 else if(phase<85){const bend=Math.min(.15,Math.hypot(b[0]-gate[0],b[1]-gate[1])/r.length*.35);({pos,heading}=taxi(b,gate,[b[0]+r.dx*bend,b[1]+r.dy*bend],lerp(b,gate,.7),(phase-75)/10));}
 else{pos=gate;heading=[gate[0]-b[0],gate[1]-b[1]];}
 return {pos,heading,alt,gear};
}
function drawAviation(g){
 const air=G.airport,r=runwayGeometry();if(!air?.operating||!r)return;
 const terminal=readBuild(air.building);if(!terminal)return;const gate=iso(terminal.x,terminal.y);gate[1]+=64;
 const phase=gameOptions.reducedMotion?88:frameClock%90,pose=aviationPose(r,gate,phase);if(!pose)return;
 const {pos,heading,alt,gear}=pose;
 paintRegionalAircraft(g,...pos,...heading,alt,frameClock,gear);
}
function drawStreetNames(g,sx,sy,ww,hh){
 if(!gameOptions.streetNames||!G.streetNames||cam.zoom<.48)return;
 const zoom=cam.zoom,compact=zoom<.82,minLength=zoom<.64?22:compact?17:12;
 const rank={local:1,collector:2,arterial:3,through:4},streets=new Map();
 for(const [key,name] of Object.entries(G.streetNames)){
  const id=+key;if(G.tiles[id]!==1)continue;
  if(!streets.has(name))streets.set(name,[]);streets.get(name).push(id);
 }
 const candidates=[];
 for(const [name,ids] of streets){
  if(ids.length<minLength)continue;
  const roadRank=ids.reduce((best,id)=>Math.max(best,rank[G.roadClasses?.[id]]||0),0);
  if(compact&&roadRank<2)continue;
  const mid=ids[Math.floor(ids.length*.55)],p=roadCenter(mid);
  if(p[0]<sx-100||p[0]>sx+ww+100||p[1]<sy-100||p[1]>sy+hh+100)continue;
  const a=roadCenter(ids[0]),b=roadCenter(fromEnd(ids));
  candidates.push({name,ids,p,a,b,roadRank});
 }
 candidates.sort((a,b)=>b.roadRank-a.roadRank||b.ids.length-a.ids.length||a.name.localeCompare(b.name));
 const maxLabels=compact?Math.max(4,Math.floor(cw*ch/55000)):Math.max(8,Math.floor(cw*ch/30000));
 const placed=[],screenFont=compact?8:9,fontSize=screenFont/zoom;
 g.font=`bold ${fontSize}px Arial`;g.textAlign='center';
 for(const item of candidates){
  if(placed.length>=maxLabels)break;
  const text=item.name.toUpperCase(),screenX=(item.p[0]-sx)*zoom,screenY=(item.p[1]-sy)*zoom;
  const width=g.measureText(text).width*zoom,height=screenFont+4;
  if(placed.some(box=>Math.abs(box.x-screenX)<(box.width+width)/2+7&&Math.abs(box.y-screenY)<Math.max(box.height,height)+2))continue;
  let angle=Math.atan2(item.b[1]-item.a[1],item.b[0]-item.a[0]);if(angle>Math.PI/2||angle<-Math.PI/2)angle+=Math.PI;
  g.save();g.translate(...item.p);g.rotate(angle);g.font=`bold ${fontSize}px Arial`;g.textAlign='center';g.strokeStyle='#50615a';g.lineWidth=2/zoom;g.strokeText(text,0,-3/zoom);g.fillStyle='#efe8ce';g.fillText(text,0,-3/zoom);g.restore();
  placed.push({x:screenX,y:screenY,width,height});
 }
}

// SOURCE: 67-transport.js
function setPurposeStyle(v,style){v.style=style;v.speed=style==='pedestrian'?.53:style==='truck'?.90:1.15;return v;}
function restoreTransport(){
 const state=G.trafficState;visualState=G.visualState||918273;
 traffic=[];trafficClock=0;intersectionGates.clear();
 if(state){traffic=(state.vehicles||[]).filter(v=>Array.isArray(v.path)&&v.path.length>=2&&v.path.every(n=>Number.isInteger(n)&&G.tiles[n]===1)&&Number.isInteger(v.segment)&&v.segment>=0&&v.segment<v.path.length-1&&Number.isFinite(v.fraction)&&v.fraction>=0&&v.fraction<1).slice(0,80).map(v=>({...v,path:v.path.slice()}));frameClock=Number(state.clock)||0;trafficElapsed=Number(state.elapsed)||0;vehicleSerial=Number(state.serial)||0;intersectionGates=new Map((state.gates||[]).filter(a=>Array.isArray(a)&&a.length===2));}
}
function pendingGoods(firm,good){return (G.freight||[]).filter(s=>s.to===firm.id&&s.good===good).reduce((n,s)=>n+s.qty,0);}
function dispatchGoods(seller,buyer,good,qty,path){
 G.freight=G.freight||[];G.nextFreight=(G.nextFreight||0)+1;
 const duration=Math.max(1,Math.ceil((path.length-1)/15));
 G.freight.push({id:G.nextFreight,from:seller.id,to:buyer.id,good,qty,path,remaining:duration,duration,started:G.day,delayed:0});
}
function freightDay(){
 if(!G.freight?.length)return;
 const keep=[];
 for(const s of G.freight){const from=G.firms[s.from],to=G.firms[s.to];if(!from||!to){throw Error('Shipment has an invalid owner');}
  const route=routeBetween(readBuild(from.building),readBuild(to.building));
  if(route.length<1){s.delayed++;keep.push(s);G.transport.delayed++;continue;}
  s.path=route;s.remaining--;
  if(s.remaining>0)keep.push(s);else{to.stock[s.good]=(to.stock[s.good]||0)+s.qty;G.transport.arrived++;}
 }
 G.freight=keep;
}
function spawnPurposeTrip(){
 if(!G)return null;
 // Trips are samples of actual commuter assignments or paid in-flight cargo.
 const freights=G.freight||[];if(freights.length&&vehicleSerial%3===0){const s=freights[vehicleSerial%freights.length],f=G.firms[s.from],t=G.firms[s.to];const v=beginVehicle(readBuild(f.building),readBuild(t.building));if(v){setPurposeStyle(v,'truck');v.reason=s.qty.toFixed(0)+' '+s.good+' → '+t.name;v.shipment=s.id;return v;}}
 const employed=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.job>=0);if(!employed.length)return null;
 const p=employed[hash(vehicleSerial+G.day)%employed.length],h=G.households[p.hh],f=G.firms[p.job];
 const home=readBuild(h.home),work=readBuild(f.building);if(!home||!work||f.closed)return null;
 const returning=vehicleSerial%2===1;const v=beginVehicle(returning?work:home,returning?home:work);if(v){setPurposeStyle(v,(p.id%3===0)?'pedestrian':'car');v.person=p.id;v.reason=p.name+(returning?' returning home':' commuting to '+f.name);}return v;
}
function detour(v){
 const start=v.path[v.segment],goal=fromEnd(v.path),net=graph();
 const queue=[start],parent=new Map([[start,-1]]),busy=new Set(traffic.filter(c=>c!==v&&c.wait>2).map(c=>c.path[c.segment]+'>'+c.path[c.segment+1]));
 for(let i=0;i<queue.length&&i<3200;i++){const at=queue[i];if(at===goal)break;for(const n of net.neighbors.get(at)||[]){if(parent.has(n)||busy.has(at+'>'+n))continue;parent.set(n,at);queue.push(n);}}
 if(!parent.has(goal))return false;
 const path=[];for(let at=goal;at!==-1;at=parent.get(at))path.push(at);path.reverse();
 if(path.length<2||path[1]===v.path[v.segment+1])return false;
 // Replanning happens only at a tile center, preserving continuous position.
 if(v.fraction>.001)return false;
 v.path=path;v.segment=0;v.wait=0;v.rerouted=(v.rerouted||0)+1;return true;
}

// SOURCE: 68-living-art.js
// Original illustrated-diorama layer. Static material detail is cached; live
// activity has a strict viewport budget and follows staffed, productive sites.
function livingTerrain(g,x,y,type,h){
 if(!gameOptions.decor||gameOptions.quality==='low'||fastRenderEnabled())return;
 const p=iso(x,y);
 if(type===2){
  // Each shore follows an actual land/water boundary in the isometric grid.
  const edges=[[-1,0,[-36,18],[0,0]],[0,-1,[0,0],[36,18]],[1,0,[36,18],[0,36]],[0,1,[0,36],[-36,18]]];
  for(const [dx,dy,a,b] of edges){const xx=x+dx,yy=y+dy;if(xx<0||yy<0||xx>=T||yy>=T||G.tiles[roadId(xx,yy)]===2)continue;
   const from=[p[0]+a[0],p[1]+a[1]],to=[p[0]+b[0],p[1]+b[1]];
   segment(g,from,to,'#b6b895',5);segment(g,from,to,'#d2c6a3',2);
   for(let j=1;j<5;j++){const t=j/5,px=from[0]+(to[0]-from[0])*t,py=from[1]+(to[1]-from[1])*t;g.fillStyle=j%2?'#7e9670':'#a9ac84';g.fillRect(px-2,py-1,4,2);if((h+j)%3===0){segment(g,[px,py],[px-2,py-8],'#537c55');segment(g,[px+2,py],[px+3,py-6],'#7b955c');}}
  }
  if(h%3===0){segment(g,[p[0]-15,p[1]+20],[p[0]+8,p[1]+9],'#9fc0b0',1);segment(g,[p[0]-8,p[1]+25],[p[0]+17,p[1]+13],'#699f9f',1);}
 }else if(type===0&&!G.landUse?.[roadId(x,y)]&&h%5===0){
  // Soft patches avoid a uniform lawn while preserving parcel and road edges.
  polygon(g,[[p[0]-17,p[1]+14],[p[0]-2,p[1]+8],[p[0]+16,p[1]+18],[p[0]+2,p[1]+26]],h%2?'#7c945631':'#b8ba7130');
  for(let j=0;j<4;j++){const px=p[0]-9+j*6,py=p[1]+17+(j%2)*3;segment(g,[px,py],[px+1,py-4],'#718747',1);}
 }
}
function parcelDetails(g,b,w,d){
 if(!gameOptions.decor||gameOptions.quality==='low'||b.kind==='worksite'||b.redevelopment)return;
 const f=G.firms[b.firm],shop=f&&['grocer','bakery','tavern','office'].includes(b.kind),front=point(0,d*.38,0);
 if(shop){
  const color=b.kind==='grocer'?'#5e8462':b.kind==='bakery'?'#b87552':b.kind==='tavern'?'#597c83':'#8b7658';
  const left=point(-w*.24,d*.37,18),right=point(w*.24,d*.37,18);
  polygon(g,[left,right,[right[0],right[1]+6],[left[0],left[1]+6]],color);
  for(let j=0;j<5;j++){const t=(j+.5)/5,px=left[0]+(right[0]-left[0])*t,py=left[1]+(right[1]-left[1])*t;segment(g,[px,py],[px,py+5],'#ecdbb5',2);}
  g.fillStyle='#d3bd8f';g.fillRect(front[0]-4,front[1]-4,8,3);g.fillStyle='#637953';g.fillRect(front[0]-3,front[1]-6,6,3);
 }
 if(f&&!f.closed&&['warehouse','factory','mill','sawmill','contractor'].includes(b.kind)){
  for(let j=0;j<3;j++){const q=point(w*.31-j*.11,d*.30,0);box(g,w*.29-j*.11,d*.30,.09,.10,0,5+j%2*3,j%2?'#ae9063':'#c2a579');segment(g,[q[0]-2,q[1]-4],[q[0]+2,q[1]-2],'#796c50');}
 }
}
function paintTownLight(g){
 if(!gameOptions.effects||nightMode)return;
 // One screen-sized wash: warm sun and cool distance, never per-tile animation.
 const wash=g.createLinearGradient(0,0,cw,ch);wash.addColorStop(0,'#ffe7a516');wash.addColorStop(.5,'#e5edc000');wash.addColorStop(1,'#355d7020');
 g.setTransform(dpr,0,0,dpr,0,0);g.fillStyle=wash;g.fillRect(0,0,cw,ch);transform();
}
function buildingActivity(items){
 const actors=[];
 if(!gameOptions.effects||gameOptions.reducedMotion)return actors;
 const cap=fastRenderEnabled()?5:gameOptions.quality==='high'?20:12;let count=0;
 for(const item of items){const b=item.b,f=b&&G.firms[b.firm];if(!f||f.closed||!workingStaff(f).length||!(f.production>0||f.revenue>0)||++count>cap)continue;
  const id=f.workers[0],phase=(frameClock*.14+b.id*.173)%1,t=phase<.5?phase*2:(1-phase)*2;
  const door=point(0,item.d*.38,0),road=graph().portals.get(b.id);if(road==null)continue;const target=roadCenter(road),x=item.x+door[0],y=item.y+door[1];
  // A short staff errand remains between the frontage and its connected sidewalk.
  const q={x:x+(target[0]-x)*t*.55,y:y+(target[1]-y)*t*.55,dx:target[0]-x,dy:target[1]-y};
  actors.push({kind:'vehicle',v:{id,style:'pedestrian',color:['#876c51','#536f6e','#8e755b','#687b55'][b.id%4]},...q});
 }
 return actors;
}
function paintCastShadows(g,items){
 if(!gameOptions.effects||nightMode)return;
 for(const item of items){
  if(item.kind==='tree'){g.fillStyle='#344f4326';g.beginPath();g.ellipse(item.x+15,item.y+5,17,6,.25,0,Math.PI*2);g.fill();continue;}
  if(!item.b)continue;
  const height=item.b.kind==='tower'?95:item.b.kind==='apartment'?65:['home','worksite'].includes(item.b.kind)?30:48,dx=height*.72,dy=height*.25,x=item.x,y=item.y,w=item.w,d=item.d;
  const foot=[[x-17*w,y+3*d],[x+18*w,y+13*d],[x+18*w+dx,y+13*d+dy],[x-17*w+dx,y+3*d+dy]];
  polygon(g,foot,'#304b4530');
  polygon(g,[[x-14*w,y+4*d],[x+14*w,y+11*d],[x+14*w+dx*.7,y+11*d+dy*.7],[x-14*w+dx*.7,y+4*d+dy*.7]],'#304b4514');
 }
}

// SOURCE: 69-civic-materials.js
// Stable visual states follow property condition, occupation and funded capex.
function propertyAppearance(b){
 const f=G.firms[b.firm],empty=b.kind==='home'&&!G.households[b.hh]?.people.some(id=>!G.people[id]?.deceased&&!G.people[id]?.movedAway);
 return {condition:b.condition<45?'distressed':b.condition<75?'weathered':'maintained',status:f?(f.closed?'closed':'trading'):empty?'vacant':'occupied',invested:!!f&&f.scale>=1.4};
}
function appearanceKey(b){const a=propertyAppearance(b);return a.condition+':'+a.status+':'+a.invested;}
function architecturalIdentity(g,b,w,d){
 if(!gameOptions.decor||gameOptions.quality==='low'||b.kind==='worksite'||b.redevelopment)return;
 const a=propertyAppearance(b),u=-w*.365,v=d*.35,H=b.kind==='tower'?132:b.kind==='apartment'?48:b.kind==='office'?60:['home','farm','forestry','quarry'].includes(b.kind)?0:30;
 const civic=['school','college','townhall','courthouse','bank','clinic'].includes(b.kind),shop=['grocer','bakery','tavern'].includes(b.kind),industrial=['factory','warehouse','sawmill','mill'].includes(b.kind);
 if(civic){
  for(const z of [3,17,30]){slab(g,u-.025,v-.015,w*.78,.055,z,'#d7ceb0');segment(g,point(u,v+.05,z-1),point(u+w*.76,v+.05,z-1),'#8d8d78');}
  // Alternating dressed corner stones and a broad civic entrance stair.
  for(let z=2;z<30;z+=5)box(g,u-.01,v,.07,.05,z,3,'#d9d1b5');
  for(let j=0;j<3;j++)slab(g,-.15-j*.025,v+.05+j*.055,.30+j*.05,.06,3-j,'#c6bda1');
 }
 if(shop){
  // Glazed shopfront and timber-framed display, distinct from civic windows.
  box(g,u+.05,v+.015,w*.21,.025,3,9,a.status==='closed'?'#827e6b':'#6f9690');
  box(g,u+w*.50,v+.015,w*.20,.025,3,9,a.status==='closed'?'#827e6b':'#739e9a');
  for(const x of [u+.05,u+w*.26,u+w*.50,u+w*.70])segment(g,point(x,v+.045,2),point(x,v+.045,13),'#d6c39a',1);
  if(b.kind==='bakery'){const q=point(u+.12,v+.06,7);g.fillStyle='#e4c788';for(let j=0;j<3;j++)g.fillRect(q[0]+j*3,q[1]+j,3,2);}
 }
 if(industrial){
  // Clerestory glazing and riveted cladding retain the warehouse silhouette.
  for(let j=0;j<6;j++){const x=u+.04+j*w*.105;segment(g,point(x,v+.02,1),point(x,v+.02,27),'#8d8d7a');}
  for(let j=0;j<3;j++){const q=point(u+.08+j*w*.20,-d*.05,36);polygon(g,[[q[0]-5,q[1]],[q[0]+3,q[1]-4],[q[0]+9,q[1]-1],[q[0]+1,q[1]+3]],a.status==='closed'?'#78837b':'#8fbbb1');}
 }
 if(b.kind==='home'){
  const q=point(-w*.30,d*.36,0);
  // Three parcel treatments: stone-edged beds, paved courts, kitchen plots.
  if(b.id%3===0){for(let j=0;j<5;j++){const t=point(-.34+j*.13,.39,1);g.fillStyle='#b6b79b';g.fillRect(t[0]-2,t[1]-1,4,2);}}
  else if(b.id%3===1){for(let j=0;j<4;j++)slab(g,-.34+j*.11,.36,.075,.08,1,'#c9bd9a');}
  else {for(let j=0;j<3;j++)slab(g,-.37,.17+j*.08,.25,.035,1,j%2?'#89915b':'#aa9364');}
  if(a.status==='vacant'){segment(g,[q[0],q[1]-5],[q[0],q[1]-15],'#6c7157');g.fillStyle='#d6c49e';g.fillRect(q[0]-5,q[1]-15,11,5);}
 }
 if(a.invested&&industrial){box(g,.12,-.12,.20,.20,37,8,'#81998d');slab(g,.10,-.14,.24,.24,46,'#acb9a4');segment(g,point(.21,-.02,37),point(.21,-.02,28),'#687c72',2);}
 if(a.condition!=='maintained'&&H){for(let j=0;j<3;j++){const q=point(u+.08+j*w*.2,v+.05,8+j*5);segment(g,q,[q[0]+2,q[1]+6],'#737a6755');segment(g,[q[0]+2,q[1]+6],[q[0]-1,q[1]+9],'#737a6755');}}
 if(a.status==='closed'&&H){const q=point(0,v+.07,7);g.fillStyle='#a48f6a';g.fillRect(q[0]-6,q[1]-2,12,5);segment(g,[q[0]-5,q[1]-1],[q[0]+5,q[1]+2],'#736d55');}
}

// SOURCE: 70-interaction.js
const pointer={down:false,startX:0,startY:0,px:0,py:0,moved:false,pinch:0,buildTrail:0,hover:null};
function toWorld(x,y){const wx=(x-cw/2)/cam.zoom+cam.x,wy=(y-ch/2)/cam.zoom+cam.y;
 let r=(wx-RW/2)/(TW/2),s=(wy-32-TH/2)/(TH/2);return [Math.floor((s+r)/2+.5),Math.floor((s-r)/2+.5)]}
function onTap(sx,sy){if(!G)return;const r=cv.getBoundingClientRect();const [x,y]=toWorld(sx-r.left,sy-r.top);if(!buildMode&&overlay==='charter'&&charterSurveyTap(sx-r.left,sy-r.top,x,y))return;if(x<0||x>=T||y<0||y>=T)return;
 if(buildMode){construct(buildMode,x,y);return}
 const mx=(sx-r.left-cw/2)/cam.zoom+cam.x,my=(sy-r.top-ch/2)/cam.zoom+cam.y;
 if(inspectWaterTripAt(mx,my)||inspectTripAt(mx,my))return;
 let b=buildingAt(x,y);if(!b){const hit=G.buildings.filter(v=>{const pos=iso(v.x,v.y);return Math.abs(mx-pos[0])<20&&my>=pos[1]-38&&my<=pos[1]+33}).sort((a,b)=>iso(b.x,b.y)[1]-iso(a.x,a.y)[1]);b=hit[0]}
 if(b){selected={id:b.id};openPanel('inspect')}else if(!charterOwns(x,y)&&parcelForTile(x,y)){parcelFocus=parcelForTile(x,y).id;openPanel('construction');revealCharterOffice();document.querySelector('[data-parcel-card="'+parcelFocus+'"]')?.scrollIntoView({block:'start'});}else{selected=null;toast('Unoccupied land. Private investors assess access, demand and expected returns.')}
 dirty=true;
}
cv.addEventListener('pointerdown',e=>{if(pointer.down){pointer.moved=true;return;}pointer.activeId=e.pointerId;roadPainted.clear();pointer.lastRoad=buildMode==='road'?toWorld(e.clientX-cv.getBoundingClientRect().left,e.clientY-cv.getBoundingClientRect().top):null;pointer.down=true;pointer.startX=pointer.px=e.clientX;pointer.startY=pointer.py=e.clientY;pointer.moved=false;try{cv.setPointerCapture(e.pointerId)}catch(err){} });
cv.addEventListener('pointermove',e=>{if(!pointer.down){if(buildMode){const r=cv.getBoundingClientRect(),p=toWorld(e.clientX-r.left,e.clientY-r.top);pointer.hover={x:p[0],y:p[1]};dirty=true;}return;}if(pointer.activeId!==e.pointerId||touches.size>1)return;let dx=e.clientX-pointer.px,dy=e.clientY-pointer.py;if(Math.abs(e.clientX-pointer.startX)>7||Math.abs(e.clientY-pointer.startY)>7)pointer.moved=true;
 if(buildMode==='road'){let br=cv.getBoundingClientRect(),pt=toWorld(e.clientX-br.left,e.clientY-br.top);let prev=pointer.lastRoad||pt;let dxg=pt[0]-prev[0],dyg=pt[1]-prev[1],steps=Math.max(Math.abs(dxg),Math.abs(dyg),1);for(let k=0;k<=steps;k++){let ax=Math.round(prev[0]+dxg*k/steps),ay=Math.round(prev[1]+dyg*k/steps),key=ax+'/'+ay;if(!roadPainted.has(key)){roadPainted.add(key);construct('road',ax,ay,true)}}pointer.lastRoad=pt}else{cam.x-=dx/cam.zoom;cam.y-=dy/cam.zoom;cam.x=clamp(cam.x,0,RW);cam.y=clamp(cam.y,0,RH)}pointer.px=e.clientX;pointer.py=e.clientY;let rect=cv.getBoundingClientRect(),tile=toWorld(e.clientX-rect.left,e.clientY-rect.top);pointer.hover={x:tile[0],y:tile[1]};dirty=true});
cv.addEventListener('pointerup',e=>{$('gameRoot').classList.add('map-used');if(pointer.activeId!==e.pointerId)return;if(pointer.down&&!pointer.moved)onTap(e.clientX,e.clientY);flushRoadBatch();pointer.down=false;pointer.activeId=null;pointer.lastRoad=null;roadPainted.clear()});
window.addEventListener('keydown',e=>{
 if(e.key!=='Escape')return;
 if(pendingEvent||$('helpDialog').style.display!=='none'){if(window.__townArchive?.back?.())e.preventDefault();return;}
 if(active){if(window.__townArchive?.back?.())e.preventDefault();return;}
 if(buildMode){closeBuildTool();e.preventDefault();return;}
 // Match Android Back: dismiss the top navigation layer rather than leaving
 // keyboard users stranded behind an open drawer or transient help/archive form.
 if(window.__townArchive?.back?.())e.preventDefault();
});cv.addEventListener('pointercancel',()=>{flushRoadBatch();pointer.down=false;pointer.activeId=null;pointer.lastRoad=null;roadPainted.clear()});cv.addEventListener('pointerleave',()=>{pointer.hover=null;dirty=true});
cv.addEventListener('wheel',e=>{e.preventDefault();cam.zoom=clamp(cam.zoom*(e.deltaY<0?1.12:.89),.025,1.7);dirty=true},{passive:false});
let touches=new Map();cv.addEventListener('touchstart',e=>{touches=new Map([...e.touches].map(t=>[t.identifier,{x:t.clientX,y:t.clientY}]));if(touches.size===2){pointer.moved=true;const a=[...touches.values()];pointer.pinch=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y)}},{passive:true});
cv.addEventListener('touchmove',e=>{touches=new Map([...e.touches].map(t=>[t.identifier,{x:t.clientX,y:t.clientY}]));if(touches.size===2){const a=[...touches.values()],d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);if(pointer.pinch>0){cam.zoom=clamp(cam.zoom*d/pointer.pinch,.025,1.7);dirty=true}pointer.pinch=d}},{passive:true});
cv.addEventListener('touchend',e=>{touches=new Map([...e.touches].map(t=>[t.identifier,{x:t.clientX,y:t.clientY}]));pointer.pinch=0});
cv.addEventListener('touchcancel',()=>{touches.clear();pointer.pinch=0;pointer.down=false;pointer.activeId=null;pointer.lastRoad=null;roadPainted.clear();flushRoadBatch();});
function closeBuildTool(){flushRoadBatch();buildMode='';pointer.hover=null;pointer.down=false;pointer.activeId=null;pointer.lastRoad=null;roadPainted.clear();dirty=true;$('placementHint').style.display='none';$('hint').textContent='DRAG TO PAN · TAP TO INSPECT';toast('Construction tool closed');}
function construct(kind,x,y,quiet=false){
 if(kind!=='inspect'&&!charterOwns(x,y)){if(!quiet)toast('Regional land: purchase the district in Public Works before developing it.');return;}
 if(kind==='inspect'){buildMode='';const target=buildingAt(x,y);if(target){selected={id:target.id};openPanel('inspect')}else toast('No building is present at this lot.');dirty=true;return}
 if(kind==='repair'){if(x<0||x>=T||y<0||y>=T||cityCell(x,y)!==1){if(!quiet)toast('Select an existing road tile to resurface.');return}ensureRoadWear();if(G.roadWear[roadId(x,y)]>96){if(!quiet)toast('This street is already in excellent condition.');return}if(G.treasury<buildCost.repair){if(!quiet)toast('Insufficient town funds.');return}G.treasury-=buildCost.repair;G.region+=buildCost.repair;G.roadWear[roadId(x,y)]=100;G.construction++;staticDirty=true;dirty=true;updateHeader();if(!quiet)toast('Street resurfaced.');return}
 if(kind==='road'){
   if(x<0||x>=T||y<0||y>=T)return;
   if(![0,3].includes(cityCell(x,y))||G.landUse?.[roadId(x,y)]||buildingAt(x,y)){if(!quiet)toast('Road requires vacant, unreserved land.');return}
   if(G.treasury<buildCost.road){if(!quiet)toast('Insufficient town funds for this road.');return}
   G.treasury-=buildCost.road;G.region+=buildCost.road;G.tiles[y*T+x]=1;ensureRoadWear();G.roadWear[roadId(x,y)]=100;G.construction++;dirty=true;
   if(quiet){roadBatchDirty=true;return;}invalidateRoads();staticDirty=true;recompute();updateHeader();save();return;
 }
 if(!canPlace(x,y,true,kind)){toast(['fishery','wharf'].includes(kind)?waterfrontSitingReason(x,y,kind):'This project requires a fully vacant footprint with road access.');return}
 if(kind==='forestry'&&!Array.from({length:25},(_,i)=>[x+(i%5)-2,y+Math.floor(i/5)-2]).some(([a,b])=>cityCell(a,b)===3)){toast('Forestry operations require nearby woodland.');return}
 const cost=buildCost[kind];if(G.treasury<cost){toast('Town treasury cannot afford '+types[kind].n+' ('+money(cost)+').');return}
 G.treasury-=cost;G.region+=cost;
 if(['grocer','bakery','mill','farm','forestry','sawmill','quarry','contractor','tavern','fishery','wharf','factory','warehouse','office','college'].includes(kind)){
   if(G.region<15000){toast('Regional investment capital is exhausted.');G.treasury+=cost;G.region-=cost;return}
   G.region-=12000+G.policy.permitFee;const newFirm=createFirm(kind,x,y);newFirm.cash=12000;transferTreasury(G.policy.permitFee,'permits');assignJobs();story('New local enterprise: '+types[kind].n+' opens on a developed lot.','good');
 }else if(kind==='home'){
   const b={id:G.nextId++,kind,x,y,value:48000,condition:100,owner:-1,firm:-1,hh:-1};G.buildings.push(b);let family={id:G.households.length,name:pick(surnames),cash:rn(900,3000),home:b.id,owner:-1,people:[],income:0,rent:0,food:0,tax:0,aid:0,crimeLoss:0,stress:25,security:85,last:[],worklessness:0};
   G.households.push(family);G.region-=family.cash;G.homes.push(b.id);b.hh=family.id;b.owner=family.id;
   for(let n=0;n<2;n++){let p={id:G.people.length,name:pick(first)+' '+family.name,age:Math.round(rn(19,60)),skill:rn(.3,1),health:rn(65,100),hh:family.id,job:-1,life:65,last:[]};G.people.push(p);family.people.push(p.id)}
   assignJobs();story('A new household settled in the village.','good',b.id,family.id);
 }else G.buildings.push({id:G.nextId++,kind,x,y,value:cost*10,condition:100,owner:-1,firm:-1,hh:-1,footprint:footprintFor(x,y,kind)});
 G.construction++;invalidateRoads();recompute();updateHeader();staticDirty=true;dirty=true;save();toast(types[kind].n+' constructed.');if(active==='construction')renderPanel('construction');
}
function stat(label,value,cls=''){return `<div class="stat"><small>${esc(label)}</small><b class="${cls}">${esc(value)}</b></div>`}
function line(label,value,cls=''){return `<div class="line"><span>${esc(label)}</span><span class="${cls}">${esc(value)}</span></div>`}
function head(s){return `<div class="section">${esc(s)}</div>`}
function chart(field,bad=false){const ar=G.history.slice(-65);if(!ar.length)return '';let vals=ar.map(x=>x[field]),mn=Math.min(...vals),mx=Math.max(...vals),range=Math.max(1,mx-mn);return `<div class="history">${ar.map(x=>`<i class="${bad?'bad':''}" style="height:${Math.max(4,10+90*(x[field]-mn)/range)}%" title="Day ${x.day}: ${fmt(x[field])}"></i>`).join('')}</div><div class="desc">Observations, last ${ar.length} days · range ${fmt(mn)}–${fmt(mx)}.</div>`}
function renderOverview(){const s=G.stats;
 return head('This morning in town')+`<div class="statgrid">${stat('Population',fmt(s.population))}${stat('Employment',s.employment+'%')}${stat('Business doors open',s.businesses+' / '+G.firms.length)}${stat('Households in hardship',s.hardship+'%',s.hardship>30?'negative':'')}</div>`+
 head('Public ledger')+line('Municipal cash',money(G.treasury))+line('Debt',money(G.debt))+line('Outstanding household savings',money(s.cash))+line('Private business capital',money(s.businessCash))+
 head('A village of consequences')+`<p class="desc">Tax and wage decisions affect real household balances. Goods move among farms, mills, bakeries and grocers. Businesses can close, police respond to crime, and the town can face fires. Select any property on the map to inspect its inhabitants or finances.</p>`+
 chart('employment')+head('Latest entries')+G.events.slice(0,8).map(eventHtml).join('');
}
function eventHtml(e){return `<div class="event"><strong>Day ${e.day}</strong> · ${esc(e.text)} ${e.bid>0?`<button class="small" data-inspect="${e.bid}">View</button>`:''}</div>`}
function renderCommunity(){const s=G.stats;
 return head('Community condition')+`<div class="statgrid">${stat('Safety index',s.safety+'/100')}${stat('Crime / last 30 days',fmt(s.dailyCrime))}${stat('Emergency readiness',s.preparedness+'%')}${stat('Households in hardship',s.hardship+'%')}</div>`+
 `<p class="desc">Funding and stations affect response capacity. Hardship, job loss and isolation affect risks. Theft removes real money from victims and transfers it to another local household; incidents are attached to locations.</p>`+
 head('Community expenditure')+line('Policing / day',money(G.policy.policeBudget))+line('Fire & defence / day',money(G.policy.defenseBudget))+line('Housing assistance / day',money(G.policy.aidBudget))+line('Outreach / day',money(G.policy.outreachBudget))+
 head('Local incident register')+(G.cases.length?G.cases.slice(0,15).map(eventHtml).join(''):'<p class="desc">No criminal incidents recorded yet.</p>')+
 head('Safety trend')+chart('safety');
}
function slider(d){let [k,name,lo,hi,step,unit,help]=d,v=G.policy[k];return `<div class="range"><label><b>${esc(name)}</b><span id="show-${k}">${unit==='$'?'$'+fmt(v):fmt(v)+unit}</span></label><input aria-label="${esc(name)}" type="range" min="${lo}" max="${hi}" step="${step}" value="${v}" data-policy="${k}"><div class="desc">${esc(help)}</div></div>`}
function renderPolicies(){return head('A government economics experiment')+`<p class="desc">Move a policy control to enact it immediately. Entries are logged with baseline employment, safety, hardship, cash and business counts. Comparisons are observations, not proof of causation.</p>`+
 defs.map(slider).join('')+head('Trade & exchange')+
 `<div class="line"><span>Allow regional imports</span><button id="tradeToggle" class="small ${G.policy.imports?'on':''}">${G.policy.imports?'ALLOWED':'RESTRICTED'}</button></div><p class="desc">A closed border can interrupt the village supply chain. Tariffs transfer money to the treasury but increase import costs.</p>`;
}
function renderTreasury(){let c=G.cumulative,p=G.policy;
 return head('Municipal accounts')+`<div class="statgrid">${stat('Cash on hand',money(G.treasury),G.treasury<5000?'negative':'')}${stat('Municipal borrowing',money(G.debt))}${stat('Income taxes collected',money(c.incomeTax))}${stat('Business profit taxes',money(c.profitTax))}</div>`+
 head('Receipts since founding')+line('Income tax',money(c.incomeTax))+line('Profit tax',money(c.profitTax))+line('Land and property',money(c.propertyTax))+line('Food sales tax',money(c.foodTax))+line('Business permits',money(c.permits))+line('Import tariffs',money(c.tariffs))+
 head('Expenditure since founding')+line('Public services and subsidies',money(c.spending))+line('Direct housing aid',money(c.welfare))+line('Unpaid principal',money(G.debt))+
 `<div class="btnrow"><button id="borrow">Borrow $5,000</button><button id="repay">Repay $5,000</button></div><p class="desc">Borrowing increases both cash and outstanding debt. Interest accrues each month and is paid to the regional lender. Unfunded public budgets reduce service capacity.</p>`+
 head('Treasury history')+chart('treasury');
}
function renderCitizens(){return head('Village families')+`<p class="desc">Select a household to inspect each resident's name, age, job, savings, food expenses, taxes and hardship.</p>`+
 G.households.filter(h=>h.people.length>0).map(h=>{let b=readBuild(h.home),people=h.people.map(id=>G.people[id]).filter(p=>p&&!p.deceased&&p.movedAway!==true),workers=people.filter(p=>(p.job>=0&&!p.commuteBlocked)||p.publicWork).length;return `<div class="entry" data-house="${h.id}"><strong>The ${esc(h.name)} household</strong><br><small>${people.length} people · ${workers} employed · Savings ${money(h.cash)} · Stress ${Math.round(h.stress)}/100 · Lot ${b?`${b.x},${b.y}`:'?'}</small></div>`}).join('');
}
function renderBusinesses(){let total=G.firms.filter(f=>!f.closed).length;
 return head('Private enterprises')+`<p class="desc">${total} businesses operate. Wages, input prices, permit fees, sales taxes, production and crime influence their balances. Tap one to inspect.</p>`+
 G.firms.map(f=>`<div class="entry" data-firm="${f.id}"><strong>${esc(f.name)}</strong> <span class="pill">${f.closed?'CLOSED':'OPEN'}</span><br><small>${esc(types[f.kind].n)} · ${f.workers.length}/${f.jobs} staff · ${money(f.cash)} cash · Last profit ${money(f.profit)}</small></div>`).join('');
}
function renderConstruction(){return head('Village planning and private development')+
 '<p class="desc">Choose a building type, then tap a clear roadside plot on the map. Road tiles can be extended over open land. Costs are paid from town funds and recorded as construction purchases. Private enterprises also require regional investment capital.</p>'+
 `<div class="btnrow"><button data-build="" class="${buildMode===''?'on':''}">Inspect</button>${Object.entries(buildCost).map(([key,cost])=>`<button data-build="${key}" class="${buildMode===key?'on':''}">${buildIcons[key]} ${esc(types[key]?types[key].n:'Road')} · ${money(cost)}</button>`).join('')}</div>`+
 head('Physical services')+line('Police stations',G.buildings.filter(b=>b.kind==='police').length)+line('Fire brigades',G.buildings.filter(b=>b.kind==='fire').length)+line('Houses',G.homes.length)+line('Developed lots',G.buildings.length);
}
function renderJournal(){const j=G.journal;
 return head('The policy journal')+`<p class="desc">Every change captures the village's state when enacted. The differences below compare the current village with that baseline. They may reflect other events, time and policy changes.</p>`+
 j.slice().reverse().map(p=>{
 const base=p.baseline||{};const diff=(key,suff='',sign=false)=>{let d=(key==='treasury'?G.treasury:G.stats[key])-(base[key]||0);return (d>=0?'+':'')+fmt(d)+suff};
 return `<div class="entry"><strong>Day ${p.day}: ${esc(p.name)}</strong><p class="desc">${esc(p.message||'')}</p><div class="compact">Since change: employment ${diff('employment',' pts')} · hardship ${diff('hardship',' pts')} · safety ${diff('safety',' pts')} · businesses ${diff('businesses')} · treasury ${diff('treasury')}</div></div>`}).join('');
}
function renderSettings(){return head('Local save and diagnostics')+
 line('App version',RELEASE.version+' · Android adaptation')+line('Engine','Hardware-accelerated WebView Canvas 2D')+line('Residents',G.people.length)+line('Active businesses',G.stats.businesses)+line('Rendered scenery','Retained offscreen map image')+line('Autosave schedule',gameOptions.autoSave+' seconds, pause and app exit')+
 '<p class="desc">This is an offline Android adaptation, not a port of the original Godot/C++ project. Save data resides locally in app storage.</p><div class="btnrow"><button id="saveNow">Save game</button><button id="restart" class="red">Start a new village</button></div>'+
 head('Model limitations')+'<p class="desc">This is an illustrative agent-based economy. Policy outcomes use explicit behavioural rules, not statistically estimated causal effects. A single simulated town cannot establish what real-world policy will do.</p>';
}
function renderInspect(){const b=selected&&readBuild(selected.id);if(!b)return '<p>No property selected.</p>';const loc=`Lot ${b.x}, ${b.y}`;
 let html=head(types[b.kind].n+' · '+loc)+`<div class="statgrid">${stat('Estimated property value',money(b.value))}${stat('Condition',fmt(b.condition)+'/100')}</div>`;
 if(b.kind==='home'){
   const h=G.households[b.hh];if(!h)return html;
   html+=head('The '+h.name+' household')+`<div class="statgrid">${stat('Liquid savings',money(h.cash),h.cash<150?'negative':'')}${stat('Stress',fmt(h.stress)+'/100',h.stress>60?'negative':'')}${stat('Food yesterday',money(h.food))}${stat('Income yesterday',money(h.income))}</div>`+
   line('Rent yesterday',money(h.rent))+line('Income taxes yesterday',money(h.incomeTax??h.tax))+line('Housing assistance yesterday',money(h.aid))+line('Lifetime theft losses',money(h.crimeLoss))+line('Perceived security',fmt(h.security)+'/100')+
   head('People living here')+h.people.map(id=>{const p=G.people[id];if(!p)return '';const f=G.firms[p.job];return `<div class="entry"><strong>${esc(p.name)}</strong><br><small>Age ${p.age} · ${f?esc(f.name):'Not employed'} · Health ${Math.round(p.health)}/100</small></div>`}).join('');
 }else if(b.firm>=0){const f=G.firms[b.firm];if(f){html+=head(f.name)+`<div class="statgrid">${stat('Enterprise cash',money(f.cash))}${stat('Workers',f.workers.length+'/'+f.jobs)}${stat('Revenue yesterday',money(f.revenue))}${stat('Net profit yesterday',money(f.profit),f.profit<0?'negative':'')}</div>`+
 line('Minimum payable wage',money(workerIncome(f))+'/day')+line('Cash stolen since opening',money(f.theft))+line('Business taxes yesterday',money(f.tax))+
 head('Warehouse')+Object.keys(goods).map(k=>line(k,fmt(f.stock[k]||0))).join('')+
 head('Employees')+f.workers.slice(0,20).map(id=>{const p=G.people[id];return p?`<div class="line"><span>${esc(p.name)}</span><span>${esc(G.households[p.hh]?.name||'')}</span></div>`:''}).join('');
 }}else html+='<p class="desc">Public facility. Its physical presence improves village services only when the municipality funds the corresponding budget.</p>';
 html+=`<p class="desc">Ownership and all financial amounts are modelled local accounts, not decorative scores.</p>`;return html;
}
let panelOpener=null;
function openPanel(tab,opener=null){panelOpener=opener||document.activeElement;active=tab;$('gameRoot').classList.add('drawer-open');$('panel').classList.add('show');$('panelBody').scrollTop=0;$('tabs').querySelectorAll('button').forEach(b=>b.classList.toggle('active',b.dataset.panel===tab));renderPanel(tab)}
function closePanel(){const previous=active;active='';$('gameRoot').classList.remove('drawer-open');$('panel').classList.remove('show');$('tabs').querySelectorAll('button').forEach(b=>b.classList.remove('active'));const returnTarget=panelOpener?.isConnected&&panelOpener!==document.body&&panelOpener.getClientRects().length?panelOpener:$('tabs').querySelector(`button[data-panel="${previous}"]`);if(returnTarget)returnTarget.focus();panelOpener=null}
function economySnapshot(){
 const demand=cityDemand(),activeFirms=G.firms.filter(f=>!f.closed),families=G.households.filter(h=>h.people.some(id=>G.people[id]&&!G.people[id].deceased&&!G.people[id].movedAway));
 const byType={},kindSections={farm:'Agriculture',fishery:'Agriculture',wharf:'Logistics',forestry:'Resource extraction',quarry:'Resource extraction',mill:'Manufacturing',sawmill:'Manufacturing',factory:'Manufacturing',bakery:'Food & retail',grocer:'Food & retail',tavern:'Food & retail',warehouse:'Logistics',contractor:'Construction',office:'Services',college:'Services'};
 for(const f of G.firms){const sector=kindSections[f.kind]||'Other services',entry=byType[sector]||(byType[sector]={sector,open:0,closed:0,workers:0,jobs:0,profit:0,sales:0,capital:0,atRisk:0});
  if(f.closed)entry.closed++;else {entry.open++;entry.workers+=f.workers.length;entry.jobs+=f.jobs;entry.profit+=f.profit||0;entry.sales+=f.revenue||0;entry.capital+=f.cash||0;if(f.profit<0&&f.cash<Math.max(2500,f.wage*f.jobs*12))entry.atRisk++;}
 }
 const values=families.map(h=>h.cash/Math.max(1,h.people.length)).sort((a,b)=>a-b),median=values.length?values[Math.floor(values.length/2)]:0;
 const banks=G.banks.filter(b=>!b.closed),deposits=banks.reduce((sum,b)=>sum+bankDeposits(b.id),0),reserves=banks.reduce((sum,b)=>sum+b.cash,0),loans=G.loans.filter(l=>l.status==='active').reduce((sum,l)=>sum+l.balance,0);
 const marketJobs=activeFirms.reduce((sum,f)=>sum+f.jobs,0),working=activeFirms.reduce((sum,f)=>sum+f.workers.length,0);
 const vacantHomes=G.homes.filter(id=>{const b=readBuild(id);return b&&(!G.households[b.hh]||!G.households[b.hh].people.some(pid=>G.people[pid]&&!G.people[pid].movedAway&&!G.people[pid].deceased))}).length;
 return {demand,sectors:Object.values(byType).filter(x=>x.open||x.closed).sort((a,b)=>b.workers-a.workers),families:families.length,median,open:activeFirms.length,closed:G.firms.length-activeFirms.length,atRisk:activeFirms.filter(f=>f.profit<0&&f.cash<Math.max(2500,f.wage*f.jobs*12)).length,banks:banks.length,deposits,reserves,loans,marketJobs,working,vacantHomes,projects:(G.projects||[]).length};
}
function marketSignal(){const m=economySnapshot(),s=G.stats;let title,description,kind;
 if((G.market?.foodDisconnected||0)>0){title='Groceries out of reach';description=fmt(G.market.foodDisconnected)+' residents lack an operating grocer on their road network. Restore access or develop a reachable shop.';kind='danger';}
 else if((G.market?.unmetFood||0)>G.stats.population*.08){title='Essential food is going unfilled';description='Inspect shop stock, retail staff, delivered prices and household purchasing power.';kind='danger';}
 else if(s.hardship>35){title='Households under pressure';description='High hardship threatens local demand. Consider relief, jobs and essential living costs.';kind='danger';}
 else if(s.employment<65){title='A weak labour market';description='Jobs are scarce. Check business cash flow and the cost of hiring.';kind='danger';}
 else if(m.demand.housingPressure>75){title='Housing market tightening';description='Land values and household crowding favour new homes, if zoning and finance allow.';kind='warn';}
 else if(m.atRisk>=3){title='Firms at risk';description=m.atRisk+' active businesses have losses and thin cash buffers.';kind='warn';}
 else if(G.serviceProvision&&((G.serviceProvision.health?.coverage??1)<.65||(G.serviceProvision.school?.coverage??1)<.60)){title='Care and learning need attention';description='Strong jobs alone do not purchase public services. Compare access, qualified staffing and operating funds in Services.';kind='warn';}
 else if(s.employment>85&&s.hardship<14){title='Strong work and household reserves';description='Employment is high and few households currently show low liquidity or severe stress. Continue monitoring access, services and public commitments.';kind='good';}
 else {title='The economy is adjusting';description='Follow private construction, credit, employment and household purchasing power.';kind='normal';}
 return {title,description,kind,m};
}
function renderEconomy(){let signal=marketSignal(),m=signal.m,d=m.demand,active=G.firms.filter(f=>!f.closed),jobs=active.reduce((s,f)=>s+f.jobs,0),filled=active.reduce((s,f)=>s+f.workers.length,0);
 const cell=(name,value,detail,cls='')=>`<div class="market-cell ${cls}"><small>${esc(name)}</small><strong>${esc(value)}</strong><span>${esc(detail)}</span></div>`;
 return `<div class="market-status ${signal.kind}"><small>LIVE BOROUGH ECONOMY</small><h3>${esc(signal.title)}</h3><p>${esc(signal.description)}</p></div>`+
 `<div class="market-cells">${cell('Employment',G.stats.employment+'%',G.stats.employed+' residents working')}${cell('Median savings',money(m.median),'per household member')}${cell('Housing pressure',d.housingPressure+'/100',m.vacantHomes+' vacant cottages')}${cell('Private work sites',String(m.projects),'projects underway')}${cell('Businesses',String(m.open),m.closed+' historical closures')}${cell('Banks & credit',String(m.banks),money(m.loans)+' loans outstanding')}</div>`+
 head('Where people earn their living')+`<p class="desc">Actual operating enterprises, employees, sales and daily operating profit. A negative profit reflects losses, not an abstract score.</p>`+
 `<table class="market-table"><thead><tr><th>Industry</th><th>Firms</th><th>Jobs</th><th>Daily profit</th></tr></thead><tbody>`+m.sectors.map(x=>`<tr><td>${esc(x.sector)}${x.atRisk?` <small class="risk-mark">${x.atRisk} at risk</small>`:''}</td><td>${x.open}</td><td>${x.workers}/${x.jobs}</td><td class="${x.profit<0?'negative':'positive'}">${money(x.profit)}</td></tr>`).join('')+'</tbody></table>'+
 head('Private investment, not player placement')+meter('Demand for homes',d.homeDemand,d.homeDemand>65?'#e6a37a':'#9dce9c')+meter('Demand for commerce',d.businessDemand,'#adc7a9')+strip('Job openings',d.jobVacancy)+strip('Residential capacity',d.homes+' housing units')+strip('Next private sites',m.projects+' projects in construction')+strip('Regional exports & investment',money(G.region))+
 head('Banks, loans and savings')+strip('Household and company deposits',money(m.deposits))+strip('Cash reserves at local banks',money(m.reserves))+strip('Loans still being repaid',money(m.loans))+strip('Banks in operation',m.banks)+
 head('What should the government do?')+`<div class="council-card"><p class="desc">You do not control private developers, firms or banks. Adjust a few policy rates, funding priorities or municipal borrowing and let the market respond. Watch outcomes over months and years, not just individual days.</p><div class="btnrow"><button id="marketPolicy">Review policy rates</button><button id="marketFamilies">Inspect households</button><button id="marketCompanies">Inspect firms</button></div></div>`+
 head('Employment history')+miniChart('employment')+head('Private enterprise count')+miniChart('businesses')+head('Households under pressure')+miniChart('hardship')+head('Recent economic developments')+headlineList(8);
}
const names={economy:'The Living Economy',banking:'Banks & Credit',overview:'Town Hall',agenda:'Council Agenda',community:'Civic Services',policies:'Economic Policy',treasury:'The Public Purse',citizens:'Our Residents',businesses:'Local Enterprise',construction:'Works & Planning',journal:'Public Record',settings:'Game Options',inspect:'Property Inspector',trip:'Journey Inspector'};
function renderPanel(tab){if(!G)return;const sc=$('panelBody');const y=sc.scrollTop;let contents='';
 try{contents=({overview:renderOverviewFull,economy:renderEconomy,agenda:renderAgenda,community:renderCommunityFull,policies:renderPoliciesFull,treasury:renderTreasuryFull,banking:financePanel,citizens:renderCitizensFull,businesses:renderBusinessesFull,construction:renderConstructionFull,journal:renderJournalFull,settings:renderSettingsFull,inspect:renderInspectFull,trip:renderTripInspector}[tab]||renderOverview)()}
 catch(e){contents='<div class="event">Panel error: '+esc(e.message)+'</div>';console.error(e)}
 $('panelTitle').textContent=names[tab]||'TownLedger';sc.innerHTML=contents;sc.scrollTop=y;
}
function journalPolicy(k,old,nv){const base={...G.stats,treasury:G.treasury};G.journal.push({day:G.day,name:defs.find(d=>d[0]===k)?.[1]||k,message:`Policy revised from ${fmt(old)} to ${fmt(nv)}.`,baseline:base});if(G.journal.length>100)G.journal.shift();story('Council revised '+(defs.find(d=>d[0]===k)?.[1]||k)+'.','neutral')}
$('tabs').addEventListener('click',e=>{const b=e.target.closest('button[data-panel]');if(!b)return;const p=b.dataset.panel;if(p===active)closePanel();else openPanel(p)});
$('panelClose').onclick=closePanel;$('topNotice').onclick=()=>openPanel('journal',$('topNotice'));$('liveEconomy').onclick=()=>openPanel('economy',$('liveEconomy'));
$('panelBody').addEventListener('input',e=>{if(e.target.id==='searchPeople'){citizenQuery=e.target.value;return;}const input=e.target.closest('[data-policy]');if(!input)return;let k=input.dataset.policy,value=+input.value;const d=defs.find(d=>d[0]===k);draftPolicy[k]=value;const el=$('show-'+k);if(el)el.textContent=d[5]==='$'?money(value):policyNumber(value)+d[5];const button=$('enactPolicy');if(button)button.disabled=false;const summ=$('draftSummary');if(summ)summ.textContent=Object.keys(draftPolicy).filter(k=>draftPolicy[k]!==G.policy[k]).map(k=>k==='imports'?'Regional inventory imports: '+(G.policy.imports?'OPEN':'RESTRICTED')+' → '+(draftPolicy.imports?'OPEN':'RESTRICTED'):defs.find(d=>d[0]===k)?.[1]+': '+policyNumber(G.policy[k])+' → '+policyNumber(draftPolicy[k])).join(' · ')});
$('panelBody').addEventListener('change',e=>{if(e.target.id==='searchPeople'){renderPanel('citizens');return;}const input=e.target.closest('[data-policy]');if(!input)return;draftPolicy[input.dataset.policy]=+input.value;const b=$('enactPolicy');if(b)b.disabled=false});
$('panelBody').addEventListener('click',e=>{const b=e.target.closest('button,[data-house],[data-firm],[data-inspect],[data-ambition]');if(!b)return;
 if(b.dataset.build!==undefined){flushRoadBatch();buildMode=b.dataset.build;if(overlay==='charter'){overlay='none';parcelFocus=null;}dirty=true;$('hint').textContent=buildMode?'TAP A CLEAR ROADSIDE PLOT · '+(buildMode==='road'?'DRAG TO PAINT ROADS':'DRAG TO PAN'):'DRAG TO PAN · TAP TO INSPECT';$('placementHint').style.display=buildMode?'block':'none';$('placementHint').textContent=buildMode?'PLACING '+(types[buildMode]?.n||'ROADS').toUpperCase()+' · COST '+money(buildCost[buildMode])+(['fishery','wharf'].includes(buildMode)?' · SHORE + ROAD'+(buildMode==='wharf'?' + RIVER OUTLET':''):''):'';closePanel();toast(buildMode?'Tap the map to build '+(types[buildMode]?.n||'road')+'.':'Inspection mode enabled');return}
 if(b.dataset.house!==undefined){const h=G.households[+b.dataset.house];if(h){const house=readBuild(h.home);if(!house){toast('This household no longer has an address in town.');return}selected={id:h.home};openPanel('inspect');const p=iso(house.x,house.y);cam.x=p[0];cam.y=p[1];dirty=true}return}
 if(b.dataset.firm!==undefined){const f=G.firms[+b.dataset.firm];if(f){const house=readBuild(f.building);if(!house){toast('This company no longer has premises in town.');return}selected={id:f.building};openPanel('inspect');const p=iso(house.x,house.y);cam.x=p[0];cam.y=p[1];dirty=true}return}
 if(b.dataset.inspect!==undefined){selected={id:+b.dataset.inspect};openPanel('inspect');const house=readBuild(selected.id);if(house){const p=iso(house.x,house.y);cam.x=p[0];cam.y=p[1];dirty=true}return}
 if(b.id==='enactPolicy'){enactPolicyPackage();return}
 if(b.id==='resetPolicy'){draftPolicy={};renderPanel('policies');return}
 if(b.dataset.cabinet){const packageRates={
 enterprise:{incomeTax:10,profitTax:7,permitFee:0,zoningRestriction:10,businessRegulation:20},
 housing:{zoningRestriction:0,propertyTax:1,transitBudget:90,permitFee:35},
 services:{incomeTax:19,profitTax:22,healthBudget:190,educationBudget:200,aidBudget:160,roadBudget:140},
 austerity:{incomeTax:14,profitTax:14,healthBudget:75,educationBudget:75,policeBudget:110,defenseBudget:80,aidBudget:55,roadBudget:80}
 };const rates=packageRates[b.dataset.cabinet];if(rates){for(const [k,v] of Object.entries(rates)){const d=defs.find(d=>d[0]===k);if(d)draftPolicy[k]=clamp(v,d[2],d[3]);}renderPanel('policies');toast('Policy proposal drafted. Review and enact it to apply.');}return}
 if(b.id==='marketPolicy'){openPanel('policies');return}
 if(b.id==='marketFamilies'){openPanel('citizens');return}
 if(b.id==='marketCompanies'){openPanel('businesses');return}
 if(b.id==='jumpAgenda'){openPanel('agenda');return}
 if(b.id==='jumpJournal'){openPanel('journal');return}
 if(b.id==='closeInspect'){closePanel();return}
 if(b.id==='convene'){if(G.day-G.lastEventDay>=12){offerCouncilEvent(true)}return}
 if(b.dataset.inbox!==undefined){reviewCouncilInbox(+b.dataset.inbox);return}
 if(b.dataset.ambition){G.ambition=b.dataset.ambition;updateHeader();renderPanel('agenda');save();return}
 if(b.dataset.filterPeople){filterPeople=b.dataset.filterPeople;renderPanel('citizens');return}
 if(b.dataset.filterFirms){filterFirms=b.dataset.filterFirms;renderPanel('businesses');return}
 if(b.dataset.buildCategory){constructionCategory=b.dataset.buildCategory;renderPanel('construction');return}
 if(b.id==='focusBad'){const poor=G.households.filter(h=>h.people.length>0&&readBuild(h.home)).sort((a,b)=>a.cash/Math.max(1,a.people.length)-b.cash/Math.max(1,b.people.length))[0];if(poor&&readBuild(poor.home)){selected={id:poor.home};openPanel('inspect')}return}
 if(b.id==='saveNow'){const epoch=saveEpoch;save().then(ok=>{if(epoch===saveEpoch)toast(ok?'Village saved on this device.':'Saving failed; export a backup before leaving.')})}
 if(b.id==='restart'){showCustomEvent('TOWN ARCHIVE','Found another town?','Starting a new village will overwrite your most recent local autosave. Export a backup before proceeding.',[
  {title:'Keep the present village',desc:'Return to your existing town.',apply:()=>{}},
  {title:'Start a fresh village',desc:'Discard the current local save and return to the founding menu.',apply:()=>{start(true);closePanel();toast('A new village has been founded.')}}
 ]);return}
 if(b.id==='backupSave'){exportSave();return}
 if(b.id==='importSave'){importSave();return}
 if(b.dataset.servicePolicy){openPanel('policies');const input=$('panelBody').querySelector('[data-policy="'+(b.dataset.servicePolicy==='health'?'healthBudget':'educationBudget')+'"]');if(input){input.closest('details').open=true;input.scrollIntoView({block:'center'});input.focus();}return}
 if(b.dataset.serviceAccess){overlay=b.dataset.serviceAccess==='health'?'healthAccess':'schoolAccess';closePanel();dirty=true;toast('Service access: green available · gold partial · copper unserved. Road distance and shared facility places determine reach.');return}
 if(b.dataset.openPanel){openPanel(b.dataset.openPanel);return}
 if(b.id==='tutorial'){openTutorialDialog(b);return}
 if(b.id==='toggleDevelopment'){G.autoBuild=!G.autoBuild;save();renderPanel(active);toast(G.autoBuild?'Private investment resumed.':'New private construction paused.');return;}
 if(b.id==='overlayMetro'){overlay=overlay==='metro'?'none':'metro';dirty=true;renderPanel(active);return;}
 if(b.id==='overlayR'){overlay=overlay==='roads'?'none':'roads';dirty=true;renderPanel(active);return}
 if(b.id==='overlayC'){overlay=overlay==='crime'?'none':'crime';dirty=true;renderPanel(active);return}
 if(b.id==='overlayH'){overlay=overlay==='hardship'?'none':'hardship';dirty=true;renderPanel(active);return}
 if(b.id==='overlayB'){overlay=overlay==='business'?'none':'business';dirty=true;renderPanel(active);return}
 if(b.id==='tradeToggle'){draftPolicy.imports=!(draftPolicy.imports??G.policy.imports);renderPanel('policies');return}
 if(b.id==='soundToggle'){soundEnabled=!soundEnabled;try{localStorage.setItem('townledger-audio',soundEnabled?'on':'off')}catch(e){};refreshAmbience();renderPanel('settings');return}
 if(b.id==='borrow'){let limit=Math.max(25000,G.stats.population*350);if(G.debt+5000>limit||G.region<5000){toast('Regional lender declined: the credit limit or available funds have been reached.');return;}G.debt+=5000;G.treasury+=5000;G.region-=5000;story('Council borrowed $5,000 from the regional lender.');recompute();updateHeader();save();renderPanel(active)}
 if(b.id==='repay'){let v=Math.min(5000,G.debt,G.treasury);G.debt-=v;G.treasury-=v;G.region+=v;recompute();updateHeader();save();renderPanel(active)}
});
$('zoomIn').onclick=()=>{cam.zoom=clamp(cam.zoom*1.22,.025,1.7);dirty=true};$('zoomOut').onclick=()=>{cam.zoom=clamp(cam.zoom/1.22,.025,1.7);dirty=true};$('center').onclick=()=>{if(overlay==='charter'){overlay='none';parcelFocus=null;}centerTownCamera();};$('overlayToggle').onclick=()=>{overlay=overlay==='none'?'roads':overlay==='roads'?'metro':overlay==='metro'?'hardship':overlay==='hardship'?'crime':overlay==='crime'?'business':'none';dirty=true;toast('Map overlay: '+overlay)};
 $('pause').onclick=()=>{paused=!paused;fit();updateHeader();if(paused){draw();save()}};const SPEED_PRESETS=[1,2,4,8,16,32,64];
 $('speed').onclick=()=>{const index=SPEED_PRESETS.indexOf(speed);speed=SPEED_PRESETS[(index+1)%SPEED_PRESETS.length];acc=0;sampleDays=0;sampleSeconds=0;G.speed=speed;fit();updateHeader()};
 $('speedRange').addEventListener('input',e=>{speed=SPEED_PRESETS[+e.target.value]||1;acc=0;sampleDays=0;sampleSeconds=0;if(G)G.speed=speed;fit();updateHeader();});
$('speedRange').addEventListener('change',()=>{if(G)save();});
function start(newVillage){if(newVillage){seed(Number($('townSeed')?.value)||42)}else if(!load())seed();centerTownCamera();invalidateRoads();buildMode='';selected=null;overlay='none';paused=false;speed=SPEED_PRESETS.includes(G.speed)?G.speed:1;acc=0;fit();$('welcome').style.display='none';dirty=true;staticDirty=true;updateHeader();openPanel('overview');}
$('newTown').onclick=()=>{start(true);refreshAmbience()};$('continue').onclick=()=>{start(false);refreshAmbience()};
try{if(localStorage.getItem('townledger-v6')||localStorage.getItem('townledger-v6-backup')||localStorage.getItem('townledger-village-founder-3')||localStorage.getItem('townledger-village-civic-2'))$('continue').style.display='block'}catch(e){}
window.addEventListener('resize',fit);fit();
let last=performance.now(),acc=0,lastMapDraw=0,lastHeader=0,lastPanel=0,lastAutosave=performance.now(),speedSample=0,sampleDays=0,sampleSeconds=0;
function frame(now){
 const raw=Math.max(0,(now-last)/1000);last=now;
 if(G&&!paused&&!hostSuspended&&!pendingEvent&&!document.hidden){
  // Admit requested wall time, then do a bounded amount of real simulation work.
  // A bounded queue avoids a multi-minute catchup after an interrupted phone frame.
  const dt=Math.min(raw,.25);acc=Math.min(acc+dt*speed,1.65*8);
  const budget=speed>=16?10:6,end=performance.now()+budget;let completed=0;
  while(acc>=1.65&&(!completed||performance.now()<end)&&!pendingEvent){const t=performance.now();tick();perfStats.ticks.push(performance.now()-t);if(perfStats.ticks.length>180)perfStats.ticks.shift();acc-=1.65;completed++;}
  perfStats.days+=completed;perfStats.elapsed+=dt;perfStats.backlog=acc/1.65;
  sampleDays+=completed;sampleSeconds+=raw;
  if(sampleSeconds>=1){perfStats.effective=sampleDays*1.65/sampleSeconds;sampleDays=0;sampleSeconds=0;}
  if(!gameOptions.reducedMotion){frameClock+=dt;if(gameOptions.traffic)trafficUpdate(dt);}dirty=true;
 }else{sampleDays=0;sampleSeconds=0;if(document.hidden)acc=0;}
 if(G&&!document.hidden){
  if(now-lastHeader>=250){updateHeader();lastHeader=now;}
  if(active&&!paused&&now-lastPanel>=1500&&!['policies','citizens','settings','construction'].includes(active)&&!$('panelBody').contains(document.activeElement)){renderPanel(active);lastPanel=now;}
  if(!paused&&now-lastAutosave>=gameOptions.autoSave*1000){save();lastAutosave=now;}
  const fps=speed>=32?Math.min(20,gameOptions.fps):gameOptions.fps;
  if(dirty&&now-lastMapDraw>=1000/fps){const t=performance.now();draw();perfStats.frames.push(performance.now()-t);if(perfStats.frames.length>600)perfStats.frames.shift();lastMapDraw=now;}
 }
 requestAnimationFrame(frame);
}requestAnimationFrame(frame);
window.addEventListener('beforeunload',()=>save());document.addEventListener('visibilitychange',()=>{last=performance.now();acc=0;if(document.hidden){save();stopGameAudio()}else refreshAmbience()});
window.addEventListener('error',e=>{console.error(e.error||e.message);toast('Runtime issue: '+(e.message||'Unknown'))});

// SOURCE: 71-trip-inspector.js
// A transport sample can be inspected without changing economic cargo or jobs.
let inspectedTrip=null;
function inspectTripAt(wx,wy){
 let nearest=null,distance=12/cam.zoom;
 for(const v of traffic){const p=vehiclePosition(v),d=Math.hypot(wx-p.x,wy-p.y);if(d<distance){nearest=v;distance=d;}}
 if(!nearest)return false;inspectedTrip={...nearest,path:nearest.path.slice()};openPanel('trip');dirty=true;return true;
}
function renderTripInspector(){
 if(!inspectedTrip)return tip('Tap a moving commuter or delivery on the map.');
 const live=traffic.find(v=>v.id===inspectedTrip.id),trip=live||inspectedTrip,from=readBuild(trip.from),to=readBuild(trip.to),shipment=(G.freight||[]).find(s=>s.id===trip.shipment);
 const label=b=>b?b.firm>=0?(G.firms[b.firm]?.name||types[b.kind].n):b.hh>=0?(G.households[b.hh]?.name+' household'):types[b.kind].n:'Former site';
 return head(trip.style==='truck'?'Delivery on the road':trip.style==='pedestrian'?'A resident on foot':'A resident’s journey')+tip(trip.reason||'Local service journey')+strip('Trip sample',live?'Travelling':'Completed or no longer sampled')+strip('Origin',label(from))+strip('Destination',label(to))+strip('Road segments',Math.max(0,trip.path.length-1))+(shipment?strip('Cargo in transit',fmt(shipment.qty)+' '+shipment.good)+strip('Delivery accounting',shipment.remaining+' simulated days remaining'):'')+tip('Visible trips sample real job assignments and paid cargo. The economy continues tracking residents and shipments when visual traffic is hidden.')+`<div class="btnrow">${from?`<button data-inspect="${from.id}">Inspect origin</button>`:''}${to?`<button data-inspect="${to.id}">Inspect destination</button>`:''}<button data-trip-close>Back to map</button></div>`;
}
function drawInspectedRoute(g){
 if(active!=='trip'||!inspectedTrip)return;const trip=traffic.find(v=>v.id===inspectedTrip.id)||inspectedTrip;
 g.save();g.strokeStyle='#f2d99c';g.lineWidth=3/cam.zoom;g.lineJoin='round';g.beginPath();trip.path.forEach((id,i)=>{const p=roadCenter(id);if(i)g.lineTo(...p);else g.moveTo(...p)});g.stroke();
 for(const id of [trip.path[0],fromEnd(trip.path)]){const p=roadCenter(id);g.fillStyle='#315e4b';g.beginPath();g.arc(...p,5/cam.zoom,0,Math.PI*2);g.fill();}g.restore();
}
document.addEventListener('click',e=>{if(e.target.closest('[data-trip-close]'))closePanel()});

// SOURCE: 80-civic.js
// --- Founder's Edition: long-form borough strategy systems and reporting. ---
const AMBITIONS=[
 {id:'resilient_banks',title:'A resilient banking centre',description:'Keep three solvent banks operating, fewer than two business loan defaults, and 75% employment for 50 days.',days:50,goal:g=>g.banks?.filter(b=>!b.closed&&bankEquity(b)>0).length>=3&&g.finance.businessDefaults<2&&g.stats.employment>=75,progress:g=>Math.min(1,(g.banks?.filter(b=>!b.closed).length||0)/3*.6+g.stats.employment/75*.4),reward:6500},
 {id:'balanced',title:'Keep the books',description:'Maintain $60,000 in municipal cash, no debt, and 65% employment for 25 days.',days:25,goal:g=>g.treasury>=60000&&g.debt===0&&g.stats.employment>=65,progress:g=>Math.min(1,(g.treasury/60000)*.65+(g.stats.employment/65)*.35),reward:3500},
 {id:'safe',title:'A safe place to live',description:'Maintain a safety index of 88, with no more than two crimes in 30 days, for 20 days.',days:20,goal:g=>g.stats.safety>=88&&g.stats.dailyCrime<=2,progress:g=>Math.min(1,g.stats.safety/88),reward:3200},
 {id:'market',title:'A thriving market town',description:'Support at least 25 trading businesses and employment above 80% for 25 days.',days:25,goal:g=>g.stats.businesses>=25&&g.stats.employment>=80,progress:g=>Math.min(1,g.stats.businesses/25),reward:5000},
 {id:'families',title:'A town for families',description:'Reduce household hardship under 9% while retaining at least 70 homes for 20 days.',days:20,goal:g=>g.stats.hardship<=9&&g.homes.length>=70,progress:g=>Math.min(1,.5*(1-g.stats.hardship/100)+.5*g.homes.length/70),reward:4800},
 {id:'education',title:'A learned community',description:'Raise schooling to 70 and public health to 80, then sustain both for 20 days.',days:20,goal:g=>g.education>=70&&g.health>=80,progress:g=>Math.min(1,(g.education/70+g.health/80)/2),reward:4200},
 {id:'liberty',title:'A leaner tax regime',description:'Maintain income tax at 5% or less, employment at 75%+, and a $25,000 reserve for 25 days.',days:25,goal:g=>g.policy.incomeTax<=5&&g.stats.employment>=75&&g.treasury>=25000,progress:g=>Math.min(1,.5*g.stats.employment/75+.5*g.treasury/25000),reward:4000},
 {id:'resilience',title:'Ready for hard times',description:'Raise emergency readiness to 80+, fund a second fire brigade, and sustain it 20 days.',days:20,goal:g=>g.stats.preparedness>=80&&g.buildings.filter(b=>b.kind==='fire').length>=2,progress:g=>Math.min(1,g.stats.preparedness/80),reward:4000},
 {id:'boom',title:'An ambitious borough',description:'Bring 300 residents into the town without losing employment below 70% for 25 days.',days:25,goal:g=>g.people.length>=300&&g.stats.employment>=70,progress:g=>Math.min(1,g.people.length/300),reward:6500},
 {id:'reputation',title:'An enduring mandate',description:'Earn 78% council approval, with a safety index of 75, for 30 days.',days:30,goal:g=>g.council.approval>=78&&g.stats.safety>=75,progress:g=>Math.min(1,g.council.approval/78),reward:5000}
];
const COUNCIL_EVENTS=[
 {title:'A petition from the shopkeepers',type:'COMMERCE & TRADE',text:'Local merchants say rising delivery expenses are eating their margins. They ask for temporary help, while residents want prices kept down.',choices:[
  {title:'Finance a local delivery cooperative',desc:'Pay $2,200. Deliver working capital to nearby firms.',cost:2200,apply:()=>{let list=G.firms.filter(f=>!f.closed);let n=Math.min(8,list.length);for(let f of list.slice(0,n))f.cash+=2200/n;G.council.factions.merchants+=4;}},
  {title:'Simplify commercial licences',desc:'Reduce the permit fee by $200; sacrifice possible permit revenue.',apply:()=>{G.policy.permitFee=Math.max(0,G.policy.permitFee-200);G.council.factions.merchants+=3}},
  {title:'Leave prices and freight to the market',desc:'No expenditure. Merchants remain responsible for their costs.',apply:()=>{G.council.factions.merchants-=2}}
 ]},
 {title:'The bridge needs repairs',type:'PUBLIC WORKS',text:'The stone bridge carrying traffic to the northern quarter has begun to crack. Engineers advise action before winter.',choices:[
  {title:'Repair it properly',desc:'Pay $3,000. Better trade access and road reliability.',cost:3000,apply:()=>{G.policy.roadBudget=Math.min(250,G.policy.roadBudget+10);G.council.factions.public+=3}},
  {title:'Authorize urgent patchwork',desc:'Pay $900. A partial, temporary improvement.',cost:900,apply:()=>{G.council.factions.public+=1}},
  {title:'Postpone repairs',desc:'No cost now. Residents question council priorities.',apply:()=>{G.council.factions.public-=5;G.unrest+=2}}
 ]},
 {title:'Families facing eviction',type:'HOUSING & WELFARE',text:'A local charity reports several working households have fallen behind on rent. It asks the council to contribute to an emergency relief fund.',choices:[
  {title:'Fund a relief programme',desc:'Transfer $2,400 directly to the poorest households.',cost:2400,apply:()=>{let h=G.households.slice().sort((a,b)=>a.cash-b.cash).slice(0,12);for(let p of h){p.cash+=200;p.stress=Math.max(0,p.stress-5);}G.council.factions.workers+=4}},
  {title:'Make relief conditional on training',desc:'Spend $1,300 on work placement and training.',cost:1300,apply:()=>{G.education+=2;G.council.factions.workers+=2}},
  {title:'Refer households to private charity',desc:'No budget impact. Increased dissatisfaction among poorer households.',apply:()=>{G.council.factions.workers-=4}}
 ]},
 {title:'A merchant wants to expand',type:'PRIVATE INVESTMENT',text:'A local trader has identified a vacant premises. They can open another shop if planning permission and capital are secured.',choices:[
  {title:'Offer a development grant',desc:'Pay $2,000 in startup capital and promote private entry.',cost:2000,apply:()=>{let f=G.firms.filter(f=>f.closed)[0];if(f){f.closed=false;f.cash+=5500;f.strain=0;assignJobs();}else{let f=pick(G.firms);if(f)f.cash+=2000;}G.council.factions.merchants+=3}},
  {title:'Waive the entry fee for a year',desc:'Reduce new-entry permit charges to $0.',apply:()=>{G.policy.permitFee=0;G.council.factions.merchants+=3}},
  {title:'Decline special favours',desc:'The standard planning and licensing system remains in force.',apply:()=>{G.council.factions.merchants-=1}}
 ]},
 {title:'Illness spreads at the school',type:'PUBLIC HEALTH',text:'A seasonal respiratory illness is circulating. The clinic says it can reduce disruption if a temporary programme is funded.',choices:[
  {title:'Provide treatment and preventive supplies',desc:'Spend $1,800. Improves town health and reduces household stress.',cost:1800,apply:()=>{G.health=Math.min(100,G.health+5);for(const h of G.households)h.stress=Math.max(0,h.stress-.6)}},
  {title:'Ask employers to adopt voluntary precautions',desc:'No direct cost. Modest public health gains.',apply:()=>{G.health=Math.min(100,G.health+1)}},
  {title:'Take no action',desc:'The illness is allowed to run its course.',apply:()=>{G.health=Math.max(20,G.health-3);G.council.factions.public-=2}}
 ]},
 {title:'The industrial safety dispute',type:'WORKING CONDITIONS',text:'Workers at the sawmill say basic precautions have been neglected. Employers warn that more inspection rules will raise costs.',choices:[
  {title:'Increase workplace inspections',desc:'Raise business regulation by 15 points.',apply:()=>{G.policy.businessRegulation=Math.min(100,G.policy.businessRegulation+15);G.council.factions.workers+=3;G.council.factions.merchants-=2}},
  {title:'Co-finance safety improvements',desc:'Spend $1,500 on protective equipment for firms.',cost:1500,apply:()=>{G.health+=2;G.council.factions.workers+=2;G.council.factions.merchants+=2}},
  {title:'Leave the matter to individual employers',desc:'No spending or new regulatory obligations.',apply:()=>{G.council.factions.workers-=3;G.council.factions.merchants+=2}}
 ]},
 {title:'A dry summer threatens the farms',type:'AGRICULTURE',text:'Farmers report that irrigation ditches are running low. Crop yields and exports may decline unless the borough acts.',choices:[
  {title:'Build emergency irrigation channels',desc:'Spend $2,800; support farm production capacity.',cost:2800,apply:()=>{G.firms.filter(f=>f.kind==='farm'&&!f.closed).forEach(f=>{f.stock.grain+=80;f.cash+=150;});G.council.factions.merchants+=2}},
  {title:'Provide a small farmer loan',desc:'Advance $1,000 to local farms.',cost:1000,apply:()=>{G.firms.filter(f=>f.kind==='farm'&&!f.closed).slice(0,5).forEach(f=>f.cash+=200)}},
  {title:'Allow farms to adapt privately',desc:'No expense, but traders face reduced near-term output.',apply:()=>{G.firms.filter(f=>f.kind==='farm'&&!f.closed).forEach(f=>f.stock.grain=Math.max(0,f.stock.grain-50))}}
 ]},
 {title:'The night watch requests support',type:'CRIME & SECURITY',text:'The constabulary reports a rise in burglary attempts in outlying lanes. Officers request more staff and lighting.',choices:[
  {title:'Raise daily patrol funding',desc:'Increase constabulary expenditure by $40 per day.',apply:()=>{G.policy.policeBudget=Math.min(800,G.policy.policeBudget+40);G.council.factions.public+=2}},
  {title:'Fund a one-time neighbourhood programme',desc:'Spend $1,300; support vulnerable households.',cost:1300,apply:()=>{G.households.filter(h=>h.security<65).forEach(h=>h.security+=8);G.council.factions.public+=2}},
  {title:'Maintain the existing patrols',desc:'No new expense.',apply:()=>{G.council.factions.public-=1}}
 ]},
 {title:'A new regional trade agreement',type:'COMMERCE & TRADE',text:'Regional merchants offer stable supplies of grain and timber. In return, they request lower import charges.',choices:[
  {title:'Sign a free-trade agreement',desc:'Remove import tariffs and allow unrestricted regional trade.',apply:()=>{G.policy.importTariff=0;G.policy.imports=true;G.council.factions.merchants+=4}},
  {title:'Negotiate a lower tariff',desc:'Cut the current tariff rate in half.',apply:()=>{G.policy.importTariff=Math.floor(G.policy.importTariff/2);G.council.factions.merchants+=2}},
  {title:'Keep the present trading arrangements',desc:'No immediate policy change.',apply:()=>{}}
 ]},
 {title:'Flooding on the low road',type:'CIVIL DEFENCE',text:'Heavy rain has washed out culverts on the east side. Some properties face water damage if repairs are delayed.',choices:[
  {title:'Mobilize the fire brigade and volunteers',desc:'Spend $2,700. Protect homes and restore access.',cost:2700,apply:()=>{G.crisesHandled++;G.council.factions.public+=3}},
  {title:'Organize local volunteer crews',desc:'Spend $650. Partial protection.',cost:650,apply:()=>{G.crisesHandled++;G.health=Math.max(0,G.health-1)}},
  {title:'Leave residents to arrange private repairs',desc:'No municipal expense; some households suffer damage.',apply:()=>{G.households.slice(0,8).forEach(h=>{let p=Math.min(h.cash,170);h.cash-=p;G.region+=p;h.stress+=3;});G.council.factions.public-=3}}
 ]},
 {title:'The apprentices ask for a school',type:'EDUCATION & EMPLOYMENT',text:'Young workers say the town needs formal training if local firms are to compete with regional employers.',choices:[
  {title:'Establish an apprenticeship fund',desc:'Spend $1,600, increasing vocational skill.',cost:1600,apply:()=>{G.education=Math.min(100,G.education+5);G.council.factions.workers+=3}},
  {title:'Ask businesses to organize training',desc:'No municipal expenditure. Small productivity improvement.',apply:()=>{G.education=Math.min(100,G.education+1);G.council.factions.merchants+=2}},
  {title:'Maintain current schooling',desc:'No change.',apply:()=>{G.council.factions.workers-=1}}
 ]},
 {title:'Council must address the deficit',type:'THE PUBLIC PURSE',text:'The treasurer warns that current services may become unaffordable if reserves continue to decline.',choices:[
  {title:'Reduce non-essential daily programmes',desc:'Cut administrative, outreach and road spending.',apply:()=>{G.policy.outreachBudget=Math.max(0,G.policy.outreachBudget-20);G.policy.roadBudget=Math.max(0,G.policy.roadBudget-10);G.policy.educationBudget=Math.max(0,G.policy.educationBudget-20);G.council.factions.public-=3}},
  {title:'Increase the income-tax rate',desc:'Raise income tax by 3 percentage points.',apply:()=>{G.policy.incomeTax=Math.min(40,G.policy.incomeTax+3);G.council.factions.workers-=3}},
  {title:'Raise an emergency municipal loan',desc:'Borrow $7,000 with interest due.',apply:()=>{G.debt+=7000;G.treasury+=7000;G.region-=7000}}
 ]}
];
// Additional town stories: each decision affects actual funds, people, local firms or policy rules.
COUNCIL_EVENTS.push(
 {title:'The bakers face a flour shortage',type:'FOOD SUPPLY',text:'The local bakery guild cannot obtain sufficient flour at current prices. Families are already paying more for basic bread.',choices:[
  {title:'Buy emergency supplies',desc:'Pay $1,800 to restock bakeries and reduce immediate shortages.',cost:1800,apply:()=>{G.firms.filter(f=>f.kind==='bakery'&&!f.closed).slice(0,4).forEach(f=>{f.stock.flour=(f.stock.flour||0)+120;f.cash+=150;});G.council.factions.workers+=2}},
  {title:'Ease grain import duties',desc:'Remove import tariffs to lower suppliers’ input costs.',apply:()=>{G.policy.importTariff=0;G.policy.imports=true;G.council.factions.merchants+=2}},
  {title:'Keep the market free of intervention',desc:'No public expense; food prices may remain elevated.',apply:()=>{G.council.factions.workers-=2}}
 ]},
 {title:'Petition for fair wages',type:'WORK & INCOME',text:'A group of poorly paid employees wants the council to mandate higher wages. Shopkeepers say their margins are already thin.',choices:[
  {title:'Raise the daily wage floor by $5',desc:'Employers must meet a higher payroll; workers may gain more income.',apply:()=>{G.policy.minWage=Math.min(90,G.policy.minWage+5);G.council.factions.workers+=3;G.council.factions.merchants-=2}},
  {title:'Subsidize employment instead',desc:'Pay employers an extra $2 per working resident each day.',apply:()=>{G.policy.employmentSubsidy=Math.min(15,G.policy.employmentSubsidy+2);G.council.factions.merchants+=2;G.council.factions.workers+=2}},
  {title:'Keep wages privately negotiated',desc:'Make no new employment rule.',apply:()=>{G.council.factions.workers-=2}}
 ]},
 {title:'The housing shortage petition',type:'HOUSING & PLANNING',text:'Young households say they cannot find affordable houses near the square. Established property owners oppose building on the village outskirts.',choices:[
  {title:'Open new residential land',desc:'Reduce zoning restrictions by 20 points to allow private housebuilding.',apply:()=>{G.policy.zoningRestriction=Math.max(0,G.policy.zoningRestriction-20);G.council.factions.homeowners-=2;G.council.factions.workers+=3}},
  {title:'Finance new municipal cottages',desc:'Pay $3,000 into a housing programme for families in hardship.',cost:3000,apply:()=>{G.households.slice().sort((a,b)=>a.cash-b.cash).slice(0,10).forEach(h=>{h.cash+=300;h.stress=clamp(h.stress-5,0,100)});G.council.factions.workers+=3}},
  {title:'Preserve the current neighbourhood plans',desc:'Leave building restrictions in place.',apply:()=>{G.council.factions.homeowners+=2;G.council.factions.workers-=2}}
 ]},
 {title:'A theft at the market square',type:'LAW & ORDER',text:'Several stallholders report stolen cash, and residents accuse the watch of ignoring repeated warnings.',choices:[
  {title:'Fund a targeted investigation',desc:'Spend $1,400 on detectives and restitution for the affected traders.',cost:1400,apply:()=>{G.firms.filter(f=>!f.closed).slice(0,7).forEach(f=>f.cash+=200);G.council.factions.public+=3}},
  {title:'Build a stronger night watch',desc:'Raise ongoing police funding by $30 per day.',apply:()=>{G.policy.policeBudget=Math.min(800,G.policy.policeBudget+30);G.council.factions.public+=2}},
  {title:'Ask stallholders to hire their own guards',desc:'No public expense; private traders bear the burden.',apply:()=>{G.council.factions.merchants-=2}}
 ]},
 {title:'Refugees from the flooded valley',type:'MIGRATION & COMMUNITY',text:'Families displaced by a flood in a neighbouring district are asking to settle in the town. The school and grocers expect extra demand.',choices:[
  {title:'Open a municipal resettlement fund',desc:'Spend $2,000 supporting the lowest-cash families and social integration.',cost:2000,apply:()=>{G.households.slice().sort((a,b)=>a.cash-b.cash).slice(0,10).forEach(h=>{h.cash+=200;h.stress=clamp(h.stress-2,0,100)});G.council.factions.public+=3}},
  {title:'Allow private sponsors to assist arrivals',desc:'No municipal funding; remove some housing restrictions.',apply:()=>{G.policy.zoningRestriction=Math.max(0,G.policy.zoningRestriction-10);G.council.factions.merchants+=2}},
  {title:'Defer new settlement until homes are built',desc:'No immediate housing pressure or public spending.',apply:()=>{G.council.factions.public-=2}}
 ]},
 {title:'An old mine could reopen',type:'JOBS & NATURAL RESOURCES',text:'A regional operator wants to restart an abandoned quarry. It could create jobs, but nearby residents worry about dust and road wear.',choices:[
  {title:'Offer a conditional investment grant',desc:'Pay $1,600 to boost the quarry’s capital and maintain safety standards.',cost:1600,apply:()=>{const f=G.firms.find(f=>f.kind==='quarry');if(f){f.cash+=1600;f.strain=Math.max(0,f.strain-10);if(f.closed){f.closed=false;assignJobs()}}G.council.factions.merchants+=2}},
  {title:'Permit reopening under stricter safeguards',desc:'Raise inspection standards by 10 points.',apply:()=>{G.policy.businessRegulation=Math.min(100,G.policy.businessRegulation+10);G.council.factions.homeowners+=3}},
  {title:'Do not subsidize a private enterprise',desc:'No public expenditure or special permission.',apply:()=>{G.council.factions.merchants-=1}}
 ]},
 {title:'The volunteer brigade wants equipment',type:'CIVIL DEFENCE',text:'The local volunteer corps warns that the next major storm could overwhelm the existing fire brigade.',choices:[
  {title:'Buy new equipment',desc:'Spend $2,100 on storm preparedness and local protective supplies.',cost:2100,apply:()=>{G.policy.defenseBudget=Math.min(800,G.policy.defenseBudget+20);G.crisesHandled++;G.council.factions.public+=3}},
  {title:'Expand volunteer training',desc:'Increase volunteer funding by $35 per day.',apply:()=>{G.policy.militiaBudget=Math.min(400,G.policy.militiaBudget+35);G.council.factions.public+=2}},
  {title:'Rely on mutual aid from neighbouring towns',desc:'No extra town spending; coverage remains uncertain.',apply:()=>{G.council.factions.public-=2}}
 ]},
 {title:'The grocers dispute inspection fees',type:'SMALL BUSINESS',text:'Several family-owned shops are paying more for paperwork and inspections than expected. Residents also want food safety enforced.',choices:[
  {title:'Simplify the inspection rules',desc:'Lower business regulation by 15 points, reducing operating compliance costs.',apply:()=>{G.policy.businessRegulation=Math.max(0,G.policy.businessRegulation-15);G.council.factions.merchants+=4}},
  {title:'Help small shops modernize',desc:'Spend $1,800 on better storage equipment and food safety.',cost:1800,apply:()=>{G.firms.filter(f=>f.kind==='grocer'&&!f.closed).slice(0,6).forEach(f=>{f.cash+=300;f.stock.food=(f.stock.food||0)+20});G.council.factions.public+=2}},
  {title:'Keep current safeguards and fees',desc:'No change to local regulatory standards.',apply:()=>{G.council.factions.public+=1;G.council.factions.merchants-=2}}
 ]}
);


function setupScenario(){
 if(chosenScenario==='hardtimes'){
   G.region+=G.treasury-16000;G.treasury=16000;G.debt=9000;G.treasury+=9000;G.region-=9000;for(const f of G.firms.filter(f=>f.kind==='farm'||f.kind==='sawmill')){let old=f.cash;f.cash*=.22;G.region+=old-f.cash;f.strain=34;}for(const h of G.households.slice(0,26)){let old=h.cash;h.cash*=.15;G.region+=old-h.cash;h.stress+=25}G.policy.incomeTax=19;G.policy.profitTax=26;G.policy.zoningRestriction=55;G.regionalDemand=.55;G.council.approval=41;G.council.factions.workers=39;G.scenario='hardtimes';story('The borough faces layoffs, debt and a strained treasury.','bad');
 }else if(chosenScenario==='frontier'){
   G.region+=G.treasury-43000;G.treasury=43000;G.policy.incomeTax=6;G.policy.profitTax=7;G.policy.policeBudget=90;G.policy.defenseBudget=60;G.policy.educationBudget=40;G.policy.healthBudget=35;G.policy.aidBudget=40;G.scenario='frontier';
   for(const f of G.firms.slice(10)){f.closed=true;for(let id of f.workers)if(G.people[id])G.people[id].job=-1;f.workers=[];}G.council.approval=69;story('A small frontier council inherits open land and a lean budget.','neutral');
 }else if(chosenScenario==='industrial'){
   G.region+=G.treasury-68000;G.treasury=68000;G.policy.profitTax=5;G.policy.incomeTax=15;G.policy.permitFee=0;G.policy.businessRegulation=40;G.policy.minWage=34;G.policy.educationBudget=130;G.scenario='industrial';
   for(const f of G.firms){f.cash+=2500;G.region-=2500}G.council.approval=58;story('Industrial investment is rising, but employers and workers disagree over wages and regulation.','neutral');
 }else{G.scenario='settlement';story('The council inherits a promising community and a difficult balancing act.','good');}
 recompute();
}
function fundLocalService(amount){return fundedPublicPayroll(amount);}
function fundCivicServices(){const P=G.policy;
 const healthRatio=purchaseCivicService('health',P.healthBudget||0),schoolRatio=purchaseCivicService('school',P.educationBudget||0),roadRatio=fundLocalService(P.roadBudget||0),militiaRatio=fundLocalService(P.militiaBudget||0),transitRatio=G.actualServiceFunding?.transit||0;
 G.actualServiceFunding=Object.assign(G.actualServiceFunding||{},{roads:roadRatio,health:healthRatio,school:schoolRatio,militia:militiaRatio,transit:transitRatio});
}
function extendedCivicDay(){
 let P=G.policy;
 let clinic=G.buildings.filter(b=>b.kind==='clinic').length,parks=G.buildings.filter(b=>b.kind==='park'||b.kind==='square').length,schools=G.buildings.filter(b=>b.kind==='school').length,watch=G.buildings.filter(b=>b.kind==='watchtower').length;
 const healthRatio=G.actualServiceFunding?.health||0,schoolRatio=G.actualServiceFunding?.school||0,roadRatio=G.actualServiceFunding?.roads||0,militiaRatio=G.actualServiceFunding?.militia||0,transitRatio=G.actualServiceFunding?.transit||0;
 G.health=clamp(G.health+(.063*healthRatio-.037- (G.stats.hardship||0)*.0002),25,99);
 G.education=clamp(G.education+.048*schoolRatio-.009,15,99);
 civicTrainingDay(schoolRatio);
 G.stats.health=Math.round(G.health);G.stats.education=Math.round(G.education);
 if(G.day%3===0&&schoolRatio>0){let p=pick(G.people.filter(p=>!p.deceased&&p.movedAway!==true));if(p){p.skill=clamp(p.skill+.018*localCivicCoverage('school',p.hh),0,1.3)}}
 if(G.day%6===0){let p=pick(G.people.filter(p=>!p.deceased&&p.movedAway!==true));if(p){p.health=clamp(p.health+(-.3+1.6*localCivicCoverage('health',p.hh))+rn(-.5,.5),10,100);if(p.health<25){const h=G.households[p.hh];if(h)h.stress=clamp(h.stress+1,0,100)}}}
 if(G.day%8===0&&parks>0){let h=pick(G.households);if(h)h.stress=clamp(h.stress-1.5,0,100)}
 const warmth=G.weather==='storm'?-.4:0;
 G.stats.wellbeing=Math.round(clamp(82-G.households.reduce((s,h)=>s+h.stress,0)/Math.max(1,G.households.length)*.46+parks*.5+G.health*.08+warmth,0,100));
 G.stats.avgCash=G.stats.cash/Math.max(1,G.households.length);
 G.stats.compliance=P.businessRegulation;
 G.stats.marketConfidence=Math.round(clamp(77-G.stats.unemployment*.5-G.stats.hardship*.48-P.profitTax*.23-P.permitFee*.005+Math.max(0,15-P.importTariff)*.12+parks*.3+(G.regionalDemand-1)*20,5,99));
 G.stats.propertyCosts=(2.15+P.zoningRestriction*.035);
 G.stats.realWages=Math.round(G.households.reduce((s,h)=>s+h.income-h.tax-h.rent-h.food,0)/Math.max(1,G.stats.population)*10)/10;
 G.stats.prosperity=Math.round(clamp(G.stats.employment*.5+G.stats.marketConfidence*.3+G.stats.wellbeing*.2,0,100));
 G.stats.roadService=Math.round(clamp((G.stats.roadCondition??75)*.65+clamp((P.roadBudget||0)*roadRatio/Math.max(1,(graph().neighbors.size-(G.privateRoads||[]).length)*.045/.23),0,1)*23+clamp((P.transitBudget||0)*transitRatio/280,0,1)*12,0,100));
 G.stats.militia=Math.round(clamp(25+militiaRatio*(P.militiaBudget||0)/30+watch*12,0,100));
}
function updateCouncilAndMissions(){
 const C=G.council,P=G.policy,s=G.stats;
 if(G.day%4===0){
  const worker=clamp(20+s.employment*.45-s.hardship*.75+Math.min(P.aidBudget,250)*.024-P.foodTax*.60-P.incomeTax*.30+s.wellbeing*.06,5,98);
  const merchant=clamp(36+s.marketConfidence*.22+s.employment*.20-P.profitTax*.40-P.businessRegulation*.12-P.permitFee*.008,5,98);
  const homeowner=clamp(38+s.safety*.30+s.employment*.10-P.propertyTax*6-P.zoningRestriction*.12+Math.min(16,s.wellbeing*.08),5,98);
  const publicv=clamp(17+s.safety*.40+s.wellbeing*.30+s.health*.1-Math.min(25,Math.max(0,G.debt-G.treasury)/4500),5,98);
  for(const [k,v] of Object.entries({workers:worker,merchants:merchant,homeowners:homeowner,public:publicv}))C.factions[k]=clamp(C.factions[k]*.88+v*.12,0,100);
  const avg=.31*C.factions.workers+.25*C.factions.merchants+.2*C.factions.homeowners+.24*C.factions.public;
  C.approval=clamp(C.approval*.85+avg*.15,5,97);
 }
 G.stats.approval=Math.round(C.approval);
 for(const m of AMBITIONS){if(G.achievements.includes(m.id))continue;let n=G.ambitionDays[m.id]||0;G.ambitionDays[m.id]=m.goal(G)?n+1:0;
  if(G.ambitionDays[m.id]>=m.days){G.achievements.push(m.id);let bonus=Math.min(m.reward,G.region*.5);G.treasury+=bonus;G.region-=bonus;G.council.approval=clamp(G.council.approval+3,0,100);story('AMBITION ACHIEVED: '+m.title+'. Regional development grant '+money(bonus)+'.','good');if(speed<=8)toast('Ambition complete: '+m.title+'!');save();}}
}
function privateInvestmentAndHousing(){assignJobs();}
function monthlyReview(){
 // External demand periodically contracts. Recovery is gradual; policy affects resilience through firm cash, taxes and trade.
 G.regionalDemand=clamp((G.regionalDemand||1)*.90+0.10+rn(-.035,.035),.42,1.22);
 if(G.day%180===0&&random()<.33){G.regionalDemand=clamp(G.regionalDemand-rn(.17,.34),.42,1.22);story('Regional buyers cut orders. Local mills, farms and shops brace for a trade slowdown.','bad');}
 const seasonal=G.month>=10||G.month<=2?['clear','clear','rain','storm']:G.month>=6&&G.month<=8?['clear','clear','clear','drought','rain']:['clear','clear','rain','rain','storm'];
 G.weather=weatherEnabled()?pick(seasonal):'clear';refreshAmbience();if(G.weather==='storm')story('Heavy rain and high winds are expected; fire and civil defence are on alert.','neutral');if(G.weather==='drought')story('A dry spell threatens harvest yields and local food output.','bad');
 if(random()<.22*(1-G.stats.militia/115)){let f=pick(G.firms.filter(f=>!f.closed&&f.cash>100));if(f){let stolen=Math.min(f.cash,rn(100,650));f.cash-=stolen;f.theft+=stolen;G.region+=stolen;G.council.factions.public=clamp(G.council.factions.public-2,0,100);story('A bandit raid targeted '+f.name+'; '+money(stolen)+' was stolen.','bad',f.building);}}
 let r={...G.stats,day:G.day,cash:G.treasury};G.lastMonth=r;
 if(G.treasury<5000){story('Treasurer warns: the council has less than $5,000 of uncommitted funds.','bad');}
 else if(G.stats.unemployment>30){story('Joblessness is above 30%; families are requesting employment assistance.','bad');}
 else if(G.stats.hardship<6&&G.stats.employment>75){story('The borough records a month of relatively steady work and low hardship.','good');}
 if(G.month===12)story('Year-end statements have been filed at the town hall.','neutral');
}
function electionReview(){
 G.council.elections++;let approved=G.council.approval>=50;const stamp='Year '+G.year+' election: '+(approved?'Council retains public confidence':'Council loses majority support')+' ('+Math.round(G.council.approval)+'% approval).';story(stamp,approved?'good':'bad');G.journal.push({day:G.day,name:'Municipal election',message:stamp,baseline:{...G.stats,treasury:G.treasury}});
 // Elections enter the permanent journal without interrupting unattended simulation.
 if(active==='agenda'||active==='journal')renderPanel(active);
}
function offerCouncilEvent(interrupt=false){
 // Ordinary correspondence belongs in the agenda, not in a blocking modal.
 // It is deliberately safe at 64×: the simulation never waits for a reply.
 let recent=G.recentCouncilEvents||[],pool=COUNCIL_EVENTS.filter(e=>!recent.includes(e.title));
 if(!pool.length)pool=COUNCIL_EVENTS;
 let event=pick(pool);G.recentCouncilEvents=recent.concat(event.title).slice(-6);G.lastEventDay=G.day;
 if(interrupt){showCustomEvent(event.type,event.title,event.text,event.choices);return;}
 G.councilInbox=Array.isArray(G.councilInbox)?G.councilInbox:[];
 G.councilInbox.unshift({title:event.title,day:G.day});
 G.councilInbox=G.councilInbox.slice(0,7);
 story('A council petition is waiting: '+event.title+'. Review it in the Agenda when convenient.','neutral');
}
function reviewCouncilInbox(index){
 const inbox=G.councilInbox||[],entry=inbox[index];if(!entry)return;
 const found=COUNCIL_EVENTS.find(e=>e.title===entry.title);
 if(!found)inbox.splice(index,1);
 if(found)showCustomEvent(found.type,found.title,found.text,found.choices);
 else story('An archived council petition is no longer actionable.','neutral');
 save();if(active==='agenda')renderPanel('agenda');
}

let councilOpener=null;
function closeCouncilDialog(defer=false){
 const event=pendingEvent;pendingEvent=null;$('eventDialog').style.display='none';
 if(defer&&event&&event.type!=='TOWN ARCHIVE'&&COUNCIL_EVENTS.some(e=>e.title===event.title)){G.councilInbox=G.councilInbox||[];if(!G.councilInbox.some(e=>e.title===event.title))G.councilInbox.unshift({title:event.title,day:G.day});}
 if(active==='agenda')renderPanel(active);save();
 const target=councilOpener?.isConnected?councilOpener:$('tabs').querySelector('[data-panel="agenda"]');target?.focus();councilOpener=null;
}
function showCustomEvent(type,title,text,choices){councilOpener=document.activeElement;pendingEvent={type,title,text,choices};
 $('eventEyebrow').textContent=type;$('eventTitle').textContent=title;$('eventText').textContent=text;
 $('eventChoices').innerHTML=choices.map((c,i)=>`<button data-event-choice="${i}" ${c.cost>0?'data-sound="coin"':''} ${c.cost&&G.treasury<c.cost?'disabled':''}><strong>${esc(c.title)}</strong><small>${esc(c.desc||'')}${c.cost?' · Cost: '+money(c.cost):''}</small></button>`).join('');
 if(type!=='TOWN ARCHIVE'&&COUNCIL_EVENTS.some(e=>e.title===title)){G.councilInbox=G.councilInbox||[];if(!G.councilInbox.some(e=>e.title===title))G.councilInbox.unshift({title,day:G.day});save();}
 $('eventDialog').style.display='flex';$('eventDefer').textContent=(type==='TOWN ARCHIVE'||type==='LAND PURCHASE')?'CANCEL':'DECIDE LATER';$('eventChoices').querySelector('button:not([disabled])')?.focus();
}
$('eventChoices').addEventListener('click',e=>{
 const b=e.target.closest('button[data-event-choice]');if(!b||!pendingEvent)return;
 const evt=pendingEvent,c=evt.choices[+b.dataset.eventChoice];if(!c)return;
 if(evt.type==='TOWN ARCHIVE'||evt.type==='LAND PURCHASE'){if(c.cost&&G.treasury<c.cost)return;closeCouncilDialog();c.apply();return;}
 const goodsBefore=stockTotals();const fundsBefore=totalMoney();if(c.cost){if(G.treasury<c.cost)return;G.treasury-=c.cost;G.region+=c.cost;G.cumulative.spending+=c.cost;}
 try{c.apply()}catch(ex){console.error('Council decision',ex)}
 const goodsAfter=stockTotals();for(const k of Object.keys(goods)){const delta=goodsAfter[k]-goodsBefore[k];goodsEntry(k,delta>=0?'imports':'consumed',Math.abs(delta));}
 const regionalFunding=totalMoney()-fundsBefore;G.region-=regionalFunding;if(Math.abs(regionalFunding)>.001)book(regionalFunding>0?'Regional capital':'Council settlement',regionalFunding>0?'Council decision beneficiaries':'Regional capital',Math.abs(regionalFunding),'Explicit council programme settlement');
 G.journal.push({day:G.day,name:evt.title,message:c.title+'. '+(c.desc||''),baseline:{...G.stats,treasury:G.treasury}});
 story('COUNCIL DECISION: '+c.title+' — '+evt.title,'neutral');G.councilInbox=(G.councilInbox||[]).filter(e=>e.title!==evt.title);closeCouncilDialog();recompute();updateHeader();if(active)renderPanel(active);save();dirty=true;
});
function totalMoney(){return G.treasury+G.region+(G.investors||[]).reduce((n,a)=>n+a.cash,0)+(G.metro?.cash||0)+(G.banks||[]).reduce((n,b)=>n+b.cash,0)+G.households.reduce((n,h)=>n+h.cash,0)+G.firms.reduce((n,f)=>n+f.cash,0)}
function investigateCases(){if(G.day%5!==0)return;const power=policePower();for(const item of G.cases.slice(0,30)){if(item.resolved||item.offender==null||item.loss<=0||G.day-item.day<3)continue;let age=G.day-item.day;if(age>50){item.resolved='cold';continue;}if(random()<(.025+power*.14)){let offender=G.households[item.offender];let victim=item.hid>=0?G.households[item.hid]:(G.firms[readBuild(item.bid)?.firm]);if(offender&&victim){let recovered=Math.min(offender.cash,item.loss*(.30+power*.45));if(recovered>0){offender.cash-=recovered;victim.cash+=recovered;if(item.hid<0){victim.revenue+=recovered;victim.nonSalesIncome=(victim.nonSalesIncome||0)+recovered;victim.recoveries=(victim.recoveries||0)+recovered;}else victim.recoveredLosses=(victim.recoveredLosses||0)+recovered;}item.recovered=Math.round(recovered);item.resolved=true;story('Constabulary concluded an investigation; '+money(recovered)+' was recovered for the victim.','good',item.bid,item.hid);}}}}
function yearlyDemographics(){
 let deaths=0;
 for(const p of G.people){
  if(p.deceased||p.movedAway)continue;p.age++;if(p.age>70&&p.job>=0){const f=G.firms[p.job];if(f)f.workers=f.workers.filter(id=>id!==p.id);p.job=-1;p.retired=true;p.publicWork=false;}
  if(p.age>85&&(p.age>95||random()<.17)){
   p.deceased=true;p.job=-1;
   const h=G.households[p.hh];if(h)h.people=h.people.filter(id=>id!==p.id);
   for(const f of G.firms)f.workers=f.workers.filter(id=>id!==p.id);
   deaths++;
  }
 }
 if(deaths)story(deaths+' elderly residents passed away this year. Their families will remember them.','neutral');
 // Vacant homes can receive a new household from outside town. Do not clone
 // an existing resident into two household rosters, and keep external cash balanced.
 for(const h of G.households){
  if(h.people.length||!readBuild(h.home)||G.stats.population>=2000||G.region<1000||cityDemand().housingPressure<48)continue;
  const building=readBuild(h.home),newHousehold=addHouseholdAt(building,900);
  if(newHousehold){if(building.hh===h.id)building.hh=newHousehold.id;if(Array.isArray(building.units))building.units=building.units.map(id=>id===h.id?newHousehold.id:id);h.home=-1;story('A newcomer household rented an empty home; the former estate retains its balances and title.','neutral',building.id,newHousehold.id);}

 }
 assignJobs();
}

function updateObjectiveMini(){if(!G)return;let m=AMBITIONS.find(m=>m.id===G.ambition)||AMBITIONS[0],days=G.ambitionDays[m.id]||0,p=m.progress(G);
 if(G.achievements.includes(m.id))p=1;else if(m.goal(G))p=Math.min(1,days/m.days);
 headerText('objectiveName',m.title);$('objectiveProgress').style.width=(100*clamp(p,0,1))+'%';
 const h=G.events[0];if(h){headerText('headline',h.text);}
 if(G.roadMetrics&&G.roadMetrics.connectedFirms<G.roadMetrics.totalFirms){headerText('headline','Road access warning: '+(G.roadMetrics.totalFirms-G.roadMetrics.connectedFirms)+' local businesses are cut off from town freight.');}
}

$('eventDefer').onclick=()=>closeCouncilDialog(true);
$('eventDialog').addEventListener('keydown',e=>{
 if(e.key!=='Tab')return;const controls=[...$('eventDialog').querySelectorAll('button:not([disabled])')];const first=controls[0],last=fromEnd(controls);
 if(e.shiftKey&&document.activeElement===first){last.focus();e.preventDefault();}else if(!e.shiftKey&&document.activeElement===last){first.focus();e.preventDefault();}
});

// SOURCE: 90-archive-panels.js
function hydrateSave(raw){
 const previousTown=G;
 try{let data=typeof raw==='string'?JSON.parse(raw):raw;data=normalizeRegionArchive(data);
  if(!data||![2,3].includes(data.version)||!Array.isArray(data.tiles)||data.tiles.length!==T*T||!Array.isArray(data.firms)||!Array.isArray(data.people)||!Array.isArray(data.buildings)||!Array.isArray(data.households)||!data.policy||!Number.isFinite(data.treasury)||data.tiles.some(t=>!Number.isInteger(t)||t<0||t>3)||!Number.isFinite(data.region)||data.region<0||data.households.length>3000||data.people.length>8000||data.firms.length>3000)return false;
  if(data.schema!=null&&(!Number.isInteger(data.schema)||data.schema<0||data.schema>6))return false;
  if(data.investors&&(!Array.isArray(data.investors)||data.investors.length!==1||data.investors.some(a=>!Number.isFinite(a.cash)||a.cash<0)))return false;
  if(data.freight&&(!Array.isArray(data.freight)||data.freight.length>10000||data.freight.some(s=>!Number.isInteger(s.from)||!data.firms[s.from]||!Number.isInteger(s.to)||!data.firms[s.to]||!owns(goods,s.good)||!Number.isFinite(s.qty)||s.qty<=0||!Number.isFinite(s.remaining))))return false;
  // Reject structurally broken saves before they can replace the running town.
  // These checks also protect long-playing towns from partial imports and invalid IDs.
  if(!Array.isArray(data.homes)||!Array.isArray(data.projects??[])||
     !data.buildings.every(b=>b&&Number.isInteger(b.id)&&b.id>0&&types[b.kind]&&Number.isInteger(b.x)&&Number.isInteger(b.y)&&b.x>=0&&b.x<T&&b.y>=0&&b.y<T&&Number.isFinite(b.value)&&Number.isFinite(b.condition))||
     !data.people.every((p,i)=>p&&p.id===i&&Number.isInteger(p.hh)&&p.hh>=0&&p.hh<data.households.length&&Number.isFinite(p.age))||
     !data.households.every((h,i)=>h.id===i&&h.people.every(id=>Number.isInteger(id)&&id>=0&&id<data.people.length))||
     !data.firms.every((f,i)=>f.id===i&&Number.isInteger(f.building)&&Number.isFinite(f.jobs)&&f.workers.every(id=>Number.isInteger(id)&&id>=0&&id<data.people.length)))return false;
  const addressSet=new Set(),idSet=new Set(),memberSet=new Set();
  for(const b of data.buildings){const cells=Array.isArray(b.footprint)&&b.footprint.length?b.footprint:[b.y*T+b.x];
   if(cells.length>36||new Set(cells).size!==cells.length||!cells.includes(b.y*T+b.x))return false;
   for(const plot of cells){if(!Number.isInteger(plot)||plot<0||plot>=T*T||addressSet.has(plot)||data.tiles[plot]===1||data.tiles[plot]===2||data.landUse?.[plot])return false;addressSet.add(plot);}
   if(idSet.has(b.id))return false;idSet.add(b.id);
  }
  for(const h of data.households)for(const id of h.people){if(memberSet.has(id)||data.people[id].hh!==h.id||data.people[id].deceased||data.people[id].movedAway)return false;memberSet.add(id)}
  if(!validateWaterfrontArchive(data)||!validateGoodsAccounting(data))return false;
  if(!validateCivicState(data)||!validateCreditState(data)||!validateScenarioProgramme(data)||!validateCharter(data))return false;
  data.version=3;data.policy={...defaults,...data.policy};
  data.banks=Array.isArray(data.banks)?data.banks.filter(b=>b&&Number.isInteger(b.id)&&b.id>=0&&b.id<12&&Number.isFinite(b.cash)&&b.cash>=0&&Number.isFinite(b.depositAPY)&&Number.isFinite(b.loanAPY)).slice(0,12):[];
  data.loans=Array.isArray(data.loans)?data.loans.filter(l=>l&&Number.isInteger(l.id)&&Number.isFinite(l.balance)&&l.balance>=0&&['active','repaid','default'].includes(l.status)).slice(0,10000):[];
  if(new Set(data.banks.map(b=>b.id)).size!==data.banks.length||data.banks.some((b,i)=>b.id!==i))return false;
  const loanIDs=new Set();for(const l of data.loans){if(loanIDs.has(l.id)||!['household','firm'].includes(l.ownerType)||!Number.isInteger(l.ownerId)||!Number.isInteger(l.bankId)||!Number.isFinite(l.rate)||l.rate<0||l.balance<0)return false;loanIDs.add(l.id);if(l.ownerType==='household'&&!data.households[l.ownerId]||l.ownerType==='firm'&&!data.firms[l.ownerId]||l.bankId>=data.banks.length)return false;}
  data.nextLoanId=Math.max(Number.isSafeInteger(data.nextLoanId)?data.nextLoanId:0,...data.loans.map(l=>l.id),0);
  data.finance={failures:0,businessDefaults:0,householdDefaults:0,creditIssued:0,depositLosses:0,insuredPayouts:0,foreclosures:0,downzonings:0,insolvencies:0,bankRuns:0,...(data.finance||{})};data.council=data.council||{approval:60,elections:0,factions:{workers:60,merchants:60,homeowners:60,public:60}};
  data.council.factions=data.council.factions||{workers:60,merchants:60,homeowners:60,public:60};data.achievements=data.achievements||[];data.ambition=data.ambition||'balanced';data.ambitionDays=data.ambitionDays||{};data.lastMonth=data.lastMonth||{};data.crisesHandled=data.crisesHandled||0;data.policyOutcomes=data.policyOutcomes||[];data.construction=data.construction||0;data.worldSeed=data.worldSeed||101;data.weather=data.weather||'clear';data.education=data.education||46;data.health=data.health||74;data.lastEventDay=data.lastEventDay||1;data.regionalDemand=data.regionalDemand||1;data.recentCouncilEvents=data.recentCouncilEvents||[];data.unrest=data.unrest||0;data.scenario=data.scenario||'settlement';data.stats=data.stats||{};data.history=data.history||[];data.journal=data.journal||[];data.events=data.events||[];data.cases=data.cases||[];data.cumulative={incomeTax:0,profitTax:0,propertyTax:0,foodTax:0,utilityTax:0,commercialRate:0,permits:0,tariffs:0,spending:0,crime:0,fires:0,welfare:0,...data.cumulative};
  data.debt=Number.isFinite(data.debt)?Math.max(0,data.debt):0;data.publicReserve=Number.isFinite(data.publicReserve)?Math.max(0,data.publicReserve):0;
  data.projects=Array.isArray(data.projects)?data.projects.filter(p=>p&&Number.isInteger(p.id)&&Number.isFinite(p.remaining)&&p.remaining>0).slice(0,1000):[];
  data.metro=data.metro||{cash:0,stations:[],lines:[],fare:2.75,rides:0,revenue:0,expenses:0,dailyRides:0,daysInDeficit:0,operating:false,invested:0};
  data.development=data.development||{homes:0,firms:0,roads:0,stations:0,lastReport:null,decisions:[]};data.privateRoads=Array.isArray(data.privateRoads)?data.privateRoads.filter(id=>Number.isInteger(id)&&id>=0&&id<T*T&&data.tiles[id]===1):[];
  data.autoBuild=data.autoBuild!==false;data.landUse=(data.landUse&&typeof data.landUse==='object'&&!Array.isArray(data.landUse))?data.landUse:{};data.fieldOwner=(data.fieldOwner&&typeof data.fieldOwner==='object'&&!Array.isArray(data.fieldOwner))?data.fieldOwner:{};data.fieldCount={};for(const [id,code] of Object.entries(data.landUse)){if(!/^\d+$/.test(id)||+id>=T*T||![1,2,3].includes(code)||data.tiles[+id]!==0){delete data.landUse[id];delete data.fieldOwner[id];continue}if(code===1){const owner=data.fieldOwner[id];if(!Number.isInteger(owner)||!data.firms[owner]||data.firms[owner].kind!=='farm'){delete data.landUse[id];delete data.fieldOwner[id]}else data.fieldCount[owner]=(data.fieldCount[owner]||0)+1;}}data.airport=data.airport&&Number.isInteger(data.airport.building)&&Array.isArray(data.airport.runway)?data.airport:null;data.development={fields:0,redevelopments:0,towers:0,airfields:0,...data.development};
  if(!Number.isFinite(data.metro.cash)||data.metro.cash<0||!Array.isArray(data.metro.lines)||!Array.isArray(data.metro.stations)||data.metro.stations.length>120||data.metro.lines.length>120)return false;
  for(const d of defs){const k=d[0],v=Number(data.policy[k]);data.policy[k]=clamp(Number.isFinite(v)?v:defaults[k],d[2],d[3]);}
  data.policy.imports=data.policy.imports!==false;
  if(data.households.some(h=>!h||!Array.isArray(h.people)||!Number.isFinite(h.cash)||h.cash<0)||data.firms.some(f=>!f||!Array.isArray(f.workers)||!Number.isFinite(f.cash)||f.cash<0))return false;
  const workerIDs=new Set();for(const f of data.firms){for(const id of f.workers){if(workerIDs.has(id)||!data.people[id]||data.people[id].deceased||data.people[id].movedAway||data.people[id].job!==f.id)return false;workerIDs.add(id)}}
  for(const loan of data.loans||[])if(loan.fixedRate==null)loan.fixedRate=true;
  G=data;resetTownTransientUI();G.serviceProvision=null;crewDay=-1;crewsUsed=new Map();regionalCrews=0;ensureSystems();rngState=Number.isInteger(G.rngState)?G.rngState:G.scenarioSeed;ensureFinance();ensureMarketModel();if(!G.banks.length)seedBanks();draftPolicy={};roadBatchDirty=false;invalidateRoads();cacheBuildingsFor=null;recompute();G.stats.approval=Math.round(G.council.approval);G.stats.health=Math.round(G.health);G.stats.education=Math.round(G.education);G.stats.marketConfidence=G.stats.marketConfidence||55;G.stats.wellbeing=G.stats.wellbeing??70;ensureScenarioProgramme();if(!previousTown)centerTownCamera();restoreTransport();staticDirty=true;dirty=true;updateHeader();beginSaveTimeline();return true;
 }catch(e){G=previousTown;invalidateRoads();cacheBuildingsFor=null;staticDirty=true;dirty=true;console.error('Invalid save',e);return false}
}
function writeIndexedDB(envelope,epoch){
 return new Promise(resolve=>{let settled=false,db=null;const finish=ok=>{if(settled)return;settled=true;clearTimeout(timer);if(db)db.close();resolve(ok)},timer=setTimeout(()=>finish(false),2500);
  try{const req=indexedDB.open('townledger-save',1);req.onupgradeneeded=()=>{if(!req.result.objectStoreNames.contains('saves'))req.result.createObjectStore('saves')};req.onerror=req.onblocked=()=>finish(false);
   req.onsuccess=()=>{db=req.result;if(settled||epoch!==saveEpoch){db.close();finish(false);return}try{const tx=db.transaction('saves','readwrite'),store=tx.objectStore('saves'),read=store.get('latest');let wrote=false;
    read.onsuccess=()=>{if(settled||epoch!==saveEpoch){tx.abort();return}const current=readSaveEnvelope(read.result);if(current&&current.order>=envelope.order&&current.checksum!==envelope.checksum){try{promoteSaveEnvelope(envelope,current.order)}catch(_){tx.abort();return}}store.put(envelope,'latest');wrote=true;};
    tx.oncomplete=()=>{if(wrote&&epoch===saveEpoch){saveCandidates=[envelope];window.__idbSave=envelope.payload;}finish(wrote)};tx.onerror=tx.onabort=()=>finish(false);
   }catch(_){finish(false)}};
  }catch(_){finish(false)}
 });
}
function discoverIndexedDB(){
 const epoch=saveEpoch;
 return new Promise(resolve=>{let settled=false,db=null;const finish=()=>{if(settled)return;settled=true;clearTimeout(timer);if(db)db.close();saveStoreReady=true;resolve()},timer=setTimeout(finish,2500);
  for(const e of localSaveCandidates())observeSaveOrder(e);
  try{const req=indexedDB.open('townledger-save',1);req.onupgradeneeded=()=>{if(!req.result.objectStoreNames.contains('saves'))req.result.createObjectStore('saves')};req.onerror=req.onblocked=finish;
   req.onsuccess=()=>{db=req.result;if(settled){db.close();return}try{const tx=db.transaction('saves'),read=tx.objectStore('saves').get('latest');read.onsuccess=()=>{const raw=read.result;let e=readSaveEnvelope(raw);
    // Earlier editions stored an unwrapped archive string in IndexedDB.
    if(!e&&typeof raw==='string'){try{const t=JSON.parse(raw);if(t&&Array.isArray(t.tiles)&&Array.isArray(t.people))e={payload:raw,checksum:checksum(raw),order:0,town:'',revision:0}}catch(_){}}
    if(e){observeSaveOrder(e);if(epoch===saveEpoch){saveCandidates=[e];window.__idbSave=e.payload;$('continue').style.display='block'}}};tx.oncomplete=finish;tx.onerror=tx.onabort=finish;
   }catch(_){finish()}};
  }catch(_){finish()}
 });
}
saveStorePromise=discoverIndexedDB();
let helpOpener=null;
function hideHelpDialog(){
 $('helpDialog').style.display='none';restoreHelpMarkup();
 if(helpOpener?.isConnected)helpOpener.focus();
 helpOpener=null;
}
function openTutorialDialog(opener=document.activeElement){helpOpener=opener;$('helpDialog').style.display='flex';$('helpClose').focus()}
function exportSave(){
 const text=archivePayload();const dialog=$('helpDialog');helpOpener=document.activeElement;dialog.querySelector('.paper').innerHTML=`<h2 id="helpTitle">YOUR TOWN ARCHIVE</h2><p>Copy this backup into a text file. Paste it here later to restore the village, even after reinstalling.</p><textarea id="saveText" style="display:block;width:100%;height:145px;background:#f7efd9;color:#183425;font:11px monospace;touch-action:pan-y;border:1px solid #8a8c6c;padding:9px"></textarea><button id="copySave" class="menu-primary">SELECT AND COPY</button><button id="archiveClose">CLOSE</button>`;dialog.style.display='flex';$('saveText').value=text;$('saveText').focus();$('copySave').onclick=()=>{$('saveText').focus();$('saveText').select();try{document.execCommand('copy')}catch(e){};toast('Backup text selected for copying.')};$('archiveClose').onclick=hideHelpDialog;
}
function importSave(){const dialog=$('helpDialog');helpOpener=document.activeElement;dialog.querySelector('.paper').innerHTML=`<h2 id="helpTitle">RESTORE A TOWN</h2><p>Paste a TownLedger backup below. Your current game will be replaced after validation.</p><textarea id="importText" style="display:block;width:100%;height:145px;background:#f7efd9;color:#183425;font:11px monospace;touch-action:pan-y;border:1px solid #8a8c6c;padding:9px"></textarea><button id="restoreGo" class="menu-primary">RESTORE THIS TOWN</button><button id="restoreCancel">CANCEL</button>`;dialog.style.display='flex';$('importText').focus();$('restoreGo').onclick=()=>{if(hydrateSave($('importText').value)){centerTownCamera(.68);save();dialog.style.display='none';restoreHelpMarkup();toast('Town archive restored.');renderPanel('overview');$('tabs').querySelector('button[data-panel="overview"]')?.focus();helpOpener=null;}else toast('The backup is invalid or incompatible.')};$('restoreCancel').onclick=hideHelpDialog;}
const originalHelp=$('helpDialog').querySelector('.paper').innerHTML;
function restoreHelpMarkup(){$('helpDialog').querySelector('.paper').innerHTML=originalHelp;$('helpClose').onclick=hideHelpDialog}
$('helpClose').onclick=hideHelpDialog;$('howTo').onclick=()=>openTutorialDialog($('howTo'));
$('helpDialog').addEventListener('keydown',e=>{
 if(e.key!=='Tab'||$('helpDialog').style.display==='none')return;
 const items=[...$('helpDialog').querySelectorAll('button:not([disabled]),textarea:not([disabled]),input:not([disabled]),select:not([disabled]),[href],[tabindex]:not([tabindex="-1"])')].filter(el=>el.offsetParent!==null);
 if(!items.length)return;
 const first=items[0],last=items[items.length-1];
 if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}
 else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}
});
$('scenarioPicker').addEventListener('click',e=>{let b=e.target.closest('[data-scenario]');if(!b)return;chosenScenario=b.dataset.scenario;document.querySelectorAll('[data-scenario]').forEach(v=>v.classList.toggle('chosen',v===b))});

function enterContinuedTown(){centerTownCamera();invalidateRoads();paused=false;speed=SPEED_PRESETS.includes(G.speed)?G.speed:1;acc=0;fit();$('welcome').style.display='none';dirty=true;staticDirty=true;updateHeader();openPanel('overview');}
function legacyRecoveryChoices(){
 const local=localSaveCandidates()[0],indexed=saveCandidates[0];
 if(!local||!indexed||local.format===1||indexed.format===1||local.payload===indexed.payload)return null;
 // Old editions recorded neither timeline identity nor save order. Different days
 // cannot establish which town the player founded/restored most recently.
 return [{label:'Local autosave',e:local},{label:'Secondary on-device copy',e:indexed}];
}
// Read both stores before choosing a snapshot; simulation day is not save chronology.
$('continue').onclick=async()=>{const epoch=saveEpoch,button=$('continue');button.disabled=true;try{await saveStorePromise;if(epoch!==saveEpoch)return;
 const legacy=legacyRecoveryChoices();if(legacy){showCustomEvent('TOWN ARCHIVE','Choose a recovered town','These older copies differ and contain no save chronology. A higher simulation day does not mean a more recent save. Choose the copy you recognise, or cancel without changing either.',legacy.map(({label,e})=>{let data;try{data=JSON.parse(e.payload)}catch(_){data={}}return {title:label,desc:'Day '+(data.day??'?')+' · '+(data.scenario||'legacy town')+' · '+(data.people?.length??'?')+' resident records',apply:()=>{if(restoreSaveEnvelope(e)){enterContinuedTown();save()}else toast('That copy is invalid. Try the other recovery copy.')}}}));return;}
 if(!load()){toast('No valid town could be recovered. Found a new town or restore a backup.');return}enterContinuedTown();
 }finally{button.disabled=false}};
function tip(s){return `<p class="desc">${esc(s)}</p>`}
function strip(label,value){return `<div class="line"><span>${esc(label)}</span><span>${esc(String(value))}</span></div>`}
function meter(label,value,color='#d5b779'){return `<div class="line"><span>${esc(label)}</span><span><b>${Math.round(value)}%</b></span></div><div class="progress"><i style="width:${clamp(value,0,100)}%;background:${color}"></i></div>`}
function greeting(){if(!seasonsEnabled())return 'Your council, your growing town';return G.month<4?'A quiet spring morning in the Vale':G.month<7?'High summer and hard work':G.month<10?'Harvest season in the borough':'Winter settles on the cobbled lanes'}
function miniChart(k,height=130){let ar=(G.history||[]).slice(-120);if(ar.length<2)return tip('The figures will appear as the town develops.');let vals=ar.map(o=>Number(o[k])||0),lo=Math.min(...vals),hi=Math.max(...vals),span=Math.max(1,hi-lo);let points=vals.map((v,i)=>`${(i/(vals.length-1)*330).toFixed(1)},${(height-20-(v-lo)/span*(height-35)).toFixed(1)}`).join(' ');return `<svg class="chart-lines" viewBox="0 0 330 ${height}" preserveAspectRatio="none"><path d="M0 ${height-20}H330 M0 ${height/2}H330 M0 18H330" stroke="#627563" stroke-width=".6" fill="none"/><polyline points="${points}" fill="none" stroke="#e8c887" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg><div class="desc">Past ${ar.length} days · low ${fmt(lo)} · high ${fmt(hi)} · latest ${fmt(vals[vals.length-1])}</div>`}
function headlineList(count=7){let ev=G.events.slice(0,count);return ev.map(e=>`<div class="event" style="border-left-color:${e.type==='bad'?'#e99a80':e.type==='good'?'#9fd4ab':'#c0ab7e'}"><strong>DAY ${e.day}</strong><div>${esc(e.text)}</div>${e.bid>0?`<button class="small" data-inspect="${e.bid}">Visit location</button>`:''}</div>`).join('')}
function currentAmbition(){return AMBITIONS.find(m=>m.id===G.ambition)||AMBITIONS[0]}
function ambitionCard(m,compact=false){let achieved=G.achievements.includes(m.id),days=G.ambitionDays[m.id]||0,selected=G.ambition===m.id,progress=achieved?1:m.goal(G)?days/m.days:Math.min(.95,m.progress(G)*.85);return `<div class="mission-item ${selected?'selected':''}" data-ambition="${m.id}"><div style="display:flex;align-items:center;justify-content:space-between;gap:10px"><b>${esc(m.title)}</b><span class="pill">${achieved?'ACHIEVED':selected?'TRACKING':'SELECT'}</span></div>${compact?'':`<small>${esc(m.description)}</small>`}<div class="progress"><i style="width:${Math.round(clamp(progress,0,1)*100)}%"></i></div><small>${achieved?'Completed · grant awarded':(m.goal(G)?days+' / '+m.days+' qualifying days':'Conditions not yet sustained')}${compact?'':' · Development grant '+money(m.reward)}</small></div>`}
function scenarioBriefing(){
 const signal=marketSignal();let context;
 if(G.scenario==='hardtimes')context=G.day<540?`Regional export orders remain at 52% of normal for ${540-G.day} more days. Local customers still matter: review firms’ sales, inventories and cash before changing taxes or credit. Employment can recover before exports do.`:'The opening export shock has ended. Check whether families and firms have rebuilt their cash buffers before expanding commitments.';
 else if(G.scenario==='frontier')context=G.day<280?`Regional export orders remain at 78% for ${280-G.day} more days. A small tax base makes new recurring spending consequential; inspect Budget before promising more services.`:'The opening export constraint has ended. Compare recurring service costs with the tax base as the community grows.';
 else if(G.scenario==='regional')context='Market Cross begins with a strong job market. Its opening ambition is lasting health and education, so jobs alone do not complete your council programme. A dense regional town also needs connected employers and housing. Check journey lengths, road access and household expenses before financing additional public works.';
 else context='Choose an ambition, inspect the constraint in Economy, and enact a small policy package. Let several weeks pass, then compare the Policy journal and individual household accounts.';
 return `<div class="council-card scenario-briefing"><h3>${esc(signal.title)}</h3><p class="desc">${esc(context)}</p><p class="desc">${esc(signal.description)}</p><div class="btnrow"><button data-open-panel="community">Review local services</button><button data-open-panel="economy">Review the economy</button><button data-open-panel="policies">Prepare policy</button><button data-open-panel="journal">Review outcomes</button></div></div>`;
}
function renderOverviewFull(){let s=G.stats,m=currentAmbition(),C=G.council;return `<div class="scenario-badge">${G.scenario==='settlement'?'PROSPEROUS VALE':G.scenario==='hardtimes'?'HARD TIMES':G.scenario==='frontier'?'THE FRONTIER':G.scenario==='regional'?'MARKET CROSS':'FACTORY COUNTRY'} · ${esc(greeting())}</div>`+
 head('The borough at a glance')+`<div class="statgrid">${stat('Residents',fmt(s.population))}${stat('Town treasury',money(G.treasury),G.treasury<5000?'negative':'')}${stat('Residents in work',s.employment+'%',s.employment<60?'negative':'')}${stat('Council trust',Math.round(C.approval)+'%',C.approval<45?'negative':'')}</div>`+
 scenarioBriefing()+head('The state of daily life')+meter('Public safety',s.safety,s.safety>80?'#a9d7ad':'#d9ad7b')+meter('Household wellbeing',s.wellbeing??70)+meter('Local business confidence',s.marketConfidence??60)+strip('Households struggling',s.hardship+'%')+strip('Crime reports in last month',s.dailyCrime)+strip('Trading businesses',s.businesses+' / '+G.firms.length)+
 `<div class="council-card"><h3>Current ambition: ${esc(m.title)}</h3><p class="tip">${esc(m.description)}</p>${ambitionCard(m,true)}<div class="btnrow"><button id="jumpAgenda">View council ambitions</button><button id="focusBad">Visit struggling household</button></div></div>`+
 head('A household behind the numbers')+(()=>{let h=G.households.filter(h=>h.people.length>0&&readBuild(h.home)).sort((a,b)=>b.stress-a.stress)[0];if(!h)return '';let net=h.income-h.tax-h.food-h.rent-(h.utilities||0)-(h.travel||0)-(h.debtService||0)-(h.propertyPaid||0)-(h.discretionary||0)-(h.propertyMaintenance||0)-(h.crimeLossToday||0)+(h.recoveredLosses||0)+h.aid;return `<div class="council-card"><h3>The ${esc(h.name)} family</h3><p class="desc">${h.people.length} residents · ${money(h.cash)} in savings · ${(100-h.stress).toFixed(0)}/100 wellbeing. Yesterday's income ${money(h.income)}, essential spending ${money(h.food+h.rent+(h.utilities||0)+(h.travel||0))}, net household flow ${money(net)}.</p><button data-house="${h.id}">Inspect this family</button></div>`})()+
 ((G.councilInbox||[]).length?`<div class="inbox-notice"><strong>✉ ${(G.councilInbox||[]).length} council letter(s)</strong><button id="jumpAgenda">Review when ready</button></div>`:'')+head('From the town crier')+headlineList(6)+head('Employment trend')+miniChart('employment');}
function renderAgenda(){let C=G.council,days=360-(G.day%360),completed=G.achievements.length;return head('The council chamber')+`<div class="statgrid">${stat('Approval',Math.round(C.approval)+'%',C.approval<45?'negative':'positive')}${stat('Days until election',days)}${stat('Elections held',C.elections)}${stat('Ambitions fulfilled',completed+' / '+AMBITIONS.length)}</div>`+
 tip('Council approval changes in response to employment, household finances, safety, taxation and business conditions. Each constituency weighs these outcomes differently.')+
 head('Four voices of the town')+meter('Working families',C.factions.workers,'#a6c8c1')+meter('Merchants & employers',C.factions.merchants,'#d6b779')+meter('Property owners',C.factions.homeowners,'#d5a17f')+meter('Public services & safety',C.factions.public,'#9acc9a')+
 head('Town ambitions')+tip('Choose one ambition to track. All '+AMBITIONS.length+' can be completed over a long playthrough. Awards provide small, finite grants from the region rather than creating money.')+AMBITIONS.map(m=>ambitionCard(m)).join('')+
 head('Council correspondence')+tip('Letters, petitions and dilemmas arrive in the inbox without stopping the town. Review them on your own schedule, or let the economy run unattended at any speed.')+
 ((G.councilInbox||[]).length?G.councilInbox.map((item,i)=>`<div class="council-card inbox-letter"><small class="letter-day">RECEIVED DAY ${item.day}</small><h3>${esc(item.title)}</h3><button data-inbox="${i}">Review and decide</button></div>`).join(''):'<p class="desc">No correspondence is waiting. The town continues operating on its own.</p>')+
 `<div class="btnrow"><button id="convene" ${G.day-G.lastEventDay<12?'disabled':''}>Request council meeting</button><button id="jumpJournal">Open policy journal</button></div>`;
}
function serviceProvisionPanel(){
 if(!G.serviceProvision)return tip('Service provision is recorded after the next simulated day. Budgets authorize spending; buildings and paid operating costs determine coverage.')+civicTrainingPanel();
 return ['health','school'].map(kind=>{const p=G.serviceProvision[kind];if(!p)return '';const coverage=Math.round(p.coverage*100),capacity=Math.round(p.facilityCoverage*100),bottleneck=p.accessCoverage<p.facilityCoverage-.001?'Road access or catchment places limit reach. Connect homes and facilities or build closer provision.':p.paid<p.requested-.01?'Treasury cash was insufficient for the proposed service.':p.staffing.coverage<Math.min(p.accessCoverage,p.authorized/Math.max(1,p.required))-.001?'Qualified staff capacity is limiting provision. Regional recruitment takes 30 days; funded training builds local qualifications.':p.authorized/Math.max(1,p.required)<p.accessCoverage-.001?'The allocation limits funded staffing and supplies. Expansion may require regional recruitment.':p.facilityCoverage<1?'Facility capacity limits coverage. Additional budget cannot replace a clinic or school.':'Current resident coverage is fully funded.';
 return `<div class="council-card service-provision"><h3>${kind==='health'?'Medical provision':'Schools and training'} · ${coverage}% coverage</h3><p class="desc">${esc(bottleneck)}</p><div class="btnrow"><button data-service-access="${kind}">Show access map</button><button data-service-policy="${kind}">Review operating budget</button></div>${strip('Actual purchases / day',money(p.paid))}${strip('Reachable places',Math.round(p.accessCoverage*100)+'% of residents')}<details><summary>Operating plan and staffing</summary>${strip('Authorized ceiling / day',money(p.authorized))}${strip('Retained authorization',money(p.unspent))}${strip('Full-town operating need / day',money(p.required))}${strip('Facility capacity',capacity+'% of residents')}${strip('Road catchment',p.accessLimit+' segments')}${strip('Available qualified local staff',policyNumber(p.staffing.local)+' equivalents')}${strip('Regional staff capacity',policyNumber(p.staffing.regional)+' equivalents')}${p.staffing.pending?strip('Recruitment review due','Day '+p.staffing.pending.day):''}${strip('Qualification standard',Math.round(p.staffing.qualification*100)+'/100 skill, health 60+')}<p class="desc">Planning standard: ${kind==='health'?'5 clinic teams per 350 residents':'10 school staff per 260 residents'}, priced at ${money(p.wage)} per staff-day with 65% payroll. Public wages and regional staff/supply purchases use the same funded payment. Coverage changes health and education gradually.</p></details></div>`;
 }).join('')+civicTrainingPanel();
}
function renderCommunityFull(){let s=G.stats;return head('Local care and learning')+serviceProvisionPanel()+head('Private growth and mobility')+developmentPanel()+head('Banking & enterprise finance')+strip('Competing banks',G.banks.filter(b=>!b.closed).length+' operating')+strip('Outstanding bank credit',money(G.loans.filter(l=>l.status==='active').reduce((n,l)=>n+l.balance,0)))+head('Constabulary & civil defence')+`<div class="statgrid">${stat('Public safety',s.safety+'/100')}${stat('Crime reports · 30 days',s.dailyCrime)}${stat('Emergency readiness',s.preparedness+'%')}${stat('Residents in hardship',s.hardship+'%')}</div>`+
 tip('Incidents affect named residents and firms. Police staffing and funding reduce risk; underfunded emergency services leave properties more exposed to fire and storm damage.')+
 head('People, health and schools')+`<div class="statgrid">${stat('Public health',Math.round(G.health)+'/100')}${stat('Education level',Math.round(G.education)+'/100')}${stat('Wellbeing',s.wellbeing+'/100')}${stat('Community security',s.safety+'/100')}</div>`+
 head('Road network and emergency reach')+strip('Pavement condition',Math.round(G.stats.roadCondition??100)+' / 100')+strip('Main road-network tiles',roadMetrics().roadTiles)+strip('Disconnected road clusters',Math.max(0,roadMetrics().roadClusters-1))+strip('Firms connected to town',roadMetrics().connectedFirms+' / '+roadMetrics().totalFirms)+strip('Funded road maintenance',Math.round((G.actualServiceFunding?.roads??1)*100)+'% of budget')+`<div class="btnrow"><button id="overlayR">${overlay==='roads'?'✓ ':''}Road-access map</button></div>`+head('Funded services')+strip('Actual patrol budget paid',Math.round((G.actualServiceFunding?.police??1)*100)+'% of authorized')+strip('Actual fire budget paid',Math.round((G.actualServiceFunding?.fire??1)*100)+'% of authorized')+strip('Constabulary per day',money(G.policy.policeBudget))+strip('Fire & rescue per day',money(G.policy.defenseBudget))+strip('Medical services per day',money(G.policy.healthBudget))+strip('Schools & training per day',money(G.policy.educationBudget))+strip('Civil defence volunteers',money(G.policy.militiaBudget))+strip('Household relief per day',money(G.policy.aidBudget))+strip('Heating assistance',money(G.policy.energyAidBudget||0))+strip('Commuter transit',money(G.policy.transitBudget||0))+
 `<div class="btnrow"><button id="overlayC">${overlay==='crime'?'✓ ':' '}Crime map</button><button id="overlayH">${overlay==='hardship'?'✓ ':' '}Hardship map</button></div>`+
 head('Constabulary incident log')+(G.cases.length?G.cases.slice(0,15).map(eventHtml).join(''):tip('No recorded incidents. This does not mean risk is zero.'))+
 head('Safety across time')+miniChart('safety');}
function renderPoliciesFull(){let sections=[['Taxation','incomeTax','profitTax','propertyTax','commercialRate','foodTax','utilityTax'],['Work and enterprise','minWage','employmentSubsidy','permitFee','businessRegulation','zoningRestriction'],['Government services','pensionDaily','policeBudget','defenseBudget','healthBudget','educationBudget','aidBudget','energyAidBudget','outreachBudget','roadBudget','transitBudget','militiaBudget'],['Monetary policy and credit','policyRate','bankReserve','lendingRules','depositGuarantee','treasuryInvestment'],['Trade and exchange','importTariff']];let changes=Object.keys(draftPolicy).filter(k=>draftPolicy[k]!==G.policy[k]);let projected=defs.filter(d=>changes.includes(d[0])).map(d=>`${d[1]}: ${policyNumber(G.policy[d[0]])} → ${policyNumber(draftPolicy[d[0]])}${d[5]==='$'?' dollars':d[5]}`).join('<br>');if(changes.includes('imports'))projected+=(projected?'<br>':'')+'Regional inventory imports: '+(G.policy.imports?'OPEN':'RESTRICTED')+' → '+(draftPolicy.imports?'OPEN':'RESTRICTED');
 return `<div class="notice-banner" style="background:#3b4b36;border-color:#938459">The market runs itself. You set rules and fiscal priorities. Select a council programme or adjust rates manually, then enact the package and watch the town adapt over time.</div>`+
 `<div class="cabinet-agendas"><button data-cabinet="enterprise"><strong>Make room for enterprise</strong><small>Lower taxes, permits and barriers to development.</small></button><button data-cabinet="housing"><strong>Open the housing market</strong><small>Ease planning rules and improve access.</small></button><button data-cabinet="services"><strong>Invest in families</strong><small>Finance schools, care, relief and roads.</small></button><button data-cabinet="austerity"><strong>Balance the council purse</strong><small>Reduce spending and slow new commitments.</small></button></div>`+
 sections.map((group,index)=>`<details class="policy-group" ${index===0?'open':''}><summary>${esc(group[0])}</summary>`+group.slice(1).map(k=>{let d=defs.find(d=>d[0]===k);if(!d)return '';let [key,name,lo,hi,step,unit,help]=d,v=draftPolicy[key]??G.policy[key];return `<div class="range"><label><b>${esc(name)}</b><span id="show-${key}">${unit==='$'?money(v):policyNumber(v)+unit}</span></label><input type="range" data-policy="${key}" aria-label="${esc(name)}" min="${lo}" max="${hi}" step="${step}" value="${v}"><p class="desc">${esc(help)}</p></div>`}).join('')+'</details>').join('')+
 `<div class="line"><span>Regional inventory imports</span><button id="tradeToggle" class="small ${(draftPolicy.imports??G.policy.imports)?'on':''}">${(draftPolicy.imports??G.policy.imports)?'ALLOWED':'RESTRICTED'}</button></div>`+
 `<div class="council-card"><h3>Proposed policy package</h3><p class="desc" id="draftSummary">${changes.length?projected:'Move one or more controls to propose changes.'}</p><div class="btnrow"><button id="enactPolicy" class="action-green" ${changes.length?'':'disabled'}>ENACT POLICY CHANGES</button><button id="resetPolicy">Discard changes</button></div></div>`;
}
function enactPolicyPackage(){let changes=Object.keys(draftPolicy).filter(k=>draftPolicy[k]!==G.policy[k]);if(!changes.length){toast('No policy changes have been proposed.');return}
 let before={...G.stats,treasury:G.treasury},names=[];ensureSystems();G.policyExperiments.push({day:G.day,before:fromEnd(G.observations)||{...before},changes:changes.map(k=>({key:k,from:G.policy[k],to:draftPolicy[k]})),after:null});G.policyExperiments=G.policyExperiments.slice(-30);
 for(let k of changes){let old=G.policy[k],value=draftPolicy[k],d=defs.find(d=>d[0]===k);if(k==='imports'){G.policy.imports=!!value;names.push('Regional inventory imports: '+(old?'OPEN':'RESTRICTED')+' → '+(value?'OPEN':'RESTRICTED'));continue;}if(!d)continue;G.policy[k]=value;names.push(d[1]+': '+fmt(old)+' → '+fmt(value));}
 G.council.approval=clamp(G.council.approval-Math.min(6,changes.length*.7),5,97);G.journal.push({day:G.day,name:'Council policy package',message:names.join(' · '),baseline:before});if(G.journal.length>160)G.journal.shift();story('Council enacted '+changes.length+' economic and civic policy changes.','neutral');draftPolicy={};recompute();save();updateHeader();renderPanel('policies');toast('Policy package enacted. Let time pass to observe the effects.');}
function renderTreasuryFull(){let c=G.cumulative,P=G.policy,s=G.stats;let revenues=['incomeTax','profitTax','propertyTax','foodTax','utilityTax','commercialRate','tariffs','permits'].reduce((n,k)=>n+(c[k]||0),0);let daily=(P.policeBudget+P.defenseBudget+P.healthBudget+P.educationBudget+P.aidBudget+(P.energyAidBudget||0)+P.outreachBudget+P.roadBudget+(P.transitBudget||0)+P.militiaBudget)+(s.employed||0)*P.employmentSubsidy;daily+=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.age>70).length*(P.pensionDaily||0);daily+=G.debt*((P.policyRate||0)/100+.015)/360;let avgRev=(revenues/Math.max(1,G.day-1));let forecast=avgRev-daily;
 return head('Public balance sheet')+`<div class="statgrid">${stat('Liquid municipal cash',money(G.treasury),G.treasury<5000?'negative':'')}${stat('Outstanding debt',money(G.debt))}${stat('Receipts since founding',money(revenues))}${stat('Public spending',money(c.spending||0))}</div>`+
 `<div class="council-card"><h3>Budget outlook</h3><p class="desc">Authorization is a ceiling. Health and school services retain funds that exceed current operating need or facility capacity; compare actual provision in Services.</p>${strip('Average daily receipts since founding',money(avgRev))}${strip('Authorized daily programmes',money(daily))}${strip('Difference at full authorization',money(forecast))}<div class="desc">A backward-looking estimate, not a guaranteed forecast. Receipts change with employment, business profitability, imports and other conditions; annual taxes accrue daily.</div></div>`+
 strip('Pensions paid',money(c.pensions||0))+strip('Pension funding today',Math.round((G.market?.pensionFunding??1)*100)+'%')+head('Cumulative receipts')+strip('Income tax',money(c.incomeTax||0))+strip('Company profit tax',money(c.profitTax||0))+strip('Annual property tax instalments',money(c.propertyTax||0))+strip('Food sales tax',money(c.foodTax||0))+strip('Domestic energy levy',money(c.utilityTax||0))+strip('Commercial property rates',money(c.commercialRate||0))+strip('Import duties',money(c.tariffs||0))+strip('Business licences',money(c.permits||0))+
 head('Financial instruments')+`<div class="btnrow"><button id="borrow">Draw $5,000 credit</button><button id="repay" ${G.debt<=0?'disabled':''}>Repay up to $5,000</button></div>`+tip('Regional credit is capped at '+money(Math.max(25000,s.population*350))+'. Credit creates matching debt; monthly interest uses the policy benchmark plus a 1.5-point regional spread. Private investment is not municipal borrowing.')+
 head('Cash reserve over time')+miniChart('treasury');}
function renderCitizensFull(){let hs=G.households.filter(h=>h.people.length);if(filterPeople==='struggling')hs=hs.filter(h=>h.cash/Math.max(1,h.people.length)<600||h.stress>50);if(filterPeople==='jobless')hs=hs.filter(h=>h.people.some(id=>G.people[id]?.age>=16&&G.people[id]?.age<=70&&G.people[id]?.job<0&&!G.people[id]?.publicWork));if(filterPeople==='wealthy')hs.sort((a,b)=>b.cash-a.cash);if(filterPeople==='lowcash')hs.sort((a,b)=>a.cash-b.cash);if(citizenQuery.trim())hs=hs.filter(h=>(h.name+' '+h.people.map(id=>G.people[id]?.name||'').join(' ')).toLowerCase().includes(citizenQuery.trim().toLowerCase()));
 return head('Lives behind the statistics')+tip('Every family has savings, employment, food spending, rent, a home, health and security. Inspect a cottage to see the direct consequences of policy.')+
 `<input id="searchPeople" class="search-field" placeholder="Search a family or resident" value="${esc(citizenQuery)}"><div class="filter-row">${[['all','All'],['struggling','At risk'],['jobless','No job'],['lowcash','Least savings'],['wealthy','Most savings']].map(([k,n])=>`<button class="${filterPeople===k?'on':''}" data-filter-people="${k}">${n}</button>`).join('')}</div>`+
 `<div class="miniNote">Showing ${Math.min(80,hs.length)} of ${hs.length} matching households</div>`+
 hs.slice(0,80).map(h=>{let people=h.people.map(id=>G.people[id]).filter(p=>p&&!p.deceased&&p.movedAway!==true),workers=people.filter(p=>(p.job>=0&&!p.commuteBlocked)||p.publicWork).length,stress=Math.round(h.stress),net=h.income-h.tax-h.food-h.rent-(h.utilities||0)-(h.travel||0)-(h.debtService||0)-(h.propertyPaid||0)-(h.discretionary||0)-(h.propertyMaintenance||0)-(h.crimeLossToday||0)+(h.recoveredLosses||0)+h.aid;let note=h.cash<300?'Money is extremely tight':workers===0&&people.every(p=>p.age>70)?'Retired household':workers===0?'No employed household members':stress>65?'Under severe strain':net<0?'Outgoings exceed earnings':'Finances currently stable';return `<div class="entry" data-house="${h.id}"><div style="display:flex;justify-content:space-between;gap:5px"><strong>The ${esc(h.name)} family</strong><span class="pill">${stress>60?'UNDER PRESSURE':workers?'WORKING':people.every(p=>p.age>70)?'RETIRED':'SEEKING WORK'}</span></div><small>${people.length} residents · ${workers} employed · Cash ${money(h.cash)} · Daily net ${money(net)}<br>${esc(note)}</small></div>`}).join('')||tip('No households match the current filter.');}
function renderBusinessesFull(){let fs=G.firms.slice();if(filterFirms==='open')fs=fs.filter(f=>!f.closed);if(filterFirms==='closed')fs=fs.filter(f=>f.closed);if(filterFirms==='losing')fs=fs.filter(f=>!f.closed&&f.profit<0);if(filterFirms==='rich')fs.sort((a,b)=>b.cash-a.cash);if(filterFirms==='poor')fs.sort((a,b)=>a.cash-b.cash);
 return head('The commercial high street')+tip('Production follows supply chains: farms supply mills, mills supply bakeries, and bakeries supply grocers. Forests and stone quarries feed construction markets. Firms hire people and make real payments.')+
 `<div class="statgrid">${stat('Enterprises trading',G.stats.businesses)}${stat('Market confidence',G.stats.marketConfidence+'/100')}${stat('Regional demand',Math.round((G.regionalDemand||1)*100)+'/100')}${stat('Businesses on road grid',G.stats.roadAccess+'%')}${stat('Freight fees paid',money(G.cumulative.freight||0))}</div>`+
 `<div class="filter-row">${[['all','All'],['open','Trading'],['closed','Closed'],['losing','Loss-making'],['rich','Most capital'],['poor','Least capital']].map(([k,n])=>`<button class="${filterFirms===k?'on':''}" data-filter-firms="${k}">${n}</button>`).join('')}</div>`+
 fs.slice(0,90).map(f=>`<div class="entry" data-firm="${f.id}"><div style="display:flex;justify-content:space-between;gap:7px"><strong>${esc(f.name)}</strong><span class="pill">${f.closed?'CLOSED':'TRADING'}</span></div><small>${esc(types[f.kind].n)} · ${f.workers.length} / ${f.jobs} jobs · Capital ${money(f.cash)}<br>Revenue ${money(f.revenue)} · Profit ${money(f.profit)} · Tax ${money(f.tax)}</small></div>`).join('');}
function renderConstructionFull(){const cats=[['all','All'],['housing','Housing'],['commerce','Commerce'],['production','Industry'],['waterfront','Waterfront'],['services','Civic works']];let groups={waterfront:['fishery','wharf','road'],housing:['road','home','park','square'],commerce:['grocer','bakery','tavern'],production:['farm','mill','fishery','forestry','sawmill','quarry','contractor'],services:['police','fire','clinic','school','courthouse','watchtower','park','square','road','repair']};let keys=constructionCategory==='all'?Object.keys(buildCost).filter(k=>k!=='metro_station'):groups[constructionCategory]||Object.keys(buildCost).filter(k=>k!=='metro_station');
 return head('Build the borough')+tip('Choose a structure, then tap vacant land beside an existing road. Paint roads by dragging. Industrial and retail firms receive private investment, but council must authorize the site.')+
 `<div class="statgrid">${stat('Buildings in town',G.buildings.length)}${stat('Developed road tiles',G.tiles.filter(t=>t===1).length)}${stat('Road condition',Math.round(G.stats.roadCondition??100)+'%')}${stat('Firms with road access',(roadMetrics().connectedFirms)+' / '+roadMetrics().totalFirms)}${stat('Homes with road access',roadMetrics().connectedHomes+' / '+roadMetrics().totalHomes)}</div>`+
 `<div class="filter-row">${cats.map(([k,n])=>`<button class="${constructionCategory===k?'on':''}" data-build-category="${k}">${n}</button>`).join('')}</div>`+
 `<div class="build-grid"><button data-build="" class="build-item ${buildMode===''?'on':''}"><div class="build-icon">⌖</div><span><strong>INSPECT</strong><small>Return to surveying</small></span></button>${keys.map(k=>`<button data-build="${k}" class="build-item ${buildMode===k?'on':''}" ${G.treasury<buildCost[k]?'disabled':''}><div class="build-icon">${buildIcons[k]}</div><span><strong>${esc(types[k]?.n||'Road')}</strong><small>${money(buildCost[k])} · place on map</small></span></button>`).join('')}</div>`+
 `<div class="council-card"><h3>Private development</h3>${developmentPanel()}<button id="toggleDevelopment" class="small">${G.autoBuild?'PAUSE PRIVATE DEVELOPMENT':'RESUME PRIVATE DEVELOPMENT'}</button><button id="overlayMetro" class="small">${overlay==='metro'?'HIDE':'SHOW'} UNDERGROUND NETWORK</button></div>`+`<div class="council-card"><h3>Road transport</h3><p class="desc">All traffic follows connected streets. Disconnected businesses cannot use local suppliers; deliveries become more expensive with distance and poor maintenance. Roads connect only at shared tile edges.</p><button id="overlayR" class="small">${overlay==='roads'?'✓ ':''}Show road accessibility</button></div>`+`<div class="council-card"><h3>Planning office notes</h3><div class="desc">Building requires unoccupied land touching a road. Parks improve local wellbeing; stations strengthen funded services. New enterprises need workers and customers to survive. Private developers can extend roads, build new homes and open companies without council placement. Construction responds to demand, taxation, local earnings, capital availability and planning restrictions.</div></div>`;
}
function renderJournalFull(){let j=G.journal.slice().reverse();return head('The public record')+tip('Every recorded policy change preserves the indicators at the date of enactment. Comparisons are observational; several causes can change at once.')+
 `<div class="statgrid">${stat('Recorded decisions',j.length)}${stat('Years in office',G.year)}${stat('Crimes reported',G.cumulative.crime)}${stat('Emergency incidents',G.cumulative.fires)}</div>`+
 head('Economic history')+miniChart('employment')+head('Council trust over time')+miniChart('approval')+
 head('Government decisions')+j.slice(0,45).map(p=>{let base=p.baseline||{};let delta=(k)=>{let current=k==='treasury'?G.treasury:G.stats[k],old=base[k]||0,d=(current-old);return (d>=0?'+':'')+fmt(d)};return `<div class="entry"><strong>DAY ${p.day}: ${esc(p.name)}</strong><p class="desc">${esc(p.message||'')}</p><div class="compact">Employment ${delta('employment')} pts &nbsp;·&nbsp; Hardship ${delta('hardship')} pts &nbsp;·&nbsp; Safety ${delta('safety')} pts<br>Businesses ${delta('businesses')} &nbsp;·&nbsp; Treasury ${delta('treasury')}</div></div>`}).join('')+
 head('Recent events')+headlineList(24);}
function renderSettingsFull(){return head('Your game and archive')+strip('Edition',RELEASE.edition+' '+RELEASE.version)+strip('Engine','Offline fixed-step economy + cached pixel canvas')+strip('Living residents',fmt(G.stats.population))+strip('Construction completed',fmt(G.construction))+strip('Town founded',G.scenario)+strip('Automatic saving',autoSaveOK?'On-device save confirmed':'Check backup export')+strip('Simulation speed',speed+'× (1–64×, dynamic workload cap)')+
 `<div class="btnrow"><button id="soundToggle" aria-pressed="${soundEnabled}">${soundEnabled?'TURN OFF AMBIENCE & SOUND':'TURN ON AMBIENCE & SOUND'}</button><button id="saveNow" class="action-green">SAVE NOW</button><button id="backupSave">EXPORT BACKUP</button><button id="importSave">RESTORE BACKUP</button><button id="tutorial">GAME MANUAL</button><button id="restart" class="action-red">START NEW TOWN</button></div>`+
 head('Simulation principles')+tip('The economy runs as real linked accounts: wages and purchases move money among firms, families, the town treasury and the external region. Goods have inventory; people have jobs; firms have expenses. Government services spend actual cash and provide observable benefits.')+
 `<div class="notice-banner">Important: This is an experimental, self-contained Android adaptation. Policy coefficients are designed for gameplay, not calibrated forecasts of real municipal outcomes. Retain a text backup if you change devices or uninstall.</div>`;
}
function renderInspectFull(){const b=selected&&readBuild(selected.id);if(!b)return tip('Tap a building on the map.');const h=b.kind==='home'?G.households[b.hh]:null,f=b.firm>=0?G.firms[b.firm]:null;
 let html=`<div class="scenario-badge">PLOT ${b.x} · ${b.y} · ${esc(types[b.kind].n)}</div>`+head('Property report')+`<div class="statgrid">${stat('Estimated property value',money(b.value))}${stat('Physical condition',Math.round(b.condition)+'/100')}${stat('Land footprint',footprintOf(b).length+' plots')}</div>`;
 if(h){let people=h.people.map(id=>G.people[id]).filter(p=>p&&!p.deceased&&p.movedAway!==true),working=people.filter(p=>(p.job>=0&&!p.commuteBlocked)||p.publicWork),net=h.income-h.tax-h.food-h.rent-(h.utilities||0)-(h.travel||0)-(h.debtService||0)-(h.propertyPaid||0)-(h.discretionary||0)-(h.propertyMaintenance||0)-(h.crimeLossToday||0)+(h.recoveredLosses||0)+h.aid;let note=net<0?'Spending currently exceeds earnings. Low savings could place the family at risk.':h.stress>65?'Members of this household are experiencing substantial hardship.':'This household can presently meet its daily needs.';
 html+=head('The '+h.name+' household')+tip(note)+`<div class="statgrid">${stat('Savings',money(h.cash),h.cash<200?'negative':'')}${stat('Wellbeing',Math.round(100-h.stress)+'/100')}${stat('After-expense daily flow',money(net),net<0?'negative':'positive')}${stat('Family members employed',working.length+'/'+people.length)}</div>`+
 head('Banking & household credit')+creditDecisionReport(h)+strip('Deposits',money(Object.values(h.deposits||{}).reduce((a,v)=>a+v,0)))+strip('Credit standing',Math.round((h.creditScore??.65)*100)+'/100')+strip('Scheduled debt today',money(h.debtDue||0))+strip('Loan balance',money(G.loans.filter(l=>l.ownerType==='household'&&l.ownerId===h.id&&l.status==='active').reduce((a,l)=>a+l.balance,0)))+head('The daily household ledger')+strip('Earned wages',money(h.wages??h.income))+strip('Retirement pension',money(h.pension||0))+strip('Rental receipts',money(h.rentalIncome||0))+strip('Dividends',money(h.dividends||0))+strip('Income tax paid',money(h.incomeTax??h.tax))+strip('Energy levy',money(h.energyTax||0))+strip('Food basket',money(h.food))+strip('Heating and electricity',money(h.utilities||0))+strip('Regional utility link',h.utilityConnected==null?'Not yet observed':h.utilityConnected?'Connected through the road corridor':'No link · reconnect to the high street')+strip('Work and shopping travel',money(h.travel||0))+strip('Local service receipts',money(h.serviceReceipts||0))+strip('Housing payment',money(h.rent))+strip('Public assistance',money(h.aid))+strip('Property repair spending',money(h.propertyMaintenance||0))+strip('Burglaries today / recorded total',money(h.crimeLossToday||0)+' / '+money(h.crimeLoss))+strip('Recovered losses today',money(h.recoveredLosses||0))+strip('Perceived security',Math.round(h.security)+'/100')+
 householdServiceReport(h.id)+head('People who live here')+people.map(p=>`<div class="entry"><strong>${esc(p.name)}</strong><small>Age ${p.age} · ${p.job>=0?(p.commuteBlocked?'Road connection interrupted · ':'')+esc(G.firms[p.job]?.name||'Employed'):(p.publicWork?'Municipal day work':'Not employed')}<br>Health ${Math.round(p.health)}/100 · Skill ${Math.round(p.skill*100)}/100</small></div>`).join('');}
 else if(f){html+=head(f.name)+tip(f.closed?'This business is currently closed. New investors may reopen it if conditions permit.':'A private company facing real demand, wages, supply costs, taxes and regulation.')+`<div class="statgrid">${stat('Working capital',money(f.cash),f.cash<600?'negative':'')}${stat('Staff',f.workers.length+'/'+f.jobs)}${stat('Sales today',money(f.revenue))}${stat('Operating profit',money(f.profit),f.profit<0?'negative':'positive')}</div>`+
 head('Business accounts')+waterfrontFirmReport(f)+creditDecisionReport(f)+strip('Installed capacity factor',policyNumber(f.scale||1)+'×')+(f.pendingEquipment?strip('Funded equipment commissioning','Day '+f.pendingEquipment.ready)+tip('Paid '+money(f.pendingEquipment.cost)+'. Capacity changes when the order is commissioned; workers, inputs and customers still limit output.'):'')+strip('Attending workers today',workingStaff(f).length+' / '+f.workers.length+' contracted')+strip('Road access',graph().portals.has(b.id)&&graph().parts[graph().portals.get(b.id)]===graph().mainPart?'Connected to high street':'Disconnected · no road freight')+strip('Operating expenses',money(f.expenses))+strip('Profit taxes',money(f.tax))+strip('Profit after tax',money(f.netProfit??f.profit))+strip('Effective daily wage',money(workerIncome(f)))+strip('Cash stolen',money(f.theft))+strip('Days trading',f.age)+
 strip('Outstanding bank debt',money(f.debt||0))+strip('Credit standing',Math.round((f.creditScore??.68)*100)+'/100')+
 head('Inventory available')+Object.keys(goods).map(k=>strip(k,fmt(f.stock[k]||0)+' units')).join('')+
 head('Employees')+f.workers.slice(0,25).map(id=>{let p=G.people[id];return p?`<div class="line"><span>${esc(p.name)}</span><span>${esc(G.households[p.hh]?.name||'')}</span></div>`:''}).join('');}
 else if(b.kind==='apartment'||b.kind==='tower'){let occupants=(b.units||[]).map(id=>G.households[id]).filter(Boolean);html+=head('A rebuilt residential district')+tip('A private developer consolidated a former low-density plot into multi-family homes. Existing residents retained an address and owners received acquisition compensation when applicable.')+strip('Occupied dwellings',occupants.length)+strip('Living residents',occupants.reduce((n,h)=>n+h.people.length,0))+strip('Original building',b.replacedKind||'Cottage')+head('Households')+occupants.slice(0,15).map(h=>`<div class="entry"><strong>The ${esc(h.name)} household</strong><small> · ${h.people.length} residents · Savings ${money(h.cash)}</small></div>`).join('');}
 else if(b.kind==='airport'){html+=head('Private regional airfield')+tip('Airport investment responds to regional activity and requires a large clear runway site, upfront capital, and continuing ticket and freight demand.')+strip('Runway plots',G.airport?.runway?.length||0)+strip('Passengers served',fmt(G.airport?.passengers||0))+strip('Freight tons',fmt(G.airport?.freight||0))+strip('Service',G.airport?.operating?'Operating':'Suspended');}
 else if(b.kind==='worksite'){const p=G.projects?.find(p=>p.id===b.id);html+=head('Private construction')+tip('A contractor is developing this property with private capital. Its residents or business will arrive when construction finishes.')+strip('Planned use',p?.kind==='home'?'Cottage':p?.firmKind||'Business')+strip('Days remaining',p?.remaining??'Unknown');}
 else if(b.kind==='bank'){const bk=G.banks.find(v=>v.id===b.bankId);html+=head('Local banking branch')+tip('A privately capitalized bank competing for deposits and borrowers. Losses reduce capital and can lead to failure.')+(bk?strip('Institution',bk.name)+strip('Cash reserves',money(bk.cash))+strip('Outstanding loans',money(bankLoans(bk.id)))+strip('Customer deposits',money(bankDeposits(bk.id)))+strip('Status',bk.closed?'Receivership':'Open to depositors'):'Branch closed');}
 else if(b.kind==='metro_station'){let metro=G.metro||{};html+=head('Private Underground Railway')+tip('Station owned by the Vale Underground company. Shareholders pay for track and stations; passengers pay fares. The town does not automatically subsidize this operator.')+strip('Service status',metro.operating?'Trains operating':'Suspended')+strip('Network',((metro.stations||[]).length)+' stations · '+((metro.lines||[]).length)+' lines')+strip('Fare',money(metro.fare||0))+strip('Journeys recorded',fmt(metro.rides||0))+strip('Shareholders’ cash',money(metro.cash||0));}
 else{html+=head('Municipal property')+tip('This structure serves the public. The building contributes to service effectiveness when paired with a funded government programme.')+strip('Type',types[b.kind].n)+strip('Town funding','Managed through Policies and Budget');}
 return html+`<div class="btnrow"><button id="closeInspect">BACK TO MAP</button></div>`;
}


// SOURCE: 92-government.js
function observedChart(key,color='#7f9968'){
 const a=G.observations.slice(-72);if(a.length<2)return tip('Observations accumulate every ten days.');
 const values=a.map(x=>Number(x[key])||0),lo=Math.min(...values),hi=Math.max(...values),span=Math.max(.0001,hi-lo);
 const p=values.map((v,i)=>`${(i/(values.length-1)*330).toFixed(2)},${(100-(v-lo)/span*85).toFixed(2)}`).join(' ');
 return `<svg class="chart-lines" viewBox="0 0 330 115" aria-label="${esc(key)} over time"><path d="M0 100H330M0 57H330M0 15H330" stroke="#bac4a3" fill="none"/><polyline points="${p}" fill="none" stroke="${color}" stroke-width="2"/></svg><div class="miniNote">Day ${a[0].day}–${fromEnd(a).day} · ${fmt(lo)}–${fmt(hi)}</div>`;
}
function renderEconomicAtlas(){
 ensureSystems();const m=G.housingMarket,active=G.firms.filter(f=>!f.closed),latest=fromEnd(G.observations)||{};
 return head('Property & capital')+`<div class="statgrid">${stat('Median home valuation',money(m.medianValue||0))}${stat('Rent index (founding = 1)',fmt(m.rentIndex))}${stat('Unoccupied dwellings',m.vacancy??0)}${stat('Paid construction contracts',money(G.investors[0].spending))}</div>`+
 tip('Valuations respond gradually to rents, access, condition and location. Investors compare operating yields with funding costs. Regional capital is finite; land and construction have recorded counterparties.')+
 head('Housing rents over time')+observedChart('rentIndex')+
 head('A government decision, followed through')+(G.policyExperiments.length?G.policyExperiments.slice(-4).reverse().map(e=>{
 const later=e.after||latest,days=later.day-e.day,before=e.before;
 return `<div class="council-card"><small>ENACTED DAY ${e.day} · ${e.after?'180-DAY REVIEW':Math.max(0,days)+' DAYS OBSERVED'}</small><h3>${esc(e.changes.map(c=>defs.find(d=>d[0]===c.key)?.[1]||c.key).join(', '))}</h3>${e.changes.map(c=>strip(defs.find(d=>d[0]===c.key)?.[1]||c.key,fmt(c.from)+' → '+fmt(c.to))).join('')}${strip('Population',fmt(before.population)+' → '+fmt(later.population))}${strip('Employment',fmt(before.employment)+'% → '+fmt(later.employment)+'%')}${strip('Private construction spending',money(before.privateSpend||0)+' → '+money(later.privateSpend||0))}${strip('Hardship',fmt(before.hardship)+'% → '+fmt(later.hardship)+'%')}<p class="desc">Observed changes include other influences. Compare identical seeded scenarios in the test suite to isolate a policy change.</p></div>`;
 }).join(''):tip('Enact a policy package to begin a before-and-after record. A review is retained after 180 days.'))+
 head('Freight in the real supply chain')+strip('Cargo currently travelling',(G.freight||[]).length+' consignments')+strip('Cargo and sampled trips completed',fmt(G.transport.arrived))+strip('Blocked cargo-days',fmt(G.transport.delayed))+
 (G.freight||[]).slice(0,8).map(s=>`<div class="entry"><strong>${fmt(s.qty)} ${esc(s.good)}</strong><small>${esc(G.firms[s.from]?.name)} → ${esc(G.firms[s.to]?.name)}<br>${s.delayed?'Delayed by access interruption':s.remaining+' day(s) remaining'} · goods remain owned in transit</small></div>`).join('')+
 head('Physical goods & clearing prices')+`<table class="report-table"><tr><td>Commodity</td><td>Inventory incl. cargo</td><td>Unit price</td></tr>${goodsBalance().map(a=>`<tr><td>${esc(a.good)}</td><td>${fmt(a.stock)}</td><td>${money(a.price)}</td></tr>`).join('')}</table>`+tip('Production, transformation, household use, imports, exports and cargo are counted separately. Wholesale prices adjust gradually to inventory coverage and regional demand.')+head('Recent investment accounts')+G.transactions.slice(-18).reverse().map(t=>`<div class="entry"><strong>${money(t.amount)} · ${esc(t.reason)}</strong><small>Day ${t.day} · ${esc(t.from)} → ${esc(t.to)}</small></div>`).join('');
}
const economyOriginal=renderEconomy;
renderEconomy=function(){return economyOriginal()+renderEconomicAtlas();};
const inspectOriginal=renderInspectFull;
renderInspectFull=function(){
 let html=inspectOriginal(),b=selected?.id?readBuild(selected.id):null;if(!b)return html;
 const owner=b.owner>=0?'The '+(G.households[b.owner]?.name||'unknown')+' household':b.owner===-2?G.investors[0].name:'Regional owner / public authority';
 html+=head('Parcel title & investment')+strip('Recorded owner',owner)+strip('Property valuation',money(b.value))+strip('Legal land footprint',footprintOf(b).length+' tiles')+strip('Physical condition',Math.round(b.condition)+' / 100');
 if(b.kind==='worksite'||b.redevelopment){const p=G.projects.find(p=>p.id===b.id);if(p)html+=head('Construction progress')+strip('Responsible builder',p.builder||'Crew assignment pending')+strip('Work days remaining',p.remaining)+strip('Days stalled',p.stalledDays||0)+tip(p.reason||'Construction financed; crew and materials are allocated daily.');}
 if(b.investment){const q=b.investment;html+=strip('Investment approved','Day '+q.day)+strip('Expected operating yield',(q.yield*100).toFixed(1)+'%')+strip('Funding hurdle',(q.hurdle*100).toFixed(1)+'%')+strip('Construction budget',money(q.cost))+strip('Land consideration',money(q.land))+tip('Expected returns are the developer’s estimate at approval; realized returns can differ.');}
 html+=G.transactions.filter(t=>t.entity===b.id).slice(-5).reverse().map(t=>`<div class="entry"><strong>${esc(t.reason)}</strong><small>Day ${t.day} · ${money(t.amount)} · ${esc(t.from)} → ${esc(t.to)}</small></div>`).join('');
 return html;
};
const settingsOriginal=renderSettingsFull;
renderSettingsFull=function(){
 const p=perfStats;
 return `<div class="btnrow"><button id="recoverAutosave">Recover previous autosave</button></div>`+head('Views of the Vale')+`<div class="maptool-row"><button id="nightView">${nightMode?'Morning light':'Evening light'}</button><button data-district="all">Whole borough</button><button data-district="main">Market district</button><button data-district="farms">Farm belt</button><button data-view="land">Land values</button><button data-view="roads">Road access</button></div>`+
 head('Session diagnostics')+strip('Draw CPU median / p95',percentile(p.frames,.5).toFixed(2)+' / '+percentile(p.frames,.95).toFixed(2)+' ms')+strip('Daily simulation median / p95',percentile(p.ticks,.5).toFixed(2)+' / '+percentile(p.ticks,.95).toFixed(2)+' ms')+strip('Requested / measured speed',speed+'× / '+p.effective.toFixed(1)+'×')+strip('Queued simulation',p.backlog.toFixed(1)+' days')+strip('Largest cash ledger drift',money(G.accounts?.maxError||0))+tip('CPU timings in this session are not device FPS or a thermal measurement. Measured speed counts completed simulation days. CPU work and queued wall time are bounded to keep controls responsive.')+
 settingsOriginal();
};
function navigateDistrict(which){
 const list=which==='farms'?G.buildings.filter(b=>b.kind==='farm'):which==='main'?G.buildings.filter(b=>b.firm>=0&&!['farm','forestry','quarry'].includes(b.kind)):G.buildings;
 if(!list.length)return;const x=list.reduce((n,b)=>n+b.x,0)/list.length,y=list.reduce((n,b)=>n+b.y,0)/list.length,p=iso(x,y);
 cam.x=p[0];cam.y=p[1]+18;cam.zoom=which==='all'?.59:1.35;closePanel();dirty=true;
}
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b||!G)return;
 if(b.id==='recoverAutosave'){try{const e=readSaveEnvelope(localStorage.getItem('townledger-v6-backup'));if(e&&hydrateSave(e.payload)){toast('Previous autosave recovered. Export it to keep a separate copy.');renderPanel('settings');}else toast('No valid earlier autosave is available.');}catch(_){toast('No valid earlier autosave is available.');}}
 if(b.id==='nightView'){nightMode=!nightMode;atlas.clear();dirty=true;renderPanel('settings');}
 if(b.dataset.district)navigateDistrict(b.dataset.district);
 if(b.dataset.view){overlay=b.dataset.view;closePanel();dirty=true;toast(overlay==='land'?'Land values: green low · gold middle · copper high':'Road access: green connected · copper disconnected');}
});
// Android uses the system document picker; desktop retains the text archive workflow.
window.__townArchive={
 suspend:()=>{hostSuspended=true;acc=0;last=performance.now();save();stopGameAudio();},
 resume:()=>{hostSuspended=false;acc=0;last=performance.now();refreshAmbience();},
 export:()=>archivePayload(),
 restore:text=>{const ok=hydrateSave(text);if(ok){save();$('welcome').style.display='none';dirty=true;staticDirty=true;toast('Town restored with its property, bank, cargo and resident records.');}else toast('Archive rejected. The current town is unchanged.');return ok;},
 back:()=>{if($('helpDialog').style.display!=='none'){hideHelpDialog();return true;}if(pendingEvent){closeCouncilDialog(true);return true;}if(active){closePanel();return true;}return false;}
};
const originalExport=exportSave,originalImport=importSave;
exportSave=function(){if(window.AndroidArchive)window.AndroidArchive.writeBackup(archivePayload());else originalExport();};
importSave=function(){if(window.AndroidArchive)window.AndroidArchive.openBackup();else originalImport();};

if($('townSeed')){try{$('townSeed').value=String(crypto.getRandomValues(new Uint32Array(1))[0]||42);}catch(_){$('townSeed').value=String(Date.now()%4294967295||42);}}

// SOURCE: 93-preferences.js
const settings61Base=renderSettingsFull;
renderSettingsFull=function(){
 const toggle=(k,label,note)=>`<div class="option-row"><div><strong>${label}</strong><small>${note}</small></div><button data-option="${k}" aria-pressed="${k==='seasons'?seasonsEnabled():k==='weather'?weatherEnabled():gameOptions[k]}">${(k==='seasons'?seasonsEnabled():k==='weather'?weatherEnabled():gameOptions[k])?'ON':'OFF'}</button></div>`;
 const select=(k,label,values)=>`<label class="option-row"><strong>${label}</strong><select data-preference="${k}">${values.map(([v,t])=>`<option value="${v}" ${String(gameOptions[k])===String(v)?'selected':''}>${t}</option>`).join('')}</select></label>`;
 return head('Display & accessibility')+select('quality','Graphics quality',[['low','Performance'],['balanced','Balanced'],['high','Rich detail']])+select('fps','Frame-rate limit',[[20,'20 FPS'],[30,'30 FPS'],[60,'60 FPS']])+toggle('streetNames','Street names','Named streets and a visible road hierarchy.')+toggle('traffic','Visible traffic','Commuters and trucks. Cargo and jobs continue when hidden.')+toggle('effects','Atmospheric effects','Smoke, water shimmer and weather particles.')+toggle('decor','Gardens & landscape detail','Flowers, fences, masonry and roof texture.')+toggle('reducedMotion','Reduced motion','Stop decorative movement and traffic animation.')+toggle('largeText','Larger text','Larger menu labels and reading text.')+toggle('showHints','Map hints','Show the short map guidance below the town.')+
 head('Climate rules')+toggle('seasons','Seasonal cycle','OFF by default: green landscape and stable farm output all year. Saved with this town.')+toggle('weather','Weather events','OFF by default: no storms or droughts. Saved with this town.')+
 head('Saving')+select('autoSave','Autosave interval',[[15,'15 seconds'],[30,'30 seconds'],[60,'1 minute'],[120,'2 minutes']])+tip('Pausing or leaving the app also saves. At 64×, Balanced and Performance simplify ground detail and reduce map resolution; pause or choose Rich detail to restore full detail. At high speed, the map refreshes at up to 20 FPS to give the economy more CPU time. The speed indicator measures days actually completed; slower devices may run below the selected rate.')+settings61Base();
};
function changePreference(key,value){
 if(!(key in OPTION_DEFAULTS))return;
 gameOptions[key]=value;
 if(key==='seasons'&&G){G.climateSeasons=value;staticDirty=true;}
 if(key==='weather'&&G){G.climateWeather=value;if(!value)G.weather='clear';refreshAmbience();}
 try{localStorage.setItem('townledger-options',JSON.stringify(gameOptions));}catch(_){}
 applyPresentationOptions();if(G){save();renderPanel('settings');}
}
document.addEventListener('click',e=>{const b=e.target.closest('[data-option]');if(b){const k=b.dataset.option;changePreference(k,!(k==='seasons'?seasonsEnabled():k==='weather'?weatherEnabled():gameOptions[k]));}});
document.addEventListener('change',e=>{const k=e.target.dataset.preference;if(k)changePreference(k,typeof OPTION_DEFAULTS[k]==='number'?Number(e.target.value):e.target.value);});

// SOURCE: 94-economic-reports.js
const workingEconomyBase=renderEconomy;
renderEconomy=function(){
 const m=G.market||{},fs=G.firms.filter(f=>!f.closed),sales=fs.reduce((n,f)=>n+(f.operating?.sales??f.revenue),0),inputs=fs.reduce((n,f)=>n+(f.cogs||0),0),payroll=fs.reduce((n,f)=>n+(f.payroll||0),0),profit=fs.reduce((n,f)=>n+(f.netProfit||0),0);
 const publicRoads=charterRoadCount(),maintenance=publicRoads*.045/.23,issues=[];
 if((G.policy.roadBudget||0)*(G.actualServiceFunding?.roads??1)<maintenance*.9)issues.push('Road upkeep: approximately '+money(maintenance)+'/day is needed to offset ordinary wear on public streets; '+money(G.policy.roadBudget||0)+'/day is authorized. Growing infrastructure needs a larger maintenance budget.');
 if(m.blockedCommutes>0)issues.push('Work access: '+fmt(m.blockedCommutes)+' contracted workers could not reach their workplace. Restore the road connection; extra credit cannot supply missing work hours.');
 if(m.foodDisconnected>0)issues.push('Grocery access: '+fmt(m.foodDisconnected)+' residents have no operating grocer on their road network. Income or cheaper credit cannot deliver across a missing connection.');
 if((m.unmetFood||0)>1)issues.push('Food access: '+fmt(m.unmetFood)+' units of essential demand went unfilled today. Check shop stock, retail staff, prices, household income and import access.');
 if(G.stats.unemployment>15)issues.push('Employment: '+G.stats.unemployment+'% of the workforce is seeking work. Inspect sector operating margins and vacancies; lower financing costs help viable expansion but cannot supply customers to an unprofitable business.');
 const programmes=['policeBudget','defenseBudget','healthBudget','educationBudget','aidBudget','roadBudget'].reduce((n,k)=>n+(G.policy[k]||0),0);
 if(G.treasury<programmes*30)issues.push('Public cash: less than one month of core authorized programmes is in reserve. Compare recurring receipts with services, pensions and debt costs before expanding commitments.');
 for(const [kind,p] of Object.entries(G.serviceProvision||{}))if(p.coverage<.8)issues.push((kind==='health'?'Medical care':'Schooling')+': '+Math.round(p.coverage*100)+'% resident coverage. '+(p.facilityCoverage<.8?'Existing facilities cannot serve the whole town; compare capacity and purchases in Services.':'Compare the operating need, authorization and actual payment in Services.'));
 if(!G.banks.some(b=>!b.closed))issues.push('Credit access: no bank is operating. Replacement institutions need subscribed capital; cash grants alone do not repair a failed loan portfolio.');
 return head('Current pressures')+(issues.length?issues.map(x=>tip(x)).join(''):tip('No major shortfall is flagged in food access, current road funding, employment or near-term public cash. Continue monitoring sector earnings and the household ledger.'))+head('Orders, costs and monetary policy')+`<div class="statgrid">${stat('Benchmark interest',policyNumber(G.policy.policyRate||0)+'%')}${stat('Living-cost basket index',fmt(m.cpi||100))}${stat('Business sales / day',money(sales))}${stat('Private payroll / day',money(payroll))}${stat('Inventory sold at cost',money(inputs))}${stat('Net business earnings',money(profit))}</div>`+
 tip('Firms buy inventories, sell to finite local and external demand, and hire from sustained sales. Stock purchases reduce cash immediately; their cost enters profit when sold. The interest benchmark feeds lending and deposit quotes gradually, reprices variable debt, and changes investment hurdles. A tax cut helps returns; it cannot replace missing customers or inputs.')+
 strip('Unfilled food demand today',fmt(m.unmetFood||0)+' units')+strip('Regional export receipts today',money(m.externalSales||0))+strip('Subscribed restart equity since upgrade',money(m.privateRestartCapital||0))+
 `<div class="btnrow"><button data-open-monetary="true">Adjust interest policy</button></div>`+workingEconomyBase();
};
const workingInspectBase=renderInspectFull;
renderInspectFull=function(){const b=selected?.id?readBuild(selected.id):null,f=b&&G.firms[b.firm];let html=workingInspectBase();if(!f)return html;const o=f.operating||{};
 return html+head('Operating statement')+strip('Sales recognized',money(o.sales||0))+strip('Grants and recovered losses',money(o.otherIncome||0))+strip('Cost of goods sold',money(o.costOfGoods||0))+strip('Payroll actually paid',money(o.payroll||0))+strip('Other operating and finance costs',money(o.otherCosts||0))+strip('Profit tax',money(o.profitTax||0))+strip('Net earnings',money(o.netProfit||0))+strip('Stock purchased (cash flow)',money(o.purchases||0))+strip('Inventory at purchase/production cost',money(o.inventoryValue||0))+strip('Smoothed operating margin',fmt((f.marginTrend||0)*100)+'%')+strip('Orders / sales trend',fmt(f.salesTrend||0)+' units per day')+tip('Hiring adjusts every two weeks using sustained orders and capacity. Expensive credit and low retained earnings limit expansion. Persistent losses lead to layoffs and eventual closure; unpaid workers leave rather than remaining in fictional jobs.');
};
const workingFinanceBase=financePanel;
financePanel=function(){return head('Monetary authority')+strip('Policy benchmark',policyNumber(G.policy.policyRate||0)+'% annual')+tip('Bank quotes adjust every fifteen days. Variable-rate loan costs adjust monthly; existing fixed-rate contracts retain their agreed rate. The authority sets a benchmark, not every bank’s final risk spread.')+`<div class="btnrow"><button data-open-monetary="true">Set policy interest rate</button></div>`+workingFinanceBase();};
document.addEventListener('click',e=>{if(e.target.closest('[data-open-monetary]')){openPanel('policies');const field=document.querySelector('[data-policy="policyRate"]');if(field){field.closest('details').open=true;field.scrollIntoView({block:'center'});field.focus();}}});

// SOURCE: 95-audio.js
// Licensed synthesized effects from the original TownLedger project, played only after interaction.
let soundEnabled=true;try{soundEnabled=localStorage.getItem('townledger-audio')!=='off'}catch(e){};let ambient=null,ambientFile='';const audioCache={};
function stopGameAudio(){if(ambient)ambient.pause();for(const a of Object.values(audioCache))a.pause();}
function refreshAmbience(){if(!soundEnabled||!G||document.hidden||hostSuspended){stopGameAudio();return}const name=G.weather==='rain'||G.weather==='storm'?'rain':'village';if(name!==ambientFile){if(ambient)ambient.pause();ambient=new Audio('sound/'+name+'.wav');ambient.loop=true;ambient.volume=.10;ambientFile=name}ambient.play().catch(()=>{})}function playSfx(name){if(!soundEnabled||document.hidden||hostSuspended)return;try{let a=audioCache[name];if(!a){a=new Audio('sound/'+name+'.wav');a.volume=.22;audioCache[name]=a}a.pause();a.currentTime=0;a.play().catch(()=>{})}catch(e){}}
document.addEventListener('click',e=>{let b=e.target.closest('button');if(!b||b.disabled)return;let id=b.id;if(id==='newTown'||id==='enactPolicy'||id==='borrow'||id==='repay'||b.dataset.sound==='coin')playSfx('coin');else if(id==='saveNow')playSfx('save');else if(b.dataset.build!==undefined)playSfx('zone');else playSfx('click')},{passive:true});

// SOURCE: 96-council-programme.js
// Scenario programmes measure sustained outcomes; they do not grant free resources.
function programmeMetrics(){
 const households=G.households.filter(h=>h.people.length),latest=fromEnd(G.observations)||{},need=G.market?.consumedFood+G.market?.unmetFood;
 const recurring=['policeBudget','defenseBudget','healthBudget','educationBudget','aidBudget','energyAidBudget','outreachBudget','roadBudget','transitBudget','militiaBudget'].reduce((n,k)=>n+(G.policy[k]||0),0)+G.people.filter(p=>!p.deceased&&!p.movedAway&&p.age>70).length*(G.policy.pensionDaily||0)+(G.policy.employmentSubsidy||0)*G.people.filter(p=>p.job>=0&&!p.commuteBlocked).length+G.debt*((G.policy.policyRate||0)/100+.015)/360;
 return {employment:G.stats.employment||0,hardship:G.stats.hardship||0,food:need>0?100*G.market.consumedFood/need:0,medical:100*(G.serviceProvision?.health?.coverage??latest.medicalCoverage??0),school:100*(G.serviceProvision?.school?.coverage??latest.schoolCoverage??0),buffers:100*households.filter(h=>householdLiquidity(h)/h.people.length>=300).length/Math.max(1,households.length),reserve:Math.min(999,G.treasury/Math.max(1,recurring)),banks:G.banks.filter(b=>!b.closed&&bankEquity(b)>0).length,blocked:G.market?.blockedCommutes||0,training:G.civicTrainingCompletions||0,treasury:G.treasury,debt:G.debt};
}
const PROGRAMME_RULES={
 work:['Residents in work','employment',75,'min','%','economy','Inspect sales and margins before financing more jobs.'],
 food:['Essential food supplied','food',95,'min','%','economy','Check reachable shops, stock, retail staff and household buying power.'],
 hardship:['Households in hardship','hardship',15,'max','%','citizens','Inspect a struggling family; income, rent and access can bind differently.'],
 care:['Funded medical access','medical',65,'min','%','community','Compare reachable places, qualified staff and operating purchases.'],
 learning:['Funded school access','school',60,'min','%','community','Buildings need reachable pupils, staff and sustained operating funds.'],
 cash:['Authorized spending reserve','reserve',30,'min',' days','treasury','Reserve days compare cash with authorized services, pensions, subsidy and debt interest. Unused allocations can make actual spending lower.'],
 banks:['Solvent operating banks','banks',2,'min','','banking','Default losses absorb equity; new banks need subscribed regional capital.'],
 buffers:['Families with $300 per resident','buffers',75,'min','%','citizens','Cash and bank deposits count; home valuations are not immediately spendable.'],
 access:['Interrupted work journeys','blocked',0,'max','','construction','Reconnect workplaces and homes before adding capacity.'],
 training:['Adult training terms completed','training',2,'min','','community','A term needs 120 equivalent locally funded school days; partial coverage takes longer.']
};
function programmeRule(key,target){const a=PROGRAMME_RULES[key];return {key,label:a[0],metric:a[1],target:target??a[2],direction:a[3],unit:a[4],panel:a[5],help:a[6]};}
function programmeChapter(title,description,keys,days=30){return {title,description,days,rules:keys.map(k=>Array.isArray(k)?programmeRule(...k):programmeRule(k))};}
const SCENARIO_PROGRAMMES={
 settlement:{title:'Build a lasting borough',chapters:[programmeChapter('The everyday essentials','Establish reliable work and a food basket families can obtain.',['work','food','hardship']),programmeChapter('Care within reach','Purchase usable care and teaching, then retain a month of authorized commitments.',['care','learning','cash']),programmeChapter('Prosperity with a cushion','Sustain useful services and family buffers through a longer operating period.',['work','buffers','care','learning','cash'],60)]},
 frontier:{title:'An independent frontier',chapters:[programmeChapter('A viable foothold','Secure the smaller town’s essentials before promising a larger public establishment.',[['work',65],'food',['hardship',25]]),programmeChapter('A modest public settlement','Expand care and learning within a thin tax base.',[['care',50],['learning',45],['cash',20]]),programmeChapter('Room to endure','Retain household buffers, reachable employment and a month of public commitments.',[['work',80],'buffers','access','cash'],60)]},
 hardtimes:{title:'A recovery that lasts',chapters:[programmeChapter('Stop the immediate slide','Restore essentials and retain access to solvent institutions.',[['work',70],'food',['hardship',25],'banks']),programmeChapter('Rebuild the cushions','Rebuild family savings while restoring funded local care and schooling.',['buffers',['care',50],['learning',45]]),programmeChapter('A durable recovery','Sustain employment and services without consuming the public cash reserve.',[['work',80],['hardship',12],'care','learning','cash'],90)]},
 industrial:{title:'An industrial social contract',chapters:[programmeChapter('Work that sustains families','Judge industrial expansion by paid work and essential living conditions.',[['work',80],'food','hardship']),programmeChapter('Skills behind the factories','Support actual adult training and reachable public care.',['training','learning','care']),programmeChapter('Investment with resilience','Keep the workforce connected and retain family and public buffers.',['work','access','buffers','cash'],60)]},
 regional:{title:'A city beyond full employment',chapters:[programmeChapter('An accessible regional city','A strong headline job market still needs reachable work and funded local places.',['access','care','learning']),programmeChapter('Broader capability','Complete sustained adult learning while families retain liquid savings.',['training','buffers',['learning',70]]),programmeChapter('A sustainable civic settlement','Carry the commitments through two months with a public reserve.',['work',['care',75],['learning',70],'cash'],60)]}
};
function programmeDefinition(){return owns(SCENARIO_PROGRAMMES,G.scenario)?SCENARIO_PROGRAMMES[G.scenario]:SCENARIO_PROGRAMMES.settlement;}
function initializeScenarioProgramme(){G.scenarioProgramme={version:1,scenario:G.scenario,started:G.day,stage:0,held:0,lastDay:G.day,completed:[],baseline:programmeMetrics()};}
function ensureScenarioProgramme(){if(!G.scenarioProgramme)initializeScenarioProgramme();}
function programmeRuleMet(rule,metrics){return rule.direction==='min'?metrics[rule.metric]+.00001>=rule.target:metrics[rule.metric]-.00001<=rule.target;}
function updateScenarioProgramme(){
 ensureScenarioProgramme();const state=G.scenarioProgramme,definition=programmeDefinition(),chapter=definition.chapters[state.stage];if(!chapter||state.lastDay===G.day)return;
 const metrics=programmeMetrics();state.lastDay=G.day;state.held=chapter.rules.every(r=>programmeRuleMet(r,metrics))?state.held+1:0;
 if(state.held<chapter.days)return;
 state.completed.push({stage:state.stage,day:G.day});state.stage++;state.held=0;state.baseline=metrics;
 const final=state.stage===definition.chapters.length,message=final?'Council programme completed: '+definition.title+'. The town remains open for continued government.':'Council chapter completed: '+chapter.title+'. Next: '+definition.chapters[state.stage].title+'.';
 G.journal.push({day:G.day,name:final?'Council programme complete':'Council chapter complete',message,baseline:{...G.stats,treasury:G.treasury}});story(message,'good');
}
function validateScenarioProgramme(data){
 if(data.scenario!=null&&!owns(SCENARIO_PROGRAMMES,data.scenario))return false;
 if(data.civicTrainingCompletions!=null&&(!Number.isInteger(data.civicTrainingCompletions)||data.civicTrainingCompletions<0||data.civicTrainingCompletions>1000000))return false;
 const p=data.scenarioProgramme;if(p==null)return true;const definition=SCENARIO_PROGRAMMES[data.scenario]||SCENARIO_PROGRAMMES.settlement;
 if(p.version!==1||p.scenario!==data.scenario||!Number.isInteger(p.started)||p.started<1||p.started>data.day||!Number.isInteger(p.lastDay)||p.lastDay<p.started||p.lastDay>data.day||!Number.isInteger(p.stage)||p.stage<0||p.stage>definition.chapters.length||!Number.isInteger(p.held)||p.held<0||p.held>=(definition.chapters[p.stage]?.days||1)||!Array.isArray(p.completed)||p.completed.length!==p.stage)return false;
 if(p.completed.some((c,i)=>c.stage!==i||!Number.isInteger(c.day)||c.day<p.started||c.day>data.day||(i>0&&c.day<=p.completed[i-1].day)))return false;
 return p.baseline&&typeof p.baseline==='object'&&!Array.isArray(p.baseline)&&Object.keys(p.baseline).length<=20&&['employment','hardship','food','medical','school','buffers','reserve','banks','blocked','training','treasury','debt'].every(k=>Number.isFinite(p.baseline[k])&&p.baseline[k]>=0);
}
function programmeTrend(){
 const samples=G.observations.filter(o=>Number.isFinite(o.medicalCoverage)&&Number.isFinite(o.schoolCoverage)).slice(-36);if(samples.length<2)return tip('The ten-day record will begin to show trends after two observations.');
 const lines=[['employment','Employment','#536c70',1],['medicalCoverage','Medical access','#2f6945',100],['schoolCoverage','School access','#886020',100]],path=(key,scale)=>samples.map((s,i)=>`${(i/(samples.length-1)*320).toFixed(1)},${(110-clamp(s[key]*scale,0,100)).toFixed(1)}`).join(' ');
 return `<svg class="programme-chart" viewBox="0 0 355 135" role="img" aria-label="Employment, funded medical access and school access on a fixed zero to one hundred percent scale, days ${samples[0].day} to ${fromEnd(samples).day}"><path d="M0 10H320M0 60H320M0 110H320" stroke="#b2ba9c" fill="none"/>${lines.map(([key,label,color,scale])=>`<polyline points="${path(key,scale)}" fill="none" stroke="${color}" stroke-width="2.5"/>`).join('')}<g fill="#344d3d" font-size="10"><text x="325" y="14">100%</text><text x="325" y="64">50%</text><text x="325" y="114">0%</text><text x="0" y="132">DAY ${samples[0].day}</text><text x="255" y="132">DAY ${fromEnd(samples).day}</text></g></svg><div class="programme-legend">${lines.map(([key,label,color,scale])=>`<span><i style="background:${color}"></i>${label} ${policyNumber(fromEnd(samples)[key]*scale)}%</span>`).join('')}</div>`;
}
function scenarioProgrammeCard(full=false){
 const state=G.scenarioProgramme;if(!state)return '';const definition=programmeDefinition(),chapter=definition.chapters[state.stage],metrics=programmeMetrics();
 const heading=chapter?chapter.title:'Programme complete',progress=chapter?state.held/chapter.days:1;
 let html=`<section class="programme-card ${full?'full':'compact'}" aria-label="Council programme"><small>COUNCIL PROGRAMME · ${state.stage===3?'COMPLETED':'CHAPTER '+(state.stage+1)+' OF 3'}</small><h3>${esc(full?definition.title:heading)}</h3>${full?`<strong>${esc(heading)}</strong><p class="desc">${esc(chapter?.description||'The programme has been sustained. Keep governing, try another ambition, or export a record of this town.')}</p>`:''}<div class="progress" role="progressbar" aria-label="Sustained qualifying days" aria-valuemin="0" aria-valuemax="${chapter?.days||1}" aria-valuenow="${chapter?state.held:1}"><i style="width:${Math.round(progress*100)}%"></i></div>`;
 if(chapter){html+=`<p class="miniNote">${state.held} / ${chapter.days} consecutive qualifying days.${full?' Missing a condition resets this chapter’s count; completed chapters remain recorded.':''}</p>`;
 html+=chapter.rules.map(r=>`<div class="programme-rule ${programmeRuleMet(r,metrics)?'met':'waiting'}"><span class="programme-state">${programmeRuleMet(r,metrics)?'MET':'NEEDS WORK'}</span><div><strong>${esc(r.label)}</strong><span>${policyNumber(metrics[r.metric])}${r.unit} / ${r.direction==='min'?'at least':'at most'} ${r.target}${r.unit}</span></div><button data-programme-panel="${r.panel}" title="${esc(r.help)}" aria-label="${esc(r.label+': '+r.help)}">Review</button></div>`).join('');
 html+=`<details><summary>How to work on this chapter</summary><p class="desc">${esc(chapter.description)} Missing a condition resets this chapter’s qualifying-day count. Completed chapters remain recorded.</p>${chapter.rules.map(r=>`<p class="desc"><strong>${esc(r.label)}.</strong> ${esc(r.help)}</p>`).join('')}<p class="desc">This is an observed programme, not a forecast. Recruitment takes 30 days; training needs 120 funded teaching days; equipment commissions 30 days after payment. A budget cannot create a missing road or qualified worker instantly.</p></details>`;
 }
 if(full)html+=head('Observed outcomes')+programmeTrend()+tip('The shared scale is 0–100%. These are observed outcomes, including other influences; a policy change is not a controlled experiment.')+head('The full programme')+definition.chapters.map((c,i)=>`<div class="programme-chapter"><span>${i<state.stage?'COMPLETED DAY '+state.completed[i].day:i===state.stage?'CURRENT':'LATER CHAPTER'}</span><strong>${i+1}. ${esc(c.title)}</strong><p class="desc">${esc(c.description)} Sustain all conditions ${c.days} days.</p>${i===state.stage?'':c.rules.map(r=>`<small>${esc(r.label)}: ${r.direction==='min'?'at least':'at most'} ${r.target}${r.unit}</small>`).join('')}</div>`).join('');
 return html+'</section>';
}
const programmeOverviewBase=renderOverviewFull;renderOverviewFull=function(){return scenarioProgrammeCard()+programmeOverviewBase();};
const programmeAgendaBase=renderAgenda;renderAgenda=function(){return scenarioProgrammeCard(true)+programmeAgendaBase();};
document.addEventListener('click',e=>{const b=e.target.closest('[data-programme-panel]');if(b){openPanel(b.dataset.programmePanel);$('panelBody').scrollTop=0;}});

// SOURCE: 97-workday-scenes.js
// Original small workday tableaux. They visualize actual operating activity;
// samples never create cargo, income, pupils or production in the simulation.
function workdayScenes(items){
 if(!gameOptions.effects||!gameOptions.decor||gameOptions.quality==='low'||gameOptions.reducedMotion||cam.zoom<.52)return [];
 const scenes=[],cap=fastRenderEnabled()?3:gameOptions.quality==='high'?12:7;
 for(let n=items.length-1;n>=0;n--){const item=items[n],b=item.b;if(!b||scenes.length>=cap)continue;const f=G.firms[b.firm];let scene=null;
  if(f&&!f.closed&&workingStaff(f).length&&f.production>0){if(['mill','sawmill','factory'].includes(b.kind))scene='machinery';else if(['farm','fishery','forestry'].includes(b.kind))scene='harvest';}
  if(f&&!f.closed&&b.kind==='wharf'&&workingStaff(f).length&&(f.cargoToday||0)>0)scene='loading';
  if(b.kind==='clinic'&&G.serviceProvision?.health?.paid>0&&G.serviceProvision.health.coverage>0)scene='care';
  if(b.kind==='school'&&G.serviceProvision?.school?.paid>0&&G.serviceProvision.school.coverage>0)scene='teaching';
  if(b.kind==='worksite'||b.redevelopment){const p=G.projects.find(p=>p.id===b.id);if(p&&!p.reason&&p.remaining>0)scene='construction';}
  if(!scene)continue;const front=point(item.w*.10,item.d*.48,0),portal=graph().portals.get(b.id),road=portal==null?null:roadCenter(portal);const x=road&&road[1]>=item.y?item.x*.35+road[0]*.65:item.x+front[0],y=road&&road[1]>=item.y?item.y*.35+road[1]*.65:item.y+front[1];scenes.push({kind:'workday',scene,b,f,x,y,dx:1,dy:.5});
 }
 return scenes;
}
function paintWorkdayScene(g,a,clock){
 const phase=clock+a.b.id*.17,x=Math.round(a.x),y=Math.round(a.y),skin=['#d6b38b','#c79570','#9d7358'][a.b.id%3];
 g.save();g.translate(x,y);g.fillStyle='#304b4530';g.beginPath();g.ellipse(0,2,16,4,.2,0,Math.PI*2);g.fill();
 const person=(px,py,color,scale=1,working=false)=>{g.save();g.translate(Math.round(px),Math.round(py));g.scale(scale,scale);const reach=working?Math.sin(phase*3)*2:0;
  g.fillStyle='#374e43';g.fillRect(-2,-2,2,4);g.fillRect(1,-1,2,3);g.fillStyle=color;g.fillRect(-3,-9,6,8);g.fillStyle=tone(color,.75);g.fillRect(2,-8,2,7);g.fillStyle=skin;g.fillRect(-2,-14,5,5);g.fillRect(-5,-8+reach,2,5);g.fillRect(4,-8-reach,2,5);g.fillStyle='#6a5a41';g.fillRect(-3,-15,7,2);g.restore();};
 if(a.scene==='machinery'){
  // A cast-iron flywheel and a short handling bench share one drive phase.
  polygon(g,[[-16,-4],[-3,-9],[14,-1],[1,5]],'#aa9674');segment(g,[-14,-2],[-14,5],'#6d7160',2);segment(g,[12,0],[12,7],'#6d7160',2);
  g.save();g.translate(-6,-10);g.transform(.85,.42,0,1,0,0);g.strokeStyle='#565f53';g.lineWidth=3;g.beginPath();g.arc(0,0,8,0,Math.PI*2);g.stroke();g.strokeStyle='#b2ad86';g.lineWidth=1;g.beginPath();g.arc(0,0,6,0,Math.PI*2);g.stroke();
  for(let j=0;j<6;j++){const turn=phase*1.8+j*Math.PI/3;segment(g,[0,0],[Math.cos(turn)*6,Math.sin(turn)*6],'#7d856c',1.5);}g.fillStyle='#d0bb83';g.fillRect(-2,-2,4,4);g.restore();
  const drift=(phase*.35)%1;if(a.b.kind==='sawmill'){segment(g,[0+drift*6,-5],[12+drift*6,1],'#b19464',4);segment(g,[1+drift*6,-6],[13+drift*6,0],'#d0b583',1);}else{polygon(g,[[3,-7],[9,-10],[14,-7],[8,-4]],'#c2ad7d');polygon(g,[[3,-7],[8,-4],[8,1],[3,-2]],'#9f895d');polygon(g,[[8,-4],[14,-7],[14,-2],[8,1]],'#ad996c');}
  person(14,8,'#6f8271',.86,true);
 }else if(a.scene==='harvest'){
  person(-5+Math.sin(phase*.6)*3,0,'#9c8054',.93,true);g.fillStyle='#ad8d5d';g.fillRect(5,-4,8,5);g.fillStyle='#d3be87';g.fillRect(5,-5,8,2);
  if(a.b.kind==='fishery'){segment(g,[-5,-9],[5,-21+Math.sin(phase)*1.2],'#b3a37a');segment(g,[5,-21+Math.sin(phase)*1.2],[11,-3],'#ddd7b099');}else for(let j=0;j<3;j++){segment(g,[6+j*2,-5],[6+j*2,-10],'#b8ad65');g.fillStyle='#d2bd72';g.fillRect(5+j*2,-11,3,3);}
 }else if(a.scene==='loading'){
  const step=(phase*.22)%1;person(-12+step*20,step*6,'#718b80',.93,true);g.fillStyle='#c8aa72';g.fillRect(-14+step*20,-5+step*6,7,5);segment(g,[-13+step*20,-4+step*6],[-8+step*20,-2+step*6],'#8d7854');box(g,.12,.12,.13,.11,0,5,'#b69a65');
 }else if(a.scene==='care'){
  person(-7,0,'#d3d8c3',.97,true);g.fillStyle='#477b66';g.fillRect(-9,-8,4,1);person(8,5+Math.sin(phase*.5),'#8b7765',.87);g.fillStyle='#c7b587';g.fillRect(0,-2,5,4);g.fillStyle='#607d6b';g.fillRect(1,-1,3,1);
 }else if(a.scene==='teaching'){
  person(-7,-1,'#687e77',1,true);person(3,5,'#ab8b60',.72);person(12,9,'#84956a',.70);segment(g,[-11,-11],[-1,-7],'#c7b994',2);
 }else{
  person(-5,1,'#9c855b',.93,true);g.fillStyle='#dbc183';g.fillRect(-8,-14,7,3);const angle=Math.sin(phase*3)*.65;segment(g,[-1,-9],[6+angle*4,-16+angle*5],'#7b6f52',2);segment(g,[3+angle*4,-17+angle*5],[9+angle*4,-15+angle*5],'#66776e',3);polygon(g,[[6,2],[13,-1],[18,2],[11,5]],'#b9a27b');
 }
 g.restore();
}

// SOURCE: 98-charter-ui.js
function charterPlan(){return `<svg class="charter-plan" viewBox="0 0 82 82" role="img" aria-label="Original town and five adjoining regional districts"><rect x="0" y="0" width="56" height="56" fill="#78946b" stroke="#344f3d" stroke-width=".5"/>${ANNEX_PARCELS.map(p=>`<rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" fill="${G.charter.owned.includes(p.id)?'#78946b':p.id===parcelFocus?'#d4b873':'#d7d3b3'}" stroke="#536c4b" stroke-width=".5"/>`).join('')}<path d="M5 0 4 18 6 30 4 49 5 65 4 80" stroke="#7baba4" stroke-width="3" fill="none"/><ellipse cx="66" cy="22" rx="6" ry="8" fill="#7baba4"/><text x="18" y="29" font-size="4" fill="#fff3d5">ORIGINAL TOWN</text></svg>`;}
function charterPanel(){
 const area=CHARTER_BASE*CHARTER_BASE+ANNEX_PARCELS.filter(p=>G.charter.owned.includes(p.id)).reduce((n,p)=>n+p.w*p.h,0);
 return `<details id="charterOffice" class="charter-accordion"><summary>Expand the borough · ${ANNEX_PARCELS.length-G.charter.owned.length} districts available</summary>`+head('Expand the borough')+`<section class="charter-office"><h3>New land, a real civic commitment</h3><p class="desc">The original 56 × 56 town retains its rights. Five substantial outer districts extend this region to 80 × 80. A deed makes new land available for development; it does not create roads, workers, utilities or service coverage. Existing private property titles remain unchanged.</p>${charterPlan()}${strip('Chartered surface',fmt(area)+' regional tiles')}${strip('Outer districts acquired',G.charter.owned.length+' / '+ANNEX_PARCELS.length)}<div class="btnrow"><button data-charter-overview>View regional boundaries</button><button data-charter-home>Return to town</button></div></section>`+
 ANNEX_PARCELS.map(p=>{const q=parcelSurvey(p),owned=G.charter.owned.includes(p.id),near=parcelAdjacent(p),deed=G.charter.deeds.find(d=>d.id===p.id);return `<section class="charter-district ${p.id===parcelFocus?'selected':''}" data-parcel-card="${p.id}"><small>${owned?'DEED RECORDED':near?'REGIONAL LAND AVAILABLE':'ADJOINING DEED REQUIRED'}</small><h3>${esc(p.name)}</h3><p class="desc">${esc(p.description)}</p>${strip('District surface',q.area+' tiles · '+p.w+' × '+p.h)}${strip('Land / water',q.land+' / '+q.water+' tiles')}${strip(owned?'Price paid':'Development-rights price',money(owned?deed.price:q.price))}${owned?strip('Acquired','Day '+deed.day):tip(near?'A connection from existing streets is still required. New households and firms face the usual utility bills, paid staffing and local service catchments.':'Acquire County Ridge or Orchard Downs before this far corner.')}<div class="btnrow"><button data-parcel-preview="${p.id}">Preview district</button>${owned?'':`<button data-parcel-buy="${p.id}" ${!near||G.treasury<q.price?'disabled':''}>Review purchase · ${money(q.price)}</button>`}</div>${!owned&&G.treasury<q.price?`<p class="desc">Treasury shortfall: ${money(q.price-G.treasury)}. This is a one-time land outlay; retain funds for construction and recurring commitments.</p>`:''}</section>`;}).join('')+'</details>';
}
function revealCharterOffice(){const office=$('charterOffice');if(office)office.open=true;}
function previewParcel(id){const p=ANNEX_PARCELS.find(p=>p.id===id);if(!p)return;parcelFocus=id;overlay='charter';const center=iso(p.x+p.w/2,p.y+p.h/2);cam={x:center[0],y:center[1]+18,zoom:clamp(Math.min((cw-50)/((p.w+p.h)*36),(ch-100)/((p.w+p.h)*18)),.025,.55)};cam.y+=38/cam.zoom;closePanel();dirty=true;toast(p.name+': '+(G.charter.owned.includes(id)?'chartered land':'regional land · review its deed in Public Works'));}
function requestParcelPurchase(id){const p=ANNEX_PARCELS.find(p=>p.id===id);if(!p||G.charter.owned.includes(id)||!parcelAdjacent(p))return;const q=parcelSurvey(p),town=G;if(G.treasury<q.price){toast('Insufficient treasury for this district.');return;}
 showCustomEvent('LAND PURCHASE','Acquire '+p.name+'?',q.area+' new regional tiles, including '+q.land+' land and '+q.water+' water tiles. Pay '+money(q.price)+' to the regional land authority. Existing private titles stay intact. Roads, utilities, buildings and service staffing are separate commitments.',[{title:'Acquire the district',desc:'One-time price '+money(q.price)+'. The deed expands municipal development rights.',cost:q.price,apply:()=>{if(G!==town||!purchaseParcel(id,q.price)){toast('The quote is no longer valid. Review the district again.');return;}parcelFocus=id;openPanel('construction');revealCharterOffice();document.querySelector('[data-parcel-card="'+id+'"]')?.scrollIntoView({block:'start'});}},{title:'Keep the current boundary',desc:'No payment and no change to ownership.',apply:()=>{}}]);
}
let surveySignature='';
function updateRegionSurvey(){
 const signature=JSON.stringify([parcelFocus,G.charter?.owned]);if(signature===surveySignature)return;surveySignature=signature;
 $('surveyReview').disabled=!parcelFocus;$('surveyDistrict').innerHTML='<option value="" disabled '+(!parcelFocus?'selected':'')+'>Choose a district…</option>'+ANNEX_PARCELS.map((p,i)=>`<option value="${p.id}" ${parcelFocus===p.id?'selected':''}>${i+1}. ${esc(p.name)}${G.charter.owned.includes(p.id)?' · Owned':''}</option>`).join('');
}
function reviewSurveyDistrict(id){if(!ANNEX_PARCELS.some(p=>p.id===id))return;parcelFocus=id;openPanel('construction');revealCharterOffice();document.querySelector('[data-parcel-card="'+id+'"]')?.scrollIntoView({block:'start'});}
function charterLabelLayout(){
 const occupied=[],labels=[];for(const p of ANNEX_PARCELS.slice().sort((a,b)=>(b.id===parcelFocus)-(a.id===parcelFocus))){const index=ANNEX_PARCELS.indexOf(p),q=iso(p.x+p.w/2,p.y+p.h/2),x=cw/2+(q[0]-cam.x)*cam.zoom,y=ch/2+(q[1]-cam.y)*cam.zoom;
  let compact=cam.zoom<.20||parcelFocus!==p.id,text=(index+1)+'. '+p.name+(G.charter.owned.includes(p.id)?' · OWNED':'');
  const width=text.length*6.1+14;let box={x:x-width/2,y:y-11,w:width,h:22};
  if(occupied.some(a=>box.x<a.x+a.w+6&&box.x+box.w>a.x-6&&box.y<a.y+a.h+5&&box.y+box.h>a.y-5))compact=true;
  if(compact){text=String(index+1);box={x:x-11,y:y-11,w:22,h:22};}
  occupied.push(box);labels.push({p,index,text,compact,x,y,box});
 }return labels;
}
function charterSurveyTap(sx,sy,x,y){
 const label=charterLabelLayout().filter(a=>Math.abs(sx-a.x)<=Math.max(22,a.box.w/2)&&Math.abs(sy-a.y)<=22).sort((a,b)=>Math.hypot(sx-a.x,sy-a.y)-Math.hypot(sx-b.x,sy-b.y))[0],p=label?.p||parcelForTile(x,y);if(!p)return false;
 if(parcelFocus===p.id)reviewSurveyDistrict(p.id);else previewParcel(p.id);dirty=true;return true;
}
function drawCharterBounds(g){
 if(!G.charter)return;g.save();g.lineJoin='round';
 for(const p of ANNEX_PARCELS){const owned=G.charter.owned.includes(p.id);if(owned&&overlay!=='charter'&&parcelFocus!==p.id)continue;
  const points=[[p.x-.5,p.y-.5],[p.x+p.w-.5,p.y-.5],[p.x+p.w-.5,p.y+p.h-.5],[p.x-.5,p.y+p.h-.5]].map(([x,y])=>{const q=iso(x,y);return[q[0],q[1]+18]});
  g.strokeStyle=owned?'#bfd2a4':'#d4b777';g.lineWidth=(parcelFocus===p.id?2.5:1.2)/cam.zoom;g.setLineDash(owned?[]:[7/cam.zoom,5/cam.zoom]);g.beginPath();points.forEach((q,i)=>i?g.lineTo(...q):g.moveTo(...q));g.closePath();g.stroke();
 }
 if(overlay==='charter'||parcelFocus)for(const label of charterLabelLayout()){if(overlay!=='charter'&&label.p.id!==parcelFocus)continue;const q=iso(label.p.x+label.p.w/2,label.p.y+label.p.h/2),w=label.box.w/cam.zoom;
  g.font=(11/cam.zoom)+'px Arial';g.fillStyle=label.p.id===parcelFocus?'#e9cc8bed':'#f1ead3ed';g.fillRect(q[0]-w/2,q[1]-11/cam.zoom,w,22/cam.zoom);g.strokeStyle='#536c4b';g.lineWidth=1/cam.zoom;g.strokeRect(q[0]-w/2,q[1]-11/cam.zoom,w,22/cam.zoom);g.fillStyle='#29422e';g.textAlign='center';g.textBaseline='middle';g.fillText(label.text,q[0],q[1]);
 }
 g.setLineDash([]);g.restore();
}
$('surveyDistrict').addEventListener('change',e=>previewParcel(e.target.value));$('surveyReview').onclick=()=>reviewSurveyDistrict(parcelFocus||$('surveyDistrict').value);
const charterConstructionBase=renderConstructionFull;renderConstructionFull=function(){return charterPanel()+charterConstructionBase();};
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b||!G)return;if(b.dataset.parcelPreview)previewParcel(b.dataset.parcelPreview);if(b.dataset.parcelBuy)requestParcelPurchase(b.dataset.parcelBuy);if(b.hasAttribute('data-charter-home')){overlay='none';parcelFocus=null;closePanel();centerTownCamera();}if(b.hasAttribute('data-charter-overview')){overlay='charter';parcelFocus=null;closePanel();const p=iso(40,40);cam={x:p[0],y:p[1]+18,zoom:Math.max(.025,Math.min((cw-24)/RW,(ch-100)/RH))};cam.y+=38/cam.zoom;dirty=true;}});

const charterBackBase=window.__townArchive.back;window.__townArchive.back=()=>{if(!active&&!pendingEvent&&$('helpDialog').style.display==='none'){if(buildMode){closeBuildTool();return true;}if(overlay==='charter'){overlay='none';parcelFocus=null;centerTownCamera();return true;}}return charterBackBase();};

// SOURCE: 98-waterfront-art.js
// Original river craft. Animation samples only staffed fishing or paid cargo;
// its bounded visual clock never draws from the simulation's seeded RNG.
function drawWaterfrontPiers(g,visible){
 for(const f of G.firms){if(!['fishery','wharf'].includes(f.kind))continue;const b=readBuild(f.building);if(!b)continue;const p=iso(b.x+.5,b.y+.5);if(!visible(p[0],p[1],80))continue;const site=waterfrontSite(b.x,b.y,f.kind);if(!site)continue;const water=iso(site.id%T+.5,(site.id/T|0)+.5),dx=water[0]-p[0],dy=water[1]-p[1],length=Math.hypot(dx,dy)||1,px=-dy/length*5,py=dx/length*5;
  polygon(g,[[p[0]+px,p[1]+py],[water[0]+px,water[1]+py],[water[0]-px,water[1]-py],[p[0]-px,p[1]-py]],f.closed?'#897f62':'#b49a6d');
  for(let k=0;k<=6;k++){const t=k/6,x=p[0]+dx*t,y=p[1]+dy*t;segment(g,[x-px,y-py],[x+px,y+py],'#806e50');}
  for(const side of [-1,1]){const x=water[0]+px*side,y=water[1]+py*side;segment(g,[x,y+6],[x,y-5],'#6d6851',2);g.fillStyle='#d2bd88';g.fillRect(x-2,y-5,4,2);}
  if(!f.closed&&f.kind==='wharf'&&(f.cargoToday||0)>0&&workingStaff(f).length){const moving=gameOptions.effects&&!gameOptions.reducedMotion,phase=moving?(frameClock*.13+f.id*.17)%1:.5,t=.25+(phase<.5?phase*2:2-phase*2)*.7,x=p[0]+dx*t,y=p[1]+dy*t;segment(g,[x-5,y+1],[x+5,y+1],'#5e6a58',2);g.fillStyle='#4a584c';g.fillRect(x-4,y+2,2,2);g.fillRect(x+3,y+2,2,2);if(phase<=.5){g.fillStyle='#ceaf72';g.fillRect(x-3,y-6,6,6);g.fillStyle='#8c7654';g.fillRect(x,y-6,1,6);}}
 }
}
function fishingRoute(site){
 const w=waterNetwork(),path=[site.id],used=new Set(path);let current=site.id;
 for(let i=0;i<8;i++){const next=w.adjacent(current).filter(n=>!used.has(n)).sort((a,b)=>{const ax=a%T,bx=b%T;return ax-bx||a-b;})[0];if(next==null)break;path.push(next);used.add(next);current=next;}
 return path;
}
function waterRoutePose(path,travel,returning=false){
 const span=path.length-1,index=Math.min(span-1,Math.floor(travel)),fraction=travel-index,r=.18,cell=id=>[id%T+.5,(id/T|0)+.5];let a=cell(path[index]),b=cell(path[index+1]),position=[a[0]+(b[0]-a[0])*fraction,a[1]+(b[1]-a[1])*fraction],tangent=[b[0]-a[0],b[1]-a[1]],corner=null,u=0;
 if(fraction>1-r&&index+2<path.length){corner=[a,b,cell(path[index+2])];u=(fraction-(1-r))/(2*r);}else if(fraction<r&&index>0){corner=[cell(path[index-1]),a,b];u=(fraction+r)/(2*r);}
 if(corner){const [before,at,after]=corner,start=[at[0]-(at[0]-before[0])*r,at[1]-(at[1]-before[1])*r],end=[at[0]+(after[0]-at[0])*r,at[1]+(after[1]-at[1])*r];position=start.map((v,k)=>(1-u)*(1-u)*v+2*(1-u)*u*at[k]+u*u*end[k]);tangent=start.map((v,k)=>2*(1-u)*(at[k]-v)+2*u*(end[k]-at[k]));}
 const p=iso(...position),sign=returning?-1:1;return {x:p[0],y:p[1],gx:position[0],gy:position[1],dx:(tangent[0]-tangent[1])*36*sign,dy:(tangent[0]+tangent[1])*18*sign};
}
let waterVesselTown=null,waterVesselClock=0,waterVessels=new Map();
function waterfrontActors(visible){
 if(!gameOptions.traffic||!gameOptions.effects||gameOptions.reducedMotion||gameOptions.quality==='low'||cam.zoom<.32)return [];
 if(waterVesselTown!==G||frameClock<waterVesselClock){waterVessels=new Map();waterVesselTown=G;waterVesselClock=frameClock;}
 const elapsed=Math.min(.25,Math.max(0,frameClock-waterVesselClock));waterVesselClock=frameClock;
 const cap=fastRenderEnabled()?2:gameOptions.quality==='high'?10:6,actors=[],orders=new Map();
 for(const m of (G.waterway?.manifests||[]).slice().reverse())if(!orders.has(m.port))orders.set(m.port,m);
 for(const f of G.firms){if(!['fishery','wharf'].includes(f.kind))continue;const b=readBuild(f.building);if(!b||b.firm!==f.id){waterVessels.delete(f.id);continue;}
  const m=orders.get(f.id),fishing=f.kind==='fishery',working=!f.closed&&workingStaff(f).length>0,hasOrder=working&&(fishing?f.production>0:!!m),token=fishing?G.day:m?.id;
  let vessel=waterVessels.get(f.id);
  if(hasOrder&&(!vessel||!vessel.active&&vessel.lastToken!==token)){
   const site=waterfrontSite(b.x,b.y,f.kind),path=fishing?(site?fishingRoute(site):[]):m.path;
   if(path.length>=2&&(vessel||waterVessels.size<32)){vessel={id:f.id+(fishing?10000:50000),f,path:path.slice(),travel:0,cargo:fishing?'fish':m.good,quantity:fishing?f.production:m.qty,lastToken:token,active:true,turned:false,turnRemaining:0};waterVessels.set(f.id,vessel);}
  }
  if(vessel&&!vessel.active&&f.closed){waterVessels.delete(f.id);continue;}if(!vessel)continue;const span=vessel.path.length-1;
  // A vessel keeps the same paid load and continuous route across simulation
  // days. New manifests never teleport a boat or change its cargo mid-voyage.
  if(vessel.active){if(vessel.turnRemaining>0)vessel.turnRemaining=Math.max(0,vessel.turnRemaining-elapsed);else{vessel.travel+=elapsed*(fishing?.32:.48);if(!vessel.turned&&vessel.travel>=span){vessel.travel=span;vessel.turned=true;vessel.turnRemaining=1.2;}if(vessel.travel>=span*2){vessel.travel=0;vessel.active=false;}}}
  const returning=!vessel.active||vessel.travel>span||vessel.turned&&vessel.travel===span&&vessel.turnRemaining===0,travel=vessel.travel>span?span*2-vessel.travel:vessel.travel,pose=waterRoutePose(vessel.path,travel,returning);
  if(vessel.turnRemaining>0){const angle=Math.atan2(pose.dy,pose.dx)+Math.PI*(1-vessel.turnRemaining/1.2),length=Math.hypot(pose.dx,pose.dy);pose.dx=Math.cos(angle)*length;pose.dy=Math.sin(angle)*length;}
  if(G.tiles[Math.floor(pose.gy)*T+Math.floor(pose.gx)]===1||!visible(pose.x,pose.y,30))continue;actors.push({kind:'boat',...pose,returning,...vessel});
 }
 for(const id of waterVessels.keys())if(!G.firms[id]||!readBuild(G.firms[id].building))waterVessels.delete(id);
 return actors.slice(0,cap);
}
function paintWaterBoat(g,a,clock){
 const cargo=a.cargo!=='fish',length=cargo?17:10,width=cargo?6:4,m=Math.hypot(a.dx,a.dy)||1;g.save();g.translate(a.x,a.y+(gameOptions.reducedMotion?0:Math.sin(clock*1.7+a.id)*.45));g.transform(a.dx/m,a.dy/m,-a.dy/m*.85,a.dx/m*.65,0,0);
 const wake=.55+Math.sin(clock*5+a.id)*.15;if(a.active)for(let j=0;j<3;j++){g.globalAlpha=(.28-j*.06)*wake;segment(g,[-length-2-j*4,-width-j*2],[-length+3-j*4,width+j*2],'#e3e7c8',1);}g.globalAlpha=1;
 polygon(g,[[-length,-width],[length-3,-width],[length+3,0],[length-3,width],[-length,width],[-length-2,0]],'#425d57');polygon(g,[[-length+1,-width+1],[length-3,-width+1],[length,0],[length-3,width-1],[-length+1,width-1]],cargo?'#c3b88e':'#ad8b5d');
 if(cargo){g.fillStyle='#e4d5ac';g.fillRect(-length+2,-width+1,6,width*2-2);g.fillStyle='#648d91';g.fillRect(-length+6,-width+1,2,width*2-2);if(!a.returning){for(let j=0;j<3;j++){g.fillStyle=['#b77851','#999c68','#cfb36f'][j];g.fillRect(-4+j*5,-width+1,4,width*2-2);g.fillStyle='#76654c';g.fillRect(-4+j*5,-width+1,1,width*2-2);}}}else{g.fillStyle='#718d78';g.fillRect(-3,-2,5,4);g.fillStyle='#d2b088';g.fillRect(-1,-3,2,2);segment(g,[2,-width],[5,-width-5],'#dbd1a4');}
 if(!cargo&&a.active&&a.travel>(a.path.length-1)*.7&&a.travel<(a.path.length-1)*1.3){const sway=Math.sin(clock*2+a.id);polygon(g,[[0,-width],[7,-width-8+sway],[-5,-width-10+sway]],'#b9c6a050');for(let j=0;j<4;j++)segment(g,[0,-width],[-5+j*4,-width-9+sway],'#c4c9a780');}segment(g,[-length+1,-width],[length-3,-width],'#e1c995');g.restore();
}
function waterfrontPanel(){const state=G.waterway||{},wharves=G.firms.filter(f=>f.kind==='wharf'&&!f.closed),fisheries=G.firms.filter(f=>f.kind==='fishery'&&!f.closed);return `<details class="council-card"><summary>Working waterfront · fisheries & river cargo</summary><p class="desc">Build beside real water and a connected road. Fisheries turn staffed catch into food. Cargo wharves require a river outlet; an enclosed lake can support fishing, but cannot carry regional exports. Exporters compare road and river freight costs. A dock without crews or competitive orders earns nothing.</p><div class="statgrid">${stat('Trading fisheries',fisheries.length)}${stat('Trading cargo wharves',wharves.length)}${stat('River cargo today',policyNumber(state.todayCargo||0))}${stat('Wharf receipts today',money(state.todayFees||0))}</div><p class="desc">A cargo manifest belongs to its paying regional buyer after collection. Boats show paid cargo voyages and fishing trips. Export ownership passes to the regional buyer on collection; follow the accounts to see stock and payments.</p><button data-waterfront-camera="1">Visit the river landing</button><button data-waterfront-build="1">Choose a waterfront business</button></details>`;}
const waterfrontConstructionBase=renderConstructionFull;renderConstructionFull=function(){return waterfrontConstructionBase()+waterfrontPanel();};
document.addEventListener('click',e=>{if(e.target.closest('[data-waterfront-camera]')){const b=G.buildings.find(b=>b.kind==='wharf')||G.buildings.find(b=>b.kind==='fishery')||{x:5,y:27},p=iso(b.x+.5,b.y+.5);cam={x:p[0]+40,y:p[1],zoom:1.15};closePanel();dirty=true;}if(e.target.closest('[data-waterfront-build]')){constructionCategory='waterfront';openPanel('construction');$('panelBody').scrollTop=0;}});

let selectedWaterTrip=null;
function inspectWaterTripAt(x,y){
 const radius=22/Math.max(.32,cam.zoom),boat=waterfrontActors(()=>true).filter(a=>Math.hypot(a.x-x,a.y-y)<radius).sort((a,b)=>Math.hypot(a.x-x,a.y-y)-Math.hypot(b.x-x,b.y-y))[0];if(!boat)return false;
 selectedWaterTrip={firm:boat.f.id,token:boat.lastToken,cargo:boat.cargo,quantity:boat.quantity,path:boat.path.slice(),returning:boat.returning};selected={id:boat.f.building};openPanel('inspect');dirty=true;return true;
}
function drawSelectedWaterRoute(g){
 if(!selectedWaterTrip)return;if(!selected||readBuild(selected.id)?.firm!==selectedWaterTrip.firm){selectedWaterTrip=null;return;}
 const path=waterVessels.get(selectedWaterTrip.firm)?.path||selectedWaterTrip.path;g.save();g.strokeStyle='#f2d492';g.lineWidth=2/Math.max(.32,cam.zoom);g.setLineDash([5/cam.zoom,4/cam.zoom]);g.beginPath();path.forEach((id,i)=>{const q=iso(id%T+.5,(id/T|0)+.5);i?g.lineTo(...q):g.moveTo(...q)});g.stroke();g.restore();
}
function selectedWaterInfo(){const live=selectedWaterTrip&&waterVessels.get(selectedWaterTrip.firm);return live?{cargo:live.cargo,quantity:live.quantity,journey:!live.active?'Moored at its landing':live.turnRemaining>0?'Turning at the destination':live.travel>live.path.length-1?'Returning to its landing':'Outbound from its landing'}:selectedWaterTrip?{...selectedWaterTrip,journey:'Previously selected voyage'}:null;}
const waterInspectBase=renderInspectFull;renderInspectFull=function(){const info=selectedWaterInfo();return (info&&readBuild(selected?.id)?.firm===selectedWaterTrip.firm?head(info.cargo==='fish'?'Fishing trip':'Paid regional cargo voyage')+strip('Sampled load',policyNumber(info.quantity)+' '+(info.cargo==='fish'?'food units':info.cargo))+strip('Journey',info.journey)+tip('The highlighted route follows connected water. The business accounts below record the actual catch or paid freight.'):'' )+waterInspectBase();};

function drawWaterLife(g,visible){
 if(!gameOptions.effects||gameOptions.reducedMotion||gameOptions.quality==='low'||cam.zoom<.32)return;
 const cap=fastRenderEnabled()?3:gameOptions.quality==='high'?14:8;let count=0;
 for(const id of waterNetwork().nodes){if(G.tiles[id]!==2||hash(id)%9!==0)continue;const p=iso(id%T+.5,(id/T|0)+.5);if(!visible(p[0],p[1],20))continue;const phase=(frameClock*.24+(hash(id)%101)/101)%1,light=Math.sin(phase*Math.PI);g.globalAlpha=light*.35;
  segment(g,[p[0]-11+phase*5,p[1]+5-phase*2],[p[0]+7+phase*5,p[1]-4-phase*2],'#deead0',1);g.globalAlpha=light*.18;segment(g,[p[0]-6,p[1]+8],[p[0]+13,p[1]-1],'#c8dfc8',1);g.globalAlpha=1;if(++count>=cap)break;
 }
}

// SOURCE: 99-instrumentation.js
// Read-only / test instrumentation. No remote telemetry is used.
window.__townTest={view:()=>({camera:{...cam},touchCount:touches.size,pointer:{down:pointer.down,moved:pointer.moved,pinch:pointer.pinch}}),goods:()=>goodsBalance(),validate:()=>validateTown(),observations:()=>G.observations,perf:()=>perfStats,capture:(opts={})=>{if(opts.month){G.month=opts.month;staticDirty=true}if(opts.night!==undefined)nightMode=opts.night;if(opts.overlay!==undefined)overlay=opts.overlay;if(opts.zoom)cam.zoom=opts.zoom;if(opts.x)cam.x=opts.x;if(opts.y)cam.y=opts.y;dirty=true;updateHeader();draw();return true;},systems:()=>({housing:G.housingMarket,investors:G.investors,accounts:G.accounts,transactions:G.transactions,experiments:G.policyExperiments}),inbox:()=>G.councilInbox||[],offerPetition:()=>offerCouncilEvent(),reviewPetition:reviewCouncilInbox,finance:()=>({banks:G.banks,loans:G.loans,indicators:G.finance,deposits:G.banks.map(b=>bankDeposits(b.id))}),takeLoan:(kind,id,amount,term)=>bankLoan(kind,id,amount,term),bankFailure:(id)=>liquidateBank(G.banks[id],'Test insolvency'),reverseLand:()=>reverseRedevelopment(),renderBench:(n=100)=>{let t=performance.now();for(let i=0;i<n;i++){dirty=true;draw()}return Math.round((performance.now()-t)/n*100)/100},advanceTraffic:(dt=1)=>{trafficUpdate(dt);return traffic.length},traffic:()=>traffic.map(v=>({id:v.id,route:v.path,position:vehiclePosition(v),segment:v.segment,fraction:v.fraction,wait:v.wait,age:v.age})),road:()=>roadMetrics(),regional:()=>({landUse:G?.landUse,fieldCount:G?.fieldCount,airport:G?.airport,demand:cityDemand(),startFields:()=>farmDistrictExpansion(cityDemand()),startRedevelopment:()=>urbanRedevelopment(cityDemand()),startAirfield:()=>airfieldInvestment(cityDemand()),airfieldCandidate:()=>airfieldCandidate(),firmTypes:G?.firms.reduce((t,f)=>(t[f.kind]=(t[f.kind]||0)+Number(!f.closed),t),{})}),development:()=>({development:G?.development,metro:G?.metro,privateRoads:G?.privateRoads}),autogrow:()=>autonomousDevelopment(),path:(a,b)=>routeBetween(a,b),spawn:()=>beginVehicle(),invalidateRoads:()=>invalidateRoads(),get:()=>({day:G?.day,treasury:G?.treasury,debt:G?.debt,population:G?.stats.population,employment:G?.stats.employment,hardship:G?.stats.hardship,businesses:G?.stats.businesses,approval:G?.council.approval,cases:G?.cases.length,total:G?totalMoney():0,regional:G?.region,hhCash:G?.households.reduce((n,h)=>n+h.cash,0),firmCash:G?.firms.reduce((n,f)=>n+f.cash,0),events:G?.events.length,policy:G?.policy,stats:G?.stats,achievements:G?.achievements,pending:!!pendingEvent}),
 step:(n=1)=>{simulationBusy=true;try{for(let i=0;i<n;i++){if(pendingEvent){const ix=pendingEvent.choices.findIndex(c=>!c.cost||G.treasury>=c.cost);$('eventChoices').querySelectorAll('button')[Math.max(0,ix)]?.click()}tick()}}finally{simulationBusy=false;updateHeader();}return G.stats},
 save:()=>archivePayload(),load:(t)=>hydrateSave(t),choose:(i)=>{$('eventChoices').querySelectorAll('button')[i]?.click()},
 reset:(sc='settlement',seedValue=42)=>{chosenScenario=sc;seed(seedValue);invalidateRoads();updateHeader();if(active)renderPanel(active);draw();return G.stats},set:(k,v)=>{G.policy[k]=v;recompute()}};
})();
