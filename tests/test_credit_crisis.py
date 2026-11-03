"""Inherited concentrated credit loss: actual loan funding, liquidation and recovery."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
script=source.decode().replace('// SOURCE: 99-instrumentation.js','''
window.__crisisShock=()=>{const before=totalMoney(),funded=[];for(const [i,b] of G.banks.entries()){
 const f=G.firms.filter(f=>!f.closed)[i],amount=b.cash*.94;b.cash-=amount;f.cash+=amount;f.debt+=amount;
 G.loans.push({id:++G.nextLoanId,bankId:b.id,ownerType:'firm',ownerId:f.id,original:amount,balance:amount,rate:.12,fixedRate:true,term:720,created:G.day,arrears:0,status:'active',paid:0});
 // An authored inherited-risk stress, deliberately outside current underwriting:
 // paid-for equipment loses its resale value; its regional seller kept the cash.
 G.region+=f.cash;f.cash=0;liquidateFirm(f,'Stress fixture: unrecoverable inherited investment');funded.push(amount);
 }return {funded,drift:totalMoney()-before};};
// SOURCE: 99-instrumentation.js''')
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_default_timeout(120000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click()
 for seed in [42,909]:
  p.evaluate('seed=>{__townTest.reset("settlement",seed);__townTest.step(30);}',seed);saved=p.evaluate('__townTest.save()')
  for guarantee in [0,100]:
   p.evaluate('s=>__townTest.load(s)',saved);p.evaluate('v=>__townTest.set("depositGuarantee",v)',guarantee);total=p.evaluate('__townTest.get().total');shock=p.evaluate('__crisisShock()');assert abs(shock['drift'])<.001
   points=[]
   for month in range(24):
    p.evaluate('__townTest.step(30)');g=json.loads(p.evaluate('__townTest.save()'));assert p.evaluate('__townTest.validate().ok');points.append({'day':g['day'],'banks':sum(not x['closed'] for x in g['banks']),'employment':g['stats']['employment'],'failures':g['finance']['failures'],'defaults':g['finance']['businessDefaults'],'depositLosses':g['finance']['depositLosses'],'insurance':g['finance']['insuredPayouts'],'treasury':g['treasury']})
   drift=p.evaluate('__townTest.get().total')-total;assert abs(drift)<.1
   assert points[0]['defaults']>=3 and max(x['failures'] for x in points)>=1,points
   assert points[-1]['banks']>=2 and points[-1]['employment']>=60,points
   rows.append({'seed':seed,'guarantee':guarantee,'shock':shock,'points':points,'drift':drift});print(seed,guarantee,points[0],points[-1],flush=True)
 assert not errors,errors;assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha;b.close()
for seed in [42,909]:
 a,c=[r for r in rows if r['seed']==seed];assert c['points'][-1]['insurance']>0 and c['points'][-1]['depositLosses']<a['points'][-1]['depositLosses']
out=ROOT/'reports/development-player-loop';out.mkdir(parents=True,exist_ok=True);(out/'credit-crisis.json').write_text(json.dumps({'source_sha256':sha,'rows':rows,'errors':errors},indent=2)+'\n');print('PASS inherited credit loss, funded guarantees, depositor haircuts, banking re-entry and two-year recovery')
