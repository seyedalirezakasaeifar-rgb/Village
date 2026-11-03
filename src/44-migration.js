// Migration assessments use existing paid wages, actual road/transit access and
// redeemable savings. Reports are derived; they are not archive authority.
let migrationReportOwner=null,migrationRecent=[],migrationObservedDay=0,migrationSessionCounts={};
function migrationReport(){if(migrationReportOwner!==G){migrationReportOwner=G;migrationRecent=[];migrationObservedDay=G.day;migrationSessionCounts={births:0,deaths:0,immigration:0,emigration:0};}return migrationRecent;}
function migrationRecord(kind,detail){const rows=migrationReport(),n=detail.people||0;if(kind==='birth')migrationSessionCounts.births+=n;if(kind==='death')migrationSessionCounts.deaths+=n;if(kind==='household-arrival'||kind==='family-arrival')migrationSessionCounts.immigration+=n;if(kind==='departure')migrationSessionCounts.emigration+=n;rows.push({day:G.day,kind,...detail});if(rows.length>80)rows.splice(0,rows.length-80);}
function residentHouseholdsAt(buildingOrId,town=G){const id=typeof buildingOrId==='object'?buildingOrId?.id:buildingOrId;return town.households.filter(h=>h.home===id&&h.people.length>0);}
function housingUnitCapacity(building){return building?.kind==='home'?1:building?.kind==='apartment'?4:building?.kind==='tower'?9:0;}
function pruneLegacySharedTenants(building,town=G){
 if(!Array.isArray(building?.legacySharedTenants))return;const current=residentHouseholdsAt(building,town).map(h=>h.id);
 if(current.length<=housingUnitCapacity(building)){delete building.legacySharedTenants;return;}
 building.legacySharedTenants=building.legacySharedTenants.filter(id=>current.includes(id)).sort((a,b)=>a-b);
}
function migrationTenancyDay(){migrationReport();for(const h of G.households)if(!h.people.length&&h.home>=0)migrationReleaseTenancy(h);for(const b of G.buildings)if(b.legacySharedTenants)pruneLegacySharedTenants(b);}
function migrationHousingStatus(building){
 const capacity=housingUnitCapacity(building);
 const households=building?residentHouseholdsAt(building).map(h=>h.id):[];
 return {building:building?.id??-1,capacity,households,occupied:households.length,available:Math.max(0,capacity-households.length),overcrowded:households.length>capacity,reviewRequired:households.length>capacity,legacySharedTenants:Array.isArray(building?.legacySharedTenants)?building.legacySharedTenants.slice():[],reserved:!!building?.relocationReserve,underConstruction:!!building?.redevelopment};
}
function migrationReleaseTenancy(h){
 if(!h||h.people.length)return false;const b=readBuild(h.home);if(b){if(b.hh===h.id)b.hh=-1;if(Array.isArray(b.units))b.units=b.units.filter(id=>id!==h.id);}h.home=-1;if(b){if(b.hh<0)b.hh=residentHouseholdsAt(b)[0]?.id??-1;pruneLegacySharedTenants(b);}return true;
}
function migrationRegisterTenancy(h,b){
 if(!h||!b||!h.people.length)return false;h.home=b.id;
 // Clear stale EMPTY tenancy references only; ownership, loans, cash and bank
 // claims remain with the former household, including external estates.
 for(const old of G.households)if(old!==h&&old.home===b.id&&!old.people.length)migrationReleaseTenancy(old);
 if(b.kind==='home')b.hh=h.id;else{b.units=(b.units||[]).filter(id=>id!==h.id&&G.households[id]?.people.length&&G.households[id].home===b.id);b.units.push(h.id);b.hh=b.units[0]??-1;}pruneLegacySharedTenants(b);return true;
}
function migrationSpendable(h){
 let cash=Math.max(0,h.cash||0),region=Math.max(0,G.region||0),claims=0,redeemed=0;
 for(const [id,value]of Object.entries(h.deposits||{})){const amount=Math.max(0,value||0);claims+=amount;const bank=G.banks[+id];if(!bank||bank.closed)continue;const vault=Math.min(amount,Math.max(0,bank.cash)),sale=Math.min(amount-vault,Math.max(0,bank.regionCredit||0),region);cash+=vault+sale;region-=sale;redeemed+=sale;}
 return {cash:Math.max(0,h.cash||0),claims,spendable:cash,locked:Math.max(0,Math.max(0,h.cash||0)+claims-cash),redeemableSecurities:redeemed};
}
function migrationCanReach(home,f){
 const net=graph(),a=net.portals.get(home?.id),b=net.portals.get(f.building);if(a==null||b==null||net.parts[a]!==net.parts[b])return null;
 const distance=roadDistancesFrom(b,net)[a],limit=60+(G.transit?.routes.length?0:(G.policy.transitBudget||0)/8),work=readBuild(f.building),trip=distance>=8?transitJourney(home,work):null;
 if(trip&&trip.time<=90&&trip.time<distance*2)return {distance,fare:trip.fare,mode:'paid-transit'};
 if(hasMetroCommute(home,work))return {distance,fare:Math.max(0,G.metro?.fare||0),mode:'legacy-metro'};
 if(distance<=limit){const fare=(Math.abs(home.x-work.x)+Math.abs(home.y-work.y))*.035*(1-clamp(G.policy.transitBudget*(G.actualServiceFunding?.transit||0)/280,0,.65));return {distance,fare,mode:'road'};}return null;
}
function migrationDebtDue(h){return h?G.loans.filter(l=>l.ownerType==='household'&&l.ownerId===h.id&&l.status==='active').reduce((n,l)=>n+Math.min(l.balance,l.original/Math.max(30,l.term))+l.balance*l.rate/360,0):0;}
function migrationPropertyDue(h){return h?G.buildings.filter(b=>b.owner===h.id&&['home','apartment','tower'].includes(b.kind)).reduce((n,b)=>n+b.value*(G.policy.propertyTax||0)/100/360,0):0;}
function migrationFoodChoice(home,size,offers){
 if(!home)return null;const shops=G.firms.filter(f=>!f.closed&&f.kind==='grocer'&&(workingStaff(f).length>0||offers.some(o=>o.firm===f.id)));
 return groceryChoices({home:home.id,people:Array(size).fill(-1)},home,shops)[0]||null;
}

