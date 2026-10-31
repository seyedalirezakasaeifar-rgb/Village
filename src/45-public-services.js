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
 const prior=G.households[young.hh],cash=Math.min(1800,prior.cash*.25),h={...prior,id:G.households.length,name:young.name.split(' ').at(-1),cash,home:vacant.id,owner:-1,people:[young.id],deposits:{},income:0,rent:0,food:0,tax:0,aid:0,stress:25,last:[]};
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
