from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
native=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
source=(native/'assets/game.js').read_text();worker=(native/'experimental/worker/model.generated.js').read_text()
assert hashlib.sha256(source.encode()).hexdigest()=='218de17d31e130f8f683ab1287307380eb2ec0689b06d39a9003ef26883a1fc7'
assert hashlib.sha256(worker.encode()).hexdigest()=='4d25fdaaad07f79cd7d9e5cbff03268d7572bcbd04fa18617d54f716680e0b75','Build exact a675ce4 worker first'
hook='''save=()=>true;window.nativeSeedOracle={state:()=>{G.rngState=rngState;return JSON.parse(JSON.stringify(G));},step:()=>{tick();tick();G.rngState=rngState;return JSON.parse(JSON.stringify(G));}};\n'''
def clean(g):return {k:v for k,v in g.items() if k not in ('trafficState','visualState')}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'));p.evaluate("__townTest.reset('settlement',314159265)");p.evaluate("document.getElementById('pause').click()")
 archive=p.evaluate('__townTest.save()');initial=p.evaluate('nativeSeedOracle.state()')
 p.evaluate('''code=>{const w=new Worker(URL.createObjectURL(new Blob([code],{type:'application/javascript'})));let serial=0,epoch=0;window.ask=m=>new Promise((resolve,reject)=>{const id=++serial;const h=e=>{if(e.data.id!==id)return;w.removeEventListener('message',h);if(e.data.ok){epoch=e.data.result.epoch;resolve(e.data.result);}else reject(Error(e.data.error));};w.addEventListener('message',h);w.postMessage({epoch,...m,id});});}''',worker)
 loaded=p.evaluate("a=>ask({type:'load',archive:a})",archive);assert clean(loaded['model'])==clean(initial)
 advanced=p.evaluate("ask({type:'step',days:2})");expected=p.evaluate('nativeSeedOracle.step()');assert clean(advanced['model'])==clean(expected)
 receipt={'prototype':'a675ce4e3b7ed421f0cc04f600d5543606bceb0d','sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'seed':'314159265','initialPopulation':initial['stats']['population'],'initialDay':initial['day'],'archiveBytes':len(archive.encode()),'archiveSha256':hashlib.sha256(archive.encode()).hexdigest(),'day0Exact':True,'day2ExactModelRng':True,'initialRng':str(initial['rngState']),'workerRng':str(advanced['rng']),'hostRng':str(expected['rngState']),'reportedNativeHostRng':'2786499683','host':'Chromium only; native failure remains open'}
 Path('experimental/worker/native-seed-replay.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt));b.close()
