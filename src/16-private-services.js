// Fee-funded institutions are ordinary firms with actual payroll, private owners
// and bankruptcy. Public facilities never acquire private capacity for free.
function isPublicFacility(b){return !(b.firm>=0&&G.firms[b.firm]?.privateService)}
function privateQualified(p,f){return !p.deceased&&!p.movedAway&&p.age>=18&&p.age<=70&&p.health>=60&&p.skill>=(f.privateService==='school'?.55:.4)}
function privateEligiblePupil(p){return !p.deceased&&!p.movedAway&&p.age>=6&&(p.age<=24||p.age<=60&&p.skill<.7)}
function privateServiceDistance(f,h){const a=graph().portals.get(f.building),b=graph().portals.get(h.home);return a==null||b==null?Infinity:roadDistance(a,b)}
let privatePublicSchoolCache = null;
function privateSchoolPublicGap(h) {
 const net = graph(), provision = G.serviceProvision?.school;
 if (!privatePublicSchoolCache || privatePublicSchoolCache.town !== G || privatePublicSchoolCache.day !== G.day || privatePublicSchoolCache.net !== net || privatePublicSchoolCache.provision !== provision || privatePublicSchoolCache.population !== G.stats.population) {
  const access = serviceAccess('school'), coverage = new Map();
  for (const home of access.households) coverage.set(home.id, provision && access.coverage ? clamp(home.served / home.residents * provision.coverage / access.coverage, 0, 1) : 0);
  privatePublicSchoolCache = {town:G, day:G.day, net, provision, population:G.stats.population, coverage};
 }
 return 1 - (privatePublicSchoolCache.coverage.get(h.id) || 0);
}
function privateServiceDistances(port){
 const net=graph();if(!net.privateServiceDistances)net.privateServiceDistances=new Map();if(net.privateServiceDistances.has(port))return net.privateServiceDistances.get(port);
 const distances=new Map(),queue=[];if(port!=null){distances.set(port,0);queue.push(port);}for(let i=0;i<queue.length;i++){const at=queue[i],d=distances.get(at);if(d>=40)continue;for(const next of net.neighbors.get(at)||[])if(!distances.has(next)){distances.set(next,d+1);queue.push(next);}}
 if(net.privateServiceDistances.size>=128)net.privateServiceDistances.clear();net.privateServiceDistances.set(port,distances);return distances;
}
function privateServiceDemand(kind, site = null, exclude = null) {
 const net = graph();
 const sitePort = site ? net.portals.get(site.id) ?? roadOffsets.map(([dx, dy]) => roadId(site.x + dx, site.y + dy)).find(id => G.tiles[id] === 1) : null;
 const distances=site?privateServiceDistances(sitePort):null;
 return G.households.filter(h => h.people.length).reduce((total, h) => {
  const home = readBuild(h.home), port = net.portals.get(h.home);
  const distance = site ? distances.get(port) ?? Infinity : 0;
  if (site && (!home || distance > 40)) return total;
  const eligible = kind === 'school' ? h.people.filter(id => privateEligiblePupil(G.people[id])).length : h.people.length;
  const publicResponse = kind === 'fire' && home ? publicFireResponse(home) : 0;
  if (kind === 'fire' && site && clamp(1 - distance / 58, 0, 1) * .72 <= publicResponse + .03) return total;
  const gap = kind === 'school' ? privateSchoolPublicGap(h) : Math.max(0, 1 - publicResponse);
  const occupied=privateServiceOtherClients(kind,h,exclude);
  return total + Math.max(0,eligible*gap-occupied);
 }, 0);
}
// Demand is remaining customers, not the same city-wide market promised to every investor.
function privateServiceOtherClients(kind,h,exclude=null){
 const allocations=G.privateServiceProvision?.allocations;
 if(allocations)return Object.entries(allocations).reduce((n,[id,homes])=>n+(+id!==exclude&&G.firms[+id]?.privateService===kind&&!G.firms[+id].closed?(homes[h.id]?.served||0):0),0);
 return Math.max(0,(G.privateServiceProvision?.[kind]?.[h.id]||0)*h.people.length-(exclude!=null?(G.firms[exclude]?.clientsToday||0)*h.people.length/Math.max(1,G.stats.population):0));
}
function privateServicePurchase(h,count,fee,vouchers,restore=null){
 const due=count*fee,reserve=h.people.length*100,previous=Math.max(0,(h.privateServiceFees||0)-(restore?.paid||0)),cash=h.cash+(restore?.paid||0);
 const budget=Math.max(0,(h.income||0)*.12+Math.max(0,householdLiquidity(h)+(restore?.paid||0)-h.people.length*800)*.001-previous);
 let paid=Math.min(due,Math.max(0,cash-reserve),budget),subsidy=householdLiquidity(h)<h.people.length*500?Math.min(vouchers,due-paid):0;
 const share=due>0?(paid+subsidy)/due:0;
 if(share<.5)return {served:0,paid:0,subsidy:0};
 paid=Math.min(due-subsidy,paid);return {served:count*share,paid,subsidy};
}
function privateServiceForecast(kind,site,fee,staff=kind==='school'?1:2,exclude=null,wageOffer=null){
 const capacity=staff*(kind==='school'?16:90),wage=wageOffer??(exclude!=null?workerIncome(G.firms[exclude]):Math.max(G.policy.minWage,36)),own=G.privateServiceProvision?.allocations?.[exclude]||{};
 let remaining=capacity,clients=0,revenue=0,vouchers=Math.max(0,Math.min(G.treasury,G.policy.serviceVoucherBudget||0)-(G.privateServiceProvision?.vouchers||0)+Object.values(own).reduce((n,a)=>n+a.subsidy,0));
 const net=graph(),port=site?(net.portals.get(site.id)??roadOffsets.map(([dx,dy])=>roadId(site.x+dx,site.y+dy)).find(id=>G.tiles[id]===1)):null;
 const distances=site?privateServiceDistances(port):null;
 const homes=G.households.filter(h=>h.people.length).sort((a,b)=>householdLiquidity(a)/a.people.length-householdLiquidity(b)/b.people.length||a.id-b.id);
 const training=new Set((G.civicTraining||[]).filter(c=>G.households[G.people[c.person]?.hh]&&privateSchoolPublicGap(G.households[G.people[c.person].hh])<1).map(c=>c.person));
 for(const h of homes){if(remaining<=.0001)break;const home=readBuild(h.home),target=net.portals.get(h.home),distance=site?(distances.get(target)??Infinity):0;if(distance>40)continue;
  const publicResponse=kind==='fire'?publicFireResponse(home):0;if(kind==='fire'&&clamp(1-distance/58,0,1)*.72<=publicResponse+.03)continue;
  const gap=kind==='school'?privateSchoolPublicGap(h):1-publicResponse,eligible=kind==='school'?h.people.filter(id=>privateEligiblePupil(G.people[id])&&!training.has(id)).length:h.people.length;
  const count=Math.min(remaining,Math.max(0,eligible*gap-privateServiceOtherClients(kind,h,exclude))),purchase=privateServicePurchase(h,count,fee,vouchers,own[h.id]);
  clients+=purchase.served;remaining-=purchase.served;revenue+=purchase.paid+purchase.subsidy;vouchers-=purchase.subsidy;
 }
 const payroll=wage*staff,overhead=2+staff*(.6+G.policy.businessRegulation*.035)+(site?.value||buildCost[kind]*10)*(G.policy.commercialRate||0)/100/360,profit=revenue-payroll-overhead;
 return {clients,capacity,fee,staff,wage,revenue,payroll,overhead,profit,net:profit-Math.max(0,profit)*G.policy.profitTax/100};
}
function privateServiceFee(kind,demand,staff=kind==='school'?1:2,wageOffer=null){const wage=wageOffer??Math.max(G.policy.minWage,36),capacity=staff*(kind==='school'?16:90),cap=kind==='school'?G.policy.privateTuitionCap:G.policy.privateFireFeeCap;return Math.min(cap,Math.max(kind==='school'?1:.35,(wage*staff+6)*1.22/Math.max(1,Math.min(demand,capacity))))}
function planPrivateService(f){
 if(G.day%30!==0)return;const kind=f.privateService,minimum=kind==='school'?1:2,demand=privateServiceDemand(kind,readBuild(f.building),f.id),clients=f.serviceClientTrend??f.clientsYesterday??0;
 const desired=clamp(Math.ceil(clients/(kind==='school'?16:90)),minimum,kind==='school'?5:3);f.jobs=desired;
 // A lower staffing plan must actually release positions and payroll.
 while(f.workers.length>f.jobs){const id=f.workers.pop(),p=G.people[id];if(p?.job===f.id){p.job=-1;p.searchAfter=G.day+1;}}
 const target=privateServiceFee(kind,demand,f.jobs,workerIncome(f));f.serviceFee=(f.serviceFee||target)*.8+target*.2;
}
function recruitPrivateServiceStaff(){for(const f of G.firms.filter(f=>f.privateService&&!f.closed)){if(f.workers.length>=f.jobs||f.cash<workerIncome(f)*20)continue;for(const p of G.people){if(f.workers.length>=f.jobs)break;if(p.job<0||p.job===f.id||p.publicWork||p.previousPublicRole||!privateQualified(p,f)||G.day-(p.privateJobChange||-90)<60)continue;const old=G.firms[p.job];if(!old||old.closed||workerIncome(f)<workerIncome(old)*1.12||privateServiceDistance(f,G.households[p.hh])>40)continue;old.workers=old.workers.filter(id=>id!==p.id);p.job=f.id;p.privateJobChange=G.day;f.workers.push(p.id);}}}
function privateServiceDay(){
 if(G.privateServiceProvision?.day===G.day)return;
 const state={version:1,day:G.day,school:{},fire:{},tuition:0,memberships:0,vouchers:0,pupils:0,fireMembers:0,allocations:{}};G.privateServiceProvision=state;let vouchers=Math.min(G.treasury,G.policy.serviceVoucherBudget||0);const enrolled=new Set(),publicStudents=new Set((G.civicTraining||[]).filter(c=>G.households[G.people[c.person]?.hh]&&privateSchoolPublicGap(G.households[G.people[c.person].hh])<1).map(c=>c.person));
 for(const h of G.households)h.privateServiceFees=0;
 for(const f of G.firms.filter(f=>f.privateService)){f.clientsYesterday=f.clientsToday||0;f.clientsToday=0;f.privateReceipts=0;f.privateVouchers=0;f.serviceCapacity=0;if(f.closed)continue;const qualified=workingStaff(f).filter(id=>privateQualified(G.people[id],f));if(!qualified.length)continue;const kind=f.privateService,quality=clamp(qualified.reduce((n,id)=>n+G.people[id].skill,0)/qualified.length/.75,.6,1),capacity=qualified.length*(kind==='school'?16:90);f.serviceCapacity=capacity;let left=capacity;const fee=Math.min(Math.max(0,f.serviceFee||0),kind==='school'?G.policy.privateTuitionCap:G.policy.privateFireFeeCap);
  const homes=G.households.filter(h=>h.people.length&&privateServiceDistance(f,h)<=40).sort((a,b)=>householdLiquidity(a)/a.people.length-householdLiquidity(b)/b.people.length||a.id-b.id);
  for(const h of homes){if(left<=.0001)break;const publicGap=kind==='school'?Math.max(0,privateSchoolPublicGap(h)-(state.school[h.id]||0)):Math.max(0,1-publicFireResponse(readBuild(h.home))-(state.fire[h.id]||0));if(publicGap<=.001)continue;if(kind==='fire'&&clamp(1-privateServiceDistance(f,h)/58,0,1)*quality*.9<=publicFireResponse(readBuild(h.home))+.03)continue;const candidates=kind==='school'?h.people.filter(id=>privateEligiblePupil(G.people[id])&&!enrolled.has(id)&&!publicStudents.has(id)):h.people.slice();if(!candidates.length)continue;
   const count=Math.min(left,candidates.length*publicGap),purchase=privateServicePurchase(h,count,fee,vouchers),served=purchase.served,householdPaid=purchase.paid,subsidy=purchase.subsidy;
   // No forced debt or rescue bill. A family declines unaffordable service.
   if(served<=0)continue;(state.allocations[f.id]||(state.allocations[f.id]={}))[h.id]={served,paid:householdPaid,subsidy};h.cash-=householdPaid;h.discretionary+=householdPaid;h.privateServiceFees+=householdPaid;G.treasury-=subsidy;G.cumulative.spending+=subsidy;vouchers-=subsidy;enterpriseRevenue(f,householdPaid+subsidy);f.privateReceipts+=householdPaid;f.privateVouchers+=subsidy;f.clientsToday+=served;left-=served;state.vouchers+=subsidy;
   if(kind==='school'){state.tuition+=householdPaid;state.pupils+=served;state.school[h.id]=(state.school[h.id]||0)+served/Math.max(1,h.people.length)*quality;const teaching=served/candidates.length;for(const id of candidates){enrolled.add(id);const p=G.people[id];p.privateLearningDays=(p.privateLearningDays||0)+teaching*quality;if(p.privateLearningDays>=120){p.privateLearningDays-=120;p.skill=Math.min(1.3,p.skill+.1);G.privateTrainingCompletions=(G.privateTrainingCompletions||0)+1;story(p.name+' completed a fee-funded learning term at '+f.name+'.','good',f.building,h.id)}}}
   else{state.memberships+=householdPaid;state.fireMembers+=served;state.fire[h.id]=(state.fire[h.id]||0)+served/h.people.length*quality;}
  }
 }
 for(const f of G.firms)if(f.privateService&&!f.closed){f.serviceClientTrend=(f.serviceClientTrend??f.clientsToday)*.965+f.clientsToday*.035;f.serviceWeakDays=f.cash<workerIncome(f)*Math.max(1,f.jobs)*3&&(f.clientsToday<.5||f.revenue<f.expenses)?(f.serviceWeakDays||0)+1:0;if(f.serviceWeakDays>=90)liquidateFirm(f,'90 days of unfunded private service operations');}
 const publicCoverage=G.serviceProvision?.school?.coverage||0,additional=G.households.reduce((n,h)=>n+(state.school[h.id]||0)*h.people.length,0)/Math.max(1,G.stats.population);G.actualServiceFunding.school=clamp(publicCoverage+additional,0,1);
}
function privateFireResponse(b){let best=0;const subscription=b.hh>=0?G.privateServiceProvision?.fire?.[b.hh]||0:0;for(const f of G.firms.filter(f=>f.privateService==='fire'&&!f.closed&&f.serviceCapacity>0)){const distance=roadServiceDistance(readBuild(f.building),b);if(!Number.isFinite(distance))continue;const reach=clamp(1-distance/58,0,1),staff=clamp(f.serviceCapacity/180,0,1);best=Math.max(best,reach*staff*(.25+.65*subscription));}return best}
function seekPrivateServiceInvestment(requested=null){
 if(!G.policy.privateServices)return 'Private service entry is not licensed.';if(!G.autoBuild&&!requested)return 'Private development is paused.';if(G.projects.some(p=>p.privateService))return 'A private service site is already under construction.';
 for(const kind of requested?[requested]:['school','fire']){
  if(!['school','fire'].includes(kind))continue;const wage=Math.max(G.policy.minWage,36),cost=buildCost[kind],capital=6000,minimum=kind==='school'?1:2,requiredReturn=(cost+capital)*((G.policy.policyRate||0)/100+.08)/360;
  const available=G.people.filter(p=>!p.publicWork&&!p.previousPublicRole&&privateQualified(p,{privateService:kind})).length;if(available<minimum)continue;
  const evaluate=(site,exclude=null)=>{const net=graph(),port=net.portals.get(site.id)??roadOffsets.map(([dx,dy])=>roadId(site.x+dx,site.y+dy)).find(id=>G.tiles[id]===1),distances=privateServiceDistances(port),bids=G.people.filter(p=>!p.publicWork&&!p.previousPublicRole&&privateQualified(p,{privateService:kind})&&(distances.get(net.portals.get(G.households[p.hh]?.home))??Infinity)<=40).map(p=>p.job<0?wage:Math.max(wage,workerIncome(G.firms[p.job])*1.121)).sort((a,b)=>a-b),demand=privateServiceDemand(kind,site,exclude),plans=[];
   for(let staff=minimum;staff<=2;staff++){if(staff>bids.length)continue;const offered=bids[staff-1],fee=privateServiceFee(kind,demand,staff,offered),forecast=privateServiceForecast(kind,site,fee,staff,exclude,offered);if(forecast.net>requiredReturn)plans.push(forecast);}return plans.sort((a,b)=>b.net-a.net)[0]||null;};
  let awaitingReview=false;
  for(const closed of G.firms.filter(f=>f.privateService===kind&&f.closed&&G.day-(f.closedDay||0)>=120)){
   const plan=evaluate(readBuild(closed.building),closed.id);if(!plan){delete closed.serviceRecoverySince;continue;}
   // Require viable demand in two monthly reviews before risking fresh capital.
   if(closed.serviceRecoverySince==null){closed.serviceRecoverySince=G.day;awaitingReview=true;continue;}if(G.day-closed.serviceRecoverySince<30){awaitingReview=true;continue;}
   if(G.region<=capital+50000)continue;G.region-=capital;closed.cash+=capital;closed.owner=-1;readBuild(closed.building).owner=-1;closed.closed=false;closed.jobs=plan.staff;closed.wage=plan.wage;closed.strain=0;closed.lossDays=0;closed.serviceWeakDays=0;closed.serviceFee=plan.fee;closed.serviceClientTrend=plan.clients;delete closed.serviceRecoverySince;
   story('A new operator recapitalized '+closed.name+' after two viable fee-paying demand reviews; '+plan.staff+' planned staff, '+policyNumber(plan.clients)+' forecast clients/day.','good',closed.building);return 'A provider has been recapitalized after sustained demand reviews.';
  }
  if(awaitingReview)continue;
  if(G.firms.filter(f=>f.privateService===kind&&!f.closed).length>=Math.max(1,Math.ceil(G.stats.population/(kind==='school'?180:400))))continue;
  const candidates=buildableCandidates('housing').filter(p=>canPlace(p.x,p.y,true,kind)).slice(0,50),choices=candidates.map(p=>({p,plan:evaluate(p)})).filter(o=>o.plan).sort((a,b)=>b.plan.net-a.plan.net),choice=choices[0];if(!choice||G.region<cost+capital+50000)continue;
  if(!privateContract(cost))return 'Construction capital is unavailable.';const {p:site,plan}=choice,b=startDevelopmentProject('firm',site,cost*10,45,{firmKind:kind,capital,privateService:kind,serviceFee:plan.fee});if(!b)return 'No permitted, connected site is available.';
  const project=G.projects.find(p=>p.id===b.id);G.region-=capital;project.serviceEscrow=capital;project.serviceStaff=plan.staff;project.serviceWage=plan.wage;b.title={kind:'investor',id:0};
  story('An entrepreneur financed a private '+(kind==='school'?'school':'fire brigade')+'. Forecast: '+policyNumber(plan.clients)+' paying clients/day, '+money(plan.payroll+plan.overhead)+' operating costs/day; 45 funded construction days. Public competition, affordability and qualified staffing can change.','neutral',b.id);return 'An entrepreneur has financed a new service site.';
 }return 'No proposal covers qualified payroll, operating costs and capital return from currently unserved, affordable customers. Existing providers, public coverage, family budgets, fees and actual vouchers affect viability.';
}
function privateServiceInvestmentDay(){if(G.day%30===0)seekPrivateServiceInvestment()}
function validatePrivateServices(data){if(data.projects.some(p=>p.serviceWage!=null&&(!p.privateService||!Number.isFinite(p.serviceWage)||p.serviceWage<0||p.serviceWage>1000)))return false;if(data.firms.some(f=>f.serviceWeakDays!=null&&(!Number.isInteger(f.serviceWeakDays)||f.serviceWeakDays<0||f.serviceWeakDays>90)))return false;if(data.firms.some(f=>f.serviceClientTrend!=null&&(!Number.isFinite(f.serviceClientTrend)||f.serviceClientTrend<0||f.serviceClientTrend>data.people.length))||data.firms.some(f=>f.serviceRecoverySince!=null&&(!Number.isInteger(f.serviceRecoverySince)||f.serviceRecoverySince<1||f.serviceRecoverySince>data.day))||data.projects.some(p=>p.serviceStaff!=null&&(!p.privateService||!Number.isInteger(p.serviceStaff)||p.serviceStaff<1||p.serviceStaff>2)))return false;if(data.projects.some(p=>p.serviceEscrow!=null&&!p.privateService))return false;if(data.privateTrainingCompletions!=null&&(!Number.isSafeInteger(data.privateTrainingCompletions)||data.privateTrainingCompletions<0))return false;return data.firms.every(f=>!f.privateService||['school','fire'].includes(f.privateService)&&f.kind===f.privateService&&Number.isFinite(f.serviceFee)&&f.serviceFee>=0&&f.serviceFee<=20)&&data.people.every(p=>p.privateLearningDays==null||Number.isFinite(p.privateLearningDays)&&p.privateLearningDays>=0&&p.privateLearningDays<121)&&data.projects.every(p=>!p.privateService||p.kind==='firm'&&p.firmKind===p.privateService&&['school','fire'].includes(p.privateService)&&Number.isFinite(p.serviceFee)&&p.serviceFee>=0&&p.serviceFee<=20&&Number.isFinite(p.serviceEscrow)&&p.serviceEscrow>=0&&p.serviceEscrow<=1000000)}

