"""Historical candidate-only negative; this does not enable the held warning.

Requires the public 2d5df40 candidate and 4056c66 retention checkpoint objects.
"""
from pathlib import Path
import gzip, hashlib, io, json, re, subprocess, tarfile
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE='4056c66e4ca15e5fb38d85516f841ff53c13fde2'
CANDIDATE='2d5df40e26d32eefc03c82fbcedcd51053ec7eb3'
def blob(commit,path):return subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT)
archive=subprocess.check_output(['git','archive',BASE,'src'],cwd=ROOT)
with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
 modules={Path(m.name).name:bundle.extractfile(m).read().decode() for m in bundle.getmembers() if m.isfile() and m.name.endswith('.js')}
for name in ['17-service-budget-plan.js','98-service-budget-ui.js']:modules[name]=blob(CANDIDATE,'src/'+name).decode()
source='\n'.join('// SOURCE: '+name+'\n'+modules[name] for name in sorted(modules))
metadata=json.loads(blob(BASE,'release.json'))
source=re.sub(r'const RELEASE=Object.freeze\(\{[^\n]+\}\);','const RELEASE=Object.freeze('+json.dumps(metadata,separators=(',',':'))+');',source,count=1)
sha=hashlib.sha256(source.encode()).hexdigest()
assert sha=='e98d0be5fd54eb9ba2f0b2f20d6fb48f3c452accf1d90868665c8603700586f3',sha
html=blob(BASE,'assets/index.html').decode().replace('<script src="game.js"></script>','')
for name in ['style.css','vale.css','civic7.css','mayor8.css','service-budget.css']:html=html.replace('<link rel="stylesheet" href="'+name+'">','<style>'+blob(BASE,'assets/'+name).decode()+'</style>')
fixture=json.loads(gzip.decompress(blob(CANDIDATE,'docs/evidence/service-budget-warning8/fixtures/late-town-service-terminal.json.gz')))
probe='''window.__heldWarning={pressure:serviceBudgetCashPressure,step:()=>__townTest.step(1),load:x=>__townTest.load(x),pensions:()=>G.households.reduce((n,h)=>n+(h.pension||0),0),enact:()=>{draftPolicy={...G.policy,pensionDaily:0};enactPolicyPackage();},day:()=>G.day};'''
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();page.set_content(html);page.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));page.locator('#newTown').click();page.locator('#pause').click()
 assert page.evaluate('x=>__heldWarning.load(x)',fixture)
 page.evaluate('__heldWarning.step()');before=page.evaluate('__heldWarning.pressure()');actual=page.evaluate('__heldWarning.pensions()')
 page.evaluate('__heldWarning.enact()');after=page.evaluate('__heldWarning.pressure()');current_actual=page.evaluate('__heldWarning.pensions()');day=page.evaluate('__heldWarning.day()')
 assert before['day']==after['day']==day and actual>0 and actual==current_actual
 assert abs(before['pensionPaid']-actual)<.001 and after['pensionPaid']==0
 result={'candidate':CANDIDATE,'assembled_on':BASE,'source_sha256':sha,'day':day,'reported_before_policy_edit':before['pensionPaid'],'actual_paid_to_households':actual,'reported_after_same_day_policy_edit':after['pensionPaid'],'actual_paid_unchanged':current_actual,'defect':'Historical payment attribution changes after policy enactment without advancing a day','candidate_only':True}
 browser.close()
out=ROOT/'reports/service-warning-review';out.mkdir(parents=True,exist_ok=True);(out/'confirmed-staleness.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));print('CONFIRMED held candidate rewrites the reported prior pension payment after same-day policy enactment')
