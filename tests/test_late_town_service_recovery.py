"""Matched ordinary-budget reallocation from the late-town service bottleneck."""
from pathlib import Path
import hashlib, json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html

evidence = json.loads((ROOT/'docs/evidence/food-shortage-recovery8/late-town-service-diagnosis.json').read_text())
archive = evidence['result']['archive']
source = (ROOT/'assets/game.js').read_text()

probe = r'''window.__serviceArms=(saved)=>{
 const metrics=()=>({day:G.day,population:G.stats.population,treasury:G.treasury,region:G.region,debt:G.debt,policy:{health:G.policy.healthBudget,school:G.policy.educationBudget,police:G.policy.policeBudget,fire:G.policy.defenseBudget,aid:G.policy.aidBudget,outreach:G.policy.outreachBudget,road:G.policy.roadBudget,militia:G.policy.militiaBudget,transit:G.policy.transitBudget},service:Object.fromEntries(['health','school'].map(k=>[k,{...(G.serviceProvision?.[k]||{}),actualFunding:G.actualServiceFunding?.[k]??null}])),access:Object.fromEntries(['health','school'].map(k=>{const a=serviceAccess(k);return[k,{coverage:a.coverage,served:a.served,population:a.population}]})),health:G.health,education:G.education,hardship:G.stats.hardship,employment:G.stats.employment,aidToday:G.households.reduce((n,h)=>n+(h.aid||0),0),valid:validateTown().ok});
 const run=(label,action)=>{if(!__townTest.load(saved))throw Error('Late-town terminal archive rejected');const cash=totalMoney(),goods=goodsBalance();let serviceCalls=[];const originalFund=fundCivicServices;fundCivicServices=function(){const before=G.treasury;originalFund();serviceCalls.push({day:G.day,treasuryBefore:before,treasuryAfter:G.treasury,healthPaid:G.serviceProvision?.health?.paid||0,schoolPaid:G.serviceProvision?.school?.paid||0,healthCoverage:G.serviceProvision?.health?.coverage||0,schoolCoverage:G.serviceProvision?.school?.coverage||0});};let change=null;if(action){const old={healthBudget:G.policy.healthBudget,educationBudget:G.policy.educationBudget,policeBudget:G.policy.policeBudget,defenseBudget:G.policy.defenseBudget};draftPolicy={healthBudget:old.healthBudget+50,educationBudget:old.educationBudget+50,policeBudget:old.policeBudget-50,defenseBudget:old.defenseBudget-50};enactPolicyPackage();change={from:old,to:{healthBudget:G.policy.healthBudget,educationBudget:G.policy.educationBudget,policeBudget:G.policy.policeBudget,defenseBudget:G.policy.defenseBudget},budgetTotalBefore:old.healthBudget+old.educationBudget+old.policeBudget+old.defenseBudget,budgetTotalAfter:G.policy.healthBudget+G.policy.educationBudget+G.policy.policeBudget+G.policy.defenseBudget};}
 const points=[{label:'day0',...metrics()}];for(let d=1;d<=60;d++){__townTest.step(1);if(d===1||d===30||d===60)points.push({label:'day'+d,...metrics()});}
 fundCivicServices=originalFund;const finalMoney=totalMoney(),finalGoods=goodsBalance(),cashDrift=finalMoney-cash,goodsError=Math.max(0,...finalGoods.map(x=>Math.abs(x.error||0)));if(points.some(p=>!p.valid)||Math.abs(cashDrift)>.1||goodsError>.01)throw Error('service intervention conservation/validation failed '+label+' '+cashDrift+' '+goodsError);
 return{label,action:change,points,serviceCalls:serviceCalls.map(x=>x),servicePaidDays:{health:serviceCalls.filter(x=>x.healthPaid>0).length,school:serviceCalls.filter(x=>x.schoolPaid>0).length},maxDailyPaid:{health:Math.max(0,...serviceCalls.map(x=>x.healthPaid)),school:Math.max(0,...serviceCalls.map(x=>x.schoolPaid))},cashDrift,goodsError,valid:validateTown()};};
 if(!__townTest.load(saved))throw Error('Late-town archive rejected for baseline');const start=metrics();return{start,control:run('control',false),intervention:run('priority-to-care-budget-reallocation',true)};
};'''

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page()
    page.set_default_timeout(300000)
    errors=[]
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.set_content(html)
    page.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'))
    page.locator('#newTown').click()
    page.locator('#pause').click()
    result=page.evaluate('x=>__serviceArms(x)',archive)
    browser.close()

assert not errors, errors
assert result['control']['valid']['ok'] and result['intervention']['valid']['ok']
out={
    'source_commit':__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'terminal_archive_sha256':hashlib.sha256(archive.encode()).hexdigest(),
    'baseline_day':result['start']['day'],
    'method':'Matched 60-day continuation from the exact 25-year terminal state; control vs logged native council-policy enactment. Reallocation moves $50/day each from police and fire budgets into public health and school budgets, holding the four-budget sum constant. No cash/goods/people injected.',
    'result':result,
}
dest=ROOT/'docs/evidence/food-shortage-recovery8/late-town-service-recovery.json'
dest.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='serviceCalls'},indent=2))
