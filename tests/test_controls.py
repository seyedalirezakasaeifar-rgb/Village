"""Current 6.0 pointer controls with actual canvas bounds and full footprints."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os
R=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':844,'height':390},has_touch=True,is_mobile=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((R/'assets/index.html').as_uri());page.locator('#townSeed').fill('42');page.locator('#newTown').click()
 assert page.locator('#panel').evaluate("e=>e.classList.contains('show')")
 page.locator('#panelClose').focus();page.keyboard.press('Escape')
 assert not page.locator('#panel').evaluate("e=>e.classList.contains('show')")
 assert page.evaluate("document.activeElement===document.querySelector('[data-panel=overview]')"), 'Escape should return keyboard focus to the panel launcher'
 page.locator('[data-panel=overview]').click();page.locator('#panelClose').click();page.locator('#pause').click()
 page.locator('[data-panel=construction]').click();page.locator('[data-build=park]').click()
 state=page.evaluate('JSON.parse(__townTest.save())');box=page.locator('#view').bounding_box();camera=page.evaluate('__townTest.view().camera');grid=state['gridSize']
 occupied={i for x in state['buildings'] for i in x.get('footprint',[x['y']*grid+x['x']])}
 def screen(x,y):return (box['x']+box['width']/2+camera['zoom']*((x-y)*36+(grid*72+140)/2-camera['x']),box['y']+box['height']/2+camera['zoom']*((x+y)*18+50-camera['y']))
 legal=[]
 for y in range(5,51):
  for x in range(5,51):
   i=y*grid+x;sx,sy=screen(x,y)
   if state['tiles'][i]==0 and i not in occupied and not state['landUse'].get(str(i)) and any(state['tiles'][(y+dy)*grid+x+dx]==1 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]) and 80<sx<760 and 175<sy<315:legal.append((x,y))
 assert legal
 x,y=legal[0];sx,sy=screen(x,y);page.touchscreen.tap(sx,sy)
 after=page.evaluate('JSON.parse(__townTest.save())')
 assert len(after['buildings'])==len(state['buildings'])+1
 assert abs(state['treasury']-after['treasury']-550)<.001
 assert after['buildings'][-1]['kind']=='park'
 page.locator('[data-panel=construction]').click();page.locator('[data-build=""]').click()
 sx,sy=screen(26,26);page.touchscreen.tap(sx,sy)
 assert page.locator('#panelTitle').inner_text()=='Property Inspector'
 page.locator('#panelClose').click()
 page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
 initial_zoom=page.evaluate('__townTest.view().camera.zoom')
 first=page.screenshot();before=len(after['buildings'])
 cdp=page.context.new_cdp_session(page)
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':350,'y':230,'id':1},{'x':490,'y':230,'id':2}]})
 cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':320,'y':230,'id':1},{'x':520,'y':230,'id':2}]})
 cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
 page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
 assert page.evaluate('__townTest.view().camera.zoom')>initial_zoom
 assert page.screenshot()!=first
 assert len(page.evaluate('JSON.parse(__townTest.save()).buildings'))==before
 page.locator('#center').click();page.locator('[data-panel=policies]').click()
 page.locator('input[data-policy=incomeTax]').fill('18');assert page.evaluate('__townTest.get().policy.incomeTax')==12
 page.locator('#enactPolicy').click();assert page.evaluate('__townTest.get().policy.incomeTax')==18
 page.locator('#panelClose').click();page.locator('#speedRange').fill('6')
 assert page.locator('#speed').inner_text()=='64×'
 page.locator('[data-panel=settings]').click();page.locator('#backupSave').click()
 assert page.locator('#helpDialog').is_visible()
 assert page.locator('#helpDialog').get_attribute('role')=='dialog' and page.locator('#helpDialog').get_attribute('aria-modal')=='true'
 assert page.locator('#helpDialog').inner_text().startswith('YOUR TOWN ARCHIVE')
 page.keyboard.press('Shift+Tab');assert page.evaluate("document.activeElement.id==='archiveClose'"), 'modal keyboard focus should wrap backward'
 page.keyboard.press('Tab');assert page.evaluate("document.activeElement.id==='saveText'"), 'modal keyboard focus should wrap forward'
 page.keyboard.press('Escape')
 assert page.locator('#helpDialog').is_hidden()
 assert page.evaluate("document.activeElement===document.querySelector('#backupSave')"), 'archive dismissal should return focus to its opener'
 page.locator('#tutorial').click()
 assert 'THE TOWN CHARTER' in page.locator('#helpDialog').inner_text()
 page.locator('#helpClose').click()
 assert page.evaluate("document.activeElement===document.querySelector('#tutorial')"), 'manual dismissal should return focus to its opener'
 page.locator('#panelClose').click()
 page.evaluate('__townTest.step(360)');assert page.locator('#eventDialog').is_hidden()
 assert page.evaluate('JSON.parse(__townTest.save()).council.elections')==1
 assert not errors,errors
 page.screenshot(path=str(R/'reports/final/controls-phone.png'))
 print('PASS touch placement/cost, inspection, pinch without construction, staged policy, speed slider and nonblocking election',flush=True)
 b.close()
