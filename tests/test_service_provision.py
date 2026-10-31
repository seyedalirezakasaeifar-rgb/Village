"""Matched-state service-purchase staircase and conserved public accounts."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,os
source=(ROOT/'assets/game.js').read_text()
source=source.replace('// SOURCE: 99-instrumentation.js', '''window.__serviceProbe=()=>{const before={health:G.health,education:G.education,total:totalMoney(),treasury:G.treasury};extendedCivicDay();return {before,health:G.health,education:G.education,total:totalMoney(),treasury:G.treasury,provision:G.serviceProvision,ratios:G.actualServiceFunding};};
// SOURCE: 99-instrumentation.js''')
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click()
 for service,policy,building in [('health','healthBudget','clinic'),('school','educationBudget','school')]:
  for facilities in [False,True]:
   for cash in [10,100000]:
    for amount in [0,1,25,100,250,1000,4000]:
     row=p.evaluate('''o=>{__townTest.reset('settlement',42);const g=JSON.parse(__townTest.save());g.region+=g.treasury-o.cash;g.treasury=o.cash;for(const k of ['healthBudget','educationBudget','roadBudget','militiaBudget','transitBudget'])g.policy[k]=0;g.policy[o.policy]=o.amount;if(!o.facilities)g.buildings=g.buildings.filter(b=>b.kind!==o.building);if(!__townTest.load(g))throw Error('probe state rejected');return {...o,...__serviceProbe()};}''',{'service':service,'policy':policy,'building':building,'facilities':facilities,'cash':cash,'amount':amount});assert abs(row['total']-row['before']['total'])<.0001;rows.append(row)
 # Unfunded promises must not grant fare relief or civic benefits.
 counterfactual=[]
 for promises in [False,True]:
  row=p.evaluate('''promises=>{__townTest.reset('settlement',42);const g=JSON.parse(__townTest.save());g.region+=g.treasury;g.treasury=0;for(const k of ['incomeTax','profitTax','propertyTax','foodTax','utilityTax','commercialRate','importTariff','permitFee','employmentSubsidy','policeBudget','defenseBudget','healthBudget','educationBudget','aidBudget','energyAidBudget','outreachBudget','roadBudget','militiaBudget','transitBudget','pensionDaily'])g.policy[k]=0;if(promises)for(const k of ['transitBudget','militiaBudget','outreachBudget'])g.policy[k]=1000;if(!__townTest.load(g))throw Error('load');__townTest.step(1);const after=JSON.parse(__townTest.save());return {travel:after.households.reduce((n,h)=>n+h.travel,0),safety:after.stats.safety,militia:after.stats.militia,treasury:after.treasury,valid:__townTest.validate()};}''',promises);counterfactual.append(row)
 assert counterfactual[0]['travel']==counterfactual[1]['travel'],counterfactual
 assert counterfactual[0]['safety']==counterfactual[1]['safety'],counterfactual
 assert counterfactual[0]['militia']==counterfactual[1]['militia'],counterfactual
 assert all(r['valid']['ok'] for r in counterfactual)
 b.close()
out=ROOT/'reports/service-cycle';out.mkdir(parents=True,exist_ok=True);(out/'staircase.json').write_text(json.dumps(rows,indent=2)+'\n')
if os.environ.get('TOWNLEDGER_SERVICE_BASELINE')!='1':
 for service in ['health','school']:
  metric='health' if service=='health' else 'education'
  full=[r for r in rows if r['service']==service and r['facilities'] and r['cash']==100000]
  assert full[1][metric]<full[3][metric]<full[-1][metric],(service,[(r['amount'],r[metric]) for r in full])
  assert full[-1][metric]==full[-2][metric], 'Coverage must saturate at capacity'
  for row in [r for r in rows if r['service']==service and not r['facilities']]:
   assert row['treasury']==row['before']['treasury'],'Do not buy service that has no facility capacity'
  for row in [r for r in rows if r['service']==service and r['cash']==10]:
   assert row['provision'][service]['paid']<=10
print(json.dumps([{k:r[k] for k in ['service','facilities','cash','amount','health','education','treasury']} for r in rows if r['cash']==100000 and r['facilities']],indent=2))
