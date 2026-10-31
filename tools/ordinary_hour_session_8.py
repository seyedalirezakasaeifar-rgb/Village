"""One-hour ordinary-play soak on the generated terminal-town checkpoint.

The game uses real RAF, audio, economic growth, actual UI controls, saves and
trusted browser pointer input. No wallet injections, tick fast-forward or
disabled economic systems are used. Set ORDINARY_MINUTES=1 for harness preflight.
"""
from pathlib import Path
import functools,gzip,hashlib,http.server,json,os,subprocess,threading,time,traceback
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'assets/game.js').read_text()
SOURCE_SHA=hashlib.sha256(SOURCE.encode()).hexdigest()
BASE_COMMIT=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
FIXTURE_GZ=subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)
ARCHIVE=gzip.decompress(FIXTURE_GZ).decode()
FIXTURE=json.loads(ARCHIVE)
FIXTURE_SHA=hashlib.sha256(ARCHIVE.encode()).hexdigest()
MINUTES=float(os.environ.get('ORDINARY_MINUTES','60'))
DURATION=MINUTES*60
LABEL=os.environ.get('ORDINARY_LABEL','one-hour-latest-sync')
OUT=ROOT/'reports/session-performance'/LABEL
OUT.mkdir(parents=True,exist_ok=True)

PROBE=r'''
const ordinary={active:false,previous:0,raf:[],input:[],longtasks:0,maxLongtask:0};
function ordinaryFrame(now){if(ordinary.active&&ordinary.previous)ordinary.raf.push(now-ordinary.previous);ordinary.previous=now;requestAnimationFrame(ordinaryFrame)}requestAnimationFrame(ordinaryFrame);
document.addEventListener('pointerdown',e=>{if(e.isTrusted&&ordinary.active){const sent=e.timeStamp,handler=performance.now()-sent;requestAnimationFrame(()=>ordinary.input.push({handlerMs:handler,nextRAFMs:performance.now()-sent,pointerType:e.pointerType}));}},{capture:true,passive:true});
if(typeof PerformanceObserver==='function')try{new PerformanceObserver(list=>{for(const x of list.getEntries()){ordinary.longtasks++;ordinary.maxLongtask=Math.max(ordinary.maxLongtask,x.duration)}}).observe({entryTypes:['longtask']})}catch(_){}
window.__ordinary={
 start:()=>{ordinary.active=true;ordinary.raf=[];ordinary.input=[];ordinary.previous=0;ordinary.longtasks=0;ordinary.maxLongtask=0},
 pull:()=>{const r={raf:ordinary.raf,input:ordinary.input,longtasks:ordinary.longtasks,maxLongtask:ordinary.maxLongtask};ordinary.raf=[];ordinary.input=[];ordinary.longtasks=0;ordinary.maxLongtask=0;ordinary.previous=0;return r},
 stop:()=>{ordinary.active=false},
 state:()=>({day:G.day,population:G.stats.population,people:G.people.length,households:G.households.length,buildings:G.buildings.length,firms:G.firms.length,treasury:G.treasury,region:G.region,total:totalMoney(),growth:G.autoBuild,privateEntry:G.policy.privateServices,requested:speed,grid:T,deeds:G.charter.owned.length,routes:G.transit.routes.length,operating:G.transit.routes.filter(r=>r.stats.operating).length,cargo:G.regionalTrade.shipments.length,atlas:atlas.size,atlasBytes,serviceCaches:serviceAccessCaches.size,traffic:traffic.length,history:G.history.length,events:G.events.length,transactions:G.transactions.length,observations:G.observations.length,paused,hostSuspended,hidden:document.hidden,pending:!!pendingEvent,backlog:acc/1.65,zoom:cam.zoom,tickRecent:perfStats.ticks.slice(),saveOrder,savePending:!!savePendingWrite,saveRunning:saveWriteRunning,musicEnabled,musicTrack,musicError,musicDecks:musicDecks.map(d=>({index:d.index,paused:d.audio.paused,currentTime:d.audio.currentTime,readyState:d.audio.readyState,error:d.audio.error?.code||0}))}),
 audit:()=>({valid:validateTown(),goodsError:Math.max(...goodsBalance().map(v=>Math.abs(v.error)))}),
 inspect:(kind)=>{const rect=cv.getBoundingClientRect(),visible=[];for(let y=3;y<T-3;y++)for(let x=3;x<T-3;x++){const id=roadId(x,y),cell=cityCell(x,y);if(!charterOwns(x,y))continue;if(kind==='road'){if(![0,3].includes(cell)||G.landUse?.[id]||buildingAt(x,y))continue;}else if(kind==='repair'){if(cell!==1||(G.roadWear?.[id]??100)>96)continue;}else if(kind==='park'){if(G.treasury<buildCost.park||!canPlace(x,y,true,'park'))continue;}const q=iso(x,y),sx=rect.left+rect.width/2+(q[0]-cam.x)*cam.zoom,sy=rect.top+rect.height/2+(q[1]-cam.y)*cam.zoom;if(sx>rect.left+12&&sx<rect.right-12&&sy>rect.top+12&&sy<rect.bottom-12)visible.push({x,y,sx,sy});}visible.sort((a,b)=>Math.hypot(a.sx-(rect.left+rect.width/2),a.sy-(rect.top+rect.height/2))-Math.hypot(b.sx-(rect.left+rect.width/2),b.sy-(rect.top+rect.height/2)));return {count:visible.length,site:visible[0]||null,treasury:G.treasury,roadCost:buildCost.road,repairCost:buildCost.repair,parkCost:buildCost.park,roads:G.tiles.filter(x=>x===1).length,buildings:G.buildings.length,construction:G.construction};},
 counts:()=>({roads:G.tiles.filter(x=>x===1).length,buildings:G.buildings.length,construction:G.construction,treasury:G.treasury}),
};
'''

