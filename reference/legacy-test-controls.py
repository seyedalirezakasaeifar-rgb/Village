"""End-to-end mobile viewport touch/click paths, municipal works, election decision."""
from playwright.sync_api import sync_playwright
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':844,'height':390},device_scale_factor=1,has_touch=True,is_mobile=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 html=(root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
 page.set_content(html);page.add_script_tag(content=(root/'assets/game.js').read_text())
 page.screenshot(path=str(root/'mobile-00-menu.png'))
 page.locator('#newTown').click();page.locator('#panelClose').click();page.screenshot(path=str(root/'mobile-01-map.png'))
 page.locator('button[data-panel=construction]').click()
 print('construction visible:',page.locator('[data-build=road]').is_visible())
 page.locator('button[data-build=park]').click()
 state=page.evaluate('JSON.parse(__townTest.save())');T=56
 tiles=state['tiles']; buildings={(b['x'],b['y']) for b in state['buildings']};coords=None
 for y in range(16,38):
  for x in range(16,38):
   if tiles[y*T+x]==0 and (x,y) not in buildings and any(tiles[yy*T+xx]==1 for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]):
    coords=(x,y);break
  if coords:break
 assert coords
 # Prefer a vacant, road-adjacent plot that is visible outside the town crier overlay.
 def screen(x,y): return (422+.68*((x-y)*36),49+289/2+.68*((x+y)*18+50-(56*36+120)/2))
 possible=[(x,y) for y in range(15,39) for x in range(15,39) if tiles[y*T+x]==0 and (x,y) not in buildings and any(tiles[yy*T+xx]==1 for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))) and 90<screen(x,y)[0]<745 and 160<screen(x,y)[1]<300]
 assert possible
 coords=min(possible,key=lambda pt:abs(screen(*pt)[0]-422)+abs(screen(*pt)[1]-220))
 initial_money=state['treasury'];n0=len(state['buildings']); sx,sy=screen(*coords)
 page.mouse.click(sx,sy)
 new_state=page.evaluate('JSON.parse(__townTest.save())')
 print('park construction:',coords,'cost',initial_money-new_state['treasury'],'buildings',len(new_state['buildings'])-n0)
 assert len(new_state['buildings'])==n0+1 and initial_money-new_state['treasury']==550
 assert new_state['buildings'][-1]['kind']=='park'
 # Change from construction to surveying, then tap a real property.
 page.locator('button[data-panel=construction]').click();page.locator('button[data-build=""]').click()
 # At center townhall, projection x=(26-26)*36+2086=2086, y=(26+26)*18+32=968; tile center +18; camera zoom .68.
 cv=page.locator('#view');box=cv.bounding_box();print('view bounding',box)
 x=box['x']+box['width']/2
 y=box['y']+box['height']/2+.68*(968+18-(56*36+120)/2)
 print('click pixel',x,y)
 page.mouse.click(x,y)
 print('after tap',page.locator('#panelTitle').inner_text(),page.locator('#panel').get_attribute('class'))
 assert page.locator('#panelTitle').inner_text()=='Property Inspector'
 page.locator('#panelClose').click()
 # Weather, time control and map zoom interaction.
 old=page.evaluate('JSON.parse(__townTest.save()).day');page.locator('#speed').click();assert '2' in page.locator('#speed').inner_text()
 page.locator('#zoomIn').click();page.locator('#center').click()
 page.locator('button[data-panel=agenda]').click();page.locator('#panelClose').click()
 # Elections and routine correspondence must NEVER block simulation at 64×.
 page.locator('#pause').click() # Prevent wall-clock simulation from racing manual advancement.
 page.evaluate('__townTest.step(359)');print('day',page.evaluate('__townTest.get().day'),'letters',page.evaluate('__townTest.inbox().length'))
 assert not page.locator('#eventDialog').is_visible(), 'Election opened an interrupting modal'
 assert page.evaluate('()=>JSON.parse(__townTest.save()).council.elections')==1
 assert page.evaluate('__townTest.inbox().length')>0
 page.locator('button[data-panel=journal]').click();page.screenshot(path=str(root/'mobile-02-journal.png'))
 print('errors',errors);assert not errors
 b.close()
