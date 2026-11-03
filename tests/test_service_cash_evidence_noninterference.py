"""New historical cash observations must not change existing model/RNG behavior."""
import hashlib,json,subprocess
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
BASE='5dbc04186a1ee930b0a2f92b2df82d4556417d22'
old=subprocess.check_output(['git','show',BASE+':assets/game.js'],cwd=ROOT,text=True);new=(ROOT/'assets/game.js').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for source in [old,new]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();pages.append(p)
 rows=[]
 for scenario in ['settlement','regional','hardtimes','industrial']:
  for seed in [42,909]:
   for p in pages:p.evaluate('a=>__townTest.reset(...a)',[scenario,seed])
   for days in [1,29,15]:
    values=[]
    for p in pages:
     p.evaluate('n=>__townTest.step(n)',days);values.append(json.loads(p.evaluate('__townTest.save()')))
    evidence=values[1].pop('serviceCashEvidence',None)
    assert evidence and evidence['day']==values[1]['day'] and evidence['closingCash']==values[1]['treasury'],evidence
    assert values[0]==values[1],(scenario,seed,values[0]['day'],'Model changed beyond additive evidence')
   rows.append({'scenario':scenario,'seed':seed,'day':values[1]['day'],'all_existing_fields_equal':True})
 b.close()
print(json.dumps({'base':BASE,'source_sha256':hashlib.sha256(new.encode()).hexdigest(),'cases':rows,'comparison':'Only newly introduced serviceCashEvidence removed; all pre-existing fields compared exactly'},indent=2))
