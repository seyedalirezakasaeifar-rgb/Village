"""Council monthly review saves only after a complete committed simulation day."""
from pathlib import Path
import functools, hashlib, http.server, json, threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'assets/game.js').read_text()
probe = r'''window.__dayBoundary={
 ready:()=>saveStorePromise.then(()=>saveStoreReady),
 createRisk:()=>{const h=G.households.find(h=>h.people.some(id=>G.people[id]?.age>=16&&G.people[id]?.age<=70));if(!h)throw Error('No eligible household');h.cash=0;h.stress=90;h.worklessness=90;h.income=0;h.incomeTax=0;h.netIncomeTrend=0;h.deposits={};G.day=29;G.month=1;G.year=1;G.recentCouncilEvents=[];return {id:h.id,name:h.name,assessment:migrationEmigrationAssessment(h)};},
 commitOneDay:()=>tick(),
 persisted:()=>{const e=JSON.parse(localStorage.getItem('townledger-v6'));return e&&JSON.parse(e.payload);},
 current:()=>JSON.parse(archivePayload()),
 settledWrites:()=>saveWrites,
 inbox:()=>G.councilInbox,
};'''


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()

try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(viewport={'width': 844, 'height': 390}, has_touch=True)
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.route('**/assets/game.js', lambda route: route.fulfill(content_type='application/javascript', body=source.replace('// SOURCE: 99-instrumentation.js', probe + '\n// SOURCE: 99-instrumentation.js')))
        page.goto('http://127.0.0.1:' + str(server.server_port) + '/assets/index.html')
        page.locator('#townSeed').fill('42')
        page.locator('#newTown').click()
        page.locator('#pause').click()
        assert page.evaluate('__dayBoundary.ready()')
        page.evaluate('__townTest.step(28)')
        case = page.evaluate('__dayBoundary.createRisk()')
        assert case['assessment']['eligible'], case
        page.evaluate('__dayBoundary.commitOneDay()')
        page.evaluate('__dayBoundary.settledWrites()')
        live = page.evaluate('__dayBoundary.current()')
        saved = page.evaluate('__dayBoundary.persisted()')
        assert live['day'] == saved['day'] == 30
        assert live['history'][-1]['day'] == saved['history'][-1]['day'] == 30, (live['history'][-1], saved['history'][-1])
        assert live['observations'][-1]['day'] == saved['observations'][-1]['day'] == 30
        assert live['rngState'] == saved['rngState']
        assert any(e.get('title', '').startswith('A household may leave: ') for e in saved['councilInbox'])

        # A real reload plus Continue must recover the committed boundary, then replay identically.
        page.reload()
        page.locator('#continue').wait_for(state='visible')
        page.locator('#continue').click()
        page.wait_for_function('document.querySelector("#welcome").style.display === "none"')
        assert page.evaluate('__townTest.get().day') == 30
        checkpoint = page.evaluate('__townTest.save()')
        page.evaluate('__townTest.step(10)')
        expected = page.evaluate('__townTest.save()')
        assert page.evaluate('s=>__townTest.load(s)', checkpoint)
        page.evaluate('__townTest.step(10)')
        actual = page.evaluate('__townTest.save()')
        normalize = lambda value: json.dumps({k: v for k, v in json.loads(value).items() if k not in ('trafficState', 'visualState')}, sort_keys=True, separators=(',', ':'))
        if normalize(actual) != normalize(expected):
            a, e = json.loads(actual), json.loads(expected)
            differences = [k for k in sorted(set(a) | set(e)) if a.get(k) != e.get(k) and k not in ('trafficState', 'visualState')]
            detail = {'expected': {k:e.get(k) for k in ('day','scenario','rngState','treasury','councilInbox')}, 'actual': {k:a.get(k) for k in ('day','scenario','rngState','treasury','councilInbox')}}
            raise AssertionError('cold reload from committed day 30 changed deterministic continuation: ' + ', '.join(differences[:20]) + ' ' + json.dumps(detail))
        assert page.evaluate('__townTest.validate().ok') and not errors, errors
        browser.close()
finally:
    server.shutdown()

print('PASS committed day-30 history, observation, RNG and council inbox survive cold reload and exact 10-day replay')
