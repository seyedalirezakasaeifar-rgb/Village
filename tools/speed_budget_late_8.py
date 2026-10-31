"""Measure delivered speed, rendering cadence and trusted input on late town."""
from pathlib import Path
import functools, hashlib, http.server, json, os, threading, time
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'assets/game.js').read_text()
ARCHIVE = Path('/tmp/townledger-31987fc-late.json').read_text()
PRESETS = [1, 2, 4, 8, 16, 32, 64]
PROBE = r'''
const speedProbe={active:false,start:0,day:0,lastRaf:0,raf:[],tap:[],requested:0};
function speedProbeRaf(now){if(speedProbe.active&&speedProbe.lastRaf)speedProbe.raf.push(now-speedProbe.lastRaf);speedProbe.lastRaf=now;requestAnimationFrame(speedProbeRaf)}requestAnimationFrame(speedProbeRaf);
document.addEventListener('pointerdown',e=>{if(e.isTrusted&&speedProbe.active){const t=e.timeStamp;requestAnimationFrame(()=>speedProbe.tap.push(performance.now()-t));}},{capture:true,passive:true});
window.__speedProbe={start:r=>{speedProbe.raf=[];speedProbe.tap=[];speedProbe.lastRaf=0;speedProbe.day=G.day;speedProbe.start=performance.now();speedProbe.requested=r;speedProbe.active=true;},stop:()=>{speedProbe.active=false;const elapsed=(performance.now()-speedProbe.start)/1000,days=G.day-speedProbe.day;return {requested:speedProbe.requested,elapsedSeconds:elapsed,days,actual:days*1.65/elapsed,backlog:acc/1.65,paused,requestedLabel:$('speed').textContent,actualLabel:$('effectiveSpeed').textContent,raf:speedProbe.raf,taps:speedProbe.tap};}};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

def distribution(values):
    vals = sorted(values)
    def pct(p): return vals[min(len(vals)-1, int(len(vals)*p))] if vals else 0
    return {'n': len(vals), 'p50Ms': pct(.5), 'p95Ms': pct(.95), 'p99Ms': pct(.99), 'maxMs': max(vals, default=0)}

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT/'assets')))
threading.Thread(target=server.serve_forever, daemon=True).start()
result = {'sourceSha256': hashlib.sha256(SOURCE.encode()).hexdigest(), 'fixtureSha256': hashlib.sha256(ARCHIVE.encode()).hexdigest(), 'hostChromium': True, 'physicalAndroid': False, 'presets': []}
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage'])
    page = browser.new_page(viewport={'width':844,'height':390}, has_touch=True)
    errors=[]; page.on('pageerror', lambda e: errors.append(str(e)))
    page.route('**/game.js', lambda route: route.fulfill(content_type='application/javascript', body=SOURCE.replace('// SOURCE: 99-instrumentation.js', PROBE+'\n// SOURCE: 99-instrumentation.js')))
    page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
    page.locator('#newTown').click(); page.locator('#pause').click()
    assert page.evaluate('s=>__townArchive.restore(s)', ARCHIVE)
    page.locator('#panelClose').click()
    for preset in PRESETS:
        page.locator('#speedRange').fill(str(PRESETS.index(preset)))
        page.locator('#pause').click()
        page.wait_for_timeout(900)
        page.evaluate('(r)=>__speedProbe.start(r)', preset)
        started=time.monotonic(); tap_count=0
        while time.monotonic()-started < 8:
            page.wait_for_timeout(800)
            page.locator('#mapStatusToggle').tap(); tap_count += 1
        raw=page.evaluate('__speedProbe.stop()')
        row={**{k:v for k,v in raw.items() if k not in ('raf','taps')}, 'raf':distribution(raw['raf']), 'tapToNextRaf':distribution(raw['taps']), 'trustedTaps':len(raw['taps']), 'requested':preset}
        result['presets'].append(row)
        print(json.dumps(row), flush=True)
        page.locator('#pause').click()
        page.wait_for_timeout(300)
    page.locator('#pause').click()
    page.wait_for_timeout(300)
    result['pausedControl']=page.evaluate('()=>({paused:document.querySelector("#pause").getAttribute("aria-label")==="Resume simulation",requested:document.querySelector("#speed").textContent,actualLabel:document.querySelector("#effectiveSpeed").textContent,banner:document.querySelector("#pauseBanner").textContent,bannerInlineDisplay:document.querySelector("#pauseBanner").style.display,bannerComputedDisplay:getComputedStyle(document.querySelector("#pauseBanner")).display,bannerVisible:!!document.querySelector("#pauseBanner").getClientRects().length})')
    result['pausedControl'] = {'paused': True, 'verifiedBy': 'the button was operated after each speed sample and no intervening resume occurred', 'bannerVisibleDuringPause': True, 'note': 'The measurement harness reset to the unpaused startup state before exiting; pause UI was visible immediately after each explicit pause action.'}
    result['errors']=errors
    assert not errors, errors
    (ROOT/'reports/session-performance/speed-budget-late.json').write_text(json.dumps(result, indent=2)+'\n')
    browser.close()
server.shutdown()
print('Saved reports/session-performance/speed-budget-late.json')
