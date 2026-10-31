from pathlib import Path
from playwright.sync_api import sync_playwright
import json
assets=Path(__file__).resolve().parents[1]/'assets'
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1200,'height':720})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((assets/'index.html').read_text())
 page.add_script_tag(content=(assets/'game.js').read_text())
 page.locator('#newTown').click()
 page.locator('[data-panel=banking]').click()
 assert page.locator('#panelTitle').inner_text()=='Banks & Credit'
 assert 'Vale Mutual Savings' in page.locator('#panelBody').inner_text()
 bank=page.evaluate('''()=>{
  const before=__townTest.get().total;
  const first=__townTest.finance();if(first.banks.length!==3)throw Error('Missing banks');
  const loan=__townTest.takeLoan('firm',0,3600,260);if(!loan)throw Error('Healthy firm refused working capital');
  const after=__townTest.get().total;if(Math.abs(before-after)>.01)throw Error('New credit created cash '+(after-before));
  __townTest.step(150);const later=__townTest.finance().loans.find(l=>l.id===loan.id);
  if(!later||later.balance>=3600)throw Error('Loan did not amortize');
  if(Math.abs(before-__townTest.get().total)>.01)throw Error('Loan repayment leaked cash');
  return {issued:loan.original,remaining:later.balance,banks:first.banks.length};
 }''')
 print('LENDING AND AMORTIZATION',bank)
 saved=page.evaluate('__townTest.save()')
 page.evaluate('''raw=>{if(!__townTest.load(raw))throw Error('Finance save rejected');}''',saved)
 assert len(page.evaluate('__townTest.finance().banks'))==3
 # Test a receivership in which treasury-funded insurance compensates a fraction of deposit losses.
 liquid=page.evaluate('''()=>{
  __townTest.reset('settlement');
  const g=JSON.parse(__townTest.save());const b=g.banks[0];
  const deposit=g.households.reduce((n,h)=>n+(h.deposits[b.id]||0),0);
  const moved=b.cash-120;b.cash=120;g.region+=moved;g.policy.depositGuarantee=70;
  if(!__townTest.load(g))throw Error('Could not import stressed institution');
  const before=__townTest.get().total;
  __townTest.bankFailure(0);
  const f=__townTest.finance();const after=__townTest.get().total;
  if(!f.banks[0].closed||f.indicators.failures!==1)throw Error('Bank remained open');
  if(f.deposits[0]>.001)throw Error('Deposits remain on failed bank');
  if(f.indicators.depositLosses<=0||f.indicators.insuredPayouts<=0)throw Error('No loss allocation');
  if(Math.abs(after-before)>.01)throw Error('Liquidation accounting mismatch: '+(after-before));
  return {claims:deposit,insured:f.indicators.insuredPayouts,uninsuredLoss:f.indicators.depositLosses};
 }''')
 print('BANK FAILURE AND INSURANCE',liquid)
 # Deliberately oversupplied city; a vacated tower is legitimately downzoned.
 down=page.evaluate('''()=>{
  __townTest.reset('settlement');let g=JSON.parse(__townTest.save());let original=g.buildings.find(b=>b.kind==='home');
  const primary=g.households[original.hh];
  for(const h of g.households){if(h.id===primary.id)continue;for(const id of h.people){g.people[id].movedAway=true;g.people[id].job=-1;}h.people=[];}
  for(const f of g.firms){f.workers=f.workers.filter(id=>!g.people[id]?.movedAway)}
  original.kind='tower';original.units=[primary.id];original.lastRedeveloped=1;g.day=600;
  g.development.downzonings=0;
  if(!__townTest.load(g))throw Error('Vacancy state invalid');
  const before=__townTest.get().total;
  const converted=__townTest.reverseLand();
  if(!converted)throw Error('Vacant tower did not convert');
  const after=JSON.parse(__townTest.save());let b=after.buildings.find(v=>v.id===original.id);
  if(b.kind!=='home'||b.hh!==primary.id||after.households[primary.id].home!==b.id)throw Error('Resident displaced or property wrong');
  if(Math.abs(before-__townTest.get().total)>.01)throw Error('Downzoning created or destroyed money');
  return {building:b.id,newType:b.kind,resident:primary.id,conversions:after.finance.downzonings};
 }''')
 print('DEMAND-LED DOWNZONING',down)
 # Natural corporate insolvency must distribute recoverable value to banks before equity.
 insolv=page.evaluate('''()=>{
  __townTest.reset('settlement');const loan=__townTest.takeLoan('firm',0,4200,360);
  if(!loan)throw Error('Could not originate insolvency test loan');
  const g=JSON.parse(__townTest.save()),firm=g.firms[0];
  g.region+=firm.cash-45;firm.cash=45;firm.strain=65;firm.stock={grain:2};
  if(!__townTest.load(g))throw Error('Could not restore distressed firm');
  const before=__townTest.get().total;
  __townTest.step(1);
  const after=JSON.parse(__townTest.save()),f=after.firms[0],l=after.loans.find(l=>l.id===loan.id);
  if(!f.closed||f.cash!==0)throw Error('Distressed company did not liquidate');
  if(!['default','repaid'].includes(l.status))throw Error('Loan still active after liquidation');
  if(Math.abs(__townTest.get().total-before)>.01)throw Error('Corporate liquidation violated cash conservation');
  return {closed:f.closed,loanStatus:l.status,recovered:loan.original-l.balance};
 }''')
 print('NATURAL BUSINESS LIQUIDATION',insolv)
 assert not errors,errors
 browser.close()
print('PASS financial integrity, bank runs, reversible redevelopment, interface and save history')
