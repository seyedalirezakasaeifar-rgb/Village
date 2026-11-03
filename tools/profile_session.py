"""Bounded whole-session host Chromium profile; no Android performance claim.

Uses the existing 2,000-resident fixture, 48 paid routes and 21 deeds, actual
HTTP-served audio, real RAF, UI interactions and imports. Test probes wrap
functions only in memory; the shipped source remains immutable.
"""
from pathlib import Path
import ast,collections,functools,gzip,hashlib,http.server,json,math,os,threading,time,subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
local_source=(ROOT/'assets/game.js').read_text();ref=os.environ.get('SESSION_REF');source=subprocess.check_output(['git','show',ref+':assets/game.js'],cwd=ROOT,text=True) if ref else local_source;sha=hashlib.sha256(source.encode()).hexdigest()
fixture=next(ast.literal_eval(n.value) for n in ast.parse((ROOT/'tests/test_transit_live_performance.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe=r'''
const sessionSamples={},sessionInput=[];
document.addEventListener('pointerdown',e=>{if(!e.isTrusted)return;const sent=e.timeStamp,handler=performance.now()-sent;requestAnimationFrame(()=>{sessionInput.push({handlerMs:handler,nextFrameMs:performance.now()-sent});if(sessionInput.length>1000)sessionInput.shift();});},{capture:true,passive:true});
function sessionMeasure(name,fn){return function(...args){const start=performance.now();try{return fn.apply(this,args)}finally{const a=sessionSamples[name]||(sessionSamples[name]=[]);a.push(performance.now()-start);if(a.length>10000)a.shift();}}}
// Function bindings are wrapped after all module decorators have run.
for(const name of ['tick','updateHeader','renderPanel','save','archivePayload','persistSnapshot','draw','trafficUpdate','refreshMusic','hydrateSave','recompute','privateServiceInvestmentDay','districtProgrammeDay','urbanEvolutionDay','dailyEconomy'])eval(name+'=sessionMeasure("'+name+'",'+name+')');
window.__session={
 evolve:()=>{G.autoBuild=true;G.policy.privateServices=1;},
 mode:m=>{paused=m==="paused";hostSuspended=m==="suspended";cam.zoom=m==="far"?.23:.85;dirty=true;updateHeader();if(hostSuspended)stopGameAudio();else refreshAmbience();},
 setup:()=>{__transitLive.large();const injection=Math.min(G.region,6000000);G.region-=injection;G.treasury+=injection;let deeds=0;while(deeds<ANNEX_PARCELS.length){const p=ANNEX_PARCELS.find(p=>!G.charter.owned.includes(p.id)&&parcelAdjacent(p));if(!p)break;if(!purchaseParcel(p.id,parcelSurvey(p).price))throw Error('deed rejected');deeds++;}__transitLive.build(48);G.autoBuild=false;G.policy.privateServices=0;G.policy.serviceVoucherBudget=100;for(const kind of ['school','fire']){const b=G.buildings.find(b=>b.kind===kind);if(!b)continue;const f=createFirm(kind,b.x,b.y,true,()=>b);G.region-=f.cash;f.privateService=kind;f.serviceFee=kind==='school'?3:.8;f.wage=36;f.jobs=2;b.title={kind:'firm',id:f.id};}assignJobs();invalidateRoads(false);tick();const f=G.firms.find(f=>f.kind==='grocer');for(const m of OUTSIDE_MARKETS)if(dispatchRegional(f,'food',30,'import',regionalQuote(f,m,'food','import'))>0)break;return {population:G.stats.population,deeds,grid:T,routes:G.transit.routes.length,providers:G.firms.filter(f=>f.privateService).length,cargo:G.regionalTrade.shipments.length,total:totalMoney()};},
 clear:()=>{sessionInput.length=0;for(const a of Object.values(sessionSamples))a.length=0;perfStats.frames.length=0;perfStats.ticks.length=0;},
 state:()=>({day:G.day,total:totalMoney(),valid:validateTown(),goodsError:Math.max(...goodsBalance().map(v=>Math.abs(v.error))),deeds:G.charter.owned.length,routes:G.transit.routes.length,operating:G.transit.routes.filter(r=>r.stats.operating).length,drivers:G.transit.daily.staff,providers:G.firms.filter(f=>f.privateService&&!f.closed).length,providerStaff:G.firms.filter(f=>f.privateService&&!f.closed).reduce((n,f)=>n+f.workers.length,0),privateClients:G.firms.filter(f=>f.privateService&&!f.closed).reduce((n,f)=>n+(f.clientsToday||0),0),cargo:G.regionalTrade.shipments.length,atlas:atlas.size,atlasBytes,serviceCaches:serviceAccessCaches.size,traffic:traffic.length,observations:G.observations.length,loans:G.loans.length,history:G.history.length,events:G.events.length,transactions:G.transactions.length,musicDecks:musicDecks.length,musicTrack,musicError,suspended:hostSuspended,paused,requestedSpeed:speed,backlog:acc/1.65}),
 samples:()=>sessionSamples, input:()=>sessionInput,
 sample:ms=>new Promise(resolve=>{const raf=[],input=[],begin=performance.now(),startedDay=G.day;let previous=0;const timer=setInterval(()=>{const sent=performance.now();setTimeout(()=>input.push(performance.now()-sent),0);},83);function frame(now){if(previous)raf.push(now-previous);previous=now;if(now-begin<ms)requestAnimationFrame(frame);else{clearInterval(timer);resolve({raf,input,elapsed:performance.now()-begin,days:G.day-startedDay});}}requestAnimationFrame(frame);})
};
'''
def stats(a):
 a=sorted(a);return {'count':len(a),'totalMs':sum(a),'medianMs':a[len(a)//2] if a else 0,'p95Ms':a[min(len(a)-1,int(len(a)*.95))] if a else 0,'p99Ms':a[min(len(a)-1,int(len(a)*.99))] if a else 0,'maxMs':max(a) if a else 0}
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
result={'source_sha256':sha,'commit':subprocess.check_output(['git','rev-parse',ref or 'HEAD'],cwd=ROOT,text=True).strip(),'physicalAndroid':False,'hostChromium':True,'input':'trusted emulated touch pointer events','fixture':'synthetic 2000 residents; actual paid 48 routes, 21 deeds, paid cargo and two licensed private firms; treasury funded from existing region','rows':[]}
seconds=int(os.environ.get('SESSION_SECONDS','15'));suffix=os.environ.get('SESSION_LABEL','baseline')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':844,'height':390},has_touch=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+probe+'\n// SOURCE: 99-instrumentation.js')));p.goto('http://127.0.0.1:'+str(server.server_port)+'/index.html');p.locator('#newTown').click();p.locator('#pause').click();result['fixtureState']=p.evaluate('__session.setup()');result['evolving']=os.environ.get('SESSION_EVOLVING')=='1'
 if result['evolving']:p.evaluate('__session.evolve()')
 p.locator('#panelClose').click();initial_archive=p.evaluate('__townTest.save()');p.locator('#speedRange').fill('6');cdp=p.context.new_cdp_session(p);cdp.send('HeapProfiler.collectGarbage');result['initialHeapAfterGC']=cdp.send('Runtime.getHeapUsage')
 for mode in filter(None,os.environ.get('SESSION_MODES','near,far,economy,paused,suspended').split(',')):
  p.evaluate('m=>__session.mode(m)',mode)
  if mode=='economy':p.locator('[data-panel=economy]').click()
  p.wait_for_timeout(1200);p.evaluate('__session.clear()')
  if mode=='near' and os.environ.get('SESSION_CPU')=='1':cdp.send('Profiler.enable');cdp.send('Profiler.start')
  initial=p.evaluate('__session.state()');p.evaluate('ms=>{window.__sampleRun=__session.sample(ms);}',seconds*1000)
  for _ in range(max(1,seconds//2)):
   p.wait_for_timeout(1850);p.locator('#panelTitle' if mode=='economy' else '#mapStatusToggle').tap()
  sample=p.evaluate('window.__sampleRun')
  if mode=='near' and os.environ.get('SESSION_CPU')=='1':
   profile=cdp.send('Profiler.stop')['profile'];nodes={n['id']:n for n in profile['nodes']};totals=collections.Counter()
   for node,delta in zip(profile['samples'],profile['timeDeltas']):totals[node]+=delta/1000
   result['cpuExclusiveTop']=[{'function':nodes[n]['callFrame']['functionName'],'line':nodes[n]['callFrame']['lineNumber']+1,'url':nodes[n]['callFrame']['url'],'ms':v} for n,v in totals.most_common(30)]
   with gzip.open(ROOT/'reports/session-performance'/('cpu-'+suffix+'.cpuprofile.gz'),'wt') as f:json.dump(profile,f)
  trusted_input=p.evaluate('__session.input()');final=p.evaluate('__session.state()');samples=p.evaluate('__session.samples()');ui=[]
  for target in ['citizens','construction','settings']:
   latency=p.evaluate('tab=>{const t=performance.now();document.querySelector("[data-panel="+tab+"]").click();return new Promise(done=>requestAnimationFrame(()=>done(performance.now()-t)));}',target);ui.append({'panel':target,'toNextFrameMs':latency,'error':'Panel error' in p.locator('#panelBody').inner_text()});p.locator('#panelClose').click()
  row={'mode':mode,'seconds':sample['elapsed']/1000,'days':sample['days'],'measuredSpeed':sample['days']*1650/sample['elapsed'],'raf':stats(sample['raf']),'timerInput':stats(sample['input']),'trustedInputHandler':stats([i['handlerMs'] for i in trusted_input]),'trustedInputNextFrame':stats([i['nextFrameMs'] for i in trusted_input]),'components':{k:stats(v) for k,v in samples.items()},'heap':cdp.send('Runtime.getHeapUsage'),'state':final,'ui':ui};result['rows'].append(row);print(mode,'speed',round(row['measuredSpeed'],1),'rafP99',round(row['raf']['p99Ms'],1),'components',[(k,round(v['totalMs'])) for k,v in row['components'].items()],flush=True)
  if mode=='economy' and p.locator('#panel').is_visible():p.locator('#panelClose').click()
  (ROOT/'reports/session-performance'/('profile-'+suffix+'.json')).write_text(json.dumps(result,indent=2)+'\n')
  assert not errors and final['valid']['ok'] and abs(final['total']-result['fixtureState']['total'])<.1 and final['goodsError']<.001,(errors,final)
  if mode in ['paused','suspended']:assert row['days']==0,row
 soak_seconds=int(os.environ.get('SESSION_SOAK_SECONDS','0'));result['soak']=[]
 for index in range(math.ceil(soak_seconds/10)):
  p.evaluate('m=>__session.mode(m)','far' if index%2 else 'near');p.evaluate('__session.clear()');start=p.evaluate('__session.state()');p.evaluate('()=>{window.__sampleRun=__session.sample(10000);}')
  for _ in range(2):p.wait_for_timeout(4000);p.locator('#mapStatusToggle').tap()
  sample=p.evaluate('window.__sampleRun');end=p.evaluate('__session.state()');trusted=p.evaluate('__session.input()');item={'seconds':(index+1)*10,'days':sample['days'],'speed':sample['days']*1650/sample['elapsed'],'raf':stats(sample['raf']),'input':stats([i['nextFrameMs'] for i in trusted]),'state':end,'heap':cdp.send('Runtime.getHeapUsage')}
  assert end['requestedSpeed']==64 and end['valid']['ok'] and abs(end['total']-result['fixtureState']['total'])<.1 and end['goodsError']<.001 and end['atlasBytes']<=48*1024*1024 and end['serviceCaches']<=2 and end['musicDecks']<=2 and end['traffic']<=80 and end['history']<=240 and end['observations']<=1200 and end['events']<=160 and end['transactions']<=800 and end['atlas']<=600,(index,end)
  # Actual UI paths; imports/foundings test interruption and stale cache release.
  if index%3==2:
   p.locator('[data-panel=settings]').click();p.locator('#musicNext').click();p.locator('#saveNow').click();p.wait_for_function('!document.querySelector("#saveNow").disabled');assert 'Panel error' not in p.locator('#panelBody').inner_text();p.locator('#panelClose').click()
  if index%6==5:
   p.evaluate('__session.mode("paused")');before=p.evaluate('__townTest.save()');assert not p.evaluate('s=>__townArchive.restore(s)', '{"version":3}');assert p.evaluate('__townTest.save()')==before
   if index%12==11:p.locator('#newTown').evaluate('b=>b.click()')
   t=time.monotonic();assert p.evaluate('s=>__townArchive.restore(s)',initial_archive);item['replaceMs']=(time.monotonic()-t)*1000;p.evaluate('__session.mode("near")');p.locator('#speedRange').fill('6')
   if p.locator('#panel').is_visible():p.locator('#panelClose').click()
  result['soak'].append(item);(ROOT/'reports/session-performance'/('profile-'+suffix+'.json')).write_text(json.dumps(result,indent=2)+'\n');print('soak',(index+1)*10,'day',end['day'],'heapMiB',round(item['heap']['usedSize']/1048576,1),'speed',round(item['speed'],1),flush=True)
 p.evaluate('__session.mode("paused")');raw=p.evaluate('__townTest.save()');before=p.evaluate('__session.state()');t=time.monotonic();assert p.evaluate('s=>__townTest.load(s)',raw);result['archiveRoundTripMs']=(time.monotonic()-t)*1000;assert abs(p.evaluate('__session.state().total')-before['total'])<.001;p.wait_for_timeout(300);cdp.send('HeapProfiler.collectGarbage');result['finalHeapAfterGC']=cdp.send('Runtime.getHeapUsage');result['errors']=errors;b.close()
server.shutdown();assert (ROOT/'assets/game.js').read_text()==local_source
(ROOT/'reports/session-performance'/('profile-'+suffix+'.json')).write_text(json.dumps(result,indent=2)+'\n');print('PASS bounded source-bound whole-session profile',suffix,flush=True)
