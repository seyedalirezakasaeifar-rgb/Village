"""Shipment timing and disruption advice read the real logistics state only."""
from pathlib import Path
import hashlib, json
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright

OUT = ROOT / 'docs/evidence/trade-quality8'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = (ROOT / 'assets/game.js').read_text()
PROBE = r'''
window.__cargoTimingQA={
 town:()=>G,
 prepare:()=>{const f=G.firms.find(f=>!f.closed&&formulas[f.kind]?.out==='grain'),m=OUTSIDE_MARKETS[0],before=totalMoney(),q=regionalQuote(f,m,'grain','import');if(!q)throw Error('No paid import route');const qty=dispatchRegional(f,'grain',12,'import',q);if(qty!==12)throw Error('Existing firm could not fund the paid test consignment');const o=G.regionalTrade.shipments[G.regionalTrade.shipments.length-1];if(!o||o.direction!=='import'||pendingGoods(f,'grain')<12)throw Error('Cargo was not booked as actual inbound stock');return {id:o.id,qty,estimate:o.due,mode:o.mode||'road',firm:o.firm,market:o.market,quoteDays:q.days,cashConserved:Math.abs(before-totalMoney())<.001,goods:goodsBalance()};},
 completed:id=>{let order;for(let n=0;n<60&&!order;n++){__townTest.step(1);order=G.regionalTrade.recent.find(o=>o.id===id)}if(!order)throw Error('No completed paid cargo record');const before=JSON.stringify(G),rng=rngState,money=totalMoney(),timing=regionalCargoTiming(order,G.day+5);inspectedTrip={regional:id,path:order.path.slice()};const inspector=renderTripInspector();return {record:order,timing,inspector,unchanged:before===JSON.stringify(G)&&rng===rngState&&money===totalMoney()};},
 timing:(id,day)=>regionalCargoTiming(G.regionalTrade.shipments.find(o=>o.id===id),day),
 snapshot:()=>({town:JSON.stringify(G),rng:rngState,money:totalMoney(),goods:JSON.stringify(goodsBalance())}),
 outage:(id)=>{const o=G.regionalTrade.shipments.find(x=>x.id===id),f=G.firms[o.firm],m=OUTSIDE_MARKETS.find(x=>x.id===o.market),removed={};const path=()=>o.mode==='river'?logisticsPath(graph().portals.get(f.building),graph().portals.get(G.firms[o.depot]?.building)):regionalRoadPath(f,m);let attempts=0;while(path().length&&attempts++<40){for(const tile of path())if(G.tiles[tile]===1||G.tiles[tile]===2){if(!Object.prototype.hasOwnProperty.call(removed,tile))removed[tile]=G.tiles[tile];G.tiles[tile]=0;}invalidateRoads(false);}if(typeof regionalShipmentRouteAvailable==='function'&&regionalShipmentRouteAvailable(o,f,m)){for(const [tile,value]of Object.entries(removed))G.tiles[+tile]=value;invalidateRoads(false);throw Error('Controlled cut did not interrupt the real shipment route');}for(let n=0;n<80&&o.status!=='Route interrupted'&&G.day<o.stageDue+80;n++){G.day=Math.max(G.day+1,o.stageDue);regionalFreightDay();}const interrupted=o.status==='Route interrupted',detail=regionalCargoTiming(o);return {interrupted,day:G.day,due:o.due,stage:o.stage,status:o.status,detail,removed:Object.keys(removed).length,restoration:Object.entries(removed)};},
 restore:rows=>{for(const [tile,value]of rows)G.tiles[+tile]=value;invalidateRoads(false);},
 display:(id)=>{const o=G.regionalTrade.shipments.find(x=>x.id===id);inspectedTrip={regional:id,path:o.path.slice()};openPanel('trip');return renderTripInspector();},
 refresh:()=>{renderPanel('economy');const office=document.querySelector('#logisticsOffice');if(office)office.open=true;},
 overlay:()=>overlay,
 read:()=>regionalTradePanel()
};'''
SCRIPT = SOURCE.replace('// SOURCE: 99-instrumentation.js', PROBE + '\n// SOURCE: 99-instrumentation.js')


