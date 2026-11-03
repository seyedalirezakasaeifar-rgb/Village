"""Paid bus/rail transfers survive real atlas, outage, rehousing and retirement flows."""
from test_mobile_rendering import ROOT
from playwright.sync_api import sync_playwright
import json,hashlib,functools,http.server,threading
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__combinedTransitState=null;
window.__combinedTransit={
 setup:()=>{
  chosenScenario='settlement';seed(42);G.autoBuild=false;__townTest.step();const total=totalMoney(),grant=Math.min(G.region,4000000);G.region-=grant;G.treasury+=grant;
  const net=graph(),near=id=>roadOffsets.map(([dx,dy])=>({x:id%T+dx,y:(id/T|0)+dy})).find(p=>canPlace(p.x,p.y,true,'elevated_station'));
  const choices=G.people.filter(p=>p.job>=0).flatMap(p=>G.firms.filter(f=>!f.closed&&f.workers.length&&f.id!==p.job).map(f=>{const h=G.households[p.hh],path=routeBetween(readBuild(h.home),readBuild(f.building));return {p,h,f,path};})).filter(c=>c.path.length>=25).sort((a,b)=>b.path.length-a.path.length);
  const choice=choices.find(c=>near(c.path[c.path.length/2|0])&&near(c.path[c.path.length-1]));if(!choice)throw Error('No actual long commuter and two station sites');
  // Author a long assignment by exchanging two existing workers: no new jobs or people.
  const prior=G.firms[choice.p.job],otherId=choice.f.workers[choice.f.workers.length-1];prior.workers[prior.workers.indexOf(choice.p.id)]=otherId;choice.f.workers[choice.f.workers.length-1]=choice.p.id;G.people[otherId].job=prior.id;choice.p.job=choice.f.id;
  const lot=buildableCandidates('business').find(p=>canPlace(p.x,p.y,true,'transit_depot')),depot=buildTransitFacility('transit_depot',lot.x,lot.y),aLot=near(choice.path[choice.path.length/2|0]),a=buildTransitFacility('elevated_station',aLot.x,aLot.y),bLot=near(choice.path[choice.path.length-1]),b=buildTransitFacility('elevated_station',bLot.x,bLot.y);if(!depot||!a||!b)throw Error('Facility build failed');
  const drivers=G.people.filter(p=>p.id!==choice.p.id&&p.age>=18&&p.age<=70&&roadDistance(graph().portals.get(G.households[p.hh]?.home),graph().portals.get(depot.id))<=60).slice(0,12);
  for(const p of drivers){if(G.firms[p.job])G.firms[p.job].workers=G.firms[p.job].workers.filter(id=>id!==p.id);p.job=-1;p.skill=.8;p.health=90;p.previousPublicRole='';p.publicWork=false;p.publicIncome=0;p.searchAfter=G.day+1000;}
  const homePort=graph().portals.get(choice.h.home),mid=graph().portals.get(a.id),bs={mode:'bus',depot:depot.id,stops:[homePort,mid],level:2},rs={mode:'elevated',depot:depot.id,stops:[a.id,b.id],level:1},bus=buildTransitRoute(bs,transitQuote(bs)),rail=buildTransitRoute(rs,transitQuote(rs));if(!bus||!rail)throw Error('Paid mixed corridors failed');
  __townTest.step();const p=G.people[choice.p.id],trip=p.transitTrip;if(!trip||trip.routes.length!==2||!trip.routes.includes(bus.id)||!trip.routes.includes(rail.id)||!trip.settled)throw Error('Actual commuter did not buy a two-mode itinerary '+JSON.stringify({person:p.id,job:p.job,trip,stats:G.transit.routes.map(r=>r.stats)}));
  const before=JSON.stringify(G.transit),cargo=JSON.stringify(G.regionalTrade?.shipments||[]);while(G.charter.owned.length<ANNEX_PARCELS.length){const parcel=ANNEX_PARCELS.find(p=>!G.charter.owned.includes(p.id)&&parcelAdjacent(p));if(!parcel||!purchaseParcel(parcel.id,parcelSurvey(parcel).price))throw Error('Expansion failed');}
  if(before!==JSON.stringify(G.transit)||cargo!==JSON.stringify(G.regionalTrade?.shipments||[]))throw Error('Deeds changed a paid itinerary or shipment');
  const protectedStation=urbanClearanceQuote(a.x,a.y),protectedDepot=urbanClearanceQuote(depot.x,depot.y);if(protectedStation.ok||protectedDepot.ok||removeTransitFacility(a.id)||removeTransitFacility(depot.id))throw Error('Routed facilities were silently demolished');
  __combinedTransitState={person:p.id,household:choice.h.id,work:choice.f.building,bus:bus.id,rail:rail.id,stations:[a.id,b.id],depot:depot.id,total};
  return {grid:T,deeds:G.charter.owned.length,trip,protectedStation:protectedStation.reason,protectedDepot:protectedDepot.reason,cashDrift:totalMoney()-total};
 },
 outages:()=>{
  const s=__combinedTransitState,rail=G.transit.routes.find(r=>r.id===s.rail),bus=G.transit.routes.find(r=>r.id===s.bus),railTile=rail.path.find((id,i)=>i>1&&i<rail.path.length-2&&!bus.path.includes(id));if(railTile==null)throw Error('No separate rail road cell');
  G.tiles[railTile]=0;invalidateRoads(false);__townTest.step();const suspended=G.transit.routes.find(r=>r.id===s.rail).stats;if(suspended.operating||transitVehiclePoses(1,1).some(p=>p.route===s.rail))throw Error('Rail ran through a broken alignment');
  const saved=archivePayload();if(!hydrateSave(saved))throw Error('Interrupted network cannot be saved');construct('road',railTile%T,railTile/T|0);__townTest.step();if(!G.transit.routes.find(r=>r.id===s.rail).stats.operating)throw Error('Paid road reopening did not restore rail');
  const currentBus=G.transit.routes.find(r=>r.id===s.bus),beforePath=transitTopology().routes.find(r=>r.id===s.bus).path;let closed=null;
  for(const id of beforePath.slice(2,-2)){if(currentBus.stops.includes(id)||G.transit.routes.find(r=>r.id===s.rail).path.includes(id))continue;G.tiles[id]=0;invalidateRoads(false);const runtime=transitTopology().routes.find(r=>r.id===s.bus);const possible=runtime.valid&&runtime.path.length>1&&!runtime.path.includes(id);G.tiles[id]=1;invalidateRoads(false);if(possible){closed=id;break;}}
  if(closed==null)throw Error('No ordinary street with an alternate bus corridor');G.tiles[closed]=0;invalidateRoads(false);__townTest.step();const detour=transitTopology().routes.find(r=>r.id===s.bus);if(!detour.stats.operating||detour.path.includes(closed))throw Error('Bus did not use the real street detour');
  const detourLength=detour.path.length;construct('road',closed%T,closed/T|0);__townTest.step();const restored=transitTopology().routes.find(r=>r.id===s.bus);if(!restored.stats.operating||JSON.stringify(restored.path)!==JSON.stringify(beforePath))throw Error('Bus did not return to its restored shortest street route');
  return {railSuspended:true,closedSaveRestored:true,railReopened:true,busDetour:true,originalLength:beforePath.length,detourLength,busRestored:true,cashDrift:totalMoney()-s.total};
 },
 prepareRedevelopment:()=>{
  const q=urbanRehousingQuote();if(!q.ok||!commissionUrbanRehousing(q).ok)throw Error('Real municipal rehousing could not be commissioned');for(let n=0;n<90&&!G.buildings.some(b=>b.relocationReserve);n++)__townTest.step();if(!G.buildings.some(b=>b.relocationReserve))throw Error('Paid replacement dwelling did not complete');
  const s=__combinedTransitState,h=G.households[s.household],preferred=readBuild(h.home),home=[preferred,...G.buildings.filter(b=>b.kind==='home'&&G.households.some(h=>h.home===b.id&&h.people.length))].find(b=>b&&urbanClearanceQuote(b.x,b.y).ok);if(!home)throw Error('No compensated household clearance is available');
  const quote=urbanClearanceQuote(home.x,home.y);s.redevelopment={home:home.id,x:home.x,y:home.y,households:quote.households.map(id=>({id,people:G.households[id].people.slice(),oldHome:G.households[id].home})),transit:JSON.stringify(G.transit)};selected={id:home.id};openPanel('inspect');return {id:home.id,cost:quote.total,day:G.day};
 },
 finishRedevelopment:()=>{
  const s=__combinedTransitState,r=s.redevelopment;if(readBuild(r.home))throw Error('UI did not clear the property');for(const h of r.households){const now=G.households[h.id];if(JSON.stringify(now.people)!==JSON.stringify(h.people)||now.home===h.oldHome||!readBuild(now.home))throw Error('Displaced identities or real replacement homes lost');}
  if(JSON.stringify(G.transit)!==r.transit)throw Error('Residential redevelopment changed paid transit books');construct('clinic',r.x,r.y);if(buildingAt(r.x,r.y)?.kind!=='clinic')throw Error('Clinic was not built on the acquired home plot');__townTest.step();
  const saved=archivePayload(),normal=()=>{const g=JSON.parse(archivePayload());delete g.trafficState;delete g.visualState;return g;};__townTest.step(30);const end=normal();if(!hydrateSave(saved))throw Error('Mixed redevelopment save rejected');__townTest.step(30);if(JSON.stringify(normal())!==JSON.stringify(end))throw Error('Post-redevelopment exact continuation diverged');
  const valid=validateTown();if(!valid.ok||Math.abs(totalMoney()-s.total)>.001||Math.max(...goodsBalance().map(g=>Math.abs(g.error)))>.001)throw Error('Combined accounts invalid');return {households:r.households.length,identitiesPreserved:true,replacementClinic:true,exactContinuation:true,fares:G.transit.fares,valid};
 },
 retire:()=>{
  const s=__combinedTransitState,rail=G.transit.routes.find(r=>r.id===s.rail),station=readBuild(s.stations[0]);setTransitLevel(s.rail,0);if(urbanClearanceQuote(station.x,station.y).ok||removeTransitFacility(station.id))throw Error('Suspending a route confiscated its station');
  if(!deleteTransitRoute(rail.id)||!removeTransitFacility(s.stations[0])||removeTransitFacility(s.stations[0])||!removeTransitFacility(s.stations[1])||!removeUnusedGuideway())throw Error('Explicit asset retirement/salvage failed');if(removeTransitFacility(s.depot))throw Error('Bus depot was removed while in use');if(!deleteTransitRoute(s.bus)||!removeTransitFacility(s.depot))throw Error('Unused depot could not retire');
  const valid=validateTown();if(!valid.ok||Math.abs(totalMoney()-s.total)>.001)throw Error('Retirement created cash or invalid land');return {suspendedStationProtected:true,explicitRetirement:true,noDuplicateSalvage:true,remainingTracks:G.transit.tracks.length,cashDrift:totalMoney()-s.total,valid};
 }
};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1280,'height':800});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda route:route.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();rows={'setup':p.evaluate('__combinedTransit.setup()')};rows['outages']=p.evaluate('__combinedTransit.outages()');rows['clearanceQuote']=p.evaluate('__combinedTransit.prepareRedevelopment()');p.locator(f'[data-urban-clear="{rows["clearanceQuote"]["id"]}"]').click();p.locator('[data-event-choice="0"]').click();rows['redevelopment']=p.evaluate('__combinedTransit.finishRedevelopment()');rows['retirement']=p.evaluate('__combinedTransit.retire()');assert not errors,errors;b.close()
server.shutdown();out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledExistingCashAndStaff':True,'results':rows,'errors':errors};(ROOT/'reports/transit-combined-redevelopment-8.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));print('PASS real paid bus/rail commuter,21deeds, closure/detour/reopening, interrupted save, actual rehousing/clearance UI, clinic, exact continuation and protected explicit retirement')
