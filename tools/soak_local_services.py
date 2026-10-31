"""Unpackaged development soak: matched towns, service withdrawal/recovery."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest();rows=[];out=ROOT/'reports/development-local-services';out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_default_timeout(120000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.decode());p.locator('#newTown').click();p.locator('#pause').click()
 for scenario in ['settlement','frontier','hardtimes','industrial','regional']:
  for seed in [42,101,909]:
   for mode in ['baseline','withdraw-recover']:
    r=p.evaluate('''o=>{__townTest.reset(o.scenario,o.seed);const total=__townTest.get().total,points=[];for(let month=0;month<24;month++){
      if(o.mode==='withdraw-recover'&&month===3){__townTest.set('healthBudget',0);__townTest.set('educationBudget',0);}
      if(o.mode==='withdraw-recover'&&month===6){__townTest.set('healthBudget',300);__townTest.set('educationBudget',400);}
      if([3,6,7].includes(month)){for(let d=0;d<30;d++){__townTest.step(1);const a=JSON.parse(__townTest.save()),w=Math.max(24,a.policy.minWage);if(a.people.some(p=>(p.publicIncome||0)>w+.0001||(p.job>=0&&p.publicWork)))throw Error('Daily workforce overlap at service transition');}}else __townTest.step(30);const g=JSON.parse(__townTest.save()),wage=Math.max(24,g.policy.minWage);if(g.people.some(p=>(p.publicIncome||0)>wage+.0001||(p.job>=0&&p.publicWork)))throw Error('Public/private workforce overlap');
      points.push({day:g.day,population:g.stats.population,employment:g.stats.employment,treasury:g.treasury,health:g.health,education:g.education,provision:g.serviceProvision,trainees:g.civicTraining?.length||0});
     }return {...o,points,valid:__townTest.validate(),drift:__townTest.get().total-total};}''',{'scenario':scenario,'seed':seed,'mode':mode});assert r['valid']['ok'] and abs(r['drift'])<.1,r
    if mode=='withdraw-recover':assert all(x['provision']['health']['coverage']==x['provision']['school']['coverage']==0 for x in r['points'][3:6])
    rows.append(r);print(scenario,seed,mode,r['points'][-1]['employment'],round(r['drift'],7),flush=True);assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
    (out/'soak.json').write_text(json.dumps({'source_sha256':sha,'rows':rows,'errors':errors},indent=2)+'\n')
 assert not errors,errors;b.close()
print('PASS 30 matched two-year service histories, workforce overlap checks and currency conservation')
