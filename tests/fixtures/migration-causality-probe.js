
window.__migrationAudit=(()=>{
 const alive=p=>!p.deceased&&!p.movedAway,sum=(xs,f)=>xs.reduce((n,x)=>n+(Number(f(x))||0),0);
 function clock(day){G.day=day;G.year=Math.floor(day/360)+1;G.month=Math.floor(day/30)%12+1;}
 function departureFixture(seedValue,deposit,withdraw=false,borrow=false){
  __townTest.reset('settlement',seedValue);G.autoBuild=false;
  const h=G.households.filter(h=>h.people.length).sort((a,b)=>b.cash-a.cash)[0],home=readBuild(h.home);
  for(const a of G.households)a.stress=0;
  const loan=borrow?bankLoan('household',h.id,100,360):null;
  if(deposit>0){const bank=G.banks.find(b=>!b.closed);depositTransfer(h,bank,deposit);}
  G.region+=h.cash;h.cash=0;h.stress=90;if(withdraw)for(const [id,amount]of Object.entries(h.deposits||{}))withdrawal(h,G.banks[+id],amount);clock(30);
  G.stats.hardship=70;G.stats.unemployment=60;G.regionalDemand=.5;
  const original=rngState;let rollSeed=1;for(;rollSeed<1000;rollSeed++){rngState=rollSeed;if(random()<.27)break;}rngState=rollSeed;
  const total=totalMoney(),before={people:h.people.slice(),cash:h.cash,deposits:{...h.deposits},liquidity:householdLiquidity(h),title:home.title,home:h.home,region:G.region,ownedProperties:G.buildings.filter(b=>b.owner===h.id).map(b=>({id:b.id,value:b.value})),loans:G.loans.filter(l=>l.ownerType==='household'&&l.ownerId===h.id).map(l=>({...l}))},n=outwardMigration();
  return {h,home,total,loan,result:{seed:seedValue,deposit,withdraw,rollSeed,departed:n,before,after:{people:h.people.slice(),cash:h.cash,deposits:{...h.deposits},home:h.home,region:G.region,title:home.title},cashDrift:totalMoney()-total}};
 }
 return {
 departures:(seedValue)=>[0,1500].map(deposit=>departureFixture(seedValue,deposit).result),
 wealthPlacement:(seedValue)=>[false,true].map(withdraw=>departureFixture(seedValue,1500,withdraw).result),
 debt:(seedValue)=>{const d=departureFixture(seedValue,1500,false,true),before=d.loan?{...d.loan}:null;clock(31);if(d.loan)loanPayments([d.loan]);return{departure:d.result,loanApproved:!!d.loan,before,after:d.loan?{...d.loan}:null,remainingDeposits:{...d.h.deposits},cashDrift:totalMoney()-d.total,ownedProperties:G.buildings.filter(b=>b.owner===d.h.id).map(b=>({id:b.id,value:b.value}))};},
 duplicate:(seedValue)=>{
  const o=departureFixture(seedValue,0),h=o.h,b=o.home;
  if(!o.result.departed)throw Error('Departure fixture did not depart');
  // Controlled sufficient vacancies; no cash, skills, residents or housing granted.
  G.firms.find(f=>!f.closed).jobs+=100;G.regionalDemand=1;recompute();G.stats.employment=100;
  const before=G.people.length;occupyVacantHousing();const replacement=b.hh;
  const afterMonth={originalEstateHome:h.home,registered:b.hh,residents:G.households.filter(a=>a.home===b.id&&a.people.length).map(a=>a.id),addedPeople:G.people.length-before};
  clock(360);G.stats.employment=100;yearlyDemographics();recompute();
  const afterYear={originalEstateHome:h.home,registered:b.hh,residents:G.households.filter(a=>a.home===b.id&&a.people.length).map(a=>({id:a.id,people:a.people.slice()})),replacementStillRegistered:b.hh===replacement,cashDrift:totalMoney()-o.total,valid:validateTown()};
  const save=archivePayload(),loadAccepted=hydrateSave(save);
  return {seed:seedValue,departure:o.result,afterMonth,afterYear,loadAccepted};
 },
 arrivalGate:(seedValue,variant)=>{
  __townTest.reset('settlement',seedValue);G.autoBuild=false;clock(30);
  const old=G.households[0],building=readBuild(old.home);
  // A controlled candidate cottage is made vacant by a real funded departure.
  const d=departureFixture(seedValue,0),b=d.home;G.regionalDemand=1;
  for(const f of G.firms)f.jobs=f.workers.length;
  const f=G.firms.find(f=>!f.closed);f.jobs+=100;
  if(variant==='no-vacancies')f.jobs=f.workers.length;
  if(variant==='unfunded-vacancies'){G.region+=f.cash;f.cash=0;}
  if(variant==='no-services'){G.policy.healthBudget=0;G.policy.educationBudget=0;G.policy.defenseBudget=0;}
  if(variant==='high-rent'){G.housingMarket.rentIndex=1.5;}
  if(variant==='low-wages')G.policy.minWage=10;
  if(variant==='low-wages')for(const firm of G.firms)firm.wage=10;
  if(variant==='disconnected'){for(const id of [...graph().neighbors.keys()].filter(id=>Math.abs(id%T-b.x)+Math.abs((id/T|0)-b.y)<=3)){if(G.tiles[id]===1)G.tiles[id]=0;}invalidateRoads(false);}
  recompute();G.stats.employment=100;
  const assessment=migrationAssessment(b,[{age:30,skill:.4,health:90},{age:30,skill:.4,health:90}],2500);
  const total=totalMoney(),region=G.region,oldCount=G.people.length,h=addHouseholdAt(b,2500);
  return {seed:seedValue,variant,assessment,admitted:!!h,newPeople:G.people.slice(oldCount).map(p=>({id:p.id,age:p.age,skill:p.skill,health:p.health,job:p.job,household:p.hh})),capital:h?.cash||0,effectiveWage:workerIncome(f),expectedNetIncome:h?openingHouseholdIncome(h):null,expectedEssentials:h?expectedHouseholdEssentials(h):null,estimatedRent:h?urbanHousingRent(h,b,h.people.length*(3.1+G.policy.zoningRestriction*.035)*(G.housingMarket?.rentIndex||1)*urbanRentMultiplier(b)):null,regionDelta:G.region-region,cashDrift:totalMoney()-total,home:b.id,homeConnected:graph().portals.has(b.id),vacancies:sum(G.firms.filter(f=>!f.closed),f=>Math.max(0,f.jobs-f.workers.length)),household:h?{id:h.id,home:h.home,income:h.income,people:h.people}:null};
 },
 newbornBoundary:(seedValue)=>{
  __townTest.reset('settlement',seedValue);G.autoBuild=false;clock(360);
  for(const h of G.households){h.stress=0;h.lastBirth=-720;}
  const before=G.people.length;birthsAndGenerations();const ids=G.people.slice(before).map(p=>p.id),birthAges=ids.map(id=>G.people[id].age);yearlyDemographics();
  return {seed:seedValue,ids,birthAges,afterAnnualAges:ids.map(id=>G.people[id].age),postTickAgeZeroHeuristicWouldMiss:ids.filter(id=>G.people[id].age!==0).length};
 }
 };
})();
