"""Regression: deferred council decisions, transactional trade and long-session UI."""
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':390,'height':844},has_touch=True)
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=(ROOT/'assets/game.js').read_text());p.locator('#newTown').click();p.locator('#pause').click()
 p.locator('[data-panel=policies]').click();initial=p.evaluate('__townTest.get().policy.imports');saved=p.evaluate('__townTest.save()')
 p.locator('#tradeToggle').click();assert p.evaluate('__townTest.get().policy.imports')==initial
 p.locator('[data-policy=incomeTax]').fill('17');assert 'Regional imports' in p.locator('#draftSummary').inner_text()
 p.locator('#resetPolicy').click();assert p.evaluate('__townTest.get().policy.imports')==initial
 p.locator('#tradeToggle').click();p.locator('#enactPolicy').click();assert p.evaluate('__townTest.get().policy.imports')!=initial
 p.evaluate('__townTest.offerPetition()');p.locator('[data-panel=agenda]').click();title=p.evaluate('__townTest.inbox()[0].title');p.locator('[data-inbox="0"]').click()
 assert p.locator('#eventDialog').is_visible() and p.locator('#eventDialog').get_attribute('aria-modal')=='true'
 p.locator('#eventDefer').focus();p.keyboard.press('Tab');assert p.evaluate("document.activeElement.closest('#eventChoices')!==null")
 p.keyboard.press('Shift+Tab');assert p.locator('#eventDefer').evaluate('(e)=>e===document.activeElement')
 p.keyboard.press('Escape');assert not p.locator('#eventDialog').is_visible() and p.locator('#panel').is_visible()
 assert title in p.evaluate('__townTest.inbox().map(e=>e.title)')
 assert not p.evaluate('__townTest.get().pending')
 p.locator('[data-inbox="0"]').click();assert p.evaluate('__townArchive.back()');assert not p.locator('#eventDialog').is_visible()
 p.locator('[data-inbox="0"]').click();p.locator('#eventChoices button:not([disabled])').first.click();assert title not in p.evaluate('__townTest.inbox().map(e=>e.title)')
 # Reset and visit every panel repeatedly after real simulation/save/restore steps.
 for days in range(0,1080,180):
  p.evaluate('__townTest.step(180)');archive=p.evaluate('__townTest.save()');assert p.evaluate('__townTest.load(JSON.parse(arg))'.replace('arg',json.dumps(archive)))
  for tab in p.locator('#tabs button').evaluate_all('(items)=>items.map(e=>e.dataset.panel)'):
   p.locator('[data-panel='+tab+']').click();assert 'Panel error' not in p.locator('#panelBody').inner_text();p.keyboard.press('Escape')
 assert p.evaluate('__townTest.validate().ok') and not errors,errors
 b.close();print('PASS council defer/back/focus, imports draft/discard/enact, six 180-day save/restore/all-panel cycles')
