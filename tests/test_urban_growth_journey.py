"""Ordinary-funded parcel expansion, farm transition and serviced rehousing UI journey."""
from pathlib import Path
import hashlib, json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html

source = (ROOT / 'assets/game.js').read_text()
probe = r'''window.__growthJourney={
 state:()=>({day:G.day,treasury:G.treasury,region:G.region,total:totalMoney(),population:G.stats.population,owned:G.charter.owned.slice(),valid:validateTown()}),
 homes:()=>G.buildings.filter(b=>b.kind==='home').map(b=>({id:b.id,x:b.x,y:b.y,households:G.households.filter(h=>h.home===b.id&&h.people.length).map(h=>h.id),quote:urbanClearanceQuote(b.x,b.y)})),
 farms:()=>G.firms.filter(f=>f.kind==='farm'&&!f.closed).map(f=>{const b=readBuild(f.building),d=urbanDescriptor(b.x,b.y);return{id:f.id,building:b.id,x:b.x,y:b.y,key:d.key,density:d.density,workers:f.workers.slice(),fields:G.fieldCount[f.id],stock:{...f.stock}}}),
 renewalAudit:()=>{const d=cityDemand(),all=G.firms.filter(f=>f.kind==='farm'&&!f.closed).map(f=>{const b=readBuild(f.building);return{id:f.id,density:b?urbanDescriptor(b.x,b.y).density:0,fields:G.fieldCount[f.id]||0,freight:(G.freight||[]).filter(s=>s.from===f.id||s.to===f.id).length,regionalCargo:(G.regionalTrade?.shipments||[]).filter(s=>s.firm===f.id).length,project:G.projects.some(p=>p.firmId===f.id),lastRelocated:b?.lastRelocated||null};}),eligible=G.firms.filter(f=>f.kind==='farm'&&!f.closed&&!G.projects.some(p=>p.firmId===f.id)&&!(G.freight||[]).some(s=>s.from===f.id||s.to===f.id)&&!(G.regionalTrade?.shipments||[]).some(s=>s.firm===f.id)).map(f=>({f,b:readBuild(f.building)})).filter(v=>v.b&&urbanDescriptor(v.b.x,v.b.y).density>=5&&G.day-(v.b.lastRelocated||-720)>=540&&footprintOf(v.b).length===4).sort((a,b)=>urbanDescriptor(b.b.x,b.b.y).landValue-urbanDescriptor(a.b.x,a.b.y).landValue||a.f.id-b.f.id),candidate=eligible[0];if(!candidate)return{demand:d,autoBuild:G.autoBuild,eligible:0,region:G.region,farms:all};const oldRng=rngState,oldFields=Object.keys(G.fieldOwner||{}).filter(id=>G.fieldOwner[id]===candidate.f.id&&G.landUse[id]===1).length,lots=buildableCandidates('business').filter(v=>canPlace(v.x,v.y,true,'farm')&&urbanDescriptor(v.x,v.y).density<1.5).map(v=>({x:v.x,y:v.y,plots:urbanRelocationFields(v.x,v.y,oldFields).length})),replacement=lots.find(v=>v.plots===oldFields),need=types.farm.cost+39000+8500+oldFields*200+Math.round(candidate.b.value*.35)+100000;const oldSiteApartment=canPlace(candidate.b.x,candidate.b.y,true,'apartment',candidate.b);rngState=oldRng;return{demand:d,autoBuild:G.autoBuild,eligible:eligible.length,candidate:{id:candidate.f.id,x:candidate.b.x,y:candidate.b.y,density:urbanDescriptor(candidate.b.x,candidate.b.y).density,fields:oldFields,plots:replacement?.plots??0},ruralLots:lots.length,suitableReplacement:!!replacement,region:G.region,requiredRegionalCapital:need,oldSiteApartment};},
 sites:(x,y)=>{const a=[];for(let yy=Math.max(0,y-6);yy<Math.min(T,y+7);yy++)for(let xx=Math.max(0,x-6);xx<Math.min(T,x+7);xx++)if(canPlace(xx,yy,true,'home'))a.push({x:xx,y:yy,density:urbanDescriptor(xx,yy).density});return a.sort((a,b)=>Math.abs(a.x-x)+Math.abs(a.y-y)-Math.abs(b.x-x)-Math.abs(b.y-y));},
 point:(x,y)=>{const q=iso(x,y),r=cv.getBoundingClientRect();return{x:r.left+cw/2+(q[0]-cam.x)*cam.zoom,y:r.top+ch/2+(q[1]+18-cam.y)*cam.zoom};},
 center:(x,y)=>{const q=iso(x,y);cam={x:q[0],y:q[1]+18,zoom:.9};dirty=true;},
 can:(kind,x,y)=>canPlace(x,y,true,kind),
 roadPlan:()=>{const cells=[];for(let y=26;y>=14;y--){const id=roadId(55,y);if(G.tiles[id]===1)continue;if(![0,3].includes(cityCell(55,y))||G.landUse[id]||buildingAt(55,y))return {ok:false,blocked:[55,y]};cells.push([55,y]);}for(let x=56;x<=58;x++){const id=roadId(x,14);if(G.tiles[id]===1)continue;if(![0,3].includes(cityCell(x,14))||G.landUse[id]||buildingAt(x,14))return {ok:false,blocked:[x,14]};cells.push([x,14]);}return {ok:true,cells,cost:cells.length*buildCost.road};},
 edgeRoadPlan:()=>{const cells=[];for(let y=13;y>=10;y--){const id=roadId(55,y);if(G.tiles[id]===1)continue;if(![0,3].includes(G.tiles[id])||!charterOwns(55,y)||G.landUse[id]||buildingAt(55,y))return {ok:false,blocked:[55,y]};cells.push([55,y]);}for(let x=56;x<=125;x++){const id=roadId(x,10);if(G.tiles[id]===1)continue;if(![0,3].includes(G.tiles[id])||!charterOwns(x,10)||G.landUse[id]||buildingAt(x,10))return {ok:false,blocked:[x,10]};cells.push([x,10]);}return {ok:true,cells,cost:cells.length*buildCost.road};},
 roadReach:(id)=>{const net=graph(),home=net.portals.get(id),hall=net.portals.get(G.buildings.find(b=>b.kind==='townhall')?.id);return home==null||hall==null?null:roadDistance(home,hall);},
 serviceRoadDistances:(id)=>{const net=graph(),home=net.portals.get(id),nearest=kind=>Math.min(Infinity,...G.buildings.filter(b=>b.kind===kind&&isPublicFacility(b)).map(b=>{const port=net.portals.get(b.id);return home==null||port==null?Infinity:roadDistance(home,port)}));return{clinic:nearest('clinic'),school:nearest('school')};},
 treasury:()=>G.treasury,
 parcelPrice:(id)=>parcelSurvey(ANNEX_PARCELS.find(p=>p.id===id)).price,
 plan:(x,y)=>ensureUrban().zones[urbanBlockKey(x,y)],
 planAt:(x,y)=>urbanDescriptor(x,y).plan,
 density:(x,y)=>urbanDescriptor(x,y).density,
 farmDensity:(id)=>{const f=G.firms[id],b=f&&readBuild(f.building);return b?urbanDescriptor(b.x,b.y).density:null;},
 homeAt:(x,y)=>G.buildings.find(b=>b.kind==='home'&&b.x===x&&b.y===y)?.id??null,
 clinicAt:(x,y)=>G.buildings.find(b=>b.kind==='clinic'&&b.x===x&&b.y===y)?.id??null,
 kindAt:(kind,x,y)=>G.buildings.find(b=>b.kind===kind&&b.x===x&&b.y===y)||null,
 buildingExists:(id)=>G.buildings.some(b=>b.id===id),
 household:(id)=>{const h=G.households[id];return h&&{id:h.id,home:h.home,people:h.people.slice(),income:h.income,tax:h.tax,cash:h.cash,workers:h.people.map(id=>({id,job:G.people[id]?.job,blocked:G.people[id]?.commuteBlocked}))};},
 profile:()=>Object.values(urbanSpatial().profiles).map(p=>({key:p.key,character:p.character,incomeBand:p.incomeBand,people:urbanSpatial().blocks[p.key].residents,perPersonIncome:p.perPersonIncome,rentBurden:p.rentBurden,condition:p.condition})),
 selectFarm:id=>{const f=G.firms[id];selected={id:f.building};openPanel('inspect');},
 farmQuote:id=>urbanFarmRenewalQuote(id),
 renewalProject:()=>G.projects.find(p=>p.urbanRenewal)||null,
 staleQuote:id=>{const q=urbanFarmRenewalQuote(id),before=archivePayload(),result=urbanFarmRenewal(cityDemand(),id,q.reviewKey+'changed');return {result,unchanged:before===archivePayload()};},
 fence:(id,flag)=>{const q=urbanFarmRenewalQuote(id);if(!q.ok)throw Error(q.reason);const before=archivePayload();if(flag==='simulationTickFailed')simulationTickFailed=true;else simulationTickActive=true;let result;try{result=urbanFarmRenewal(cityDemand(),id,q.reviewKey)}finally{simulationTickFailed=false;simulationTickActive=false}return{result,unchanged:before===archivePayload()};},
 snapshot:()=>__townTest.save(),
};'''
script = source.replace('// SOURCE: 99-instrumentation.js', probe + '\n// SOURCE: 99-instrumentation.js')
result = {'source_sha256': hashlib.sha256(source.encode()).hexdigest()}

