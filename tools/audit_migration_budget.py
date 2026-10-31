#!/usr/bin/env python3
"""Source-bound read-only migration fixtures and compact municipal-flow audit."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
PROBE=r'''
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
  if(variant==='disconnected'){for(const id of roadNeighborsForBuilding(b)){if(G.tiles[id]===1)G.tiles[id]=0;}invalidateRoads(false);}
  recompute();G.stats.employment=100;
  const total=totalMoney(),region=G.region,oldCount=G.people.length,h=addHouseholdAt(b,2500);
  return {seed:seedValue,variant,admitted:!!h,newPeople:G.people.slice(oldCount).map(p=>({id:p.id,age:p.age,skill:p.skill,health:p.health,job:p.job,household:p.hh})),capital:h?.cash||0,effectiveWage:workerIncome(f),expectedNetIncome:h?openingHouseholdIncome(h):null,expectedEssentials:h?expectedHouseholdEssentials(h):null,estimatedRent:h?urbanHousingRent(h,b,h.people.length*(3.1+G.policy.zoningRestriction*.035)*(G.housingMarket?.rentIndex||1)*urbanRentMultiplier(b)):null,regionDelta:G.region-region,cashDrift:totalMoney()-total,home:b.id,homeConnected:graph().portals.has(b.id),vacancies:sum(G.firms.filter(f=>!f.closed),f=>Math.max(0,f.jobs-f.workers.length)),household:h?{id:h.id,home:h.home,income:h.income,people:h.people}:null};
 },
 newbornBoundary:(seedValue)=>{
  __townTest.reset('settlement',seedValue);G.autoBuild=false;clock(360);
  for(const h of G.households){h.stress=0;h.lastBirth=-720;}
  const before=G.people.length;birthsAndGenerations();const ids=G.people.slice(before).map(p=>p.id),birthAges=ids.map(id=>G.people[id].age);yearlyDemographics();
  return {seed:seedValue,ids,birthAges,afterAnnualAges:ids.map(id=>G.people[id].age),postTickAgeZeroHeuristicWouldMiss:ids.filter(id=>G.people[id].age!==0).length};
 }
 };
})();
'''
# Resolve immediate road-adjacent tiles without inventing passenger links.
PROBE=PROBE.replace('roadNeighborsForBuilding(b)', '[...graph().neighbors.keys()].filter(id=>Math.abs(id%T-b.x)+Math.abs((id/T|0)-b.y)<=3)')

def write(path,value):
 temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',default='reports/migration-budget-audit');args=parser.parse_args();out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True)
 source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest();result={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':sha,'controlledFixtures':True,'productionRulesChanged':False,'cases':[]}
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage']);page=browser.new_page();page.set_default_timeout(120000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);page.add_script_tag(content=source.decode().replace('// SOURCE: 99-instrumentation.js',PROBE+'\n// SOURCE: 99-instrumentation.js'));page.locator('#newTown').click();page.locator('#pause').click()
  for seed in [42,101,909]:
   for name in ['departures','wealthPlacement','debt','duplicate','newbornBoundary']:
    try:row=page.evaluate('o=>__migrationAudit[o.name](o.seed)',{'name':name,'seed':seed});result['cases'].append({'case':name,'seed':seed,'outcome':row});print(name,seed,json.dumps(row),flush=True)
    except Exception as error:result['cases'].append({'case':name,'seed':seed,'error':str(error)});print('RETAINED',name,seed,str(error),flush=True)
   for variant in ['normal','no-vacancies','unfunded-vacancies','no-services','high-rent','low-wages','disconnected']:
    try:row=page.evaluate('o=>__migrationAudit.arrivalGate(o.seed,o.variant)',{'seed':seed,'variant':variant});result['cases'].append({'case':'arrivalGate','seed':seed,'outcome':row});print('arrivalGate',seed,variant,row['admitted'],flush=True)
    except Exception as error:result['cases'].append({'case':'arrivalGate','seed':seed,'variant':variant,'error':str(error)});print('RETAINED arrivalGate',seed,variant,str(error),flush=True)
   write(out/'fixtures.json',{**result,'pageErrors':errors})
  browser.close()
 assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
 print('Source unchanged; outcomes retained without treating confirmed defects as passes',flush=True)
if __name__=='__main__':main()
