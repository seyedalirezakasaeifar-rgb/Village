"""Viewport repair remains deterministic across pan, night and LOD transitions."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,json,hashlib
fixture=next(ast.literal_eval(n.value) for n in ast.parse((ROOT/'tests/test_transit_network.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='probe' for x in n.targets))
source=(ROOT/'assets/game.js').read_text();out=ROOT/'docs/previews/render-precision-audit'
probe=r'''window.__cameraAudit=()=>{
 const before=JSON.stringify(G),origin={...cam},checks=[];
 for(const zoom of [1.4,.6,.4,.2,1.1])for(const night of [false,true]){
  __townTest.capture({zoom,night,x:origin.x+80*(1-zoom),y:origin.y+30});
  const first=cv.toDataURL();dirty=true;draw();const stable=first===cv.toDataURL();
  checks.push({zoom,night,stable,bytes:viewUnderlayRaster.width*viewUnderlayRaster.height*4,repairBytes:actorRepairRaster.width*actorRepairRaster.height*4,viewportBytes:cv.width*cv.height*4});
 }
 return {checks,unchanged:before===JSON.stringify(G)};
};'''
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');p.evaluate("__townTest.reset('settlement',42)");p.evaluate('__transitProbe.setup()');p.evaluate('__transitProbe.rail()');p.evaluate('__townTest.step(3)');r=p.evaluate('__cameraAudit()');assert r['unchanged'] and all(c['stable'] and c['bytes']<=c['viewportBytes'] and c['repairBytes']<=c['viewportBytes'] and (c['zoom']!=.2 or c['bytes']==c['repairBytes']==0) for c in r['checks']),r
 for name,opts in [('mobile-day',{'zoom':1.1,'night':False}),('mobile-night',{'zoom':1.1,'night':True}),('mobile-far',{'zoom':.2,'night':False})]:
  p.evaluate('(o)=>__townTest.capture(o)',opts);p.locator('#view').screenshot(path=str(out/(name+'.png')))
 assert not errors,errors;b.close()
r.update(source_sha256=hashlib.sha256(source.encode()).hexdigest(),errors=errors);(out/'camera-checks.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
