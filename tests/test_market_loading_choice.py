"""Existing paid queue: budget choice, no extra household purchases."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,json,hashlib
source=(ROOT/'assets/game.js').read_text();tree=ast.parse((ROOT/'tests/test_logistics_recovery.py').read_text());fixture=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='probe'for t in n.targets))
extra=r'''
window.__marketChoice={limited:()=>{G.region+=G.treasury-.72;G.treasury=.72;const r=authorizeMarketLoadingChoice(reviewMarketLoadingChoice());G.day++;regionalFreightDay();return {ok:r.ok,support:G.cumulative.logisticsSupport||0,queued:G.regionalTrade.shipments.filter(o=>['loading','unloading'].includes(o.stage)).length};},open:()=>{const site=publicPlaceOffer();if(!site)throw Error('No square site');construct('square',site.x,site.y);openCivicGatheringReview(buildingAt(site.x,site.y).id);},review:()=>{window.__loadingQuote=reviewMarketLoadingChoice();return {ok:__loadingQuote.ok,reason:__loadingQuote.reason,summary:__loadingQuote.summary};},authorize:()=>authorizeMarketLoadingChoice(__loadingQuote),state:()=>({support:G.cumulative.logisticsSupport||0,until:G.regionalTrade.reliefUntil,householdPurchases:G.households.map(h=>[h.food,h.discretionary]),cash:totalMoney(),treasury:G.treasury,day:G.day}),stale:()=>{G.policy.roadBudget++},poor:()=>{G.region+=G.treasury;G.treasury=0},stop:()=>{G.regionalTrade.reliefUntil=0},sample:()=>({goods:goodsBalance(),valid:validateTown()})};
'''
out=ROOT/'reports/market-loading-choice';out.mkdir(exist_ok=True);rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_default_timeout(120000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',fixture+extra+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();assert not p.evaluate('__marketChoice.review().ok');f=p.evaluate('__queueFixture()');save=p.evaluate('__townTest.save()')
 for mode in ['balanced','relief','stop','poor','stale']:
  assert p.evaluate('s=>__townTest.load(s)',save);q=p.evaluate('__marketChoice.review()');assert q['ok'],q;before=p.evaluate('__marketChoice.state()')
  if mode=='stale':p.evaluate('__marketChoice.stale()');assert not p.evaluate('__marketChoice.authorize().ok');continue
  if mode=='poor':p.evaluate('__marketChoice.poor()');assert not p.evaluate('__marketChoice.review().ok');continue
  if mode!='balanced':
   assert p.evaluate('__marketChoice.authorize().ok');after=p.evaluate('__marketChoice.state()');assert before['cash']==after['cash']and before['treasury']==after['treasury']and before['householdPurchases']==after['householdPurchases'];assert not p.evaluate('__marketChoice.authorize().ok')
  if mode=='stop':p.evaluate('__marketChoice.stop()')
  arrival=None
  for day in range(12):
   p.evaluate('__townTest.step(1)');r=p.evaluate('id=>__queueSample(id)',f['food']);assert r['valid']['ok']and abs(r['total']-f['total'])<.001
   if r['foodArrived']and arrival is None:arrival=r['day']
  row={'mode':mode,'arrival':arrival,'state':p.evaluate('__marketChoice.state()')};rows.append(row);assert arrival is not None
  check=p.evaluate('__townTest.save()');p.evaluate('__townTest.step(10)');nextSave=p.evaluate('__townTest.save()');assert p.evaluate('s=>__townTest.load(s)',check);p.evaluate('__townTest.step(10)');assert p.evaluate('__townTest.save()')==nextSave;assert max(abs(x['error'])for x in p.evaluate('__townTest.goods()'))<.001
 assert p.evaluate('s=>__townTest.load(s)',save);limited=p.evaluate('__marketChoice.limited()');assert limited['ok']and limited['support']<=.720001 and limited['queued']>0;assert p.evaluate('s=>__townTest.load(s)',save);p.evaluate('__marketChoice.open()');assert 'Instead: prioritize essentials' in p.locator('[data-event-choice="1"]').inner_text();p.locator('[data-event-choice="1"]').click();assert p.evaluate('__marketChoice.state().until>__townTest.get().day');assert p.evaluate('s=>__townTest.load(s)',save);p.evaluate('__marketChoice.open()');p.locator('[data-event-choice="2"]').click();assert p.evaluate('__marketChoice.state().until')==0;rows.append({'mode':'limited','result':limited})
 assert rows[1]['arrival']<rows[0]['arrival'];assert rows[1]['state']['support']>0 and rows[2]['state']['support']==0;assert not errors;b.close()
(out/'results.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledPaidPeakFixture':True,'rows':rows,'errors':errors},indent=2));print('PASS actual funded relief, priority opportunity cost, no upfront purchases, stale/poor/repeat rejection, stop, conservation and replay')
