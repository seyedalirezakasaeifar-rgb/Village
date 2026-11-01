"""Disabled realtime prototype: complete JSON delta, real view and bounded clock controls."""
from pathlib import Path
import sys,json,gzip,subprocess,hashlib,time
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text();bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js'])
archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode()
hook='''window.rtProbe={model:()=>JSON.stringify(G),load:a=>{G=JSON.parse(a);rngState=G.rngState;const metrics=G.roadMetrics;invalidateRoads();G.roadMetrics=metrics;pendingEvent=null;paused=true;},step:n=>{for(let i=0;i<n;i++)tick();return JSON.parse(archivePayload());}};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1000,'height':740});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://realtime.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://realtime.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bridge+hook+'// SOURCE: 99-instrumentation.js'))
 p.evaluate('''async a=>window.real=await __workerRealView.enable(a.code,a.archive,{realtime:true,startPaused:true,initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':code,'archive':archive})
 rows=[]
 for speed in [1,16,64]:
  p.evaluate('a=>real.load(a)',archive);p.evaluate('s=>real.setRealtimeSpeed(s)',speed);p.evaluate('real.settleSaves()');p.evaluate('''()=>{window.frames=[];window.inputs=[];let last=performance.now();function f(t){frames.push(t-last);last=t;for(const x of inputs)if(!x.raf)x.raf=performance.now()-x.stamp;if(!window.stopFrames)requestAnimationFrame(f);}window.stopFrames=false;requestAnimationFrame(f);window.inputListener=e=>inputs.push({stamp:e.timeStamp,delay:performance.now()-e.timeStamp,trusted:e.isTrusted});document.addEventListener('pointerdown',inputListener,true);}''');start=p.evaluate('performance.now()');p.evaluate('real.setRealtimePaused(false)')
  for i in range(8):
   p.wait_for_timeout(500);p.mouse.move(460,350);p.mouse.down();p.mouse.move(500,370,steps=2);p.mouse.up()
  p.evaluate('real.setRealtimePaused(true)');p.evaluate('real.settleRealtime()');end=p.evaluate('performance.now()');state=p.evaluate('real.realtimeStatus()');p.wait_for_timeout(150);assert p.evaluate('real.realtimeStatus().committedDay')==state['committedDay'],'Pause drained days';assert not p.evaluate('real.recoveryStatus().faulted'),p.evaluate('real.recoveryStatus()')
  metrics=p.evaluate('''()=>{stopFrames=true;document.removeEventListener('pointerdown',inputListener,true);const stats=a=>{a.sort((x,y)=>x-y);return {n:a.length,p95:a[Math.floor(a.length*.95)],p99:a[Math.floor(a.length*.99)],max:Math.max(...a)}};return {frames:stats(frames),input:stats(inputs.filter(x=>x.raf).map(x=>x.raf)),trusted:inputs.every(x=>x.trusted),hud:document.querySelector('#effectiveSpeed').textContent};}''');rows.append({'speed':speed,'elapsedMs':end-start,'days':state['committedDay']-json.loads(archive)['day'],'state':state,**metrics});print({k:v for k,v in rows[-1].items() if k!='state'},flush=True)
  # Compare every canonical field including RNG, except original visual metadata.
  exported=p.evaluate('real.command({type:"export"})');assert json.loads(exported['archive'])==exported['model'];actual=exported['model'];oracle=b.new_page();oracle.route('http://oracle.test/',lambda r:r.fulfill(body=html,content_type='text/html'));oracle.goto('http://oracle.test/');oracle.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'));oracle.evaluate('a=>rtProbe.load(a)',archive);expected=oracle.evaluate('n=>rtProbe.step(n)',rows[-1]['days']);expected['speed']=speed
  for key in ['visualState','trafficState']:actual.pop(key,None);expected.pop(key,None)
  assert actual==expected,'Realtime full canonical model/RNG mismatch';oracle.close()
 assert not errors,errors
 receipt={'productionEnabled':False,'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'bridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'fixtureSha256':hashlib.sha256(archive.encode()).hexdigest(),'fullCanonicalModelRngEqual':True,'rows':rows,'pageErrors':errors};Path('experimental/worker/realtime-view-proof.json').write_text(json.dumps(receipt,indent=2)+'\n');b.close()
