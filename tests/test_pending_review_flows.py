"""Pending quotes stay bound to their site, town, price, and safe focus path."""
from pathlib import Path
import hashlib, json, re
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html

OUT = ROOT / 'reports' / 'pending-review8'
OUT.mkdir(parents=True, exist_ok=True)
source = (ROOT / 'assets' / 'game.js').read_text()
probe = '''window.__reviewAudit={
 tick:()=>{const before={day:G.day,treasury:G.treasury};tick();return {before,after:{day:G.day,treasury:G.treasury}}},
 openBudget:()=>openPanel('treasury'),
 selectParcel:id=>{parcelFocus=id},
 regionQuote:id=>{const p=ANNEX_PARCELS.find(p=>p.id===id);return p&&parcelSurvey(p)},
 restore:text=>window.__townArchive.restore(text)
};
// SOURCE: 99-instrumentation.js'''
bundle_sha256 = hashlib.sha256(source.encode()).hexdigest()
source = source.replace('// SOURCE: 99-instrumentation.js', probe)
results = {'sourceSha256': bundle_sha256, 'instrumentedSha256': hashlib.sha256(source.encode()).hexdigest(), 'scenarios': []}

def parsed_save(page):
    return json.loads(page.evaluate('__townTest.save()'))

def cost_in(text):
    match = re.search(r'\$([0-9,]+(?:\.\d+)?)', text)
    assert match, text
    return float(match.group(1).replace(',', ''))

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page(viewport={'width':844,'height':390}, has_touch=True)
    errors=[]
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(html)
    page.add_script_tag(content=source)
    page.locator('#townSeed').fill('42')
    page.locator('#newTown').click()
    page.locator('#pause').click()
    page.locator('[data-panel=construction]').click()
    page.locator('#charterOffice>summary').click()

    # A cancelled first parcel review returns focus to the same control and
    # leaves both the deed list and ordinary treasury unchanged.
    first=page.locator('[data-parcel-buy=east-meadow]')
    first.scroll_into_view_if_needed()
    first_text=first.inner_text();first_price=cost_in(first_text)
    before=parsed_save(page);cash=before['treasury']
    first.click()
    assert page.locator('#eventTitle').inner_text()=='Acquire East Meadow?'
    assert f'Pay ${first_price:,.0f}' in page.locator('#eventText').inner_text()
    page.keyboard.press('Escape')
    assert page.evaluate('document.activeElement===document.querySelector("[data-parcel-buy=east-meadow]")')
    assert parsed_save(page)['treasury']==cash and parsed_save(page)['charter']['owned']==[]

    # A different parcel gets its own current quote after cancellation.
    other=page.locator('[data-parcel-buy=river-reach]')
    other.scroll_into_view_if_needed()
    other_price=cost_in(other.inner_text())
    other.click()
    assert 'Lower River Reach' in page.locator('#eventTitle').inner_text()
    assert f'Pay ${other_price:,.0f}' in page.locator('#eventText').inner_text()
    assert page.evaluate('__townArchive.back()')
    assert page.evaluate('document.activeElement===document.querySelector("[data-parcel-buy=river-reach]")')
    assert parsed_save(page)['treasury']==cash and parsed_save(page)['charter']['owned']==[]

    # The review overlay blocks normal pointer routing; even if an underlying
    # report and parcel selection change through an external callback, the
    # visible East Meadow quote remains bound to East Meadow.
    first=page.locator('[data-parcel-buy=east-meadow]');first.scroll_into_view_if_needed();first.click()
    title=page.locator('#eventTitle').inner_text();body=page.locator('#eventText').inner_text()
    blocked=page.evaluate('''()=>{const b=document.querySelector('[data-parcel-buy="river-reach"]');b.scrollIntoView({block:'center'});const r=b.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return {buttonVisible:r.width>0,covered:!!hit?.closest('#eventDialog'),hit:hit?.id||hit?.className||hit?.tagName}}''')
    assert blocked['covered'], blocked
    tick=page.evaluate('__reviewAudit.tick()')
    assert tick['after']==tick['before'], tick
    page.evaluate("__reviewAudit.selectParcel('river-reach');__reviewAudit.openBudget()")
    assert page.locator('#eventDialog').is_visible()
    assert page.locator('#eventTitle').inner_text()==title and page.locator('#eventText').inner_text()==body
    assert page.locator('[data-event-choice="0"]').is_visible()
    page.locator('[data-event-choice="0"]').click()
    after=parsed_save(page)
    assert after['charter']['owned']==['east-meadow'] and after['charter']['deeds'][0]['id']=='east-meadow'
    assert before['treasury']-after['treasury']==first_price and after['region']-before['region']==first_price
    assert page.evaluate('document.activeElement.tagName+" "+document.activeElement.innerText')=='H3 East Meadow'
    page.evaluate('document.querySelector(\'#eventChoices button[data-event-choice="0"]\').click()')
    assert parsed_save(page)['treasury']==after['treasury'] and parsed_save(page)['charter']['owned']==['east-meadow']
    after_purchase=page.evaluate('__townTest.get()')
    results['scenarios'].append({'scenario':'annex quote and report interruption','displayedParcel':'East Meadow','displayedPrice':first_price,'pointerCovered':blocked['covered'],'pendingTickUnchanged':tick['after']==tick['before'],'actualDeed':after['charter']['owned'],'treasuryDelta':before['treasury']-after['treasury'],'regionCredit':after['region']-before['region'],'focusAfterPurchase':page.evaluate('document.activeElement.innerText')})

    # Save a second real town after buying East Meadow. Restoring it while the
    # first town's same deed review is pending must remove the stale purchase
    # button and show the recorded deed without charging again.
    page.evaluate("__townTest.reset('settlement',84)")
    page.locator('#charterOffice>summary').click()
    other_town_buy=page.locator('[data-parcel-buy=east-meadow]')
    quote_b=cost_in(other_town_buy.inner_text())
    other_town_buy.click()
    assert page.locator('#eventTitle').inner_text()=='Acquire East Meadow?'
    page.locator('[data-event-choice="0"]').click()
    archive_b=page.evaluate('__townTest.save()')
    restored_cash=json.loads(archive_b)['treasury']
    restored_deed_price=json.loads(archive_b)['charter']['deeds'][0]['price']
    page.evaluate("__townTest.reset('settlement',42)")
    page.locator('#charterOffice>summary').click()
    page.locator('[data-parcel-buy=east-meadow]').click()
    assert page.locator('#eventDialog').is_visible()
    assert page.evaluate('s=>__reviewAudit.restore(s)',archive_b)
    restored=parsed_save(page)
    assert page.locator('#eventDialog').is_hidden() and not page.evaluate('__townTest.get().pending')
    assert restored['scenario']=='settlement' and restored['charter']['owned']==['east-meadow']
    assert restored['treasury']==restored_cash
    loaded_focus=page.evaluate('document.activeElement.id')
    assert loaded_focus=='panelClose'
    page.locator('#charterOffice>summary').click()
    card=page.locator('[data-parcel-card=east-meadow]')
    assert 'DEED RECORDED' in card.inner_text() and f'Price paid\n${restored_deed_price:,.0f}' in card.inner_text()
    assert page.locator('[data-parcel-buy=east-meadow]').count()==0
    results['scenarios'].append({'scenario':'town restore during pending deed review','dialogRevoked':page.locator('#eventDialog').is_hidden(),'loadedScenario':restored['scenario'],'loadedDeedPrice':restored_deed_price,'loadedTreasury':restored['treasury'],'panelRefreshed':page.locator('[data-parcel-buy=east-meadow]').count()==0,'focusAfterLoad':loaded_focus})

    # Planning confirmations name their actual spatial target and price;
    # cancellation returns focus, while acceptance charges once and focuses
    # the updated planning report after its panel re-renders.
    page.evaluate("__townTest.reset('settlement',42)")
    page.locator('[data-panel=citizens]').click()
    page.locator('#panelBody [data-house]').first.click()
    page.locator('#panelBody details summary').first.click()
    plan=page.locator('[data-urban-plan]:not([disabled])').first
    plan_name=plan.inner_text();plan.click()
    modal=page.locator('#eventText').inner_text()
    assert 'centered at grid (' in modal and 'Pay $600' in modal
    plan_selector='[data-urban-plan="'+plan.get_attribute('data-urban-plan')+'"][data-urban-building="'+plan.get_attribute('data-urban-building')+'"]'
    plan_price=cost_in(modal);cash=page.evaluate('__townTest.get().treasury')
    page.keyboard.press('Escape')
    assert page.evaluate('s=>document.activeElement.matches(s)',plan_selector)
    assert page.evaluate('__townTest.get().treasury')==cash
    page.locator(plan_selector).click()
    page.locator('[data-event-choice="0"]').click()
    assert page.evaluate('__townTest.get().treasury')==cash-plan_price
    assert page.evaluate('document.activeElement.tagName+" "+document.activeElement.innerText')=='SUMMARY Change the 8 × 8 neighbourhood plan'
    page.evaluate('document.querySelector(\'#eventChoices button[data-event-choice="0"]\').click()')
    assert page.evaluate('__townTest.get().treasury')==cash-plan_price
    results['scenarios'].append({'scenario':'neighbourhood plan target and focus','targetGrid':re.search(r'grid \((\d+), (\d+)\)',modal).group(0),'plan':plan_name,'displayedPrice':plan_price,'treasuryDelta':cash-page.evaluate('__townTest.get().treasury'),'focusAfterPurchase':page.evaluate('document.activeElement.innerText')})

    # Brownfield review shows the identified business, coordinate and price.
    # Cancel and paid survey both return focus to a useful live control.
    page.evaluate("__townTest.reset('settlement',42)")
    page.locator('[data-panel=construction]').click();page.locator('#brownfieldOffice>summary').click()
    assessment=page.locator('#brownfieldOffice [data-brownfield-action=assess]:not([disabled])').first
    site_id=assessment.get_attribute('data-brownfield-id');site_name=page.evaluate('id=>{const s=JSON.parse(__townTest.save()),b=s.buildings.find(b=>b.id===+id);return s.firms[b.firm].name}',site_id)
    assessment.click()
    title=page.locator('#eventTitle').inner_text();body=page.locator('#eventText').inner_text()
    assert site_name in title and 'grid (' in title and 'Authorize $300' in body, (title,body)
    cash=page.evaluate('__townTest.get().treasury')
    page.keyboard.press('Escape')
    assert page.evaluate('id=>document.activeElement===document.querySelector("[data-brownfield-action=assess][data-brownfield-id="+JSON.stringify(id)+"]")',site_id)
    assert page.evaluate('__townTest.get().treasury')==cash
    page.locator('[data-brownfield-action=assess][data-brownfield-id="'+site_id+'"]').click()
    assert page.locator('#eventTitle').inner_text()==title and page.locator('#eventText').inner_text()==body
    page.locator('[data-event-choice="0"]').click()
    brownfield=parsed_save(page)['brownfields'][-1]
    assert brownfield['id']==int(site_id) and brownfield['status']=='assessed'
    assert cash-page.evaluate('__townTest.get().treasury')==300
    assert page.evaluate('document.activeElement.matches("#brownfieldOffice>summary")')
    page.evaluate('document.querySelector(\'#eventChoices button[data-event-choice="0"]\').click()')
    assert parsed_save(page)['brownfields'][-1]['status']=='assessed' and cash-page.evaluate('__townTest.get().treasury')==300
    results['scenarios'].append({'scenario':'brownfield assessment quote','target':title,'displayedPrice':300,'treasuryDelta':cash-page.evaluate('__townTest.get().treasury'),'recordedStatus':brownfield['status'],'focusAfterPurchase':'brownfield office'})

    assert not errors, errors
    browser.close()

(OUT/'controls.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
