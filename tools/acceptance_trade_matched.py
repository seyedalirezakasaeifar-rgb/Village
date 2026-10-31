#!/usr/bin/env python3
"""Actual forecast-sized food contract versus retaining stock, from the same save."""
from pathlib import Path
import hashlib,json,sys,subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
PROBE=r'''window.__tradeAcceptance=()=>({day:G.day,population:G.stats.population,hardship:G.stats.hardship,treasury:G.treasury,region:G.region,total:totalMoney(),goods:goodsBalance(),firmFood:G.firms.reduce((n,f)=>n+(f.stock.food||0),0),firmCash:G.firms.reduce((n,f)=>n+f.cash,0),householdFoodSpending:G.households.reduce((n,h)=>n+(h.food||0),0),trade:JSON.parse(JSON.stringify(G.regionalTrade)),cumulative:{...G.cumulative},valid:validateTown()});'''
def main():
 source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest();result={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':sha,'method':'Normal seed42 cities, first25 days. Both arms restore the identical archive before choosing either no new commitment or the actual forecast-sized food offer in the exchange UI. Continue35 days. Automatic local/regional trade continues in both. Finite external cash and real goods ledger retained. This is a small contract comparison, not an export-led whole-economy claim.','rows':[]};out=ROOT/'reports/trade-matched';out.mkdir(parents=True,exist_ok=True)
 with sync_playwright()as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page();p.set_default_timeout(120000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.decode().replace('// SOURCE: 99-instrumentation.js',PROBE+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
  for scenario in ['settlement','regional']:
   p.evaluate('s=>{__townTest.reset(s,42);__townTest.step(25)}',scenario);save=p.evaluate('__townTest.save()')
   for strategy in ['retain-stock','forecast-contract']:
    assert p.evaluate('s=>__townTest.load(s)',save)
    row={'scenario':scenario,'seed':42,'strategy':strategy,'starting_save_sha256':hashlib.sha256(save.encode()).hexdigest(),'before':p.evaluate('__tradeAcceptance()')};result['rows'].append(row)
    if strategy=='forecast-contract':
     p.keyboard.press('Escape');p.locator('[data-panel=economy]').click();p.locator('#supplierMarket').evaluate("e=>{for(let p=e;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true}");p.locator('#supplierMarket').select_option('port');p.locator('#supplierGood').evaluate("e=>{for(let p=e;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true}");p.locator('#supplierGood').select_option('food');p.locator('#alternativeSuppliers').evaluate("e=>{for(let p=e;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true}");row['offer']=p.locator('#alternativeSuppliers').inner_text();button=p.locator('#alternativeSuppliers [data-trade-offer]')
     if button.count()and button.is_enabled():
      button.click();row['review']=p.locator('#eventText').inner_text();p.locator('[data-event-choice="0"]').click();row['commitment']=p.evaluate('__tradeAcceptance().trade.contracts.slice(-1)[0]')
     else:row['unavailable']='No enabled real food offer; no inventory or opportunity fabricated'
    p.evaluate('__townTest.step(35)');row['after']=p.evaluate('__tradeAcceptance()');(out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    assert row['after']['valid']['ok'] and abs(row['after']['total']-row['before']['total'])<.01
    assert max(abs(x['error'])for x in row['after']['goods'])<.01
    if row.get('commitment'):
     row['settled']=next(c for c in row['after']['trade']['contracts']if c['id']==row['commitment']['id']);assert row['settled']['status']=='fulfilled',row['settled']
    print(scenario,strategy,'population',row['after']['population'],'hardship',row['after']['hardship'],'contract',row.get('settled',{}).get('status',row.get('unavailable','none')),flush=True)
  result['pageErrors']=errors;(out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');b.close()
 assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha and not errors
if __name__=='__main__':main()
