"""Source-bound live synchronous dense-town attribution; host diagnostic, not FPS certification."""
from pathlib import Path
import gzip,subprocess,hashlib,json,functools,http.server,threading,collections,os
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];source=Path(os.environ.get('SYNC_SOURCE_FILE',str(R/'assets/game.js'))).read_text();archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=R)).decode();out=R/'reports/sync-final';out.mkdir(exist_ok=True,parents=True)
probe=r'''
let syncOn=false;const syncCalls={};for(const name of ['tick','dailyEconomy','recompute','systemsDay','assignJobs','renderPanel','draw','updateHeader','archivePayload','save','urbanEvolutionDay']){const fn=eval(name);eval(name+'=function(...args){if(!syncOn)return fn.apply(this,args);const t=performance.now();try{return fn.apply(this,args)}finally{(syncCalls[name]||(syncCalls[name]=[])).push(performance.now()-t);}}');}
window.syncProfile={start:n=>{stopGameAudio();musicEnabled=false;pendingEvent=null;speed=n;G.speed=n;acc=0;sampleDays=0;sampleSeconds=0;for(const k of Object.keys(syncCalls))delete syncCalls[k];syncOn=true;paused=false;return {day:G.day,population:G.stats.population,total:totalMoney()};},end:()=>{syncOn=false;paused=true;return {day:G.day,calls:syncCalls,population:G.stats.population,total:totalMoney(),goodsError:Math.max(...goodsBalance().map(x=>Math.abs(x.error))),valid:validateTown(),requested:speed,displayedActual:perfStats.effective,backlog:acc/1.65,pending:pendingEvent?.title||null};}};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(R/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();rows=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for rate in [1,16,64]:
  p=b.new_page(viewport={'width':844,'height':390});p.route('**/game.js',lambda r:r.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',probe+'// SOURCE: 99-instrumentation.js'),content_type='application/javascript'));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('a=>__townArchive.restore(a)',archive);p.keyboard.press('Escape');p.locator('[data-panel=economy]').click();p.locator('#panelTitle').focus();p.wait_for_timeout(500);cdp=p.context.new_cdp_session(p);cdp.send('Profiler.enable');cdp.send('Profiler.start');initial=p.evaluate('n=>syncProfile.start(n)',rate);start=p.evaluate('performance.now()');p.wait_for_timeout(int(os.environ.get('SYNC_PROFILE_MS','8000')));final=p.evaluate('syncProfile.end()');elapsed=p.evaluate('performance.now()')-start;profile=cdp.send('Profiler.stop')['profile'];nodes={n['id']:n for n in profile['nodes']};counts=collections.Counter()
  for n,delta in zip(profile['samples'],profile['timeDeltas']):counts[n]+=delta/1000
  final['calls']={k:{'n':len(v),'totalMs':sum(v),'meanMs':sum(v)/len(v),'maxMs':max(v)} for k,v in final['calls'].items()};row={'rate':rate,'initial':initial,'final':final,'wallMs':elapsed,'deliveredRate':(final['day']-initial['day'])*1650/elapsed,'cpuExclusive':[dict(function=nodes[n]['callFrame']['functionName'],line=nodes[n]['callFrame']['lineNumber']+1,ms=ms) for n,ms in counts.most_common(25)]};rows.append(row);print(json.dumps(row),flush=True);p.close()
 b.close()
server.shutdown();(out/(os.environ.get('SYNC_LABEL','baseline')+'.json')).write_text(json.dumps({'sourceSHA256':hashlib.sha256(source.encode()).hexdigest(),'fixtureSHA256':hashlib.sha256(archive.encode()).hexdigest(),'physicalDevice':False,'audioStopped':True,'panel':'economy','rows':rows},indent=2)+'\n')
