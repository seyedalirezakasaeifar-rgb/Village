"""Bounded paired dense realtime responsiveness; functional replay is a separate gate."""
from pathlib import Path
import sys,json,gzip,subprocess,hashlib,time
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
public='87811c52cdb9aecd13cd23beebd52f6475c6dd9c'
original=subprocess.check_output(['git','show',public+':assets/game.js']).decode();source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text();bridge=Path('experimental/worker/real-view.generated.js').read_text();archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode()
hook='''window.metricLoad=a=>{G=JSON.parse(a);rngState=G.rngState;traffic=[];intersectionGates.clear();const metrics=G.roadMetrics;invalidateRoads(false);restoreTransport();G.roadMetrics=metrics;pendingEvent=null;active='';paused=true;$('welcome').style.display='none';centerTownCamera();dirty=true;};window.metricState=()=>({day:G.day,population:G.stats.population,total:totalMoney(),valid:validateTown().ok,heap:performance.memory?.usedJSHeapSize});'''
trace='''()=>{window.mt={frames:[],inputs:[]};let last=performance.now();window.mtStop=false;function f(t){mt.frames.push(t-last);last=t;for(const i of mt.inputs)if(i.raf===undefined)i.raf=performance.now()-i.stamp;if(!mtStop)requestAnimationFrame(f);}requestAnimationFrame(f);window.mtListener=e=>mt.inputs.push({stamp:e.timeStamp,delay:performance.now()-e.timeStamp,trusted:e.isTrusted});document.addEventListener('pointerdown',mtListener,true);}'''
def stats(xs):
 xs=sorted(xs);return {'n':len(xs),'p95':xs[min(len(xs)-1,int(len(xs)*.95))]if xs else None,'p99':xs[min(len(xs)-1,int(len(xs)*.99))]if xs else None,'max':max(xs)if xs else None}
rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for rate in [0,1,16,64]:
  for mode in ['sync','worker']:
   p=b.new_page(viewport={'width':1000,'height':740});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://metrics.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://metrics.test/');p.add_script_tag(content=(source if mode=='worker'else original).replace('// SOURCE: 99-instrumentation.js',(bridge if mode=='worker'else '')+hook+'// SOURCE: 99-instrumentation.js'))
   if mode=='worker':
    p.evaluate('''async a=>window.real=await __workerRealView.enable(a.code,a.archive,{realtime:true,startPaused:true,initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':code,'archive':archive});p.evaluate('real.settleSaves()')
   else:p.evaluate('metricLoad',archive)
   p.locator('#speedRange').fill(str([1,2,4,8,16,32,64].index(rate or 1)));p.locator('#speedRange').dispatch_event('change')
   if mode=='worker':p.evaluate('real.settleRealtime()');p.evaluate('real.settleSaves()')
   initial=p.evaluate('metricState()');p.evaluate(trace);start=p.evaluate('performance.now()')
   if rate:p.locator('#pause').click()
   for i in range(10):
    p.wait_for_timeout(500);p.mouse.move(460,350);p.mouse.down();p.mouse.move(500,370,steps=2);p.mouse.up()
   if rate:p.locator('#pause').click()
   if mode=='worker':p.evaluate('real.settleRealtime()')
   end=p.evaluate('performance.now()');p.wait_for_timeout(80);metrics=p.evaluate('''()=>{mtStop=true;document.removeEventListener('pointerdown',mtListener,true);return {trace:mt,state:metricState(),status:window.real?real.realtimeStatus():null,hud:document.querySelector('#effectiveSpeed').textContent};}''');t=metrics['trace'];assert all(i['trusted']for i in t['inputs']);assert not errors,errors;assert metrics['state']['valid'];assert abs(metrics['state']['total']-initial['total'])<.05
   rows.append({'mode':mode,'requested':rate,'initialPopulation':initial['population'],'finalPopulation':metrics['state']['population'],'days':metrics['state']['day']-initial['day'],'elapsedMs':end-start,'delivered':(metrics['state']['day']-initial['day'])*1650/(end-start),'frameMs':stats(t['frames']),'handlerDelayMs':stats([i['delay']for i in t['inputs']]),'inputNextRafMs':stats([i['raf']for i in t['inputs']if 'raf'in i]),'heapObservedBytes':metrics['state']['heap'],'owedDays':metrics['status']['owedDays']if metrics['status']else None,'hud':metrics['hud'],'errors':errors});print({k:v for k,v in rows[-1].items()if k not in ['errors','hud']},flush=True);p.close()
 b.close()
Path('experimental/worker/current-realtime-metrics.json').write_text(json.dumps({'productionEnabled':False,'publicOracle':public,'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'bridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'fixtureSha256':hashlib.sha256(archive.encode()).hexdigest(),'fixturePopulation':778,'physicalAndroidClaim':False,'classicRendererOnly':True,'audioHardwareClaim':False,'sameInitialFixtureSequentialWorkloads':True,'deterministicReplayClaim':False,'rows':rows},indent=2)+'\n')
