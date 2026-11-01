"""Actual HTTP origin cold Continue; strict full state, including live traffic."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[1];source=(ROOT/'assets/game.js').read_text()
probe=r'''
const actualEnterContinuedTown=enterContinuedTown;enterContinuedTown=function(){actualEnterContinuedTown();paused=true;};
const canonicalCold=v=>Array.isArray(v)?v.map(canonicalCold):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonicalCold(v[k])])):v;
window.__coldCanonical={legacy:()=>{const saved=JSON.parse(archivePayload());delete saved.regionalTrade;if(!hydrateSave(saved)||!G.regionalTrade)throw Error('Missing legacy trade not initialized');const a=canonicalCold(JSON.parse(archivePayload()));const expectedRng=rngState;enterContinuedTown();const c=canonicalCold(JSON.parse(archivePayload()));if(JSON.stringify(a)!==JSON.stringify(c)||rngState!==expectedRng)throw Error('Legacy overview changed initialized model');return true;},prepare:async()=>{paused=true;active='';seed(42);for(let i=0;i<30&&traffic.length<4;i++)beginVehicle();if(!traffic.length)throw Error('No traffic fixture');const raw=archivePayload();if(!await save())throw Error('Initial save failed');return {state:canonicalCold(JSON.parse(raw)),traffic:traffic.length};},read:()=>({state:canonicalCold(JSON.parse(archivePayload())),traffic:traffic.length}),enter:()=>{$('continue').click();}};
'''
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'assets')));Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)+'/index.html'
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.route('**/game.js',lambda route:route.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'),content_type='application/javascript'));p.goto(url);p.locator('#newTown').click();before=p.evaluate('__coldCanonical.prepare()');p.reload();p.locator('#continue').wait_for(state='visible');p.evaluate('__coldCanonical.enter()');p.locator('#welcome').wait_for(state='hidden');after=p.evaluate('__coldCanonical.read()');legacy=p.evaluate('__coldCanonical.legacy()') if not os.environ.get('NATIVE_CANONICAL_EXPECT_FAIL') else None;b.close()
finally:server.shutdown()
def differences(a,b,path=''):
 if type(a)!=type(b):return [{'path':path,'beforeType':type(a).__name__,'afterType':type(b).__name__}]
 if isinstance(a,dict):return sum((differences(a.get(k),b.get(k),path+'.'+k) if k in a and k in b else [{'path':path+'.'+k,'missingBefore':k not in a,'missingAfter':k not in b}]for k in set(a)|set(b)),[])
 if isinstance(a,list):return [{'path':path,'beforeLength':len(a),'afterLength':len(b)}] if len(a)!=len(b) else sum((differences(x,y,path+'.'+str(i))for i,(x,y)in enumerate(zip(a,b))),[])
 return [] if a==b else [{'path':path,'before':a,'after':b}]
diff=differences(before['state'],after['state']);out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'exactCanonical':not diff,'trafficBefore':before['traffic'],'trafficAfter':after['traffic'],'legacyTradeDefaultStable':legacy,'differences':diff};dest=ROOT/'reports/cold-continue-canonical';dest.mkdir(exist_ok=True);label='before' if os.environ.get('NATIVE_CANONICAL_EXPECT_FAIL') else 'after';(dest/(label+'.json')).write_text(json.dumps(out,indent=2)+'\n');assert bool(diff)==bool(os.environ.get('NATIVE_CANONICAL_EXPECT_FAIL')),out;print('PASS',out)