const publicCivicCoverage=localCivicCoverage;localCivicCoverage=function(kind,id){const base=publicCivicCoverage(kind,id);return kind==='school'?clamp(base+(G.privateServiceProvision?.school?.[id]||0),0,1):base};
let privatePublicFireCache = null;
function publicFireResponse(b) {
 if (!b) return 0;
 const net = graph(), funded = G.actualServiceFunding?.fire, budget = G.policy.defenseBudget;
 if (!privatePublicFireCache || privatePublicFireCache.town !== G || privatePublicFireCache.net !== net || privatePublicFireCache.day !== G.day || privatePublicFireCache.funded !== funded || privatePublicFireCache.budget !== budget || privatePublicFireCache.count !== G.buildings.length || privatePublicFireCache.population !== G.stats.population) {
  privatePublicFireCache = {town:G, net, day:G.day, funded, budget, count:G.buildings.length, population:G.stats.population, power:defensePower(), stations:G.buildings.filter(s=>s.kind==='fire'&&isPublicFacility(s)), values:new Map()};
 }
 const cache = privatePublicFireCache;
 if (!cache.values.has(b.id)) {
  const distance = cache.stations.length ? Math.min(...cache.stations.map(station => roadServiceDistance(station, b))) : 80;
  cache.values.set(b.id, clamp(1-distance/58,0,1)*cache.power);
 }
 return cache.values.get(b.id);
}
