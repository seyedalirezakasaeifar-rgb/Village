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
 isPaused:()=>paused,
 deferredState:()=>({requested:saveAfterCommittedTick,waiters:saveAfterCommittedTickWaiters.length}),
 inbox:()=>G.councilInbox,
};
window.__inTickSavePromises=[];window.__indexedWriteCalls=0;window.__gateIndexedWrite=false;
const __actualSave=save,__actualIndexedWrite=writeIndexedDB,__storageSetItem=Storage.prototype.setItem;
save=function(){const result=__actualSave();if(simulationTickActive)window.__inTickSavePromises.push(result);return result;};
writeIndexedDB=function(envelope,epoch){window.__indexedWriteCalls++;if(window.__gateIndexedWrite)return new Promise(resolve=>{window.__releaseIndexedWrite=()=>Promise.resolve(__actualIndexedWrite(envelope,epoch)).then(resolve,()=>resolve(false));});return __actualIndexedWrite(envelope,epoch);};
window.__dayBoundary.failAfterReview=()=>{const old=brownfieldDay;brownfieldDay=()=>{throw Error('injected after monthly review')};try{tick();return 'tick unexpectedly returned'}catch(e){return e.message}finally{brownfieldDay=old}};
window.__dayBoundary.multiSaveTick=()=>{const old=brownfieldDay;brownfieldDay=()=>{old();save();save()};try{tick()}finally{brownfieldDay=old}return window.__inTickSavePromises.length};
window.__dayBoundary.beginWriteGate=()=>{window.__indexedWriteCalls=0;window.__gateIndexedWrite=true};
window.__dayBoundary.writeStatus=async()=>Promise.race([Promise.all(window.__inTickSavePromises).then(values=>({settled:true,values})),new Promise(resolve=>setTimeout(()=>resolve({settled:false}),50))]);
window.__dayBoundary.releaseWrite=()=>{window.__gateIndexedWrite=false;window.__releaseIndexedWrite?.()};
window.__dayBoundary.inTickResults=()=>Promise.all(window.__inTickSavePromises);
window.__dayBoundary.failStorage=()=>{Storage.prototype.setItem=function(){throw new DOMException('Injected storage failure','QuotaExceededError')};writeIndexedDB=()=>Promise.resolve(false)};
window.__dayBoundary.restoreStorage=()=>{Storage.prototype.setItem=__storageSetItem;writeIndexedDB=__actualIndexedWrite};
window.__dayBoundary.manualSave=()=>save();
'''


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

        # Paused Back/Escape leaves the reviewed household in the inbox and cannot enact it.
        assert page.evaluate('__dayBoundary.isPaused()')
        cash = page.evaluate('__townTest.get().treasury')
        page.locator('[data-panel=agenda]').click()
        page.locator('[data-inbox="0"]').click()
        assert page.locator('#eventDialog').is_visible()
        page.keyboard.press('Escape')
        assert page.locator('#eventDialog').is_hidden()
        assert page.evaluate('__dayBoundary.isPaused()')
        assert page.evaluate('__townTest.get().treasury') == cash
        assert any(e.get('title', '').startswith('A household may leave: ') for e in page.evaluate('__dayBoundary.inbox()'))
        page.locator('[data-inbox="0"]').click()
        page.locator('#eventDefer').click()
        assert page.evaluate('__townTest.get().treasury') == cash and page.evaluate('__dayBoundary.isPaused()')

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

        # Ordinary user-triggered save outside a tick resolves only after the write.
        if not (page.locator('#panel').evaluate('e=>e.classList.contains("show")') and 'active' in (page.locator('[data-panel=settings]').get_attribute('class') or '')):
            page.locator('[data-panel=settings]').click()
        page.locator('#saveNow').click()
        page.wait_for_function("document.querySelector('#toast').textContent.includes('Village saved on this device.')")
        assert page.evaluate('__dayBoundary.persisted().day') == 40

        # A failure after the monthly-review save request must discard the partial day.
        page.evaluate("__townTest.reset('settlement',42);__townTest.step(28);window.__inTickSavePromises=[];window.__indexedWriteCalls=0")
        assert page.evaluate('__dayBoundary.createRisk().assessment.eligible')
        before_fault = page.evaluate('__dayBoundary.persisted().day')
        assert page.evaluate('__dayBoundary.failAfterReview()') == 'injected after monthly review'
        assert page.evaluate('__dayBoundary.inTickResults()') == [False]
        assert page.evaluate('__dayBoundary.persisted().day') == before_fault
        assert page.evaluate('__dayBoundary.deferredState()') == {'requested': False, 'waiters': 0}
        assert page.evaluate('__dayBoundary.manualSave()') is False, 'A later manual save must not bless the partially executed failed day'
        fault_day = page.evaluate('__townTest.get().day')
        page.evaluate('__dayBoundary.commitOneDay()')
        assert page.evaluate('__townTest.get().day') == fault_day, 'A failed day cannot be skipped and then persisted as complete'
        assert page.evaluate('__townArchive.export()') is None, 'A failed partial day cannot be exported as a valid backup'
        assert not page.evaluate('__townArchive.restore("{broken")')
        assert page.evaluate('__dayBoundary.manualSave()') is False, 'Invalid restoration cannot clear the failed-day fence'
        if not (page.locator('#panel').evaluate('e=>e.classList.contains("show")') and 'active' in (page.locator('[data-panel=settings]').get_attribute('class') or '')):
            page.locator('[data-panel=settings]').click()
        page.locator('#saveNow').click()
        page.wait_for_function("document.querySelector('#toast').textContent.includes('Reload the last saved town')")
        page.locator('#backupSave').click()
        assert page.locator('#helpDialog').is_hidden()
        assert page.evaluate('__townArchive.restore(JSON.stringify(__dayBoundary.persisted()))')
        assert page.evaluate('__dayBoundary.manualSave()'), 'Valid committed restoration must permit real persistence again'

        # Three in-tick requests coalesce to one write; no caller sees success
        # until IndexedDB settles, and all callers receive the real result.
        page.evaluate("__townTest.reset('settlement',42);__townTest.step(28);window.__inTickSavePromises=[];window.__indexedWriteCalls=0")
        assert page.evaluate('__dayBoundary.createRisk().assessment.eligible')
        page.evaluate('__dayBoundary.beginWriteGate()')
        assert page.evaluate('__dayBoundary.multiSaveTick()') == 3
        page.wait_for_function('window.__indexedWriteCalls===1')
        assert page.evaluate('__dayBoundary.writeStatus()') == {'settled': False}
        assert page.evaluate('window.__indexedWriteCalls') == 1
        page.evaluate('__dayBoundary.releaseWrite()')
        assert page.evaluate('__dayBoundary.inTickResults()') == [True, True, True]
        assert page.evaluate('window.__indexedWriteCalls') == 1
        assert page.evaluate('__dayBoundary.persisted().history.slice(-1)[0].day') == 30

        # Storage failure resolves deferred and manual saves as failures, keeps
        # the prior durable copy, and does not strand a later retry.
        page.evaluate("__townTest.reset('settlement',42);__townTest.step(28);window.__inTickSavePromises=[];window.__indexedWriteCalls=0;__dayBoundary.failStorage()")
        assert page.evaluate('__dayBoundary.createRisk().assessment.eligible')
        old_durable_day = page.evaluate('__dayBoundary.persisted().day')
        page.evaluate('__dayBoundary.commitOneDay()')
        assert page.evaluate('__dayBoundary.inTickResults()') == [False]
        assert page.evaluate('__dayBoundary.persisted().day') == old_durable_day
        if not (page.locator('#panel').evaluate('e=>e.classList.contains("show")') and 'active' in (page.locator('[data-panel=settings]').get_attribute('class') or '')):
            page.locator('[data-panel=settings]').click()
        page.locator('#saveNow').click()
        page.wait_for_function("document.querySelector('#toast').textContent.includes('Saving failed; export a backup before leaving.')")
        assert 'Village saved on this device.' not in page.locator('#toast').inner_text()
        page.evaluate('__dayBoundary.restoreStorage()')
        assert page.evaluate('__dayBoundary.manualSave()')
        assert page.evaluate('__dayBoundary.persisted().day') == page.evaluate('__townTest.get().day')
        browser.close()
finally:
    server.shutdown()

print('PASS committed day save/cold reload/replay, paused Back/defer, deferred exception, coalesced pending writes, storage failure and outside-tick save')
