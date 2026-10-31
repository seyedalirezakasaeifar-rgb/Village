"""Exercise game workflows without the newer Array.at API (not a full engine emulation)."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.evaluate('delete Array.prototype.at');p.add_script_tag(content=(ROOT/'assets/game.js').read_text());p.locator('#newTown').click();p.locator('#pause').click()
 for scenario in ['settlement','regional']:
  p.evaluate('s=>__townTest.reset(s,42)',scenario);p.evaluate('__townTest.step(180)');p.evaluate('__townTest.capture({zoom:.7})')
  for panel in ['overview','economy','community','policies','journal']:
   p.locator('[data-panel='+panel+']').click();assert 'Panel error' not in p.locator('#panelBody').inner_text();p.keyboard.press('Escape')
 p.locator('[data-panel=policies]').click();p.locator('#tradeToggle').click();p.locator('#enactPolicy').click()
 p.evaluate('__townTest.offerPetition()');p.locator('[data-panel=agenda]').click();p.locator('[data-inbox="0"]').click();p.locator('#eventDefer').focus();p.keyboard.press('Tab');p.keyboard.press('Escape')
 assert p.evaluate('__townTest.validate().ok') and not errors,errors
 b.close();print('PASS rendering, charts, policy enactment, development and Council focus without Array.at; not a full older-engine certification')