function migrationJobOffers(home,profiles,excludeHousehold=-1){
 const firms=G.firms.filter(f=>!f.closed&&f.workers.length<f.jobs).slice().sort((a,b)=>b.wage-a.wage||a.id-b.id),reserved=new Set(),offers=[];
 const local=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.hh!==excludeHousehold&&p.age>=16&&p.age<=70&&p.job<0&&!p.publicWork&&!p.previousPublicRole&&(p.searchAfter||0)<=G.day);
 for(const f of firms){const wage=workerIncome(f),funded=Math.max(0,Math.min(f.jobs-f.workers.length,Math.floor(Math.max(0,f.cash)/Math.max(1,wage))-f.workers.length));if(!funded)continue;
  let left=funded;for(const p of local){if(reserved.has(p.id)||f.privateService&&!privateQualified(p,f))continue;const site=readBuild(G.households[p.hh]?.home);if(!site||!migrationCanReach(site,f))continue;reserved.add(p.id);left--;if(!left)break;}
  if(left)offers.push({firm:f.id,wage,slots:left,reach:migrationCanReach(home,f)});
 }
 const assignments=[];for(let i=0;i<profiles.length;i++){const p=profiles[i];if(p.age<16||p.age>70)continue;for(const offer of offers){const f=G.firms[offer.firm];if(offer.slots<=0||!offer.reach||f.privateService&&!privateQualified(p,f))continue;offer.slots--;assignments.push({person:i,firm:f.id,wage:offer.wage,...offer.reach});break;}}
 return assignments;
}
function migrationOutsideReference(size,workers,retirees=0){
 // Named markets supply price comparisons, not a pretend foreign labour census.
 // The income/rent reference is the existing founding policy, disclosed as a
 // benchmark rather than an observed guaranteed offer in another city.
 const retail=Math.max(.01,foodPriceEstimate()),base=Math.max(.01,marketPrice('food')),markets=typeof OUTSIDE_MARKETS==='undefined'?[]:OUTSIDE_MARKETS;
 const options=markets.map(m=>{const food=retail*regionalMarketQuote(m,'food','imports')/base,net=workers*defaults.minWage*(1-defaults.incomeTax/100)+retirees*defaults.pensionDaily,cold=seasonsEnabled()&&(G.month>=10||G.month<=2),essentials=size*((3.1+defaults.zoningRestriction*.035)+1.6*food*(1+defaults.foodTax/100)+(2.25+(cold?1.8:0))*(1+defaults.utilityTax/100));return {market:m.id,name:m.name,net,essentials,surplus:net-essentials,referenceOnly:true};});
 options.sort((a,b)=>b.surplus-a.surplus);return options[0]||{market:null,name:'Outside-region reference',net:0,essentials:0,surplus:0,referenceOnly:true};
}
function migrationServiceAt(home){
 // Forecast from persisted paid roles, ready staffing contracts, actual facility
 // access and available authorization. Last-day serviceProvision is derived and
 // deliberately cleared on load; it must never decide an authoritative arrival.
 const coverage=kind=>{const standard=CIVIC_STANDARDS[kind],limit=kind==='health'?60:40,net=graph(),homePort=net.portals.get(home.id),reaches=G.buildings.some(b=>{if(b.kind!==standard.building||!isPublicFacility(b))return false;const station=net.portals.get(b.id);return station!=null&&homePort!=null&&net.parts[station]===net.parts[homePort]&&roadDistancesFrom(station,net)[homePort]<=limit;});if(!reaches)return 0;
  const access=serviceAccess(kind),needed=Math.max(1,G.stats.population)*standard.staff/standard.capacity,wage=Math.max(24,G.policy.minWage),authorized=Math.min(Math.max(0,G.treasury),Math.max(0,G.policy[kind==='health'?'healthBudget':'educationBudget']||0)),funding=authorized/Math.max(1,needed*wage/.65),contract=G.civicStaffing?.[kind];
  // First-day/legacy services inherit the funded operating arrangements already
  // supplied by civicStaffCapacity; later expansion waits for actual readiness.
  if(!contract)return clamp(Math.min(access.coverage,funding),0,1);
  const regional=contract.pending&&contract.pending.day<=G.day?contract.pending.target:contract.ready,local=G.people.reduce((n,p)=>n+Number(p.job<0&&p.publicRole===kind&&(p.publicIncome||0)>0&&qualifiedForService(p,kind)),0);
  return clamp(Math.min(access.coverage,funding,(local+Math.max(0,regional||0))/needed),0,1);
 };
 return {health:coverage('health'),school:coverage('school'),forecastOnly:true};
}

