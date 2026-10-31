import sys,ast,json,hashlib,time,functools,http.server,threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_mobile_rendering import ROOT
from playwright.sync_api import sync_playwright
m=ast.parse((ROOT/'tests/test_v7_live_large_town.py').read_text());large=next(ast.literal_eval(n.value.args[0]) for n in ast.walk(m) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='town' for t in n.targets))
source=(ROOT/'assets/game.js').read_text();probe=(ROOT/'tools/qa_live_network.js').read_text()+(ROOT/'tools/qa_transit_phase_profile.js').read_text()
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for zoom in [.95,.2]:
  p=b.new_page(viewport={'width':844,'height':390});p.route('**/game.js',lambda route:route.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate(large);network=p.evaluate('__liveNetworkBuild()');p.locator('#panelClose').click();p.evaluate('(z)=>__townTest.capture({zoom:z})',zoom);cold=p.evaluate('__transitProfileCold()');p.evaluate('()=>{__transitPhaseProfile={phases:{},slow:[],invalidations:[]};__townTest.perf().ticks.length=0;}');p.locator('#speedRange').fill('6');cdp=p.context.new_cdp_session(p);cdp.send('Profiler.enable');cdp.send('Profiler.start');p.locator('#pause').click()
  raf=p.evaluate('''()=>new Promise(resolve=>{const times=[];let previous=0,start=performance.now();function f(now){if(previous)times.push(now-previous);previous=now;if(now-start<8000)requestAnimationFrame(f);else resolve(times);}requestAnimationFrame(f);})''');p.locator('#pause').click();profile=cdp.send('Profiler.stop')['profile'];nodes={n['id']:n for n in profile['nodes']};counts={}
  for sample,delta in zip(profile['samples'],profile['timeDeltas']):
   n=nodes[sample]['callFrame'];key=n['functionName']+' @'+str(n['lineNumber']+1);counts[key]=counts.get(key,0)+delta
  row={'zoom':zoom,'network':network,'cold':cold,'timings':p.evaluate('__transitPhaseProfile'),'topSelfMs':[(k,round(v/1000,2)) for k,v in sorted(counts.items(),key=lambda v:-v[1])[:35]],'rafP99':sorted(raf)[min(len(raf)-1,int(len(raf)*.99))]};rows.append(row);print(json.dumps({'zoom':zoom,'cold':cold,'phases':row['timings']['phases'],'topSelfMs':row['topSelfMs'],'slow':sorted(row['timings']['slow'],key=lambda r:-r['ms'])[:15]},indent=2),flush=True);p.close()
 b.close()
server.shutdown();(ROOT/'reports'/('transit-combined-profile-after.json' if len(sys.argv)>1 else 'transit-combined-profile-before.json')).write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'rows':rows},indent=2))
