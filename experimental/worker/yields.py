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
 ask({'type':'load','archive':archive})
 rows=[]
 for yield_mode in ["timer","channel"]:
  projection=True
  ask({'type':'load','archive':archive});p.evaluate('a=>oracle.load(a)',archive)
  sample=p.evaluate("""async options=>{const t=performance.now();const r=await ask({type:'step',days:31,projection:true,yieldMode:options});if(!r.ok)throw Error(r.error);window.componentSnapshot=r.result;return {browserRoundTripMs:performance.now()-t,workerRequestMs:r.result.requestMs,transferAndDispatchMs:performance.timeOrigin+performance.now()-r.result.workerSentAt,profile:r.result.profile};}""",yield_mode)
  sample['mainApplication']=p.evaluate('''()=>{const result=componentSnapshot;let t=performance.now();window.readonlyComponent=Object.freeze(result);const applyMs=performance.now()-t;const canvas=document.createElement('canvas');canvas.width=400;canvas.height=200;const ctx=canvas.getContext('2d'),draw=[];for(let i=0;i<30;i++){t=performance.now();ctx.clearRect(0,0,400,200);for(const b of result.model.buildings)ctx.fillRect((b.x%80)*5,(b.y%40)*5,3,3);draw.push(performance.now()-t);}draw.sort((a,b)=>a-b);return {applyMs,drawMedianMs:draw[15],drawP95Ms:draw[28]};}''')
  sample['syncTickMs']=p.evaluate('()=>{const t=performance.now();oracle.step(31);return performance.now()-t;}')
  exported=ask({'type':'export'});assert clean(exported['model'])==clean(p.evaluate('oracle.state()'))
  sample['projection']=projection;sample['yieldMode']=yield_mode;sample['exactModelRng']=True;rows.append(sample)
 Path('experimental/worker/yield-profile.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows));b.close()
