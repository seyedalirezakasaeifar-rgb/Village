#!/usr/bin/env python3
"""Controlled deferral -> exact repair -> actual admission, without minted funds."""
from pathlib import Path
import hashlib,json,sys,subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
METHOD=r'''
 recovery:(seedValue,variant)=>{
  const d=departureFixture(seedValue,0),b=d.home;G.regionalDemand=1;
  // Controlled published capacity isolates funding/access; this is not organic growth evidence.
  for(const f of G.firms)f.jobs=f.workers.length;
  const f=G.firms.find(f=>!f.closed);f.jobs+=100;recompute();
  const total=totalMoney(),profiles=[{age:30,skill:.4,health:90},{age:30,skill:.4,health:90}],quote=()=>migrationAssessment(b,profiles,2500),initial=quote(),tiles=G.tiles.slice(),cash=f.cash;
  if(variant==='funding'){G.region+=f.cash;f.cash=0;}
  if(variant==='access'){for(const id of [...graph().neighbors.keys()].filter(id=>Math.abs(id%T-b.x)+Math.abs((id/T|0)-b.y)<=3))if(G.tiles[id]===1)G.tiles[id]=0;invalidateRoads(false);}
  if(variant==='construction')b.redevelopment={fixture:true};
  const blocked=quote(),beforePeople=G.people.length,beforeFunds=totalMoney(),denied=addHouseholdAt(b,2500);
  if(denied)throw Error('Blocked candidate admitted');
  const deniedState={newPeople:G.people.length-beforePeople,cashDrift:totalMoney()-beforeFunds};
  if(variant==='funding'){G.region-=cash;f.cash=cash;}
  if(variant==='access'){G.tiles=tiles;invalidateRoads(false);}
  if(variant==='construction')delete b.redevelopment;
  const restored=quote(),regionBefore=G.region,peopleBefore=G.people.length;let h=null,attempts=0;
  // Ordinary generated profiles and probabilistic decisions; no RNG overrides or forced admission.
  for(;attempts<40&&!h;attempts++)h=addHouseholdAt(b,2500);
  const admitted=h?{id:h.id,people:h.people.slice(),cash:h.cash,home:h.home,offers:h.people.map(id=>({person:id,age:G.people[id].age,skill:G.people[id].skill,firm:G.people[id].job})),capitalRegionDelta:G.region-regionBefore}:null;
  const capitalDrift=totalMoney()-total,peopleAdded=G.people.length-peopleBefore;
  if(h)tick();
  return {seed:seedValue,variant,initial,blocked,deniedState,restored,attempts,admitted,peopleAdded,capitalDrift,afterDay:h?{cash:h.cash,income:h.income,incomeTax:h.incomeTax,people:h.people.slice(),jobs:h.people.map(id=>G.people[id].job),home:h.home,housing:migrationHousingStatus(b)}:null,cashDrift:totalMoney()-total,valid:validateTown(),roundTrip:hydrateSave(archivePayload())};
 },
'''

def main():
 source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest();fixture=(ROOT/'tests/fixtures/migration-causality-probe.js').read_text();assert fixture.count('departures:(seedValue)')==1
 probe=fixture.replace('departures:(seedValue)',METHOD+'departures:(seedValue)');out=ROOT/'reports/migration-recovery';out.mkdir(parents=True,exist_ok=True)
 result={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':sha,'method':'Controlled cottage vacancy follows actual departure. Published firm capacity is enlarged to isolate causes; no residents, money, skills, stock or wages granted. Funding stress moves existing payroll cash into region then exactly reverses it; access stress removes and restores the same road tiles; construction stress marks then completes redevelopment on the same empty cottage. Blocked admission attempted once; after exact repair at most 40 ordinary probabilistic invitations, without RNG overrides. This proves causal recovery boundaries, not organic job creation or player construction costs.','rows':[]}
 with sync_playwright()as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page();p.set_default_timeout(120000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.decode().replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
  for seed in [42,101,909]:
   for variant in ['funding','access','construction']:
    r=p.evaluate('o=>__migrationAudit.recovery(o.seed,o.variant)',{'seed':seed,'variant':variant});result['rows'].append(r);(out/'recovery.json').write_text(json.dumps(result,indent=2)+'\n')
    assert r['initial']['eligible']and not r['blocked']['eligible']and r['restored']['eligible'],r
    assert r['deniedState']['newPeople']==0 and abs(r['deniedState']['cashDrift'])<.001,r
    assert r['admitted']and r['peopleAdded']==len(r['admitted']['people'])and r['admitted']['capitalRegionDelta']==-2500,r
    assert all(x['firm']>=0 for x in r['admitted']['offers']),r
    assert r['afterDay']['income']>0 and r['valid']['ok']and r['roundTrip'],r
    assert abs(r['capitalDrift'])<.001 and abs(r['cashDrift'])<.001,r
    print(seed,variant,'blocked:',r['blocked']['reasons'],'recovered after',r['attempts'],'invitations; income',r['afterDay']['income'],flush=True)
  result['pageErrors']=errors;b.close()
 (out/'recovery.json').write_text(json.dumps(result,indent=2)+'\n')
 assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha and not result['pageErrors']

if __name__=='__main__':main()
