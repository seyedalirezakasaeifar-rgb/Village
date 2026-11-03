"""Paired actual synchronous UI phase timings; no worker/64x speed guarantee."""
from pathlib import Path
import sys,gzip,subprocess,json,hashlib,functools,http.server,threading
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];base=subprocess.check_output(['git','show','87811c5:assets/game.js'],text=True);fixed=(R/'assets/game.js').read_text();archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode();out=R/'reports/sync-header-save';out.mkdir(exist_ok=True,parents=True)
hook=r'''let phaseOn=false;const phaseRows={};for(const name of ['updateHeader','persistSnapshot','tick','draw','renderPanel']){const fn=eval(name);eval(name+'=function(...args){if(!phaseOn)return fn.apply(this,args);const t=performance.now();try{return fn.apply(this,args);}finally{(phaseRows[name]||(phaseRows[name]=[])).push(performance.now()-t);}}');}window.syncPhases={begin:()=>{stopGameAudio();musicEnabled=false;phaseOn=true;return {day:G.day,population:G.stats.population,total:totalMoney()};},end:()=>{phaseOn=false;return {day:G.day,population:G.stats.population,total:totalMoney(),valid:validateTown(),goodsError:Math.max(...goodsBalance().map(x=>Math.abs(x.error))),rows:phaseRows};}};'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(R/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();rows=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for repeat in range(2):
  for variant,source in [('base',base),('candidate',fixed)]:
   p=b.new_page(viewport={'width':1000,'height':740});p.route('**/game.js',lambda r:r.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'),content_type='application/javascript'));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('a=>__townArchive.restore(a)',archive);p.keyboard.press('Escape');p.locator('#speedRange').fill('6');initial=p.evaluate('syncPhases.begin()');p.locator('#pause').click()
   for i in range(6):
    p.wait_for_timeout(500);p.mouse.move(400,330);p.mouse.down();p.mouse.move(440,350,steps=2);p.mouse.up()
    if i==2:p.locator('[data-panel=economy]').click()
   p.locator('#pause').click();p.locator('[data-panel=settings]').click()
   for i in range(3):p.locator('#saveNow').click();p.wait_for_function('!document.querySelector("#saveNow").disabled')
   final=p.evaluate('syncPhases.end()');assert final['valid']['ok'] and abs(final['total']-initial['total'])<.001 and final['goodsError']<.001
   final['rows']={k:{'calls':len(a),'totalMs':sum(a),'meanMs':sum(a)/len(a),'maxMs':max(a)} for k,a in final['rows'].items()};rows.append({'repeat':repeat,'variant':variant,'sourceSHA256':hashlib.sha256(source.encode()).hexdigest(),'initial':initial,'final':final});print(json.dumps(rows[-1]),flush=True);p.close()
 b.close()
server.shutdown();(out/'real-ui-phases.json').write_text(json.dumps({'hostDiagnostic':True,'physicalDevice':False,'audioStopped':True,'workerEnabled':False,'fixtureSHA256':hashlib.sha256(archive.encode()).hexdigest(),'actions':'real pans, Economy, Pause, Options and three actual Save clicks','rows':rows},indent=2)+'\n')
