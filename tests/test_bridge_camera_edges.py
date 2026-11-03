"""A paid bridge remains admitted at all viewport edges across 36 camera cases."""
import ast,hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text()
tree=ast.parse((ROOT/'tests/test_road_bridge_art.py').read_text())
fixture=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe=r'''window.__bridgeEdgeCase=(zoom,edge,overlap)=>{const item=bridgeArtItems(()=>true)[0],r=item.bounds;cam={x:item.x,y:item.y,zoom};if(edge==='left')cam.x=r[2]-overlap+cw/(2*zoom);if(edge==='right')cam.x=r[0]+overlap-cw/(2*zoom);if(edge==='top')cam.y=r[3]-overlap+ch/(2*zoom);if(edge==='bottom')cam.y=r[1]+overlap-ch/(2*zoom);dirty=true;draw();const sx=cam.x-cw/(2*zoom),sy=cam.y-ch/(2*zoom),intersects=sceneIntersectsView(item,sx,sy,cw/zoom,ch/zoom),admitted=viewBuildings.some(a=>a.kind==='roadBridge');const before=cv.toDataURL();viewRasterKey='';viewBackgroundKey='';staticDirty=true;dirty=true;draw();return {zoom,edge,overlap,intersects,admitted,coldStable:before===cv.toDataURL()};};window.__bridgeEdgeState=()=>JSON.stringify(G);'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__bridgeArtTest.setup()');before=p.evaluate('__bridgeEdgeState()')
 rows=[p.evaluate('a=>__bridgeEdgeCase(...a)',[zoom,edge,overlap]) for zoom in [1.6,.88,.32] for edge in ['left','right','top','bottom'] for overlap in [1,8,24]];after=p.evaluate('__bridgeEdgeState()');b.close()
result={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':rows,'modelUnchanged':before==after};print(json.dumps(result,indent=2),flush=True)
assert before==after and all(r['intersects'] and r['admitted'] and r['coldStable'] for r in rows),[r for r in rows if not(r['intersects'] and r['admitted'] and r['coldStable'])]
print('PASS 36 bridge viewport-edge admissions, paused cold redraws and unchanged model')
