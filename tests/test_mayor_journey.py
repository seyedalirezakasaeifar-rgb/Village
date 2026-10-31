"""Real control journey, archive validation and deterministic observed progression.
Runs through localhost because managed Chromium disables file: navigation.
"""
from pathlib import Path
import functools, http.server, json, threading, os, hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
OUT=ROOT/'reports/player-experience';OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':844,'height':390},is_mobile=True,has_touch=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:'+str(server.server_port)+'/assets/index.html')
 page.locator('#townSeed').fill('42');page.locator('#newTown').click();page.locator('#pause').click()
 state=lambda:page.evaluate('JSON.parse(__townTest.save())')
 initial=state();total=page.evaluate('__townTest.get().total')
 assert 'Awaiting the first daily settlement' in page.locator('.mayor-desk').inner_text()
 # Rendering and expanding informational content cannot mutate the economy or journey.
 page.locator('.mayor-pressure-grid summary').first.click()
 page.screenshot(path=str(OUT/'landscape-first-session.png'))
 assert state().get('mayorJourney') is None
 page.locator('[data-mayor-agenda]').click()
 page.locator('[data-mayor-direction=exchange]').click()
 assert page.locator('#eventDefer').inner_text()=='CANCEL'
 page.keyboard.press('Escape');assert page.locator('#eventDialog').is_hidden()
 assert state().get('mayorJourney') is None,'Cancel must not choose a direction'
 page.locator('[data-mayor-direction=exchange]').click();page.locator('[data-event-choice="0"]').click()
 assert state()['mayorJourney']['direction']=='exchange'
 assert page.evaluate('__townTest.get().total')==total
 assert state()['treasury']==initial['treasury']
 page.locator('[data-mayor-baseline]').click();baseline=state()['mayorJourney']['review']
 page.locator('[data-mayor-baseline]').click();page.keyboard.press('Escape')
 assert state()['mayorJourney']['review']==baseline
 # Actual paid order: Cancel, reopen, confirm once, then follow arrival.
 page.locator('[data-panel=overview]').click();page.locator('#firstFoodOrder').click()
 page.keyboard.press('Escape');assert not state()['regionalTrade']['shipments']
 page.locator('#firstFoodOrder').click();page.locator('[data-event-choice="0"]').click()
 ordered=state();assert ordered['regionalTrade']['shipments']
 assert ordered['treasury']==initial['treasury']
 assert page.evaluate('__townTest.get().total')==total
 assert sum(f['cash'] for f in ordered['firms'])<sum(f['cash'] for f in initial['firms'])
 page.evaluate('__townTest.step(12)');arrived=state()
 assert arrived['regionalTrade']['delivered']>0
 assert arrived['mayorJourney']['stage']>=1
 assert arrived['mayorJourney']['completed'][0]['day']>1
 # Exact next-day determinism, preserving earned stages and guide preferences.
 checkpoint=page.evaluate('__townTest.save()')
 page.evaluate('__townTest.step(5)');a=state()
 assert page.evaluate('(s)=>__townTest.load(s)',checkpoint)
 page.evaluate('__townTest.step(5)');c=state()
 for key in ['day','treasury','regionalTrade','mayorJourney']:
  assert a[key]==c[key],key
 # A genuinely paid export commitment can be kept after the inbound buffer.
 page.locator('[data-panel=economy]').click()
 page.locator('[data-trade-offer]:not([disabled])').first.click()
 before_contract=state();page.locator('[data-event-choice="0"]').click()
 assert state()['treasury']==before_contract['treasury']
 page.evaluate('__townTest.step(32)')
 assert state()['regionalTrade']['contracts'][0]['status']=='fulfilled'
 assert state()['mayorJourney']['stage']==2
 assert page.evaluate('__townTest.validate().ok')
 # Legacy archives migrate lazily without claiming earlier deeds or deliveries.
 legacy=state();legacy.pop('mayorJourney',None)
 assert page.evaluate('(s)=>__townTest.load(JSON.stringify(s))',legacy)
 assert state().get('mayorJourney') is None
 page.evaluate('__townTest.step(1)');assert state()['mayorJourney']['direction']==''
 # Corrupt progression is rejected atomically, preserving current town.
 valid=state();before=page.evaluate('__townTest.save()')
 for mut in [dict(stage=99),dict(direction='unknown'),dict(held=-1),dict(visited=['invented']),dict(completed=[{'stage':0,'day':1}])]:
  bad=json.loads(json.dumps(valid));bad['mayorJourney'].update(mut)
  assert not page.evaluate('(s)=>__townTest.load(JSON.stringify(s))',bad),mut
  assert page.evaluate('__townTest.get().day')==valid['day']
 # Visible direction choices and actual navigations; persistent guide toggle.
 page.locator('[data-panel=agenda]').click();page.locator('[data-panel=overview]').click();page.locator('[data-mayor-guide=hide]').click()
 assert not state()['mayorJourney']['guide']
 page.locator('[data-mayor-guide=show]').click();assert state()['mayorJourney']['guide']
 page.locator('[data-mayor-panel=economy]').first.click();assert page.locator('#panelTitle').inner_text()=='The Living Economy'
 assert 'economy' in state()['mayorJourney']['visited']
 page.locator('[data-panel=agenda]').click();page.locator('[data-mayor-direction=river]').click();page.locator('[data-event-choice="0"]').click()
 assert state()['mayorJourney']['direction']=='river'
 assert state()['mayorJourney']['stage']==0
 assert 'Care within reach' not in page.locator('.mayor-desk').inner_text()
 page.screenshot(path=str(OUT/'landscape-river-direction.png'))
 # Portrait report wraps within the panel and controls remain reachable.
 page.set_viewport_size({'width':390,'height':844})
 page.locator('[data-panel=overview]').click();page.locator('[data-mayor-agenda]').click()
 page.get_by_text('Compare another direction',exact=True).click();page.locator('[data-mayor-direction=community]').click();page.locator('#eventDefer').click()
 assert state()['mayorJourney']['direction']=='river'
 assert page.locator('#panelBody').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
 page.locator('#panelBody').evaluate('e=>e.scrollTop=0');page.screenshot(path=str(OUT/'portrait-direction.png'))
 assert not errors,errors
 receipt={'source_sha256':hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest(),'seed':42,'viewportChecks':[[844,390],[390,844]],'firstDeliveryDay':arrived['mayorJourney']['completed'][0]['day'],'agreementStatus':'fulfilled','earnedStagesBeforeMigration':2,'exactReplayDays':5,'invalidArchiveCases':5,'errors':errors,'realControls':True,'note':'Simulated days and actual browser controls; no claim of a multi-hour human play session or device certification.'}
 (OUT/'journey.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('PASS real paid import / arrival / fulfilled export agreement / two earned stages, Cancel and Escape, no free money, exact 5-day replay, legacy migration, atomic corruption rejection, persistent guide, landscape and portrait controls')
 b.close()
server.shutdown()
