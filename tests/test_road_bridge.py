"""A paid five-cell lake bridge provides real road routing without claiming the water."""
from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html

source=(ROOT/'assets/game.js').read_text()
probe=r'''window.__bridgeTest={
 setup:()=>{__townTest.reset('settlement',42);G.autoBuild=false;const p=ANNEX_PARCELS.find(p=>p.id==='east-meadow'),q=parcelSurvey(p),opening=totalMoney();if(!purchaseParcel(p.id,q.price))throw Error('ordinary funds cannot acquire crossing');for(let x=43;x<=63;x++)construct('road',x,15,true);for(let x=69;x<=76;x++)construct('road',x,15,true);flushRoadBatch();invalidateRoads();const bank=roadId(63,15),quote=bridgeCandidateFromBank(bank),i=iso(63,15),r=cv.getBoundingClientRect();cam={x:i[0],y:i[1]+18,zoom:1};dirty=true;draw();return {opening,total:totalMoney(),treasury:G.treasury,accounts:__bridgeTest.accounts(),quote,bank,screen:[r.left+cw/2,r.top+ch/2],span:G.tiles.slice(roadId(64,15),roadId(69,15)),water:waterNetwork().components.length};},
 point:()=>{const i=iso(63,15),r=cv.getBoundingClientRect();cam={x:i[0],y:i[1]+18,zoom:1};dirty=true;draw();return [r.left+cw/2,r.top+ch/2];},
 quote:bank=>bridgeCandidateFromBank(bank),commit:(bank,key)=>commitRoadBridge(bank,key),town:()=>G,total:totalMoney,valid:()=>validateTown(),save:()=>__townTest.save(),load:s=>__townTest.load(s),water:()=>waterNetwork(),graph:()=>graph(),accounts:()=>({treasury:G.treasury,region:G.region,spending:G.cumulative.spending}),
 stale:(bank,key)=>{const before=totalMoney(),cells=G.bridges?.length||0,cash=G.treasury;G.treasury--;const result=commitRoadBridge(bank,key);G.treasury=cash;return {result,before,after:totalMoney(),cellsBefore:cells,cellsAfter:G.bridges?.length||0};},validateBridgeArchive:data=>validateBridgeArchive(data),normalize:normalizeRegionArchive,roadVersion:()=>roadsVersion,surface:id=>roadSurface(id),descriptor:()=>bridgeRenderSnapshot(),bankRemoval:id=>roadRemovalQuote(id%T,id/T|0),makeRoads:()=>{for(let x=43;x<=63;x++)construct('road',x,15,true);for(let x=69;x<=76;x++)construct('road',x,15,true);flushRoadBatch();invalidateRoads()},settleOnEastBank:()=>{construct('farm',72,16,true);construct('home',70,16,true);flushRoadBatch();invalidateRoads();const fb=G.buildings.find(b=>b.kind==='farm'&&b.x===72&&b.y===16),farm=G.firms.find(f=>fb&&f.building===fb.id),home=G.buildings.find(b=>b.kind==='home'&&b.x===70&&b.y===16),market=OUTSIDE_MARKETS.find(m=>farm&&regionalQuote(farm,m,'grain','import')),quote=farm&&market&&regionalQuote(farm,market,'grain','import'),quantity=farm&&market?dispatchRegional(farm,'grain',60,'import',quote):0,shipment=G.regionalTrade.shipments.at(-1);recompute();return {farm:farm?.id,home:home?.id,service:home&&urbanRelocationServiceRoutes(home),quantity,path:quote?.path,shipment:shipment&&{id:shipment.id,path:shipment.path,activePath:shipment.activePath,stage:shipment.stage},valid:validateTown(),total:totalMoney(),bridgeRemoval:bridgeRemovalQuote(G.bridges[0].id)}},step:n=>__townTest.step(n),capture:o=>__townTest.capture(o)
};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
result={'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':844,'height':390});page.set_default_timeout(10000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html);page.add_script_tag(content=script);page.locator('#newTown').click();page.locator('#pause').click()
 fixture=page.evaluate('__bridgeTest.setup()');assert fixture['quote']['ok'] and fixture['quote']['cells']==[1984,1985,1986,1987,1988],fixture
 assert fixture['quote']['cost']==13450 and fixture['quote']['maintenance']==12.5 and fixture['water']>0,fixture
 # The capital review is reachable through the actual council panel and map placement controls.
 page.locator('[data-panel=construction]').click();button=page.locator('[data-bridge-build]');button.scroll_into_view_if_needed();button.click();point=page.evaluate('__bridgeTest.point()');page.mouse.click(*point)
 assert page.locator('#eventDialog').is_visible();review=page.locator('#eventText').inner_text();assert '5 water tiles' in review and '$13,450' in review and '$12.50/day' in review,review
 page.screenshot(path=str(ROOT/'docs/previews/urban8/bridge-review-phone.png'))
 # A changed treasury invalidates the review without a charge or partial tile writes.
 stale=page.evaluate('(q)=>__bridgeTest.stale(q.bank,q.key)',fixture['quote']);assert not stale['result']['ok'] and stale['before']==stale['after'] and stale['cellsBefore']==stale['cellsAfter']==0,stale
 page.locator('[data-event-choice="1"]').click();assert not page.locator('#eventDialog').is_visible()
 page.locator('[data-panel=construction]').click();page.locator('[data-bridge-build]').scroll_into_view_if_needed();page.locator('[data-bridge-build]').click();page.mouse.click(*point);page.locator('[data-event-choice="0"]').click()
 after=page.evaluate('''()=>{const g=__bridgeTest.town(),b=g.bridges[0],a=b.banks[0],z=b.banks[1],graph=__bridgeTest.graph();return {count:g.bridges.length,bridge:b,tiles:b.cells.map(id=>g.tiles[id]),waterNodes:b.cells.map(id=>__bridgeTest.water().components.some(c=>c.cells.includes(id))),sameRoadPart:graph.parts[a]===graph.parts[z],roadSurface:b.cells.map(id=>__bridgeTest.surface(id)),total:__bridgeTest.total(),accounts:__bridgeTest.accounts(),descriptor:__bridgeTest.descriptor(),town:__bridgeTest.valid()}}''')
 assert after['count']==1 and after['tiles']==[4]*5 and after['waterNodes']==[True]*5 and after['sameRoadPart'] and after['roadSurface']==[True]*5,after
 assert after['town']['ok'] and not after['town']['issues'],after['town']
 assert abs(after['total']-fixture['total'])<.001 and abs(after['accounts']['treasury']-(fixture['treasury']-13450))<.001 and abs(after['accounts']['region']-(fixture['accounts']['region']+13450))<.001,after['accounts']
 assert after['descriptor'][0]['cells']==after['bridge']['cells'] and after['descriptor'][0]['axis']=='east-west'
 assert not page.evaluate('id=>__bridgeTest.bankRemoval(id).ok',after['bridge']['banks'][0]),'bank road retirement must preserve bridge approach'
 # A newly opened farm and municipal home on the far bank use the surfaced route for freight and civic reach.
 journey=page.evaluate('__bridgeTest.settleOnEastBank()');assert journey['quantity']==60 and all(id in journey['path'] for id in after['bridge']['cells']) and journey['service']['health']['within'] and journey['service']['health']['distance']<=60,journey
 assert journey['valid']['ok'] and not journey['bridgeRemoval']['ok'] and 'consignment' in journey['bridgeRemoval']['reason'].lower(),journey
 # Save/load preserves bridge identity and water under the surfaced road; tampering is rejected atomically.
 archived=page.evaluate('__bridgeTest.save()');assert page.evaluate('s=>__bridgeTest.load(s)',archived)
 replay=page.evaluate('__bridgeTest.save()');parsed=json.loads(replay);payload=json.loads(parsed if isinstance(parsed,str) else json.dumps(parsed)) if isinstance(parsed,str) else parsed
 assert page.evaluate('d=>__bridgeTest.validateBridgeArchive(d)',payload)
 # An 80x80 pre-bridge archive that contains this inland span remaps all tile IDs once.
 remap=page.evaluate('''()=>{const tiles=new Array(80*80).fill(0),cells=[64,65,66,67,68].map(x=>15*80+x),banks=[15*80+63,15*80+69];for(const id of cells)tiles[id]=4;for(const id of banks)tiles[id]=1;const data=__bridgeTest.normalize({version:3,gridSize:80,day:1,worldSeed:42,tiles,bridges:[{id:1,name:'Legacy Lake Bridge',axis:'east-west',cells,banks,condition:100,builtDay:1,capital:13450}]});return {gridSize:data?.gridSize,cells:data?.bridges?.[0]?.cells,banks:data?.bridges?.[0]?.banks,valid:data&&__bridgeTest.validateBridgeArchive(data)}}''')
 assert remap=={'gridSize':128,'cells':after['bridge']['cells'],'banks':after['bridge']['banks'],'valid':True},remap
 bad=dict(payload);bad['tiles']=payload['tiles'][:];bad['tiles'][after['bridge']['cells'][0]]=2
 assert not page.evaluate('d=>__bridgeTest.validateBridgeArchive(d)',bad), 'orphaned bridge metadata accepted'
 page.evaluate('__bridgeTest.step(1)');paid=page.evaluate('''()=>({bridge:__bridgeTest.town().bridges[0],accounts:__bridgeTest.accounts(),total:__bridgeTest.total(),water:__bridgeTest.water().components.some(c=>c.cells.includes(1984)),valid:__bridgeTest.valid()})''')
 assert paid['bridge']['condition']>100-1e-8 or paid['bridge']['condition']>=100,paid['bridge']
 assert paid['water'] and paid['valid']['ok'] and abs(paid['total']-after['total'])<.001,paid
 base=page.evaluate('__bridgeTest.save()');page.evaluate('__bridgeTest.step(30)');one=page.evaluate('__bridgeTest.save()');assert page.evaluate('s=>__bridgeTest.load(s)',base);page.evaluate('__bridgeTest.step(30)');two=page.evaluate('__bridgeTest.save()');assert json.loads(one)==json.loads(two)
 assert not errors,errors
 result.update({'span':fixture['quote']['cells'],'review':review,'built':{k:v for k,v in after.items() if k not in ('town',)},'eastBankFreightAndService':journey,'maintenanceAfterDay':paid,'exact30DayReplay':True,'errors':errors})
 out=ROOT/'docs/previews/urban8';out.mkdir(parents=True,exist_ok=True);(out/'road-bridge.json').write_text(json.dumps(result,indent=2)+'\n');browser.close()
print('PASS reviewed bridge construction, stale-quote rejection, road and water connectivity, save validation, maintenance and exact replay')
