"""Measured policy-impact copy stays honest and compact on a phone."""
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright


def run():
    errors = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page(viewport={'width': 390, 'height': 844}, has_touch=True)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content(html)
        page.add_script_tag(content=(ROOT / 'assets/game.js').read_text())
        page.locator('#newTown').click()
        page.locator('#pause').click()
        page.evaluate('__townTest.observations().splice(0);__townTest.systems().experiments.splice(0)')
        page.locator('[data-panel=policies]').click()
        page.locator('[data-policy=incomeTax]').evaluate("e=>{e.value='17';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}")
        page.locator('#enactPolicy').click()
        page.locator('[data-panel=economy]').click()
        text = page.locator('#panelBody').inner_text()
        assert 'No post-change reading yet' in text
        assert 'BEFORE:' not in text and 'Δ' not in text
        assert page.evaluate('__townTest.systems().experiments[__townTest.systems().experiments.length-1].before.day') == 1

        page.evaluate('__townTest.step(9)')  # day 10: first scheduled post-change observation
        page.keyboard.press('Escape')
        page.locator('[data-panel=economy]').click()
        text = page.locator('#panelBody').inner_text()
        assert 'AFTER: day 10' in text and 'not proof it caused them' in text
        archive = page.evaluate('__townTest.save()')
        assert page.evaluate('arg=>__townTest.load(arg)', archive)
        page.keyboard.press('Escape')
        page.locator('[data-panel=economy]').click()
        assert 'AFTER: day 10' in page.locator('#panelBody').inner_text()

        # Exercise retained maximum-length histories and the 30-entry policy journal.
        page.evaluate("""()=>{
          const observations=__townTest.observations(),experiments=__townTest.systems().experiments,sample=observations[observations.length-1];
          observations.splice(0,observations.length,...Array.from({length:1200},(_,i)=>({...sample,day:i*10})));
          experiments.splice(0,experiments.length,...Array.from({length:30},(_,i)=>({day:i*20,before:{...sample,day:i*20},after:{...sample,day:i*20+180},changes:[{key:'incomeTax',from:12,to:12+i}]})));
        }""")
        page.keyboard.press('Escape')
        page.locator('[data-panel=economy]').click()
        card = page.locator('#panelBody .council-card').filter(has=page.get_by_text('RECENT POLICY'))
        assert card.count() == 1
        assert 'ENACTED DAY 580' in card.inner_text()
        assert 'AFTER: day 11990' in card.inner_text()
        assert 'RECENT POLICY' in card.inner_text()
        assert 'not proof it caused them' in card.inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors, errors
        browser.close()
    print('PASS no-history baseline, first delayed sample, save/load, bounded 1,200-sample history and 390px phone layout')


if __name__ == '__main__':
    run()
