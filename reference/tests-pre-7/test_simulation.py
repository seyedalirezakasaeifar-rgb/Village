from playwright.sync_api import sync_playwright
from pathlib import Path
import time,json
root=Path(__file__).resolve().parent.parent
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1080,'height':610},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
 html=(root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
 page.set_content(html);page.add_script_tag(content=(root/'assets/game.js').read_text());page.locator('#newTown').click()
 for sc in ['settlement','hardtimes','frontier','industrial']:
  print('\nSCENARIO',sc,flush=True)
  page.evaluate('(sc)=>__townTest.reset(sc)',sc)
  base=page.evaluate('__townTest.get()');print('start', {k:base[k] for k in ['day','treasury','debt','population','employment','hardship','businesses','approval','total']},flush=True)
  start=time.perf_counter();page.evaluate('()=>__townTest.step(360)');spent=time.perf_counter()-start
  later=page.evaluate('__townTest.get()');print('year', {k:later[k] for k in ['day','treasury','debt','population','employment','hardship','businesses','approval','cases','events','total','achievements','pending']},'speed:',round(spent,2),'sec',flush=True)
  assert abs(later['total']-base['total'])<3, 'Cash conservation violation'
  assert later['day']>=360 and later['population']>0 and later['businesses']>=0
  assert not errors, errors
  saved=page.evaluate('__townTest.save()');assert page.evaluate('(s)=>__townTest.load(s)',saved)
  again=page.evaluate('__townTest.get()');assert again['day']==later['day'];print('save restored',len(saved),'bytes')
 print('PASS: all scenarios and economy conserved, no errors')
 browser.close()
