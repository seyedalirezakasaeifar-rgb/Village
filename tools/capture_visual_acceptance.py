"""HTTP-origin integrated128-world mobile map review with real paid-service fixtures."""
from pathlib import Path
import ast,json,hashlib,sys,http.server,threading
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_mobile_rendering import ROOT
from playwright.sync_api import sync_playwright
out=ROOT/'docs/previews/visual-acceptance';out.mkdir(parents=True,exist_ok=True)
def probe(file):return next(ast.literal_eval(n.value) for n in ast.parse((ROOT/'tests'/file).read_text()).body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='probe' for x in n.targets))
big=next(n.value for n in ast.walk(ast.parse((ROOT/'tests/test_v7_live_large_town.py').read_text())) if isinstance(n,ast.Constant) and isinstance(n.value,str) and 'while(g.people.length<2000' in n.value)
mall=next(n.value for n in ast.walk(ast.parse((ROOT/'tests/test_urban_evolution.py').read_text())) if isinstance(n,ast.Constant) and isinstance(n.value,str) and 'Controlled catchment worker' in n.value)
source=(ROOT/'assets/game.js').read_text();extra=probe('test_urban_evolution.py')+'\n'+probe('test_private_services.py')+'\n'+(ROOT/'tools/qa_live_network.js').read_text()+'''\nwindow.__acceptCamera=(kind)=>{const b=G.buildings.find(b=>kind==='mall'?b.retailCentre:b.kind===kind),p=iso(b.x,b.y);__townTest.capture({x:p[0]+40,y:p[1]+15,zoom:1.3});};'''
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT/'assets'),**k)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();rows=[]
try:
 with sync_playwright() as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda route:route.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',extra+'\n// SOURCE: 99-instrumentation.js'),content_type='text/javascript'));p.goto('http://127.0.0.1:'+str(server.server_port)+'/index.html');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.evaluate(big);network=p.evaluate('__liveNetworkBuild()');p.evaluate('__townTest.step(15)')
  def shot(name,opts=None):
   if opts:p.evaluate('(o)=>__townTest.capture(o)',opts)
   p.locator('#view').screenshot(path=str(out/(name+'.png')));rows.append(name)
  shot('network-near',{'zoom':.95});shot('network-far',{'zoom':.2});p.evaluate('__acceptCamera("elevated_station")');shot('rail-crossing');shot('rail-night',{'night':True});p.evaluate(mall);p.evaluate('__acceptCamera("mall")');shot('market-hall',{'night':False});shot('market-night',{'night':True})
  for kind in ['school','fire']:
   p.evaluate('k=>__privateFixture(k,100)',kind);p.evaluate('__townTest.step(2)');p.evaluate('__acceptCamera',kind);shot('private-'+kind,{'night':False})
  assert not errors,errors;b.close()
finally:server.shutdown();server.server_close()
(out/'capture-receipt.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'origin':'Loopback HTTP, shipped assets','controlledFixtures':True,'allDeedsNetwork':network,'captures':rows,'errors':errors},indent=2)+'\n');print(rows)
