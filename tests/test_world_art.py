"""Visual-only freight continuity, LOD short-circuit and deterministic rendering."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json,time
out=ROOT/'reports/visual-world';out.mkdir(parents=True,exist_ok=True)
source=(ROOT/'assets/game.js').read_text()
probe='''window.__worldArtProbe=()=>{
 const before=JSON.stringify(G),saved={day:G.day,acc,zoom:cam.zoom};
 const path=[roadId(18,0),roadId(18,1),roadId(18,2),roadId(19,2),roadId(20,2)];
 const o={id:1,market:'upland',direction:'import',path,started:G.day,travelDays:10,good:'food'};
 const points=[];for(let t=0;t<10;t+=.001){G.day=saved.day+Math.floor(t);acc=(t%1)*1.65;points.push(shipmentVisualPose(o));}
 G.day=saved.day;acc=saved.acc;
 const jumps=points.slice(1).map((p,i)=>Math.hypot(p.x-points[i].x,p.y-points[i].y));
 let poseCalls=0;const base=shipmentVisualPose;shipmentVisualPose=(o)=>{poseCalls++;return base(o)};
 cam.zoom=.2;const hidden=regionalCargoActors();shipmentVisualPose=base;cam.zoom=saved.zoom;
 dirty=true;draw();const one=cv.toDataURL();dirty=true;draw();const two=cv.toDataURL();
 return {maxJump:Math.max(...jumps),hidden:hidden.length,poseCalls,unchanged:before===JSON.stringify(G),pausedStable:one===two,atlasBytes,atlasSize:atlas.size};
};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':1100,'height':720});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'// SOURCE: 99-instrumentation.js'))
 p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42)");p.locator('#panelClose').click()
 result=p.evaluate('__worldArtProbe()');assert result['maxJump']<.2,result
 assert result['hidden']==0 and result['poseCalls']==0 and result['unchanged'] and result['pausedStable'],result
 assert result['atlasBytes']<=48*1024*1024 and result['atlasSize']<=600,result
 result['renderBenchMs']={}
 for name,zoom in [('far',.25),('town',.75),('close',1.3)]:
  p.evaluate('(z)=>__townTest.capture({zoom:z})',zoom);p.locator('#view').screenshot(path=str(out/(name+'.png')));result['renderBenchMs'][name]=p.evaluate('__townTest.renderBench(100)')
 assert not errors,errors
 result.update(source_sha256=hashlib.sha256(source.encode()).hexdigest(),errors=errors)
 (out/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(result);b.close()
