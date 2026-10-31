from playwright.sync_api import sync_playwright
from pathlib import Path
import json
root=Path(__file__).resolve().parent.parent
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage']);page=b.new_page()
 page.set_content((root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','').replace('<script src="game.js"></script>',''))
 page.add_script_tag(content=(root/'assets/game.js').read_text());page.evaluate('()=>__townTest.reset("frontier")');base=page.evaluate('__townTest.save()')
 cases=[('baseline',{}),('zero taxation',{'incomeTax':0,'profitTax':0,'foodTax':0,'propertyTax':0}),('high taxes',{'incomeTax':38,'profitTax':42,'foodTax':26,'propertyTax':4.5}),('wage mandate',{'minWage':80}),('defunded police',{'policeBudget':0,'outreachBudget':0}),('well funded public services',{'policeBudget':600,'aidBudget':500,'educationBudget':400,'healthBudget':400})]
 results=[]
 for name,changes in cases:
  res=page.evaluate('''({base,changes})=>{__townTest.load(base);let seed=312123;Math.random=()=>{seed=(Math.imul(1664525,seed)+1013904223)>>>0;return seed/4294967296};for(const [k,v] of Object.entries(changes))__townTest.set(k,v);__townTest.step(240);const r=__townTest.get();return {name:changes,treasury:Math.round(r.treasury),employment:r.employment,hardship:r.hardship,crime:r.cases,safety:r.stats.safety,businesses:r.businesses,approval:Math.round(r.approval),health:r.stats.health,education:r.stats.education,wellbeing:r.stats.wellbeing,total:r.total}}''',{'base':base,'changes':changes})
  results.append((name,res));print(name, {k:v for k,v in res.items() if k not in ('name','total')},flush=True)
 assert len(set(x[1]['treasury'] for x in results))>=4
 print('PASS: Policy experiments produce distinct fiscal outcomes.');b.close()
