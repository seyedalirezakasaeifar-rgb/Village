"""Matched-seed passive/expansion/austerity/closed-import comparisons."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=(ROOT/'assets/game.js').read_text());p.locator('#newTown').click();p.locator('#pause').click()
 for seed in [42,101,909]:
  for policy in ['passive','services','austerity','closed_trade']:
   result=p.evaluate('''o=>{__townTest.reset('regional',o.seed);const start=__townTest.get().total;
    const settings=o.policy==='services'?{educationBudget:1500,healthBudget:1500,aidBudget:1000}:o.policy==='austerity'?{educationBudget:0,healthBudget:0,aidBudget:0,policeBudget:0,roadBudget:0}:o.policy==='closed_trade'?{imports:false,importTariff:40}:{};
    for(const [k,v] of Object.entries(settings))__townTest.set(k,v);
    const samples=[];for(let i=0;i<4;i++){__townTest.step(90);const g=JSON.parse(__townTest.save());samples.push({day:g.day,employment:g.stats.employment,hardship:g.stats.hardship,treasury:g.treasury,safety:g.stats.safety,health:g.health,education:g.education,businesses:g.stats.businesses});}
    return {...o,samples,drift:__townTest.get().total-start,valid:__townTest.validate()};}''',{'seed':seed,'policy':policy});assert result['valid']['ok'] and abs(result['drift'])<.1;rows.append(result)
 b.close()
out=ROOT/'reports'/json.loads((ROOT/'release.json').read_text())['version'];out.mkdir(parents=True,exist_ok=True);(out/'regional-tradeoffs.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ['seed','policy']}|r['samples'][-1] for r in rows],indent=2))
