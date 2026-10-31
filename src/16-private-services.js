// Fee-funded institutions are ordinary firms with actual payroll, private owners
// and bankruptcy. Public facilities never acquire private capacity for free.
function isPublicFacility(b){return !(b.firm>=0&&G.firms[b.firm]?.privateService)}
function privateQualified(p,f){return !p.deceased&&!p.movedAway&&p.age>=18&&p.age<=70&&p.health>=60&&p.skill>=(f.privateService==='school'?.55:.4)}
function privateEligiblePupil(p){return !p.deceased&&!p.movedAway&&p.age>=6&&(p.age<=24||p.age<=60&&p.skill<.7)}
function privateServiceDistance(f,h){const a=graph().portals.get(f.building),b=graph().portals.get(h.home);return a==null||b==null?Infinity:roadDistance(a,b)}
function privateSchoolPublicGap(h){return 1-publicCivicCoverage('school',h.id)}
function privateServiceDemand(kind, site = null) {
 const net = graph();
 const sitePort = site ? net.portals.get(site.id) ?? roadOffsets.map(([dx, dy]) => roadId(site.x + dx, site.y + dy)).find(id => G.tiles[id] === 1) : null;
 const distances = new Map(), queue = [];
 if (sitePort != null) { distances.set(sitePort, 0); queue.push(sitePort); }
 for (let i = 0; i < queue.length; i++) { const at = queue[i], d = distances.get(at); if (d >= 40) continue; for (const next of net.neighbors.get(at) || []) if (!distances.has(next)) { distances.set(next, d + 1); queue.push(next); } }
 return G.households.filter(h => h.people.length).reduce((total, h) => {
  const home = readBuild(h.home), port = net.portals.get(h.home);
  const distance = site ? distances.get(port) ?? Infinity : 0;
  if (site && (!home || distance > 40)) return total;
  const eligible = kind === 'school' ? h.people.filter(id => privateEligiblePupil(G.people[id])).length : h.people.length;
  const publicResponse = kind === 'fire' && home ? publicFireResponse(home) : 0;
  if (kind === 'fire' && site && clamp(1 - distance / 58, 0, 1) * .72 <= publicResponse + .03) return total;
  const gap = kind === 'school' ? privateSchoolPublicGap(h) : Math.max(0, 1 - publicResponse);
  return total + eligible * gap * (householdLiquidity(h) > h.people.length * 180 ? 1 : G.policy.serviceVoucherBudget > 0 ? .6 : 0);
 }, 0);
}
function privateServiceFee(kind,demand,staff=2){const wage=Math.max(G.policy.minWage,36),capacity=staff*(kind==='school'?16:90),cap=kind==='school'?G.policy.privateTuitionCap:G.policy.privateFireFeeCap;return Math.min(cap,Math.max(kind==='school'?1:.35,(wage*staff+6)*1.22/Math.max(1,Math.min(demand,capacity))))}
function planPrivateService(f){if(G.day%30!==0)return;const demand=privateServiceDemand(f.privateService,readBuild(f.building)),target=privateServiceFee(f.privateService,demand,Math.max(2,f.jobs));f.serviceFee=(f.serviceFee||target)*.8+target*.2;f.jobs=clamp(Math.ceil((f.clientsYesterday||0)/(f.privateService==='school'?16:90)),2,f.privateService==='school'?5:3);}
function recruitPrivateServiceStaff(){for(const f of G.firms.filter(f=>f.privateService&&!f.closed)){if(f.workers.length>=f.jobs||f.cash<workerIncome(f)*20)continue;for(const p of G.people){if(f.workers.length>=f.jobs)break;if(p.job<0||p.job===f.id||p.publicWork||p.previousPublicRole||!privateQualified(p,f)||G.day-(p.privateJobChange||-90)<60)continue;const old=G.firms[p.job];if(!old||old.closed||workerIncome(f)<workerIncome(old)*1.12||privateServiceDistance(f,G.households[p.hh])>40)continue;old.workers=old.workers.filter(id=>id!==p.id);p.job=f.id;p.privateJobChange=G.day;f.workers.push(p.id);}}}
function privateServiceDay(){
 if(G.privateServiceProvision?.day===G.day)return;
 const state={version:1,day:G.day,school:{},fire:{},tuition:0,memberships:0,vouchers:0,pupils:0,fireMembers:0};G.privateServiceProvision=state;let vouchers=Math.min(G.treasury,G.policy.serviceVoucherBudget||0);const enrolled=new Set(),publicStudents=new Set((G.civicTraining||[]).filter(c=>publicCivicCoverage('school',G.people[c.person]?.hh)>0).map(c=>c.person));
 for(const h of G.households)h.privateServiceFees=0;
 for(const f of G.firms.filter(f=>f.privateService)){f.clientsYesterday=f.clientsToday||0;f.clientsToday=0;f.privateReceipts=0;f.privateVouchers=0;f.serviceCapacity=0;if(f.closed)continue;const qualified=workingStaff(f).filter(id=>privateQualified(G.people[id],f));if(!qualified.length)continue;const kind=f.privateService,quality=clamp(qualified.reduce((n,id)=>n+G.people[id].skill,0)/qualified.length/.75,.6,1),capacity=qualified.length*(kind==='school'?16:90);f.serviceCapacity=capacity;let left=capacity;const fee=Math.min(Math.max(0,f.serviceFee||0),kind==='school'?G.policy.privateTuitionCap:G.policy.privateFireFeeCap);
  const homes=G.households.filter(h=>h.people.length&&privateServiceDistance(f,h)<=40).sort((a,b)=>householdLiquidity(a)/a.people.length-householdLiquidity(b)/b.people.length||a.id-b.id);
  for(const h of homes){if(left<=.0001)break;const publicGap=kind==='school'?Math.max(0,privateSchoolPublicGap(h)-(state.school[h.id]||0)):Math.max(0,1-publicFireResponse(readBuild(h.home))-(state.fire[h.id]||0));if(publicGap<=.001)continue;if(kind==='fire'&&clamp(1-privateServiceDistance(f,h)/58,0,1)*quality*.9<=publicFireResponse(readBuild(h.home))+.03)continue;const candidates=kind==='school'?h.people.filter(id=>privateEligiblePupil(G.people[id])&&!enrolled.has(id)&&!publicStudents.has(id)):h.people.slice();if(!candidates.length)continue;
   const count=Math.min(left,candidates.length*publicGap),due=count*fee,reserve=h.people.length*100,affordable=Math.min(Math.max(0,h.cash-reserve),Math.max(0,(h.income||0)*.12+Math.max(0,householdLiquidity(h)-h.people.length*800)*.001));let householdPaid=Math.min(due,affordable),subsidy=householdLiquidity(h)<h.people.length*500?Math.min(vouchers,due-householdPaid):0,share=due>0?(householdPaid+subsidy)/due:0;
   // No forced debt or rescue bill. A family declines unaffordable service.
   if(share<.5)continue;const served=count*share;householdPaid=Math.min(due-subsidy,householdPaid);h.cash-=householdPaid;h.discretionary+=householdPaid;h.privateServiceFees+=householdPaid;G.treasury-=subsidy;G.cumulative.spending+=subsidy;vouchers-=subsidy;enterpriseRevenue(f,householdPaid+subsidy);f.privateReceipts+=householdPaid;f.privateVouchers+=subsidy;f.clientsToday+=served;left-=served;state.vouchers+=subsidy;
   if(kind==='school'){state.tuition+=householdPaid;state.pupils+=served;state.school[h.id]=(state.school[h.id]||0)+served/Math.max(1,h.people.length)*quality;const teaching=served/candidates.length;for(const id of candidates){enrolled.add(id);const p=G.people[id];p.privateLearningDays=(p.privateLearningDays||0)+teaching*quality;if(p.privateLearningDays>=120){p.privateLearningDays-=120;p.skill=Math.min(1.3,p.skill+.1);G.privateTrainingCompletions=(G.privateTrainingCompletions||0)+1;story(p.name+' completed a fee-funded learning term at '+f.name+'.','good',f.building,h.id)}}}
   else{state.memberships+=householdPaid;state.fireMembers+=served;state.fire[h.id]=(state.fire[h.id]||0)+served/h.people.length*quality;}
  }
 }
 const publicCoverage=G.serviceProvision?.school?.coverage||0,additional=G.households.reduce((n,h)=>n+(state.school[h.id]||0)*h.people.length,0)/Math.max(1,G.stats.population);G.actualServiceFunding.school=clamp(publicCoverage+additional,0,1);
}
function privateFireResponse(b){let best=0;const subscription=b.hh>=0?G.privateServiceProvision?.fire?.[b.hh]||0:0;for(const f of G.firms.filter(f=>f.privateService==='fire'&&!f.closed&&f.serviceCapacity>0)){const distance=roadServiceDistance(b,readBuild(f.building));if(!Number.isFinite(distance))continue;const reach=clamp(1-distance/58,0,1),staff=clamp(f.serviceCapacity/180,0,1);best=Math.max(best,reach*staff*(.25+.65*subscription));}return best}
function seekPrivateServiceInvestment(requested=null){
 if(!G.policy.privateServices)return 'Private service entry is not licensed.';if(!G.autoBuild&&!requested)return 'Private development is paused.';if(G.projects.some(p=>p.privateService))return 'A private service site is already under construction.';
 for(const kind of requested?[requested]:['school','fire']){const demand=privateServiceDemand(kind),fee=privateServiceFee(kind,demand),wage=Math.max(G.policy.minWage,36),served=Math.min(demand,kind==='school'?32:180),net=served*fee-wage*2-6,cost=buildCost[kind],capital=6000,requiredReturn=(cost+capital)*((G.policy.policyRate||0)/100+.08)/360;
  if(net<=requiredReturn||demand<(kind==='school'?16:60))continue;if(G.firms.filter(f=>f.privateService===kind&&!f.closed).length>=Math.max(1,Math.ceil(G.stats.population/(kind==='school'?180:400))))continue;
  const closed=G.firms.find(f=>f.privateService===kind&&f.closed&&G.day-(f.closedDay||0)>=120);if(closed&&G.region>capital+50000&&privateServiceDemand(kind,readBuild(closed.building))>=served*.6){G.region-=capital;closed.cash+=capital;closed.owner=-1;readBuild(closed.building).owner=-1;closed.closed=false;closed.jobs=2;closed.wage=wage;closed.strain=0;closed.lossDays=0;closed.serviceFee=fee;story('A new private operator recapitalized '+closed.name+' after reviewing fee-paying demand.','good',closed.building);return 'A provider has been recapitalized.'}
  const available=G.people.filter(p=>!p.publicWork&&!p.previousPublicRole&&privateQualified(p,{privateService:kind})&&(p.job<0||workerIncome(G.firms[p.job])<=wage/1.12)).length;if(available<2)continue;
  const candidates=buildableCandidates('housing').filter(p=>canPlace(p.x,p.y,true,kind)).slice(0,50),site=candidates.map(p=>({p,demand:privateServiceDemand(kind,p)})).filter(o=>o.demand>=(kind==='school'?16:60)).sort((a,b)=>b.demand-a.demand)[0]?.p;if(!site||G.region<cost+capital+50000)continue;
  const localDemand=privateServiceDemand(kind,site),localFee=privateServiceFee(kind,localDemand);if(Math.min(localDemand,kind==='school'?32:180)*localFee-wage*2-6<=requiredReturn)continue;
  if(!privateContract(cost))return 'Construction capital is unavailable.';const b=startDevelopmentProject('firm',site,cost*10,45,{firmKind:kind,capital,privateService:kind,serviceFee:localFee});if(!b)return 'No permitted, connected site is available.';const project=G.projects.find(p=>p.id===b.id);G.region-=capital;project.serviceEscrow=capital;b.title={kind:'investor',id:0};story('An entrepreneur financed a private '+(kind==='school'?'school':'fire brigade')+'. Construction takes45 funded workdays; fees, qualified staff and actual demand must sustain it.','neutral',b.id);return 'An entrepreneur has financed a new service site.';
 }return 'No investor cleared the staffing, fee-paying demand and return tests. Public coverage, household income, fee caps and finance affect viability.';
}
function privateServiceInvestmentDay(){if(G.day%30===0)seekPrivateServiceInvestment()}
function validatePrivateServices(data){if(data.privateTrainingCompletions!=null&&(!Number.isSafeInteger(data.privateTrainingCompletions)||data.privateTrainingCompletions<0))return false;return data.firms.every(f=>!f.privateService||['school','fire'].includes(f.privateService)&&f.kind===f.privateService&&Number.isFinite(f.serviceFee)&&f.serviceFee>=0&&f.serviceFee<=20)&&data.people.every(p=>p.privateLearningDays==null||Number.isFinite(p.privateLearningDays)&&p.privateLearningDays>=0&&p.privateLearningDays<121)&&data.projects.every(p=>!p.privateService||p.kind==='firm'&&p.firmKind===p.privateService&&['school','fire'].includes(p.privateService)&&Number.isFinite(p.serviceFee)&&p.serviceFee>=0&&p.serviceFee<=20&&Number.isFinite(p.serviceEscrow)&&p.serviceEscrow>=0&&p.serviceEscrow<=1000000)}

const publicCivicCoverage=localCivicCoverage;localCivicCoverage=function(kind,id){const base=publicCivicCoverage(kind,id);return kind==='school'?clamp(base+(G.privateServiceProvision?.school?.[id]||0),0,1):base};
function publicFireResponse(b){if(!b)return 0;const stations=G.buildings.filter(s=>s.kind==='fire'&&isPublicFacility(s)),distance=stations.length?Math.min(...stations.map(s=>roadServiceDistance(b,s))):80;return clamp(1-distance/58,0,1)*defensePower()}
