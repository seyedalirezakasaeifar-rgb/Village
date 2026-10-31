from pathlib import Path
from playwright.sync_api import sync_playwright
import os,json,hashlib
R=Path(__file__).resolve().parents[1];out={'source_sha256':hashlib.sha256((R/'assets/game.js').read_bytes()).hexdigest(),'cases':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox']);p=b.new_page();p.goto((R/'assets/index.html').as_uri());p.locator('#newTown').click();p.locator('#pause').click()
 for name in ['corporate-liquidity-trap.json','v60-distressed-town.json']:
  raw=(R/'tests/fixtures'/name).read_text();assert p.evaluate('s=>__townTest.load(s)',raw);before=p.evaluate('__townTest.get()');checkpoints=[]
  for y in range(5):
   p.evaluate('__townTest.step(360)');g=p.evaluate('__townTest.get()');v=p.evaluate('__townTest.validate()');assert v['ok'],v;assert abs(g['total']-before['total'])<.1;sample={k:g[k] for k in ['population','employment','businesses','regional','treasury']};sample['activeBanks']=p.evaluate('__townTest.finance().banks.filter(b=>!b.closed).length');checkpoints.append(sample)
  assert checkpoints[-1]['activeBanks']>=1;assert checkpoints[-1]['businesses']>before['businesses'],(name,before,checkpoints)
  out['cases'].append({'fixture':name,'before':{k:before[k] for k in ['population','employment','businesses','regional']},'years':checkpoints,'cashDrift':g['total']-before['total']});print(name,checkpoints,flush=True)
 b.close()
(R/'reports/v7.0/liquidity-recovery.json').write_text(json.dumps(out,indent=2))
