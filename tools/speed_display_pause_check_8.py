"""Check instant pause, backlog retention and actual-rate label after speed changes."""
from pathlib import Path
import functools,gzip,hashlib,http.server,json,subprocess,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'assets/game.js').read_text()
ARCHIVE=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)).decode()
PROBE=r'''
window.__speedControl={read:()=>({day:G.day,paused,requested:speed,effective:perfStats.effective,requestedLabel:$('speed').textContent,actualLabel:$('effectiveSpeed').textContent,backlog:acc/1.65,pauseAria:$('pause').getAttribute('aria-label'),pauseBanner:getComputedStyle($('pauseBanner')).display!=='none'}),set:i=>{$('speedRange').value=String(i);$('speedRange').dispatchEvent(new Event('input',{bubbles:true}));}};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
result={'sourceSha256':hashlib.sha256(SOURCE.encode()).hexdigest(),'fixtureSha256':hashlib.sha256(ARCHIVE.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':844,'height':390},has_touch=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=SOURCE.replace('// SOURCE: 99-instrumentation.js',PROBE+'\n// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townArchive.restore(s)',ARCHIVE);p.locator('#panelClose').click();p.evaluate('__speedControl.set(6)');p.locator('#pause').click();p.wait_for_timeout(3300);result['beforePause']=p.evaluate('__speedControl.read()');p.locator('#pause').click();result['immediatePause']=p.evaluate('__speedControl.read()');p.wait_for_timeout(1200);result['afterPausedWait']=p.evaluate('__speedControl.read()');result['pausedDayDelta']=result['afterPausedWait']['day']-result['immediatePause']['day'];p.evaluate('__speedControl.set(4)');result['afterRateChangeWhilePaused']=p.evaluate('__speedControl.read()');p.locator('#pause').click();result['labelSamples']=[p.evaluate('__speedControl.read()')]
 for _ in range(12):p.wait_for_timeout(250);result['labelSamples'].append(p.evaluate('__speedControl.read()'))
 result['errors']=errors
 result['labelClearedOnResume']=result['labelSamples'][0]['actualLabel']=='' and result['labelSamples'][0]['effective']==0
 result['actualLabelRecovered']=any(s['actualLabel'].startswith('Actual ') for s in result['labelSamples'][1:])
 assert not errors and result['pausedDayDelta']==0 and result['immediatePause']['backlog']>0 and result['labelClearedOnResume'] and result['actualLabelRecovered'],result
 out=ROOT/'reports/session-performance/speed-display-pause.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));b.close()
server.shutdown()
