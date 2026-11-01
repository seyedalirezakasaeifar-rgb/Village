from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();worker=Path('experimental/worker/model.generated.js').read_text()
hook='''save=()=>true;window.seedOracle=(scenario,value)=>{chosenScenario=scenario;seed(value);G.rngState=rngState;return JSON.parse(archivePayload());};\n'''
def clean(g):return {k:v for k,v in g.items() if k not in ('trafficState','visualState')}
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'))
 for scenario,value in [('settlement',42),('settlement',4294967295),('hardtimes',42),('frontier',42),('industrial',42),('regional',42)]:
  expected=p.evaluate('a=>seedOracle(...a)',[scenario,value])
  result=p.evaluate('''args=>new Promise((resolve,reject)=>{const w=new Worker(URL.createObjectURL(new Blob([args.code],{type:'application/javascript'})));w.onerror=e=>{w.terminate();reject(Error(e.message));};w.onmessage=e=>{w.terminate();resolve(e.data);};w.postMessage({id:1,type:'prepare-founding',scenario:args.scenario,seed:args.value});})''',{'code':worker,'scenario':scenario,'value':value});assert result['ok'],result
  actual=json.loads(result['result']['archive']);assert clean(actual)==clean(expected),(scenario,value,[k for k in expected if clean(actual).get(k)!=clean(expected).get(k)])
  rows.append({'scenario':scenario,'seedDecimal':str(value),'exactModelRng':True,'population':actual['stats']['population'],'rngDecimal':str(actual['rngState'])})
 b.close()
Path('experimental/worker/founding-equivalence.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'rows':rows},indent=2));print(json.dumps(rows))
