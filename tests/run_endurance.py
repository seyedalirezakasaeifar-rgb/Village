from pathlib import Path
from playwright.sync_api import sync_playwright
import json,os,sys,time,hashlib
R=Path(__file__).resolve().parents[1];out=R/'reports/final';sc,seed,years,zone=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])
source_digest=hashlib.sha256((R/'assets/game.js').read_bytes()).hexdigest()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page();p.goto((R/'assets/index.html').as_uri());p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('o=>{__townTest.reset(o.sc,o.seed);__townTest.set("zoningRestriction",o.zone)}',{'sc':sc,'seed':seed,'zone':zone});total=p.evaluate('__townTest.get().total');start=time.perf_counter()
 for year in range(0,years,5):
  value=p.evaluate('''()=>{__townTest.step(1800);let g=JSON.parse(__townTest.save()),v=__townTest.validate();if(!v.ok)throw Error(v.issues.join(';'));return {day:g.day,population:g.stats.population,homes:g.development.homes,redevelopments:g.development.redevelopments,towers:g.development.towers,airfields:g.development.airfields,stations:g.development.stations,openFirms:g.stats.businesses,failures:g.finance.failures,total:v.total,peakDrift:g.accounts.maxError}}''');assert abs(value['total']-total)<.1
  (out/(sc+'-endurance-town.json')).write_text(p.evaluate('__townTest.save()'));print(sc,year+5,value['population'],flush=True)
 assert hashlib.sha256((R/'assets/game.js').read_bytes()).hexdigest()==source_digest,'Source changed while test ran'
 value.update(scenario=sc,seed=seed,years=years,seconds=time.perf_counter()-start,source_sha256=source_digest);(out/(sc+'-endurance-result.json')).write_text(json.dumps(value,indent=2));b.close();print('PASS',sc,years,flush=True)
