"""Cold road/passenger caches and actual post-restore Public Works response."""
from test_mobile_rendering import ROOT
from playwright.sync_api import sync_playwright
import ast,json,hashlib,functools,http.server,threading,math
source=(ROOT/'assets/game.js').read_text();m=ast.parse((ROOT/'tests/test_v7_live_large_town.py').read_text());large=next(ast.literal_eval(n.value.args[0]) for n in ast.walk(m) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='town' for t in n.targets))
probe=(ROOT/'tools/qa_live_network.js').read_text()+r'''
window.__coldTransitCaches=()=>{
 const save=archivePayload(),money=totalMoney(),fares=G.transit.fares;if(!hydrateSave(save))throw Error('Active network restore failed');const before=JSON.stringify(G),start=performance.now(),net=graph(),graphMs=performance.now()-start,at=performance.now();let queries=0,rides=0;
 for(const h of G.households)for(const f of G.firms.filter(f=>!f.closed)){if(queries>=5000)break;const home=readBuild(h.home),work=readBuild(f.building);roadDistance(net.portals.get(h.home),net.portals.get(f.building));const journey=transitJourney(home,work);queries++;if(journey)rides++;}
 const coldMs=performance.now()-at,t=performance.now();let warm=0;for(const h of G.households)for(const f of G.firms.filter(f=>!f.closed)){if(warm>=5000)break;roadDistance(net.portals.get(h.home),net.portals.get(f.building));transitJourney(readBuild(h.home),readBuild(f.building));warm++;}
 if(before!==JSON.stringify(G)||Math.abs(totalMoney()-money)>.001||fares!==G.transit.fares)throw Error('Cache fill paid another fare or changed the city');
 return {grid:T,deeds:G.charter.owned.length,population:G.stats.population,operating:G.transit.routes.filter(r=>r.stats.operating).length,queries,possibleJourneys:rides,graphMs,coldMs,warmMs:performance.now()-t,distanceTrees:net.distanceTrees?.size||0,originTrees:transitRouting().homes.size,itineraries:transitRouting().journeys.size,noEconomicWrites:true};
};
window.__coldTransitPanel=()=>{const save=archivePayload(),cash=totalMoney(),fares=G.transit.fares,start=performance.now();if(!hydrateSave(save)||totalMoney()!==cash||G.transit.fares!==fares)throw Error('Restore changed paid money');openPanel('construction');const synchronousMs=performance.now()-start;return new Promise(resolve=>requestAnimationFrame(()=>resolve({synchronousMs,nextFrameMs:performance.now()-start,paused,day:G.day,moneyDrift:totalMoney()-cash,operating:G.transit.routes.filter(r=>r.stats.operating).length})));};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda route:route.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate(large);p.evaluate('__liveNetworkBuild()');p.evaluate('__townTest.step(1)');p.locator('#panelClose').click()
 for zoom in [.95,.2]:
  p.evaluate('(z)=>__townTest.capture({zoom:z})',zoom);cache=p.evaluate('__coldTransitCaches()');panel=p.evaluate('__coldTransitPanel()');assert cache['operating']==3 and cache['possibleJourneys']>0,cache;assert cache['distanceTrees']<=32 and cache['originTrees']<=512 and cache['itineraries']<=4096,cache;assert abs(panel['moneyDrift'])<.001 and panel['nextFrameMs']<500,panel;p.locator('#panelClose').click();rows.append({'zoom':zoom,'cold':cache,'postRestoreUI':panel})
 assert not errors,errors;b.close()
server.shutdown();out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'hostOnly':True,'coldIncludesGraphAndCacheRebuild':True,'rows':rows,'errors':errors};(ROOT/'reports/transit-cold-start-8.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));print('PASS active paid network cold restore/cache fills, bounded memory, no duplicate fares, near/overview Public Works response')
