"""Raised causeway visuals, real freight-route height, and cold-redraw determinism."""
from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html

source=(ROOT/"assets/game.js").read_text()
probe=r'''window.__bridgeArtTest={
 setup:()=>{__townTest.reset('settlement',42);G.autoBuild=false;const p=ANNEX_PARCELS.find(p=>p.id==='east-meadow'),survey=parcelSurvey(p);purchaseParcel(p.id,survey.price);for(let x=43;x<=63;x++)construct('road',x,15,true);for(let x=69;x<=76;x++)construct('road',x,15,true);flushRoadBatch();invalidateRoads();const a0=roadCenter(roadId(63,15)),z0=roadCenter(roadId(69,15));cam={x:(a0[0]+z0[0])/2,y:(a0[1]+z0[1])/2,zoom:.88};dirty=true;draw();const baselineDrawMs=__townTest.renderBench(30);construct('farm',72,16,true);construct('home',70,16,true);flushRoadBatch();invalidateRoads();const quote=bridgeCandidateFromBank(roadId(63,15));if(!quote.ok||!commitRoadBridge(quote.bank,quote.key).ok)throw Error('bridge fixture failed');const build=G.buildings.find(b=>b.kind==='farm'&&b.x===72&&b.y===16),firm=G.firms.find(f=>build&&f.building===build.id),market=OUTSIDE_MARKETS.find(m=>firm&&regionalQuote(firm,m,'grain','import')),trade=regionalQuote(firm,market,'grain','import');if(dispatchRegional(firm,'grain',60,'import',trade)!==60)throw Error('paid cargo fixture failed');recompute();const b=G.bridges[0],a=roadCenter(b.banks[0]),z=roadCenter(b.banks[1]);cam={x:(a[0]+z[0])/2,y:(a[1]+z[1])/2,zoom:.88};buildMode='';$('toast').style.display='none';$('placementHint').style.display='none';dirty=true;draw();return {bridge:bridgeRenderSnapshot()[0],shipment:G.regionalTrade.shipments[G.regionalTrade.shipments.length-1],quantity:60,baselineDrawMs,item:viewBuildings.find(i=>i.kind==='roadBridge')};},
 draw:()=>{dirty=true;draw();const renderMs=__townTest.renderBench(30);return {renderMs,items:viewBuildings.filter(i=>i.kind==='roadBridge').map(i=>({closed:i.closed,condition:i.condition,bounds:i.bounds}))};},
 depth:(path,id)=>{const p=roadCenter(id),actor={kind:'vehicle',v:{path,style:'truck'},x:p[0],y:p[1]},bus={...actor,kind:'transitArt',mode:'bus'},metro={...actor,kind:'transitArt',mode:'elevated'},boat={kind:'boat',x:p[0],y:p[1]};return {truck:!!bridgeTrafficLift(actor),bus:!!bridgeTrafficLift(bus),metro:!!bridgeTrafficLift(metro),boat:!!bridgeTrafficLift(boat),truckY:sceneActorPaintY(actor,[]),deckY:viewBuildings.find(i=>i.kind==='roadBridge').y,boatY:sceneActorPaintY(boat,[])};},
 close:()=>{G.bridges[0].condition=0;G.bridgeRevision++;staticDirty=true;dirty=true;draw();return {closed:viewBuildings.find(i=>i.kind==='roadBridge').closed,water:waterNetwork().components.some(c=>c.cells.includes(G.bridges[0].cells[2]))};},
 reopen:()=>{G.bridges[0].condition=100;G.bridgeRevision++;staticDirty=true;dirty=true;draw();},
 cold:()=>{const before=ctx.getImageData(0,0,cv.width,cv.height).data;viewRasterKey='';viewBackgroundKey='';staticDirty=true;dirty=true;draw();const after=ctx.getImageData(0,0,cv.width,cv.height).data;let diff=0;for(let i=0;i<before.length;i++)if(before[i]!==after[i])diff++;return {differentChannels:diff,channels:before.length};},
 state:()=>({day:G.day,cash:G.treasury,region:G.region,total:totalMoney(),seed:G.worldSeed,observations:G.observations.length})
};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
result={'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':844,'height':390});page.set_default_timeout(10000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html);page.add_script_tag(content=script);page.locator('#newTown').click();page.locator('#pause').click()
 fixture=page.evaluate('__bridgeArtTest.setup()');assert fixture['quantity']==60 and all(i in fixture['shipment']['path'] for i in fixture['bridge']['cells']),fixture
 before=page.evaluate('__bridgeArtTest.state()');draw=page.evaluate('__bridgeArtTest.draw()');items=draw['items'];assert len(items)==1 and not items[0]['closed'] and items[0]['condition']==100,items
 depth=page.evaluate('(a)=>__bridgeArtTest.depth(a.path,a.id)',{'path':fixture['shipment']['path'],'id':fixture['bridge']['cells'][2]})
 assert depth['truck'] and depth['bus'] and not depth['metro'] and not depth['boat'] and depth['truckY']>depth['deckY']>depth['boatY'],depth
 cold=page.evaluate('__bridgeArtTest.cold()');assert cold['differentChannels']==0,cold
 page.screenshot(path=str(ROOT/'docs/previews/urban8/road-bridge-art-phone.png'))
 closed=page.evaluate('__bridgeArtTest.close()');assert closed=={'closed':True,'water':True},closed
 page.screenshot(path=str(ROOT/'docs/previews/urban8/road-bridge-art-closed-phone.png'));page.evaluate('__bridgeArtTest.reopen()')
 after=page.evaluate('__bridgeArtTest.state()');assert before==after,(before,after);assert not errors,errors
 result.update({'paidImportQuantity':fixture['quantity'],'routeCrossesAllSpanTiles':True,'openBridge':items[0],'baselineDrawMs':fixture['baselineDrawMs'],'bridgeDrawMs':draw['renderMs'],'closedState':closed,'actorDepth':depth,'coldRedraw':cold,'stateUnchanged':before==after,'errors':errors})
 out=ROOT/'docs/previews/urban8';out.mkdir(parents=True,exist_ok=True);(out/'road-bridge-art.json').write_text(json.dumps(result,indent=2)+'\n');browser.close()
print('PASS raised bridge art, real paid route, actor depth, closed water continuity, paused cold redraw and state invariance')
