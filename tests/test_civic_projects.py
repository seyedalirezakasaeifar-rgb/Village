"""Concrete projects through paid controls, real geography and deterministic saves."""
from pathlib import Path
import functools,http.server,threading,json,hashlib,os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
OUT=ROOT/'reports/civic-projects';OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':844,'height':390},is_mobile=True,has_touch=True);page.set_default_timeout(8000)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:'+str(server.server_port)+'/assets/index.html');page.locator('#townSeed').fill('42');page.locator('#newTown').click();page.locator('#pause').click()
 state=lambda:page.evaluate('JSON.parse(__townTest.save())')
 openboard=lambda:page.evaluate("document.querySelector('[data-civic-projects]')?.click()")
 # Open from the actual desk, review and cancel before adopting.
 page.locator('[data-civic-projects]').click();assert state().get('civicProjects') is None
 page.locator('[data-civic-project-review=food]').click();page.keyboard.press('Shift+Tab');assert page.evaluate("document.activeElement.id==='eventDefer'")
 page.keyboard.press('Tab');assert page.evaluate("document.activeElement.dataset.eventChoice==='0'")
 page.keyboard.press('Escape');assert state().get('civicProjects') is None
 page.locator('[data-civic-project-review=food]').click();page.locator('[data-event-choice="0"]').click()
 initial=state();total=page.evaluate('__townTest.get().total');assert not initial['regionalTrade']['shipments']
 page.locator('[data-civic-project-order]').click();page.keyboard.press('Escape');assert not state()['regionalTrade']['shipments']
 page.locator('[data-civic-project-order]').click();page.locator('[data-event-choice="0"]').click()
 ordered=state();ids=ordered['civicProjects']['active']['food']['orders'];assert ids
 qty=sum(o['qty'] for o in ordered['regionalTrade']['shipments'] if o['id'] in ids);assert abs(qty-180)<.001
 assert ordered['treasury']==initial['treasury'];assert abs(page.evaluate('__townTest.get().total')-total)<.0001
 serial=ordered['regionalTrade']['serial'];page.locator('[data-civic-project-order]').click();assert state()['regionalTrade']['serial']==serial,'Repeated control duplicated paid food'
 page.evaluate('__townTest.step(12)');food=state()['civicProjects']['active']['food'];assert food['status']=='complete' and abs(food['arrived']-180)<.001,food
 assert not food['orders'];assert page.evaluate('__townTest.validate().ok')
 # Existing completed certificate is retained while a district becomes the next concrete choice.
 page.locator('[data-panel=overview]').click();page.locator('[data-civic-projects]').click()
 page.locator('[data-civic-project-review=district]').click();assert page.locator('#projectFocus option[value=waterfront]').evaluate('e=>e.disabled');page.locator('#projectParcel').select_option('river-reach');assert page.locator('#projectFocus option[value=waterfront]').evaluate('e=>!e.disabled');page.locator('#projectParcel').select_option('county-ridge');page.locator('#projectFocus').select_option('industry')
 assert page.evaluate('__townArchive.back()');assert page.locator('#projectParcel').count()==0
 assert 'district' not in state()['civicProjects']['active']
 page.locator('[data-civic-project-review=district]').click();page.locator('#projectParcel').select_option('county-ridge');page.locator('#projectFocus').select_option('industry');page.locator('#projectDistrictAdopt').click()
 assert page.locator('#projectParcel').count()==0
 page.locator('[data-civic-project-deed]').click();page.keyboard.press('Escape');assert not state()['charter']['owned']
 before_deed=state();page.locator('[data-civic-project-deed]').click();page.locator('[data-event-choice="0"]').click();after_deed=state()
 assert 'county-ridge' in after_deed['charter']['owned'];deed=after_deed['charter']['deeds'][0]
 assert abs(before_deed['treasury']-after_deed['treasury']-deed['price'])<.001
 assert page.locator('[data-civic-project-charter]').is_visible()
 page.locator('[data-civic-project-charter]').click();page.locator('[data-event-choice="0"]').click()
 assert state()['districtProgrammes']['county-ridge']['focus']=='industry'
 assert page.locator('[data-civic-project-road]').count()==1
 before_road=state();page.locator('[data-civic-project-road]').click();assert page.locator('.civic-blueprint-layout').count()==1
 page.screenshot(path=str(OUT/'landscape-gateway-survey.png'))
 page.keyboard.press('Escape');assert page.locator('.civic-project-survey').count()==0;assert state()['treasury']==before_road['treasury']
 page.locator('[data-civic-project-road]').click();page.locator('[data-event-choice="0"]').click();after_road=state()
 added=sum(x==1 for x in after_road['tiles'])-sum(x==1 for x in before_road['tiles']);assert added>0
 assert abs(before_road['treasury']-after_road['treasury']-added*150)<.001
 assert all(a==b or a in [0,3] and b==1 for a,b in zip(before_road['tiles'],after_road['tiles']))
 # Commission a visible named factory using the normal construction transaction.
 before_factory=state();page.locator('[data-civic-project-build=factory]').click();assert page.locator('.civic-blueprint-layout').count()==1
 page.keyboard.press('Escape');assert state()['treasury']==before_factory['treasury']
 page.locator('[data-civic-project-build=factory]').click();page.locator('[data-event-choice="0"]').click();factory_state=state()
 factories=[f for f in factory_state['firms'] if f['kind']=='factory'];assert len(factories)>len([f for f in before_factory['firms'] if f['kind']=='factory'])
 assert abs(before_factory['treasury']-factory_state['treasury']-9800+factory_state['policy']['permitFee'])<.001
 assert page.locator('[data-civic-project-build=factory]').count()==0,'Project must inspect an existing pilot instead of recommending duplicate factories'
 assert page.locator('[data-firm="'+str(factories[-1]['id'])+'"]').count()>0
 page.screenshot(path=str(OUT/'landscape-working-project.png'))
 # Skills compete for recurring funds: drafting does not enact or spend anything.
 page.locator('[data-civic-project-review=skills]').click();page.locator('[data-event-choice="0"]').click()
 before_budget=state();page.locator('[data-civic-project-budget]').click();page.locator('[data-event-choice="0"]').click()
 assert state()['policy']['educationBudget']==before_budget['policy']['educationBudget']
 assert state()['treasury']==before_budget['treasury'];assert page.locator('[data-policy=educationBudget]').is_visible()
 page.locator('#enactPolicy').click();assert state()['policy']['educationBudget']>before_budget['policy']['educationBudget']
 # Exact replay covers paid cargo, commissioned works and project observations.
 checkpoint=page.evaluate('__townTest.save()');page.evaluate('__townTest.step(15)');expected=state()
 assert page.evaluate('(s)=>__townTest.load(s)',checkpoint);page.evaluate('__townTest.step(15)');actual=state()
 for k in ['day','treasury','civicProjects','districtProgrammes']:assert expected[k]==actual[k],k
 assert page.evaluate('__townTest.validate().ok')
 # Recoverable withdrawal/cancel and decline/restore change records, not owned assets.
 page.locator('[data-panel=overview]').click();page.locator('[data-civic-projects]').click()
 project=page.locator('[data-project-card=skills]');project.locator('summary').click();project.locator('[data-civic-project-withdraw=skills]').click();page.keyboard.press('Escape');assert 'skills' in state()['civicProjects']['active']
 project.locator('[data-civic-project-withdraw=skills]').click();page.locator('[data-event-choice="0"]').click();withdrawn=state();assert 'skills' not in withdrawn['civicProjects']['active'];assert withdrawn['charter']['owned']==actual['charter']['owned'];assert len(withdrawn['buildings'])==len(actual['buildings'])
 page.locator('[data-civic-project-decline=skills]').click();assert 'skills' in state()['civicProjects']['declined']
 page.locator('[data-civic-project-restore]').click();assert not state()['civicProjects']['declined']
 # Corruption must be rejected before changing town; optional legacy absence is accepted.
 valid=state()
 for patch in [{'serial':-1},{'declined':['food','food']},{'active':{'bad':valid['civicProjects']['active']['food']}},{'lastDay':valid['day']+1}]:
  bad=json.loads(json.dumps(valid));bad['civicProjects'].update(patch);assert not page.evaluate('(s)=>__townTest.load(JSON.stringify(s))',bad);assert state()['civicProjects']==valid['civicProjects']
 page.set_viewport_size({'width':390,'height':844});page.locator('#panelBody').evaluate('e=>e.scrollTop=0');page.screenshot(path=str(OUT/'portrait-project-board.png'))
 assert page.locator('#panelBody').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
 legacy=state();legacy.pop('civicProjects',None);assert page.evaluate('(s)=>__townTest.load(JSON.stringify(s))',legacy);assert state().get('civicProjects') is None
 assert not errors,errors
 receipt={'source_sha256':hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest(),'realControls':True,'paidFoodUnits':qty,'foodCertificate':food,'districtDeedPrice':deed['price'],'newRoadTiles':added,'newRoadCost':added*150,'factoryMunicipalSiteCost':9800,'draftedTeachingThenEnacted':actual['policy']['educationBudget'],'exactReplayDays':15,'invalidArchiveCases':4,'errors':errors,'limits':'Simulated browser playthrough; later district establishment and full adult term tested separately, not claimed here.'}
 (OUT/'journey.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('PASS commissioned food delivery/certificate, repeat guard, district adoption/deed/charter, surveyed paid roads, named factory, recurring teaching draft/enact, exact replay, withdrawal/cancel, modal keyboard containment and legacy/corrupt archives',flush=True)
 b.close()
server.shutdown()
