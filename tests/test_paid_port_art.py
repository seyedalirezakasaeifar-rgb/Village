"""Real river orders: subday continuity, sampling, inspection and visual-state purity."""
from test_mobile_rendering import ROOT
from playwright.sync_api import sync_playwright
from PIL import Image
import http.server,threading,json,hashlib,io,time
source=(ROOT/'assets/game.js').read_text();out=ROOT/'docs/previews/paid-port-art';out.mkdir(parents=True,exist_ok=True)
probe=r'''window.__paidPortArt={available:()=>portCargoPoses().length,step:()=>__townTest.step(1),camera:()=>{const a=waterfrontActors(()=>true).find(a=>a.consignment);if(!a)return false;__townTest.capture({x:a.x,y:a.y-10,zoom:1.45});return true;},check:()=>{
 const before=JSON.stringify(G),day=G.day,remainder=acc,zoom=cam.zoom,motion=gameOptions.reducedMotion,o=portCargoPoses()[0];cam.zoom=1;acc=.1;const first=paidPortBoatPose(o);acc=.7;const later=paidPortBoatPose(o);acc=1.65-.00001;const edge=paidPortBoatPose(o);G.day++;acc=.00001;const next=paidPortBoatPose(o);G.day=day;acc=remainder;
 const sample=()=>waterfrontActors(()=>true).map(a=>({id:a.id,x:a.x,y:a.y,dx:a.dx,dy:a.dy,consignment:a.consignment,loads:a.sampledLoads})),a=sample(),b=sample(),boat=waterfrontActors(()=>true).find(a=>a.consignment);let underBridge=true;if(boat){const id=roadId(Math.floor(boat.gx),Math.floor(boat.gy)),tile=G.tiles[id];G.tiles[id]=1;underBridge=!waterfrontActors(()=>true).some(a=>a.consignment===boat.consignment);G.tiles[id]=tile;}let inspected=false,info=null,paidTransferRoute=false;if(boat){inspected=inspectWaterTripAt(boat.x,boat.y);info=selectedWaterInfo();const load=G.regionalTrade.shipments.find(s=>s.id===boat.consignment),mode=load.mode,active=load.activePath,road=load.path.slice(0,3),points=[],g={save(){},restore(){},setLineDash(){},beginPath(){},moveTo(x,y){points.push([x,y])},lineTo(x,y){points.push([x,y])},stroke(){}};try{load.mode=undefined;load.activePath=road;drawSelectedWaterRoute(g);paidTransferRoute=JSON.stringify(points)===JSON.stringify(road.map(id=>iso(id%T+.5,(id/T|0)+.5)));}finally{load.mode=mode;load.activePath=active;}closePanel();}
 const api=portCargoPoses;portCargoPoses=()=>{throw Error('Hidden paid cargo queried')};cam.zoom=.2;const far=waterfrontActors(()=>true).length;cam.zoom=1;gameOptions.reducedMotion=true;const reduced=waterfrontActors(()=>true).length;gameOptions.reducedMotion=motion;portCargoPoses=api;cam.zoom=zoom;
 return {paidTransferRoute,underBridge,subdayDistance:Math.hypot(later.x-first.x,later.y-first.y),boundaryJump:Math.hypot(next.x-edge.x,next.y-edge.y),stable:JSON.stringify(a)===JSON.stringify(b),unchanged:before===JSON.stringify(G),far,reduced,actors:a.length,paidSamples:a.filter(x=>x.consignment).length,sampledLoads:a.filter(x=>x.consignment).reduce((n,a)=>n+a.loads,0),inspected,info};
}};'''
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT/'assets'),**k)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();frames=[]
try:
 with sync_playwright() as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'),content_type='text/javascript'));p.goto('http://127.0.0.1:'+str(server.server_port)+'/index.html');p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');p.locator('[data-panel=economy]').click();p.locator('#portFreightOffice').evaluate('e=>e.open=true');button=p.locator('[data-port-direction=import]:not([disabled])').first
  for _ in range(8):
   if button.is_disabled():break
   button.click();p.locator('[data-event-choice="0"]').click()
  p.keyboard.press('Escape')
  for _ in range(30):
   if p.evaluate('__paidPortArt.available()'):break
   p.evaluate('__paidPortArt.step()')
  assert p.evaluate('__paidPortArt.available()');r=p.evaluate('__paidPortArt.check()');assert r['paidTransferRoute'];assert r['underBridge'] and r['subdayDistance']>0 and r['boundaryJump']<.1 and r['stable'] and r['unchanged'] and r['far']==r['reduced']==0 and r['paidSamples']>0 and r['sampledLoads']>=r['paidSamples'] and r['inspected'] and 'Owned import' in r['info']['journey'],r
  assert p.evaluate('__paidPortArt.camera()');r['renderBenchMs']=p.evaluate('__townTest.renderBench(100)');p.locator('#view').screenshot(path=str(out/'river-loads.png'));p.evaluate('__townTest.capture({night:true})');p.locator('#view').screenshot(path=str(out/'night.png'));p.evaluate('__townTest.capture({night:false})');p.locator('#pause').click();started=time.monotonic()
  for _ in range(32):
   p.evaluate('__paidPortArt.camera()');frames.append(Image.open(io.BytesIO(p.locator('#view').screenshot())).convert('RGB'));p.wait_for_timeout(60)
  elapsed=time.monotonic()-started;p.locator('#pause').click();assert not errors,errors;b.close()
finally:server.shutdown();server.server_close()
private_capture=ROOT.parent/'scratch/townledger-port-art';private_capture.mkdir(parents=True,exist_ok=True)
frames[0].save(private_capture/'river-session.gif',save_all=True,append_images=frames[1:],duration=round(elapsed/len(frames)*1000),loop=0,optimize=True)
r.update(source_sha256=hashlib.sha256(source.encode()).hexdigest(),errors=errors,capture='Actual reviewed imports; continuous normal-clock session after accelerated waiting for the local river leg. Camera follows visible cargo. Not an FPS benchmark.',frames=len(frames),seconds=elapsed);(out/'checks.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
