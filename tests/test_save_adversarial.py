"""Reject corrupt record graphs atomically; preserve valid input and exact replay.

No economics mocks: archive fault injection runs against the assembled game. The
replay checks all persisted fields recursively except presentation/transient caches.
"""
from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
probe=r'''
window.__saveQA=()=>{
 const original=archivePayload(),base=JSON.parse(original),checks=[];
 const mutations={
  missingMember:g=>{const p=g.people.find(p=>!p.deceased&&!p.movedAway);g.households[p.hh].people=g.households[p.hh].people.filter(id=>id!==p.id)},
  duplicateMember:g=>g.households[0].people.push(g.households[0].people[0]),
  // Current membership is bidirectional only for living residents in town.
  householdMismatch:g=>{const p=g.people.find(p=>!p.deceased&&!p.movedAway);p.hh=(p.hh+1)%g.households.length;},
  missingHome:g=>g.households.find(h=>h.people.length).home=999999,
  tileUsedAsHomeId:g=>{const b=g.buildings.find(b=>b.kind==='home');g.households.find(h=>h.people.length).home=b.y*T+b.x},
  missingFirmBuilding:g=>g.firms[0].building=999999,
  negativeStock:g=>g.firms[0].stock.grain=-1,
  invalidStock:g=>g.firms[0].stock.grain=null,
  unknownStock:g=>g.firms[0].stock.unobtainium=1,
  negativeDeposit:g=>g.households[0].deposits={0:-100},
  missingDepositBank:g=>g.households[0].deposits={999999:100},
  malformedBank:g=>g.banks.push({id:g.banks.length,cash:-1,depositAPY:.1,loanAPY:.1}),
  malformedLoan:g=>g.loans.push({id:999999,balance:-1,status:'active'}),
  negativeLoanBank:g=>g.loans.push({id:999999,balance:100,status:'active',ownerType:'household',ownerId:0,bankId:-2,rate:.1}),
  duplicateBuildingId:g=>g.buildings[1].id=g.buildings[0].id,
  exhaustedIdCounter:g=>g.nextId=1,
  duplicateHomeId:g=>g.homes.push(g.homes[0]),
  orphanWorker:g=>{const f=g.firms.find(f=>f.workers.length);f.workers=[]},
  duplicateWorker:g=>{const f=g.firms.find(f=>f.workers.length);f.workers.push(f.workers[0])},
  missingOwner:g=>g.buildings[0].owner=999999,
  missingTitleHolder:g=>g.buildings[0].title={kind:'household',id:999999},
  truncatedTiles:g=>g.tiles.pop(),
  malformedProject:g=>g.projects.push(null),
  futureSchema:g=>g.schema=RELEASE.schema+1,
  invalidDay:g=>g.day=-1
 };
 for(const [name,mutate] of Object.entries(mutations)){
  const g=JSON.parse(original);mutate(g);const candidate=JSON.stringify(g),before=archivePayload(),rng=rngState,head=[saveEpoch,saveTown,saveRevision,saveOrder];
  if(hydrateSave(g))throw Error('Accepted malformed archive: '+name);
  if(archivePayload()!==before||rngState!==rng||JSON.stringify(head)!==JSON.stringify([saveEpoch,saveTown,saveRevision,saveOrder]))throw Error('Rejected import changed live town/timeline/RNG: '+name);
  if(JSON.stringify(g)!==candidate)throw Error('Rejected import mutated caller candidate: '+name);checks.push(name);
 }
 for(const raw of [original.slice(0,-1),'{broken','null','[]'])if(hydrateSave(raw)||archivePayload()!==original)throw Error('Truncated/raw import not atomic');
 const candidate=JSON.parse(original),before=JSON.stringify(candidate);if(!hydrateSave(candidate))throw Error('Valid object import rejected');if(JSON.stringify(candidate)!==before)throw Error('Successful import mutated caller candidate');candidate.households[0].cash+=99999;if(G.households[0].cash===candidate.households[0].cash)throw Error('Live town aliases caller object');
 if(!hydrateSave(original)||!validateTown().ok)throw Error('Original cannot continue');
 return {grid:T,schema:RELEASE.schema,originalPersonZero:{id:base.people[0].id,hh:base.people[0].hh,deceased:!!base.people[0].deceased,movedAway:!!base.people[0].movedAway,rosters:base.households.filter(h=>h.people.includes(0)).map(h=>h.id)},recordsRejected:checks,truncatedRejected:4,callerIndependent:true,atomicRNGAndTimeline:true};
};
window.__householdCounterexamples=()=>{
 const original=archivePayload(),money=totalMoney(),results=[];
 // Historical people deliberately leave current rosters at death/departure.
 // Their household and its financial/property identity remain in the archive.
 for(const status of ['deceased','movedAway'])for(const legacy of [false,true])for(const empty of [false,true]){
  const g=JSON.parse(original),h=g.households.find(h=>h.people.length>1),ids=empty?h.people.slice():h.people.slice(0,1);
  for(const id of ids){const p=g.people[id];p[status]=true;p.job=-1;for(const f of g.firms)f.workers=f.workers.filter(n=>n!==id);}
  h.people=h.people.filter(id=>!ids.includes(id));if(empty&&!legacy)h.home=-1;if(legacy)g.schema=7;
  const estate={id:h.id,cash:h.cash,deposits:JSON.stringify(h.deposits),owners:JSON.stringify(g.buildings.filter(b=>b.owner===h.id||b.title?.kind==='household'&&b.title.id===h.id).map(b=>b.id)),loans:JSON.stringify(g.loans.filter(l=>l.ownerType==='household'&&l.ownerId===h.id))};
  if(!hydrateSave(g))throw Error('Valid historical household rejected: '+status+'/'+legacy+'/'+empty);
  const kept=G.households[h.id];if(kept.cash!==estate.cash||JSON.stringify(kept.deposits)!==estate.deposits||JSON.stringify(G.loans.filter(l=>l.ownerType==='household'&&l.ownerId===h.id))!==estate.loans||JSON.stringify(G.buildings.filter(b=>b.owner===h.id||b.title?.kind==='household'&&b.title.id===h.id).map(b=>b.id))!==estate.owners||ids.some(id=>G.people[id].hh!==h.id)||Math.abs(totalMoney()-money)>.001)throw Error('Historical estate identity/balances changed');
  const accepted=archivePayload();for(const fault of ['historicalRoster','missingHistoricalHousehold']){
   const bad=JSON.parse(accepted);if(fault==='historicalRoster')bad.households[h.id].people.push(ids[0]);else bad.people[ids[0]].hh=bad.households.length;
   const before=archivePayload(),rng=rngState,timeline=JSON.stringify([saveEpoch,saveTown,saveRevision,saveOrder]),caller=JSON.stringify(bad);
   if(hydrateSave(bad)||archivePayload()!==before||rngState!==rng||JSON.stringify([saveEpoch,saveTown,saveRevision,saveOrder])!==timeline||JSON.stringify(bad)!==caller)throw Error('Historical graph rejection not atomic: '+fault);
  }
  results.push({status,legacy,people:ids.length,emptyEstate:empty,validHouseholdAccepted:true,financialIdentityPreserved:true,invalidRosterAndHouseholdRejected:true});
 }
 if(!hydrateSave(original))throw Error('Counterexample original cannot continue');return results;
};
window.__saveReplay=()=>{
 const canonical=v=>Array.isArray(v)?v.map(canonical):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])])):v;
 const snapshot=()=>{const g=JSON.parse(archivePayload());for(const key of ['trafficState','visualState'])delete g[key];return canonical(g)};
 const saved=archivePayload(),total=totalMoney();__townTest.step(90);const first=snapshot();if(!hydrateSave(saved))throw Error('Valid replay import rejected');__townTest.step(90);const second=snapshot();
 const changed=Object.keys(first).filter(k=>JSON.stringify(first[k])!==JSON.stringify(second[k]));if(changed.length)throw Error('Replay changed: '+changed.join(','));
 const valid=validateTown(),goods=Math.max(...goodsBalance().map(r=>Math.abs(r.error)));if(!valid.ok||Math.abs(total-totalMoney())>.01||goods>.001)throw Error('Replay violated books');return {days:90,exactCanonical:true,cashDrift:totalMoney()-total,goodsError:goods,population:G.stats.population};
};
'''
results={'source_sha256':sha,'checks':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
 for scenario,days in [('settlement',0),('regional',360),('hardtimes',720)]:
  p.evaluate('sc=>__townTest.reset(sc,42)',scenario)
  if days:p.evaluate('n=>__townTest.step(n)',days)
  result=p.evaluate('__saveQA()');result['scenario']=scenario;result['ageDays']=days;result['historicalCounterexamples']=p.evaluate('__householdCounterexamples()');result['replay']=p.evaluate('__saveReplay()');results['checks'].append(result);print('PASS',scenario,days,'atomic rejection and replay',flush=True)
 for path in sorted((ROOT/'tests/fixtures').glob('*.json')):
  assert p.evaluate('s=>__townTest.load(s)',path.read_text()),path.name
  assert p.evaluate('__townTest.validate().ok'),path.name
  results.setdefault('historicalFixtures',[]).append(path.name)
 assert not errors,errors;b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-save-qa';out.mkdir(exist_ok=True);(out/'adversarial.json').write_text(json.dumps(results,indent=2)+'\n')
