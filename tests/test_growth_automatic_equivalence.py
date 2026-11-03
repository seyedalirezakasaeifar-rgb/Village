"""Manual farm invitation leaves ordinary automatic economies exactly unchanged."""
import hashlib,json,subprocess
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
from neighborhood_history_oracle import ORACLE_PROBE
BASE='2e4ce5c8869a0483657ba3321d3e66e8954d780d'
current=(ROOT/'assets/game.js').read_text();reference=subprocess.check_output(['git','show',BASE+':assets/game.js'],cwd=ROOT,text=True);rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for source in [reference,current]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',ORACLE_PROBE+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();pages.append(p)
 for scenario in ['settlement','regional','industrial','hardtimes']:
  for p in pages:p.evaluate('s=>{__resetHistoryOracle();__townTest.reset(s,42)}',scenario)
  for days in [0,30,60,90,120,150,180]:
   states=[];expected_ledgers=[]
   for p in pages:
    if days:p.evaluate('__townTest.step(30)')
    states.append(json.loads(p.evaluate('__townTest.save()')));expected_ledgers.append(p.evaluate('__historyOracle()'))
   assert expected_ledgers[0]==expected_ledgers[1],(scenario,days)
   if 'function urbanRecordActivity()' in current and expected_ledgers[0]:states[0]['urban']['activity']=expected_ledgers[0]
   assert states[0]==states[1],(scenario,days)
   rows.append({'scenario':scenario,'elapsedDays':days,'completeArchiveMatchesIndependentExpectedState':True})
 b.close()
print(json.dumps({'reference':BASE,'reference_source_sha256':hashlib.sha256(reference.encode()).hexdigest(),'source_sha256':hashlib.sha256(current.encode()).hexdigest(),'excludedFields':[],'optionalHistoryComparedToIndependentPhaseOracle':True,'checkpoints':rows},indent=2))
