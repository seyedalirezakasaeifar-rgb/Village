from pathlib import Path
from playwright.sync_api import sync_playwright
from time import perf_counter
root=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1100,'height':680})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((root/'assets/index.html').read_text())
 page.add_script_tag(content=(root/'assets/game.js').read_text())
 page.locator('#newTown').click()
 for scenario in ['settlement','hardtimes','frontier','industrial']:
  elapsed=perf_counter()
  stats=page.evaluate('''sc=>{
   __townTest.reset(sc);const baseline=__townTest.get().total;
   __townTest.step(3600);const g=JSON.parse(__townTest.save());
   let memberships=new Set(),duplicates=0,orphan=0;
   for(const h of g.households)for(const id of h.people){if(memberships.has(id))duplicates++;memberships.add(id);if(g.people[id].hh!==h.id||g.people[id].deceased||g.people[id].movedAway)orphan++;}
   const outstanding=g.loans.filter(l=>l.status==='active').reduce((n,l)=>n+l.balance,0);
   const moneyDiff=__townTest.get().total-baseline;
   if(duplicates||orphan||Math.abs(moneyDiff)>.05)throw Error('Invalid long-run accounting: '+JSON.stringify({duplicates,orphan,moneyDiff}));
   if(g.firms.some(f=>!Number.isFinite(f.cash)||f.cash<-.001)||g.banks.some(b=>!Number.isFinite(b.cash)||b.cash<-.001))throw Error('Nonfinite negative firms or bank balances');
   return {population:g.stats.population,households:g.households.length,openFirms:g.firms.filter(f=>!f.closed).length,bankFailures:g.finance.failures,activeBanks:g.banks.filter(b=>!b.closed).length,loans:g.loans.length,outstanding,insolvencies:g.finance.insolvencies,emigrants:g.people.filter(p=>p.movedAway).length,downzonings:g.finance.downzonings,moneyDiff};
  }''',scenario)
  print(scenario,'10 simulated years:',stats,'time',round(perf_counter()-elapsed,2),'s',flush=True)
 assert not errors,errors
 # Financial competition should resume after a bank liquidation; this tests
 # subsequent regional investors, not a guaranteed subsidy from the council.
 replacement=page.evaluate('''()=>{
  __townTest.reset('settlement');const before=__townTest.get().total;
  __townTest.bankFailure(0);
  __townTest.step(360);
  const f=__townTest.finance(),balance=__townTest.get().total;
  if(f.banks.length<4||f.banks[3].closed)throw Error('Market entry did not restore competition');
  if(Math.abs(before-balance)>.05)throw Error('New bank capitalization leaked money');
  return {banks:f.banks.map(b=>[b.name,b.closed]),difference:balance-before};
 }''')
 print('New bank market entry:',replacement)
 browser.close()
print('PASS 10-year endurance and competitive entry')
