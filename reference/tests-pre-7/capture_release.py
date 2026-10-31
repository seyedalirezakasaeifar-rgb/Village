"""Actual renderer captures and input/viewport checks for the release."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os,json,time
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/final'
OUT.mkdir(exist_ok=True)
errors=[];checks={}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files'])
 page=b.new_page(viewport={'width':1280,'height':720})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((ROOT/'assets/index.html').as_uri())
 page.locator('#townSeed').fill('42')
 page.screenshot(path=str(OUT/'title-desktop.png'))
 page.locator('#newTown').click();page.locator('#panelClose').click();page.locator('#pause').click()
 page.evaluate('__townTest.capture({zoom:1.20})')
 page.screenshot(path=str(OUT/'village-desktop.png'))
 for month,name in [(1,'spring'),(4,'summer'),(7,'autumn'),(10,'winter')]:
  page.evaluate('(month)=>__townTest.capture({month,zoom:1.05})',month)
  page.screenshot(path=str(OUT/('village-'+name+'.png')))
 page.evaluate('__townTest.capture({month:4,night:true,zoom:1.20})')
 page.screenshot(path=str(OUT/'village-evening.png'))
 page.evaluate('__townTest.capture({night:false,month:1})')
 page.locator('[data-panel=policies]').click()
 page.locator('[data-cabinet=housing]').click()
 page.locator('#enactPolicy').click()
 page.locator('#panelClose').click()
 page.evaluate('__townTest.step(190)')
 page.locator('[data-panel=economy]').click()
 assert 'PROPERTY & CAPITAL' in page.locator('#panelBody').inner_text()
 assert '180-DAY REVIEW' in page.locator('#panelBody').inner_text()
 page.screenshot(path=str(OUT/'economy-desktop.png'))
 page.locator('#panelClose').click()
 page.locator('[data-panel=settings]').click()
 assert '6.0.0' in page.locator('#panelBody').inner_text()
 assert 'SESSION DIAGNOSTICS' in page.locator('#panelBody').inner_text().upper()
 page.screenshot(path=str(OUT/'settings-desktop.png'))
 page.locator('#panelClose').click()
 # Use genuine autonomously developed state from the same release test, if ready.
 saved=OUT/'regional-endurance-town.json'
 if saved.exists():assert page.evaluate('(s)=>__townTest.load(s)',saved.read_text())
 else:page.evaluate("__townTest.reset('regional',42);__townTest.step(1080)")
 g=page.evaluate('JSON.parse(__townTest.save())')
 assert g['airport'] and g['development']['towers']>0 and len(g['metro']['stations'])>=2
 checks['grownCity']={k:g['development'].get(k,0) for k in ['homes','firms','towers','airfields','stations']}
 checks['grownCity']['population']=g['stats']['population']
 page.evaluate("__townTest.capture({month:4,night:false,overlay:'none',zoom:.70})")
 page.screenshot(path=str(OUT/'city-desktop.png'))
 air=next(x for x in g['buildings'] if x['kind']=='airport')
 cells=g['airport']['runway']+air.get('footprint',[air['y']*56+air['x']])
 xs=[(i%56-i//56)*36+(56*72+140)/2 for i in cells]
 ys=[(i%56+i//56)*18+50 for i in cells]
 page.evaluate('(p)=>__townTest.capture(p)',{'x':(min(xs)+max(xs))/2,'y':(min(ys)+max(ys))/2,'zoom':1.30,'overlay':'none'})
 page.screenshot(path=str(OUT/'airfield-desktop.png'))
 # Native-sized browser view verifies layout, not Android hardware rendering.
 phone=b.new_page(viewport={'width':844,'height':390},device_scale_factor=1,has_touch=True,is_mobile=True)
 phone.on('pageerror',lambda e:errors.append(str(e)))
 phone.goto((ROOT/'assets/index.html').as_uri());phone.locator('#townSeed').fill('42')
 phone.screenshot(path=str(OUT/'title-phone.png'))
 for sel in ['#newTown','[data-scenario=regional]']:
  bb=phone.locator(sel).bounding_box();assert bb and bb['y']>=0 and bb['y']+bb['height']<=390,(sel,bb)
 phone.locator('#newTown').click();phone.locator('#panelClose').click()
 phone.screenshot(path=str(OUT/'village-phone.png'))
 for panel in ['overview','economy','agenda','policies','treasury','banking','community','businesses','citizens','construction','journal','settings']:
  phone.locator('[data-panel='+panel+']').click()
  text=phone.locator('#panelBody').inner_text()
  assert 'Panel error' not in text,(panel,text)
  panelbox=phone.locator('#panel').bounding_box();assert panelbox and panelbox['y']>=0 and panelbox['y']+panelbox['height']<=390
  phone.locator('#panelClose').click()
 checks['panels']=12
 phone.locator('[data-panel=policies]').click();phone.screenshot(path=str(OUT/'policy-phone.png'));phone.locator('#panelClose').click()
 # Actual 64x playback, with navigation while the simulation runs.
 before=phone.evaluate('__townTest.get().day');phone.locator('#speedRange').fill('6')
 start=time.perf_counter();phone.wait_for_timeout(4000)
 t=time.perf_counter();phone.locator('[data-panel=economy]').click();latency=(time.perf_counter()-t)*1000
 assert 'WHERE PEOPLE EARN THEIR LIVING' in phone.locator('#panelBody').inner_text().upper()
 after=phone.evaluate('__townTest.get().day')
 assert after>before+50,(before,after)
 assert phone.locator('#eventDialog').is_hidden()
 checks['highSpeed']={'requested':64,'days':after-before,'seconds':time.perf_counter()-start,'panelActionMs':latency,'modalFree':True}
 phone.locator('#pause').click();phone.screenshot(path=str(OUT/'economy-phone.png'))
 checks['desktopDrawMs']=page.evaluate('__townTest.renderBench(100)')
 checks['errors']=errors
 assert not errors,errors
 (OUT/'visual-ui-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
 print(json.dumps(checks,indent=2),flush=True)
 b.close()
