"""Bounded mayor histories; no grants, forced closures or edited residents."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__mayor=o=>{__townTest.reset(o.scenario,42);const total=totalMoney(),actions=[],samples=[];if(o.strategy==='private-first'){G.policy.educationBudget=0;G.policy.defenseBudget=0;G.policy.serviceVoucherBudget=100;actions.push({day:G.day,privateSchool:seekPrivateServiceInvestment('school')});}
__townTest.step(25);const offer=publicPlaceOffer();if(offer&&G.treasury>=buildCost.square){construct('square',offer.x,offer.y);actions.push({day:G.day,square:buildingAt(offer.x,offer.y)?.id});}
const supplier=G.firms.find(f=>f.kind==='farm'&&!f.closed);if(supplier){const review=reviewRegionalProcurement({firmId:supplier.id,marketId:'port',good:'grain',milestones:[{quantity:50,deadline:G.day+15},{quantity:100,deadline:G.day+30}]});actions.push({day:G.day,order:review.ok?authorizeRegionalProcurement(review):{ok:false,reason:review.reason}});}
for(let month=0;month<12;month++){
 if(o.strategy==='public-first'){const p=G.stats.population,w=Math.max(24,G.policy.minWage);G.policy.educationBudget=Math.ceil(p*10/260*w/.65);G.policy.healthBudget=Math.ceil(p*5/350*w/.65);}
 if(month%3===0){const venue=civicGatheringVenues()[0];if(venue){const q=reviewCivicGathering({venue:venue.b.id,start:G.day+1});actions.push({day:G.day,gathering:q.ok?authorizeCivicGathering(q):{ok:false,reason:q.reason}});}}
 const candidate=G.buildings.find(b=>BROWNFIELD_KINDS.includes(b.kind)&&G.firms[b.firm]?.closed&&!brownfieldSites().some(s=>s.id===b.id));if(candidate&&G.treasury>100000)actions.push({day:G.day,assessment:brownfieldAssess(candidate.id)});
 for(const s of brownfieldSites()){if(s.status==='assessed'&&G.treasury>100000)actions.push({day:G.day,acquisition:brownfieldAcquire(s.id)});if(s.status==='acquired'&&G.treasury>100000)actions.push({day:G.day,groundWorks:brownfieldFund(s.id)});if(s.status==='ready'&&G.treasury>50000)actions.push({day:G.day,reuse:brownfieldReuse(s.id,'park')});}
 __townTest.step(30);const cashDrift=totalMoney()-total,goodsError=Math.max(...goodsBalance().map(x=>Math.abs(x.error)));if(Math.abs(cashDrift)>.001||goodsError>.001||!validateTown().ok)throw Error('Combined books failed');samples.push({day:G.day,population:G.stats.population,treasury:G.treasury,hardship:G.stats.hardship,education:G.education,health:G.health,providers:G.firms.filter(f=>f.privateService).map(f=>({kind:f.kind,closed:!!f.closed,clients:f.clientsToday,cash:f.cash})),brownfields:brownfieldSites().map(s=>({id:s.id,status:s.status})),contracts:G.regionalTrade.contracts.map(c=>({id:c.id,status:c.status,delivered:c.delivered})),gatherings:civicCalendarView().events.map(e=>({status:e.status,paid:e.paid,visits:e.visits})),migration:migrationDiagnostics(),cashDrift,goodsError});
}
const checkpoint=archivePayload();__townTest.step(30);const future=archivePayload();if(!hydrateSave(checkpoint))throw Error('Combined load rejected');__townTest.step(30);if(archivePayload()!==future)throw Error('Combined replay differs');return {actions,samples,closedIndustrialSites:G.buildings.filter(b=>BROWNFIELD_KINDS.includes(b.kind)&&G.firms[b.firm]?.closed).length};};
'''
out=ROOT/'reports/combined-mayor';out.mkdir(exist_ok=True);rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_default_timeout(180000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
 for scenario in ['settlement','regional']:
  for strategy in ['public-first','private-first']:
   row={'scenario':scenario,'strategy':strategy};rows.append(row)
   try:row['result']=p.evaluate('o=>__mayor(o)',{'scenario':scenario,'strategy':strategy});row['status']='complete'
   except Exception as e:row['status']='failed';row['failure']=str(e)
   (out/'results.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'rows':rows,'errors':errors},indent=2));print(scenario,strategy,row['status'],row.get('failure',''),flush=True)
 b.close()
assert all(x['status']=='complete'for x in rows)and not errors
