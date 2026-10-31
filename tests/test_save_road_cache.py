"""Actual road wear must update cached quality identically across restore."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import threading,hashlib,json,os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];source=Path(os.environ.get('SAVE_QA_SOURCE',str(ROOT/'assets/game.js'))).read_bytes();sha=hashlib.sha256(source).hexdigest()
probe=r'''
window.__roadSaveRegression=()=>{
 __townTest.reset('settlement',42);G.autoBuild=false;__townTest.step(116);G.policy.roadBudget=0;
 ensureRoadWear();for(const id of graph().neighbors.keys())G.roadWear[id]=96.51;G.stats.roadCondition=97;invalidateRoads(false);
 const raw=archivePayload(),initialTotal=totalMoney();
 const canon=v=>Array.isArray(v)?v.map(canon):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canon(v[k])])):v;
 const snapshot=()=>{const g=JSON.parse(archivePayload());delete g.trafficState;delete g.visualState;return canon(g)};
 __townTest.step(1);const uninterrupted=snapshot(),rngA=rngState;
 if(!hydrateSave(raw))throw Error('Checkpoint restore rejected');__townTest.step(1);const restored=snapshot(),rngB=rngState;
 const changed=Object.keys(uninterrupted).filter(k=>JSON.stringify(uninterrupted[k])!==JSON.stringify(restored[k]));
 if(!validateTown().ok||Math.abs(totalMoney()-initialTotal)>.01||Math.max(...goodsBalance().map(g=>Math.abs(g.error)))>.001)throw Error('Financial invariants failed');
 return {day:118,exact:changed.length===0,changed,uninterruptedQuality:uninterrupted.roadMetrics.quality,restoredQuality:restored.roadMetrics.quality,roadCondition:restored.stats.roadCondition,statsDifferences:Object.keys(restored.stats).filter(k=>restored.stats[k]!==uninterrupted.stats[k]).map(k=>({key:k,uninterrupted:uninterrupted.stats[k],restored:restored.stats[k]})),rngA,rngB,moneyDrift:totalMoney()-initialTotal};
};
'''
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.route('**/game.js',lambda r:r.fulfill(body=source.decode().replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'),content_type='application/javascript'));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__roadSaveRegression()');b.close()
finally:server.shutdown();server.server_close()
negative=os.environ.get('SAVE_QA_EXPECT_NEGATIVE')=='1';assert r['rngA']==r['rngB'],r;assert r['exact']!=negative,r
out=Path(os.environ.get('SAVE_QA_CACHE_OUTPUT',str(ROOT/'reports/save-road-cache')));out.mkdir(parents=True,exist_ok=True);(out/('before.json' if negative else 'after.json')).write_text(json.dumps({'source_sha256':sha,'httpOrigin':True,'expectedNegative':negative,'result':r},indent=2)+'\n');print('PASS', 'negative reproduced' if negative else 'exact next-day road-quality continuation',r)
