"""5.6 graphics, autonomous-economy dashboard, ambient citizens and decision regression."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import threading,functools,http.server
R=Path(__file__).resolve().parent.parent
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(R/'assets'))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1130,'height':650},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 html=(R/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(R/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
 page.set_content(html);page.add_script_tag(content=(R/'assets/game.js').read_text())
 page.locator('#newTown').click();page.wait_for_timeout(700)
 page.locator('button[data-panel="economy"]').click();page.wait_for_timeout(600)
 body=page.locator('#panelBody').inner_text()
 for phrase in ['Where people earn their living','Median savings','Housing pressure','Banks, loans and savings','What should the government do?']:
  assert phrase.lower() in body.lower(),(phrase,body[:1200])
 assert page.locator('tr').count()>=3
 assert 'Panel error' not in body,body[:700]
 page.screenshot(path=str(R/'reports'/'new-economy.png'))
 print('economy panel validated',len(body),'chars',page.locator('tr').count(),'rows')
 page.locator('#marketPolicy').click();assert page.locator('#panelTitle').inner_text()=='Economic Policy'
 page.locator('button[data-panel="economy"]').click();page.locator('#marketFamilies').click();assert page.locator('#panelTitle').inner_text()=='Our Residents'
 page.locator('#panelClose').click();page.wait_for_timeout(250)
 page.screenshot(path=str(R/'reports'/'reforged-town.png'))
 # No automatic modal after long unattended operation, including election day.
 page.evaluate('__townTest.step(365)')
 assert page.locator('#eventDialog').is_hidden()
 assert page.locator('#liveEconomy').is_visible()
 pulse=page.locator('#liveEconomy').inner_text();assert 'employed' in pulse
 assert page.evaluate('()=>__townTest.get().day')>=366
 page.locator('button[data-panel="economy"]').click();body=page.locator('#panelBody').inner_text()
 assert 'private work sites' in body.lower() and 'bank' in body.lower()
 # The government package is ONLY a proposal until explicitly enacted.
 page.locator('button[data-panel="policies"]').click()
 previous=page.evaluate('__townTest.get().policy.zoningRestriction')
 page.locator('button[data-cabinet="housing"]').click()
 assert page.evaluate('__townTest.get().policy.zoningRestriction')==previous
 assert page.locator('input[data-policy="zoningRestriction"]').input_value()=='0'
 page.locator('#enactPolicy').click()
 assert page.evaluate('__townTest.get().policy.zoningRestriction')==0
 print('staged cabinet proposal and explicit enactment passed')
 assert not errors,errors
 print('PASS new public dashboard, manual navigation, unattended year, annual election, pulse')
 browser.close()
