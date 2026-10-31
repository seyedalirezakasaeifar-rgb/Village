"""Quantify explicit interruption/overflow on a real terminal monthly day."""
from pathlib import Path
import sys,ast,gzip,subprocess,json,hashlib,functools,http.server,threading
ROOT=Path(__file__).resolve().parents[1]
from playwright.sync_api import sync_playwright
late=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)).decode();source=(ROOT/'assets/game.js').read_text()
m=ast.parse((ROOT/'tests/test_cooperative_barriers.py').read_text());probe=next(ast.literal_eval(n.value) for n in m.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
extra=r'''window.__lateBarrier={prepare:()=>{paused=true;hostSuspended=false;for(let i=0;i<18;i++)tick();const before=totalMoney();__coopBarrier.hold('ensureSystems');return {before,workingDay:cooperativeJob.day+1};},run:async kind=>{const t=performance.now();let result,callMs=0,commands=0;if(kind==='export'){result=JSON.parse(__townArchive.export()).day;callMs=performance.now()-t;}else if(kind==='suspend'){const pending=__townArchive.suspend();callMs=performance.now()-t;result=await pending;}else if(kind==='save'||kind==='exit'){const pending=kind==='save'?save():__townArchive.prepareExit();callMs=performance.now()-t;cooperativeHarnessHold=false;cooperativePost();result=await pending;}else{const pending=[];for(let i=0;i<300;i++)pending.push(__cooperativeSimulation.command('controlled settlement '+i,()=>{G.treasury-=.01;G.region+=.01;commands++;}));callMs=performance.now()-t;await Promise.all(pending);}return {kind,callMs,totalMs:performance.now()-t,result,commands,day:G.day,busy:cooperativeDayBusy(),queued:cooperativeCommands.length,total:totalMoney(),valid:validateTown(),barriers:__cooperativeSimulation.samples().barriers};}};'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'fixture_sha256':hashlib.sha256(late.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'rows':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for kind in ['export','suspend','save','exit','overflow']:
  p=b.new_page();p.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n'+extra+'\n// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townTest.load(s)',late);before=p.evaluate('__lateBarrier.prepare()');row=p.evaluate('k=>__lateBarrier.run(k)',kind);assert row['valid']['ok'] and not row['busy'] and not row['queued'] and abs(row['total']-before['before'])<.01,row
  if kind in ['save','exit','suspend']:assert row['result'] is True,row
  if kind=='overflow':assert row['commands']==300,row
  out['rows'].append(row);print(kind,row['callMs'],row['totalMs'],flush=True);p.close()
 b.close()
server.shutdown();(ROOT/'reports/cooperative-late-barriers.json').write_text(json.dumps(out,indent=2));print('PASS actual monthly-day export/suspend/save/exit and300settlements; explicit barrier costs retained')
