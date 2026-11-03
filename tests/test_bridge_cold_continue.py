"""Full-state cold Continue immediately after bridge/cargo work and after a committed day."""
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
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'assets')));Thread(target=server.serve_forever,daemon=True).start();rows=[]
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for steps in [0,1]:
   probe=probe_from('test_road_bridge_art.py')+'\n'+probe_from('test_cold_continue_canonical.py').replace('seed(42);',f'__bridgeArtTest.setup();__townTest.step({steps});')
   context=b.new_context();p=context.new_page();p.route('**/game.js',lambda route:route.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'),content_type='application/javascript'));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();before=p.evaluate('__coldCanonical.prepare()');p.reload();p.locator('#continue').wait_for(state='visible');p.evaluate('__coldCanonical.enter()');p.locator('#welcome').wait_for(state='hidden');after=p.evaluate('__coldCanonical.read()')
   changed=[k for k in set(before['state'])|set(after['state']) if before['state'].get(k)!=after['state'].get(k)];assert before==after,{'steps':steps,'changed':changed}
   assert len(after['state']['bridges'])==1 and after['state']['regionalTrade']['shipments'] and before['traffic']>0
   rows.append({'committedDaysAfterWork':steps,'fullCanonicalStateEqual':True,'excludedFields':[],'bridge':after['state']['bridges'][0],'traffic':after['traffic'],'shipments':len(after['state']['regionalTrade']['shipments'])});context.close()
  b.close()
finally:server.shutdown()
print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':rows},indent=2));print('PASS immediate/committed bridge plus live freight full-state cold reload/Continue, including paid service receipts; no exclusions')
