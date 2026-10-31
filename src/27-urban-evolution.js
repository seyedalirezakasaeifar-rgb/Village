// Urban planning owns no renderer or transport state. Spatial caches are derived;
// only mayoral plans, neighbourhood history and renewal cooldowns are archived.
const URBAN_BLOCK=8;
const URBAN_PLANS={market:'Market-led mixed use',residential:'Residential neighbourhood',agriculture:'Protected agricultural belt',employment:'Employment district',civic:'Civic reserve'};
let urbanCache=null;
function ensureUrban(){return G.urban||(G.urban={version:1,revision:0,zones:{},districts:{},renewals:[],lastReview:0});}
function urbanBlockKey(x,y){return Math.floor(x/URBAN_BLOCK)+':'+Math.floor(y/URBAN_BLOCK);}
function invalidateUrban(){urbanCache=null;}
function urbanSpatial(){
 // Staffing, closures and household income can change daily. A monthly cache
 // must not carry stale rent/land-value inputs across a save and restore.
 const u=ensureUrban(),net=graph(),day=G.day;
 if(urbanCache?.town===G&&urbanCache.net===net&&urbanCache.day===day&&urbanCache.count===G.buildings.length&&urbanCache.revision===u.revision)return urbanCache;
 const residentsByHome=new Map();for(const h of G.households)if(h.people.length){if(!residentsByHome.has(h.home))residentsByHome.set(h.home,[]);residentsByHome.get(h.home).push(h);}
 const homes=new Float32Array(T*T),jobs=new Float32Array(T*T),industry=new Float32Array(T*T),amenity=new Float32Array(T*T),blocks={};
 for(const b of G.buildings){
  const f=G.firms[b.firm],key=urbanBlockKey(b.x,b.y),block=blocks[key]||(blocks[key]={key,x:Math.floor(b.x/8)*8,y:Math.floor(b.y/8)*8,buildings:[],households:[],residents:0,farms:0,jobs:0,retail:0,industry:0,income:0,rent:0,condition:0});
  block.buildings.push(b.id);block.condition+=b.condition;
  const residents=residentsByHome.get(b.id)||[];
  for(const h of residents){block.households.push(h.id);block.residents+=h.people.length;block.income+=Math.max(0,(h.income||0)-(h.tax||0));block.rent+=h.rent||0;}
  const units=['home','apartment','tower'].includes(b.kind)?(b.kind==='tower'?9:b.kind==='apartment'?4:1):0;
  const heavy=f&&!f.closed&&['factory','quarry','sawmill','forestry','wharf'].includes(f.kind),work=f&&!f.closed?f.jobs:0,civic=['school','clinic','park','square','college'].includes(b.kind);
  if(f&&!f.closed){block.jobs+=f.jobs;if(f.kind==='farm')block.farms++;if(f.kind==='grocer'||f.kind==='tavern')block.retail++;if(heavy)block.industry++;}
  for(let dy=-6;dy<=6;dy++)for(let dx=-6;dx<=6;dx++){
   const d=Math.abs(dx)+Math.abs(dy),x=b.x+dx,y=b.y+dy;if(d>6||x<0||y<0||x>=T||y>=T)continue;const id=roadId(x,y),weight=(7-d)/7;
   homes[id]+=units*weight;jobs[id]+=work*weight*.14;if(heavy)industry[id]+=weight;if(civic)amenity[id]+=weight;
  }
 }
 const incomes=Object.values(blocks).filter(b=>b.residents).map(b=>b.income/b.residents).sort((a,b)=>a-b),median=incomes[Math.floor(incomes.length/2)]||15;
 for(const b of Object.values(blocks)){
  b.condition/=Math.max(1,b.buildings.length);b.perPersonIncome=b.income/Math.max(1,b.residents);b.rentBurden=b.rent/Math.max(1,b.income);
  b.incomeBand=b.residents?(b.perPersonIncome<median*.72?'Lower income':b.perPersonIncome>median*1.4?'Higher income':'Middle income'):'No resident income';
  b.character=b.industry>=2?'Employment quarter':b.retail>=2&&b.jobs>12?'Market centre':b.farms&&b.residents<12?'Agricultural belt':b.residents>=12?'Residential neighbourhood':b.buildings.length>=3?'Mixed quarter':'Open countryside';
 }
 return urbanCache={town:G,net,day,count:G.buildings.length,revision:u.revision,homes,jobs,industry,amenity,blocks,median};
}
function urbanDescriptor(x,y){
 const c=urbanSpatial(),id=roadId(x,y),block=c.blocks[urbanBlockKey(x,y)],u=ensureUrban(),plan=u.zones[urbanBlockKey(x,y)]?.plan||'market',district=u.districts[urbanBlockKey(x,y)];
 const density=c.homes[id]||0,work=c.jobs[id]||0,pollution=c.industry[id]||0,access=nearRoad(x,y),central=Math.max(0,1-(Math.abs(x-27)+Math.abs(y-27))/35);
 return {key:urbanBlockKey(x,y),plan,density,work,pollution,amenity:c.amenity[id]||0,landValue:Math.round(600+(density*130+work*95+central*900+(c.amenity[id]||0)*170)*(access?1:.55)),agricultural:plan==='agriculture'||density<2.8&&central<.58,name:district?.name||'Unsettled land',character:district?.character||block?.character||'Open countryside',incomeBand:block?.incomeBand||'No resident income',perPersonIncome:block?.perPersonIncome||0,rentBurden:block?.rentBurden||0,condition:block?.condition||100,retailCentre:false};
}
function urbanPlacementReason(x,y,kind){
 if(['road','repair','inspect','urban_clearance','plot'].includes(kind))return '';
 const d=urbanDescriptor(x,y),housing=['home','apartment','tower'].includes(kind),heavy=['farm','factory','quarry','forestry','sawmill','warehouse','wharf'].includes(kind),civic=['school','clinic','fire','police','park','square','courthouse','watchtower','metro_station','bus_depot','skytrain_station','transit_depot','elevated_station'].includes(kind);
 if(d.plan==='agriculture'&&!['farm','forestry','park','fire','road'].includes(kind))return 'Protected agricultural belt: revise its neighbourhood plan before approving urban construction.';
 if(d.plan==='residential'&&heavy)return 'Residential plan: reserve this neighbourhood for homes, shops and services.';
 if(d.plan==='employment'&&housing)return 'Employment plan: connect homes in an adjoining neighbourhood.';
 if(d.plan==='civic'&&!civic)return 'Civic reserve: this land is held for services and public space.';
 if(kind==='farm'&&!d.agricultural)return 'Urban land is unsuitable for a new farm. Use the outer agricultural belt or designate a protected farm district.';
 return '';
}
const parcelPlacementReason=districtPlacementReason;
districtPlacementReason=function(x,y,kind){return parcelPlacementReason(x,y,kind)||urbanPlacementReason(x,y,kind);};
function urbanPlanChange(x,y,plan){
 if(!owns(URBAN_PLANS,plan)||!charterOwns(x,y))return {ok:false,reason:'Acquire the land first.'};const u=ensureUrban(),key=urbanBlockKey(x,y),old=u.zones[key];
 if(old?.plan===plan)return {ok:false,reason:'This plan is already recorded.'};
 if(old&&G.day-old.day<90)return {ok:false,reason:'Neighbourhood plans have a 90-day review period.'};
 const cost=old?1800:600;if(G.treasury<cost)return {ok:false,reason:'The planning survey requires '+money(cost)+'.'};
 G.treasury-=cost;G.region+=cost;G.cumulative.spending+=cost;u.zones[key]={plan,day:G.day};u.revision++;invalidateUrban();staticDirty=true;dirty=true;save();return {ok:true,reason:URBAN_PLANS[plan]+' recorded. Existing titles remain legal.'};
}
function urbanDistrictReview(){
 const u=ensureUrban();if(u.lastReview===G.day)return;const c=urbanSpatial(),active=new Set();
 for(const [key,b] of Object.entries(c.blocks)){
  if(b.buildings.length<3)continue;active.add(key);const old=u.districts[key];
  if(!old){u.districts[key]={name:['Oak','Cedar','Willow','Maple','River','Stone','Meadow','Market','Birch','Alder','Orchard','Pine','Elm','Laurel','Ash','Beech'][(b.x/8+(G.worldSeed%16))%16]+' '+['Quarter','Ward','Gardens','Heights','Terrace','Crossing','Meadows','Commons','Park','Reach','Grove','Vale','Gate','Fields','Square','Hill'][(b.y/8+(hash(G.worldSeed)%16))%16],character:b.character,since:G.day,changed:G.day};continue;}
  delete old.vacantSince;
  if(old.character===b.character){delete old.proposed;delete old.proposedSince;continue;}
  if(old.proposed!==b.character){old.proposed=b.character;old.proposedSince=G.day;}
  else if(G.day-old.proposedSince>=90){old.character=b.character;old.changed=G.day;delete old.proposed;delete old.proposedSince;}
 }
 for(const [key,d] of Object.entries(u.districts))if(!active.has(key)){d.vacantSince=d.vacantSince||G.day;if(G.day-d.vacantSince>=180)delete u.districts[key];}
 u.lastReview=G.day;
}
function validateUrban(data){
 if((data.projects||[]).some(p=>p.urbanEscrow!=null&&(!p.retailCentre||p.kind!=='firm'||p.firmKind!=='grocer'||!Number.isFinite(p.urbanEscrow)||p.urbanEscrow!==28000||p.capital!==28000)))return false;
 const u=data.urban;if(u==null)return true;if(!u||u.version!==1||!Number.isSafeInteger(u.revision)||u.revision<0||!u.zones||typeof u.zones!=='object'||Array.isArray(u.zones)||!u.districts||typeof u.districts!=='object'||Array.isArray(u.districts)||!Array.isArray(u.renewals)||u.renewals.length>80||!Number.isInteger(u.lastReview)||u.lastReview<0||u.lastReview>data.day)return false;
 const validKey=k=>{if(!/^\d+:\d+$/.test(k))return false;const [x,y]=k.split(':').map(Number);return x<T/8&&y<T/8;};
 if(Object.keys(u.zones).length>T*T/64||Object.keys(u.districts).length>T*T/64)return false;
 if(!Object.entries(u.zones).every(([k,z])=>validKey(k)&&z&&owns(URBAN_PLANS,z.plan)&&Number.isInteger(z.day)&&z.day>=1&&z.day<=data.day))return false;
 return Object.entries(u.districts).every(([k,d])=>validKey(k)&&d&&typeof d.name==='string'&&d.name.length<=50&&typeof d.character==='string'&&d.character.length<=50&&Number.isInteger(d.since)&&d.since>=1&&d.since<=data.day&&Number.isInteger(d.changed)&&d.changed>=d.since&&d.changed<=data.day&&(!d.proposed||(typeof d.proposed==='string'&&d.proposed.length<=50&&Number.isInteger(d.proposedSince)&&d.proposedSince<=data.day)))&&u.renewals.every(r=>r&&Number.isInteger(r.day)&&r.day>=1&&r.day<=data.day&&typeof r.action==='string'&&r.action.length<=100&&Number.isFinite(r.cost)&&r.cost>=0);
}
function urbanTitleAccount(b){
 const title=b.title;
 if(title?.kind==='household')return G.households[title.id]||null;
 if(title?.kind==='investor')return G.investors[title.id]||null;
 if(title?.kind==='firm')return G.firms[title.id]||null;
 return b.owner>=0?G.households[b.owner]:b.owner===-2?propertyInvestor():null;
}
function urbanVacancies(exclude,includeReserved=true){
 const net=graph(),result=[];
 for(const b of G.buildings){if(b.id===exclude||b.redevelopment||!includeReserved&&b.relocationReserve||!['home','apartment','tower'].includes(b.kind))continue;const port=net.portals.get(b.id);if(port==null||net.parts[port]!==net.mainPart)continue;
  const capacity=b.kind==='tower'?9:b.kind==='apartment'?4:1,occupied=G.households.filter(h=>h.home===b.id&&h.people.length).length;
  for(let n=occupied;n<capacity;n++)result.push(b);
 }return result;
}
function urbanRelocationWorkerRoutes(h,dest){
 const routes=[];for(const id of h.people){const p=G.people[id],f=p?.job>=0?G.firms[p.job]:null;if(!p||p.deceased||p.movedAway||p.commuteBlocked||!f||f.closed)continue;const trip=typeof migrationCanReach==='function'?migrationCanReach(dest,f):null;routes.push({person:id,firm:f.id,reachable:!!trip,mode:trip?.mode||null,distance:trip?.distance??null});}return {ok:routes.every(r=>r.reachable),routes};
}
function urbanRelocationServiceRoutes(dest){
 const net=graph(),port=net.portals.get(dest.id);return Object.fromEntries(['health','school'].map(kind=>{const standard=CIVIC_STANDARDS[kind],limit=kind==='health'?60:40,near=[];if(port!=null)for(const b of G.buildings){if(b.kind!==standard.building||!isPublicFacility(b))continue;const facility=net.portals.get(b.id);if(facility==null||net.parts[facility]!==net.parts[port])continue;const distance=roadDistancesFrom(facility,net)[port];if(distance>=0)near.push(distance);}near.sort((a,b)=>a-b);return [kind,{distance:near[0]??null,limit,within:near.length>0&&near[0]<=limit}];}));
}
function urbanClearanceReviewKey(q){return JSON.stringify([q.building,q.total,q.fields,q.households,q.relocations,q.workers]);}
const urbanPropertyGuards=[];
function urbanRegisterPropertyGuard(guard){if(typeof guard==='function'&&!urbanPropertyGuards.includes(guard))urbanPropertyGuards.push(guard);}
function urbanClearanceQuote(x,y){
 if(!charterOwns(x,y))return {ok:false,reason:'Acquire this district before assembling land.'};
 const b=buildingAt(x,y),id=roadId(x,y),field=G.landUse?.[id],farm=G.firms[G.fieldOwner?.[id]];
 if(!b){if(!field)return {ok:false,reason:'This lot is already vacant.'};if(field!==1)return {ok:false,reason:'Finish or cancel the existing land project before clearance.'};return {ok:true,x,y,building:null,fields:[id],households:[],relocations:[],workers:[],compensation:450,demolition:150,total:600,reason:'Purchase one crop title and pay for clearance. The farm loses one productive field; stored grain is retained.'};}
 if(typeof transitInfrastructureInUse==='function'&&transitInfrastructureInUse(b.id))return {ok:false,reason:'This facility serves an active passenger route. Retire or replan the route through the transit office first.'};
 const guarded=urbanPropertyGuards.map(guard=>guard(b)).find(Boolean);if(guarded)return {ok:false,reason:guarded};
 if(['townhall','bank','airport','metro_station','bus_depot','skytrain_station','transit_depot','elevated_station'].includes(b.kind)||b.redevelopment||G.projects.some(p=>p.id===b.id))return {ok:false,reason:'This property has an active project or a network/financial role. Complete that commitment before clearance.'};
 const f=G.firms[b.firm];
 if(f&&((G.freight||[]).some(s=>s.from===f.id||s.to===f.id)||(G.regionalTrade?.shipments||[]).some(s=>s.firm===f.id||s.depot===f.id)||(G.waterway?.manifests||[]).some(m=>m.port===f.id)||(G.regionalTrade?.contracts||[]).some(c=>c.firm===f.id&&c.status==='active')||G.projects.some(p=>p.firmId===f.id)))return {ok:false,reason:'This enterprise has paid cargo, crop works or an active trade contract. Settle those commitments before land assembly.'};
 const fields=f?Object.keys(G.fieldOwner||{}).filter(k=>G.fieldOwner[k]===f.id).map(Number):[],households=G.households.filter(h=>h.home===b.id&&h.people.length),vacant=urbanVacancies(b.id).sort((a,c)=>Number(!!c.municipalRehousing)-Number(!!a.municipalRehousing)||(Math.abs(a.x-b.x)+Math.abs(a.y-b.y))-(Math.abs(c.x-b.x)+Math.abs(c.y-b.y))||a.id-c.id);
 if(vacant.length<households.length)return {ok:false,reason:'Provide '+households.length+' real vacant, connected dwelling'+(households.length===1?'':'s')+' before displacing these households. Tenants are never erased.'};
 const available=vacant.slice(),relocations=[];
 households.sort((a,c)=>householdLiquidity(a)-householdLiquidity(c)||a.id-c.id);
 const relocationReview=[];
 for(const h of households){const affordable=available.filter(dest=>urbanRelocationAffordable(h,dest,b)),reachable=affordable.filter(dest=>urbanRelocationWorkerRoutes(h,dest).ok),dest=reachable[0];if(!dest){if(affordable.length)return {ok:false,reason:'A current worker in this household could not reach their existing job from the available affordable homes by the present road or transit network. Provide closer connected replacement housing or a working passenger route first.'};return {ok:false,reason:'Provide affordable connected replacement housing before displacing these tenants. Commission a reserved municipal home in Public Works; its rent is capped at 25% of after-tax income.'};}const jobAccess=urbanRelocationWorkerRoutes(h,dest),services=urbanRelocationServiceRoutes(dest);relocationReview.push({household:h.id,destination:dest.id,x:dest.x,y:dest.y,reserved:!!dest.relocationReserve||!!dest.municipalRehousing,workers:jobAccess.routes,services});relocations.push(dest.id);available.splice(available.indexOf(dest),1);}
 const workers=f&&!f.closed?f.workers.slice():[],municipal=b.title?.kind==='municipal'&&b.owner===-1||['school','clinic','fire','police','park','square','courthouse','watchtower'].includes(b.kind)&&isPublicFacility(b),compensation=municipal?0:Math.round(b.value*1.1)+fields.length*450,demolition=1500+footprintOf(b).length*350,relocation=households.length*2000,severance=workers.length*Math.max(G.policy.minWage,f?.wage||0)*12;
 const output=f?.productionTrend??f?.production,farmLoss=f?.kind==='farm'&&!f.closed?` This permanently closes ${f.name}; ${fields.length} productive crop plots are lost.${Number.isFinite(output)?' Recent grain-output trend of '+fmt(output)+' units/day is also lost.':''} Its ${fmt(f.stock?.grain||0)} stored grain is liquidated through the firm's accounts, and ${workers.length} farm jobs end after the quoted severance. This clearance does not relocate the farm.`:'';
 const tenants=relocationReview.map(r=>{const h=G.households[r.household],dest=readBuild(r.destination),clinic=r.services.health,school=r.services.school,serviceText=(label,s)=>s.distance==null?`${label} is outside the road network`: `nearest public ${label} ${s.distance} road segments (${s.within?'within':'outside'} the ${s.limit}-segment range)`,jobText=r.workers.length?`${r.workers.length} current commute${r.workers.length===1?'':'s'} remain reachable by ${[...new Set(r.workers.map(w=>w.mode))].join('/')}`:'no currently commuting household workers';return `${h.name} → ${dest.kind==='home'?'cottage':'multi-unit home'} ${r.destination} at (${r.x}, ${r.y})${r.reserved?' · reserved municipal home':''}; ${jobText}; ${serviceText('clinic',clinic)}, ${serviceText('school',school)}. Service capacity and funded coverage are assessed separately.`;}).join(' ');
 return {ok:true,x:b.x,y:b.y,building:b.id,fields,households:households.map(h=>h.id),relocations,relocationReview,workers,compensation,demolition,relocation,severance,total:compensation+demolition+relocation+severance,reason:households.length+' households move to specific vacant homes on the connected town road network. '+tenants+' '+workers.length+' workers receive twelve days of severance. Enterprise inventories are sold through liquidation, loans settled, and crop titles released.'+farmLoss};
}
function urbanClearance(x,y,quotedTotal,reviewedKey=null){
 const q=urbanClearanceQuote(x,y);if(!q.ok||q.total!==quotedTotal||G.treasury<q.total)return {ok:false,reason:q.reason||'The quote changed or the treasury is insufficient.'};
 if(reviewedKey&&urbanClearanceReviewKey(q)!==reviewedKey)return {ok:false,reason:'A replacement address or protected property changed since review. Inspect the current destinations and cost before clearing this site.'};
 const b=q.building&&readBuild(q.building),f=b&&G.firms[b.firm],title=b&&urbanTitleAccount(b);
 // All dependent checks precede the first mutation. Accounts only transfer cash.
 G.treasury-=q.total;G.cumulative.spending+=q.total;
 if(title)title.cash+=q.compensation;else if(!b&&G.firms[G.fieldOwner?.[q.fields[0]]])G.firms[G.fieldOwner[q.fields[0]]].cash+=q.compensation;else G.region+=q.compensation;
 G.region+=q.demolition;
 q.households.forEach((id,i)=>{const h=G.households[id],dest=readBuild(q.relocations[i]);h.cash+=2000;h.home=dest.id;if(dest.municipalRehousing)dest.relocationReserve=false;h.lastRelocated=G.day;h.stress=clamp(h.stress+8,0,100);if(dest.kind==='home')dest.hh=h.id;else{dest.units=(dest.units||[]).filter(id=>G.households[id]?.people.length);dest.units.push(h.id);dest.hh=dest.units[0];}});
 for(const id of q.workers){const p=G.people[id],h=p&&G.households[p.hh];if(h)h.cash+=q.severance/Math.max(1,q.workers.length);else G.region+=q.severance/Math.max(1,q.workers.length);}
 if(f&&!f.closed)liquidateFirm(f,'Compensated municipal land assembly');
 for(const id of q.fields){const owner=G.fieldOwner[id];if(G.landUse[id]===1)G.fieldCount[owner]=Math.max(0,(G.fieldCount[owner]||0)-1);delete G.landUse[id];delete G.fieldOwner[id];}
 if(b){G.homes=G.homes.filter(id=>id!==b.id);G.buildings=G.buildings.filter(v=>v.id!==b.id);if(f){f.demolished=true;f.demolishedDay=G.day;}if(selected?.id===b.id)selected=null;}
 const u=ensureUrban();u.renewals.unshift({day:G.day,action:b?'Municipal clearance: '+types[b.kind].n:'Crop-title acquisition',cost:q.total});u.renewals=u.renewals.slice(0,80);u.revision++;invalidateUrban();invalidateBuildingIndex();invalidateRoads(false);recompute();assignJobs();staticDirty=true;dirty=true;book('Municipal land assembly','Owners, tenants, workers and clearance contractors',q.total,'Compensated land assembly',b?.id||-1);story('Land assembled for redevelopment. '+q.reason,'neutral');save();return {ok:true,reason:'Land is vacant and available for a new permitted use.'};
}
function urbanSiteSuitability(x,y,kind){const d=urbanDescriptor(x,y);if(urbanPlacementReason(x,y,kind))return -10000;if(kind==='farm')return 28-d.density*5-d.landValue*.006;if(['home','apartment','tower'].includes(kind))return d.work*.55+d.amenity*2-d.pollution*4;if(['grocer','tavern'].includes(kind))return d.density*1.8+d.work*.5;return d.work*.3-d.density*.5;}
function urbanRetailStoreReview(f){const closed=!!f.closed,staff=closed?0:workingStaff(f).length,stock=Math.max(0,f.stock?.food||0),capacity=staff*80,stockAndStaff=Math.min(stock,capacity);return {id:f.id,name:f.name,retailCentre:!!f.retailCentre,closed,staff,stock,price:f.price,capacity,stockAndStaff,competitionWeight:closed?0:f.retailCentre?2:1,status:closed?'closed':!staff?'open, unstaffed':!stock?'open, no food stock':'staffed and stocked'};}
// Existing farms can move intact when urban land demand makes renewal worthwhile.
// Identity, inventory, capital and contracts remain with the same enterprise.
function urbanFarmRenewal(demand){
 if(G.autoBuild===false||demand.homeDemand<18||demand.housingPressure<65||demand.confidence<40||G.policy.zoningRestriction>65||G.projects.some(p=>p.urbanRenewal))return false;
 const farms=G.firms.filter(f=>f.kind==='farm'&&!f.closed&&!G.projects.some(p=>p.firmId===f.id)&&!(G.freight||[]).some(s=>s.from===f.id||s.to===f.id)&&!(G.regionalTrade?.shipments||[]).some(s=>s.firm===f.id)).map(f=>({f,b:readBuild(f.building)})).filter(v=>v.b&&urbanDescriptor(v.b.x,v.b.y).density>=5&&G.day-(v.b.lastRelocated||-720)>=540&&footprintOf(v.b).length===4);
 farms.sort((a,b)=>urbanDescriptor(b.b.x,b.b.y).landValue-urbanDescriptor(a.b.x,a.b.y).landValue||a.f.id-b.f.id);
 const candidate=farms[0];if(!candidate)return false;const {f,b}=candidate,u=ensureUrban();
 const lots=buildableCandidates('business').filter(v=>canPlace(v.x,v.y,true,'farm')&&urbanDescriptor(v.x,v.y).density<1.5).sort((a,b)=>urbanSiteSuitability(b.x,b.y,'farm')-urbanSiteSuitability(a.x,a.y,'farm')||a.x-b.x||a.y-b.y),dest=lots[0];
 const oldFields=Object.keys(G.fieldOwner||{}).filter(id=>G.fieldOwner[id]===f.id&&G.landUse[id]===1).length;
 const replacement=lots.map(place=>({...place,plots:urbanRelocationFields(place.x,place.y,oldFields)})).find(place=>place.plots.length===oldFields);
 if(!replacement)return false;
 const cost=types.farm.cost+39000+8500+oldFields*200,compensation=Math.round(b.value*.35);if(!dest||G.region<cost+compensation+100000||!canPlace(b.x,b.y,true,'apartment',b))return false;
 // canPlace ignores the old building but never ignores neighbouring property.
 if(!financeConstruction(cost,b.id))return false;
 const account=urbanTitleAccount(b);if(account){G.region-=compensation;account.cash+=compensation;book('Regional developer',account.name||'Property owner',compensation,'Urban land-release premium with replacement farm',b.id);}
 const origin={x:b.x,y:b.y};
 for(const id of Object.keys(G.fieldOwner||{}))if(G.fieldOwner[id]===f.id){delete G.landUse[id];delete G.fieldOwner[id];}G.fieldCount[f.id]=0;
 b.x=replacement.x;b.y=replacement.y;b.lastRelocated=G.day;reserveFootprint(b,'farm');invalidateUrban();
 // Replanting is part of the paid relocation contract; standing fields are not
 // inventory and generate no cash/grain on relocation.
 for(const plot of replacement.plots){G.landUse[plot.id]=1;G.fieldOwner[plot.id]=f.id;G.fieldCount[f.id]++;}
 const site=startDevelopmentProject('redevelop',origin,175000,40,{target:'apartment',units:4,priorKind:'farm',formerValue:b.value,urbanRenewal:true});
 if(site){site.footprint=footprintFor(origin.x,origin.y,'apartment');invalidateBuildingIndex();}
 if(!site)throw Error('Reserved urban renewal origin became unavailable');
 u.renewals.unshift({day:G.day,action:'Farm relocated; four urban dwellings commissioned',cost:cost+(account?compensation:0)});u.renewals=u.renewals.slice(0,80);u.revision++;G.development.privateSpend=(G.development.privateSpend||0)+cost+(account?compensation:0);invalidateUrban();invalidateRoads(false);assignJobs();story('A farm moved to the agricultural belt with its existing workers, stocks and accounts. Paid construction is replacing its urban plot with housing.','good',b.id);return true;
}
function urbanRetailProposal(explicit=false,reviewedKey=null){
 const preview=explicit==='preview';
 const demand=cityDemand();if((!explicit&&G.autoBuild===false)||demand.residents<320||demand.confidence<42||G.projects.some(p=>p.retailCentre)||G.firms.some(f=>!f.closed&&f.retailCentre&&G.day-(f.openedDay||0)<360))return {ok:false,reason:'A retail centre needs at least 320 residents, investment confidence, and no recent competing centre.'};
 const reviewRng=preview||!!reviewedKey?rngState:null,places=buildableCandidates('business'),net=graph(),popByBuilding=new Map(),search={vacant:0,permitted:0,connected:0,market:0,staffed:0,viable:0};for(const h of G.households)if(h.people.length)popByBuilding.set(h.home,(popByBuilding.get(h.home)||0)+h.people.length);
 let best=null;
 for(const c of places){const footprint=[];for(let dy=0;dy<2;dy++)for(let dx=0;dx<3;dx++)footprint.push(roadId(c.x+dx,c.y+dy));if(c.x+3>=T-2||c.y+2>=T-2||!footprint.every(id=>charterOwns(id%T,id/T|0)&&[0,3].includes(G.tiles[id])&&!G.landUse?.[id]&&!buildingAt(id%T,id/T|0)))continue;search.vacant++;
  if(urbanPlacementReason(c.x,c.y,'grocer')||footprint.some(id=>districtPlacementReason(id%T,id/T|0,'grocer')))continue;search.permitted++;
  const access=roadOffsets.map(([dx,dy])=>roadId(c.x+dx,c.y+dy)).find(id=>net.parts[id]===net.mainPart);if(access==null)continue;search.connected++;
  const dist=new Map([[access,0]]),queue=[access];for(let n=0;n<queue.length;n++){const id=queue[n],d=dist.get(id);if(d>=24)continue;for(const next of net.neighbors.get(id)||[])if(!dist.has(next)){dist.set(next,d+1);queue.push(next);}}
  let catchment=0,competition=0;for(const [id,pop] of popByBuilding)if(dist.has(net.portals.get(id)))catchment+=pop;for(const f of G.firms)if(!f.closed&&f.kind==='grocer'&&dist.has(net.portals.get(f.building)))competition+=f.retailCentre?2:1;
  const score=catchment/Math.max(1,competition+1);if(catchment<180||score<75)continue;search.market++;const plan=urbanRetailPlan(c,score);
  if(!plan)continue;search.staffed++;if(plan.net*360<(44000+28000)*.09)continue;search.viable++;if(!best||plan.net>best.plan.net)best={...c,score,catchment,competition,footprint,plan};
 }
 const cost=44000,capital=28000;if(!best){if(reviewRng!=null)rngState=reviewRng;const reason=search.vacant===0?'No vacant 3 × 2 site is available in acquired land. Annex a new parcel and connect its street frontage, or review lawful land assembly; existing shops and productive fields will not be cleared for this proposal.':search.permitted===0?'Vacant centre-sized sites are protected by neighbourhood plans or land-use reservations. Review a plan after its cooldown, or choose another district while preserving active farms.':search.connected===0?'No permitted centre site touches the connected town street network. Extend a municipal street to an available parcel before inviting investors.':search.market===0?'Connected legal sites do not have 180 residents within 24 road steps and enough uncrowded local demand. Grow nearby housing or look for an underserved district.':search.staffed===0?'Nearby demand exists, but no reachable eligible workers can accept the centre’s modeled wage. Improve commute access or grow the local labour pool.':'Available sites fail the centre’s investor return hurdle at current prices, wages and competition. Revisit the market later; the forecast cannot promise profit.';return {ok:false,reason,search};}
 const signature=preview||reviewedKey?JSON.stringify({day:G.day,region:G.region,confidence:demand.confidence,residents:demand.residents,revision:ensureUrban().revision,roads:[...net.neighbors.keys()],homes:[...popByBuilding],shops:G.firms.filter(f=>f.kind==='grocer').map(f=>{const b=readBuild(f.building);return [f.id,b?.x,b?.y,!!f.closed,f.jobs,workingStaff(f).length,f.cash,f.price,f.stock.food||0]}),site:[best.x,best.y,best.catchment,best.competition,best.plan.staff,best.plan.wage,best.plan.net]}):null;
 if(preview){if(G.region<cost+capital+100000){rngState=reviewRng;return {ok:false,reason:'Regional investors lack the construction and working capital reserve.'};}const nearby=G.firms.filter(f=>f.kind==='grocer'&&net.portals.has(f.building)&&(()=>{const access=roadOffsets.map(([dx,dy])=>roadId(best.x+dx,best.y+dy)).find(id=>net.parts[id]===net.mainPart);return access!=null&&roadDistance(access,net.portals.get(f.building))<=24;})()).map(urbanRetailStoreReview),units=best.plan.units,physicalCapacity=best.plan.staff*80,capacityUnits=Math.min(units,physicalCapacity),overhead=2+best.plan.staff*(.6+G.policy.businessRegulation*.035),rates=220000*(G.policy.commercialRate||0)/100/360,capacityNet=((capacityUnits*(best.plan.price-best.plan.cost))-best.plan.staff*best.plan.wage-overhead-rates)*(1-G.policy.profitTax/100),quote={ok:true,x:best.x,y:best.y,catchment:best.catchment,competition:best.competition,nearby,nearbyOpen:nearby.filter(f=>!f.closed).length,nearbyClosed:nearby.filter(f=>f.closed).length,nearbyServing:nearby.filter(f=>f.stockAndStaff>0).length,nearbyStockAndStaff:nearby.reduce((n,f)=>n+f.stockAndStaff,0),regionalConstruction:cost,regionalWorkingCapital:capital,staff:best.plan.staff,wage:best.plan.wage,units,physicalCapacity,capacityUnits,capacityNet,net:best.plan.net,shareBefore:(best.catchment*1.6)/Math.max(1,best.competition),shareAfter:(best.catchment*1.6)/(best.competition+1),reviewKey:signature};rngState=reviewRng;return quote;}
 if(reviewedKey&&reviewedKey!==signature){rngState=reviewRng;return {ok:false,reason:'The city, site or market changed since this proposal review. Inspect a fresh quote before inviting investors.'};}
 if(G.region<cost+capital+100000){if(reviewRng!=null)rngState=reviewRng;return {ok:false,reason:'Regional investors lack the construction and working capital reserve.'};}
 const site=startDevelopmentProject('firm',best,220000,65,{firmKind:'grocer',capital,retailCentre:true,retailCatchment:best.catchment,retailExpectedNet:best.plan.net,retailStaff:best.plan.staff,retailWage:best.plan.wage});if(!site)return {ok:false,reason:'The retail site is no longer available.'};
 const project=G.projects.find(p=>p.id===site.id);G.region-=capital;project.urbanEscrow=capital;
 site.footprint=best.footprint;site.retailCentre=true;invalidateBuildingIndex();financeConstruction(cost,site.id);G.development.privateSpend=(G.development.privateSpend||0)+cost;ensureUrban().revision++;invalidateUrban();story('Investors funded a six-plot shopping centre with an anchor food market, covered shopfronts and a loading court. It must recruit staff and buy real inventory before serving its catchment.','good',site.id);return {ok:true,reason:'A privately funded shopping centre is under construction.'};
}
function urbanEvolutionDay(){if(G.day%30!==0)return;urbanHousingMobility();urbanDistrictReview();if(!urbanFarmRenewal(cityDemand())&&G.day%90===0)urbanRetailProposal();}
function urbanRentMultiplier(home){if(!home)return 1;const d=urbanDescriptor(home.x,home.y);return clamp(.80+d.landValue/12000+home.condition*.0015+d.amenity*.018-d.pollution*.04,.65,1.55);}
function urbanHousingMobility(){
 const living=G.households.filter(h=>h.people.length),vacancies=urbanVacancies(-1,false);if(!living.length||!vacancies.length)return 0;const net=graph(),offset=(Math.floor(G.day/30)*24)%living.length;let moved=0;
 const costAt=(h,site)=>{const portal=net.portals.get(site.id);if(portal==null||net.parts[portal]!==net.mainPart)return null;let commute=0,workers=0;
  for(const id of h.people){const p=G.people[id],work=p?.job>=0&&readBuild(G.firms[p.job]?.building);if(!work)continue;const workPortal=net.portals.get(work.id);if(workPortal==null||net.parts[workPortal]!==net.parts[portal])return null;const distance=roadDistance(portal,workPortal);if(distance>60+(G.policy.transitBudget||0)/8&&!hasMetroCommute(site,work))return null;commute+=distance;workers++;}
  const rent=urbanHousingRent(h,site,site.owner===h.id?0:h.people.length*(3.1+G.policy.zoningRestriction*.035)*(G.housingMarket?.rentIndex||1)*urbanRentMultiplier(site)),d=urbanDescriptor(site.x,site.y),income=Math.max(1,(h.income||0)-(h.tax||0)),comfortable=income/h.people.length>urbanSpatial().median*1.3;
  return {rent,score:rent*(comfortable?.7:1.5)+(workers?commute/workers:0)*.18+d.pollution*.8-d.amenity*(comfortable?1.8:.5)-site.condition*.025};};
 for(let n=0;n<Math.min(24,living.length)&&moved<2;n++){const h=living[(offset+n)%living.length],old=readBuild(h.home),moving=150+50*h.people.length;
  if(!old||old.redevelopment||h.temporaryHousing||G.day-(h.lastRelocated||-720)<180||h.cash<moving+h.people.length*200)continue;
  const current=costAt(h,old);if(!current)continue;const choices=[];
  for(let i=0;i<vacancies.length;i++){const target=vacancies[i];if(target.id===old.id)continue;const offer=costAt(h,target);if(!offer||offer.rent>Math.max(8,((h.income||0)-(h.tax||0))*.35)||current.score-offer.score<3)continue;choices.push({target,index:i,...offer});}
  choices.sort((a,b)=>a.score-b.score||a.target.id-b.target.id);const offer=choices[0];if(!offer)continue;
  h.cash-=moving;G.region+=moving;if(old.kind==='home')old.hh=-1;else{old.units=(old.units||[]).filter(id=>id!==h.id);old.hh=old.units[0]??-1;}
  h.home=offer.target.id;h.lastRelocated=G.day;if(offer.target.kind==='home')offer.target.hh=h.id;else{offer.target.units=(offer.target.units||[]).filter(id=>G.households[id]?.people.length);offer.target.units.push(h.id);offer.target.hh=offer.target.units[0];}
  vacancies.splice(offer.index,1);vacancies.push(old);moved++;book(h.name+' household','Regional moving service',moving,'Voluntary move to an affordable connected dwelling',offer.target.id);
 }
 if(moved){ensureUrban().revision++;invalidateUrban();invalidateRoads(false);staticDirty=true;dirty=true;story(moved+' households moved voluntarily to vacant homes after comparing rent, work access and local conditions. Moving costs were paid from their savings.','neutral');}return moved;
}
