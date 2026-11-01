"""Owned district and civic-place names stay safe, stable, and cosmetic."""
from pathlib import Path
import hashlib, json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html
source=(ROOT/'assets/game.js').read_text()
probe="window.__nameProbe={districts:()=>ensureUrban().districts,money:totalMoney,rename:urbanRenameDistrict,review:urbanDistrictReview,label:urbanDistrictMapLabel,projects:openCivicProjects,evolve:k=>{const g=G,d=ensureUrban().districts[k];d.character='Redevelopment in progress';g.day+=30;g.urban.lastReview=g.day-30;urbanDistrictReview();return __townTest.save()}};\n"
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'// SOURCE: 99-instrumentation.js')
results={"source_sha256":hashlib.sha256(source.encode()).hexdigest()}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844},has_touch=True)
 page.set_default_timeout(5000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html);page.add_script_tag(content=script);page.locator('#newTown').click();page.locator('#pause').click()
 page.evaluate("__townTest.reset('settlement',42);__townTest.step(30);__nameProbe.review()")
 # Unowned region keys must not be renameable, even through a stale/direct action.
 assert not page.evaluate("__nameProbe.rename('7:7')")
 page.locator('[data-panel=construction]').click();page.locator('#urbanPlanningOffice>summary').click()
 assert page.locator('[data-rename-district]').count()>0
 district_button=page.locator('[data-rename-district]').first
 key=district_button.get_attribute('data-rename-district')
 before=page.evaluate("()=>({total:__nameProbe.money(),districts:JSON.stringify(__nameProbe.districts()),save:__townTest.save()})")
 district_button.click();assert page.locator('[aria-label="New district name"]:visible').is_visible();page.locator('[data-event-choice="1"]').click()
 assert page.evaluate('()=>__nameProbe.money()')==before['total']
 assert page.evaluate("k=>__nameProbe.districts()[k].name",key)==json.loads(before['save'])['urban']['districts'][key]['name']
 page.locator('[data-rename-district="'+key+'"]').click();field=page.locator('[aria-label="New district name"]:visible');field.fill('')
 page.locator('[data-event-choice="0"]').click()
 assert page.evaluate("k=>__nameProbe.districts()[k].name",key)==json.loads(before['save'])['urban']['districts'][key]['name']
 assert 'non-empty' in page.locator('#toast').inner_text().lower()
 page.locator('[data-rename-district="'+key+'"]').click();page.locator('[aria-label="New district name"]:visible').fill('x'*51);page.locator('[data-event-choice="0"]').click()
 assert page.evaluate("k=>__nameProbe.districts()[k].name",key)==json.loads(before['save'])['urban']['districts'][key]['name']
 name='<img src=x onerror=alert(1)> Å区'
 page.locator('[data-rename-district="'+key+'"]').click();page.locator('[aria-label="New district name"]:visible').fill(name);page.locator('[data-event-choice="0"]').click()
 district=page.evaluate("k=>__nameProbe.districts()[k]",key)
 assert district['name']==name
 assert page.locator('#panelBody img').count()==0
 page.locator('[data-panel=construction]').click();page.locator('#urbanPlanningOffice').evaluate('(e)=>e.open=true');assert name in page.locator('#panelBody').inner_text()
 assert page.evaluate('()=>__townTest.save()')
 # Name stays attached to the owned block when its observed character changes and after loading.
 archive=page.evaluate('k=>__nameProbe.evolve(k)',key)
 assert page.evaluate('k=>__nameProbe.districts()[k]?.name',key)==name
 assert page.evaluate('s=>__townTest.load(s)',archive)
 assert page.evaluate('k=>__nameProbe.districts()[k]?.name',key)==name
 assert page.evaluate('__townTest.validate().ok')
 # Map overlay at a phone viewport draws a bounded label while retaining full saved name.
 page.locator('[data-panel=construction]').click();page.locator('#urbanPlanningOffice').evaluate('(e)=>e.open=true');page.locator('[data-urban-overlay]').click()
 label=page.evaluate('s=>__nameProbe.label(s)',name);assert len(label)<=20
 map=page.locator('#view').bounding_box();assert map and map['width']<=390
 out=ROOT/'docs/previews/urban8';out.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(out/'district-map-naming-phone.png'))
 results['district']={'key':key,'name':name,'unownedRejected':True,'cancelAndInvalidInputsRejected':True,'stableAfterCharacterChangeAndLoad':True,'phoneViewport':390,'mapBounds':map,'readableAsLiteralText':True,'phoneMapLabel':label,'moneyUnchanged':abs(page.evaluate('__nameProbe.money()')-before['total'])<.001}
 assert results['district']['moneyUnchanged']
 # Real civic-place creation then municipal-title rename through the actual register.
 page2=browser.new_page(viewport={'width':390,'height':844},has_touch=True);page2.set_default_timeout(5000);page2.on('pageerror',lambda e:errors.append(str(e)));page2.set_content(html);page2.add_script_tag(content=script);page2.locator('#newTown').click();page2.locator('#pause').click();page2.evaluate("__townTest.reset('settlement',42);__townTest.step(2)");page2.evaluate('__nameProbe.projects()');assert page2.locator('[data-public-place=square]').count()>0
 page2.locator('[data-public-place=square]').click();page2.locator('#publicPlaceName').fill('Harbour Steps');page2.locator('[data-event-choice="0"]').click()
 place=page2.evaluate("()=>JSON.parse(__townTest.save()).publicPlaces.places[0]")
 public_money_before=page2.evaluate('__nameProbe.money()')
 page2.evaluate('__nameProbe.projects()')
 assert page2.locator('[data-rename-place]').count()==1
 page2.locator('[data-rename-place]').click();page2.locator('[data-event-choice="1"]').click()
 assert page2.evaluate("()=>JSON.parse(__townTest.save()).publicPlaces.places[0].name")==place['name']
 page2.locator('[data-rename-place]').click();page2.locator('[aria-label="New public place name"]:visible').fill('');page2.locator('[data-event-choice="0"]').click()
 assert page2.evaluate("()=>JSON.parse(__townTest.save()).publicPlaces.places[0].name")==place['name']
 page2.locator('[data-rename-place]').click();page2.locator('[aria-label="New public place name"]:visible').fill('x'*49);page2.locator('[data-event-choice="0"]').click()
 assert page2.evaluate("()=>JSON.parse(__townTest.save()).publicPlaces.places[0].name")==place['name']
 page2.locator('[data-rename-place]').click();page2.locator('[aria-label="New public place name"]:visible').fill(name);page2.locator('[data-event-choice="0"]').click()
 place_after=page2.evaluate("()=>JSON.parse(__townTest.save()).publicPlaces.places[0]")
 assert place_after['name']==name and place_after['building']==place['building']
 assert page2.evaluate('__nameProbe.money()')==public_money_before
 assert page2.locator('#panelBody img').count()==0 and name in page2.locator('#panelBody').inner_text()
 assert page2.evaluate('__townTest.validate().ok')
 save=page2.evaluate('__townTest.save()');assert page2.evaluate('s=>__townTest.load(s)',save)
 assert page2.evaluate("()=>JSON.parse(__townTest.save()).publicPlaces.places[0].name")==name
 results['publicPlace']={'buildingIdStable':place_after['building']==place['building'],'municipalTitle':True,'moneyUnchanged':True,'unicodeAndLiteralText':True,'saveLoad':True}
 assert not errors,errors
 out=ROOT/'docs/previews/urban8';out.mkdir(parents=True,exist_ok=True)
 (out/'city-naming.json').write_text(json.dumps(results,indent=2)+'\n')
 page2.screenshot(path=str(out/'city-naming-phone.png'),full_page=True)
 browser.close()
print('PASS owned district/place rename, unowned rejection, cancel, invalid lengths, Unicode literal text, map viewport, stable IDs and save/load')
