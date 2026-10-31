"""Muted/background audio and council feedback use actual control events."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
probe='''window.__stopAudio=stopGameAudio;window.__audioProbe=()=>({enabled:soundEnabled,suspended:hostSuspended,playing:window.__sounds.filter(a=>!a.paused).map(a=>a.src)});window.__choiceProbe=cost=>showCustomEvent('TOWN ARCHIVE','Sound check','No financial action',[{title:'Choose',cost,apply:()=>{}}]);'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html)
 p.add_script_tag(content='''window.__sounds=[];window.Audio=class {constructor(src){this.src=src;this.paused=true;window.__sounds.push(this)}play(){this.paused=false;return Promise.resolve()}pause(){this.paused=true}};''')
 p.add_script_tag(content=source.decode().replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click()
 p.evaluate('__choiceProbe(0)');p.locator('[data-event-choice="0"]').click();r=p.evaluate('__audioProbe()');assert 'sound/click.wav' in r['playing'],r
 p.evaluate('__stopAudio();__choiceProbe(1)');p.locator('[data-event-choice="0"]').click();assert 'sound/coin.wav' in p.evaluate('__audioProbe().playing')
 p.evaluate('__townArchive.suspend()');assert not p.evaluate('__audioProbe().playing');p.locator('[data-panel=settings]').click();assert not p.evaluate('__audioProbe().playing');p.evaluate('__townArchive.resume()');assert p.evaluate('__audioProbe().playing')==['sound/village.wav']
 p.locator('#soundToggle').click();assert p.locator('#soundToggle').get_attribute('aria-pressed')=='false';assert not p.evaluate('__audioProbe().playing');p.locator('#soundToggle').click();assert p.evaluate('__audioProbe().playing')
 p.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>window.__hidden});window.__hidden=true;document.dispatchEvent(new Event('visibilitychange'))");assert not p.evaluate('__audioProbe().playing');p.locator('#saveNow').click();assert not p.evaluate('__audioProbe().playing');p.evaluate("window.__hidden=false;document.dispatchEvent(new Event('visibilitychange'))");assert p.evaluate('__audioProbe().playing')==['sound/village.wav'];assert not errors,errors;b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-integration';out.mkdir(exist_ok=True);(out/'audio.json').write_text(json.dumps({'source_sha256':sha,'mockedAudio':True,'checks':['paid vs free council choice','mute stops effects and ambience','native suspend/resume','hidden document suppresses effects','visible resume ambience only'],'errors':errors},indent=2)+'\n');print('PASS audio lifecycle and paid/free choice feedback (mock Audio, no subjective listening claim)')
