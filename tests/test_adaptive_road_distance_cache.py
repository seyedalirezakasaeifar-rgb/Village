"""Exact chain oracle, repeated employer workload, byte cap and graph invalidation."""
from pathlib import Path
import functools,hashlib,http.server,json,subprocess,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'assets/game.js').read_text()
old=subprocess.check_output(['git','show','cc86311:src/60-renderer.js'],cwd=ROOT,text=True)
old=old[old.index('function roadDistancesFrom('):old.index('function beginVehicle(')]
old=old.replace('roadDistancesFrom','baselineRoadDistancesFrom').replace('roadDistance(','baselineRoadDistance(').replace('const DistanceArray=','baselineBuilds++;const DistanceArray=')
probe=old+r'''
let baselineBuilds=0;
window.__adaptiveDistance=()=>{
 const savedGraph=graph,before=JSON.stringify(G),make=n=>{const neighbors=new Map(),parts=new Int32Array(G.tiles.length);for(let i=0;i<n;i++)neighbors.set(i,[...(i?[i-1]:[]),...(i<n-1?[i+1]:[])]);return {neighbors,parts};};
 try{
  const workloads=[];
  for(const baseline of [true,false]){
   const net=make(2048);graph=()=>net;baselineBuilds=0;const call=baseline?baselineRoadDistance:roadDistance,start=performance.now();let sum=0;
   for(let repeat=0;repeat<2;repeat++)for(let home=600;home<728;home++)for(let job=0;job<64;job++){const d=call(home,job);if(d!==Math.abs(home-job))throw Error('Distance oracle mismatch');sum+=d;}
   workloads.push({baseline,ms:performance.now()-start,sum,builds:baseline?baselineBuilds:net.distanceRows.stats.builds,stats:net.distanceRows?.stats,bytes:net.distanceRows?.bytes||0});
  }
  if(workloads[0].sum!==workloads[1].sum||workloads[1].builds>=workloads[0].builds)throw Error('No genuine reuse improvement '+JSON.stringify(workloads));
  const net=make(2048);graph=()=>net;
  for(let pass=0;pass<2;pass++)for(let root=0;root<512;root++){const row=roadDistancesFrom(root,net);if(row[2047]!==2047-root||row[4000]!==-1)throw Error('Expanded row mismatch');}
  if(net.distanceRows.stats.builds!==512||net.distanceTrees.size!==32)throw Error('Expanded rows thrashed compact working set');
  const cap=make(G.tiles.length);graph=()=>cap;for(let root=0;root<160;root++)roadDistancesFrom(root,cap);
  if(cap.distanceRows.bytes>ROAD_DISTANCE_ROW_BYTES||cap.distanceRows.stats.evictions===0)throw Error('Byte cap not exercised');
  for(let root=G.tiles.length;root<G.tiles.length+1000;root++)roadDistanceRow(root,cap);
  if(cap.distanceRows.rows.size>128)throw Error('Invalid roots retained');
  const graphOwner={rows:cap.distanceRows.rows.size,bytes:cap.distanceRows.bytes,stats:cap.distanceRows.stats};
  if(before!==JSON.stringify(G))throw Error('Query changed model');
  graph=savedGraph;const first=graph();roadDistanceRows(first);invalidateRoads(false);const second=graph();if(first===second||second.distanceRows)throw Error('Stale topology cache survived invalidation');
  return {workloads,expanded:{rows:net.distanceRows.rows.size,bytes:net.distanceRows.bytes,stats:net.distanceRows.stats},cap:graphOwner,invalidated:true,unchanged:true};
 }finally{graph=savedGraph;}
};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page();p.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42)");result=p.evaluate('__adaptiveDistance()');b.close()
server.shutdown();result['source_sha256']=hashlib.sha256(source.encode()).hexdigest();out=ROOT/'reports/integration/adaptive-road-distance-8';out.mkdir(parents=True,exist_ok=True);(out/'queries.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
