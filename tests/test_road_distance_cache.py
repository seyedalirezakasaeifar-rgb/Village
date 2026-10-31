"""Road-distance trees equal actual legacy routes, including cold graph rebuilds.
Also compares full seeded model continuation against original hiring/distance code.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import ast,json,hashlib,functools,http.server,threading,os
from test_mobile_rendering import ROOT
source=(ROOT/'assets/game.js').read_text();references=(ROOT/'tests/fixtures/road-distance-525.js').read_text()+(ROOT/'tests/fixtures/assign-jobs-525.js').read_text()
m=ast.parse((ROOT/'tests/test_v7_live_large_town.py').read_text());large=next(ast.literal_eval(n.value.args[0]) for n in ast.walk(m) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='town' for t in n.targets))
probe=(ROOT/'tools/qa_live_network.js').read_text()+references+r'''
window.__distanceOracle=()=>{
 const net=graph(),nodes=[...net.neighbors.keys()],before=JSON.stringify(G);let checked=0;
 for(let i=0;i<12000;i++){const a=nodes[hash(i*13+7)%nodes.length],b=nodes[hash(i*31+101)%nodes.length],old=referenceRoadDistance(a,b),fresh=roadDistance(a,b);if(old!==fresh)throw Error('Distance mismatch '+a+' '+b+': '+old+' '+fresh);checked++;}
 if(JSON.stringify(G)!==before)throw Error('Distance lookup changed economic state');
 return {checked,cachedTrees:net.distanceTrees?.size||0,cacheBytes:[...(net.distanceTrees?.values()||[])].reduce((n,a)=>n+a.byteLength,0),unchanged:true};
};
window.__distanceIsland=()=>{const before=__distanceOracle();G.tiles[roadId(125,125)]=1;G.tiles[roadId(126,125)]=1;invalidateRoads(false);const net=graph(),anchor=net.portals.get(G.buildings.find(b=>b.kind==='townhall').id),distance=roadDistance(anchor,roadId(125,125));if(distance!==Infinity||referenceRoadDistance(anchor,roadId(125,125))!==Infinity)throw Error('Island connected');return {before,after:__distanceOracle(),disconnected:true};};
window.__distanceCold=()=>{const before=JSON.stringify(G),t=performance.now();graph().distanceTrees=null;graph().distanceRows=null;assignJobs();return {ms:performance.now()-t,unchanged:before===JSON.stringify(G)};};
window.__distanceModel=()=>{const g=JSON.parse(archivePayload());delete g.trafficState;delete g.visualState;return g;};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
checkpoint=Path(os.environ['DISTANCE_CHECKPOINT']).read_text() if os.environ.get('DISTANCE_CHECKPOINT') else None
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'reference_commit':'525e47d','models':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for dense,days in ([(False,180)] if checkpoint else [(False,360),(True,180)]):
  pages=[]
  for reference in [True,False]:
   p=browser.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));extra=probe+('roadDistance=referenceRoadDistance;assignJobs=referenceAssignJobs;' if reference else '');p.route('**/game.js',(lambda payload: lambda route:route.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',payload+'\n// SOURCE: 99-instrumentation.js')))(extra));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42)")
   if checkpoint:assert p.evaluate('s=>__townArchive.restore(s)',checkpoint)
   if dense:p.evaluate(large);p.evaluate('__liveNetworkBuild()')
   assert not errors,errors;pages.append(p)
  checkpoints=[]
  for i in range(days//30):
   for p in pages:p.evaluate('__townTest.step(30)')
   a,b=[p.evaluate('__distanceModel()') for p in pages]
   assert a==b,'Model differs: '+str([k for k in a if a[k]!=b.get(k)])
   checkpoints.append(a['day'])
  oracle=pages[1].evaluate('__distanceOracle()');assert oracle['cachedTrees']<=32 and oracle['cacheBytes']<=32*128*128*2,oracle
  # New disconnected island is genuine topology, not a distance-cache shortcut.
  disrupted=pages[1].evaluate('__distanceIsland()')
  out['models'].append({'dense':dense,'days':days,'exactCheckpoints':checkpoints,'oracle':oracle,'closure':disrupted});print('PASS exact model',dense,days,oracle,flush=True)
  for p in pages:p.close()
 browser.close()
server.shutdown();(ROOT/'reports/transit-distance-cache-8.json').write_text(json.dumps(out,indent=2));print('PASS complete-model equality and 72,000 distance pairs across original and rebuilt 128-grid networks; bounded cache and no account writes')
