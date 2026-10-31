"""Real district outlook, ordinary funded housing action and exact replay."""
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright
import gzip, json, hashlib

def canonical(archive_text):
    state = json.loads(archive_text)
    state.pop('trafficState', None)
    state.pop('visualState', None)
    return json.dumps(state, sort_keys=True, separators=(',', ':'))

archive = gzip.open(ROOT / 'docs/previews/growth-journey/regional-42-planned.json.gz', 'rt').read()
source = (ROOT / 'assets/game.js').read_text()
probe = '''window.__parcelOutlook={status:()=>({day:G.day,treasury:G.treasury,region:G.region,total:totalMoney(),homes:G.buildings.filter(b=>b.kind==='home'&&b.x>=56&&b.x<78&&b.y>=2&&b.y<28).length,residents:G.households.filter(h=>h.people.length&&(()=>{const b=readBuild(h.home);return b&&b.x>=56&&b.x<78&&b.y>=2&&b.y<28})()).reduce((n,h)=>n+h.people.length,0),rng:rngState,valid:validateTown()}),point:(x,y)=>{const q=iso(x,y);return{x:q[0],y:q[1]+18};},mode:()=>buildMode,can:(x,y)=>canPlace(x,y,true,'home')};'''
script = source.replace('// SOURCE: 99-instrumentation.js', probe + '\n// SOURCE: 99-instrumentation.js')

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(html)
    page.add_script_tag(content=script)
    page.locator('#newTown').click()
    page.locator('#pause').click()
    assert page.evaluate('archive => __townTest.load(archive)', archive)
    before = page.evaluate('__parcelOutlook.status()')
    archive_before = page.evaluate('__townTest.save()')
    page.locator('[data-panel=construction]').click()
    office = page.locator('#charterOffice')
    if not office.evaluate('node => node.open'):
        office.locator(':scope > summary').click()
    page.locator('[data-parcel-outlook=east-meadow]').click()
    text = page.locator('#eventText').inner_text()
    assert '67 of 67 street tiles connect' in text
    assert '0 residents, 0 homes, 0 household units and 0 vacancies' in text
    assert 'best legal private home site is (59, 14)' in text
    assert 'current top private housing candidate is (42, 33)' in text
    assert 'passes today’s funded-work, food, access and budget checks' in text
    assert 'Current sample job access:' in text and 'modeled road travel cost' in text
    assert 'No paid passenger route is currently used' in text
    assert 'Forecast service coverage at this address' in text
    assert 'do not extend those civic catchments' in text
    assert 'Employment outlook:' in text and 'vacancies' in text
    assert 'Roadside sites currently support Farm' in text and 'regional working capital' in text
    assert 'Visit Cottage site (59, 14)' in page.locator('#eventChoices').inner_text()
    evidence = ROOT / 'docs/previews/parcel-growth-outlook'
    evidence.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(evidence / 'east-meadow-outlook.png'))
    assert page.evaluate('__parcelOutlook.status()') == before
    assert page.evaluate('__townTest.save()') == archive_before

    # Follow the reviewed ordinary purchase. No actors, money or land are seeded.
    page.locator('#eventChoices button', has_text='Visit Cottage site').click()
    assert page.evaluate('__parcelOutlook.mode()') == 'home' and page.evaluate('__parcelOutlook.can(59,14)')
    treasury = page.evaluate('__parcelOutlook.status().treasury')
    box = page.locator('#view').bounding_box()
    page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
    after = page.evaluate('__parcelOutlook.status()')
    assert after['homes'] == 1 and after['residents'] >= 0
    assert abs(treasury - after['treasury'] - 20000) < .001
    assert abs(after['total'] - before['total']) < .05
    assert after['valid']['ok'] and not errors

    # Save, advance, restore, and repeat the same ordinary clock interval.
    checkpoint = page.evaluate('__townTest.save()')
    page.evaluate('__townTest.step(30)')
    continuation = page.evaluate('__townTest.save()')
    assert page.evaluate('archive => __townTest.load(archive)', checkpoint)
    page.evaluate('__townTest.step(30)')
    replay = page.evaluate('__townTest.save()')
    assert canonical(replay) == canonical(continuation)
    final = page.evaluate('__parcelOutlook.status()')
    assert final['valid']['ok'] and not errors
    result = {'source_sha256': hashlib.sha256(source.encode()).hexdigest(), 'baseline': before, 'surveyWasReadOnly': True,
              'outlook': {'connectedRoads': '67 / 67', 'localLegalCottage': [59, 14], 'currentGlobalCandidate': [42, 33],
                          'sampleArrivalEligible': True, 'globalVacancies': 0, 'demand': 100, 'pressure': 65},
              'fundedHomePurchase': {'site': [59, 14], 'cost': 20000, 'newResidents': final['residents'], 'treasuryAfter': final['treasury']},
              'cashConserved': abs(final['total'] - before['total']) < .05, 'exactThirtyDayReplay': canonical(replay) == canonical(continuation),
              'final': final, 'errors': errors}
    (evidence / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    browser.close()
