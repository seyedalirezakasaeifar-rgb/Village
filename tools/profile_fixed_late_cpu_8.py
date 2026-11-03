"""Two identical 180-day simulation CPU traces; no FPS/input or device claim."""
from pathlib import Path
import collections,functools,gzip,hashlib,http.server,json,subprocess,threading,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];source=(ROOT/'assets/game.js').read_text();archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)).decode();modules={};module=''
for i,line in enumerate(source.splitlines()):
 if line.startswith('// SOURCE: '):module=line[11:]
 modules[i]=module
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();out=ROOT/'reports/integration/fixed-late-cpu-8';out.mkdir(parents=True,exist_ok=True);result={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'checkpoint_sha256':hashlib.sha256(archive.encode()).hexdigest(),'simulationOnly':True,'audioPausedForMeasurement':True,'physicalAndroid':False,'runs':[]}
probe='window.__cpuModel=()=>{const g=JSON.parse(archivePayload());delete g.trafficState;delete g.visualState;const canon=x=>Array.isArray(x)?x.map(canon):x&&typeof x==="object"?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canon(x[k])])):x;return JSON.stringify(canon(g));};window.__cpuMeasure=()=>{stopGameAudio();musicEnabled=false;const start=performance.now();__townTest.step(180);return {ms:performance.now()-start,day:G.day,valid:validateTown(),total:totalMoney(),goodsError:Math.max(...goodsBalance().map(v=>Math.abs(v.error))),rng:rngState};};\n'
with sync_playwright()as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for run in range(2):
  p=browser.new_page();p.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',probe+'// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townArchive.restore(s)',archive);p.keyboard.press('Escape');p.evaluate('__cpuMeasure()');assert p.evaluate('s=>__townArchive.restore(s)',archive);p.keyboard.press('Escape');cdp=p.context.new_cdp_session(p);cdp.send('Profiler.enable');cdp.send('Profiler.start');state=p.evaluate('__cpuMeasure()');profile=cdp.send('Profiler.stop')['profile'];nodes={n['id']:n for n in profile['nodes']};parents={child:n['id']for n in profile['nodes']for child in n.get('children',[])};exclusive=collections.Counter();inclusive=collections.Counter()
  def key(n):
   frame=nodes[n]['callFrame'];line=frame['lineNumber'];return(frame['functionName'],modules.get(line,'')if frame['url'].endswith('game.js')else frame['url'],line+1)
  for n,delta in zip(profile.get('samples',[]),profile.get('timeDeltas',[])):
   ms=delta/1000;exclusive[key(n)]+=ms;seen=set()
   while n in nodes:
    k=key(n)
    if k not in seen:inclusive[k]+=ms;seen.add(k)
    if n not in parents:break
    n=parents[n]
  rows=lambda counter:[{'function':k[0],'module':k[1],'line':k[2],'ms':v}for k,v in counter.most_common(40)]
  state.update(model_sha256=hashlib.sha256(p.evaluate('__cpuModel()').encode()).hexdigest(),exclusive=rows(exclusive),inclusive=rows(inclusive));result['runs'].append(state);assert state['valid']['ok']and state['goodsError']<.001
  with gzip.open(out/f'run-{run}.cpuprofile.gz','wt')as f:json.dump(profile,f)
  p.close();print('PASS fixed late run',run,state['ms'],state['model_sha256'],flush=True)
 browser.close()
server.shutdown();assert result['runs'][0]['model_sha256']==result['runs'][1]['model_sha256'];(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
