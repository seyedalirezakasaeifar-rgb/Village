"""A real funded ground-bus pose cannot overwrite opaque elevated guideway pixels."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,json,hashlib,base64
fixture=next(ast.literal_eval(n.value) for n in ast.parse((ROOT/'tests/test_transit_network.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='probe' for x in n.targets))
source=(ROOT/'assets/game.js').read_text();out=ROOT/'docs/previews/render-bug-audit';out.mkdir(parents=True,exist_ok=True)
probe=r'''window.__bridgeAudit=()=>{
 const oldClock=frameClock,before=JSON.stringify(G),make=()=>{const c=document.createElement('canvas');c.width=cv.width;c.height=cv.height;const g=c.getContext('2d');g.imageSmoothingEnabled=false;return {c,g};},mask=make(),bus=make(),old=make(),fixed=make();let found=null;
 for(let time=.1;time<45&&!found;time+=.2){frameClock=time;
  for(const actor of transitArtActors(()=>true).filter(a=>a.mode==='bus')){
   const bounds=scenePaintBounds(actor),decks=viewBuildings.filter(i=>i.kind==='guideway'&&paintBoundsOverlap(bounds,scenePaintBounds(i)));if(!decks.length)continue;
   mask.g.setTransform(1,0,0,1,0,0);mask.g.clearRect(0,0,cv.width,cv.height);mapPaintTransform(mask.g);for(const d of decks)paintTransitStructure(mask.g,d);
   bus.g.setTransform(1,0,0,1,0,0);bus.g.clearRect(0,0,cv.width,cv.height);mapPaintTransform(bus.g);paintTransitVehicle(bus.g,actor);
   const x=Math.max(0,Math.floor(((bounds[0]-cam.x)*cam.zoom+cw/2)*dpr)),y=Math.max(0,Math.floor(((bounds[1]-cam.y)*cam.zoom+ch/2)*dpr)),w=Math.min(cv.width-x,Math.ceil((bounds[2]-bounds[0])*cam.zoom*dpr)),h=Math.min(cv.height-y,Math.ceil((bounds[3]-bounds[1])*cam.zoom*dpr));if(w<=0||h<=0)continue;
   const deck=mask.g.getImageData(x,y,w,h).data,body=bus.g.getImageData(x,y,w,h).data;let overlap=0;for(let p=3;p<deck.length;p+=4)if(deck[p]>250&&body[p]>250)overlap++;if(overlap<20)continue;
   for(const o of [old,fixed]){o.g.setTransform(1,0,0,1,0,0);o.g.drawImage(viewRaster,0,0);mapPaintTransform(o.g);}
   old.g.save();old.g.beginPath();old.g.rect(actor.x-90,actor.y-42,180,90);old.g.clip();for(const a of [actor,...viewBuildings.filter(a=>a.y>=actor.y&&Math.abs(a.x-actor.x)<112&&a.y-actor.y<220)].sort((a,b)=>a.y-b.y))paintSceneLayer(old.g,a);old.g.restore();
   paintSceneActors(fixed.g,[actor],()=>true);
   const original=viewRaster.getContext('2d').getImageData(x,y,w,h).data,a=old.g.getImageData(x,y,w,h).data,b=fixed.g.getImageData(x,y,w,h).data;let oldWrong=0,fixedWrong=0;
   for(let p=0;p<deck.length;p+=4)if(deck[p+3]>250&&body[p+3]>250){if(Math.max(...[0,1,2].map(k=>Math.abs(a[p+k]-original[p+k])))>2)oldWrong++;if(Math.max(...[0,1,2].map(k=>Math.abs(b[p+k]-original[p+k])))>2)fixedWrong++;}
   if(oldWrong>20&&fixedWrong<oldWrong*.05){found={phase:time,overlap,oldWrong,fixedWrong};window.__bridgeImages={old:old.c.toDataURL(),fixed:fixed.c.toDataURL()};break;}
  }
 }frameClock=oldClock;return {found,unchanged:before===JSON.stringify(G)};
};'''
with sync_playwright() as w:
 browser=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=browser.new_page(viewport={'width':1280,'height':720});p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');p.evaluate("__townTest.reset('settlement',42)");p.evaluate('__transitProbe.setup()');p.evaluate('__transitProbe.rail()');p.evaluate('__townTest.step(3)');p.evaluate('__townTest.capture({zoom:1.15})');r=p.evaluate('__bridgeAudit()');print(r);assert r['found'] and r['unchanged'],r
 for name,data in p.evaluate('__bridgeImages').items():(out/('bridge-'+name+'.png')).write_bytes(base64.b64decode(data.split(',')[1]))
 browser.close()
r['source_sha256']=hashlib.sha256(source.encode()).hexdigest();(out/'bridge-checks.json').write_text(json.dumps(r,indent=2)+'\n')
