"""Real daily purchases see a published census matching their live demand rows."""
import hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text();probe=r'''window.__purchasePopulationBoundary=scenario=>{__townTest.reset(scenario,42);const original=purchaseCivicService,rows=[];let calls=0;purchaseCivicService=function(kind,authorized){const actual=G.households.reduce((n,h)=>n+h.people.filter(id=>G.people[id]&&!G.people[id].deceased&&!G.people[id].movedAway).length,0);calls++;if(G.stats.population!==actual)rows.push({day:G.day,kind,published:G.stats.population,actual});return original(kind,authorized)};const money=totalMoney();try{__townTest.step(370);return {scenario,days:370,calls,allMismatches:rows,moneyError:totalMoney()-money,valid:validateTown().ok}}finally{purchaseCivicService=original}};''';rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
 for scenario in ['settlement','regional','industrial','hardtimes']:
  row=p.evaluate('s=>__purchasePopulationBoundary(s)',scenario);rows.append(row);assert row['calls']==740 and row['allMismatches']==[] and row['valid']and abs(row['moneyError'])<.001,row
 b.close()
print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':rows,'scope':'Normal authored-scenario daily purchase boundaries through annual demographics; no blanket statement about externally corrupted aggregates'},indent=2))
