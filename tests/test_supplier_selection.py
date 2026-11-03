"""Buyer demand stays visible independently of preferred supplier, with real reserves."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();probe='window.__captureSupplierReview=()=>{window.__staleSupplierChoice=pendingEvent.choices[0].apply;};'
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_default_timeout(10000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click()
 def exchange():
  p.keyboard.press('Escape');p.locator('[data-panel=economy]').click();p.locator('#alternativeSuppliers').evaluate('e=>e.open=true')
 state=lambda:p.evaluate('JSON.parse(__townTest.save())')
 exchange();assert p.locator('#supplierGood').input_value()=='food';initial=p.locator('#alternativeSuppliers').inner_text();print(initial,flush=True);assert 'retained' in initial and 'Greyhaven' in initial
 p.locator('#supplierMarket').select_option('upland');assert 'food'not in p.locator('#supplierGood').locator('option').all_text_contents()
 p.locator('#supplierMarket').select_option('port');p.locator('#supplierGood').select_option('food');choices=p.locator('#supplierFirm option').all_text_contents();assert choices
 p.locator('#alternativeSuppliers [data-trade-offer]').click();p.keyboard.press('Escape');assert not state()['regionalTrade']['contracts']
 p.evaluate('__townTest.step(25)');exchange();later=p.locator('#alternativeSuppliers').inner_text();print(later,flush=True)
 p.locator('#alternativeSuppliers [data-trade-offer]').click();assert 'food' in p.locator('#eventText').inner_text();assert 'working reserve' in p.locator('#eventText').inner_text();p.evaluate('__captureSupplierReview()');snapshot=p.evaluate('__townTest.save()');p.keyboard.press('Escape');assert p.evaluate('s=>__townTest.load(s)',snapshot);before=state();p.evaluate('__staleSupplierChoice()');assert state()['regionalTrade']['contracts']==before['regionalTrade']['contracts'],'Stale review must not create an obligation'
 exchange();p.locator('#alternativeSuppliers [data-trade-offer]').click();assert p.locator('[data-event-choice="0"]').inner_text().find('forecast-sized')>=0;p.locator('[data-event-choice="0"]').click();contract=state()['regionalTrade']['contracts'][-1];assert contract['good']=='food'and contract['market']=='port';assert contract['quantity']>=10
 p.evaluate('__townTest.step(35)');settled=next(c for c in state()['regionalTrade']['contracts']if c['id']==contract['id']);assert settled['status']=='fulfilled',settled
 exchange();p.locator('#alternativeSuppliers').scroll_into_view_if_needed();out=ROOT/'reports/supplier-selection';out.mkdir(parents=True,exist_ok=True);p.screenshot(path=str(out/'food-comparison.png'));(out/'controls.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'initial':initial,'after25Days':later,'realFoodCommitment':contract,'settledFoodAgreement':settled,'errors':errors},indent=2)+'\n');assert not errors,errors;assert p.evaluate('__townTest.validate().ok');b.close()
print('PASS market/commodity/producer selection, real food reserve/forecast, cancel, stale-town review rejection and actual forecast-sized food commitment')
