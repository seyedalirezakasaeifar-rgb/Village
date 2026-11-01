"""Host-only phase attribution; external timers, no model writes or performance certification."""
import sys,json,gzip,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text(); archive=gzip.decompress((ROOT/'tests/fixtures/retail-refusal-pending-project.json.gz').read_bytes()).decode()
marks=[(" const residentsByHome=new Map();", "geometry"),(" const market=householdMarket(),localGrocers=", "retail"),(" const incomes=Object.values(blocks)","services"),(" for(const b of Object.values(blocks)){", "profiles"),(" return urbanCache={town:G,net,day", "end")]
for needle,label in marks:
 assert source.count(needle)==1,(needle,source.count(needle))
 source=source.replace(needle, ('districtMark('+json.dumps(label)+');'+needle),1)
needle=' const population=homes.reduce((n,h)=>n+h.residents,0);';assert source.count(needle)==1
source=source.replace(needle,' const districtPopStart=performance.now();'+needle+'districtAttr.populationMs+=performance.now()-districtPopStart;districtAttr.populationCalls++;')
probe=r'''let districtAttr={},districtPhase=null,districtTime=0;function districtMark(next){const now=performance.now();if(districtPhase)districtAttr[districtPhase]=(districtAttr[districtPhase]||0)+now-districtTime;districtPhase=next==='end'?null:next;districtTime=now;}
window.__districtAttribution={run:({archive,days})=>{__townTest.load(archive);closePanel();paused=true;districtAttr={populationMs:0,populationCalls:0};districtPhase=null;const start=performance.now();__townTest.step(days);return {days,wallMs:performance.now()-start,...districtAttr,valid:validateTown().ok}}};'''
source=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();page.set_content(html);page.add_script_tag(content=source);page.locator('#newTown').click();page.locator('#pause').click();page.evaluate('a=>__districtAttribution.run(a)',{'archive':archive,'days':7});rows=[page.evaluate('a=>__districtAttribution.run(a)',{'archive':archive,'days':days})for days in [20,30]for _ in range(5)];b.close()
print(json.dumps({'source_sha256':hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest(),'instrumentation':'external phase timers only; timers add overhead; identical archived town and test-step clock; population timer nested in services','samples':rows},indent=2))
