"""Read-only production control catalogue and isolated presentation-preference audit."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,hashlib,sys,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from playwright.sync_api import sync_playwright
R=ROOT;out=R/'reports/request-coverage-audit';out.mkdir(exist_ok=True,parents=True);source=(R/'assets/game.js').read_text()
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(R/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
probe="window.__coverage={options:()=>({...gameOptions}),audio:()=>({enabled:musicEnabled,volume:musicVolume,mood:musicMood,track:musicTrack,status:musicStatus(),decks:musicDecks.map(d=>({paused:d.audio.paused,time:d.audio.currentTime,src:d.audio.currentSrc}))}),render:()=>({context:ctx.constructor.name,zoom:cam.zoom,visualBudget:visualDetailBudget(),workerEndpoint:!!window.__workerArchiveAsync}),model:()=>({day:G.day,total:totalMoney(),population:G.stats.population,privateServices:G.firms.filter(f=>f.privateService&&!f.closed).map(f=>f.kind),transitRoutes:G.transit?.routes?.length})};"
result={'localCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'panels':[],'errors':[]}
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:result['errors'].append(str(e)));p.route('**/game.js',lambda route:route.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'),content_type='application/javascript'));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42)");result['model']=p.evaluate('__coverage.model()');result['map']=p.evaluate('__coverage.render()');p.locator('#panelClose').click();p.screenshot(path=str(out/'current-production-map.png'))
 for panel in ['overview','economy','policies','community','construction','agenda','treasury','banking','businesses','citizens','journal','settings']:
  p.locator('[data-panel="'+panel+'"]').click();
  for _ in range(2):
   for summary in p.locator('#panelBody details>summary').all():
    if summary.is_visible()and not summary.evaluate('e=>e.parentElement.open'):summary.click()
  result['panels'].append({'panel':panel,'title':p.locator('#panelTitle').inner_text(),'text':p.locator('#panelBody').inner_text(),'buttons':p.locator('#panelBody button').evaluate_all('(xs)=>xs.map(x=>({text:x.innerText.trim(),id:x.id,disabled:x.disabled,visible:!!(x.offsetWidth||x.offsetHeight)}))'),'inputs':p.locator('#panelBody input,#panelBody select').evaluate_all('(xs)=>xs.map(x=>({id:x.id,type:x.type,value:x.value,preference:x.dataset.preference}))')})
 # Actual settings controls and persistence; restore their initial presentation.
 initial=p.evaluate('__coverage.options()');p.locator('[data-option=reducedMotion]').click();assert p.evaluate('__coverage.options().reducedMotion')!=initial['reducedMotion'];p.locator('[data-preference=quality]').select_option('low');p.locator('[data-preference=fps]').select_option('20');result['settingsChanged']=p.evaluate('__coverage.options()');p.screenshot(path=str(out/'current-settings-controls.png'));p.reload();assert p.evaluate('__coverage.options().quality')=='low'and p.evaluate('__coverage.options().fps')==20;result['settingsPersisted']=True;result['audioAfterReloadBeforeNewGesture']=p.evaluate('__coverage.audio()');result['mapAfterReload']=p.evaluate('__coverage.render()');b.close()
server.shutdown();server.server_close();(out/'actual-controls.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS actual 12-panel controls, settings changes/reload, actual Canvas path; catalogue saved')
