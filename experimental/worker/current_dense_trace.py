"""Bounded matched 31-day dense trace. Experimental batch cadence, not realtime acceptance."""
from pathlib import Path
import sys,json,gzip,subprocess,hashlib,time
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();worker=Path('experimental/worker/model.generated.js').read_text();archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode()
bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js'])
hook='''paused=true;window.denseHost={load:a=>{G=JSON.parse(a);rngState=G.rngState;pendingEvent=null;const metrics=G.roadMetrics;invalidateRoads();G.roadMetrics=metrics;centerTownCamera();dirty=true;draw();},step:n=>{const t=performance.now();for(let i=0;i<n;i++)tick();const model=JSON.parse(archivePayload());updateHeader();dirty=true;draw();return {model,ms:performance.now()-t};}};\n'''
trace='''()=>{window.perfTrace={frames:[],inputs:[]};let last=performance.now();function frame(t){perfTrace.frames.push(t-last);last=t;for(const i of perfTrace.inputs)if(i.nextRaf===undefined)i.nextRaf=performance.now()-i.stamp;requestAnimationFrame(frame);}requestAnimationFrame(frame);document.addEventListener('pointerdown',e=>perfTrace.inputs.push({trusted:e.isTrusted,handlerDelay:performance.now()-e.timeStamp,stamp:e.timeStamp}),true);}'''
def summary(xs):
 xs=sorted(xs);return {'n':len(xs),'p95':xs[min(len(xs)-1,int(len(xs)*.95))] if xs else None,'max':max(xs) if xs else None}
def clean(g):return {k:v for k,v in g.items() if k not in ['visualState','trafficState']}
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for rep in range(3):
  models={}
  for mode in ['sync','worker']:
   p=b.new_page(viewport={'width':1000,'height':740});p.route('http://dense-current.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://dense-current.test/');errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',(bridge if mode=='worker' else hook)+'// SOURCE: 99-instrumentation.js'))
   if mode=='worker':p.evaluate('async a=>window.real=await __workerRealView.enable(a.worker,a.archive)',{'worker':worker,'archive':archive})
   else:p.evaluate('a=>denseHost.load(a)',archive)
   p.evaluate(trace);p.wait_for_timeout(100);p.mouse.move(470,360)
   p.evaluate('''mode=>{window.finished=false;setTimeout(async()=>{const t=performance.now();try{window.result=mode==='worker'?await real.command({type:'step',days:31}):denseHost.step(31);window.elapsed=performance.now()-t;}catch(e){window.failure=String(e);}finally{window.finished=true;}},100);}''',mode)
   time.sleep(.12)
   for _ in range(4):
    p.mouse.down();p.mouse.move(530,390,steps=3);p.mouse.up();p.mouse.move(470,360);time.sleep(.02)
   p.wait_for_function('finished',timeout=60000);p.wait_for_timeout(80);assert not p.evaluate('window.failure||null');result=p.evaluate('result');models[mode]=clean(result['model']);metrics=p.evaluate('({elapsed,trace:perfTrace,heap:performance.memory?.usedJSHeapSize})');assert all(x['trusted'] for x in metrics['trace']['inputs']);rows.append({'rep':rep,'mode':mode,'days':31,'elapsedMs':metrics['elapsed'],'workerRequestMs':result.get('requestMs'),'workerProfile':result.get('profile'),'frameMs':summary(metrics['trace']['frames']),'handlerDelayMs':summary([x['handlerDelay'] for x in metrics['trace']['inputs']]),'inputToRafMs':summary([x['nextRaf'] for x in metrics['trace']['inputs'] if 'nextRaf' in x]),'heapObservedBytes':metrics['heap'],'pageErrors':errors});assert not errors,errors;p.close()
  assert models['sync']==models['worker'],'Dense monthly model/RNG mismatch'
 b.close()
Path('experimental/worker/current-dense-trace.json').write_text(json.dumps({'candidateCommit':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),'bridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'fixtureSha256':hashlib.sha256(archive.encode()).hexdigest(),'population':json.loads(archive)['stats']['population'],'fullModelRngEqual':True,'productionAdmissionOwner':False,'snapshotCadence':'one full snapshot per31-day batch, not realtime acceptance','trustedInput':'four actual map pans per matched run','rows':rows},indent=2)+'\n');print(json.dumps(rows,indent=2))
