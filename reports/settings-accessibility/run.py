import threading,json,hashlib
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
R=Path('/workspace/accessibility-audit');O=R/'reports/settings-accessibility';O.mkdir(parents=True,exist_ok=True)
class H(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(H,directory=str(R/'assets')));threading.Thread(target=s.serve_forever,daemon=True).start();src=(R/'assets/game.js').read_text();report={'source_sha256':hashlib.sha256(src.encode()).hexdigest(),'viewport':[360,640],'checks':{}}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':360,'height':640});p.route('**/game.js',lambda r:r.fulfill(body=src.replace('// SOURCE: 99-instrumentation.js','window.__settingsEval=s=>eval(s);\n// SOURCE: 99-instrumentation.js'),content_type='application/javascript'));p.goto(f'http://127.0.0.1:{s.server_port}/index.html')
 def ev(x):return p.evaluate('(s)=>__settingsEval(s)',x)
 def settings():p.locator('[data-panel=settings]').click()
 p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();settings();p.wait_for_timeout(500)
 p.locator('#musicToggle').click();p.locator('#soundToggle').click();p.locator('[data-option=reducedMotion]').click();p.locator('[data-option=largeText]').click();p.locator('[data-preference=quality]').select_option('low');p.locator('[data-option=traffic]').click();p.locator('[data-option=effects]').click();p.locator('[data-option=decor]').click();p.locator('#saveNow').click();p.reload();p.locator('#continue').click();settings()
 def state():return ev('({musicEnabled,soundEnabled,options:{...gameOptions},largeClass:document.body.classList.contains("large-text"),music:musicDecks.map(d=>({paused:d.audio.paused,gain:d.gain,volume:d.audio.volume})),ambient:ambient?{paused:ambient.paused,volume:ambient.volume}:null,effects:Object.values(audioCache).map(a=>({paused:a.paused,volume:a.volume})),budget:visualDetailBudget()})')
 a=state();assert not a['musicEnabled'] and not a['soundEnabled'];assert all(x['paused'] for x in a['music']+a['effects']);assert not a['ambient'] or a['ambient']['paused'];assert a['options']['reducedMotion'] and a['options']['largeText'] and a['largeClass'];assert a['options']['quality']=='low';assert not any(a['options'][k] for k in ['traffic','effects','decor']);report['checks']['reload']=a
 ev('__townArchive.suspend()');ev('__townArchive.resume()');p.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));Object.defineProperty(document,'hidden',{configurable:true,value:false});document.dispatchEvent(new Event('visibilitychange'))");a=state();assert not a['musicEnabled'] and not a['soundEnabled'];assert all(x['paused'] for x in a['music']+a['effects']);assert not a['ambient'] or a['ambient']['paused'];report['checks']['resumeMute']=a
 # Verify reduced motion freezes the actual presentation clock while simulation runs.
 ev('paused=false');before=ev('frameClock');p.wait_for_timeout(500);after=ev('frameClock');assert before==after;ev('paused=true');report['checks']['reducedMotionClock']={'before':before,'after':after}
 p.locator('#musicToggle').scroll_into_view_if_needed();p.locator('#musicToggle').focus();p.keyboard.press('Tab');report['checks']['keyboardNext']=p.evaluate('document.activeElement.id');assert report['checks']['keyboardNext']=='musicNext'
 clips=[]
 for sel in ['#musicToggle','#musicNext','#musicVolume','#musicMood','[data-option=reducedMotion]','[data-option=largeText]']:
  p.locator(sel).scroll_into_view_if_needed();box=p.locator(sel).bounding_box();clips.append({'control':sel,'box':box,'horizontalInside':box['x']>=0 and box['x']+box['width']<=361})
 assert all(x['horizontalInside'] for x in clips);report['checks']['controlBounds']=clips;report['checks']['horizontalOverflow']=p.evaluate('document.documentElement.scrollWidth>innerWidth');assert not report['checks']['horizontalOverflow'];p.locator('#musicToggle').scroll_into_view_if_needed();p.screenshot(path=str(O/'settings-360-large.png'));report['status']='passed';b.close()
s.shutdown();(O/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
