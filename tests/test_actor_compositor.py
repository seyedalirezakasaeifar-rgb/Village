"""Compare damaged-region compositing against a complete single-pass scene redraw."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib,os
source=(ROOT/'assets/game.js').read_text();out=ROOT/'docs/previews/render-precision-audit'/os.getenv('AUDIT_CASE','default');out.mkdir(parents=True,exist_ok=True)
probe=r'''window.__composeAudit=()=>{
 const item=displayItems.find(a=>a.b?.kind==='home');__townTest.capture({x:item.x,y:item.y,zoom:1.15});const before=JSON.stringify(G),actor={kind:'vehicle',v:{id:12000,style:'truck',color:'#ce9b56'},x:item.x+35,y:item.y-1,dx:1,dy:.5};
 const actors=[actor],make=()=>{const c=document.createElement('canvas');c.width=cv.width;c.height=cv.height;const g=c.getContext('2d');g.imageSmoothingEnabled=false;return{c,g};},reference=make(),old=make(),fixed=make();
 const ground=g=>{drawWaterLife(g,()=>true);drawWaterfrontPiers(g,()=>true);drawRegionalGates(g,()=>true);drawTransitInfrastructure(g,()=>true);};
 reference.g.drawImage(viewUnderlayRaster,0,0);mapPaintTransform(reference.g);ground(reference.g);for(const a of [...viewBuildings,...actors].sort((a,b)=>a.y-b.y))paintSceneLayer(reference.g,a);
 for(const o of [old,fixed]){o.g.drawImage(viewRaster,0,0);mapPaintTransform(o.g);ground(o.g);}
 old.g.save();old.g.beginPath();old.g.rect(actor.x-25,actor.y-32,56,52);old.g.clip();for(const a of [...actors,...viewBuildings.filter(a=>a.y>=actor.y&&Math.abs(a.x-actor.x)<112&&a.y-actor.y<220)].sort((a,b)=>a.y-b.y))paintSceneLayer(old.g,a);old.g.restore();
 paintSceneActors(fixed.g,actors,()=>true);
 const r=scenePaintBounds(actor),x=Math.max(0,Math.floor(((r[0]-cam.x)*cam.zoom+cw/2)*dpr)),y=Math.max(0,Math.floor(((r[1]-cam.y)*cam.zoom+ch/2)*dpr)),w=Math.min(cv.width-x,Math.ceil((r[2]-r[0])*cam.zoom*dpr)),h=Math.min(cv.height-y,Math.ceil((r[3]-r[1])*cam.zoom*dpr)),expected=reference.g.getImageData(x,y,w,h).data;
 const compare=g=>{const a=g.getImageData(x,y,w,h).data;let channels=0,max=0;for(let i=0;i<a.length;i++){const d=Math.abs(a[i]-expected[i]);if(d>2)channels++;max=Math.max(max,d);}return{channels,max};};
 const result={old:compare(old.g),fixed:compare(fixed.g),unchanged:before===JSON.stringify(G),underlayBytes:viewUnderlayRaster.width*viewUnderlayRaster.height*4};window.__composeImages={old:old.c.toDataURL(),fixed:fixed.c.toDataURL(),reference:reference.c.toDataURL()};return result;
};'''
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':int(os.getenv('AUDIT_WIDTH','1280')),'height':int(os.getenv('AUDIT_HEIGHT','720'))},device_scale_factor=float(os.getenv('AUDIT_DPR','1')));errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');p.evaluate("__townTest.reset('settlement',42)");r=p.evaluate('__composeAudit()');print(r);assert r['unchanged'] and r['old']['channels']>100 and r['fixed']['channels']==0,r
 import base64
 for name,data in p.evaluate('__composeImages').items():(out/(name+'.png')).write_bytes(base64.b64decode(data.split(',')[1]))
 assert p.locator('#pause svg').count()==1 and p.locator('#pause').get_attribute('aria-label')=='Resume simulation';p.locator('#pause').click();assert p.locator('#pause svg path').get_attribute('d')=='M6 4H10V20H6ZM14 4H18V20H14Z';p.locator('#pause').screenshot(path=str(out/'pause-icon.png'));p.locator('#pause').click();assert not errors,errors;b.close()
r.update(source_sha256=hashlib.sha256(source.encode()).hexdigest(),errors=errors);(out/'compositor-checks.json').write_text(json.dumps(r,indent=2)+'\n')