class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def utc():return datetime.now(timezone.utc).isoformat()
def stats(values):
 a=sorted(values)
 def p(q):return a[min(len(a)-1,int(len(a)*q))] if a else 0
 return {'n':len(a),'p50Ms':p(.5),'p95Ms':p(.95),'p99Ms':p(.99),'maxMs':max(a,default=0)}

server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')))
threading.Thread(target=server.serve_forever,daemon=True).start()
result={'status':'starting','commit':BASE_COMMIT,'sourceSha256':SOURCE_SHA,'fixture':'generated terminal city; 128 atlas, embedded day41681, 778 residents, 797 buildings, 81 firms, 48 contracted/total routes, 21 owned districts','fixtureSha256':FIXTURE_SHA,'fixtureGzipSha256':hashlib.sha256(FIXTURE_GZ).hexdigest(),'hostChromium':True,'physicalAndroid':False,'requestedMinutes':MINUTES,'startedUTC':utc(),'samples':[],'operations':[],'errors':[],'notes':['Ordinary growth, private entry, freight and transit simulation remain enabled; route closures and firm changes are allowed to occur naturally.','No treasury injection or simulation-step fast-forward.','Touch is trusted emulated Chromium input; touch-to-next-RAF is not photon latency.','Heap numbers are V8 heap only and exclude native canvas/audio/GPU allocations.']}
def persist():
 t=OUT/'session.tmp';t.write_text(json.dumps(result,indent=2)+'\n');t.replace(OUT/'session.json')
persist()