def canonical(text):
    data = json.loads(text)
    return json.dumps(data, sort_keys=True, separators=(',', ':'))

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.set_default_timeout(15000)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(html)
    page.add_script_tag(content=script)
    page.locator('#newTown').click()
    page.locator('#pause').click()
    # A fixed ordinary settlement seed makes the long natural interval replayable;
    # no cash, households, buildings, crops, workers or businesses are injected.
    page.evaluate("__townTest.reset('settlement',42)")
    initial = page.evaluate('__growthJourney.state()')
    def open_construction():
        tab = page.locator('[data-panel=construction]')
        if 'active' not in (tab.get_attribute('class') or ''):
            tab.click()
    open_construction()
    charter = page.locator('#charterOffice')
    charter.locator(':scope > summary').click()

    deed_prices = {}
    for parcel in ('east-meadow', 'county-ridge'):
        button = page.locator(f'[data-parcel-buy="{parcel}"]')
        price = page.evaluate('__growthJourney.parcelPrice', parcel)
        deed_prices[parcel] = price
        assert not button.is_disabled()
        button.click()
        page.locator('[data-event-choice="0"]').click()
    shortfall = page.locator('[data-parcel-card="belt-78-2"]')
    third = shortfall.locator('[data-parcel-buy]')
    assert third.is_disabled() and 'Treasury shortfall:' in shortfall.inner_text()
    shortfall_at_start = page.evaluate("id=>__growthJourney.parcelPrice(id)-__growthJourney.treasury()", 'belt-78-2')
    after_two = page.evaluate('__growthJourney.state()')
    assert after_two['owned'] == ['east-meadow', 'county-ridge']
    assert abs(after_two['total'] - initial['total']) < .05

    # Keep the charter panel open while the natural economy replenishes the
    # treasury. Its disabled control and quote must recover without reopening.
    page.evaluate('__townTest.step(2160)')
    six_year = page.evaluate('__growthJourney.state()')
    assert six_year['day'] == 2161 and six_year['treasury'] >= 40224
    assert not third.is_disabled() and page.locator('[data-parcel-funds="belt-78-2"]').is_hidden()
    third.click()
    page.locator('[data-event-choice="0"]').click()
    after_three = page.evaluate('__growthJourney.state()')
    assert after_three['owned'] == ['east-meadow', 'county-ridge', 'belt-78-2']
    assert abs(after_three['total'] - initial['total']) < .05 and after_three['valid']['ok']
    page.evaluate('__townTest.load(__townTest.save())')

    # Deeds grant land rights, not roads. Extend an ordinary municipal road
    # from the connected town spine to the reviewed East Meadow cottage site.
    road_plan = page.evaluate('__growthJourney.roadPlan()')
    assert road_plan['ok'], road_plan
    open_construction()
    page.locator('[data-build=road]').click()
    page.evaluate('__growthJourney.center(56,20)')
    for x, y in road_plan['cells']:
        point = page.evaluate('(q)=>__growthJourney.point(q[0],q[1])', [x,y])
        page.mouse.click(point['x'], point['y'])
    assert page.evaluate("__growthJourney.can('home',59,14)")

    # Place one ordinary-funded cottage at the reviewed East Meadow site, then
    # record the residential plan through the mayor's actual planning dialog.
    assert page.evaluate("__growthJourney.can('home',59,14)")
    open_construction()
    page.evaluate('__growthJourney.center(59,14)')
    page.locator('[data-build=home]').click()
    point = page.evaluate('__growthJourney.point(59,14)')
    page.mouse.click(point['x'], point['y'])
    cottage = page.evaluate('__growthJourney.homeAt(59,14)')
    assert cottage is not None
    after_cottage = page.evaluate('__growthJourney.state()')
    assert abs(after_three['treasury'] - road_plan['cost'] - after_cottage['treasury'] - 20000) < .001
    open_construction()
    page.locator('[data-build=""]').click()
    page.evaluate("__growthJourney.center(59,14)")
    point = page.evaluate('__growthJourney.point(59,14)')
    page.mouse.click(point['x'], point['y'])
    page.locator('summary', has_text='Change the 8 × 8 neighbourhood plan').click()
    page.locator('[data-urban-plan=residential]').click()
    page.locator('[data-event-choice="0"]').click()
    plan = page.evaluate('__growthJourney.plan(59,14)')
    assert plan['plan'] == 'residential'

    # Move one extant farm's block past the residential density threshold using
    # paid homes, then let the ordinary monthly renewal system decide whether
    # the site is viable. No crop titles, workers or stocks are altered by test.
    farms_before = page.evaluate('__growthJourney.farms()')
    farm = max(farms_before, key=lambda f: f['density'])
    page.evaluate('(id)=>__growthJourney.selectFarm(id)', farm['id'])
    page.locator('summary', has_text='Change the 8 × 8 neighbourhood plan').click()
    page.locator('[data-urban-plan=residential]').click()
    page.locator('[data-event-choice="0"]').click()
    assert page.evaluate('(q)=>__growthJourney.planAt(q.x,q.y)', farm) == 'residential'
    extra_homes = []
    while len(extra_homes) < 6 and page.evaluate('(id)=>{const d=__growthJourney.farmDensity(id);return d!=null&&d<5}', farm['id']):
        current_farm = next(f for f in page.evaluate('__growthJourney.farms()') if f['id'] == farm['id'])
        candidates = page.evaluate('(f)=>__growthJourney.sites(f.x,f.y)', current_farm)
        site = next((q for q in candidates if page.evaluate('(q)=>__growthJourney.can("home",q.x,q.y)', q)), None)
        if not site:
            break
        if page.evaluate('(q)=>__growthJourney.can("home",q.x,q.y)', site):
            open_construction()
            page.locator('[data-build=home]').click()
            page.evaluate('(q)=>__growthJourney.center(q.x,q.y)', site)
            point = page.evaluate('(q)=>__growthJourney.point(q.x,q.y)', site)
            page.mouse.click(point['x'], point['y'])
            made = page.evaluate('(q)=>__growthJourney.homeAt(q.x,q.y)', site)
            if made is not None:
                extra_homes.append({'site': [site['x'], site['y']], 'building': made, 'cost': 20000})
    if extra_homes:
        page.evaluate('__townTest.step(540)')
    farms_after = page.evaluate('__growthJourney.farms()')
    farm_audit_at_attempt = page.evaluate('__growthJourney.renewalAudit()')
    farm_candidate = next((f for f in farms_after if f['id'] == farm['id']), None)
    farm_review = page.evaluate('id=>__growthJourney.farmQuote(id)', farm['id'])
    assert farm_review['ok'], farm_review
    stale = page.evaluate('id=>__growthJourney.staleQuote(id)',farm['id'])
    assert stale['result']['ok'] is False and stale['unchanged'], stale
    # Source-matched valid proposal makes the failure-fence checks meaningful.
    fence_archive = page.evaluate('__townTest.save()')
    Path('/tmp/townledger-growth-farm-review.json').write_text(fence_archive)
    result['manualBoundaryGuards'] = []
    result['staleQuoteAtomic'] = stale
    for flag in ('simulationTickFailed', 'simulationTickActive'):
        fence = browser.new_page()
        fence.set_content(html)
        fence.add_script_tag(content=script)
        fence.locator('#newTown').click()
        fence.locator('#pause').click()
        assert fence.evaluate('s=>__townTest.load(s)', fence_archive)
        check = fence.evaluate('({id,flag})=>__growthJourney.fence(id,flag)', {'id':farm['id'],'flag':flag})
        fence.close()
        assert check['result']['ok'] is False and check['unchanged'], (flag,check)
        result['manualBoundaryGuards'].append({'flag':flag,**check})
    farm_readonly = page.evaluate('__growthJourney.snapshot()')
    page.evaluate('(id)=>__growthJourney.selectFarm(id)', farm['id'])
    button = page.locator(f'[data-urban-farm-renew="{farm["id"]}"]')
    assert button.count() == 1
    button.click()
    review_text = page.locator('#eventText').inner_text()
    assert 'active crop titles' in review_text and 'working reserve' in review_text and 'not guaranteed' in review_text
    page.locator('[data-event-choice="1"]').click()
    assert page.evaluate('__growthJourney.snapshot()') == farm_readonly
    page.evaluate('(id)=>__growthJourney.selectFarm(id)', farm['id'])
    page.locator(f'[data-urban-farm-renew="{farm["id"]}"]').click()
    page.locator('[data-event-choice="0"]').click()
    after_manual_renewal = page.evaluate('(id)=>__growthJourney.farms().find(f=>f.id===id)', farm['id'])
    assert after_manual_renewal and (after_manual_renewal['x'], after_manual_renewal['y']) != (farm['x'], farm['y'])
    assert after_manual_renewal['fields'] == farm_candidate['fields'] and after_manual_renewal['workers'] == farm_candidate['workers'] and after_manual_renewal['stock'] == farm_review['stock'], {'before': farm_candidate, 'quote': farm_review, 'after': after_manual_renewal}
    manual_committed = page.evaluate('__townTest.save()')
    assert page.evaluate('s=>__townTest.load(s)', manual_committed)
    assert canonical(page.evaluate('__townTest.save()')) == canonical(manual_committed), 'Immediate farm-relocation cold state changed'
    result['immediateManualColdCompleteStateIdentical'] = True
    renewal_project = page.evaluate('__growthJourney.renewalProject()')
    assert renewal_project and renewal_project['target'] == 'apartment' and renewal_project['units'] == 4
    farm_after = after_manual_renewal
    moved_farms = []
    for before_farm in farms_before:
        after_farm = next((f for f in farms_after if f['id'] == before_farm['id']), None)
        if after_farm and (after_farm['x'], after_farm['y']) != (before_farm['x'], before_farm['y']):
            assert after_farm['fields'] == before_farm['fields'] and len(after_farm['workers']) == len(before_farm['workers'])
            moved_farms.append({'before': before_farm, 'after': after_farm})
    farm_after = next((f for f in farms_after if f['id'] == farm['id']), None)
    farm_relocated = bool(farm_after and (farm_after['x'], farm_after['y']) != (farm['x'], farm['y']))
    if farm_relocated:
        assert farm_after['fields'] == farm['fields'] and len(farm_after['workers']) == len(farm['workers'])

    # Find a normal occupied home with a lawful affordable replacement quote.
    homes = page.evaluate('__growthJourney.homes()')
    target = next((h for h in homes if h['households'] and h['quote']['ok'] and h['quote']['total'] < page.evaluate('__growthJourney.treasury()') and page.evaluate('(q)=>__growthJourney.planAt(q.x,q.y)!=="civic"',h)), None)
    assert target, 'Natural settlement has no affordable, commute-preserving assembly site.'
    original_household = page.evaluate('id=>__growthJourney.household(id)', target['households'][0])
    open_construction()
    page.locator('[data-build=""]').click()
    page.evaluate('(q)=>__growthJourney.center(q.x,q.y)', target)
    point = page.evaluate('(q)=>__growthJourney.point(q.x,q.y)', target)
    page.mouse.click(point['x'], point['y'])
    assert page.locator(f'[data-urban-clear="{target["id"]}"]').count() == 1
    # Record a civic reserve for the service before assembling the occupied lot.
    page.locator('summary', has_text='Change the 8 × 8 neighbourhood plan').click()
    page.locator('[data-urban-plan=civic]').click()
    page.locator('[data-event-choice="0"]').click()
    page.locator(f'[data-urban-clear="{target["id"]}"]').click()
    dialog_text = page.locator('#eventText').inner_text()
    assert 'compensation' in dialog_text.lower() and 'replacement' in dialog_text.lower()
    pre_clear = page.evaluate('__growthJourney.state()')
    page.locator('[data-event-choice="0"]').click()
    after_clear = page.evaluate('__growthJourney.state()')
    moved = page.evaluate('id=>__growthJourney.household(id)', original_household['id'])
    assert moved and moved['home'] != original_household['home'] and moved['people'] == original_household['people']
    assert abs(pre_clear['treasury'] - after_clear['treasury'] - target['quote']['total']) < .05
    assert all(w['job'] < 0 or not w['blocked'] for w in moved['workers'])
    assert not page.evaluate('__growthJourney.buildingExists', target['id'])

    # Build a real clinic on the cleared public-service site through the map tool.
    assert page.evaluate('(q)=>__growthJourney.can("clinic",q.x,q.y)', target)
    open_construction()
    page.locator('[data-build=clinic]').click()
    page.evaluate('(q)=>__growthJourney.center(q.x,q.y)', target)
    point = page.evaluate('(q)=>__growthJourney.point(q.x,q.y)', target)
    page.mouse.click(point['x'], point['y'])
    clinic = page.evaluate('(q)=>__growthJourney.clinicAt(q.x,q.y)', target)
    assert clinic is not None
    post_service = page.evaluate('__growthJourney.state()')
    assert abs(after_clear['treasury'] - post_service['treasury'] - 8000) < .001
    assert post_service['valid']['ok'] and abs(post_service['total'] - initial['total']) < .1

    # Let the apartment project advance partway, then verify that its exact
    # remaining work survives archive load and continues identically.
    page.evaluate('__townTest.step(12)')
    project_before_save = page.evaluate('__growthJourney.renewalProject()')
    assert project_before_save and 0 < project_before_save['remaining'] < project_before_save['duration']

    # Capture emergent income bands after a natural further year, then verify
    # the same ordinary interval replays exactly through the archive loader.
    profiles_before = page.evaluate('__growthJourney.profile()')
    checkpoint = page.evaluate('__growthJourney.snapshot()')
    assert page.evaluate('s=>__townTest.load(s)', checkpoint)
    assert canonical(page.evaluate('__townTest.save()')) == canonical(checkpoint), 'Midconstruction cold state changed'
    result['midconstructionColdCompleteStateIdentical'] = True
    result['replayExcludedFields'] = []
    page.evaluate('__townTest.step(360)')
    continuation = page.evaluate('__growthJourney.snapshot()')
    profiles_after = page.evaluate('__growthJourney.profile()')
    assert page.evaluate('s=>__townTest.load(s)', checkpoint)
    project_after_load = page.evaluate('__growthJourney.renewalProject()')
    assert project_after_load and project_after_load['id'] == project_before_save['id'] and project_after_load['remaining'] == project_before_save['remaining']
    page.evaluate('__townTest.step(360)')
    replay = page.evaluate('__growthJourney.snapshot()')
    assert canonical(replay) == canonical(continuation)
    # Extend the same funded street line to a genuinely outer parcel close to
    # the 128×128 atlas boundary using actual deed, road and home controls.
    open_construction()
    office = page.locator('#charterOffice')
    if not office.evaluate('(e)=>e.open'):
        office.locator(':scope > summary').click()
    edge_button = page.locator('[data-parcel-buy="belt-102-2"]')
    edge_price = page.evaluate('__growthJourney.parcelPrice', 'belt-102-2')
    assert not edge_button.is_disabled()
    edge_button.scroll_into_view_if_needed()
    edge_button.click()
    page.locator('[data-event-choice="0"]').click()
    assert abs(page.evaluate("__townTest.get().total") - initial['total']) < .1
    edge_road_plan = page.evaluate('__growthJourney.edgeRoadPlan()')
    assert edge_road_plan['ok'], edge_road_plan
    open_construction()
    page.locator('[data-build=road]').click()
    for start in range(0, len(edge_road_plan['cells']), 8):
        group = edge_road_plan['cells'][start:start+8]
        page.evaluate('(q)=>__growthJourney.center(q[0],q[1])', group[len(group)//2])
        for x,y in group:
            point = page.evaluate('(q)=>__growthJourney.point(q[0],q[1])', [x,y])
            page.mouse.click(point['x'], point['y'])
    assert page.evaluate('(q)=>__growthJourney.can("home",125,11)', edge_road_plan)
    open_construction()
    page.locator('[data-build=home]').click()
    page.evaluate('__growthJourney.center(125,11)')
    point = page.evaluate('__growthJourney.point(125,11)')
    page.mouse.click(point['x'], point['y'])
    edge_home = page.evaluate('__growthJourney.homeAt(125,11)')
    assert edge_home is not None and page.evaluate('__growthJourney.roadReach', edge_home) is not None
    edge_services = page.evaluate('__growthJourney.serviceRoadDistances', edge_home)
    assert edge_services['clinic'] > 60 and edge_services['school'] > 40, edge_services
    edge_state = page.evaluate('__growthJourney.state()')
    assert 'belt-102-2' in edge_state['owned'] and edge_state['valid']['ok']
    final = edge_state
    apartment = page.evaluate('(q)=>__growthJourney.kindAt("apartment",q.x,q.y)', farm)
    assert apartment and not page.evaluate('__growthJourney.renewalProject()')
    assert final['valid']['ok'] and abs(final['total'] - initial['total']) < .1 and not errors
    result.update({
        'ordinaryFundingOnly': True,
        'initial': initial,
        'twoDayOneDeeds': {'prices': deed_prices, 'state': after_two, 'nextDeedShortfall': shortfall_at_start, 'nextDeedInitiallyDisabled': True},
        'sixYearRecovery': six_year,
        'sameOpenPanelDeedBecamePurchasable': True,
        'thirdDeed': {'parcel': 'belt-78-2', 'price': 40224, 'state': after_three},
        'outerCottage': {'site': [59,14], 'price': 20000, 'plan': plan, 'roadTiles': road_plan['cells'], 'roadCost': road_plan['cost']},
        'farmTransition': {'before': farm, 'paidHomes': extra_homes, 'after': farm_after, 'relocated': farm_relocated,
                           'anyFarmRelocated': bool(moved_farms), 'movedFarms': moved_farms,
                           'renewalGateAudit': farm_audit_at_attempt,
                           'reviewedRelocation': {'quote': farm_review, 'cancelWasReadOnly': True, 'afterApproval': after_manual_renewal, 'project': renewal_project,
                           'preservedFieldsWorkersStock': True, 'fourUnitHousingProjectStarted': True,
                           'completedAfterNaturalYear': apartment},
                           'note': 'Automatic renewal remains gated by strong market pressure. A mayor can separately review moderate observed demand after a residential plan; full farm titles move intact and housing proceeds only through a funded project.'},
        'serviceAssembly': {'target': target['id'], 'quote': target['quote'], 'householdBefore': original_household, 'householdAfter': moved,
                            'clinic': clinic, 'clinicCost': 8000, 'treasuryAfter': final['treasury']},
        'incomeProfilesBefore': profiles_before,
        'incomeProfilesAfterOneNaturalYear': profiles_after,
        'exact360DaySaveReplay': True,
        'partiallyCompletedProjectArchive': {'beforeSave': project_before_save, 'afterLoad': project_after_load,
                                             'exactRemainingWorkPreserved': True, 'completionAfterReplay': apartment},
        'edgeExpansionJourney': {'parcel': 'belt-102-2', 'price': edge_price, 'site': [125,11],
                                 'roadTiles': edge_road_plan['cells'], 'roadCost': edge_road_plan['cost'],
                                 'connectedRoadDistanceToTownHall': page.evaluate('__growthJourney.roadReach', edge_home),
                                 'nearestPublicServiceRoadDistances': edge_services,
                                 'outsideCurrentClinicAndSchoolRanges': True,
                                 'ownedBoundaryParcel': True, 'homeBuiltAtOuterEdge': edge_home},
        'final': final,
        'errors': errors,
    })
    browser.close()

out = ROOT / 'docs/previews/urban8'
out.mkdir(parents=True, exist_ok=True)
(out / 'district-growth-journey.json').write_text(json.dumps(result, indent=2) + '\n')
print('PASS ordinary-funded repeated expansion, residential planning, compensated rehousing/service build and exact replay')
