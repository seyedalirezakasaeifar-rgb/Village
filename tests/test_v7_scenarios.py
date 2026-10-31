from pathlib import Path
from playwright.sync_api import sync_playwright
import json
R=Path(__file__).resolve().parents[1];rows=[]
source_digest=__import__('hashlib').sha256((R/'assets/game.js').read_bytes()).hexdigest()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox']);p=b.new_page();p.goto((R/'assets/index.html').as_uri());p.locator('#newTown').click();p.locator('#pause').click()
 for sc in ['settlement','frontier','hardtimes','industrial','regional']:
  for seed in [42,101,909]:
   row=p.evaluate('''o=>{__townTest.reset(o.sc,o.seed);const before=__townTest.get(),samples=[];for(let i=0;i<12;i++){__townTest.step(90);const s=__townTest.get();samples.push({day:s.day,employment:s.employment,population:s.population,firms:s.businesses,hardship:s.hardship});}return {...o,initial:before.employment,samples,valid:__townTest.validate(),drift:__townTest.get().total-before.total}}''',{'sc':sc,'seed':seed});assert row['valid']['ok'] and abs(row['drift'])<.1;assert row['samples'][-1]['employment']>=65;rows.append(row);print(sc,seed,row['initial'],[x['employment'] for x in row['samples']],row['valid']['ok'],flush=True)
 assert __import__('hashlib').sha256((R/'assets/game.js').read_bytes()).hexdigest()==source_digest
 (R/'reports/v7.0/scenario-trajectories.json').write_text(json.dumps({'source_sha256':source_digest,'rows':rows},indent=2));b.close()
