from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_text();results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source);p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.step(2)');snapshot=p.evaluate('__townTest.save()')
 def board():
  p.keyboard.press('Escape');p.locator('[data-panel=overview]').click();p.locator('[data-civic-projects]').click()
 for kind,cost in [('square',2500),('warehouse',12000)]:
  assert p.evaluate('s=>__townTest.load(s)',snapshot);board();assert p.locator('[data-public-place=square]').evaluate('e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight;}');before=p.evaluate('JSON.parse(__townTest.save()).treasury');p.locator('[data-public-place='+kind+']').click();p.keyboard.press('Escape');assert p.evaluate('JSON.parse(__townTest.save()).treasury')==before
  p.locator('[data-public-place='+kind+']').click();p.locator('#publicPlaceName').fill('Copper & Cedar');p.locator('[data-event-choice="0"]').click();g=p.evaluate('JSON.parse(__townTest.save())');place=g['publicPlaces']['places'][0];assert place['name']=='Copper & Cedar'and place['kind']==kind;assert abs(before-g['treasury']-(cost-(g['policy']['permitFee']if kind=='warehouse'else 0)))<.001,(kind,before-g['treasury'],cost)
  p.evaluate('__townTest.step(15)');board();assert 'Copper & Cedar' in p.locator('#publicLife').inner_text();assert 'Other decisions and events' in p.locator('#publicLife').inner_text();p.locator('[data-public-visit]').click();assert not p.locator('#panel').evaluate('e=>e.classList.contains("show")');saved=p.evaluate('__townTest.save()');assert p.evaluate('s=>__townTest.load(s)',saved);assert p.evaluate('__townTest.validate().ok');results.append(place)
  assert p.evaluate('()=>{let g=JSON.parse(__townTest.save());g.publicPlaces.places[0].x=-1;return !__townTest.load(JSON.stringify(g))}')
 assert (results[0]['x'],results[0]['y'])==(results[1]['x'],results[1]['y']);board();out=ROOT/'reports/public-life';out.mkdir(parents=True,exist_ok=True);p.screenshot(path=str(out/'actual-market-place.png'));(out/'controls.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'actualAlternativePurchases':results,'errors':errors},indent=2)+'\n');assert not errors,errors;b.close()
print('PASS same real site square/warehouse alternatives, exact costs, named actual property, cancel, continued settlement, visits, save/load and invalid coordinates')
