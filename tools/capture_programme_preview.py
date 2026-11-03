"""Capture actual authored browser scenes; sampled visual phases keep economics paused."""
from pathlib import Path
import sys,io,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
from PIL import Image
source=(ROOT/'assets/game.js').read_bytes();out=ROOT/'docs/previews/council-programme';out.mkdir(parents=True,exist_ok=True);frames=[]
script=source.decode().replace('// SOURCE: 99-instrumentation.js','''window.__sceneFocus=(kind)=>{closePanel();gameOptions.quality='high';gameOptions.effects=true;gameOptions.decor=true;cam.zoom=1.7;const a=workdayScenes(displayItems).find(a=>a.scene===kind);if(!a)throw Error('Scene absent '+kind);cam.x=a.x;cam.y=a.y;dirty=true;draw();return a.b.id;};window.__scenePhase=phase=>{frameClock=phase;dirty=true;draw();}; // SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390},device_scale_factor=2);p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("settlement",42);__townTest.step(90)');p.locator('[data-panel=agenda]').click();p.locator('[data-panel=overview]').click();p.wait_for_timeout(3500);p.screenshot(path=str(out/'programme-landscape.png'))
 p.locator('[data-panel=agenda]').click();p.locator('.programme-chart').scroll_into_view_if_needed();p.screenshot(path=str(out/'programme-trend.png'))
 for kind in ['machinery','harvest','care','teaching']:
  p.evaluate('k=>__sceneFocus(k)',kind);p.evaluate('__scenePhase(3.5)');data=p.locator('canvas').first.screenshot();Image.open(io.BytesIO(data)).convert('RGB').save(out/(kind+'-detail.png'))
 p.evaluate('__sceneFocus("machinery")')
 for n in range(24):
  p.evaluate('t=>__scenePhase(t)',n*.12);im=Image.open(io.BytesIO(p.locator('canvas').first.screenshot())).convert('RGB');frames.append(im.resize((844,im.height//2)))
 frames[0].save(out/'working-machinery.webp',save_all=True,append_images=frames[1:],duration=120,loop=0,lossless=True,method=4);b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==hashlib.sha256(source).hexdigest()
(out/'provenance.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source).hexdigest(),'viewport':[844,390],'density':2,'scenario':'settlement','seed':42,'day':91,'animation':'24 explicitly sampled visual phases, 120ms apart; economy paused','runtime':'Chromium host browser; not Android'},indent=2)+'\n')
print('Captured programmes and four real operating scenes with source provenance')
