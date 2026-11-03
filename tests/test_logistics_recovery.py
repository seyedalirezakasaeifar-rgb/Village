"""Paid peak-arrival fixture; actual mayor choices followed by active recovery."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
probe=r'''
window.__queueFixture=()=>{__townTest.reset('settlement',42);G.autoBuild=false;const s=ensureRegionalTrade();s.routePreference='interchange';const warehouse=G.firms.find(f=>f.kind==='warehouse'),grocer=G.firms.find(f=>f.kind==='grocer'),market=OUTSIDE_MARKETS[0],total=totalMoney();for(let day=0;day<4;day++){if(day)G.day++;for(let i=0;i<4;i++)dispatchRegional(warehouse,'stone',120,'import',regionalQuote(warehouse,market,'stone','import'));}dispatchRegional(grocer,'food',60,'import',regionalQuote(grocer,market,'food','import'));const food=s.shipments.at(-1);G.day+=6;regionalFreightDay();return{food:food.id,total,day:G.day,queue:s.shipments.filter(o=>o.stage==='unloading').length,warehouse:warehouse.id};};
window.__queueSample=id=>{const s=ensureRegionalTrade();return{day:G.day,active:s.shipments.length,queued:s.shipments.filter(o=>['loading','unloading'].includes(o.stage)).length,foodArrived:s.recent.some(o=>o.id===id&&o.status==='Delivered'),support:G.cumulative.logisticsSupport||0,total:totalMoney(),unmet:G.market.unmetFood||0,food:G.market.consumedFood||0,employment:G.stats.employment,hardship:G.stats.hardship,treasury:G.treasury,claims:s.claims.length,valid:validateTown()}};
'''
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390},has_touch=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();fixture=p.evaluate('__queueFixture()');assert fixture['queue']>=5,fixture;snapshot=p.evaluate('__townTest.save()')
 for mode in ['balanced','essentials','relief']:
  assert p.evaluate('s=>__townTest.load(s)',snapshot);p.keyboard.press('Escape');p.locator('[data-panel=economy]').click();p.locator('#logisticsOffice>summary').click()
  if mode=='essentials':p.locator('[data-logistics-priority=essentials]').click()
  if mode=='relief':p.locator('#logisticsRelief').click();p.locator('[data-event-choice="0"]').click()
  p.keyboard.press('Escape');arrival=None;samples=[]
  for day in range(12):
   p.evaluate('__townTest.step(1)');r=p.evaluate('id=>__queueSample(id)',fixture['food']);assert r['valid']['ok'] and abs(r['total']-fixture['total'])<.001,r;samples.append(r)
   if r['foodArrived'] and arrival is None:arrival=r['day']
  assert arrival is not None,(mode,samples);rows.append({'mode':mode,'arrivalDay':arrival,'samples':samples})
 assert rows[1]['arrivalDay']<rows[0]['arrivalDay'],[(r['mode'],r['arrivalDay']) for r in rows]
 assert rows[2]['arrivalDay']<=rows[0]['arrivalDay'];assert rows[2]['samples'][-1]['support']>0
 # Continue the intervention branch, stop contingent spending, and restore
 # automatic depot routing; inspect actual accounts between monthly advances.
 p.locator('[data-panel=economy]').click();p.locator('#logisticsOffice>summary').click();p.locator('#logisticsReliefStop').click();p.locator('#logisticsOffice>summary').click();p.locator('[data-logistics-routing=automatic]').click();p.keyboard.press('Escape');long=[]
 for month in range(6):
  p.evaluate('__townTest.step(30)');p.locator('[data-panel=economy]').click();assert 'Panel error' not in p.locator('#panelBody').inner_text();p.keyboard.press('Escape');r=p.evaluate('id=>__queueSample(id)',fixture['food']);assert r['valid']['ok'] and abs(r['total']-fixture['total'])<.001,r;long.append(r)
 saved=p.evaluate('__townTest.save()');assert p.evaluate('s=>__townTest.load(s)',saved);assert not errors,errors;b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-8.0';(out/'logistics-recovery.json').write_text(json.dumps({'source_sha256':sha,'controlledPaidPeak':True,'fixture':fixture,'comparisons':rows,'sixMonthFollowup':long,'errors':errors},indent=2)+'\n');print('PASS actual priority/extra-shift choices, paid arrival backlog and six-month followup',[(r['mode'],r['arrivalDay']) for r in rows],long[-1])
