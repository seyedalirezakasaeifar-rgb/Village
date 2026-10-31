"""Active purpose-built shore streets, real partial orders and a controlled closure UI fixture."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();OUT=ROOT/'reports/civic-turnarounds';OUT.mkdir(parents=True,exist_ok=True)
probe='''
window.__turnaroundProbe={plan:()=>civicDistrictBlueprint(G.civicProjects.active.district,true),pending:()=>pendingEvent,
 closeHistoricalWharf:()=>{const p=G.civicProjects.active.district,b=G.buildings.find(b=>b.kind==='wharf'&&parcelForTile(b.x,b.y)?.id===p.target),f=G.firms[b.firm],before=totalMoney();p.status='complete';p.completed=G.day;p.proof='Controlled historical operating record';const d=G.districtProgrammes[p.target];d.completed=true;d.held=30;d.completedDay=G.day;liquidateFirm(f,'Controlled closure for stewardship UI');civicStewardship(true);updateHeader();if(active)renderPanel(active);return{firm:f.id,building:b.id,before,after:totalMoney(),cash:f.cash,closed:f.closed};},
 facts:()=>({issues:civicStewardship(true),campaign:G.civicCampaign,learner:civicRenewalHousehold(),total:totalMoney()})};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390},has_touch=True);p.set_default_timeout(10000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click()
 state=lambda:p.evaluate('JSON.parse(__townTest.save())')
 def panel(name):
  if p.locator('#panel').evaluate('e=>e.classList.contains("show")') and 'active' in (p.locator('[data-panel='+name+']').get_attribute('class')or''):return
  p.locator('[data-panel='+name+']').click()
 def board():panel('overview');p.locator('[data-civic-projects]').click()
 def confirm():p.locator('[data-event-choice="0"]').click()
 def step(n):assert not p.evaluate('__townTest.get().pending');p.evaluate('n=>__townTest.step(n)',n)
 def policy(k,v):
  panel('policies');f=p.locator('[data-policy='+k+']');f.evaluate('e=>e.closest("details").open=true');f.fill(str(v));p.locator('#enactPolicy').click()
 # Real 180-unit bridge accepts two physical orders; a returned load never earns progress.
 board();p.locator('[data-civic-project-review=food]').click();confirm();p.locator('[data-civic-project-order]').click();confirm();s=state();orders=s['civicProjects']['active']['food']['orders'];loads=[o for o in s['regionalTrade']['shipments']if o['id']in orders];assert sorted(o['qty']for o in loads)==[60,120]
 returned=next(o['id']for o in loads if o['qty']==60);panel('economy');p.locator('#logisticsOffice > summary').click();p.locator('[data-logistics-cancel="'+str(returned)+'"]').click();confirm();step(22)
 assert abs(state()['civicProjects']['active']['food']['arrived']-120)<.001
 board();p.locator('[data-civic-project-order]').click();confirm();replacement=state()['civicProjects']['active']['food']['orders'];assert replacement
 step(25);assert state()['civicProjects']['active']['food']['status']=='complete'
 # Normal public funding and an actual adult term unlock later chapters.
 board();p.locator('[data-civic-project-review=skills]').click();confirm();p.locator('[data-civic-project-budget]').click();confirm();p.locator('#enactPolicy').click();step(180)
 assert state()['civicProjects']['active']['skills']['status']=='complete'
 board();assert p.locator('#civicCampaign').count()==1
 # A purpose plan reserves two different shore footprints and connects both in one purchase.
 p.locator('[data-civic-project-review=district]').click();p.locator('#projectParcel').select_option('river-reach');p.locator('#projectFocus').select_option('waterfront');p.locator('#projectDistrictAdopt').click();p.locator('[data-civic-project-deed]').click();confirm();p.locator('[data-civic-project-charter]').click();confirm()
 plan=p.evaluate('__turnaroundProbe.plan()');assert plan['ok'];assert {s['kind']for s in plan['sites']}=={'fishery','wharf'}
 assert len(set(plan['sites'][0]['footprint'])&set(plan['sites'][1]['footprint']))==0
 assert not set(plan['roads'])&set(plan['sites'][0]['footprint']+plan['sites'][1]['footprint']);assert plan['cost']==len(plan['roads'])*150
 before=state();p.locator('[data-civic-project-road]').click();p.keyboard.press('Shift+Tab');assert p.evaluate("document.activeElement.tagName==='SUMMARY'");p.keyboard.press('Enter');assert p.locator('.civic-blueprint-layout').evaluate('e=>e.open');p.screenshot(path=str(OUT/'shore-blueprint.png'));assert p.evaluate('__townArchive.back()');assert state()['treasury']==before['treasury'];assert not state()['civicProjects']['active']['district'].get('sitePlans')
 p.locator('[data-civic-project-road]').click();confirm();after=state();assert abs(before['treasury']-after['treasury']-plan['cost'])<.001
 assert after['civicProjects']['active']['district']['sitePlans']
 for kind in ['fishery','wharf']:
  p.locator('[data-civic-project-build='+kind+']').click();assert p.locator('#eventDialog').is_visible();assert 'at grid' in p.locator('#eventTitle').inner_text();confirm()
 built=state();assert sum(b['kind']=='wharf'for b in built['buildings'])==sum(b['kind']=='wharf'for b in before['buildings'])+1
 assert sum(t==1 for t in built['tiles'])-sum(t==1 for t in before['tiles'])==len(plan['roads']),'Second dock must not need an undisclosed extra spur'
 # Real physical plans survive an exact replay; impossible/overlapping plan data is rejected.
 checkpoint=p.evaluate('__townTest.save()');step(3);expected=state();assert p.evaluate('(s)=>__townTest.load(s)',checkpoint);step(3);actual=state()
 for key in ['day','treasury','civicProjects','regionalTrade']:assert actual[key]==expected[key],key
 for bad in ['g.civicProjects.active.district.sitePlans[0].x=-1','g.civicProjects.active.district.sitePlans[1]=g.civicProjects.active.district.sitePlans[0]']:
  assert p.evaluate('code=>{const g=JSON.parse(__townTest.save());new Function("g",code)(g);return !__townTest.load(JSON.stringify(g));}',bad)
 # Controlled historical metadata + real liquidation isolates the later-failure UI.
 step(35);closed=p.evaluate('__turnaroundProbe.closeHistoricalWharf()');assert closed['closed']and abs(closed['after']-closed['before'])<.001
 assert 'Cargo wharf closed' in p.locator('#mapStatusHeadline').inner_text();board();card=p.locator('[data-project-card=district]');assert 'Controlled historical operating record' in card.inner_text();assert 'Cargo wharf closed' in card.locator('.civic-watch-line').inner_text();assert card.locator('[data-inspect="'+str(closed['building'])+'"]').count()==1
 panel('overview');p.locator('#panelClose').click();assert p.locator('#mapStatusToggle').get_attribute('aria-expanded')=='false';p.locator('#mapStatusToggle').click();p.locator('[data-civic-watch-project]').click();assert p.locator('.civic-watch-line').count()==1
 p.screenshot(path=str(OUT/'current-closure-preserves-history.png'))
 before_rezone=state();p.locator('[data-civic-recharter]').click();p.keyboard.press('Escape');assert state()['treasury']==before_rezone['treasury']
 p.locator('[data-civic-recharter]').click();p.get_by_text('Recharter as Mixed neighbourhood',exact=True).click();pivot=state();assert abs(before_rezone['treasury']-pivot['treasury']-1200)<.001
 assert pivot['districtProgrammes']['river-reach']['focus']=='neighbourhood';assert any(b['id']==closed['building']for b in pivot['buildings']);assert pivot['firms'][closed['firm']]['closed'];assert pivot['civicProjects']['history'][0]['proof']=='Controlled historical operating record'
 assert pivot['civicProjects']['active']['district']['branch']=='neighbourhood'
 assert not p.evaluate('__turnaroundProbe.facts().issues')
 # Actual binding agreement after the chapter starts; past fulfilled contracts cannot qualify.
 p.locator('[data-campaign-review=promise]').last.click();p.keyboard.press('Escape');assert state().get('civicCampaign')is None
 p.locator('[data-campaign-review=promise]').last.click();confirm();chapter=state()['civicCampaign']['active'];assert chapter['reference']is None;step(3);assert state()['civicCampaign']['active']['status']=='active'
 board();p.locator('[data-campaign-exchange]').click();p.locator('[data-trade-offer]:not([disabled])').first.click();confirm();reference=state()['civicCampaign']['active']['reference'];assert reference and reference['kind']=='contract'
 board();p.locator('[data-campaign-operations]').click();p.locator('[data-logistics-priority=contracts]').click();assert state()['regionalTrade']['priority']=='contracts'
 step(35);campaign=state()['civicCampaign']['active'];assert campaign['status']=='complete',campaign
 assert campaign['proof'];assert p.evaluate('__townTest.validate().ok');assert not errors,errors
 (OUT/'active-controls.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'acceptedBridgeLoads':[120,60],'cancelledLoadCredited':False,'blueprint':plan,'secondShoreSpurRequired':False,'controlledHistoricalClosureFixture':closed,'recharterCost':1200,'existingPrivateBuildingRetained':True,'realSupplierChapter':campaign,'errors':errors},indent=2)+'\n')
 print('PASS staged 120+60/return/no-progress, real teaching unlock, complete paired shore blueprint/true cost/keyboard/Back, no second spur, controlled actual closure alert, historical record and private title retained, paid recharter and a genuinely new supplier agreement',flush=True)
 b.close()
