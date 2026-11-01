"""Commercial districts must describe actual retail access and bank activity."""
from pathlib import Path
import hashlib, json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html

source=(ROOT/'assets/game.js').read_text()
probe=r'''window.__commercialDistricts={
 seed:(seed,days)=>{__townTest.reset('settlement',seed);if(days)__townTest.step(days);const c=urbanSpatial();return {day:G.day,population:G.stats.population,profiles:Object.values(c.profiles),banks:G.banks.filter(b=>!b.closed).map(b=>({id:b.id,createdDay:b.createdDay||0,deposit:bankDeposits(b.id),loans:bankLoans(b.id)})),valid:validateTown()};},
 state:()=>({archive:__townTest.save(),money:totalMoney(),region:G.region,treasury:G.treasury,rng:G.rngState,goods:JSON.stringify(goodsBalance()),banks:G.banks.map(b=>({id:b.id,createdDay:b.createdDay||0,cash:b.cash,deposit:bankDeposits(b.id),loans:bankLoans(b.id)}))}),
 inspect:id=>{const b=readBuild(id);selected={id};openPanel('inspect');return urbanBuildingDescriptor(b);},
 firstBank:()=>G.buildings.find(b=>b.kind==='bank'&&!G.banks[b.bankId]?.closed)?.id,
 quietRetail:key=>{const ids=G.firms.filter(f=>['grocer','tavern'].includes(f.kind)&&!f.closed&&urbanBlockKey(readBuild(f.building).x,readBuild(f.building).y)===key);for(const f of ids){f.workers=[];f.salesTrend=0;f.revenueTrend=0;}invalidateUrban();const p=urbanSpatial().profiles[key];return {ids:ids.map(f=>f.id),profile:p};},
 openMap:()=>{overlay='neighbourhoods';dirty=true;},
 valid:validateTown
};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
results={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'naturalSixYear':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1280,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html);page.add_script_tag(content=script);page.locator('#newTown').click();page.locator('#pause').click()
 for seed in (42,101):
  town=page.evaluate('(s)=>__commercialDistricts.seed(s,2160)',seed);profiles=town['profiles'];market=[p for p in profiles if 'Market centre' in p['observedTags']];finance=[p for p in profiles if 'Financial district' in p['observedTags']]
  assert town['valid']['ok'],town['valid']
  assert market,('ordinary six-year town has no active market street',seed)
  assert all(p['retailActiveBusinesses']>=2 and p['retailStaffedWorkers']>0 and p['retailSalesTrend']>0 and p['retailResidentsWithin24']>=12 and p['farms']==0 for p in market),market
  assert any(p['industrialBusinesses']>0 and 'Employment quarter' in p['observedTags'] for p in market),market
  assert all('Market centre' not in p['observedTags'] and 'Financial district' not in p['observedTags'] for p in profiles if p['farms']),profiles
  assert not finance and all(b['createdDay']==0 for b in town['banks']), (finance,town['banks'])
  before=page.evaluate('__commercialDistricts.state()');key=market[0]['key'];failed=page.evaluate('k=>__commercialDistricts.quietRetail(k)',key)
  assert failed['ids'] and failed['profile']['retailActiveBusinesses']==0 and 'Market centre' not in failed['profile']['observedTags'],failed
  assert page.evaluate('s=>__townTest.load(s)',before['archive']);after=page.evaluate('__commercialDistricts.state()')
  assert before['money']==after['money'] and before['region']==after['region'] and before['treasury']==after['treasury'] and before['rng']==after['rng'] and before['goods']==after['goods'] and before['banks']==after['banks']
  card=page.locator('[data-panel=construction]');card.click();page.locator('#urbanPlanningOffice>summary').click();panel=page.locator('#panelBody').inner_text()
  assert 'Market centre' in panel and 'within 24 road steps' in panel and 'stocked, staffed grocer' in panel,panel
  bank=page.evaluate('__commercialDistricts.firstBank()');descriptor=page.evaluate('id=>__commercialDistricts.inspect(id)',bank)
  assert descriptor['openBankBranches']==3 and descriptor['foundingBankBranches']==3 and descriptor['expandedBankBranches']==0
  assert descriptor['bankDeposits']>0 and 'Financial district' not in descriptor['observedTags']
  results['naturalSixYear'].append({'seed':seed,'day':town['day'],'population':town['population'],'marketBlocks':[{'key':p['key'],'retail':p['retailActiveBusinesses'],'workers':p['retailStaffedWorkers'],'salesUnitsDay':p['retailSalesTrend'],'salesRevenueDay':p['retailRevenueTrend'],'residentsReachable':p['retailResidentsWithin24'],'stockedReach':p['retailStockedResidentsWithin24'],'industry':p['industrialBusinesses'],'tags':p['observedTags']} for p in market],'banks':town['banks'],'financeBlocks':finance,'quietRetailClearsMarketTag':True})
 # A normal twenty-year settlement shows the new market pattern without forcing
 # bank entry; all institutions keep their original balance-sheet identities.
 long=page.evaluate('(s)=>__commercialDistricts.seed(s,7200)',42);markets=[p for p in long['profiles'] if 'Market centre' in p['observedTags']]
 assert long['valid']['ok'] and markets,long
 assert len(long['banks'])==3 and all(b['createdDay']==0 for b in long['banks'])
 before=page.evaluate('__commercialDistricts.state()');assert page.evaluate('s=>__townTest.load(s)',before['archive']);canonical=page.evaluate('__commercialDistricts.state()');archive=canonical['archive'];first=page.evaluate('s=>{__townTest.step(30);return __townTest.save()}',archive)
 assert page.evaluate('s=>__townTest.load(s)',archive);second=page.evaluate('s=>{__townTest.step(30);return __townTest.save()}',archive)
 assert json.loads(first)==json.loads(second)
 results['natural20Year']={'day':long['day'],'population':long['population'],'marketBlocks':[p['key'] for p in markets],'openBanks':long['banks'],'financeBlocks':[p['key'] for p in long['profiles'] if 'Financial district' in p['observedTags']],'exact30DayReplayAfterArchiveCanonicalization':True,'valid':long['valid']}
 assert not errors,errors;results['errors']=errors;browser.close()
out=ROOT/'docs/previews/urban8';out.mkdir(parents=True,exist_ok=True);(out/'commercial-districts.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS natural market access, mixed-use tags, bank-entry limits, quiet-market adversity and exact replay')
