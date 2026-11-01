"""Manual farm invitation leaves ordinary automatic economies exactly unchanged."""
import hashlib,json,subprocess
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
BASE='2e4ce5c8869a0483657ba3321d3e66e8954d780d'
current=(ROOT/'assets/game.js').read_text();reference=subprocess.check_output(['git','show',BASE+':assets/game.js'],cwd=ROOT,text=True);rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for source in [reference,current]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();pages.append(p)
 for scenario in ['settlement','regional','industrial','hardtimes']:
  for p in pages:p.evaluate('s=>__townTest.reset(s,42)',scenario)
  for days in [0,30,60,90,120,150,180]:
   states=[]
   for p in pages:
    if days:p.evaluate('__townTest.step(30)')
    states.append(json.loads(p.evaluate('__townTest.save()')))
   assert states[0]==states[1],(scenario,days)
   rows.append({'scenario':scenario,'elapsedDays':days,'completeArchiveIdentical':True})
 b.close()
print(json.dumps({'reference':BASE,'reference_source_sha256':hashlib.sha256(reference.encode()).hexdigest(),'source_sha256':hashlib.sha256(current.encode()).hexdigest(),'excludedFields':[],'checkpoints':rows},indent=2))
