"""A paid, reviewed outer-street change updates live access and route caches."""
from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text()
probe=r'''window.__roadAudit={
 setup:()=>{__townTest.reset('settlement',42);G.autoBuild=false;const east=ANNEX_PARCELS.find(p=>p.id==='east-meadow'),quote=parcelSurvey(east),opening=totalMoney();if(!purchaseParcel(east.id,quote.price))throw Error('Ordinary town funds could not buy East Meadow');for(let x=56;x<=64;x++)construct('road',x,27,true);for(const y of [26,25])construct('road',55,y,true);for(let y=18;y<=25;y++)construct('road',56,y,true);flushRoadBatch();construct('farm',58,25,true);invalidateRoads();const farm=G.firms.find(f=>f.kind==='farm'&&f.building===103);if(!farm)throw Error('Cargo-route farm unavailable');const preReserve=__townTest.save(),homeQuote=urbanRehousingQuote(),reserved=commissionUrbanRehousing({...homeQuote,x:57,y:18}),protectedQuote=roadRemovalQuote(56,25);return {opening,total:totalMoney(),treasury:G.treasury,farm:farm.id,bridgeA:roadId(56,27),bridgeB:roadId(56,25),preReserve,reserve:{commission:reserved,quote:protectedQuote},};},
 restoreCommittedTown:()=>{construct('farm',57,22,true);construct('home',57,18,true);flushRoadBatch();invalidateRoads();assignJobs();const home=G.buildings.find(b=>b.kind==='home'&&b.x===57&&b.y===18),hh=G.households.find(h=>h.home===home.id),farm=G.firms.find(f=>f.kind==='farm'&&f.building===104);if(!home||!hh||!farm||!farm.workers.length)throw Error('Branch residents and working farm not established');return {home:home.id,household:hh.id,residents:hh.people.length,farm:farm.id,farmWorkers:farm.workers.slice(),commuters:G.people.filter(p=>p.job===farm.id&&!p.commuteBlocked).length,services:urbanRelocationServiceRoutes(home),access:regionalUtilityAccess(home),bridgeA:roadId(56,27),bridgeB:roadId(56,25),total:totalMoney()};},
 cargo:()=>{const f=G.firms.find(f=>f.kind==='farm'&&f.building===103),m=OUTSIDE_MARKETS.find(m=>regionalQuote(f,m,'grain','import'));if(!m)throw Error('No ordinary market quote for the cargo-route farm');const q=regionalQuote(f,m,'grain','import'),qty=dispatchRegional(f,'grain',60,'import',q),o=G.regionalTrade.shipments.at(-1);return {market:m.id,qty,days:q.days,path:q.path,shipment:o&&{id:o.id,path:o.path,activePath:o.activePath||[]},bridgeA:roadId(56,27),bridgeB:roadId(56,25),quoteA:roadRemovalQuote(56,27),quoteB:roadRemovalQuote(56,25),valid:validateTown().ok};},
 quote:roadRemovalQuote,staleQuote:firmId=>{const q=roadRemovalQuote(56,25),p=G.people.find(p=>p.job===firmId&&!p.commuteBlocked),before=totalMoney(),tile=G.tiles[q.id];if(!p)throw Error('No commute record for stale-quote test');p.commuteBlocked=true;const refused=retireRoadTile(56,25,q.key);p.commuteBlocked=false;return {refused,before,after:totalMoney(),tileBefore:tile,tileAfter:G.tiles[q.id]};},town:()=>G,total:totalMoney,accounts:()=>({treasury:G.treasury,region:G.region,spending:G.cumulative.spending}),mode:()=>buildMode,closeTool:()=>closeBuildTool(),service:id=>urbanRelocationServiceRoutes(readBuild(id)),access:id=>regionalUtilityAccess(readBuild(id)),version:()=>roadsVersion,center:(x,y)=>{const p=iso(x,y);cam={x:p[0],y:p[1]+18,zoom:1};dirty=true;draw();const r=cv.getBoundingClientRect();return {x,y,screen:[r.left+cw/2,r.top+ch/2],canvas:[cv.width,cv.height]};},save:()=>__townTest.save(),load:s=>__townTest.load(s),step:n=>__townTest.step(n),valid:()=>__townTest.validate(),goods:()=>goodsBalance()
};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
result={'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':844,'height':390});page.set_default_timeout(10000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);page.add_script_tag(content=script);page.locator('#newTown').click();page.locator('#pause').click()
 base=page.evaluate('__roadAudit.setup()');assert base['reserve']['commission']['ok'] and not base['reserve']['quote']['ok'] and 'replacement housing' in base['reserve']['quote']['reason'].lower(),base
 baseline=base['preReserve'];assert page.evaluate('s=>__roadAudit.load(s)',baseline)
 # Dispatch a real paid shipment on street A; it must block A while allowing review on separate street B.
 cargo=page.evaluate('__roadAudit.cargo()');assert cargo['qty']==60 and base['bridgeA'] in cargo['path'] and not cargo['quoteA']['ok'] and 'shipment' in cargo['quoteA']['reason'].lower(),cargo
 assert cargo['valid'] and cargo['bridgeB'] not in cargo['path'] and cargo['quoteB']['ok'],cargo
 # Now extend a second annexed neighbourhood using ordinary costs; its farm/home spur has a distinct one-tile connection.
 # The archive predates the reserve test. Keep the paid shipment on its separate trunk while the branch is committed.
 branch=page.evaluate('__roadAudit.restoreCommittedTown()');assert branch['access'] and branch['commuters']>0 and branch['services']['health']['within'] and branch['services']['school']['within'],branch
 stale=page.evaluate('id=>__roadAudit.staleQuote(id)',branch['farm']);assert not stale['refused']['ok'] and 'changed' in stale['refused']['reason'].lower() and stale['before']==stale['after'] and stale['tileBefore']==stale['tileAfter'],stale
 # Cargo remains physically in transit on A, disjoint from the B connection being retired.
 assert page.evaluate('id=>__roadAudit.town().regionalTrade.shipments.some(o=>o.path.includes(id))',branch['bridgeA'])
 # Actual planning button selects the removal tool; actual canvas tap opens the signed quote.
 page.locator('[data-panel=construction]').click();tool=page.locator('[data-road-remove-tool]');tool.scroll_into_view_if_needed();tool.click();point=page.evaluate('__roadAudit.center(56,25)')
 page.mouse.click(*point['screen'])
 assert page.locator('#eventDialog').is_visible()
 quote_text=page.locator('#eventText').inner_text();assert 'workers commute' in quote_text and 'public school' in quote_text and '$50' in quote_text,quote_text
 out=ROOT/'docs/previews/urban8';out.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(out/'road-removal-impact-phone.png'))
 before_remove=page.evaluate('__roadAudit.total()');accounts_before=page.evaluate('__roadAudit.accounts()');version_before=page.evaluate('__roadAudit.version()')
 page.locator('[data-event-choice="0"]').click()
 assert page.evaluate('()=>__roadAudit.town().tiles[3256]===0')
 assert page.evaluate('__roadAudit.version()')>version_before
 after=page.evaluate('''ids=>{const g=__roadAudit.town(),h=g.households.find(h=>h.home===ids.home),f=g.firms.find(f=>f.id===ids.farm);return {main:__roadAudit.access(ids.home),service:__roadAudit.service(ids.home),commuters:g.people.filter(p=>p.job===f.id&&!p.commuteBlocked).length,firmWorkers:f.workers.length,total:__roadAudit.total(),accounts:__roadAudit.accounts(),roadVersion:__roadAudit.version(),day:g.day,household:h.id,home:ids.home,farm:ids.farm}}''',{'home':branch['home'],'farm':branch['farm']})
 assert not after['main'] and after['service']['health']['distance'] is None and after['service']['school']['distance'] is None,after
 assert abs(after['total']-before_remove)<.001,after
 # Save/load in the isolated state preserves the road gap and household, not just renderer state.
 disconnected=page.evaluate('__roadAudit.save()');assert page.evaluate('s=>__roadAudit.load(s)',disconnected)
 assert not page.evaluate('id=>__roadAudit.access(id)',branch['home']) and page.evaluate('id=>__roadAudit.town().households.find(h=>h.id===id).people.length===2',branch['household'])
 assert page.evaluate('id=>__roadAudit.town().regionalTrade.shipments.find(o=>o.id===id).path.includes(3512)&&!__roadAudit.town().regionalTrade.shipments.find(o=>o.id===id).path.includes(3256)',cargo['shipment']['id'])
 page.evaluate('__roadAudit.step(1)');cut_effects=page.evaluate('''ids=>{const g=__roadAudit.town(),f=g.firms.find(f=>f.id===ids.farm);return {blocked:f.workers.filter(id=>g.people[id].commuteBlocked).length,workers:f.workers.length,homeAccess:__roadAudit.access(ids.home),shipment:g.regionalTrade.shipments.find(o=>o.id===ids.shipment)?.stage,valid:__roadAudit.valid()}}''',{'home':branch['home'],'farm':branch['farm'],'shipment':cargo['shipment']['id']})
 assert cut_effects['blocked']==cut_effects['workers']==4 and not cut_effects['homeAccess'] and cut_effects['valid']['ok'],cut_effects
 page.evaluate('__roadAudit.closeTool()');page.evaluate('xy=>__roadAudit.center(xy.x,xy.y)',{'x':57,'y':18});page.screenshot(path=str(out/'road-removal-disconnected-phone.png'))
 # A normal $150 road tile rebuild restores the main component, commute and civic distances.
 before_rebuild=page.evaluate('__roadAudit.accounts()');assert page.evaluate('id=>__roadAudit.town().tiles[id]===0',branch['bridgeB'])
 page.locator('[data-panel=construction]').click();page.locator('[data-build=road]').scroll_into_view_if_needed();page.locator('[data-build=road]').click();assert page.evaluate('__roadAudit.mode()')=='road';point=page.evaluate('__roadAudit.center(56,25)');page.mouse.click(*point['screen'])
 accounts_cut=before_rebuild;restored=page.evaluate('''ids=>({road:__roadAudit.town().tiles[ids.bridgeB],main:__roadAudit.access(ids.home),service:__roadAudit.service(ids.home),valid:__roadAudit.valid(),total:__roadAudit.total(),accounts:__roadAudit.accounts(),version:__roadAudit.version(),mode:__roadAudit.mode()})''',{'bridgeB':branch['bridgeB'],'home':branch['home']})
 assert restored['road']==1 and restored['main'] and restored['service']['health']['within'] and restored['service']['school']['within'] and restored['valid']['ok'],restored
 assert abs(restored['total']-after['total'])<.001 and restored['version']>after['roadVersion']
 assert abs(after['accounts']['treasury']-accounts_before['treasury']+50)<.001 and abs(after['accounts']['region']-accounts_before['region']-50)<.001 and abs(after['accounts']['spending']-accounts_before['spending']-50)<.001,{'before removal':accounts_before,'after removal':after['accounts']}
 assert abs(restored['accounts']['treasury']-accounts_cut['treasury']+150)<.001 and abs(restored['accounts']['region']-accounts_cut['region']-150)<.001,{'before rebuild':accounts_cut,'after rebuild':restored['accounts']}
 replay=page.evaluate('__roadAudit.save()');page.evaluate('__roadAudit.step(30)');first=page.evaluate('__roadAudit.save()');assert page.evaluate('s=>__roadAudit.load(s)',replay);page.evaluate('__roadAudit.step(30)');second=page.evaluate('__roadAudit.save()');assert json.loads(first)==json.loads(second)
 assert page.evaluate('__roadAudit.valid().ok') and not errors,errors
 result.update({'fixture':{k:v for k,v in base.items() if k!='preReserve'},'cargo':{k:v for k,v in cargo.items() if k not in ('quote','quoteA','quoteB')},'activeCargoRefusal':cargo['quoteA']['reason'],'protectedReplacementProject':base['reserve']['quote']['reason'],'staleQuote':stale,'removalQuote':quote_text,'disconnected':after,'disconnectedDayAdvance':cut_effects,'restored':restored,'exact30DayReplay':True,'errors':errors})
 (out/'road-removal-network.json').write_text(json.dumps(result,indent=2)+'\n');browser.close()
print('PASS actual expanded-road build/removal/rebuild, active freight and protected rehousing guards, commute/service access invalidation, disconnected save-load and exact replay')
