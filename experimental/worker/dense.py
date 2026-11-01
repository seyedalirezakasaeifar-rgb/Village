from pathlib import Path
import sys,json,gzip,subprocess,hashlib,time
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
 start=time.perf_counter();r=ask({'type':'step','days':31});worker_seconds=time.perf_counter()-start;start=time.perf_counter();p.evaluate('oracle.step(31)');sync_seconds=time.perf_counter()-start;assert clean(r['model'])==clean(p.evaluate('oracle.state()'))
 effects=[x for x in p.evaluate('oracle.effects()') if x not in ('header-invalidated','panel-invalidated')];assert [x['type'] for x in r['outbox']]==effects,(r['outbox'],effects)
 # Use an actual pending petition and an affordable choice in original DOM handler.
 assert r['model']['councilInbox']
 r=ask({'type':'review','index':0});p.evaluate('oracle.review(0)');event=next(x['payload'] for x in r['outbox'] if x['type']=='council-event');ix=next(c['index'] for c in event['choices'] if c['cost']<=r['model']['treasury'])
 r=ask({'type':'choice','eventId':event['id'],'index':ix});p.locator('#eventChoices button').nth(ix).click();assert clean(r['model'])==clean(p.evaluate('oracle.state()')),'Council model differs'
 stale=p.evaluate('m=>ask(m)',{'type':'choice','eventId':event['id'],'index':ix});assert not stale['ok']
 repeated=p.evaluate("ask({type:'policy',command:1,key:'minWage',value:30})");assert not repeated['ok']
 r=ask({'type':'step','days':31});p.evaluate('oracle.step(31)');assert clean(r['model'])==clean(p.evaluate('oracle.state()'))
 exported=ask({'type':'export'});assert clean(json.loads(exported['archive']))==clean(r['model'])
 # Independent readonly completed snapshot UI, no main-thread model mutation.
 p.evaluate('''()=>{cancelAnimationFrame(window.productionRAF);window.requestAnimationFrame=window.nativeRAF;}''')
 p.set_content('<button id="command">Raise wage</button><output id="city"></output><canvas id="scene" width="400" height="200"></canvas>')
 p.evaluate('''snapshot=>{window.completed=Object.freeze(snapshot);window.trace={frames:[],acks:[],inputs:[]};let last=performance.now();function paint(t){trace.frames.push(t-last);last=t;const c=document.querySelector('#scene').getContext('2d');c.clearRect(0,0,400,200);for(const b of completed.model.buildings)c.fillRect((b.x%80)*5,(b.y%40)*5,3,3);requestAnimationFrame(paint);}requestAnimationFrame(paint);document.querySelector('#city').textContent='Committed day '+completed.day;document.querySelector('#command').onclick=async e=>{const t=performance.now();trace.inputs.push({trusted:e.isTrusted,time:t});const r=await ask({type:'policy',key:'minWage',value:completed.model.policy.minWage+1});trace.acks.push({ms:performance.now()-t,ok:r.ok,epoch:r.result?.epoch,day:r.result?.day});if(r.ok){completed=Object.freeze(r.result);document.querySelector('#city').textContent='Committed day '+completed.day;}};}''',exported)
 p.evaluate("()=>{window.busy=ask({type:'step',days:60});return true;}")
 for _ in range(5):p.locator('#command').click();p.wait_for_timeout(50)
 p.evaluate('busy');p.wait_for_timeout(200);trace=p.evaluate('trace');assert len(trace['acks'])==5 and all(x['ok'] for x in trace['acks'])
 old_epoch=exported['epoch'];new=ask({'type':'load','archive':archive});bad=p.evaluate('m=>ask(m)',{'type':'export','epoch':old_epoch});assert not bad['ok']
 receipt={'fixtureSha256':hashlib.sha256(archive.encode()).hexdigest(),'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'exactModelRng62Days':True,'validCouncilChoice':True,'staleAndRepeatedRejected':True,'oldEpochRejected':True,'exportExact':True,'dayEffectsEqual':True,'first31DayWallSeconds':{'synchronous':sync_seconds,'workerIncludingSnapshot':worker_seconds},'trustedInputs':trace['inputs'],'acks':trace['acks'],'rafMaxMs':max(trace['frames']),'rafSamples':len(trace['frames']),'limitations':['Minimal separate readonly UI; not production renderer','No durable storage writes','Host Chromium only','Single matched fixture; not throughput certification']}
 Path('experimental/worker/dense-proof.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt));b.close()
