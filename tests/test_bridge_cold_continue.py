"""Actual-origin cold Continue of bridge/model/RNG/traffic; invalidated service caches are explicit."""
import ast,hashlib,json
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT
source=(ROOT/'assets/game.js').read_text()
def probe_from(name):
 tree=ast.parse((ROOT/'tests'/name).read_text())
 return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe=probe_from('test_road_bridge_art.py')+'\n'+probe_from('test_cold_continue_canonical.py').replace('seed(42);','__bridgeArtTest.setup();__townTest.step(1);')
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'assets')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.route('**/game.js',lambda route:route.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'),content_type='application/javascript'));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();before=p.evaluate('__coldCanonical.prepare()');p.reload();p.locator('#continue').wait_for(state='visible');p.evaluate('__coldCanonical.enter()');p.locator('#welcome').wait_for(state='hidden');after=p.evaluate('__coldCanonical.read()');b.close()
finally:server.shutdown()
transient=['serviceProvision','privateServiceProvision']
changed={k:{'before':before['state'].get(k),'after':after['state'].get(k)} for k in set(before['state'])|set(after['state']) if k not in transient and before['state'].get(k)!=after['state'].get(k)}
if changed:print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'changed':changed,'trafficBefore':before['traffic'],'trafficAfter':after['traffic']},indent=2),flush=True)
assert not changed and before['traffic']==after['traffic'],'Bridge cold Continue changed authoritative state'
assert all(after['state'].get(k) is None for k in transient), 'Hydration deliberately clears derived service caches'
assert len(after['state']['bridges'])==1 and after['state']['regionalTrade']['shipments'] and before['traffic']>0
print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'authoritativeStateIncludingRNGAndTrafficEqual':True,'excludedInvalidatedServiceCaches':transient,'bridge':after['state']['bridges'][0],'traffic':after['traffic'],'shipments':len(after['state']['regionalTrade']['shipments'])},indent=2))
print('PASS paid bridge plus live freight cold reload/Continue; authoritative model/RNG/traffic equal, service-cache invalidation explicit')
