"""Source-bound paired diorama and paid freight art review in host Chromium."""
from pathlib import Path
import sys,subprocess,json,hashlib,io
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
from PIL import Image
out=ROOT/'reports/visual-world';out.mkdir(parents=True,exist_ok=True)
base=subprocess.check_output(['git','show','1de6930:assets/game.js'],cwd=ROOT).decode()
current=(ROOT/'assets/game.js').read_text();results=[];frames=[]
probe='''window.__artCamera=(scene)=>{
 const shop=G.buildings.find(b=>b.kind==='factory'),m=OUTSIDE_MARKETS[0],id=regionalGateway(m),p=scene==='gateway'?roadCenter(id):iso(shop.x,shop.y);
 cam={x:p[0],y:p[1]+30,zoom:scene==='gateway'?1.8:1.6};dirty=true;draw();
};window.__freightFilm=(t)=>{
 const m=OUTSIDE_MARKETS[0],gate=regionalGateway(m),f=G.firms.find(f=>regionalRoadPath(f,m).length>4),path=regionalRoadPath(f,m).slice().reverse();
 G.regionalTrade.shipments=[{id:1,firm:f.id,market:m.id,direction:'import',good:'food',qty:120,path,started:1,travelDays:10,due:11}];
 G.day=1+Math.floor(t);acc=t%1*1.65;const p=shipmentVisualPose(G.regionalTrade.shipments[0]);cam={x:p.x,y:p.y-12,zoom:2};dirty=true;draw();
};'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for label,source in [('before',base),('after',current)]:
  p=b.new_page(viewport={'width':960,'height':640});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
  p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42)");p.locator('#panelClose').click()
  for scene in ['industry','gateway']:
   p.evaluate('__artCamera',scene);p.locator('#view').screenshot(path=str(out/(label+'-'+scene+'.png')))
  if label=='after':
   for i in range(36):
    p.evaluate('__freightFilm',i*.025);frames.append(Image.open(io.BytesIO(p.locator('#view').screenshot())).convert('RGB'))
  assert not errors,errors
  results.append({'stage':label,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'errors':errors});p.close()
 b.close()
frames[0].save(out/'regional-freight.gif',save_all=True,append_images=frames[1:],duration=90,loop=0,optimize=True)
(out/'comparison.json').write_text(json.dumps({'captures':results,'animation':'Controlled paid import visual timeline, camera following truck; host Chromium, not physical-device FPS.'},indent=2)+'\n');print(results)
