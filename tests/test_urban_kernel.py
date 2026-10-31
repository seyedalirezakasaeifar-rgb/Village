"""Exact spatial arrays, mutation invalidation, late-town timing and model replay."""
from pathlib import Path
import functools,gzip,hashlib,http.server,json,subprocess,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];source=(ROOT/'assets/game.js').read_text();old=subprocess.check_output(['git','show','bb02bbc:src/27-urban-evolution.js'],cwd=ROOT,text=True);old=old[old.index('function urbanSpatial()'):old.index('function urbanDescriptor(')].replace('function urbanSpatial()','function referenceUrbanSpatial()')
archive=gzip.decompress(subprocess.check_output(['git','show','833afee35aa714919a38e420e74cee1f719315db:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)).decode()
probe=old+r'''
function kernelDigest(c){return JSON.stringify({homes:Array.from(c.homes),jobs:Array.from(c.jobs),industry:Array.from(c.industry),amenity:Array.from(c.amenity),blocks:c.blocks,median:c.median});}
window.__kernelAudit=()=>{
 const before=JSON.stringify(G),cases=[];const compare=label=>{invalidateUrban();const expected=kernelDigest(referenceUrbanSpatial());invalidateUrban();const actual=kernelDigest(urbanSpatial());if(actual!==expected)throw Error('Spatial mismatch '+label);cases.push(label);};compare('late town');
 const f=G.firms.find(f=>!f.closed),h=G.households.find(h=>h.people.length),b=readBuild(h.home),originalIncome=h.income,originalCondition=b.condition,hadClosed=Object.hasOwn(f,'closed'),originalClosed=f.closed;
 for(const [label,change,undo] of [['jobs',()=>f.jobs++,()=>f.jobs--],['closure',()=>f.closed=true,()=>{if(hadClosed)f.closed=originalClosed;else delete f.closed;}],['income',()=>h.income+=17,()=>h.income=originalIncome],['condition',()=>b.condition-=3,()=>b.condition=originalCondition],['day',()=>G.day++,()=>G.day--],['revision',()=>G.urban.revision++,()=>G.urban.revision--]]){change();invalidateUrban();compare(label);undo();invalidateUrban();}
 if(before!==JSON.stringify(G))throw Error('Audit changed state '+Object.keys(G).filter(k=>JSON.stringify(G[k])!==JSON.stringify(JSON.parse(before)[k])));
 const timing=[];for(let round=0;round<6;round++){const results={};for(const name of round%2?['candidate','reference']:['reference','candidate']){const fn=name==='candidate'?urbanSpatial:referenceUrbanSpatial;const start=performance.now();for(let i=0;i<100;i++){invalidateUrban();fn();}results[name]=performance.now()-start;}timing.push(results);}invalidateUrban();return {cases,timing,unchanged:true,buildings:G.buildings.length,day:G.day};
};
window.__kernelModel=()=>{const g=JSON.parse(archivePayload());delete g.trafficState;delete g.visualState;return g;};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();result={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'checkpoint_sha256':hashlib.sha256(archive.encode()).hexdigest()}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);pages=[]
 for reference in [True,False]:
  p=browser.new_page();extra=probe+('urbanSpatial=referenceUrbanSpatial;' if reference else '');p.route('**/game.js',(lambda payload:lambda r:r.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',payload+'\n// SOURCE: 99-instrumentation.js')))(extra));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townArchive.restore(s)',archive);pages.append(p)
 result['audit']=pages[1].evaluate('__kernelAudit()');print('PASS array/mutation oracle',result['audit'],flush=True);result['exactDays']=[]
 for i in range(6):
  for p in pages:p.evaluate('__townTest.step(30)')
  a,b=[p.evaluate('__kernelModel()') for p in pages];assert a==b,[k for k in a if a[k]!=b.get(k)];result['exactDays'].append(a['day']);print('PASS exact continuation',a['day'],flush=True)
 browser.close()
server.shutdown();out=ROOT/'reports/integration/urban-kernel-8';out.mkdir(parents=True,exist_ok=True);(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
