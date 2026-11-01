// Councils authorize service budgets; procurement chooses sites and finances works.
function municipalProcurement(){
 if(G.day%30!==0||G.projects.some(p=>p.kind==='public'))return;
 const services=[['school',260,G.policy.educationBudget],['clinic',350,G.policy.healthBudget],['police',400,G.policy.policeBudget],['fire',450,G.policy.defenseBudget]];
 for(const [kind,capacity,budget] of services){
  const count=G.buildings.filter(b=>b.kind===kind&&isPublicFacility(b)).length;
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
 if(creatorCapacityReason(0,1))return;
 if(G.day%90!==0)return;
 const vacant=G.buildings.find(b=>b.kind==='home'&&!b.redevelopment&&!b.relocationReserve&&migrationHousingStatus(b).available>0);if(!vacant)return;
 const young=G.people.find(p=>!p.deceased&&!p.movedAway&&p.age>=20&&p.age<31&&p.job>=0&&G.households[p.hh].people.length>2&&G.households[p.hh].cash>3600);if(!young||!migrationCanReach(vacant,G.firms[young.job]))return;
 const prior=G.households[young.hh],cash=Math.min(1800,prior.cash*.25),h={...prior,id:G.households.length,name:fromEnd(young.name.split(' ')),cash,home:vacant.id,owner:-1,people:[young.id],deposits:{},netIncomeTrend:workerIncome(G.firms[young.job])*(1-G.policy.incomeTax/100),incomeVariance:0,essentialDueTrend:undefined,income:0,rent:0,food:0,tax:0,aid:0,stress:25,last:[]};
 prior.cash-=cash;prior.people=prior.people.filter(id=>id!==young.id);young.hh=h.id;G.households.push(h);migrationRegisterTenancy(h,vacant);h.essentialDueTrend=expectedHouseholdEssentials(h);
 book(prior.name+' household',h.name+' household',cash,'Savings divided on household formation',vacant.id);
 story(young.name+' formed a household and rented an existing vacant cottage.','good',vacant.id,h.id);
}

function occupyVacantHousing(){
 if(G.day%30!==0||G.stats.population>=2000)return;
 const vacancies=G.buildings.filter(b=>['home','apartment','tower'].includes(b.kind)&&!b.redevelopment&&!b.relocationReserve&&migrationHousingStatus(b).available>0);
 for(const vacancy of vacancies){const h=addHouseholdAt(vacancy,2500);if(!h)continue;migrationRegisterTenancy(h,vacancy);story('The '+h.name+' household chose a vacant home after comparing reachable paid work, living costs and outside opportunities.','good',vacancy.id,h.id);return;}
}
