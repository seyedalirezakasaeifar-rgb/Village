"""Compare requested speed and pause/input response across three large towns."""
from pathlib import Path
import ast, functools, gzip, hashlib, http.server, json, threading, time
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'assets/game.js').read_text()
PROBE=r'''
const speedProbe={active:false,last:0,raf:[],touch:[],start:0,day:0};
function speedProbeFrame(t){if(speedProbe.active&&speedProbe.last)speedProbe.raf.push(t-speedProbe.last);speedProbe.last=t;requestAnimationFrame(speedProbeFrame)}requestAnimationFrame(speedProbeFrame);
document.addEventListener('pointerdown',e=>{if(e.isTrusted&&speedProbe.active){let sent=e.timeStamp;requestAnimationFrame(()=>speedProbe.touch.push(performance.now()-sent));}},{capture:true,passive:true});
window.__speedProbe={begin:()=>{speedProbe.raf=[];speedProbe.touch=[];speedProbe.last=0;speedProbe.start=performance.now();speedProbe.day=G.day;speedProbe.active=true;},end:()=>{speedProbe.active=false;let ms=performance.now()-speedProbe.start,days=G.day-speedProbe.day;return {ms,days,actual:days*1650/ms,backlog:acc/1.65,raf:speedProbe.raf,touch:speedProbe.touch};},read:()=>({speed,speedText:$('speed').textContent,actualText:$('effectiveSpeed').textContent,actual:perfStats.effective,paused,day:G.day,backlog:acc/1.65,aria:$('pause').getAttribute('aria-label')}),town:()=>({day:G.day,population:G.stats.population,people:G.people.length,buildings:G.buildings.length,firms:G.firms.length,routes:G.transit.routes.length})};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
def summary(values):
 a=sorted(values)
 return {'n':len(a),'p50Ms':a[len(a)//2] if a else 0,'p95Ms':a[min(len(a)-1,int(len(a)*.95))] if a else 0,'p99Ms':a[min(len(a)-1,int(len(a)*.99))] if a else 0,'maxMs':max(a,default=0)}

old=(ROOT/'reports/session-performance/speed-budget-late.json')
old_data=json.loads(old.read_text())
fixture_hash=old_data['fixtureSha256']
fixtures={}
for label,ref in [('baseline-terminal','833afee'),('mid-session','833afee')]:
 raw=gzip.decompress(__import__('subprocess').check_output(['git','show',f'{ref}:tests/fixtures/generated-late-31987fc/{"terminal" if label=="baseline-terminal" else "mid-session"}.json.gz'],cwd=ROOT))
 fixtures[label]=json.loads(raw)
fixtures['regional-grown-420d']=None
story=next(ast.literal_eval(n.value) for n in ast.parse((ROOT/'tests/test_transit_live_performance.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
fixture_code=story.replace('window.__transitLive=', 'window.__transitLive=')
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')))
threading.Thread(target=server.serve_forever,daemon=True).start()
result={'sourceSha256':hashlib.sha256(SOURCE.encode()).hexdigest(),'fixtureSha256':fixture_hash,'hostChromium':True,'physicalAndroid':False,'towns':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for town in ['baseline-terminal','mid-session','regional-grown-420d']:
  p=b.new_page(viewport={'width':844,'height':390},has_touch=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
  injected=PROBE+('\n'+fixture_code if town=='regional-grown-420d' else '')
  p.route('**/game.js',lambda route,request,inject=injected:route.fulfill(content_type='application/javascript',body=SOURCE.replace('// SOURCE: 99-instrumentation.js',inject+'\n// SOURCE: 99-instrumentation.js')))
  p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click()
  if town=='baseline-terminal': assert p.evaluate('s=>__townArchive.restore(s)',gzip.decompress(__import__('subprocess').check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)).decode())
  elif town=='mid-session': assert p.evaluate('s=>__townArchive.restore(s)',gzip.decompress(__import__('subprocess').check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/mid-session.json.gz'],cwd=ROOT)).decode())
  else:
   p.evaluate('__townTest.reset("regional", 99173)');p.evaluate('__townTest.step(420)')
  p.locator('#panelClose').click();town_result={'name':town,'initial':p.evaluate('__speedProbe.town()'),'speeds':[]}
  for requested in [1,16,32,64]:
   p.locator('#speedRange').fill(str([1,2,4,8,16,32,64].index(requested)));p.locator('#pause').click();p.wait_for_timeout(600)
   p.evaluate('__speedProbe.begin()');started=time.monotonic();taps=0
   while time.monotonic()-started<7:
    p.wait_for_timeout(700);p.locator('#mapStatusToggle').tap();taps+=1
   raw=p.evaluate('__speedProbe.end()');view=p.evaluate('__speedProbe.read()')
   row={'requested':requested,'delivered':raw['actual'],'backlogDays':raw['backlog'],'raf':summary(raw['raf']),'tapToNextRaf':summary(raw['touch']),'trustedTapCount':len(raw['touch']),'requestedLabel':view['speedText'],'actualLabel':view['actualText']}
   town_result['speeds'].append(row);print(town,row,flush=True)
   if requested==64:
    p.locator('#pause').click();p.wait_for_timeout(100);before=p.evaluate('__speedProbe.read()');started=time.monotonic();p.wait_for_timeout(700);p.locator('#mapStatusToggle').tap();p.wait_for_timeout(100);after=p.evaluate('__speedProbe.read()');town_result['pauseResponse']={'before':before,'after':after,'dayDelta':after['day']-before['day'],'elapsedMs':(time.monotonic()-started)*1000,'backlogPreservedDays':after['backlog']}
   else:p.locator('#pause').click()
  town_result['errors']=errors;assert not errors,errors;result['towns'].append(town_result);p.close()
 b.close()
server.shutdown()
out=ROOT/'reports/session-performance/speed-budget-multi-town.json';out.write_text(json.dumps(result,indent=2)+'\n');print('Saved',out)
