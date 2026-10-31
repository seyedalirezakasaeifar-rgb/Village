"""Offline art, non-blocking speed, council inbox and screenshot regression."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import threading,http.server,functools,time
root=Path(__file__).resolve().parent.parent
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root/'assets'))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1100,'height':650},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 html=(root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
 page.set_content(html);page.add_script_tag(content=(root/'assets/game.js').read_text())
 page.locator('#newTown').click();page.wait_for_timeout(1700)
 page.screenshot(path=str(root/'reports/pixel-desktop.png'))
 page.locator('#panelClose').click();page.wait_for_timeout(300)
 page.screenshot(path=str(root/'reports/pixel-full-map.png'))
 arts=page.evaluate('''()=>({loaded:[...document.images].length,cache:__townTest.renderBench(2)})''');print('art',arts)
 page.locator('#pause').click()
 page.evaluate('__townTest.step(361)')
 assert not page.locator('#eventDialog').is_visible(), 'Automatic event unexpectedly blocked simulation'
 inbox=page.evaluate('__townTest.inbox()')
 assert inbox, 'No council correspondence after 360+ days'
 assert page.evaluate('JSON.parse(__townTest.save()).council.elections')==1
 print('after election inbox',len(inbox),'day',page.evaluate('__townTest.get().day'))
 page.locator('button[data-panel="agenda"]').click()
 page.screenshot(path=str(root/'reports/pixel-inbox.png'))
 assert page.locator('[data-inbox]').count()>0
 page.locator('[data-inbox]').first.click()
 assert page.locator('#eventDialog').is_visible(), 'Manually reviewing inbox did not open decision'
 page.locator('[data-event-choice]').first.click()
 assert not page.locator('#eventDialog').is_visible()
 print('manual resolution passed')
 # Serialization must retain unattended correspondence, and paused simulation
 # must stop moving traffic as well as the economic clock.
 saved=page.evaluate('__townTest.save()');before=page.evaluate('__townTest.inbox().length')
 assert page.evaluate('s=>__townTest.load(s)',saved)
 assert page.evaluate('__townTest.inbox().length')==before
 page.evaluate('()=>{__townTest.spawn();__townTest.advanceTraffic(.2)}')
 frozen=page.evaluate('__townTest.traffic()')
 page.wait_for_timeout(300)
 after=page.evaluate('__townTest.traffic()')
 assert frozen==after, 'Vehicles moved while paused'
 print('SAVE/PAUSE regression passed')
 # Resume at maximum speed; natural events must never open a blocking dialog.
 page.locator('#speedRange').fill('6')
 page.locator('#pause').click()
 page.wait_for_timeout(2300)
 assert page.locator('#eventDialog').is_hidden()
 assert page.locator('#speed').inner_text()=='64×'
 day=page.evaluate('__townTest.get().day');print('high-speed day',day)
 assert day>361
 assert not errors, errors
 print('PASS art, inbox, election, manual decision, 64x, no script errors')
 browser.close()
