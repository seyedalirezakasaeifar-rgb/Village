from playwright.sync_api import sync_playwright
from pathlib import Path
import threading,http.server,functools,time
root=Path(__file__).resolve().parent.parent
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root/'assets'))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/index.html'
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1080,'height':610},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda err:errors.append(str(err)));page.on('console',lambda msg:errors.append('console '+msg.text) if msg.type=='error' else None)
 html=(root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
 page.set_content(html);page.add_script_tag(content=(root/'assets/game.js').read_text());page.wait_for_timeout(600)
 page.screenshot(path=str(root/'screenshots-00-menu.png'))
 print('menu:',page.title(),page.locator('#newTown').count())
 page.locator('#newTown').click(timeout=20000);page.wait_for_timeout(1200)
 print('sim:',page.locator('#pop').inner_text(),page.locator('#funds').inner_text(),page.locator('#approval').inner_text())
 page.screenshot(path=str(root/'screenshots-01-town.png'))
 for tab in ['agenda','policies','treasury','community','businesses','citizens','construction','journal','settings']:
  page.locator(f'button[data-panel="{tab}"]').click();page.wait_for_timeout(80)
  title=page.locator('#panelTitle').inner_text();print('tab',tab,title,len(page.locator('#panelBody').inner_text()))
  if tab=='agenda':page.screenshot(path=str(root/'screenshots-02-agenda.png'))
  if tab=='policies':
   print('policies',page.locator('input[data-policy]').count());page.locator('[data-policy="incomeTax"]').fill('10');page.locator('[data-policy="incomeTax"]').dispatch_event('change');page.locator('#enactPolicy').click();print('policy new',page.evaluate('document.querySelector("[data-policy=incomeTax]").value'))
  if tab=='citizens':
   print('households',page.locator('[data-house]').count());page.locator('[data-house]').first.click();print('inspect',page.locator('#panelTitle').inner_text());page.locator('#panelClose').click()
  if tab=='community':page.screenshot(path=str(root/'screenshots-03-services.png'))
 if errors:print('ERRORS',errors)
 print('game done')
 browser.close()
