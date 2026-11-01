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
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.evaluate('''()=>{window.nativeRAF=requestAnimationFrame;window.requestAnimationFrame=f=>(window.productionRAF=nativeRAF(f));}''');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'))
 p.evaluate('a=>oracle.load(a)',archive)
 p.evaluate('''code=>{window.w=new Worker(URL.createObjectURL(new Blob([code],{type:'application/javascript'})));let serial=0,epoch=0,command=0;window.ask=m=>new Promise((resolve,reject)=>{const id=++serial;const h=e=>{if(e.data.id===id){w.removeEventListener('message',h);if(e.data.ok)epoch=e.data.result.epoch;resolve(e.data);}};w.addEventListener('message',h);w.postMessage({epoch,command:++command,...m,id});setTimeout(()=>reject(Error('Worker timeout')),30000);});}''',Path('experimental/worker/model.generated.js').read_text())
 def ask(m):
  r=p.evaluate('m=>ask(m)',m);assert r['ok'],r;return r['result']
 result=ask({'type':'validate-restore','archive':archive});assert result['validated'];print('PASS isolated actual hydrateSave');b.close()
