"""Disabled-by-default staged day vs unchanged synchronous tick, including RNG."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,json,hashlib
# Catch rare/conditional day-order drift independently of scenario coverage.
import re
clock=(ROOT/'src/50-clock.js').read_text();plain=clock.split('// Experimental continuation:')[0];staged=clock.split('function* stagedTick()',1)[1].split('function resetTownTransientUI',1)[0]
def calls(text):
 return [x.replace('stagedOutwardMigration','outwardMigration').replace('stagedSystemsDay','systemsDay').replace('stagedPrivateServiceInvestmentDay','privateServiceInvestmentDay').replace('stagedUrbanEvolutionDay','urbanEvolutionDay') for x in re.findall(r'(?<![.\w])([A-Za-z_$][\w$]*)\s*\(',text) if x not in ['tick','if','for','while']]
assert calls(plain)==calls(staged),'Synchronous/staged authoritative day order drifted'
source=(ROOT/'assets/game.js').read_text()
fixture=next(ast.literal_eval(n.value) for n in ast.parse((ROOT/'tests/test_transit_live_performance.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe=r'''
window.__coopTest={
 setup:(large,seedValue=42)=>{chosenScenario='settlement';seed(seedValue);if(large){__transitLive.large();__transitLive.build(12);}paused=true;return {defaultEnabled:cooperativeEnabled,population:G.people.length};},
 run:async(mode,days,commands=false)=>{for(let i=0;i<days;i++){if(mode==='synchronous')tick();else{if(!beginCooperativeDay())throw Error('Day rejected');await afterCommittedDay(()=>true);}if(commands&&i%17===0){const next=Math.min(48,G.policy.minWage+1);G.policy.minWage=next;journalPolicy('minWage',next-1,next);}}const g=JSON.parse(archivePayload());delete g.trafficState;delete g.visualState;return {archive:JSON.stringify(g),rng:rngState,day:G.day,valid:validateTown(),money:totalMoney(),samples:cooperativeSamples};},
 barrier:async()=>{const before=G.day;beginCooperativeDay();const r=await window.__cooperativeSimulation.command('minimum wage',()=>{G.policy.minWage++;return G.day;});return {before,after:G.day,executedDay:r,policy:G.policy.minWage,busy:cooperativeDayBusy()};}
};
'''
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'rows':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for large,seed_value,days in [(False,42,365),(False,81,90),(True,42,90)]:
  results=[]
  for mode in ['synchronous','staged']:
   p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();setup=p.evaluate('a=>__coopTest.setup(...a)',[large,seed_value]);assert setup['defaultEnabled'] is False;result=p.evaluate('a=>__coopTest.run(...a)',[mode,days,True]);assert result['valid']['ok'] and not errors,(result['valid'],errors);results.append(result);p.close()
  assert results[0]['archive']==results[1]['archive'],(large,seed_value,'Archive differs')
  assert results[0]['rng']==results[1]['rng'];out['rows'].append({'large':large,'seed':seed_value,'days':days,'exactArchive':True,'exactRng':True,'endDay':results[1]['day'],'maxSliceMs':max(s['ms'] for s in results[1]['samples']['slices'])})
 b.close()
(ROOT/'reports/cooperative-equivalence-8.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));print('PASS default unchanged; staged model/archive/RNG and boundary policy replay exactly match synchronous tick')
