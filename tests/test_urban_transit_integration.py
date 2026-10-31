"""Joint atlas, cargo, passenger accounts and protected redevelopment acceptance."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,json,hashlib,functools,http.server,threading
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
module=ast.parse((ROOT/'tests/test_transit_network.py').read_text())
setup=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe=r'''
window.__jointMigration=size=>{
 const live=archivePayload(),input=JSON.parse(live),map=id=>{if(id%T>=size||(id/T|0)>=size)throw Error('Fixture extends beyond legacy bounds');return (id/T|0)*size+id%T;},list=a=>a.map(map),keys=o=>Object.fromEntries(Object.entries(o||{}).map(([id,n])=>[map(+id),n]));
 input.tiles=Array.from({length:size*size},(_,id)=>G.tiles[(id/size|0)*T+id%size]);
 for(const b of input.buildings)if(b.footprint)b.footprint=list(b.footprint);
 for(const name of ['roadClasses','streetNames','landUse','fieldOwner'])if(input[name])input[name]=keys(input[name]);
 if(input.roadWear)input.roadWear=Array.from({length:size*size},(_,id)=>G.roadWear[(id/size|0)*T+id%size]);
 if(input.privateRoads)input.privateRoads=list(input.privateRoads);
 for(const p of input.projects||[])for(const name of ['plots','runway'])if(p[name])p[name]=list(p[name]);
 if(input.airport?.runway)input.airport.runway=list(input.airport.runway);
 for(const o of input.freight||[])if(o.path)o.path=list(o.path);
 for(const o of [...(input.regionalTrade?.shipments||[]),...(input.regionalTrade?.recent||[])])for(const name of ['path','activePath'])if(o[name])o[name]=list(o[name]);
 for(const o of input.waterway?.manifests||[])if(o.path)o.path=list(o.path);
 for(const v of input.trafficState?.vehicles||[])if(v.path)v.path=list(v.path);
 if(input.trafficState)input.trafficState.gates=(input.trafficState.gates||[]).map(([id,n])=>[map(id),n]);
 input.transit=remapTransitState(input.transit,map);input.gridSize=size;
 const current=JSON.stringify(G.transit),cash=totalMoney(),normalized=normalizeRegionArchive(input);
 if(archivePayload()!==live||JSON.stringify(normalized.transit)!==current)throw Error('Pure migration changed live city or passenger accounts');
 const base=ensureScenarioProgramme;try{ensureScenarioProgramme=()=>{throw Error('Injected post-validation adoption failure')};if(hydrateSave(live))throw Error('Faulted adoption succeeded');}finally{ensureScenarioProgramme=base;}if(archivePayload()!==live)throw Error('Faulted adoption lost live state');
 const bad=JSON.parse(JSON.stringify(input));bad.transit.routes[0].path[0]=size*size+5;if(hydrateSave(bad)||archivePayload()!==live)throw Error('Failed legacy transit import mutated live city');
 if(!hydrateSave(input)||JSON.stringify(G.transit)!==current||Math.abs(totalMoney()-cash)>.001)throw Error('Legacy transit migration lost accounts');
 if(!validateTown().ok)throw Error('Migrated joint city invalid');return {size,pure:true,atomicFailure:true,paidAccountsPreserved:true};
};
window.__jointAnnex=()=>{
 const total=totalMoney(),cash=Math.min(G.region,6000000);G.region-=cash;G.treasury+=cash;
 const f=G.firms.find(f=>f.kind==='grocer');for(const market of OUTSIDE_MARKETS){if(dispatchRegional(f,'food',30,'import',regionalQuote(f,market,'food','import'))>0)break;}if(!ensureRegionalTrade().shipments.length)throw Error('No paid live cargo');
 const cargo=JSON.stringify(ensureRegionalTrade().shipments),transit=JSON.stringify(G.transit),depot=G.transit.routes[0].depot,b=readBuild(depot),blocked=urbanClearanceQuote(b.x,b.y);if(blocked.ok)throw Error('Active passenger depot clearable');
 let bought=0;while(bought<ANNEX_PARCELS.length){const p=ANNEX_PARCELS.find(p=>!G.charter.owned.includes(p.id)&&parcelAdjacent(p));if(!p)break;if(!purchaseParcel(p.id,purchaseParcelQuote(p)))throw Error('Adjoining deed failed: '+p.id);bought++;}
 if(bought!==21||JSON.stringify(ensureRegionalTrade().shipments)!==cargo||JSON.stringify(G.transit)!==transit)throw Error('Annexation changed live freight/passenger accounts');
 __townTest.step(60);const valid=validateTown(),error=Math.max(...goodsBalance().map(r=>Math.abs(r.error)));if(!valid.ok||Math.abs(totalMoney()-total)>.001||error>.001)throw Error('Joint city books failed');
 return {purchased:bought,grid:T,cargoPreserved:true,activeDepotProtected:blocked.reason,days:60,fares:G.transit.fares,routes:G.transit.routes.map(r=>({id:r.id,mode:r.mode,operating:r.stats.operating,boardings:r.stats.boardings})),cashDrift:totalMoney()-total,goodsError:error};
};
'''
# Quote API deliberately reuses the authoritative survey price.
probe=probe.replace('purchaseParcelQuote(p)','parcelSurvey(p).price')
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda route:route.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',setup+'\n'+probe+'\n// SOURCE: 99-instrumentation.js')));p.goto('http://127.0.0.1:'+str(server.server_port)+'/index.html');p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__transitProbe.setup()');assert r['route'];p.evaluate('__transitProbe.rail()');p.evaluate('__townTest.step(1)');migrations=[p.evaluate('s=>__jointMigration(s)',size) for size in [56,80]];joint=p.evaluate('__jointAnnex()');p.locator('#panelClose').click();p.evaluate('__transitProbe.draw()');p.wait_for_timeout(3500);p.screenshot(path=str(ROOT/'reports/development-8.0/urban-transit-joint.png'));assert not errors,errors;b.close()
server.shutdown()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
(ROOT/'reports/development-8.0/urban-transit-integration.json').write_text(json.dumps({'source_sha256':sha,'controlledFundedNetwork':True,'migrations':migrations,'joint':joint,'errors':errors},indent=2)+'\n');print('PASS joint56/80 migration, atomic failure,21deeds with live cargo/fares, protected routed depot,60day accounting',migrations,joint)
