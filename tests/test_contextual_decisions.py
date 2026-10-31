"""Phone decision routes are contextual, readable and never enact or spend."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json,http.server,functools,threading
source=(ROOT/'assets/game.js').read_text();probe='window.__decisionTest={farm:()=>G.buildings.find(b=>b.kind==="farm")?.id,inspect:id=>{selected={id};openPanel("inspect");}};'
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':844});p.set_default_timeout(10000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(status=200,content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')));p.goto('http://127.0.0.1:'+str(server.server_port)+'/assets/index.html');p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.step(2)');initial=p.evaluate('__townTest.save()');rows=[];out=ROOT/'reports/contextual-decisions';out.mkdir(parents=True,exist_ok=True)
 state=lambda:p.evaluate('JSON.parse(__townTest.save())')
 def panel(tab):
  if not(p.locator('#panel').evaluate('e=>e.classList.contains("show")')and'active'in(p.locator('[data-panel='+tab+']').get_attribute('class')or'')):p.locator('[data-panel='+tab+']').click()
 def hint(tab):
  panel(tab);h=p.locator('.decision-hint').first
  if not h.evaluate('e=>e.open'):h.locator('summary').click()
  return h
 checks=[('construction','charter','charterOffice'),('economy','suppliers','alternativeSuppliers'),('community','migration','migrationOffice'),('policies','outlook','serviceBudgetOutlook')]
 for width,height in [(320,740),(390,844),(568,320)]:
  p.set_viewport_size({'width':width,'height':height})
  for tab,route,target in checks:
   h=hint(tab);assert h.evaluate('e=>e.getBoundingClientRect().top<=document.querySelector("#panelBody").getBoundingClientRect().top+90');h.locator('summary').click();h.locator('summary').click();assert h.evaluate('e=>e.open');h.scroll_into_view_if_needed();assert h.locator('summary').bounding_box()['height']>=40;assert all(button.bounding_box()['height']>=42 for button in h.locator('button').all());assert not p.evaluate('document.documentElement.scrollWidth>innerWidth')
   contrast=h.evaluate('''e=>{const c=getComputedStyle(e),rgb=s=>s.match(/[\\d.]+/g).slice(0,3).map(Number),lum=a=>a.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0),a=lum(rgb(c.color)),b=lum(rgb(c.backgroundColor));return(Math.max(a,b)+.05)/(Math.min(a,b)+.05);}''');assert contrast>=4.5
   
   if width==390:p.screenshot(path=str(out/('context-'+tab+'-phone.png')))
   h.locator('[data-decision-route='+route+']').click();assert p.locator('#'+target).is_visible()
   if p.locator('#'+target).evaluate('e=>e.tagName==="DETAILS"'):assert p.locator('#'+target).evaluate('e=>e.open')
   rows.append({'viewport':[width,height],'panel':tab,'route':route,'contrast':contrast});p.keyboard.press('Escape');assert not p.locator('#panel').evaluate('e=>e.classList.contains("show")')
  hint('construction');p.screenshot(path=str(out/('land-choice-'+str(width)+'x'+str(height)+'.png')))
 hint('construction').locator('[data-decision-route=renewal]').click();assert p.locator('#brownfieldOffice').evaluate('e=>e.open')
 hint('policies').locator('[data-decision-route=budget]').click();assert 'active' in p.locator('[data-panel=treasury]').get_attribute('class')
 hint('construction').locator('[data-decision-route=charter]').click();p.locator('[data-parcel-buy]:not([disabled])').first.click();assert p.evaluate('__townArchive.back()');assert not state()['charter']['owned']
 # Real reviewed contract and planning actions stay cancellable.
 hint('economy').locator('[data-decision-route=suppliers]').click();p.locator('#alternativeSuppliers [data-trade-offer]').click();assert p.locator('#eventDialog').is_visible();assert p.evaluate('__townArchive.back()');assert not state()['regionalTrade']['contracts']
 farm=p.evaluate('__decisionTest.farm()');assert farm;p.evaluate('id=>__decisionTest.inspect(id)',farm);assert 'Why this farm is still rural' in p.locator('.decision-hint').inner_text();p.locator('[data-decision-route=site-plan]').click();button=p.locator('[data-urban-plan=civic][data-urban-building="'+str(farm)+'"]');button.click();assert p.evaluate('__townArchive.back()')
 current=state();original=json.loads(initial)
 for key in ['treasury','debt','policy','charter','publicPlaces','civicCalendar']:assert current.get(key)==original.get(key),key
 saved=p.evaluate('__townTest.save()');assert p.evaluate('s=>__townTest.load(s)',saved);hint('community').locator('[data-decision-route=household]').click();assert 'household moving prospects' in p.locator('#panelBody').inner_text().lower();assert p.evaluate('__townTest.validate().ok');assert not errors,errors
 p.set_viewport_size({'width':390,'height':844});p.evaluate('id=>__decisionTest.inspect(id)',farm);p.screenshot(path=str(out/'farm-context-phone.png'));(out/'controls.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'routes':rows,'noPolicyOrCashMutation':True,'nativeBackCancelsActualReviews':True,'saveReloadRoutes':True,'errors':errors},indent=2)+'\n');b.close();server.shutdown()
print('PASS 320/390 portrait and small landscape decision routes, repeated controls, contrast, no overflow, actual-review Back/cancel, farm context, no spending/enactment and save reload')
