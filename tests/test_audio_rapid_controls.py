"""Real media/control churn on HTTP origin; no listening or Android claim."""
from pathlib import Path
import functools,hashlib,http.server,json,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];source=(ROOT/'assets/game.js').read_text();errors=[];rows=[]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
probe='window.__stressEval=code=>eval(code);\n'
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',probe+'// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.locator('[data-panel=settings]').click()
 def ev(code):return p.evaluate('(code)=>window.__stressEval(code)',code)
 def playing():p.wait_for_function('__stressEval("musicDecks.some(d=>!d.audio.paused&&d.audio.currentTime>0)")')
 def check(label,muted=False):
  row=ev('({enabled:musicEnabled,volume:musicVolume,error:musicError,decks:musicDecks.map(d=>({paused:d.audio.paused,volume:d.audio.volume,src:d.audio.getAttribute("src")})),fade:!!musicFade})');assert len(row['decks'])<=2,row
  if muted:assert all(d['paused'] or d['volume']==0 for d in row['decks']),row
  rows.append({'label':label,**row})
 playing();p.locator('#soundToggle').click();playing();check('effects-muted-music-independent');p.locator('#soundToggle').click()
 for i in range(12):
  p.locator('#musicNext').click();p.locator('#musicVolume').fill(str((i*17)%101));p.locator('#musicToggle').click();check('mute-'+str(i),True);ev('__townArchive.suspend();__townArchive.resume()');check('muted-resume-'+str(i),True);p.locator('#musicToggle').click()
 p.locator('#musicVolume').fill('0');check('zero-volume',True);ev('__townArchive.suspend();__townArchive.resume()');check('zero-volume-resume',True);p.locator('#musicVolume').fill('45');playing();check('rapid-controls')
 ev('musicDecks[musicDecks.length-1].audio.dispatchEvent(new Event("error"))');assert ev('!!musicError');ev('renderPanel("settings")');p.locator('#musicRetry').click();playing();assert not ev('musicError');check('retry')
 ev('Object.defineProperty(document,"hidden",{configurable:true,get:()=>window.__audioHidden});window.__audioHidden=true;document.dispatchEvent(new Event("visibilitychange"))');check('background',True);ev('window.__audioHidden=false;document.dispatchEvent(new Event("visibilitychange"))');playing()
 saved=ev('__townTest.save()');assert p.evaluate('(text)=>__townArchive.restore(text)',saved);p.locator('[data-panel=settings]').click();playing();check('restore')
 ev('__townTest.reset("settlement",101)');p.locator('[data-panel=settings]').click();playing();check('new-town')
 p.locator('#musicToggle').click();check('final-mute',True);ev('__townArchive.suspend();__townArchive.resume()');check('final-muted-resume',True)
 cdp=p.context.new_cdp_session(p);cdp.send('HeapProfiler.collectGarbage');proto=cdp.send('Runtime.evaluate',{'expression':'HTMLAudioElement.prototype','objectGroup':'rapid-audio'})['result']['objectId'];obj=cdp.send('Runtime.queryObjects',{'prototypeObjectId':proto,'objectGroup':'rapid-audio'})['objects']['objectId'];media=cdp.send('Runtime.callFunctionOn',{'objectId':obj,'functionDeclaration':'function(){return Array.from(this).map(a=>({src:a.getAttribute("src"),paused:a.paused}))}','returnByValue':True})['result']['value'];cdp.send('Runtime.releaseObjectGroup',{'objectGroup':'rapid-audio'});assert len([a for a in media if a['src'] and a['src'].startswith('music/')])<=2,media;assert all(a['paused'] for a in media if a['src'] and a['src'].startswith('music/')),media;assert not errors,errors;b.close()
server.shutdown();out=ROOT/'reports/integration/audio-rapid-8';out.mkdir(parents=True,exist_ok=True);(out/'receipt.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'realBrowserMedia':True,'physicalAndroid':False,'listeningAssessed':False,'rows':rows,'retainedMediaAfterGC':media,'errors':errors},indent=2)+'\n');print('PASS rapid controls, mute/lifecycle, error/retry, restore/new-town and retained streams')
