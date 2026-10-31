"""Consolidated map feedback leaves the town visible and preserves every action."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();OUT=ROOT/'reports/civic-projects';OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);rows=[]
 for width,height in [(568,320),(844,390),(390,844)]:
  p=b.new_page(viewport={'width':width,'height':height},has_touch=True);p.set_default_timeout(8000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source);p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click()
  before=p.evaluate('JSON.parse(__townTest.save())');deck=p.locator('#mapStatusDeck');area=p.locator('.workspace').bounding_box();box=deck.bounding_box();fraction=box['width']*box['height']/(area['width']*area['height']);assert fraction<.16,(width,height,fraction)
  assert p.locator('#mapStatusToggle').get_attribute('aria-expanded')=='false';assert p.locator('#topNotice').is_hidden() and p.locator('#liveEconomy').is_hidden()
  assert 'Paused' in p.locator('#mapStatusContext').inner_text()
  p.locator('#mapStatusToggle').click();assert p.locator('#topNotice').is_visible() and p.locator('#objectiveMini').is_visible() and p.locator('#liveEconomy').is_visible()
  p.locator('#topNotice').click();assert p.locator('#panelTitle').inner_text()=='Public Record';assert deck.is_hidden()
  p.keyboard.press('Escape');assert p.locator('#topNotice').evaluate('e=>e===document.activeElement')
  p.locator('#liveEconomy').click();assert p.locator('#panelTitle').inner_text()=='The Living Economy';p.keyboard.press('Escape');assert p.locator('#liveEconomy').evaluate('e=>e===document.activeElement')
  assert p.evaluate('__townArchive.back()');assert p.locator('#mapStatusToggle').get_attribute('aria-expanded')=='false';assert p.locator('#mapStatusToggle').evaluate('e=>e===document.activeElement')
  after=p.evaluate('JSON.parse(__townTest.save())')
  for key in ['day','treasury','region','firms','households','people','loans']:assert before[key]==after[key],key
  # A region survey or active placement gets the map to itself.
  p.locator('[data-panel=construction]').click();p.locator('#charterOffice > summary').click();p.locator('[data-parcel-preview=east-meadow]').click();p.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');assert deck.is_hidden();p.locator('#center').click();p.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');assert deck.is_visible()
  p.locator('[data-panel=construction]').click();p.locator('[data-build=park]').click();p.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');assert deck.is_hidden();p.keyboard.press('Escape');p.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');assert deck.is_visible()
  for target in ['#topNotice','#objectiveMini','#liveEconomy','#marketHeadline','#marketDetail','#hint']:assert p.locator(target).count()==1,target
  assert p.locator('#pauseBanner').evaluate('e=>e.closest("#liveEconomy")!==null')
  assert not errors,errors;p.screenshot(path=str(OUT/f'clear-map-{width}x{height}.png'));rows.append({'viewport':[width,height],'collapsedMapFraction':fraction,'errors':errors});p.close()
 b.close()
(OUT/'status-deck.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'layouts':rows,'economicStateUnchanged':True,'existingInformationAndActionsRetained':True},indent=2)+'\n')
print('PASS one compact map signal under 16% of map, retained newspaper/ambition/economy actions, focus and Android Back, placement/survey clearance, no economic mutation',rows)
