from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();probe='window.__followPlan=()=>districtFollowthroughPlan(G.civicProjects.active.district);'
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);results={};errors=[]
 def fresh():
  p=b.new_page(viewport={'width':844,'height':390});p.set_default_timeout(10000);p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();return p
 p=fresh()
 def state():return p.evaluate('JSON.parse(__townTest.save())')
 def panel(tab):
  p.keyboard.press('Escape')
  if not(p.locator('#panel').evaluate('e=>e.classList.contains("show")')and'active'in(p.locator('[data-panel='+tab+']').get_attribute('class')or'')):p.locator('[data-panel='+tab+']').click()
 def board():panel('overview');p.locator('[data-civic-projects]').click()
 def confirm():p.locator('[data-event-choice="0"]').click()
 def district(parcel,focus):
  board();p.locator('[data-civic-project-review=district]').click();p.locator('#projectParcel').select_option(parcel);p.locator('#projectFocus').select_option(focus);p.locator('#projectDistrictAdopt').click();p.locator('[data-civic-project-deed]').click();confirm();p.locator('[data-civic-project-charter]').click();confirm();p.locator('[data-civic-project-road]').click();confirm()
 panel('agenda');button=p.locator('[data-mayor-direction=river]');button.evaluate('e=>e.closest("details").open=true');button.click();confirm();p.evaluate('__townTest.step(31)');assert state()['mayorJourney']['stage']==0,'Existing fishery/wharf must not earn newly chosen direction stages';baseline=state()['mayorJourney']['baseline'];assert baseline['firms']
 district('river-reach','waterfront');p.locator('[data-civic-project-build=fishery]').click();confirm();p.evaluate('__townTest.step(2)');assert state()['mayorJourney']['stage']==1
 board();p.locator('[data-civic-project-build=wharf]').click();confirm();p.evaluate('__townTest.step(2)');assert state()['mayorJourney']['stage']==2;results['newWorkJourney']=state()['mayorJourney']
 saved=p.evaluate('__townTest.save()');assert p.evaluate('s=>__townTest.load(s)',saved);assert p.evaluate('()=>{let g=JSON.parse(__townTest.save());g.mayorJourney.baseline.firms.push(-1);return !__townTest.load(JSON.stringify(g));}')
 assert p.evaluate('()=>{let g=JSON.parse(__townTest.save());g.mayorJourney.baseline.districts=["missing|waterfront|1"];return !__townTest.load(JSON.stringify(g));}')
 legacy=state();legacy['mayorJourney'].pop('baseline');assert p.evaluate('g=>__townTest.load(JSON.stringify(g))',legacy);assert p.evaluate('__townTest.validate().ok');p.close()
 p=fresh();p.evaluate('__townTest.step(31)');panel('agenda');button=p.locator('[data-mayor-direction=community]');button.evaluate('e=>e.closest("details").open=true');button.click();confirm();p.evaluate('__townTest.step(1)');assert state()['mayorJourney']['completed'][0]['existingPrerequisite'];results['existingPrerequisiteLabel']=state()['mayorJourney']['completed'][0];district('orchard-downs','neighbourhood');plan=p.evaluate('__followPlan()');assert sum(s['kind']=='home'for s in plan['sites'])==4;cells=[n for s in plan['sites']for n in s['cells']];assert len(cells)==len(set(cells));assert plan['cost']==sum(s['cost']for s in plan['sites'])+plan['roadCost'];before=state()['treasury']
 p.locator('[data-district-finish]').filter(has_text='Cottage').first.click();p.keyboard.press('Escape');assert state()['treasury']==before
 p.locator('[data-district-finish]').filter(has_text='Cottage').first.click();confirm();assert state()['treasury']==before-20000;assert p.evaluate('__followPlan().metrics.pop')==2;assert sum(s['kind']=='home'for s in p.evaluate('__followPlan().sites'))==3
 for i in range(3):
  while state()['treasury']<20000:panel('treasury');p.locator('#borrow').click()
  board();p.locator('[data-district-finish]').filter(has_text='Cottage').first.click();confirm()
 after_homes=p.evaluate('__followPlan()');assert after_homes['metrics']['pop']==8
 for label in ['Grocer','Bakery']:
  while state()['treasury']<5000:panel('treasury');p.locator('#borrow').click()
  board();p.locator('[data-district-finish]').filter(has_text=label).first.click();confirm()
 assert not any(s.get('business')for s in p.evaluate('__followPlan().sites')),'Existing two businesses need staffing inspection, not duplicate capital'

 board();p.get_by_text('What this capital envelope includes',exact=True).click();assert 'Build homes first' in p.locator('#panelBody').inner_text();before_budget=state()['policy']['educationBudget'];p.locator('[data-district-budget=educationBudget]').click();assert state()['policy']['educationBudget']==before_budget;board();out=ROOT/'reports/district-followthrough';out.mkdir(parents=True,exist_ok=True);p.locator('[data-project-card=district] .civic-watch-line').scroll_into_view_if_needed();p.screenshot(path=str(out/'actual-tract-plan.png'));results['initialPlan']=plan;results['afterFourNormalHomes']=after_homes;results['errors']=errors;results['source_sha256']=hashlib.sha256(source.encode()).hexdigest();(out/'controls.json').write_text(json.dumps(results,indent=2)+'\n');assert p.evaluate('__townTest.validate().ok');assert not errors,errors;b.close()
print('PASS existing-role exclusion, real new staffed roles, baseline/legacy archives, full legal disjoint tract plan, reviewed single-site cost/cancel, actual normal-credit housing and derived updated needs')