function migrationSchoolOffer(home,learners,publicCoverage,netIncome,cash,householdSize,baseEssentials,previousFees=0){
 if(!learners||publicCoverage>=1)return null;const port=graph().portals.get(home.id);if(port==null)return null;let best=null;
 for(const f of G.firms){if(f.closed||f.privateService!=='school'||!workingStaff(f).length||f.cash<workerIncome(f)*workingStaff(f).length)continue;
  const places=Math.max(0,(f.serviceCapacity||0)-(f.clientsToday||0)),station=graph().portals.get(f.building);if(places<=.0001||station==null||(privateServiceDistances(station).get(port)??Infinity)>40)continue;
  const fee=Math.min(Math.max(0,f.serviceFee||0),G.policy.privateTuitionCap),count=Math.min(places,learners*(1-publicCoverage)),candidate={people:Array(householdSize).fill(-1),cash:Math.max(0,cash-baseEssentials),deposits:{},income:netIncome,privateServiceFees:previousFees},purchase=privateServicePurchase(candidate,count,fee,0);
  if(!purchase.served||purchase.paid>Math.max(0,netIncome-baseEssentials))continue;
  if(!best||purchase.served>best.served||purchase.served===best.served&&purchase.paid<best.dailyCost)best={firm:f.id,served:purchase.served,dailyCost:purchase.paid,fee,forecastOnly:true};
 }return best;
}
function migrationAssessment(home,profiles,capital=2500,joining=null){
 const housing=migrationHousingStatus(home),reasons=[],net=graph(),port=net.portals.get(home?.id);
 if(!housing.capacity||housing.reserved||housing.underConstruction||housing.overcrowded||(!joining&&!housing.available))reasons.push('No unreserved vacant household unit');
 if(joining&&(!joining.people.length||joining.home!==home?.id||!housing.households.includes(joining.id)||joining.people.length+profiles.length>4))reasons.push('No settled family space at this address');
 if(port==null||net.parts[port]!==net.mainPart)reasons.push('The home has no connected road gateway');
 if(G.stats.population+profiles.length>2000)reasons.push('Town population ceiling reached');
 if(!joining&&Math.min(Math.max(0,G.region),capital)<500)reasons.push('Outside household startup funds unavailable');
 const offers=reasons.length?[]:migrationJobOffers(home,profiles,joining?.id??-1),size=profiles.length+(joining?.people.length||0),existing=joining?Math.max(0,joining.netIncomeTrend??((joining.income||0)-(joining.incomeTax||0))):0;
 const netIncome=existing+offers.reduce((n,o)=>n+o.wage*(1-G.policy.incomeTax/100),0),baseRent=size*(3.1+G.policy.zoningRestriction*.035)*(G.housingMarket?.rentIndex||1)*urbanRentMultiplier(home),rent=urbanHousingRent(joining||{income:netIncome,tax:0},home,home?.owner===joining?.id?0:baseRent);
 const foodChoice=migrationFoodChoice(home,size,offers),cold=seasonsEnabled()&&(G.month>=10||G.month<=2),budget={rent,food:size*1.6*(foodChoice?.f.price||foodPriceEstimate())*(1+G.policy.foodTax/100),utilities:size*(2.25+(cold?1.8:0))*(1+G.policy.utilityTax/100),commuting:Math.max(0,(joining?.travelDue||0)-(joining?.shoppingTravel||0))+offers.reduce((n,o)=>n+o.fare,0),shopping:foodChoice?.travel||0,propertyTax:migrationPropertyDue(joining),debtService:migrationDebtDue(joining),privateFees:Math.max(0,joining?.privateServiceFees||0)};
 let essentials=Object.values(budget).reduce((n,x)=>n+x,0);const outside=migrationOutsideReference(size,profiles.filter(p=>p.age>=16&&p.age<=70).length+(joining?joining.people.filter(id=>G.people[id]?.age>=16&&G.people[id]?.age<=70).length:0)),services=home?migrationServiceAt(home):{health:0,school:0};
 outside.carriedObligations=budget.propertyTax+budget.debtService;outside.essentials+=outside.carriedObligations;outside.surplus-=outside.carriedObligations;
 if(!foodChoice)reasons.push('No reachable staffed food shop or funded entry-staffed shop');

 if(!offers.length)reasons.push('No funded reachable job remains after local jobseekers');
 if(netIncome+1e-8<essentials)reasons.push('Expected take-home pay does not cover rent, food, utilities and fares');
 const learners=profiles.filter(privateEligiblePupil).length,learning=profiles.some(p=>p.age<18||p.skill<.55),schoolOffer=home&&learning?migrationSchoolOffer(home,learners,services.school,netIncome,joining?.cash??Math.min(capital,G.region),size,essentials,joining?.privateServiceFees||0):null;if(schoolOffer){essentials+=schoolOffer.dailyCost;budget.privateFees+=schoolOffer.dailyCost;services.school=clamp(services.school+schoolOffer.served/Math.max(1,learners),0,1);services.privateSchoolOffer=schoolOffer;}
 const surplus=netIncome-essentials,financialPull=outside.surplus>0?clamp(surplus/outside.surplus,0,1):1,servicePull=(1+services.health+(learning?services.school:1))/3,pullProbability=reasons.length?0:clamp(financialPull*servicePull,0,1);
 return {eligible:!reasons.length,reasons,home:home?.id??-1,housing,offers,expectedNet:netIncome,essentials,budget,foodShop:foodChoice?.f.id??null,rent,surplus,outside,services,pullProbability,capital:joining?0:Math.min(capital,G.region),note:'Outside wages/rents are a founding-policy reference; market food prices are live. Funded vacancies, route capacity and quoted private learning places can change before arrival; any private fee forecast is included in essentials, without assumed vouchers.'};
}
function migrationAcceptOffers(people,assessment){
 if(!assessment)return;for(const offer of assessment.offers){const p=people[offer.person],f=G.firms[offer.firm];if(!p||!f||f.closed||f.workers.length>=f.jobs||f.cash<(f.workers.length+1)*workerIncome(f)||f.privateService&&!privateQualified(p,f))continue;p.job=f.id;f.workers.push(p.id);}
}
function migrationNewProfiles(count){return Array.from({length:count},()=>({age:Math.floor(rn(20,54)),skill:rn(.35,1),health:rn(65,97),life:rn(45,80)}));}
function migrationFamilyArrivalDay(){
 if(creatorCapacityReason(1))return;
 if(G.day%45!==0||G.stats.population>=2000)return;
 if(!G.firms.some(f=>!f.closed&&f.workers.length<f.jobs&&f.cash>=(f.workers.length+1)*workerIncome(f)))return;
 const families=G.households.filter(h=>h.people.length>0&&h.people.length<4&&readBuild(h.home));if(!families.length)return;
 // One family invitation at the existing 45-day cadence, then its real job,
 // unit and budget assessment. A distant unrelated vacancy never grants a person.
 const h=pick(families),profile=migrationNewProfiles(1),assessment=migrationAssessment(readBuild(h.home),profile,0,h);if(!assessment.eligible){migrationRecord('family-arrival-deferred',{household:h.id,assessment});return;}if(random()>=assessment.pullProbability*.5)return;
 const p={id:G.people.length,name:pick(first)+' '+h.name,...profile[0],hh:h.id,job:-1,last:[]};G.people.push(p);h.people.push(p.id);migrationAcceptOffers([p],assessment);assignJobs();migrationRecord('family-arrival',{household:h.id,people:1,assessment});story('A newcomer joined the '+h.name+' household after reviewing reachable work and the family budget.','good',h.home,h.id);
}

