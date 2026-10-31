from pathlib import Path
from playwright.sync_api import sync_playwright
import json
R=Path(__file__).resolve().parents[1];rows=[]
source_digest=__import__('hashlib').sha256((R/'assets/game.js').read_bytes()).hexdigest()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox']);p=b.new_page();p.goto((R/'assets/index.html').as_uri());p.locator('#newTown').click();p.locator('#pause').click()
 for seed in [1,42,101,909,2026,4567,99999,314159]:
  r=p.evaluate('''seed=>{__townTest.reset('settlement',seed);const init=__townTest.get(),samples=[];for(let i=0;i<24;i++){__townTest.step(30);const s=__townTest.get(),g=JSON.parse(__townTest.save());samples.push({day:s.day,employment:s.employment,firms:s.businesses,hardship:s.hardship,restart:g.market.privateRestartCapital});}const v=__townTest.validate();if(!v.ok)throw Error(v.issues.join(';'));return{seed,initialEmployment:init.employment,samples,drift:v.total-init.total,valid:v.ok};}''',seed);assert r['valid'] and abs(r['drift'])<.05;assert min(x['employment'] for x in r['samples'])>=65;assert all(x['restart']==0 for x in r['samples']);rows.append(r);print(seed,[x['employment'] for x in r['samples']],r['drift'],flush=True)
 assert __import__('hashlib').sha256((R/'assets/game.js').read_bytes()).hexdigest()==source_digest
 (R/'reports/v7.0/default-starts.json').write_text(json.dumps({'source_sha256':source_digest,'rows':rows},indent=2));b.close()