def test_regional_cargo_timing():
    def without_panel_progress(snapshot):
        town = json.loads(snapshot['town'])
        # Opening a panel records the player's journey visit; this UX counter is
        # intentionally allowed, while simulation, trade and RNG state stay fixed.
        town.pop('mayorJourney', None)
        return {'town': json.dumps(town, sort_keys=True), 'rng': snapshot['rng'], 'money': snapshot['money'], 'goods': snapshot['goods']}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page(viewport={'width': 390, 'height': 844}, has_touch=True)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content(html)
        page.add_script_tag(content=SCRIPT)
        page.locator('#newTown').click()
        page.locator('#pause').click()
        order = page.evaluate('__cargoTimingQA.prepare()')
        assert order['cashConserved'] and max(abs(row['error']) for row in order['goods']) < .001, order

        # Read-only ETA output is based on the actual paid order and current simulation day.
        before_read = page.evaluate('__cargoTimingQA.snapshot()')
        first = page.evaluate('(id)=>__cargoTimingQA.timing(id)', order['id'])
        for _ in range(30):
            assert page.evaluate('(id)=>__cargoTimingQA.timing(id).schedule', order['id']) == first['schedule']
        after_read = page.evaluate('__cargoTimingQA.snapshot()')
        assert before_read == after_read, 'Timing read mutated town, RNG, cash or goods'
        assert 'Expected in' in first['schedule'] and first['checkpoint'] is not None, first

        for _ in range(10):
            page.evaluate('__cargoTimingQA.read()')
        assert before_read == page.evaluate('__cargoTimingQA.snapshot()'), 'Pure full trade projection changed complete model'

        before_panel = page.evaluate('__cargoTimingQA.snapshot()')
        page.locator('[data-panel=economy]').click()
        page.locator('#logisticsOffice>summary').click()
        assert 'estimate day' in page.locator('#logisticsOffice').inner_text().lower()
        after_panel = page.evaluate('__cargoTimingQA.snapshot()')
        assert without_panel_progress(before_panel) == without_panel_progress(after_panel), 'Trade panel projection changed simulation, RNG, cash or goods'
        cargo_button = page.locator(f'[data-regional-cargo="{order["id"]}"]').first
        cargo_button.scroll_into_view_if_needed()
        assert cargo_button.is_visible()
        page.locator('#toast').evaluate("e=>e.style.display='none'")
        page.screenshot(path=str(OUT / 'regional-cargo-schedule-mobile.png'))
        cargo_button.click()
        detail = page.locator('#panelBody').inner_text()
        assert 'Arrival estimate' in detail and 'Current stage' in detail and 'Next checkpoint' in detail, detail

        # A controlled physical road cut delays that real shipment; it does not create cargo.
        outage = page.evaluate('(id)=>__cargoTimingQA.outage(id)', order['id'])
        assert outage['interrupted'] and outage['removed'] > 0, outage
        assert outage['detail']['roadAccess'] and 'road tool' in outage['detail']['detail'].lower(), outage
        delayed_read = page.evaluate('__cargoTimingQA.snapshot()')
        delay = page.evaluate('(args)=>__cargoTimingQA.timing(args.id,args.day)', {'id': order['id'], 'day': outage['due'] + 2})
        assert delay['overdue'] == 2 and '2 simulated days past estimate' in delay['schedule'], delay
        assert delayed_read == page.evaluate('__cargoTimingQA.snapshot()'), 'Delayed-cargo explanation changed the model'

        page.evaluate('(id)=>__cargoTimingQA.display(id)', order['id'])
        assert without_panel_progress(delayed_read) == without_panel_progress(page.evaluate('__cargoTimingQA.snapshot()')), 'Trip-inspector projection changed simulation, RNG, cash or goods'
        trip_text = page.locator('#panelBody').inner_text()
        assert 'Route interrupted' in trip_text and 'road tool' in trip_text.lower()
        road_button = page.locator('[data-regional-road-access]')
        road_button.scroll_into_view_if_needed()
        button_box = road_button.bounding_box()
        assert button_box and button_box['height'] >= 42 and button_box['width'] >= 44, button_box
        page.locator('#toast').evaluate("e=>e.style.display='none'")
        page.screenshot(path=str(OUT / 'regional-cargo-delay-mobile.png'))
        town_before_action = page.evaluate('__cargoTimingQA.snapshot()')
        road_button.click()
        assert page.evaluate('__cargoTimingQA.overlay()') == 'roads'
        assert not page.locator('#panel').is_visible()
        assert without_panel_progress(town_before_action) == without_panel_progress(page.evaluate('__cargoTimingQA.snapshot()')), 'Road-access map action changed economy or cargo'
        page.screenshot(path=str(OUT / 'regional-cargo-road-access-mobile.png'))

        # If access returns before the next freight check, replace the stale outage
        # instruction with the live connected-route guidance while status remains recorded.
        page.evaluate('(rows)=>__cargoTimingQA.restore(rows)', outage['restoration'])
        restored = page.evaluate('(id)=>__cargoTimingQA.timing(id)', order['id'])
        assert not restored['roadAccess'] and 'available again' in restored['detail'], restored
        assert page.evaluate('(id)=>__cargoTimingQA.town().regionalTrade.shipments.some(o=>o.id===id)', order['id'])
        assert page.evaluate('__townTest.validate().ok')
        completed = page.evaluate('(id)=>__cargoTimingQA.completed(id)', order['id'])
        assert completed['record']['status'] == 'Delivered' and completed['unchanged'], completed
        assert completed['timing']['completed'] and completed['timing']['overdue'] == 0 and completed['timing']['checkpoint'] is None, completed
        assert 'past estimate' not in completed['timing']['schedule'] and 'Recorded completion' in completed['inspector'], completed
        assert not errors, errors
        result = {'candidate_origin': '2e8b51f85f3dfba8cc46b7bc1bb3ce2569a56ebd', 'source_sha256': hashlib.sha256(SOURCE.encode()).hexdigest(), 'actualPaidOrder': order, 'initialSchedule': first, 'controlledRoadOutage': {k:v for k,v in outage.items() if k!='restoration'}, 'twoDaysPastEstimate': delay, 'restoredRouteGuidance': restored, 'completedLedger':completed, 'roadMapActionModelInvariant': True, 'validTown': True, 'errors': errors}
        (OUT / 'regional-cargo-timing.json').write_text(json.dumps(result, indent=2) + '\n')
        browser.close()
        return result


if __name__ == '__main__':
    print(json.dumps(test_regional_cargo_timing(), indent=2))
