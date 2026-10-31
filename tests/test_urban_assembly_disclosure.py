"""Actual land-assembly dialogs preserve a funded household route and disclose farm loss."""
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright
import json, gzip, hashlib

source = (ROOT / 'assets/game.js').read_text()
probe = '''window.__assembly={
 point:(x,y)=>{const q=iso(x,y);return{x:q[0],y:q[1]+18};},
 farm:()=>G.firms.filter(f=>f.kind==='farm'&&!f.closed).map(f=>{const b=readBuild(f.building);return{f:f.id,b:b&&{id:b.id,x:b.x,y:b.y},q:b&&urbanClearanceQuote(b.x,b.y)}}).find(v=>v.q?.ok&&v.q.total<=G.treasury),
 home:()=>G.buildings.filter(b=>b.kind==='home'&&G.households[b.hh]?.people.length&&G.households[b.hh].people.some(id=>G.people[id]?.job>=0)).map(b=>({b,q:urbanClearanceQuote(b.x,b.y)})).find(v=>v.q.ok&&v.q.relocationReview?.length),
 hasReserve:()=>G.buildings.some(b=>b.relocationReserve&&b.kind==='home'),
 farmBefore:s=>{const g=G,f=g.firms[s.f],b=g.buildings.find(b=>b.id===s.b.id);return{people:g.people.map(p=>[p.id,p.hh,p.deceased,p.movedAway]),workers:f.workers.slice(),stock:{...f.stock},fields:Object.keys(g.fieldOwner).filter(id=>g.fieldOwner[id]===f.id),fieldCount:g.fieldCount[f.id],owner:b.title,transit:JSON.stringify(g.transit),roads:g.tiles.map((v,i)=>v===1?i:-1).filter(i=>i>=0),total:totalMoney()};},
 farmAfter:s=>{const g=G,f=g.firms[s.f];return{closed:f.closed,building:g.buildings.some(b=>b.id===s.b.id),workers:f.workers.slice(),stock:{...f.stock},fieldOwners:Object.values(g.fieldOwner).filter(id=>id===f.id).length,people:g.people.map(p=>[p.id,p.hh,p.deceased,p.movedAway]),transit:JSON.stringify(g.transit),roads:g.tiles.map((v,i)=>v===1?i:-1).filter(i=>i>=0),total:totalMoney(),valid:validateTown(),goods:goodsBalance()};},
 moved:s=>{const g=G,h=g.households[s.q.households[0]],dest=g.buildings.find(b=>b.id===h.home),workers=h.people.filter(id=>g.people[id].job>=0&&!g.people[id].commuteBlocked).map(id=>({person:id,firm:g.people[id].job,trip:migrationCanReach(dest,g.firms[g.people[id].job])}));return{home:h.home,people:h.people.slice(),dest:{id:dest.id,x:dest.x,y:dest.y,municipal:dest.municipalRehousing,reserved:dest.relocationReserve},workers,services:{health:serviceAccess('health').households.find(v=>v.id===h.id),school:serviceAccess('school').households.find(v=>v.id===h.id)}};},
 state:()=>({day:G.day,treasury:G.treasury,total:totalMoney(),roads:G.tiles.map((v,i)=>v===1?i:-1).filter(i=>i>=0),transit:JSON.stringify(G.transit),people:G.people.map(p=>[p.id,p.hh,p.deceased,p.movedAway]),valid:validateTown()}),
 treasury:()=>G.treasury,
};'''
script = source.replace('// SOURCE: 99-instrumentation.js', probe + '\n// SOURCE: 99-instrumentation.js')

def open_property(page, site):
    point = page.evaluate('s=>__assembly.point(s.x,s.y)', site)
    page.evaluate('p=>__townTest.capture({x:p.x,y:p.y,zoom:.9})', point)
    box = page.locator('#view').bounding_box()
    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)

