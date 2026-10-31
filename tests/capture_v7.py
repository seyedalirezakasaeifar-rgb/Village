from pathlib import Path
from playwright.sync_api import sync_playwright
import json
R=Path(__file__).resolve().parents[1];O=R/'reports/v7.0'
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox']);p=b.new_page(viewport={'width':1280,'height':800});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto((R/'assets/index.html').as_uri());p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42);__townTest.step(360);__townTest.capture({zoom:1.2})");p.locator('#panelClose').click();p.locator('#pause').click();p.wait_for_timeout(8000);p.locator('#pause').click();p.screenshot(path=str(O/'town.png'))
 p.set_viewport_size({'width':844,'height':390});p.wait_for_timeout(400)
 for tab in ['overview','economy','agenda','policies','treasury','banking','community','businesses','citizens','construction','journal','settings']:
  p.locator(f'[data-panel={tab}]').click();p.wait_for_timeout(40);assert 'Panel error' not in p.locator('#panelBody').inner_text();p.screenshot(path=str(O/f'panel-{tab}.png'))
 p.locator('[data-panel=banking]').click();p.locator('[data-open-monetary]').click();p.screenshot(path=str(O/'interest-policy-phone.png'));p.locator('#panelClose').click()
 p.set_viewport_size({'width':1280,'height':800});p.wait_for_timeout(400);p.evaluate("__townTest.reset('regional',42);__townTest.step(1800)");g=p.evaluate('JSON.parse(__townTest.save())');a=g.get('airport');print('Airport',a,flush=True)
 if a and a.get('firm') is not None:
  terminal=next(bb for bb in g['buildings'] if bb['id']==a['building']);x=(terminal['x']-terminal['y'])*36+(56*72+140)/2;y=(terminal['x']+terminal['y'])*18+100
  for phase,name in [(88,'parked'),(16,'takeoff'),(70,'landing')]:
   p.evaluate('(o)=>{const g=JSON.parse(__townTest.save());g.trafficState.clock=o.phase;__townTest.load(g);__townTest.capture({x:o.x,y:o.y,zoom:1.65});}',{'phase':phase,'x':x,'y':y});p.screenshot(path=str(O/f'airfield-{name}.png'))
 p.evaluate('__townTest.capture({zoom:.7})');p.screenshot(path=str(O/'regional-city.png'));assert not errors,errors;print('PASS captures, live panels and monetary navigation');b.close()
