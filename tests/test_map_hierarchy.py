"""Readable actionable map summaries, focus return and narrow phone controls."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js','''
window.__mapPressureProbe=()=>{const old=G;try{G=JSON.parse(JSON.stringify(G));G.market.foodDisconnected=5;const access=marketSignal().title;G.market.foodDisconnected=0;G.market.unmetFood=G.stats.population*.2;const food=marketSignal().title;G.market.unmetFood=0;G.stats.employment=99;G.stats.hardship=0;G.serviceProvision={health:{coverage:.2},school:{coverage:.9}};const care=marketSignal().title;return {access,food,care};}finally{G=old;}};
window.__headerStress=()=>{G.region-=12345678-G.treasury;G.treasury=12345678;G.day=360000;G.year=1000;G.month=12;updateHeader();};
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);rows=[]
 for width,height in [(568,320),(640,360),(720,360),(844,390),(360,640)]:
  p=b.new_page(viewport={'width':width,'height':height},has_touch=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source);p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.step(30)');p.locator('#panelClose').click();assert p.locator('[data-panel=overview]').evaluate('e=>e===document.activeElement')
  p.locator('#mapStatusToggle').click();p.locator('#topNotice').click();assert p.locator('#panelTitle').inner_text()=='Public Record';p.keyboard.press('Escape');assert p.locator('#topNotice').evaluate('e=>e===document.activeElement')
  p.locator('#liveEconomy').click();assert p.locator('#panelTitle').inner_text()=='The Living Economy';assert not p.locator('#topNotice').is_visible();p.keyboard.press('Escape');assert p.locator('#liveEconomy').evaluate('e=>e===document.activeElement')
  assert p.locator('#pauseBanner').evaluate('e=>e.closest("#liveEconomy")!==null');assert p.locator('#tabs .tabico svg').count()==12
  r=p.evaluate('__mapPressureProbe()');assert r=={'access':'Groceries out of reach','food':'Essential food is going unfilled','care':'Care and learning need attention'},r
  p.evaluate('__headerStress()');assert p.locator('#funds').inner_text()=='$12.3m' and p.locator('#funds').get_attribute('title')=='$12,345,678'
  for selector in ['#pause','#speedRange','#tabs button','.mapbuttons button']:
   for e in p.locator(selector).all():
    box=e.bounding_box();assert box and box['x']>=0 and box['y']>=0 and box['x']+box['width']<=width+1 and box['y']+box['height']<=height+1,(width,height,selector,box)
    assert e.evaluate('(e)=>{const r=e.getBoundingClientRect(),p=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return e===p||e.contains(p)}'),(width,height,selector)
  assert not errors,errors;rows.append((width,height));p.close()
 b.close();print('PASS map pressure priorities, two actionable summaries, native-sized reachability, vector navigation, exact-value titles and focus return',rows)
