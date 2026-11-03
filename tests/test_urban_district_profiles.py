"""Observed district patterns, service/access indicators and renderer handoff."""
from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html

source=(ROOT/'assets/game.js').read_text()
probe=r'''window.__districtProfile={
 report:()=>{const c=urbanSpatial();return {day:G.day,medianIncome:c.median,medianCenterDistance:c.medianCenterDistance,profiles:Object.values(c.profiles),blocks:Object.values(c.blocks),districts:Object.values(ensureUrban().districts)};},
 building:id=>urbanBuildingDescriptor(id),descriptor:(x,y)=>urbanDescriptor(x,y),snapshot:()=>__townTest.save(),money:totalMoney,goods:goodsBalance,validate:validateTown,
 seed:(value,days)=>{__townTest.reset('settlement',value);if(days)__townTest.step(days);return __districtProfile.report();},
 target:()=>{const b=G.buildings.find(b=>b.kind==='home'),old=ensureUrban().zones[urbanBlockKey(b.x,b.y)],plan=old?.plan==='residential'?'civic':'residential';return {id:b.id,plan,existing:old?.plan||'market',cost:old?1800:600,day:G.day};},
 open:id=>{selected={id};openPanel('inspect');},
 inspect:()=>{const b=G.buildings.find(b=>b.kind==='bank'&&!G.banks[b.bankId]?.closed),before=__districtProfile.snapshot(),cash=totalMoney(),rng=G.rngState,goods=JSON.stringify(goodsBalance()),descriptors=G.buildings.map(b=>urbanBuildingDescriptor(b)).filter(Boolean),home=descriptors.find(d=>['home','apartment','tower'].includes(d.buildingKind)),bank=b&&urbanBuildingDescriptor(b.id),after=__districtProfile.snapshot();return {before,after,cashBefore:cash,cashAfter:totalMoney(),rngBefore:rng,rngAfter:G.rngState,goodsBefore:goods,goodsAfter:JSON.stringify(goodsBalance()),bank,home,availableKinds:[...new Set(descriptors.map(d=>d.buildingKind))],buildingFamilies:[...new Set(descriptors.map(d=>d.buildingCue))],cityValid:validateTown()};},
 state:()=>({money:totalMoney(),treasury:G.treasury,region:G.region,rng:G.rngState,buildings:G.buildings.length,people:G.people.length,goods:JSON.stringify(goodsBalance())}),
 replay:s=>{if(!__townTest.load(s))return false;__townTest.step(30);return __townTest.save();}
};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
rows={'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1280,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);page.add_script_tag(content=script);page.locator('#newTown').click();page.locator('#pause').click()
 natural=[]
 for seed in (42,101):
  result=page.evaluate('(s)=>__districtProfile.seed(s,2160)',seed);p=result['profiles'];counts={}
  for item in p:
   for tag in item['tags']:counts[tag]=counts.get(tag,0)+1
  farms=[v for v in p if v['farms']]
  assert all('Financial district' not in v['tags'] for v in farms),farms
  financial=[v for v in p if 'Financial district' in v['tags']]
  assert all(v['openBankBranches']>=2 and v['financialActivity']>0 and v['farms']==0 for v in financial),financial
  natural.append({'seed':seed,'day':result['day'],'elapsedDays':2160,'patternCounts':counts,'incomeBands':{k:sum(v['incomeBand']==k for v in p) for k in ('Lower income','Middle income','Higher income','No resident income')},'financialEvidence':[{'branches':v['openBankBranches'],'deposits':v['bankDeposits'],'loans':v['bankLoans']} for v in financial]})
 # The inspector/renderer handoff is derived and must not move RNG, cash, goods,
 # property, workers or save records. A real financial branch uses actual books.
 financial=page.evaluate('__districtProfile.inspect()')
 assert financial['before']==financial['after'] and financial['cashBefore']==financial['cashAfter'] and financial['rngBefore']==financial['rngAfter'] and financial['goodsBefore']==financial['goodsAfter']
 assert financial['bank']['buildingCue']=='nl-stone-brick-bank' and financial['bank']['bankDeposits']>0 and financial['bank']['openBankBranches']>=2
 assert financial['home']['incomeBand'] in ('Lower income','Middle income','Higher income') and isinstance(financial['home']['condition'],(int,float))
 assert financial['cityValid']['ok'],financial['cityValid']
 # Actual planning UI shows the evidence separately from zoning and then
 # records an ordinary $600 plan change without changing total cash.
 target=page.evaluate('__districtProfile.target()');page.locator('[data-panel=construction]').click();page.locator('#urbanPlanningOffice>summary').click();button=page.locator(f'[data-inspect="{target["id"]}"]');button.scroll_into_view_if_needed();button.click();page.locator('summary',has_text='Change the 8 × 8 neighbourhood plan').click();plan=page.locator(f'[data-urban-plan="{target["plan"]}"][data-urban-building="{target["id"]}"]');plan.scroll_into_view_if_needed();plan.click();assert page.locator('#eventDialog').is_visible();review=page.locator('#eventText').inner_text();assert '$600' in review and target['existing'].lower() in review.lower()
 before=page.evaluate('__districtProfile.state()');page.locator('[data-event-choice="0"]').click();after=page.evaluate('__districtProfile.state()')
 assert abs(before['money']-after['money'])<.01 and before['treasury']-after['treasury']==600 and after['region']-before['region']==600 and before['buildings']==after['buildings'] and before['people']==after['people'] and before['goods']==after['goods'] and before['rng']==after['rng']
 # This deterministic plan and normal simulation continuation survive save/load.
 archive=page.evaluate('__districtProfile.snapshot()');first=page.evaluate('__townTest.step(30);__districtProfile.snapshot()');assert page.evaluate('s=>__townTest.load(s)',archive);page.evaluate('__townTest.step(30)');second=page.evaluate('__districtProfile.snapshot()');assert json.loads(first)==json.loads(second)
 assert page.evaluate('__districtProfile.validate()').get('ok') and not errors,errors
 rows.update({'naturalSixYearProfiles':natural,'rendererHandoff':{k:v for k,v in financial.items() if k not in ('before','after','goodsBefore','goodsAfter')},'uiPlanReview':{'target':target,'reviewText':review,'totalFundsConserved':True,'noHouseholdJobOrGoodsChanges':True},'exact30DaySaveReplay':True,'errors':errors})
 out=ROOT/'docs/previews/urban8';out.mkdir(parents=True,exist_ok=True);(out/'district-profiles.json').write_text(json.dumps(rows,indent=2)+'\n');browser.close()
print('PASS natural district profiles, truthful service/finance indicators, actual planning UI and exact save replay')
