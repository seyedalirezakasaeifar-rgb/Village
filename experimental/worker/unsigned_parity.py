"""Matched-source load and two-day parity around unsigned32 transport boundaries."""
from pathlib import Path
import sys,json,gzip,subprocess,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();worker=Path('experimental/worker/model.generated.js').read_text()
base=json.loads(gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])))
hook='''paused=true;save=()=>true;toast=()=>{};refreshAmbience=()=>{};updateHeader=()=>{};renderPanel=()=>{};window.unsignedOracle={load:a=>{G=JSON.parse(a);rngState=G.rngState;pendingEvent=null;invalidateRoads();},state:()=>{G.rngState=rngState;return JSON.parse(JSON.stringify(G));},step:()=>{tick();tick();G.rngState=rngState;return JSON.parse(JSON.stringify(G));}};\n'''
def model(g):return {k:v for k,v in g.items() if k not in ('trafficState','visualState')}
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'))
 p.evaluate('''code=>{const w=new Worker(URL.createObjectURL(new Blob([code],{type:'application/javascript'})));let serial=0,epoch=0;window.ask=m=>new Promise((resolve,reject)=>{const id=++serial;const h=e=>{if(e.data.id!==id)return;w.removeEventListener('message',h);if(e.data.ok){epoch=e.data.result.epoch;resolve(e.data.result);}else reject(Error(e.data.error));};w.addEventListener('message',h);w.postMessage({epoch,...m,id});});}''',worker)
 for seed in [0,1,2147483646,2147483647,2147483648,4294967294,4294967295]:
  archive=json.dumps({**base,'rngState':seed},separators=(',',':'))
  loaded=p.evaluate("a=>ask({type:'load',archive:a})",archive);p.evaluate('a=>unsignedOracle.load(a)',archive);initial=p.evaluate('unsignedOracle.state()')
  assert loaded['rng']==seed and initial['rngState']==seed,(seed,loaded['rng'],initial['rngState'])
  assert model(loaded['model'])==model(initial),(seed,'load model mismatch')
  advanced=p.evaluate("ask({type:'step',days:2})");expected=p.evaluate('unsignedOracle.step()');assert model(advanced['model'])==model(expected),(seed,'two day model mismatch')
  assert advanced['rng']==expected['rngState'];rows.append({'seedDecimal':str(seed),'loadExact':True,'twoDayExactModel':True,'workerRngDecimal':str(advanced['rng']),'hostRngDecimal':str(expected['rngState'])})
 b.close()
receipt={'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'generatedWorkerSha256':hashlib.sha256(worker.encode()).hexdigest(),'archiveSha256':hashlib.sha256(json.dumps(base,separators=(',',':')).encode()).hexdigest(),'host':'Chromium only; native Java/bridge path not exercised','rows':rows}
Path('experimental/worker/unsigned-parity.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
