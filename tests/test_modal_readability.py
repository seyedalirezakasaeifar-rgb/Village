"""Phone-size decision controls remain readable and cancelable with large text."""
from pathlib import Path
import hashlib, json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html

OUT = ROOT / 'reports' / 'modal-readability8'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = (ROOT / 'assets' / 'game.js').read_text()
results = []

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
    for width, height in [(568, 320), (390, 844)]:
        page = browser.new_page(viewport={'width': width, 'height': height}, has_touch=True)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content(html)
        page.add_script_tag(content=SOURCE)
        page.locator('#newTown').click()
        page.locator('#pause').click()
        page.locator('[data-panel=settings]').click()
        page.locator('[data-option=largeText]').click()
        assert page.locator('body').evaluate("e=>e.classList.contains('large-text')")

        page.evaluate('__townTest.offerPetition()')
        page.locator('[data-panel=agenda]').click()
        title = page.evaluate('__townTest.inbox()[0].title')
        page.locator('[data-inbox="0"]').click()
        assert page.locator('#eventDialog').is_visible()

        # Layout-only stress: emulate a translated title, long option label and
        # long money figure without changing the underlying council decision.
        page.evaluate('''()=>{
          document.querySelector('#eventTitle').textContent='A lengthy translated council title for a regional employment proposal';
          document.querySelector('#eventText').textContent='The council has received a detailed neighbourhood request. '.repeat(5);
          const first=document.querySelector('#eventChoices button');
          first.querySelector('strong').textContent='Provide a substantially longer translated alternative for the local labour market';
          first.querySelector('small').textContent='Compare an unusually large illustrative amount $9,999,999,999,999,999.99 and its long-term consequences before choosing.';
        }''')

        checks = page.evaluate('''()=>{
          const paper=document.querySelector('.event-paper'),choices=document.querySelector('#eventChoices'),defer=document.querySelector('#eventDefer'),text=document.querySelector('#eventText');
          const p=paper.getBoundingClientRect(),d=defer.getBoundingClientRect(),first=document.querySelector('#eventChoices button').getBoundingClientRect(),copy=document.querySelector('.event-copy');
          const long=document.querySelector('#eventChoices button');
          return {paper:{top:p.top,bottom:p.bottom},defer:{top:d.top,bottom:d.bottom,height:d.height},choices:{scroll:choices.scrollHeight,client:choices.clientHeight},copy:{scroll:copy.scrollHeight,client:copy.clientHeight},firstChoice:{top:first.top,bottom:first.bottom},readingFont:parseFloat(getComputedStyle(text).fontSize),actionFont:parseFloat(getComputedStyle(defer).fontSize),choiceHeight:long.getBoundingClientRect().height,horizontalOverflow:document.documentElement.scrollWidth>innerWidth};
        }''')
        assert checks['defer']['top'] >= checks['paper']['top'] and checks['defer']['bottom'] <= checks['paper']['bottom'] + 1, checks
        assert checks['defer']['height'] >= 48 and checks['readingFont'] >= 15 and checks['actionFont'] >= 15, checks
        assert checks['choices']['client'] >= 112 and checks['choices']['scroll'] > checks['choices']['client'], checks
        assert checks['firstChoice']['top'] >= 0 and checks['firstChoice']['bottom'] <= checks['paper']['bottom'], checks
        assert checks['copy']['client'] > 0 and checks['copy']['scroll'] > checks['copy']['client'], checks
        assert not checks['horizontalOverflow'], checks
        page.screenshot(path=str(OUT / f'decision-large-text-{width}x{height}.png'))

        # The last alternative remains reachable in its own scroll region while
        # Cancel stays visible. Escape and Android Back both defer with no enactment.
        page.locator('#eventChoices button').last.scroll_into_view_if_needed()
        visible = page.evaluate('''()=>{const b=document.querySelector('#eventChoices button:last-child').getBoundingClientRect(),d=document.querySelector('#eventDefer').getBoundingClientRect();return b.top>=0&&b.bottom<=innerHeight&&d.top>=0&&d.bottom<=innerHeight}''')
        assert visible
        before = page.evaluate('__townTest.get()')
        page.keyboard.press('Escape')
        after = page.evaluate('__townTest.get()')
        assert not after['pending'] and after['treasury'] == before['treasury'] and after['policy'] == before['policy']
        assert title in page.evaluate('__townTest.inbox().map(e=>e.title)')

        page.locator('[data-inbox="0"]').click()
        before = page.evaluate('__townTest.get()')
        assert page.evaluate('__townArchive.back()')
        after = page.evaluate('__townTest.get()')
        assert not after['pending'] and after['treasury'] == before['treasury'] and after['policy'] == before['policy']

        # Inspect an actual household. Stress display text only with a long
        # single-word family label and a large valuation before checking the
        # inspector's real vertical panel layout.
        page.locator('[data-panel=citizens]').click()
        page.locator('#panelBody [data-house]').first.click()
        assert page.locator('#panelTitle').inner_text() == 'Property Inspector'
        page.evaluate('''()=>{const name=document.querySelector('#panelBody .entry strong'),value=document.querySelector('#panelBody .stat b');if(name)name.textContent='Gemeindeverwaltungsinfrastrukturplanung'.repeat(4);if(value)value.textContent='$9,999,999,999,999,999.99'}''')
        inspector = page.evaluate('''()=>{const b=document.querySelector('#panelBody');return {width:b.clientWidth,scroll:b.scrollWidth,over:[...b.querySelectorAll('.entry strong,.stat b')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>({text:e.innerText,width:e.clientWidth,scroll:e.scrollWidth}))}}''')
        assert inspector['scroll'] <= inspector['width'] + 1 and not inspector['over'], inspector
        page.screenshot(path=str(OUT / f'inspector-large-text-{width}x{height}.png'))

        # Large ledger values and long translated labels wrap inside account rows.
        page.locator('[data-panel=treasury]').click()
        page.evaluate('''()=>{const row=document.querySelector('#panelBody .line');if(row){row.children[0].textContent='Unusually long translated municipal balance label for accessibility review';row.children[1].textContent='$9,999,999,999,999,999.99'}}''')
        row = page.locator('#panelBody .line').first
        row.scroll_into_view_if_needed()
        row_metrics = row.evaluate('''e=>({width:e.clientWidth,scroll:e.scrollWidth,children:[...e.children].map(c=>({width:c.clientWidth,scroll:c.scrollWidth,text:c.innerText}))})''')
        assert row_metrics['scroll'] <= row_metrics['width'] + 1, row_metrics
        assert all(c['scroll'] <= c['width'] + 1 for c in row_metrics['children']), row_metrics

        # Help and archive sheets honor the same text preference and Escape
        # closes them without changing the town's accounts or policies.
        before = page.evaluate('__townTest.get()')
        page.locator('[data-panel=settings]').click()
        page.locator('#tutorial').click()
        assert page.locator('#helpDialog').is_visible()
        help_font = page.locator('#helpDialog .help-paper p').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')
        assert help_font >= 15, help_font
        page.keyboard.press('Escape')
        assert page.locator('#helpDialog').is_hidden()
        page.locator('#backupSave').click()
        assert page.locator('#helpDialog').is_visible()
        assert page.locator('#helpDialog textarea').is_visible()
        page.keyboard.press('Escape')
        after = page.evaluate('__townTest.get()')
        assert page.locator('#helpDialog').is_hidden()
        assert after['treasury'] == before['treasury'] and after['policy'] == before['policy']
        assert not errors, errors
        results.append({'viewport':[width,height],'largeTextDialog':checks,'inspector':inspector,'ledgerRow':row_metrics,'helpFont':help_font,'pendingAfterBack':after['pending'],'errors':errors})
        page.close()
    browser.close()

receipt = {'sourceSha256': hashlib.sha256(SOURCE.encode()).hexdigest(), 'results': results}
(OUT / 'controls.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
