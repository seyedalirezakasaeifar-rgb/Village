from pathlib import Path
import sys,json,gzip,subprocess,hashlib,time,os
projection=os.environ.get("RENDER_PROJECTION","1")=="1"
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode()
source=Path('assets/game.js').read_text()
hook='''paused=true;const oracleEffects=[];save=()=>{oracleEffects.push('save-request');return true;};toast=()=>oracleEffects.push('notification');refreshAmbience=()=>oracleEffects.push('ambience-refresh');updateHeader=()=>oracleEffects.push('header-invalidated');renderPanel=()=>oracleEffects.push('panel-invalidated');window.oracle={load:a=>{G=JSON.parse(a);rngState=G.rngState;invalidateRoads();pendingEvent=null;},step:n=>{for(let i=0;i<n;i++)tick();},review:i=>reviewCouncilInbox(i),state:()=>{G.rngState=rngState;return JSON.parse(JSON.stringify(G));},effects:()=>oracleEffects.splice(0)};
'''
def clean(g):return {k:v for k,v in g.items() if k not in ('trafficState','visualState')}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.route('http://worker-proof.test/',lambda route:route.fulfill(body=html,content_type='text/html'));p.goto('http://worker-proof.test/');p.evaluate('''()=>{window.nativeRAF=requestAnimationFrame;window.requestAnimationFrame=f=>(window.productionRAF=nativeRAF(f));}''');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'))
 p.evaluate('a=>oracle.load(a)',archive)
 p.evaluate('''code=>{window.w=new Worker(URL.createObjectURL(new Blob([code],{type:'application/javascript'})));let serial=0,epoch=0,command=0;window.ask=m=>new Promise((resolve,reject)=>{const id=++serial;const h=e=>{if(e.data.id===id){w.removeEventListener('message',h);if(e.data.ok)epoch=e.data.result.epoch;resolve(e.data);}};w.addEventListener('message',h);w.postMessage({epoch,command:++command,...m,id});setTimeout(()=>reject(Error('Worker timeout')),30000);});}''',Path('experimental/worker/model.generated.js').read_text())
 def ask(m):
  r=p.evaluate('m=>ask(m)',m);assert r['ok'],r;return r['result']
 ask({'type':'load','archive':archive})
 before=ask({'type':'export'})
 prepared=ask({'type':'save-prepare'})
 assert clean(json.loads(prepared['archive']))==clean(before['model'])
 # One isolated write and exact readback, then ACK. Never production save keys.
 stored=p.evaluate("""record=>{window.proofWrites=0;localStorage.setItem('worker-proof-only',record.archive);proofWrites++;const text=localStorage.getItem('worker-proof-only');let h=2166136261;for(let i=0;i<text.length;i++){h^=text.charCodeAt(i);h=Math.imul(h,16777619);}return {checksum:(h>>>0).toString(16),exact:text===record.archive,writes:proofWrites};}""",prepared)
 assert stored['exact'] and stored['checksum']==prepared['checksum']
 receipt=ask({'type':'save-ack','token':prepared['token'],'checksum':stored['checksum']});assert receipt['persisted']
 repeated=p.evaluate('m=>ask(m)',{'type':'save-ack','token':prepared['token'],'checksum':stored['checksum']});assert not repeated['ok']
 pinned=ask({'type':'save-prepare'});ask({'type':'load','archive':archive})
 stale=p.evaluate('m=>ask(m)',{'type':'save-ack','token':pinned['token'],'checksum':pinned['checksum']});assert not stale['ok']
 assert p.evaluate('proofWrites')==1
 p.evaluate("localStorage.removeItem('worker-proof-only')")
 Path('experimental/worker/save-handshake-proof.json').write_text(json.dumps({'exactCanonicalReadback':True,'oneWrite':True,'duplicateAckRejected':True,'loadInvalidatesPreparedToken':True,'receipt':receipt,'limitations':['Isolated test storage key; not production save envelope','No crash durability or native validation claim','Root transaction and visual-envelope contracts still require owner integration']},indent=2));print('PASS isolated prepare/write/readback/ack, no double persistence, stale epoch rejected');b.close()
