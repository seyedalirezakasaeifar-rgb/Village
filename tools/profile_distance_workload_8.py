"""Bounded source-bound attribution/paired probe of a retained synthetic late town.
Raw town stays in /tmp; reports contain aggregate timing/state only.
"""
from pathlib import Path
import collections,functools,gzip,hashlib,http.server,json,os,subprocess,threading,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
ref=os.environ.get('LATE_SOURCE_REF');source=subprocess.check_output(['git','show',ref+':assets/game.js'],cwd=ROOT,text=True) if ref else (ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest();archive=Path(os.environ.get('LATE_CHECKPOINT','/tmp/townledger-31987fc-late.json')).read_text();checkpoint_sha=hashlib.sha256(archive.encode()).hexdigest();duration=int(os.environ.get('LATE_SECONDS','24'));label=os.environ.get('LATE_LABEL','attribution')
if os.environ.get('LATE_DISTANCE_BASELINE')=='1':
 old=subprocess.check_output(['git','show','cc86311:src/60-renderer.js'],cwd=ROOT,text=True)
 old=old[old.index('function roadDistancesFrom('):old.index('function beginVehicle(')]
 old=old.replace('if(distance){','if(distance){lateBaselineStats.hits++;').replace('const DistanceArray=','lateBaselineStats.builds++;const DistanceArray=')
 old='const lateBaselineStats={hits:0,builds:0};\n'+old
else:old='const lateBaselineStats=null;'
probe=old+r'''
const lateCalls={},lateInput=[],lateTasks=[];let lateRaf=[],latePrevious=0,lateStart=0,lateDay=0,lateOn=false;
for(const name of ['frame','tick','dailyEconomy','privateServiceInvestmentDay','urbanEvolutionDay','assignJobs','recompute','systemsDay','maintainRoads','renderPanel','updateHeader','draw','save','archivePayload','persistSnapshot','readSaveEnvelope','checksum']){const base=eval(name),replacement=function(...args){if(!lateOn)return base.apply(this,args);const t=performance.now();try{return base.apply(this,args)}finally{const a=lateCalls[name]||(lateCalls[name]=[]);if(a.length<20000)a.push(performance.now()-t);}};eval(name+'=replacement');}
new PerformanceObserver(list=>{if(lateOn)for(const e of list.getEntries())lateTasks.push({start:e.startTime,duration:e.duration})}).observe({entryTypes:['longtask']});
document.addEventListener('pointerdown',e=>{if(!e.isTrusted||!lateOn)return;const sent=e.timeStamp,handler=performance.now()-sent;requestAnimationFrame(()=>lateInput.push({handlerMs:handler,nextFrameMs:performance.now()-sent}));},{capture:true,passive:true});
function sampleLate(now){if(lateOn&&latePrevious)lateRaf.push(now-latePrevious);latePrevious=now;requestAnimationFrame(sampleLate)}requestAnimationFrame(sampleLate);
const lateRoadTotals={graphs:0,queries:0,hits:0,builds:0,evictions:0,maxBytes:0};let lateRoadOwner=null;
function lateRoadAccumulate(net){const s=net?.distanceRows?.stats;if(s){for(const k of ['queries','hits','builds','evictions'])lateRoadTotals[k]+=s[k];lateRoadTotals.maxBytes=Math.max(lateRoadTotals.maxBytes,s.maxBytes);}}
const lateOriginalGraph=graph;graph=function(...args){const net=lateOriginalGraph(...args);if(net!==lateRoadOwner){lateRoadAccumulate(lateRoadOwner);lateRoadOwner=net;lateRoadTotals.graphs++;}return net;};
function lateRoadStats(){const copy={...lateRoadTotals};const s=lateRoadOwner?.distanceRows?.stats;if(s){for(const k of ['queries','hits','builds','evictions'])copy[k]+=s[k];copy.maxBytes=Math.max(copy.maxBytes,s.maxBytes);}return {aggregate:copy,baseline:lateBaselineStats,current:{roads:lateRoadOwner?.neighbors.size,compactRows:lateRoadOwner?.distanceRows?.rows.size||0,compactBytes:lateRoadOwner?.distanceRows?.bytes||0,denseRows:lateRoadOwner?.distanceTrees?.size||0}};}
window.__late={
 zoom:z=>{cam.zoom=z;dirty=true},
 begin:()=>{lateRaf=[];latePrevious=0;lateInput.length=0;lateTasks.length=0;for(const a of Object.values(lateCalls))a.length=0;lateStart=performance.now();lateDay=G.day;lateOn=true;},
 end:()=>{lateOn=false;return {seconds:(performance.now()-lateStart)/1000,days:G.day-lateDay,calls:lateCalls,raf:lateRaf,input:lateInput,longtasks:lateTasks}},
 state:()=>({day:G.day,population:G.stats.population,people:G.people.length,households:G.households.length,firms:G.firms.length,buildings:G.buildings.length,total:totalMoney(),valid:validateTown(),goodsError:Math.max(...goodsBalance().map(v=>Math.abs(v.error))),autoBuild:G.autoBuild,privateEntry:G.policy.privateServices,requestedSpeed:speed,routes:G.transit.routes.length,operating:G.transit.routes.filter(r=>r.stats.operating).length,drivers:G.transit.daily.staff,atlasBytes,serviceCaches:serviceAccessCaches.size,backlog:acc/1.65,musicError,musicTrack,musicDecks:musicDecks.length,roadCache:lateRoadStats()})
};
'''
def stats(a):
 a=sorted(a);return {'count':len(a),'totalMs':sum(a),'p50Ms':a[len(a)//2] if a else 0,'p95Ms':a[min(len(a)-1,int(len(a)*.95))] if a else 0,'p99Ms':a[min(len(a)-1,int(len(a)*.99))] if a else 0,'maxMs':max(a) if a else 0}
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
out=ROOT/'reports/integration/adaptive-road-distance-8/late';out.mkdir(parents=True,exist_ok=True);server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();result={'source_sha256':sha,'checkpoint_sha256':checkpoint_sha,'cacheBaseline':os.environ.get('LATE_DISTANCE_BASELINE')=='1','hostChromiumOnly':True,'physicalAndroid':False,'errors':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':844,'height':390},has_touch=True);p.on('pageerror',lambda e:result['errors'].append(str(e)));p.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')));p.goto('http://127.0.0.1:'+str(server.server_port)+'/index.html');p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townArchive.restore(s)',archive);p.locator('#panelClose').click();p.locator('#speedRange').fill('6');p.evaluate('__late.zoom(.85)');p.wait_for_timeout(1500);cdp=p.context.new_cdp_session(p);cdp.send('Performance.enable');cdp.send('HeapProfiler.collectGarbage');result['initialHeapAfterGC']=cdp.send('Runtime.getHeapUsage');result['initial']=p.evaluate('__late.state()');metrics=cdp.send('Performance.getMetrics');p.locator('#pause').click();p.evaluate('__late.begin()')
 if os.environ.get('LATE_CPU')=='1':cdp.send('Profiler.enable');cdp.send('Profiler.start')
 start=time.monotonic();index=0;panels=['economy','community','businesses','treasury'];panel=False
 while time.monotonic()-start<duration:
  p.wait_for_timeout(1500);p.locator('#panelTitle' if panel else '#mapStatusToggle').tap()
  if index%3==1:
   if panel:p.locator('#panelClose').click();panel=False
   else:p.locator('[data-panel='+panels[index//3%len(panels)]+']').click();panel=True
  if index%8==7:
   if panel:p.locator('#panelClose').click();panel=False
   p.locator('[data-panel=settings]').click();p.locator('#saveNow').click();p.wait_for_function('!document.querySelector("#saveNow").disabled');p.locator('#panelClose').click()
  if time.monotonic()-start>duration/2:p.evaluate('__late.zoom(.23)')
  index+=1
 raw=p.evaluate('__late.end()');result['end']=p.evaluate('__late.state()');after=cdp.send('Performance.getMetrics');old={x['name']:x['value'] for x in metrics['metrics']};result['browserMetricDeltas']={x['name']:x['value']-old.get(x['name'],0) for x in after['metrics'] if x['name'].endswith('Duration') or x['name'].endswith('Count')};result['seconds']=raw['seconds'];result['days']=raw['days'];result['actualRate']=raw['days']*1.65/raw['seconds'];result['components']={k:stats(v) for k,v in raw['calls'].items()};result['raf']=stats(raw['raf']);result['touchDelivery']=stats([v['handlerMs'] for v in raw['input']]);result['touchNextRAF']=stats([v['nextFrameMs'] for v in raw['input']]);result['longtasks']=raw['longtasks'];result['heap']=cdp.send('Runtime.getHeapUsage')
 if os.environ.get('LATE_CPU')=='1':
  cpu=cdp.send('Profiler.stop')['profile'];nodes={n['id']:n for n in cpu['nodes']};counts=collections.Counter();inclusive=collections.Counter()
  for node,delta in zip(cpu['samples'],cpu['timeDeltas']):counts[node]+=delta/1000
  result['cpuExclusiveTop']=[{'function':nodes[n]['callFrame']['functionName'],'line':nodes[n]['callFrame']['lineNumber']+1,'url':nodes[n]['callFrame']['url'],'ms':v} for n,v in counts.most_common(50)]
  with gzip.open(out/(label+'.cpuprofile.gz'),'wt') as f:json.dump(cpu,f)
 (out/(label+'.json')).write_text(json.dumps(result,indent=2)+'\n');assert not result['errors'] and result['end']['valid']['ok'] and abs(result['end']['total']-result['initial']['total'])<.1 and result['end']['goodsError']<.001,result;b.close()
server.shutdown();print(json.dumps({k:result[k] for k in ['source_sha256','checkpoint_sha256','actualRate','raf','touchNextRAF','components','browserMetricDeltas']},indent=2))
