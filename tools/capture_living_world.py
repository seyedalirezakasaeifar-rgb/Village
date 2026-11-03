"""Record a short unedited host-browser game session after an economic warmup."""
from pathlib import Path
import sys,io,json,hashlib,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
from PIL import Image
out=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'reports/art-direction');out.mkdir(parents=True,exist_ok=True)
night=len(sys.argv)>2 and sys.argv[2]=='night'
source=(ROOT/'assets/game.js').read_text();frames=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':844,'height':520});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42)");p.locator('#panelClose').click();p.evaluate('__townTest.step(20)');p.evaluate('(o)=>__townTest.capture(o)',{'zoom':1.15,'night':night});p.locator('#pause').click()
 started=time.monotonic()
 for i in range(40):
  frames.append(Image.open(io.BytesIO(p.locator('#view').screenshot())).convert('RGB'));p.wait_for_timeout(60)
 elapsed=time.monotonic()-started;p.locator('#pause').click();status=p.evaluate('__townTest.get()');assert not errors,errors
 p.locator('#view').screenshot(path=str(out/'living-city.png'));b.close()
frames[0].save(out/'living-city.gif',save_all=True,append_images=frames[1:],duration=round(elapsed/len(frames)*1000),loop=0,optimize=True)
(out/'living-session.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'capture':'Unedited host-Chromium game following20day economic warmup; soundtrack not recorded. GIF timing follows actual screenshot cadence; not an FPS benchmark.','night':night,'frames':len(frames),'elapsed_seconds':elapsed,'day':status['day'],'population':status['population'],'errors':errors},indent=2)+'\n');print({'frames':len(frames),'seconds':elapsed,'day':status['day'],'errors':errors})
