"""Real estate-release regression, funded/access/affordability and financial exits."""
from pathlib import Path
import hashlib,json,sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
PROBE=(ROOT/'tests/fixtures/migration-causality-probe.js').read_text()
from test_mobile_rendering import html
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest();out=ROOT/'reports/migration-causality';out.mkdir(parents=True,exist_ok=True)
extra=r'''
window.__migrationExtra={
 quoteReplay:seedValue=>{__townTest.reset('settlement',seedValue);__townTest.step(360);G.policy.educationBudget=10000;G.policy.healthBudget=10000;__townTest.step(1);const h=G.households.find(h=>h.people.length===2&&h.people.every(id=>G.people[id].age<70)),home=readBuild(h.home);h.netIncomeTrend=35;for(const f of G.firms)f.jobs=f.workers.length;const f=G.firms.find(f=>f.kind==='grocer');f.jobs+=100;f.wage=40;invalidateUrban();const profiles=[{age:30,skill:.4,health:90}],before=migrationAssessment(home,profiles,0,h),saved=archivePayload();if(!hydrateSave(saved))throw Error('save rejected');const after=migrationAssessment(readBuild(home.id),profiles,0,G.households[h.id]);return{before,after,cashDrift:totalMoney()-JSON.parse(saved).accounts.baseline};},
 deathEstate:seedValue=>{__townTest.reset('settlement',seedValue);const h=G.households[0],home=readBuild(h.home),ids=h.people.slice();for(const id of ids)G.people[id].age=96;for(const f of G.firms){G.region+=f.cash;f.cash=0;}G.day=360;G.year=2;G.month=1;const total=totalMoney(),wallet=h.cash,deposits=JSON.stringify(h.deposits),owner=home.owner;yearlyDemographics();migrationTenancyDay();return{home:h.home,people:h.people,identitiesRetained:ids.every(id=>G.people[id]?.deceased),walletSame:h.cash===wallet,depositsSame:JSON.stringify(h.deposits)===deposits,ownerSame:home.owner===owner,cashDrift:totalMoney()-total};},
 privateSchool:seedValue=>{__townTest.reset('settlement',seedValue);const b=G.buildings.find(b=>b.kind==='school'),f=createFirm('school',b.x,b.y,true,()=>b);G.region-=f.cash;f.privateService='school';f.serviceFee=2;f.jobs=1;f.wage=36;f.serviceCapacity=16;f.clientsToday=0;const person=G.people.find(p=>privateQualified(p,f)&&privateServiceDistance(f,G.households[p.hh])<=40);if(G.firms[person.job])G.firms[person.job].workers=G.firms[person.job].workers.filter(id=>id!==person.id);person.job=f.id;person.publicWork=false;f.workers=[person.id];const home=readBuild(G.households[person.hh].home),total=totalMoney(),paid=migrationSchoolOffer(home,2,0,100,2500,2,30);f.clientsToday=16;const full=migrationSchoolOffer(home,2,0,100,2500,2,30);f.clientsToday=0;const unaffordable=migrationSchoolOffer(home,2,0,31,2500,2,30);return{paid,full,unaffordable,cashDrift:totalMoney()-total};},
 outside:seedValue=>{__townTest.reset('settlement',seedValue);G.day=30;G.month=2;const h=G.households.find(h=>h.people.length===2&&h.people.every(id=>G.people[id].age>=18&&G.people[id].age<=70)),home=readBuild(h.home);h.netIncomeTrend=35;for(const f of G.firms)f.jobs=f.workers.length;const f=G.firms.find(f=>!f.closed);f.jobs+=100;f.wage=35;const profile=[{age:30,skill:.4,health:90}],normal=migrationAssessment(home,profile,0,h),prices=OUTSIDE_MARKETS.map(m=>m.imports.food),moneyBefore=totalMoney();for(const m of OUTSIDE_MARKETS)m.imports.food=(m.imports.food||1)*.7;const cheaper=migrationAssessment(home,profile,0,h);for(let i=0;i<OUTSIDE_MARKETS.length;i++)OUTSIDE_MARKETS[i].imports.food=prices[i];return{normal,cheaper,cashDrift:totalMoney()-moneyBefore};},
 spendable:seedValue=>{__townTest.reset('settlement',seedValue);const h=G.households.slice().sort((a,b)=>b.cash-a.cash)[0],bank=G.banks[0];depositTransfer(h,bank,Math.min(1500,h.cash));G.region+=h.cash;h.cash=0;
  const transferred=bank.cash;bank.cash=0;bank.regionCredit=(bank.regionCredit||0)+transferred;G.region+=transferred;const retained=Math.min(200,G.region),outside=G.region-retained;G.region=retained;propertyInvestor().cash+=outside;
  const total=totalMoney(),estimated=migrationSpendable(h),before=h.cash;for(const [id,amount]of Object.entries(h.deposits))withdrawal(h,G.banks[+id],amount);
  return {estimated,actualSpendable:h.cash,before,cashDrift:totalMoney()-total};},
 legacy:payload=>{if(!hydrateSave(payload))throw Error('Supported legacy archive rejected');const before={people:G.people.length,households:G.households.length,total:totalMoney(),balances:G.households.map(h=>({id:h.id,cash:h.cash,deposits:{...h.deposits},people:h.people.slice(),home:h.home})),titles:G.buildings.map(b=>({id:b.id,owner:b.owner,title:b.title}))},over=migrationDiagnostics().overcrowdedHomes;
  for(const x of over)if(addHouseholdAt(readBuild(x.building),2500))throw Error('Extra family admitted into inherited overcapacity');
  const after={people:G.people.length,households:G.households.length,total:totalMoney(),balances:G.households.map(h=>({id:h.id,cash:h.cash,deposits:{...h.deposits},people:h.people.slice(),home:h.home})),titles:G.buildings.map(b=>({id:b.id,owner:b.owner,title:b.title}))};
  return {before,after,over,roundTrip:hydrateSave(archivePayload())};},
 legacyContinuation:()=>{const before=G.people.length,households=G.households.length,groups=migrationDiagnostics().overcrowdedHomes.map(x=>({building:x.building,ids:x.households.slice()})),total=totalMoney();__townTest.step(120);const after=groups.map(x=>({building:x.building,oldIds:x.ids,status:migrationHousingStatus(readBuild(x.building))}));return{before,afterPeople:G.people.length,households,afterHouseholds:G.households.length,after,totalDrift:totalMoney()-total,valid:validateTown(),roundTrip:hydrateSave(archivePayload())};},
 roster:seedValue=>{__townTest.reset('settlement',seedValue);const h=G.households[0],b=readBuild(h.home),other=G.households[1],old=readBuild(other.home);if(old.hh===other.id)old.hh=-1;other.home=b.id;b.legacySharedTenants=[h.id,other.id];const before=migrationHousingStatus(b),accounts=totalMoney(),ids=other.people.slice();for(const id of ids){G.people[id].movedAway=true;G.people[id].job=-1;for(const f of G.firms)f.workers=f.workers.filter(x=>x!==id);}other.people=[];migrationReleaseTenancy(other);const after=migrationHousingStatus(b);return{before,after,marker:b.legacySharedTenants??null,cashDrift:totalMoney()-accounts};},
 home:seedValue=>{__townTest.reset('settlement',seedValue);G.day=30;G.month=2;G.autoBuild=false;for(const f of G.firms)f.jobs=f.workers.length;const lot=buildableCandidates('housing').find(p=>canPlace(p.x,p.y,true,'home'));if(!lot)throw Error('No real connected home lot');const count=G.people.length,moneyBefore=totalMoney(),oldId=G.nextId;construct('home',lot.x,lot.y);const b=G.buildings.find(b=>b.id>=oldId&&b.kind==='home');return{peopleCreated:G.people.length-count,home:b,housing:b&&migrationHousingStatus(b),cashDrift:totalMoney()-moneyBefore,valid:validateTown(),roundTrip:hydrateSave(archivePayload())};}
};
'''
rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page();p.set_default_timeout(120000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',PROBE+'\n'+extra+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
 for seed in [42,101,909]:
  r=p.evaluate('seed=>__migrationAudit.duplicate(seed)',seed);assert r['afterMonth']['originalEstateHome']==-1 and len(r['afterYear']['residents'])<=1 and r['afterYear']['valid']['ok']and r['loadAccepted'],r;rows.append({'duplicate':r})
  r=p.evaluate('seed=>__migrationAudit.wealthPlacement(seed)',seed);assert r[0]['before']['liquidity']==r[1]['before']['liquidity']and r[0]['departed']==r[1]['departed'],r;assert all(abs(x['cashDrift'])<.001 for x in r);rows.append({'wealthPlacement':r})
  variants={v:p.evaluate('o=>__migrationAudit.arrivalGate(o.seed,o.variant)',{'seed':seed,'variant':v})for v in ['normal','no-vacancies','unfunded-vacancies','no-services','high-rent','low-wages','disconnected']}
  assert variants['normal']['assessment']['eligible'],variants
  assert variants['normal']['assessment']['budget']['commuting']>0 and abs(sum(variants['normal']['assessment']['budget'].values())-variants['normal']['assessment']['essentials'])<.001,variants['normal']
  for v in ['no-vacancies','unfunded-vacancies','low-wages','disconnected']:assert not variants[v]['assessment']['eligible']and not variants[v]['admitted'],(v,variants[v])
  assert variants['no-services']['assessment']['pullProbability']<variants['normal']['assessment']['pullProbability']
  assert variants['high-rent']['assessment']['essentials']>variants['normal']['assessment']['essentials']
  assert all(abs(v['cashDrift'])<.001 for v in variants.values());rows.append({'seed':seed,'causalVariants':variants})
  for name in ['quoteReplay','deathEstate','privateSchool','outside','spendable','roster','home']:
   r=p.evaluate('o=>__migrationExtra[o.name](o.seed)',{'name':name,'seed':seed})
   if name=='quoteReplay':assert r['before']==r['after'],r
   if name=='deathEstate':assert r['home']==-1 and not r['people']and r['identitiesRetained']and r['walletSame']and r['depositsSame']and r['ownerSame'],r
   if name=='privateSchool':assert r['paid']and r['paid']['dailyCost']>0 and r['paid']['served']==2 and r['full']is None and r['unaffordable']is None,r
   if name=='outside':assert r['cheaper']['outside']['essentials']<r['normal']['outside']['essentials']and r['cheaper']['pullProbability']<r['normal']['pullProbability'],r
   if name=='spendable':assert abs(r['estimated']['spendable']-r['actualSpendable'])<.001 and r['estimated']['locked']>0,r
   if name=='roster':assert r['before']['overcrowded']and not r['after']['overcrowded']and r['marker']is None,r
   if name=='home':assert r['peopleCreated']==0 and r['home']['owner']==-1 and r['home']['title']['kind']=='municipal'and r['roundTrip']and r['valid']['ok'],r
   assert abs(r['cashDrift'])<.001,r;rows.append({name:r})
 legacy=json.loads((ROOT/'tests/fixtures/v60-distressed-town.json').read_text());r=p.evaluate('g=>__migrationExtra.legacy(g)',legacy);assert r['before']==r['after']and len(r['over'])==6 and r['roundTrip'],r;rows.append({'legacy':r})
 continued=p.evaluate('__migrationExtra.legacyContinuation()');assert continued['afterPeople']>=continued['before']and continued['afterHouseholds']>=continued['households']and continued['valid']['ok']and continued['roundTrip']and abs(continued['totalDrift'])<.01,continued
 for group in continued['after']:
  if group['status']['overcrowded']:assert set(group['status']['households'])<=set(group['oldIds']),group
 rows.append({'legacyContinuation':continued})
 p.locator('[data-panel=community]').click();assert p.locator('#migrationOffice').count()==1;p.locator('#migrationOffice').evaluate('e=>e.open=true');assert 'Inherited shared housing' in p.locator('#migrationOffice').inner_text();p.screenshot(path=str(out/'inherited-housing-review.png'));assert not errors,errors;b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
(out/'regressions.json').write_text(json.dumps({'source_sha256':sha,'rows':rows,'browserErrors':errors,'passed':True},indent=2)+'\n');print('PASS estate release/no duplicate refill, funded reachable affordable employment, service/outside signals, wallet/deposit equivalence, constrained withdrawal, legacy assets/rosters and municipal home capacity')
