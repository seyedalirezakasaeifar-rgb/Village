"""Allocation uses live demand; consistent-population policies/payments remain identical."""
import hashlib,json,subprocess
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text();old_access=subprocess.check_output(['git','show','848bf1b:src/12-service-access.js'],cwd=ROOT,text=True);legacy=source.replace((ROOT/'src/12-service-access.js').read_text(),old_access,1);assert legacy!=source
probe=r'''window.__populationAllocator=scenario=>{
 __townTest.reset(scenario,42);recompute();const actual=G.households.reduce((n,h)=>n+h.people.filter(id=>G.people[id]&&!G.people[id].deceased&&!G.people[id].movedAway).length,0),normal={},cases=[],baseline=archivePayload(),money=totalMoney(),rng=rngState;
 for(const kind of ['health','school'])normal[kind]=serviceAccess(kind);
 const outlook=serviceBudgetOutlook({...G.policy});
 for(const published of [0,Math.max(0,actual-1),actual+17,actual*3]){
  G.stats.population=published;serviceAccessCaches.clear();const before=JSON.stringify(G),outputs={};for(const kind of ['health','school'])outputs[kind]=serviceAccess(kind);if(before!==JSON.stringify(G)||money!==totalMoney()||rng!==rngState)throw Error('Access reader changed model, money or RNG');cases.push({published,actual,outputs});
 }
 G.stats.population=actual;serviceAccessCaches.clear();if(archivePayload()!==baseline)throw Error('Population test failed to restore original complete state');const beforeMoney=totalMoney();fundCivicServices();return {actual,normal,outlook,cases,normalPaidArchive:archivePayload(),normalPurchaseMoneyError:totalMoney()-beforeMoney};
};'''
rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for scenario in ['settlement','regional','industrial']:
  pair=[]
  for label,js in [('oldAllocator',legacy),('fixedAllocator',source)]:
   p=b.new_page();p.set_content(html);p.add_script_tag(content=js.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();data=p.evaluate('s=>__populationAllocator(s)',scenario);p.close();assert abs(data['normalPurchaseMoneyError'])<.001;pair.append(data)
  old,new=pair;assert old['normal']==new['normal']and old['outlook']==new['outlook'],scenario
  assert json.loads(old['normalPaidArchive'])==json.loads(new['normalPaidArchive']),scenario
  for case in new['cases']:
   for kind,allocation in case['outputs'].items():
    assert allocation['population']==case['actual']and abs(allocation['served']-sum(h['served']for h in allocation['households']))<1e-7,(scenario,case)
    assert abs(allocation['coverage']-(min(1,allocation['served']/case['actual'])if case['actual']else 0))<1e-10
    assert allocation==new['normal'][kind],(scenario,case)
  assert any(c['outputs']['health']['population']!=c['actual']for c in old['cases'])
  rows.append({'scenario':scenario,'actualPopulation':new['actual'],'stalePublishedCounts':[c['published']for c in new['cases']],'normalAccessIdentical':True,'normalPolicyOutlookIdentical':True,'completeStateAfterNormalPurchasesIdentical':True,'allStaleAggregateCasesUseSameLiveAllocation':True,'moneyConserved':True})
 b.close()
print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'old_allocator_control_source_sha256':hashlib.sha256(legacy.encode()).hexdigest(),'cases':rows,'limits':'Controlled aggregate perturbations change no people or workers; no guarantee of unchanged future outcomes when fixing a genuinely stale allocation.'},indent=2))