with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':844,'height':390},has_touch=True);page.set_default_timeout(20000)
 page.on('pageerror',lambda e:result['errors'].append(str(e)))
 page.on('console',lambda m:result['errors'].append(m.text) if m.type=='error' else None)
 page.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=SOURCE.replace('// SOURCE: 99-instrumentation.js',PROBE+'\n// SOURCE: 99-instrumentation.js')))
 try:
  page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
  page.locator('#newTown').click();page.locator('#pause').click()
  assert page.evaluate('s=>__townArchive.restore(s)',ARCHIVE)
  page.locator('#panelClose').click()
  # The fixture contains 21 purchased parcels and real late-game operating state.
  initial=page.evaluate('__ordinary.state()');initialAudit=page.evaluate('__ordinary.audit()');initial['audit']=initialAudit
  assert initialAudit['valid']['ok'] and initialAudit['goodsError']<.001 and initial['deeds']==21 and initial['grid']==128 and initial['routes']==48,initial
  page.locator('#speedRange').fill('4') #16x; normal slider interaction, no accumulator carryover.
  assert page.evaluate('__ordinary.state().requested')==16
  park=page.evaluate('__ordinary.inspect("park")')
  if park['site'] and park['treasury']>=park['parkCost']:
   page.locator('[data-panel=construction]').click();page.locator('[data-build=park]').click();page.mouse.click(park['site']['sx'],park['site']['sy']);placed=page.evaluate('__ordinary.counts()')
   result['operations'].append({'kind':'place-park-through-public-works','seconds':0,'site':park['site'],'before':{'buildings':park['buildings'],'construction':park['construction'],'treasury':park['treasury']},'after':placed})
   assert placed['buildings']==park['buildings']+1 and placed['construction']==park['construction']+1,('UI park action did not place',park,placed)
   roadBuildDone=True
   page.keyboard.press('Escape')
  else:
   result['operations'].append({'kind':'park-unavailable-at-start','seconds':0,'siteCount':park['count'],'treasury':park['treasury']})
  # Unlock browser audio through ordinary user input; no mocked or injected track.
  page.locator('#mapStatusToggle').tap();page.locator('#pause').click()
  cdp=page.context.new_cdp_session(page);cdp.send('Performance.enable');cdp.send('HeapProfiler.collectGarbage')
  result['initialState']=initial;result['initialHeapAfterGC']=cdp.send('Runtime.getHeapUsage');result['startedLiveUTC']=utc();result['status']='running';persist();page.evaluate('__ordinary.start()')
  began=time.monotonic();lastSample=0;lastSave=120;lastReport=60;lastPan=35;lastRoad=180;lastRepair=360;lastSquareTry=30;lastPause=-600;pauseUntil=0;lastAccounting=0;lastSourceCheck=0;lastState=initial
  reportNames=['overview','economy','community','businesses','treasury','agenda','citizens','construction','journal']
  currentPanel=False;roadBuildDone=False;repairDone=False;lastPhase=None;opsCount=0
  print('START',result['startedLiveUTC'],'durationSeconds',DURATION,'commit',BASE_COMMIT,'sourceSha256',SOURCE_SHA,flush=True)
  while time.monotonic()-began<DURATION:
   page.wait_for_timeout(1000);elapsed=time.monotonic()-began
   if elapsed-lastSourceCheck>=300:
    assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==SOURCE_SHA,'Production bundle changed during soak';lastSourceCheck=elapsed
   # Six-minute16x base cycle plus one-minute1x/8x/32x/64x bursts.
   phase=elapsed%600
   requested=1 if 360<=phase<420 else 8 if 420<=phase<480 else 32 if 480<=phase<540 else 64 if phase>=540 else 16
   if requested!=lastPhase:
    index=[1,2,4,8,16,32,64].index(requested)
    page.locator('#speedRange').fill(str(index));lastPhase=requested
    result['operations'].append({'kind':'speed-change','seconds':round(elapsed,1),'requested':requested,'actualLabel':page.locator('#effectiveSpeed').inner_text()})
   # Short pause late in each64x burst tests live interruption with queued time.
   if pauseUntil==0 and phase>=570 and phase<578 and elapsed-lastPause>=540:
    page.locator('#pause').click();pauseUntil=elapsed+8;lastPause=elapsed
    result['operations'].append({'kind':'pause-start','seconds':round(elapsed,1),'state':page.evaluate('__ordinary.state()')})
   if pauseUntil and elapsed>=pauseUntil:
    page.locator('#pause').click();pauseUntil=0;result['operations'].append({'kind':'pause-end','seconds':round(elapsed,1),'state':page.evaluate('__ordinary.state()')})
   # Pan map with real pointer drag, including during normal running.
   if elapsed>=lastPan and not page.locator('#pause').get_attribute('aria-label')=='Resume simulation':
    box=page.locator('#view').bounding_box();x=box['x']+box['width']*.72;y=box['y']+box['height']*.58
    page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-38,y+24,steps=5);page.mouse.up()
    result['operations'].append({'kind':'map-pan','seconds':round(elapsed,1)});lastPan+=60
   # Read actual reports through the navigation controls, then close them.
   if elapsed>=lastReport and not pauseUntil:
    if currentPanel:page.locator('#panelClose').click();currentPanel=False
    name=reportNames[(opsCount//3)%len(reportNames)]
    page.locator('[data-panel='+name+']').click();currentPanel=True
    error='Panel error' in page.locator('#panelBody').inner_text()
    result['operations'].append({'kind':'report','name':name,'seconds':round(elapsed,1),'error':error})
    if error:raise RuntimeError('Report panel rendering error: '+name)
    page.locator('#panelClose').click();currentPanel=False;lastReport+=60;opsCount+=1
   # Persist with the game's explicit Save button through the normal options UI.
   if elapsed>=lastSave and not pauseUntil:
    if currentPanel:page.locator('#panelClose').click();currentPanel=False
    page.locator('[data-panel=settings]').click();t=time.monotonic();page.locator('#saveNow').click();page.wait_for_function('!document.querySelector("#saveNow").disabled',timeout=30000)
    result['operations'].append({'kind':'user-save','seconds':round(elapsed,1),'completionMs':(time.monotonic()-t)*1000})
    page.locator('#panelClose').click();lastSave+=120
   # Use public works UI to construct one square and extend real roads. No funds are added.
   if not roadBuildDone and elapsed>=lastSquareTry:
    candidate=page.evaluate('__ordinary.inspect("park")')
    result['operations'].append({'kind':'park-site-survey','seconds':round(elapsed,1),'candidate':candidate})
    if candidate['site']:
     page.locator('[data-panel=construction]').click();page.locator('[data-build=park]').click();page.mouse.click(candidate['site']['sx'],candidate['site']['sy'])
     after=page.evaluate('__ordinary.counts()');result['operations'].append({'kind':'place-park','seconds':round(elapsed,1),'after':after,'candidate':candidate['site']});roadBuildDone=True
     if currentPanel:currentPanel=False
    lastSquareTry+=600
   if not repairDone and elapsed>=180:
    candidate=page.evaluate('__ordinary.inspect("repair")')
    if candidate['site'] and candidate['treasury']>=candidate['repairCost']:
     page.locator('[data-panel=construction]').click();page.locator('[data-build=repair]').click();before=page.evaluate('__ordinary.counts()');page.mouse.click(candidate['site']['sx'],candidate['site']['sy'])
     result['operations'].append({'kind':'road-repair-control','seconds':round(elapsed,1),'before':before,'after':page.evaluate('__ordinary.counts()'),'site':candidate['site']});page.keyboard.press('Escape');repairDone=True
    lastRepair+=600
   if elapsed>=lastRoad and not pauseUntil:
    candidate=page.evaluate('__ordinary.inspect("road")')
    if candidate['site'] and candidate['treasury']>=candidate['roadCost']:
     if currentPanel:page.locator('#panelClose').click();currentPanel=False
     page.locator('[data-panel=construction]').click();page.locator('[data-build=road]').click();before=page.evaluate('__ordinary.counts()');page.mouse.click(candidate['site']['sx'],candidate['site']['sy'])
     after=page.evaluate('__ordinary.counts()');result['operations'].append({'kind':'road-construction-control','seconds':round(elapsed,1),'before':before,'after':after,'site':candidate['site']});page.keyboard.press('Escape')
    else:result['operations'].append({'kind':'road-construction-unavailable','seconds':round(elapsed,1),'treasury':candidate['treasury'],'siteCount':candidate['count']})
    lastRoad+=600
   if elapsed>=lastSample+30:
    raw=page.evaluate('__ordinary.pull()');state=page.evaluate('__ordinary.state()');heap=cdp.send('Runtime.getHeapUsage');windowSeconds=elapsed-lastSample;sample={'utc':utc(),'seconds':round(elapsed,1),'windowSeconds':windowSeconds,'day':state['day'],'days':state['day']-lastState['day'],'actualRate':(state['day']-lastState['day'])*1.65/windowSeconds,'requested':state['requested'],'backlogDays':state['backlog'],'zoom':round(state['zoom'],3),'raf':stats(raw['raf']),'touchDelivery':stats([x['handlerMs'] for x in raw['input']]),'touchNextRAF':stats([x['nextRAFMs'] for x in raw['input']]),'touchCount':len(raw['input']),'longtaskCount':raw['longtasks'],'maxLongtaskMs':raw['maxLongtask'],'tickRecent':stats(state['tickRecent'][-180:]),'heap':heap,'stateBrief':{k:state[k] for k in ['population','buildings','firms','treasury','operating','routes','growth','privateEntry','paused','pending','saveOrder','savePending','saveRunning','musicTrack','musicError','atlasBytes','traffic']}}
    if elapsed-lastAccounting>=300:
     accounting=page.evaluate('__ordinary.audit()');sample['accounting']={**accounting,'totalMoney':state['total'],'totalMoneyDrift':state['total']-initial['total']};lastAccounting=elapsed
     assert accounting['valid']['ok'] and accounting['goodsError']<.001,(elapsed,accounting)
     assert abs(state['total']-initial['total'])<.1,('Money ledger drift',elapsed,state['total']-initial['total'])
     assert state['deeds']==21 and state['grid']==128 and state['routes']==48 and state['growth'] and state['privateEntry'],state
     assert state['atlasBytes']<=48*1024*1024 and state['atlas']<=600 and state['serviceCaches']<=2 and state['traffic']<=80 and state['history']<=240 and state['events']<=160 and state['transactions']<=800 and state['observations']<=1200 and len(state['musicDecks'])<=2,state
     assert not state['musicError'] and all(not d['error'] for d in state['musicDecks']),state['musicDecks']
    result['samples'].append(sample);lastState=state;lastSample=elapsed
    result['latestSampleUTC']=utc();persist()
    print('SAMPLE',round(elapsed), 'day',state['day'],'pop',state['population'],'requested',state['requested'],'actual',round(sample['actualRate'],1),'backlog',round(state['backlog'],1),'rafP99',round(sample['raf']['p99Ms'],1),'touchP99',round(sample['touchNextRAF']['p99Ms'],1),'heapMiB',round(heap['usedSize']/1048576,1),'ops',len(result['operations']),flush=True)
   if not result['samples'] and not initialAudit['valid']['ok']:raise RuntimeError('Invalid startup town')
  if currentPanel:page.locator('#panelClose').click()
  page.locator('#pause').click();page.evaluate('__ordinary.stop()');page.locator('[data-panel=settings]').click();page.locator('#saveNow').click();page.wait_for_function('!document.querySelector("#saveNow").disabled',timeout=30000);page.locator('#panelClose').click()
  cdp.send('HeapProfiler.collectGarbage');result['finalHeapAfterGC']=cdp.send('Runtime.getHeapUsage');result['finalState']=page.evaluate('__ordinary.state()');result['finalAccounting']=page.evaluate('__ordinary.audit()');result['finishedUTC']=utc();result['elapsedSeconds']=time.monotonic()-began;result['status']='completed';result['errors']=result['errors'][-100:]
  assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==SOURCE_SHA
  final=result['finalState'];audit=result['finalAccounting'];assert audit['valid']['ok'] and audit['goodsError']<.001 and abs(final['total']-initial['total'])<.1 and not result['errors'],(final,audit,result['errors'])
  persist();print('COMPLETE',result['finishedUTC'],'elapsed',round(result['elapsedSeconds'],1),'samples',len(result['samples']),'finalDay',final['day'],'source',SOURCE_SHA,flush=True)
 except BaseException as exc:
  result['status']='failed';result['failure']=str(exc);result['traceback']=traceback.format_exc();result['finishedUTC']=utc()
  try:result['failureState']=page.evaluate('__ordinary.state()')
  except Exception as sub:result['failureStateError']=str(sub)
  persist();print('FAILED',result['traceback'],flush=True);raise
 finally:
  browser.close();server.shutdown();server.server_close()