function migrationEmigrationAssessment(h){
 const funds=migrationSpendable(h),net=Math.max(0,(h.netIncomeTrend??((h.income||0)-(h.incomeTax||0)))-Math.sqrt(h.incomeVariance||0)),essentials=Math.max(1,expectedHouseholdEssentials(h)),people=h.people.map(id=>G.people[id]).filter(p=>p&&!p.deceased&&!p.movedAway),workers=people.filter(p=>p.age>=16&&p.age<=70).length,retired=people.filter(p=>p.age>70).length,outside=migrationOutsideReference(people.length,workers,retired),home=readBuild(h.home),services=home?migrationServiceAt(home):{health:0,school:0};
 const localOffers=home?migrationJobOffers(home,people.filter(p=>p.age>=16&&p.age<=70&&p.job<0&&!p.publicWork),h.id):[],prospectiveNet=net+localOffers.reduce((n,o)=>n+o.wage*(1-G.policy.incomeTax/100)-o.fare,0),debt=migrationDebtDue(h),totalEssentials=essentials+debt,localSurplus=prospectiveNet-totalEssentials,runway=funds.spendable/totalEssentials,financialPush=localSurplus<0&&runway<90,distress=(h.stress||0)>42||(h.worklessness||0)>20;
 outside.carriedObligations=debt+migrationPropertyDue(h);outside.essentials+=outside.carriedObligations;outside.surplus-=outside.carriedObligations;
 const eligible=people.length>0&&financialPush&&distress&&outside.surplus>localSurplus,severity=clamp(-localSurplus/totalEssentials,0,1),probability=eligible?clamp(.035+severity*.235,.035,.27):0;
 return {eligible,probability,spendable:funds,expectedNet:prospectiveNet,localOffers,essentials:totalEssentials,debtService:debt,runwayDays:runway,localSurplus,outside,services,reasons:eligible?['Persistent household budget shortfall','Less than ninety days of actually redeemable essentials','Outside reference offers a better budget']:['Current resources or local prospects do not justify a financial departure']};
}
function migrationDiagnostics(){
 const overcrowded=G.buildings.map(migrationHousingStatus).filter(x=>x.overcrowded),recent=migrationReport().slice(-12);
 return {day:G.day,recent,observedSinceDay:migrationObservedDay,sessionCounts:{...migrationSessionCounts},historyPersisted:false,retainedDecisionLimit:80,overcrowdedHomes:overcrowded,reviewRequired:overcrowded.length>0,legacyPolicy:'Preserve every family and financial claim. Existing overcrowding requires a rehousing review; it never creates another arrival slot.',outsideReference:migrationOutsideReference(2,2),retainedDecisionCounts:{householdArrivals:migrationReport().filter(x=>x.kind==='household-arrival').reduce((n,x)=>n+x.people,0),familyArrivals:migrationReport().filter(x=>x.kind==='family-arrival').reduce((n,x)=>n+x.people,0),emigration:migrationReport().filter(x=>x.kind==='departure').reduce((n,x)=>n+x.people,0)}};
}
