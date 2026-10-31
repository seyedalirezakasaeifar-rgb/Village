#!/usr/bin/env python3
"""Matched municipal burden experiments with source-hook demographic accounting."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
PROBE=r'''
window.__migrationLedger=(()=>{
 let enabled=false,stack=[],flows={},birthIDs=new Set(),created={},admissions=[],events=[],start=0,opening=0,cash=0,counts={},issues=[],payrollCall=0;
 const sum=(xs,f)=>xs.reduce((n,x)=>n+(Number(f(x))||0),0),alive=p=>!p.deceased&&!p.movedAway;
 function moneyWrap(label,fn){return function(...args){if(!enabled)return fn.apply(this,args);const key=typeof label==='function'?label(args):label,frame={before:G.treasury,children:0};stack.push(frame);try{return fn.apply(this,args)}finally{const net=G.treasury-frame.before,own=net-frame.children;flows[key]=(flows[key]||0)+own;stack.pop();if(stack.length)stack[stack.length-1].children+=net;}};}
 transferTreasury=moneyWrap(a=>'tax:'+a[1],transferTreasury);
 fundedPublicPayroll=moneyWrap(a=>'operations:'+(a[3]||['police','fire','outreach','commuter','roads','militia'][payrollCall++]||'other'),fundedPublicPayroll);
 regionalCapitalMarket=moneyWrap('finance:regional-reserve',regionalCapitalMarket);
 municipalProcurement=moneyWrap('capital:automatic-public-procurement',municipalProcurement);
 urbanMunicipalHousingDay=moneyWrap('operations:municipal-housing',urbanMunicipalHousingDay);
 bankDaily=moneyWrap('finance:other-bank',bankDaily);
 updateCouncilAndMissions=moneyWrap('progress:regional-development-grants',updateCouncilAndMissions);
 dailyEconomy=moneyWrap('daily:aid-pensions-subsidies-housing-other',dailyEconomy);
 const birthBase=birthsAndGenerations;birthsAndGenerations=function(...args){const n=G?.people.length||0,result=birthBase.apply(this,args);if(enabled)for(let i=n;i<G.people.length;i++){birthIDs.add(i);created[i]={age:G.people[i].age,skill:G.people[i].skill,health:G.people[i].health};}return result;};
 const admitBase=addHouseholdAt;addHouseholdAt=function(b,capital){if(!enabled)return admitBase.apply(this,arguments);const before=G.region,n=G.people.length,result=admitBase.apply(this,arguments);if(admissions.length<3000)admissions.push({day:G.day,site:b.id,requestedCapital:capital,accepted:!!result,regionDelta:G.region-before,householdCash:result?.cash||0,ids:G.people.slice(n).map(p=>p.id),ages:G.people.slice(n).map(p=>p.age),skills:G.people.slice(n).map(p=>p.skill),validHome:!!readBuild(b.id)});for(let i=n;i<G.people.length;i++)created[i]={age:G.people[i].age,skill:G.people[i].skill,health:G.people[i].health};return result;};
 const baseTick=tick;tick=moneyWrap('tick:municipal-interest-and-other',function(){if(!enabled)return baseTick();
  payrollCall=0;const n=G.people.length,before=G.people.filter(alive).length,oldDead=new Set(G.people.filter(p=>p.deceased).map(p=>p.id)),oldOut=new Set(G.people.filter(p=>p.movedAway).map(p=>p.id));baseTick();
  const births=G.people.slice(n).filter(p=>birthIDs.has(p.id)),arrivals=G.people.slice(n).filter(p=>!birthIDs.has(p.id)),deaths=G.people.filter(p=>p.deceased&&!oldDead.has(p.id)),out=G.people.filter(p=>p.movedAway&&!oldOut.has(p.id));
  for(const [kind,people]of [['births',births],['immigration',arrivals],['deaths',deaths],['emigration',out]]){counts[kind]+=people.length;for(const p of people)events.push({day:G.day,kind,id:p.id,ageAtCreation:created[p.id]?.age??null,ageAfterDay:p.age,skill:p.skill,household:p.hh,home:G.households[p.hh]?.home,job:p.job});}
  const after=G.people.filter(alive).length;if(after!==before+births.length+arrivals.length-deaths.length-out.length)throw Error('Demographic identity failed');
  const residents=new Map();for(const h of G.households){if(!h.people.length)continue;const b=readBuild(h.home);if(!b){counts.invalidHomeDays++;if(issues.length<100)issues.push({day:G.day,kind:'Missing home',household:h.id,home:h.home});continue;}let list=residents.get(b.id);if(!list){list=[];residents.set(b.id,list);}list.push(h.id);const registered=b.kind==='home'?b.hh===h.id:(b.units||[]).includes(h.id);if(!registered){counts.unregisteredHouseholdDays++;if(issues.length<100)issues.push({day:G.day,kind:'Unregistered resident household',household:h.id,home:b.id,registered:b.hh,units:b.units});}}
  for(const [id,list]of residents){const b=readBuild(id),capacity=b.kind==='home'?1:b.kind==='apartment'?4:b.kind==='tower'?9:1;if(list.length>capacity){counts.overCapacityBuildingDays++;if(issues.length<100)issues.push({day:G.day,kind:'Household capacity exceeded',home:id,capacity,households:list});}}
 });
 function snapshot(){const service=G.serviceProvision||{},total=Object.values(flows).reduce((n,x)=>n+x,0);return {day:G.day,elapsedYears:(G.day-start)/360,population:G.stats.population,employment:G.stats.employment,hardship:G.stats.hardship,health:G.health,education:G.education,roadCondition:G.stats.roadCondition,treasury:G.treasury,publicReserve:G.publicReserve,municipalDebt:G.debt,regionCash:G.region,flows:{...flows},treasuryReconciliation:G.treasury-opening-total,cashDrift:totalMoney()-cash,goodsError:Math.max(...goodsBalance().map(x=>Math.abs(x.error))),valid:validateTown(),counts:{...counts},publicFacilities:G.buildings.filter(b=>['school','clinic','police','fire'].includes(b.kind)&&isPublicFacility(b)).map(b=>({id:b.id,kind:b.kind,condition:b.condition})),services:{health:service.health,school:service.school},policy:{...G.policy},cumulative:{...G.cumulative},jobs:sum(G.firms.filter(f=>!f.closed),f=>f.jobs),households:G.households.filter(h=>h.people.length).length};}
 return {
 begin:(o)=>{enabled=false;__townTest.reset('settlement',o.seed);__townTest.step(360);paused=true;stack=[];flows={};birthIDs=new Set();created={};admissions=[];events=[];issues=[];counts={births:0,immigration:0,deaths:0,emigration:0,invalidHomeDays:0,unregisteredHouseholdDays:0,overCapacityBuildingDays:0};start=G.day;opening=G.treasury;cash=totalMoney();enabled=true;return snapshot();},
 advance:o=>{for(let i=0;i<o.days;i++){
  if(pendingEvent)throw Error('Unexpected pending dialog');if(o.strategy==='service-oriented'&&(G.day-start)%30===0){const p=G.stats.population,w=Math.max(24,G.policy.minWage),ceil=x=>Math.ceil(x/10)*10;Object.assign(G.policy,{educationBudget:Math.min(500,Math.max(90,ceil(p*10/260*w/.65))),healthBudget:Math.min(500,Math.max(70,ceil(p*5/350*w/.65))),defenseBudget:Math.min(800,Math.max(140,ceil(p*.65))),policeBudget:Math.min(800,Math.max(180,ceil(p*.7))),roadBudget:Math.min(250,Math.max(25,ceil(charterRoadCount()*.045/.23)))});}
  tick();
 }return snapshot();},finish:()=>({events,admissions,issues,counts})
 };
})();
'''

def write(path,value):
 temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',default='reports/migration-flow-audit');p.add_argument('--seeds',default='42,101,909');p.add_argument('--years',type=int,default=10);p.add_argument('--passive-years',type=int,default=30);p.add_argument('--strategy',choices=['both','passive','service-oriented'],default='both');args=p.parse_args();out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True);source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest();rows=[];report={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':sha,'method':'Normal settlement, one-year warmup, no grants/forced workforce/edited production rules. Source hooks record demographic creation before annual ageing. A nested exclusive-flow ledger reconciles treasury cash, avoiding double-counting returned payroll tax. Service-oriented arm changes only legal school/health/police/fire/road authorizations monthly, based on existing operating standards and actual population/roads. Seed42 passive is extended to30years specifically to explain earlier passive millions; other comparisons are10years.','rows':rows}
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage']);page=browser.new_page();page.set_default_timeout(120000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);page.add_script_tag(content=source.decode().replace('// SOURCE: 99-instrumentation.js',PROBE+'\n// SOURCE: 99-instrumentation.js'));page.locator('#newTown').click();page.locator('#pause').click()
  for seed in map(int,args.seeds.split(',')):
   for strategy in (['passive','service-oriented'] if args.strategy=='both' else [args.strategy]):
    years=args.passive_years if seed==42 and strategy=='passive' else args.years;row={'seed':seed,'strategy':strategy,'years':years,'samples':[],'status':'running'};rows.append(row)
    try:
     row['initial']=page.evaluate('o=>__migrationLedger.begin(o)',{'seed':seed})
     for year in range(1,years+1):
      a=page.evaluate('o=>__migrationLedger.advance(o)',{'days':360,'strategy':strategy});row['samples'].append(a)
      if not a['valid']['ok'] or abs(a['cashDrift'])>.1 or a['goodsError']>.01 or abs(a['treasuryReconciliation'])>.01:raise RuntimeError('Financial invariant failed')
      write(out/'flows.json',{**report,'pageErrors':errors})
      if year in [1,10,20,30]:print(seed,strategy,year,'treasury',round(a['treasury']),'reserve',round(a['publicReserve']),'population',a['population'],'counts',a['counts'],flush=True)
     row['status']='complete'
    except Exception as error:row['status']='failed';row['failure']=str(error);print('RETAINED',seed,strategy,str(error),flush=True)
    row['details']=page.evaluate('__migrationLedger.finish()');write(out/'flows.json',{**report,'pageErrors':errors})
  browser.close()
 assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
 print('Finished source-bound flow audit',flush=True)
if __name__=='__main__':main()
