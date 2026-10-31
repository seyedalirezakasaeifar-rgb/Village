import sys,ast,io,json,hashlib,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
from PIL import Image
fixture=next(ast.literal_eval(n.value) for n in ast.parse((ROOT/'tests/test_transit_network.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='probe' for x in n.targets))
src=(ROOT/'assets/game.js').read_text();out=ROOT.parent/'scratch/camera-matrix';out.mkdir(parents=True,exist_ok=True)
probe="window.__crossingView=()=>{frameClock=10.1;gameOptions.quality='high';const b=G.buildings.find(b=>b.kind==='fire'),p=iso(b.x,b.y);__townTest.capture({x:p[0]+60,y:p[1]-55,zoom:1.1});};"
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_content(html);p.add_script_tag(content=src.replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');p.evaluate("__townTest.reset('settlement',42)");p.evaluate('__transitProbe.setup()');p.evaluate('__transitProbe.rail()');p.evaluate('__townTest.step(3)');p.evaluate('__crossingView()');p.locator('#pause').click();frames=[];start=time.monotonic()
 for i in range(32):frames.append(Image.open(io.BytesIO(p.locator('#view').screenshot())).convert('RGB'));p.wait_for_timeout(60)
 elapsed=time.monotonic()-start;p.locator('#pause').click();frames[0].save(out/'bridge-crossing.gif',save_all=True,append_images=frames[1:],duration=round(elapsed/32*1000),loop=0);b.close()
(out/'bridge-motion.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.encode()).hexdigest(),'frames':32,'seconds':elapsed,'fixture':'Actual funded bus/rail service; initial visual frameClock selected at10.1, then ordinary unpaused game clock. No source edits or actor placement.'},indent=2)+'\n')
