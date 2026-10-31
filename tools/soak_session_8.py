"""Passive 45-minute growth/audio/input/save acceptance on an immutable bundle.

No simulation fast-forward, disabled growth, periodic economic reset, mocked audio,
render/routing profiler or GC during play. Imports retain the current town. Two
founding/restore interruptions exercise the real lifecycle without resetting its
long-running economy. All counts and timing limitations remain in the receipt.
"""
from pathlib import Path
import ast,functools,hashlib,http.server,json,math,os,subprocess,threading,time,traceback
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
EXPECTED='d90bb509173a803b75c3cdc432fea57ce2f1e2abbcb13b8886c56d8feaffe515'
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
assert sha==EXPECTED,('Unexpected source',sha)
def literal(path,name):
 return next(ast.literal_eval(n.value) for n in ast.parse(path.read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
fixture=literal(ROOT/'tests/test_transit_live_performance.py','probe')
setup=literal(ROOT/'tools/profile_session.py','probe')
# Reuse only the paid fixture construction, not its frame/component profilers.
setup=setup[setup.index('window.__session={'):setup.index(' clear:()=>')]
setup=setup[:setup.index(' state:()=>')] if ' state:()=>' in setup else setup
setup+='};\n'
# The extracted prefix includes mode/setup/evolve; make the trailing comma valid.
probe=r'''
const longStats={raf:[],ticks:[],input:[]};let longPrevious=0,longStart=0,longDay=0;
const longTickBase=tick;tick=function(){const t=performance.now();try{return longTickBase()}finally{longStats.ticks.push(performance.now()-t);if(longStats.ticks.length>10000)longStats.ticks.shift()}};
document.addEventListener('pointerdown',e=>{if(!e.isTrusted)return;const stamp=e.timeStamp,handler=performance.now()-stamp,type=e.pointerType;requestAnimationFrame(()=>{longStats.input.push({handlerMs:handler,nextFrameMs:performance.now()-stamp,type});if(longStats.input.length>1000)longStats.input.shift();});},{capture:true,passive:true});
function longRaf(now){if(longPrevious)longStats.raf.push(now-longPrevious);longPrevious=now;if(longStats.raf.length>10000)longStats.raf.shift();requestAnimationFrame(longRaf)}
let longTrace=null,longTraceInstalled=false;
function installLongTrace(){if(longTraceInstalled)return;longTraceInstalled=true;for(const name of ['frame','tick','dailyEconomy','privateServiceInvestmentDay','urbanEvolutionDay','assignJobs','recompute','systemsDay','maintainRoads','renderPanel','updateHeader','draw','save','archivePayload','persistSnapshot','readSaveEnvelope','checksum']){const base=eval(name),replacement=function(...args){if(!longTrace)return base.apply(this,args);const t=performance.now();try{return base.apply(this,args)}finally{const a=longTrace.components[name]||(longTrace.components[name]=[]);if(a.length<10000)a.push(performance.now()-t);}};eval(name+'=replacement');}if(typeof PerformanceObserver==='function')try{new PerformanceObserver(list=>{if(longTrace)for(const e of list.getEntries())if(longTrace.longtasks.length<1000)longTrace.longtasks.push({start:e.startTime,duration:e.duration,name:e.name});}).observe({entryTypes:['longtask']});}catch(_){}
}
window.__long={
 traceStart:()=>{installLongTrace();longTrace={started:performance.now(),day:G.day,components:{},longtasks:[]}},
 traceStop:()=>{const r=longTrace;longTrace=null;return {...r,ended:performance.now(),endDay:G.day}},
 begin:()=>{longStats.raf=[];longStats.ticks=[];longStats.input=[];longPrevious=0;longStart=performance.now();longDay=G.day;requestAnimationFrame(longRaf)},
 zoom:z=>{cam.zoom=z;dirty=true},
 state:()=>({day:G.day,population:G.stats.population,people:G.people.length,households:G.households.length,buildings:G.buildings.length,firms:G.firms.length,treasury:G.treasury,region:G.region,total:totalMoney(),valid:validateTown(),goodsError:Math.max(...goodsBalance().map(v=>Math.abs(v.error))),autoBuild:G.autoBuild,privateEntry:G.policy.privateServices,requestedSpeed:speed,grid:T,deeds:G.charter.owned.length,routes:G.transit.routes.length,operating:G.transit.routes.filter(r=>r.stats.operating).length,drivers:G.transit.daily.staff,cargo:G.regionalTrade.shipments.length,providers:G.firms.filter(f=>f.privateService&&!f.closed).length,providerStaff:G.firms.filter(f=>f.privateService&&!f.closed).reduce((n,f)=>n+f.workers.length,0),privateClients:G.firms.filter(f=>f.privateService&&!f.closed).reduce((n,f)=>n+(f.clientsToday||0),0),atlas:atlas.size,atlasBytes,serviceCaches:serviceAccessCaches.size,traffic:traffic.length,history:G.history.length,events:G.events.length,transactions:G.transactions.length,observations:G.observations.length,loans:G.loans.length,paused,hostSuspended,hidden:document.hidden,pending:!!pendingEvent,backlog:acc/1.65,saveOrder,savePending:!!savePendingWrite,saveRunning:saveWriteRunning,musicEnabled,musicTrack,musicError,musicDecks:musicDecks.map(d=>({index:d.index,paused:d.audio.paused,currentTime:d.audio.currentTime,readyState:d.audio.readyState,error:d.audio.error?.code||0,gain:d.gain}))}),
 pull:()=>{const now=performance.now(),r={seconds:(now-longStart)/1000,days:G.day-longDay,raf:longStats.raf,ticks:longStats.ticks,input:longStats.input};longStart=now;longDay=G.day;longStats.raf=[];longStats.ticks=[];longStats.input=[];return r},
 restoreCurrent:found=>{const raw=archivePayload(),total=totalMoney(),day=G.day,t=performance.now();if(found)start(true);if(!window.__townArchive.restore(raw))throw Error('Current archive restore rejected');if(totalMoney()!==total||G.day!==day)throw Error('Interruption changed current model');return {kind:found?'found-and-restore-current':'restore-current',ms:performance.now()-t,day,total}},
};
'''
def stats(a):
 a=sorted(a);return {'count':len(a),'p50Ms':a[len(a)//2] if a else 0,'p95Ms':a[min(len(a)-1,int(len(a)*.95))] if a else 0,'p99Ms':a[min(len(a)-1,int(len(a)*.99))] if a else 0,'maxMs':max(a) if a else 0}
def utc():return datetime.now(timezone.utc).isoformat()
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
out=ROOT/('reports/session-performance/'+os.environ.get('SESSION_RUN_LABEL','long-31987fc-corrected'));out.mkdir(parents=True,exist_ok=True)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
minutes=float(os.environ.get('SESSION_SOAK_MINUTES','45'));duration=minutes*60
result={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':sha,'instrumentation_sha256':hashlib.sha256((fixture+setup+probe).encode()).hexdigest(),'status':'starting','startedUtc':utc(),'requestedMinutes':minutes,'hostChromium':True,'physicalAndroid':False,'samples':[],'operations':[],'errors':[],'limitations':['Synthetic funded 2000-resident starting fixture; organic development enabled throughout live play.','Heap excludes portions of native canvas/GPU/media memory.','Touch is trusted emulated Chromium input; next RAF is not measured display photons.','RAF/tick capture adds light instrumentation; no renderer/transit function profiling.']}
def write():
 temp=out/'session.tmp';temp.write_text(json.dumps(result,indent=2)+'\n');temp.replace(out/'session.json')
write()
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);page=browser.new_page(viewport={'width':844,'height':390},has_touch=True);page.set_default_timeout(15000);page.on('pageerror',lambda e:result['errors'].append(str(e)));page.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+setup+'\n'+probe+'\n// SOURCE: 99-instrumentation.js')))
 try:
  page.goto('http://127.0.0.1:'+str(server.server_port)+'/index.html');page.locator('#newTown').click();page.locator('#pause').click();result['fixture']=page.evaluate('__session.setup()');page.evaluate('__session.evolve()');page.locator('#panelClose').click();page.locator('#speedRange').fill('6');cdp=page.context.new_cdp_session(page);cdp.send('Performance.enable');cdp.send('HeapProfiler.collectGarbage');result['initialHeapAfterGC']=cdp.send('Runtime.getHeapUsage');result['initialDOM']=cdp.send('Memory.getDOMCounters');page.locator('#pause').click();page.evaluate('__long.begin()');started=time.monotonic();result['liveStartedUtc']=utc();result['status']='running';write();print('START',result['liveStartedUtc'],'minutes',minutes,'source',sha,flush=True)
  panels=['economy','community','construction','settings','citizens','businesses','treasury','banking','overview','agenda'];iteration=0;next_sample=30;next_save=120;next_import=300;next_lifecycle=600;next_found=1200;trace_started=None;trace_finished=False;trace_metrics=None;last_zoom=-1;panel_open=False
  while time.monotonic()-started<duration:
   page.wait_for_timeout(4500);elapsed=time.monotonic()-started;zoom=int(elapsed//120)%2
   if zoom!=last_zoom:page.evaluate('z=>__long.zoom(z)',.23 if zoom else .85);last_zoom=zoom
   # Genuine touch each few seconds while the actual simulation keeps running.
   page.locator('#panelTitle' if panel_open else '#mapStatusToggle').tap()
   if iteration%3==2:
    if panel_open:page.locator('#panelClose').click();panel_open=False
    else:page.locator('[data-panel='+panels[(iteration//3)%len(panels)]+']').click();panel_open=True
   if elapsed>=next_save:
    if panel_open:page.locator('#panelClose').click()
    page.locator('[data-panel=settings]').click();t=time.monotonic();page.locator('#saveNow').click();page.wait_for_function('!document.querySelector("#saveNow").disabled');result['operations'].append({'kind':'save-button','seconds':elapsed,'ms':(time.monotonic()-t)*1000});page.locator('#panelClose').click();panel_open=False;next_save+=120
   if elapsed>=next_import:
    if panel_open:page.locator('#panelClose').click();panel_open=False
    result['operations'].append({'seconds':elapsed,**page.evaluate('__long.restoreCurrent(false)')});payload=page.evaluate('__townTest.save()');checkpoint=Path('/tmp/townledger-31987fc-late.json');checkpoint.write_text(payload);result['lateCheckpoint']={'path':str(checkpoint),'sha256':hashlib.sha256(payload.encode()).hexdigest(),'day':page.evaluate('__long.state().day')};next_import+=300
   if elapsed>=next_lifecycle:
    t=time.monotonic();before=page.evaluate('async()=>{await __townArchive.suspend();return __long.state().day}');page.wait_for_timeout(1800);assert page.evaluate('__long.state().day')==before;page.evaluate('__townArchive.resume()');result['operations'].append({'kind':'native-suspend-resume','seconds':elapsed,'ms':(time.monotonic()-t)*1000});next_lifecycle+=600
   if elapsed>=next_found:
    if panel_open:page.locator('#panelClose').click();panel_open=False
    result['operations'].append({'seconds':elapsed,**page.evaluate('__long.restoreCurrent(true)')});page.locator('#speedRange').fill('6');page.locator('#panelClose').click();panel_open=False;next_found+=1200
   if elapsed>=next_sample:
    raw=page.evaluate('__long.pull()');state=page.evaluate('__long.state()');sample={'utc':utc(),'seconds':elapsed,'windowSeconds':raw['seconds'],'days':raw['days'],'actualRate':raw['days']*1.65/raw['seconds'],'zoom':'far' if zoom else 'near','raf':stats(raw['raf']),'ticks':stats(raw['ticks']),'touchDelivery':stats([v['handlerMs'] for v in raw['input']]),'touchNextRAF':stats([v['nextFrameMs'] for v in raw['input']]),'touchCount':len(raw['input']),'heap':cdp.send('Runtime.getHeapUsage'),'dom':cdp.send('Memory.getDOMCounters'),'state':state};result['samples'].append(sample);write();print('SAMPLE',round(elapsed), 'day',state['day'],'pop',state['population'],'rate',round(sample['actualRate'],1),'rafP99',round(sample['raf']['p99Ms'],1),'touchMax',round(sample['touchNextRAF']['maxMs'],1),'heapMiB',round(sample['heap']['usedSize']/1048576,1),'routes',state['operating'],flush=True)
    assert not result['errors'] and state['valid']['ok'] and abs(state['total']-result['fixture']['total'])<.1 and state['goodsError']<.001,(result['errors'],state)
    assert state['autoBuild'] and state['privateEntry']==1 and state['requestedSpeed']==64 and state['grid']==128 and state['routes']==48 and state['deeds']==21,state
    assert state['atlasBytes']<=48*1024*1024 and state['atlas']<=600 and state['serviceCaches']<=2 and state['traffic']<=80 and state['history']<=240 and state['events']<=160 and state['transactions']<=800 and state['observations']<=1200 and len(state['musicDecks'])<=2,state
    assert not state['musicError'] and all(not d['error'] for d in state['musicDecks']),state['musicDecks']
    if len(result['samples'])==1:
     assert state['musicTrack']>=0 and any(not d['paused'] and d['currentTime']>2 for d in state['musicDecks']),state
     page.screenshot(path=str(out/'first-verified.png'));result['firstVerifiedUtc']=utc();write()
    next_sample+=30
   if elapsed>=660 and trace_started is None and not trace_finished:
    page.evaluate('__long.traceStart()');trace_metrics=cdp.send('Performance.getMetrics');trace_started=time.monotonic();result['componentTraceStartedUtc']=utc();write()
   if trace_started is not None and time.monotonic()-trace_started>=60:
    trace=page.evaluate('__long.traceStop()');after_metrics=cdp.send('Performance.getMetrics');before_metrics={v['name']:v['value'] for v in trace_metrics['metrics']};trace['browserMetricDeltas']={v['name']:v['value']-before_metrics.get(v['name'],0) for v in after_metrics['metrics'] if v['name'].endswith('Duration') or v['name'].endswith('Count')};trace['source_sha256']=sha;trace['state']=page.evaluate('__long.state()');trace['componentStats']={k:stats(v) for k,v in trace['components'].items()};(out/'late-component-trace.json').write_text(json.dumps(trace,indent=2)+'\n');payload=page.evaluate('__townTest.save()');checkpoint=Path('/tmp/townledger-31987fc-traced-late.json');checkpoint.write_text(payload);result['tracedLateCheckpoint']={'path':str(checkpoint),'sha256':hashlib.sha256(payload.encode()).hexdigest(),'state':trace['state']};result['componentTraceFinishedUtc']=utc();trace_started=None;trace_finished=True;write();print('LATE TRACE COMPLETE',utc(),flush=True)
   iteration+=1
  result['liveElapsedSeconds']=time.monotonic()-started;page.locator('#pause').click();page.evaluate('__townArchive.suspend()');page.wait_for_timeout(300);cdp.send('HeapProfiler.collectGarbage');result['finalHeapAfterGC']=cdp.send('Runtime.getHeapUsage');result['finalDOM']=cdp.send('Memory.getDOMCounters');result['finalState']=page.evaluate('__long.state()');result['status']='completed';result['finishedUtc']=utc();write();print('COMPLETE',utc(),'elapsed',result['liveElapsedSeconds'],flush=True)
 except BaseException as exc:
  result['status']='failed';result['failure']=str(exc);
  try:
   payload=page.evaluate('__townTest.save()');checkpoint=Path('/tmp/townledger-31987fc-late.json');checkpoint.write_text(payload);result['lateCheckpoint']={'path':str(checkpoint),'sha256':hashlib.sha256(payload.encode()).hexdigest(),'state':page.evaluate('__long.state()')}
  except Exception as checkpoint_error:result['checkpointError']=str(checkpoint_error)
  result['traceback']=traceback.format_exc();result['finishedUtc']=utc();write();print(result['traceback'],flush=True)
  try:page.screenshot(path=str(out/'failure.png'))
  except Exception:pass
  raise
 finally:browser.close();server.shutdown()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