def canonical(text):
    state = json.loads(text)
    state.pop('trafficState', None)
    state.pop('visualState', None)
    state['fieldCount'] = {k:v for k,v in state.get('fieldCount', {}).items() if v}
    return json.dumps(state, sort_keys=True, separators=(',', ':'))

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page(viewport={'width': 1280, 'height': 850})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(html)
    page.add_script_tag(content=script)
    page.locator('#newTown').click()
    page.locator('#pause').click()

    # A legal, ordinary treasury-funded farm clearance through its real inspector.
    page.evaluate("__townTest.reset('settlement',42)")
    farm = page.evaluate('__assembly.farm()')
    assert farm, 'No affordable, cargo-settled farm is available at founding.'
    before = page.evaluate('__townTest.save()')
    farm_before = page.evaluate('s=>__assembly.farmBefore(s)', farm)
    open_property(page, farm['b'])
    page.locator(f'[data-urban-clear="{farm["b"]["id"]}"]').click()
    disclosure = page.locator('#eventText').inner_text()
    assert 'permanently closes' in disclosure and f'{len(farm_before["fields"])} productive crop plots' in disclosure
    assert 'stored grain is liquidated' in disclosure and 'farm jobs end' in disclosure
    page.locator('[data-event-choice="1"]').click()
    cancelled = page.evaluate('__townTest.save()')
    a,b=json.loads(before),json.loads(cancelled)
    # Inspecting lazily computes roadMetrics/derived approval, neither of which
    # is part of the land assembly transaction. Check persistent affected data.
    for key in ('buildings','firms','fieldOwner','fieldCount','people','households','titles','treasury','region','cumulative'):
        assert a.get(key)==b.get(key), key
    page.locator(f'[data-urban-clear="{farm["b"]["id"]}"]').click()
    page.locator('[data-event-choice="0"]').click()
    farm_after = page.evaluate('s=>__assembly.farmAfter(s)', farm)
    assert farm_after['closed'] and not farm_after['building'] and farm_after['fieldOwners'] == 0
    assert farm_after['people'] == farm_before['people'] and farm_after['people']
    assert farm_after['transit'] == farm_before['transit'] and farm_after['roads'] == farm_before['roads']
    assert abs(farm_after['total'] - farm_before['total']) < .05 and farm_after['valid']['ok']
    assert all(abs(row['error']) < .001 for row in farm_after['goods'])
    farm_checkpoint = page.evaluate('__townTest.save()')
    page.evaluate('__townTest.step(30)')
    farm_next = page.evaluate('__townTest.save()')
    assert page.evaluate('s=>__townTest.load(s)', farm_checkpoint)
    page.evaluate('__townTest.step(30)')
    assert canonical(page.evaluate('__townTest.save()')) == canonical(farm_next)

    # Commission a real reserved replacement home, then clear an occupied home
    # through the normal map inspector and verify destination/job/service routes.
    page.evaluate("__townTest.reset('settlement',42)")
    opening = page.evaluate('__assembly.state()')
    page.locator('[data-panel=construction]').click()
    page.locator('#urbanPlanningOffice>summary').click()
    page.locator('[data-urban-rehousing]').click()
    page.locator('[data-event-choice="0"]').click()
    assert page.evaluate('__assembly.treasury()') < opening['treasury']
    page.evaluate('__townTest.step(90)')
    assert page.evaluate('__assembly.hasReserve()')
    home = page.evaluate('__assembly.home()')
    assert home and home['q']['relocationReview']
    review = home['q']['relocationReview'][0]
    assert review['reserved'] and review['workers']
    assert all(w['reachable'] for w in review['workers'])
    page.locator('[data-panel=construction]').click()
    source_home = {'x': home['b']['x'], 'y': home['b']['y']}
    open_property(page, source_home)
    page.locator(f'[data-urban-clear="{home["b"]["id"]}"]').click()
    warning = page.locator('#eventText').inner_text()
    assert f'at ({review["x"]}, {review["y"]})' in warning and 'reserved municipal home' in warning
    assert 'commutes remain reachable' in warning and 'nearest public clinic' in warning and 'school' in warning
    page.screenshot(path=str(ROOT / 'docs/previews/parcel-growth-outlook/relocation-disclosure.png'))
    home_before = page.evaluate('__assembly.state()')
    page.locator('[data-event-choice="0"]').click()
    home_after = page.evaluate('__assembly.state()')
    moved = page.evaluate('s=>__assembly.moved(s)', home)
    assert moved['dest']['id'] == review['destination'] and moved['dest']['municipal'] and not moved['dest']['reserved']
    assert moved['people'] and moved['workers'] and all(w['trip'] for w in moved['workers'])
    assert home_after['roads'] == home_before['roads'] and home_after['transit'] == home_before['transit']
    assert abs(home_after['total'] - home_before['total']) < .05 and home_after['valid']['ok']
    home_checkpoint = page.evaluate('__townTest.save()')
    page.evaluate('__townTest.step(30)')
    home_next = page.evaluate('__townTest.save()')
    assert page.evaluate('s=>__townTest.load(s)', home_checkpoint)
    page.evaluate('__townTest.step(30)')
    assert canonical(page.evaluate('__townTest.save()')) == canonical(home_next)
    assert not errors, errors
    result = {'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
              'farmClearance': {'cancelWasReadOnly': True, 'fieldsPermanentlyReleased': len(farm_before['fields']), 'firmClosed': farm_after['closed'],
                                'peopleAndJobsRetainedAsResidents': len(farm_after['people']), 'roadAndTransitUnchanged': True, 'goodsConserved': True,
                                'cashConserved': abs(farm_after['total'] - farm_before['total']) < .05, 'exactThirtyDayReplay': True},
              'homeReplacement': {'paidMunicipalReserve': True, 'destination': moved['dest'], 'reachableWorkers': len(moved['workers']),
                                  'clinicRoute': moved['services']['health']['distance'], 'schoolRoute': moved['services']['school']['distance'],
                                  'roadsAndTransitUnchanged': True, 'cashConserved': abs(home_after['total'] - home_before['total']) < .05,
                                  'exactThirtyDayReplay': True}, 'errors': errors}
    evidence = ROOT / 'docs/previews/parcel-growth-outlook'
    (evidence / 'assembly-results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    browser.close()
