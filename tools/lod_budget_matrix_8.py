from pathlib import Path
import ast,functools,hashlib,http.server,json,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
def literal(path):return next(ast.literal_eval(n.value) for n in ast.parse(path.read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
fixture=literal(ROOT/'tests/test_transit_live_performance.py');setup=literal(ROOT/'tools/profile_session.py');setup=setup[setup.index('window.__session={'):setup.index(' clear:()=>')]+'};'
probe=r'''
let budgetCalls={};for(const name of ['tick','draw','spriteFor','drawSceneSprite','buildingActivity','workdayScenes','trafficUpdate','vehiclePosition','neighbourhoodAmbient']){const base=eval(name),replacement=function(...args){const t=performance.now();try{const r=base.apply(this,args);const c=budgetCalls[name]||(budgetCalls[name]={calls:0,ms:0,actors:0});c.calls++;c.ms+=performance.now()-t;if(Array.isArray(r))c.actors+=r.length;return r}catch(e){throw e}};eval(name+'=replacement')}
window.__budget={mode:(v,s)=>{paused=s===0;speed=s||1;G.speed=speed;acc=0;cam.zoom=v==='far'?.2:.95;centerTownCamera(cam.zoom);if(v==='offscreen'){cam.x=RW;cam.y=0;}dirty=true;},clear:()=>{budgetCalls={}},state:()=>({day:G.day,population:G.stats.population,buildings:G.buildings.length,total:totalMoney(),valid:validateTown(),traffic:JSON.stringify({traffic,trafficClock,trafficElapsed,vehicleSerial}),calls:budgetCalls,atlasBytes}),sample:()=>new Promise(done=>{const times=[],day=G.day,start=performance.now();let prev=0;function f(now){if(prev)times.push(now-prev);prev=now;if(now-start<4000)requestAnimationFrame(f);else done({raf:times,seconds:(now-start)/1000,days:G.day-day});}requestAnimationFrame(f)}),paint:()=>{const before=JSON.stringify(G),rng=rngState;budgetCalls={};for(let i=0;i<6;i++){dirty=true;draw()}return {calls:budgetCalls,modelUnchanged:before===JSON.stringify(G)&&rng===rngState}}};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();out=ROOT/'reports/lod-budget';out.mkdir(exist_ok=True);result={'source_sha256':sha,'hostOnly':True,'rows':[],'errors':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for town in ['dense2000','lateTown']:
  p=b.new_page(viewport={'width':844,'height':390},has_touch=True);p.on('pageerror',lambda e:result['errors'].append(str(e)));p.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',fixture+setup+probe+'\n// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click()
  if town=='dense2000':p.evaluate('__session.setup();__session.evolve()')
  else:assert p.evaluate('s=>__townTest.load(s)',Path('/tmp/townledger-31987fc-late.json').read_text())
  p.locator('#panelClose').click()
  for view in ['near','far','offscreen']:
   for speed in [0,1,8,64]:
    p.evaluate('x=>__budget.mode(...x)',[view,speed]);p.wait_for_timeout(250);p.evaluate('__budget.clear()');before=p.evaluate('__budget.state()');sample=p.evaluate('__budget.sample()');after=p.evaluate('__budget.state()');t=p.evaluate('()=>{const t=performance.now();document.querySelector("[data-panel=economy]").click();return new Promise(r=>requestAnimationFrame(()=>r(performance.now()-t)))}');p.locator('#panelClose').click();p.evaluate('x=>__budget.mode(...x)',[view,0]);paint=p.evaluate('__budget.paint()');a=sorted(sample['raf']);row={'town':town,'view':view,'speed':speed,'seconds':sample['seconds'],'days':sample['days'],'actualRate':sample['days']*1.65/sample['seconds'],'rafP99':a[min(len(a)-1,int(len(a)*.99))],'panelToRAF':t,'calls':after['calls'],'population':after['population'],'buildings':after['buildings'],'pausedPaint':paint,'hiddenTrafficUnchanged':before['traffic']==after['traffic']};result['rows'].append(row);assert after['valid']['ok'] and abs(after['total']-before['total'])<.1 and paint['modelUnchanged'],row;assert not result['errors'];(out/'matrix.json').write_text(json.dumps(result,indent=2)+'\n');print(town,view,speed,round(row['actualRate'],1),round(row['rafP99'],1),flush=True)
  p.close()
 b.close()
server.shutdown()
