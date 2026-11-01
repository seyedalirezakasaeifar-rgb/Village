"""Bounded actual-UI public baseline. No step/reset/financial helper calls.
The funded archive is a preexisting generated QA trajectory, not an ordinary
human save. This journey itself uses live RAF and actual controls exclusively.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--commit',default='01eeda3d2ff09822b9422721f75e97fabbc9958a');args=ap.parse_args()
read=lambda path:subprocess.check_output(['git','show',args.commit+':'+path])
source=read('assets/game.js').decode();fixture_path='docs/previews/growth-journey/regional-42-planned.json.gz';fixture=gzip.decompress(read(fixture_path)).decode();probe=(ROOT/'tools/fixtures/realtime-player-journey-probe.js').read_text();out={'sourceCommit':args.commit,'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'fixturePath':fixture_path,'fixtureSha256':hashlib.sha256(fixture.encode()).hexdigest(),'injectedMoneyPeopleStockDrivers':False,'directSimulationCalls':False,'workerAcceptance':False,'completed':False,'actions':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1280,'height':800});p.set_default_timeout(12000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://localhost/**',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://localhost/realtime-player-journey');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'))
 def state():return p.evaluate('__playerJourney.state()')
 def save_wait():p.evaluate('__playerJourney.waitSaves()')
 def panel(tab):
  button=p.locator('[data-panel="'+tab+'"]').first
  opened='active' in (button.get_attribute('class')or'') and p.locator('#panel').evaluate('e=>e.classList.contains("show")')
  if opened and p.locator('#panelTitle').inner_text()!=p.evaluate('tab=>__playerJourney.title(tab)',tab):
   out.setdefault('stalePanelState',[]).append({'requested':tab,'active':state()['active'],'displayedTitle':p.locator('#panelTitle').inner_text()});button.click();opened=False
  if not opened:button.click()
 def reveal(target):
  while target.locator('xpath=ancestor::details[not(@open)]').count():target.locator('xpath=ancestor::details[not(@open)]').first.locator(':scope > summary').click()
  target.scroll_into_view_if_needed();return target
 def confirm(index=0):p.locator('#eventChoices button').nth(index).click()
 def log(name,before=None,extra=None):
  s=state();assert s['valid']['ok'] and s['goodsMax']<.01,(name,s['valid'],s['goodsMax']);out['actions'].append({'name':name,'day':s['day'],'treasury':s['treasury'],'construction':s['construction'],'total':s['total'],**(extra or {})});(ROOT/'reports/current-paid-worker-audit/realtime-baseline-journey.json').write_text(json.dumps(out,indent=2)+'\n');return s
 def close_panel():
  if p.locator('#panel').evaluate('e=>e.classList.contains("show")'):p.locator('#panelClose').click()
 def focus(x,y):p.evaluate('v=>__townTest.capture(v)',p.evaluate('v=>__playerJourney.world(v.x,v.y)',{'x':x,'y':y}))
 def point(x,y):
  r=p.evaluate('v=>__playerJourney.point(v.x,v.y)',{'x':x,'y':y});assert r['decoded']==[x,y],r;return {'x':r['x'],'y':r['y']}
 def place(kind,near=None):
  site=p.evaluate('v=>__playerJourney.site(v.kind,v.near)',{'kind':kind,'near':near});assert site,('No legal current site',kind);panel('construction');reveal(p.locator('[data-build-category="all"]').first).click();reveal(p.locator('[data-build="'+kind+'"]').first).click();focus(site['x'],site['y']);before=state();p.mouse.click(**point(site['x'],site['y']));p.keyboard.press('Escape');actual=p.evaluate('v=>__playerJourney.at(v.x,v.y)',site);assert actual and actual['kind']==kind and state()['construction']==before['construction']+1,(kind,actual,state()['toast']);log('construct:'+kind,extra={'site':actual});return actual
 def live(days,rate=8,during=None):
  start=state()['day'];p.locator('#speedRange').fill(str([1,2,4,8,16,32,64].index(rate)));p.locator('#speedRange').dispatch_event('change');p.locator('#pause').click();deadline=time.monotonic()+35;letters=0
  if during:during()
  while p.evaluate('__playerJourney.day()')<start+days:
   if p.locator('#eventDialog').is_visible():
    p.locator('#eventChoices button:not([disabled])').first.click();letters+=1
   if time.monotonic()>deadline:raise AssertionError('Live clock failed to progress through UI')
   p.wait_for_timeout(80)
  if p.locator('#eventDialog').is_visible():p.locator('#eventChoices button:not([disabled])').first.click();letters+=1
  p.locator('#pause').click();save_wait();stopped=state();p.wait_for_timeout(350);assert state()['day']==stopped['day'],'Paused clock advanced';log('clock:'+str(rate)+'x',extra={'startDay':start,'daysObserved':stopped['day']-start,'handledOrdinaryLetters':letters});return stopped
 p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();panel('settings');p.locator('#importSave').click();p.locator('#importText').fill(fixture);p.locator('#restoreGo').click();p.wait_for_function('document.getElementById("helpDialog").style.display==="none"');save_wait();opening=log('import:funded-trajectory');assert opening['day']==1081
 p.locator('#speed').click();log('clock:speed-button');live(2,8);panel('agenda');inbox=p.locator('[data-inbox]').first
 if inbox.count():inbox.click()
 else:p.locator('#convene').click()
 title=p.locator('#eventTitle').inner_text();confirm();log('council:actual-review',extra={'title':title});live(2,8,during=lambda:place('park'))
 parcel=p.evaluate('__playerJourney.parcel()');assert parcel;panel('construction');reveal(p.locator('[data-parcel-buy="'+parcel['id']+'"]').first).click();before=state();confirm();after=log('district:buy',extra={'parcel':parcel});assert len(after['owned'])==len(before['owned'])+1 and abs(before['treasury']-after['treasury']-parcel['price'])<.01
 focus_button=p.locator('[data-district-id="'+parcel['id']+'"][data-district-focus="neighbourhood"]');reveal(focus_button).click();confirm();assert state()['programmes'][parcel['id']]['focus']=='neighbourhood';log('district:charter')
 farm=p.evaluate('__playerJourney.farm()');assert farm;close_panel();focus(farm['x'],farm['y']);p.mouse.click(**point(farm['x'],farm['y']));plan=p.locator('[data-urban-plan="residential"][data-urban-building="'+str(farm['building'])+'"]')
 if not plan.is_disabled():reveal(plan).click();confirm();log('renewal:residential-plan')
 renew=p.locator('[data-urban-farm-renew="'+str(farm['id'])+'"]');reveal(renew).click();p.wait_for_timeout(100)
 if p.locator('#eventDialog').is_visible():
  text=p.locator('#eventText').inner_text();p.locator('#eventDefer').click();log('renewal:review-cancel',extra={'review':text})
 else:
  reason=state()['toast'];assert reason and not any(t in reason.lower()for t in ['unsupported','worker preview','unavailable in']);log('renewal:prerequisite-refusal',extra={'reason':reason})
 depot=place('transit_depot')
 def draft_bus(cancel=False):
  panel('construction');reveal(p.locator('[data-transit-action="new-bus"]')).click();p.locator('#transitLevel').select_option('2');p.locator('[data-transit-action="map"]').click();focus(27,27)
  for x in [15,27,35]:p.mouse.click(**point(x,27))
  panel('construction');reveal(p.locator('[data-transit-action="quote"]')).click();authorize=p.locator('[data-transit-action="build"]');assert authorize.count() and not authorize.is_disabled(),p.locator('#panelBody').inner_text()[-1800:]
  if cancel:p.locator('[data-transit-action="cancel"]').click()
  else:authorize.click()
 before=state();draft_bus(True);after=state();assert before['treasury']==after['treasury'] and before['transitCapital']==after['transitCapital'] and len(before['routes'])==len(after['routes']);log('transit:cancel-quoted-bus')
 draft_bus();route=state()['routes'][-1];log('transit:authorize-bus',extra={'route':route['id'],'depot':depot['id']});live(2,16);panel('construction');reveal(p.locator('[data-transit-level="'+str(route['id'])+':0"]')).click();assert next(r for r in state()['routes']if r['id']==route['id'])['level']==0;log('transit:suspend');reveal(p.locator('[data-transit-level="'+str(route['id'])+':1"]')).click();assert next(r for r in state()['routes']if r['id']==route['id'])['level']==1;log('transit:resume')
 station1=place('elevated_station');station2=place('elevated_station',station1);panel('construction');reveal(p.locator('[data-transit-action="new-elevated"]')).click();p.locator('[data-transit-action="map"]').click()
 for station in [station1,station2]:focus(station['x'],station['y']);p.mouse.click(**point(station['x'],station['y']))
 panel('construction');reveal(p.locator('[data-transit-action="quote"]')).click();p.locator('[data-transit-action="build"]').click();assert any(r['mode']=='elevated' for r in state()['routes']);log('transit:authorize-elevated')
 panel('economy');reveal(p.locator('[data-logistics-priority="essentials"]')).click();assert state()['priority']=='essentials';reveal(p.locator('#logisticsRelief')).click();confirm();assert state()['reliefUntil']>=state()['day']+29;log('freight:priority-and-paid-shift')
 offer=p.locator('[data-trade-offer]:not([disabled])').first;assert offer.count();reveal(offer).click();review=p.locator('#eventText').inner_text();prior=len(state()['contracts']);confirm();assert len(state()['contracts'])==prior+1;contract=state()['contracts'][-1];log('freight:agreement',extra={'contract':contract['id'],'review':review});live(5,16)
 panel('economy');cargo=p.locator('[data-regional-cargo]').first;assert cargo.count();cargoId=int(cargo.get_attribute('data-regional-cargo'));reveal(cargo).click();stale=None
 if 'regional freight' not in p.locator('#panelBody').inner_text().lower():
  stale={'id':cargoId,'authority':p.evaluate('id=>__playerJourney.cargo(id)',cargoId),'activePanel':state()['active'],'visibleText':p.locator('#panelBody').inner_text()[:300]};out['staleCargoPreview']=stale
  close_panel();panel('economy');cargo=p.locator('[data-regional-cargo]').first;assert cargo.count();reveal(cargo).click()
 assert 'regional freight' in p.locator('#panelBody').inner_text().lower(),{'stale':stale,'activePanel':state()['active'],'text':p.locator('#panelBody').inner_text()[:500]};log('freight:inspect-live-cargo',extra={'requiredManualRefresh':stale is not None})
 panel('construction');reveal(p.locator('[data-transit-action="retire"][data-route="'+str(route['id'])+'"]')).click();assert not any(r['id']==route['id']for r in state()['routes']);log('transit:retire-bus-retain-sites')
 panel('settings');p.locator('#nightView').click();p.locator('#nightView').click();sound=p.locator('#soundToggle').get_attribute('aria-pressed');p.locator('#soundToggle').click();assert p.locator('#soundToggle').get_attribute('aria-pressed')!=sound;p.locator('#soundToggle').click();log('settings:presentation-controls',extra={'audibleHardwareClaim':False});p.locator('#saveNow').click();save_wait();
 if not p.locator('#backupSave').count():out['missingBackup']={'active':state()['active'],'paused':state()['paused'],'text':p.locator('#panelBody').inner_text()[:1200],'errors':errors};log('settings:missing-backup');raise AssertionError(out['missingBackup'])
 p.locator('#backupSave').click();p.locator('#saveText').wait_for();exported=p.locator('#saveText').input_value();p.locator('#archiveClose').click();p.locator('#importSave').click();p.locator('#importText').fill(exported);p.locator('#restoreGo').click();p.wait_for_function('document.getElementById("helpDialog").style.display==="none"');save_wait();panel('settings');p.locator('#backupSave').click();again=p.locator('#saveText').input_value();rawEqual=json.loads(exported)==json.loads(again);out['rawArchiveRoundtripEqual']=rawEqual
 if not rawEqual:
  differences=[]
  def diff(a,b,path=''):
   if isinstance(a,dict)and isinstance(b,dict):
    for key in a.keys()|b.keys():
     if key not in a or key not in b:differences.append(path+'.'+key)
     else:diff(a[key],b[key],path+'.'+key)
   elif isinstance(a,list)and isinstance(b,list):
    if len(a)!=len(b):differences.append(path+'.length')
    for i,(x,y)in enumerate(zip(a,b)):diff(x,y,path+'['+str(i)+']')
   elif a!=b or isinstance(a,bool)!=isinstance(b,bool):differences.append(path)
  diff(json.loads(exported),json.loads(again));out['rawArchiveRoundtripDifferences']=differences[:100]
  for label,text in [('before-ui-import',exported),('after-ui-import',again)]:
   (ROOT/('reports/current-paid-worker-audit/realtime-'+label+'.json.gz')).write_bytes(gzip.compress(text.encode()))
 # Import displays Overview and may rebuild derived stats/authored preview state.
 # Compare with the ENTIRE independent original-source cold UI path, not a field filter.
 journeyPage=p;reference=b.new_page(viewport={'width':1280,'height':800});reference.on('pageerror',lambda e:errors.append(str(e)));reference.route('http://127.0.0.1/**',lambda r:r.fulfill(body=html,content_type='text/html'));reference.goto('http://127.0.0.1/realtime-cold-reference');reference.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p=reference;p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#speedRange').fill(str([1,2,4,8,16,32,64].index(json.loads(exported)['speed'])));panel('settings');p.locator('#importSave').click();p.locator('#importText').fill(exported);p.locator('#restoreGo').click();p.wait_for_function('document.getElementById("helpDialog").style.display==="none"');save_wait();panel('settings');p.locator('#backupSave').click();cold=p.locator('#saveText').input_value();assert json.loads(again)==json.loads(cold),'Whole cold original-UI oracle differs';out['fullColdUiOracleEqual']=True;p.close();p=journeyPage;p.locator('#archiveClose').click();final=log('save:full-ui-roundtrip');assert abs(final['total']-opening['total'])<.05;assert not errors,errors;out.update({'completed':True,'finalDay':final['day'],'daysElapsed':final['day']-opening['day'],'cashDrift':final['total']-opening['total'],'errors':errors,'audioHardwareClaim':False,'strictFreshViewAccepted':not bool(out.get('staleCargoPreview') or out.get('stalePanelState') or not out.get('rawArchiveRoundtripEqual'))});b.close()
(ROOT/'reports/current-paid-worker-audit/realtime-baseline-journey.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
