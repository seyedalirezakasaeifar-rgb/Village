"""Matched saved-state credit, wage and inventory-trade development histories."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest();out=ROOT/'reports/development-credit-markets';out.mkdir(parents=True,exist_ok=True);rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_default_timeout(120000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.decode());p.locator('#newTown').click();p.locator('#pause').click()
 for scenario in ['settlement','hardtimes','regional']:
  for seed in [42,909]:
   p.evaluate('o=>{__townTest.reset(o.scenario,o.seed);__townTest.step(60);}',{'scenario':scenario,'seed':seed});saved=p.evaluate('__townTest.save()')
   for mode in ['baseline','rate-tightening','high-wage','inventory-freeze','freeze-recover']:
    r=p.evaluate('''o=>{if(!__townTest.load(o.saved))throw Error('Matched source save rejected');const start=__townTest.get().total,original={...__townTest.get().policy};let approved=0;const g=JSON.parse(__townTest.save());for(const f of g.firms.filter(f=>!f.closed).slice(0,3))if(__townTest.takeLoan('firm',f.id,2000,720))approved++;
     const changes=o.mode==='rate-tightening'?{policyRate:15}:o.mode==='high-wage'?{minWage:65}:o.mode.includes('freeze')?{imports:false}:{};for(const [k,v]of Object.entries(changes))__townTest.set(k,v);const points=[];
     for(let month=0;month<24;month++){if(o.mode==='freeze-recover'&&month===6)__townTest.set('imports',original.imports);__townTest.step(30);const a=JSON.parse(__townTest.save());for(const f of a.firms.filter(f=>!f.closed&&f.operating?.netProfit!=null)){const x=f.operating;if(Math.abs(x.sales+(x.otherIncome||0)-x.costOfGoods-x.payroll-x.otherCosts-x.profitTax-x.netProfit)>.001)throw Error('Statement does not reconcile');}
      if(!__townTest.validate().ok)throw Error('Invalid town');if(__townTest.goods().some(x=>Math.abs(x.error||0)>.01))throw Error('Goods imbalance');
      points.push({day:a.day,population:a.stats.population,employment:a.stats.employment,hardship:a.stats.hardship,treasury:a.treasury,health:a.health,education:a.education,businesses:a.stats.businesses,unmetFood:a.market.unmetFood,foodDisconnected:a.market.foodDisconnected,blockedCommutes:a.market.blockedCommutes,cpi:a.market.cpi,loanBalances:a.loans.filter(l=>l.status==='active').reduce((n,l)=>n+l.balance,0),arrears:a.loans.filter(l=>l.status==='active'&&l.arrears>0).length,defaults:a.finance.businessDefaults+a.finance.householdDefaults,profit:a.firms.filter(f=>!f.closed).reduce((n,f)=>n+f.netProfit,0),wages:a.households.reduce((n,h)=>n+h.wages,0),capital:a.firms.reduce((n,f)=>n+(f.capex||0),0),equipmentOrders:a.firms.filter(f=>f.pendingEquipment).length});
     }return {scenario:o.scenario,seed:o.seed,mode:o.mode,approved,points,drift:__townTest.get().total-start};}''',{'scenario':scenario,'seed':seed,'mode':mode,'saved':saved});assert abs(r['drift'])<.1,r;rows.append(r)
    assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
    (out/'soak.json').write_text(json.dumps({'source_sha256':sha,'rows':rows,'errors':errors},indent=2)+'\n');last=r['points'][-1];print(scenario,seed,mode,'emp',last['employment'],'firms',last['businesses'],'cash',round(last['treasury']),'defaults',last['defaults'],'drift',round(r['drift'],7),flush=True)
 assert not errors,errors;b.close()
print('PASS 30 matched two-year histories, operating statements, state/goods validation and currency conservation')
