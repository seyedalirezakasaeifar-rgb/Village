from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib,os,re,subprocess
source=(ROOT/'assets/game.js').read_text();preview=os.environ.get('MIGRATION_PREVIEW_REF')
if preview:
 # Isolated, explicitly labelled composition using the engine owner's exact modules.
 # No tracked source or distribution file is modified; candidate normalization stays with its owner.
 pieces=re.split(r'(?m)^// SOURCE: ([^\n]+)\n',source);modules={pieces[i]:pieces[i+1]for i in range(1,len(pieces),2)}
 for name in ['10-finance.js','20-world.js','25-scenarios.js','40-development.js','42-construction.js','44-migration.js','45-public-services.js','50-clock.js','70-interaction.js','80-civic.js','98-migration-ui.js']:
  modules[name]=subprocess.check_output(['git','show',preview+':src/'+name],cwd=ROOT,text=True)
 source='\n'.join('// SOURCE: '+name+'\n'+body for name,body in sorted(modules.items()))
probe='window.__followPlan=()=>districtFollowthroughPlan(G.civicProjects.active.district);window.__entryFixture={closeAds:()=>{for(const f of G.firms)f.jobs=f.workers.length;}};'
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
 p=fresh();p.evaluate('__townTest.step(31)');panel('agenda');button=p.locator('[data-mayor-direction=community]');button.evaluate('e=>e.closest("details").open=true');button.click();confirm();p.evaluate('__townTest.step(1)');assert state()['mayorJourney']['completed'][0]['existingPrerequisite'];results['existingPrerequisiteLabel']=state()['mayorJourney']['completed'][0];district('orchard-downs','neighbourhood');plan=p.evaluate('__followPlan()');assert sum(s['kind']=='home'for s in plan['sites'])==(1 if plan['housing']['available'] else 4);cells=[n for s in plan['sites']for n in s['cells']];assert len(cells)==len(set(cells));assert plan['cost']==sum(s['cost']for s in plan['sites'])+plan['roadCost'];before=state()['treasury']
 p.locator('[data-district-finish]').filter(has_text='Cottage').first.click();p.keyboard.press('Escape');assert state()['treasury']==before
 p.locator('[data-district-finish]').filter(has_text='Cottage').first.click();confirm();assert state()['treasury']==before-20000;first_plan=p.evaluate('__followPlan()');aware=first_plan['housing']['available'];results['migrationAware']=aware
 if aware:
  homes=[v for v in state()['buildings']if v['kind']=='home'and v['x']==plan['sites'][next(i for i,s in enumerate(plan['sites'])if s['kind']=='home')]['x']and v['y']==plan['sites'][next(i for i,s in enumerate(plan['sites'])if s['kind']=='home')]['y']];assert homes[0]['owner']==-1 and homes[0]['title']['kind']=='municipal'
 else:assert first_plan['metrics']['pop']==2
 assert sum(s['kind']=='home'for s in first_plan['sites'])==((0 if first_plan['housing']['vacancies']or first_plan['metrics']['pop']>=8 else 1)if aware else 3)
 if aware and first_plan['housing']['vacancies']:
  board();p.locator('[data-district-admission]').first.click();results['naturalVacancyAssessment']=p.locator('#eventText').inner_text();assert 'not actual applicants' in results['naturalVacancyAssessment'];p.keyboard.press('Escape')
 for i in range(3):
  if not any(s['kind']=='home'for s in p.evaluate('__followPlan().sites')):break
  while state()['treasury']<20000:panel('treasury');p.locator('#borrow').click()
  board();p.locator('[data-district-finish]').filter(has_text='Cottage').first.click();confirm()
 after_homes=p.evaluate('__followPlan()')
 if aware:
  assert sum(h['capacity']for h in after_homes['housing']['homes'])>=1 and all(h['occupied']<=h['capacity']for h in after_homes['housing']['homes'])
  ids={h['building']for h in after_homes['housing']['homes']};assert all(b['owner']==-1 and b['title']['kind']=='municipal'for b in state()['buildings']if b['id']in ids)
 else:assert after_homes['metrics']['pop']==8
 if not aware or after_homes['housing']['vacancies']:assert not any(s['kind']=='home'for s in after_homes['sites'])
 for label in ['Grocer','Bakery']:
  while state()['treasury']<5000:panel('treasury');p.locator('#borrow').click()
  board();p.locator('[data-district-finish]').filter(has_text=label).first.click();confirm()
 assert not any(s.get('business')for s in p.evaluate('__followPlan().sites')),'Existing two businesses need staffing inspection, not duplicate capital'

 board();p.get_by_text('What this capital envelope includes',exact=True).click();assert 'Build homes first' in p.locator('#panelBody').inner_text();before_budget=state()['policy']['educationBudget'];p.locator('[data-district-budget=educationBudget]').click();assert state()['policy']['educationBudget']==before_budget;board();out=ROOT/('reports/district-migration-preview'if preview else'reports/district-followthrough');out.mkdir(parents=True,exist_ok=True);p.locator('[data-project-card=district] .civic-watch-line').first.scroll_into_view_if_needed();p.screenshot(path=str(out/'actual-tract-plan.png'));results['initialPlan']=plan;results['afterReviewedHousingPhase']=after_homes;results['errors']=errors;results['migrationPreviewDependency']=preview;results['source_sha256']=hashlib.sha256(source.encode()).hexdigest();(out/'controls.json').write_text(json.dumps(results,indent=2)+'\n');assert not errors,errors
 if not preview:assert p.evaluate('__townTest.validate().ok')
 if aware:
  p.close();p=fresh();p.evaluate('__townTest.step(31)');district('orchard-downs','neighbourhood')
  # Controlled rejection fixture: remove employer adverts, grant nobody work or cash.
  p.evaluate('__entryFixture.closeAds()');before_people=state()['people'];p.locator('[data-district-finish]').filter(has_text='Cottage').first.click();confirm();empty=p.evaluate('__followPlan()');assert empty['metrics']['pop']==0 and empty['housing']['vacancies']==1
  board();cash_before_quote=state()['treasury'];p.locator('[data-district-admission]').click();text=p.locator('#eventText').inner_text();assert 'No funded reachable job' in text and 'not actual applicants' in text;assert 'cannot' in p.locator('#eventTitle').inner_text();assert state()['people']==before_people and state()['treasury']==cash_before_quote;p.screenshot(path=str(out/'unfunded-address-assessment.png'));confirm();assert 'BUSINESS' in p.locator('#panelBody').inner_text().upper()
  results['controlledUnfundedAddress']=text;results['unfundedVacancyPlan']=empty;
  if not preview:assert p.evaluate('__townTest.validate().ok')
  (out/'controls.json').write_text(json.dumps(results,indent=2)+'\n')
 b.close()
print(('MIGRATION PREVIEW '+preview+' 'if preview else'CURRENT INTEGRATED BUNDLE ')+'PASS existing-role exclusion, real new staffed roles, baseline/legacy archives, full legal disjoint tract plan, reviewed single-site cost/cancel, actual normal-credit housing and derived updated needs')
