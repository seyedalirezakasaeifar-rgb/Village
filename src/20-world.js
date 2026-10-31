function seed(seedValue=42){
 resetTownTransientUI();
 crewDay=-1;crewsUsed=new Map();regionalCrews=0;rngState=(Number(seedValue)>>>0)||42;visualState=918273;traffic=[];trafficClock=0;frameClock=0;trafficElapsed=0;vehicleSerial=0;intersectionGates.clear();
 draftPolicy={};roadBatchDirty=false;
 const tiles=new Array(T*T).fill(0),streets=foundingStreetPlan();
 for(let y=0;y<T;y++)for(let x=0;x<T;x++){
   let road=streets.classes[y*T+x]!=null;
   if(road)tiles[y*T+x]=1;
   else if(x<5+Math.sin(y*.2)*1.7 || x===5 && y%4===0)tiles[y*T+x]=2;
   else if((x<11||x>46||y<11||y>46)&&random()<.39)tiles[y*T+x]=3;
   else if(random()<.085)tiles[y*T+x]=3;
 }
 G={roadClasses:streets.classes,streetNames:streets.names,climateSeasons:gameOptions.seasons,climateWeather:gameOptions.weather,version:3,day:1,year:1,month:1,tiles,buildings:[],homes:[],people:[],households:[],firms:[],policy:{...defaults},
    treasury:90000,debt:0,publicReserve:0,region:15000000,projects:[],metro:{cash:0,stations:[],lines:[],fare:2.75,rides:0,revenue:0,expenses:0,dailyRides:0,daysInDeficit:0,operating:false,invested:0},development:{homes:0,firms:0,roads:0,stations:0,lastReport:null,decisions:[]},privateRoads:[],landUse:{},fieldOwner:{},fieldCount:{},airport:null,autoBuild:true,nextId:1,history:[],events:[],journal:[],records:[],stats:{},cumulative:{incomeTax:0,profitTax:0,propertyTax:0,foodTax:0,utilityTax:0,commercialRate:0,permits:0,tariffs:0,spending:0,crime:0,fires:0,welfare:0},cases:[],speed:1,scenario:chosenScenario,achievements:[],council:{approval:65,elections:0,confidence:65,factions:{workers:60,merchants:62,homeowners:60,public:66},lastApproval:65},ambition:chosenScenario==='regional'?'education':chosenScenario==='hardtimes'?'families':'balanced',ambitionDays:{},lastMonth:{},crisesHandled:0,policyOutcomes:[],construction:0,worldSeed:Math.floor(random()*99999999),weather:'clear',season:0,regionalDemand:1,neighborhoods:[],lastEventDay:1,unrest:0,education:46,health:74,historyLong:[]};
 const add=(kind,x,y,opt={})=>{if(G.tiles[roadId(x,y)]===1||G.tiles[roadId(x,y)]===2)throw Error('Founding structure overlaps a roadway or river');G.tiles[roadId(x,y)]=0;let b={id:G.nextId++,kind,x,y,value:Math.round(types[kind].cost*10),condition:100,owner:-1,firm:-1,hh:-1,...opt};G.buildings.push(b);return b};
 add('townhall',26,26,{value:150000});add('police',24,26,{value:90000});add('fire',29,26,{value:80000});add('clinic',28,29,{value:74000});add('school',25,28,{value:70000});add('square',28,26,{value:15000});
 const firms=['grocer','grocer','grocer','bakery','bakery','mill','mill','farm','farm','farm','farm','forestry','forestry','sawmill','quarry','contractor','contractor','grocer','bakery','farm','tavern','office','factory','warehouse'];
 let slots=[];
 for(let y=7;y<49;y++)for(let x=7;x<49;x++)if(canPlace(x,y,true))slots.push([x,y]);
 slots=slots.filter(([x,y])=>Math.abs(x-27)+Math.abs(y-27)<35).sort((a,b)=>{let da=Math.abs(a[0]-27)+Math.abs(a[1]-27),db=Math.abs(b[0]-27)+Math.abs(b[1]-27);return da-db+rn(-2,2)});
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
 G.events.push({day:1,text:'A new council has taken responsibility for the prosperity of the Vale.',type:'neutral'});setupScenario();seedBanks();ensureSystems();initializeScenario();ensureMarketModel();G.scenarioSeed=seedValue;G.accounts={baseline:totalMoney(),maxError:0};housingMarketDay(true);recordObservation();initializeScenarioProgramme();save();
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
  const ax=x+dx,ay=y+dy,id=roadId(ax,ay),owner=buildingAt(ax,ay);
  if(![0,3].includes(G.tiles[id])||G.landUse?.[id]||(owner&&owner.id!==ignore?.id))return false;
  if(nearRoad(ax,ay))access=true;
 }
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
function regionBuy(f,good,amount,price=marketPrice(good)){if(!f||!G.region)return 0;const portal=graph().portals.get(f.building);const linked=portal!=null&&graph().parts[portal]===graph().mainPart;const access=linked?1:0;const regionalDemand=(1+G.buildings.filter(b=>b.kind==='square').length*.025+G.firms.filter(f=>f.kind==='warehouse'&&!f.closed).length*.065+(G.airport?.operating ? .13 : 0))*(G.scenario==='hardtimes'&&G.day<540?.52:G.scenario==='frontier'&&G.day<280?.78:1);const qty=Math.max(0,Math.min(f.stock[good]||0,amount*access*regionalDemand*clamp(G.regionalDemand||1,.30,1.3),G.region/Math.max(price,1)));const cash=qty*price;if(G.market)G.market.externalSales+=cash;takeInventory(f,good,qty,true);f.cash+=cash;G.region-=cash;goodsEntry(good,'exports',qty);f.revenue+=cash;return qty}
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
