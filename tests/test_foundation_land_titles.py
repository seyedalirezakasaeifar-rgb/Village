"""Founding waterfront roads never overwrite crop title; cold hydration is lossless."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.decode());p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('''()=>{const rows=[];for(const scenario of ['settlement','regional','hardtimes','frontier','industrial'])for(const seed of [1,7,42,123]){__townTest.reset(scenario,seed);for(const days of [0,150]){if(days)__townTest.step(days);const raw=__townTest.save(),g=JSON.parse(raw),before={landUse:g.landUse,fieldOwner:g.fieldOwner,fieldCount:g.fieldCount},valid=__townTest.validate();if(!valid.ok)throw Error(JSON.stringify({scenario,seed,days,issues:valid.issues}));if(!__townTest.load(raw))throw Error('Valid town rejected');const after=JSON.parse(__townTest.save());for(const k of Object.keys(before))if(JSON.stringify(before[k])!==JSON.stringify(after[k]))throw Error('Hydration changed '+scenario+'/'+seed+'/'+days+'/'+k);rows.push({scenario,seed,day:g.day,cropTiles:Object.values(g.landUse).filter(v=>v===1).length});}}return rows;}''');b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-persistence';out.mkdir(exist_ok=True);(out/'land-titles.json').write_text(json.dumps({'source_sha256':sha,'cases':result},indent=2)+'\n');print('PASS',len(result),'founding/150-day title/count round trips across five scenarios and four seeds')
