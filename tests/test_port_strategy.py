"""Matched starts, actual route controls, ordinary demand; retain port losses."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();rows=[]
probe="window.__portStrategy=()=>({day:G.day,total:totalMoney(),valid:validateTown(),goodsError:Math.max(...goodsBalance().map(g=>Math.abs(g.error))),docks:G.firms.filter(f=>f.kind==='wharf').map(f=>({id:f.id,closed:!!f.closed,cash:f.cash,cargo:f.cargoToday||0,fees:f.handlingFees||0,expenses:f.expenses||0,net:f.netProfit||0})),waterFees:G.waterway?.fees||0,delivered:G.regionalTrade?.delivered||0});"
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for seed in [42,101]:
  for mode in ['interchange','river']:
   p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#townSeed').fill(str(seed));p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');p.locator('[data-panel=economy]').click();p.locator('#logisticsOffice').evaluate('e=>e.open=true');p.locator('[data-logistics-routing='+mode+']').click();initial=p.evaluate('__portStrategy()');samples=[]
   for _ in range(6):
    p.evaluate('__townTest.step(30)');s=p.evaluate('__portStrategy()');assert s['valid']['ok']and s['goodsError']<.001 and abs(s['total']-initial['total'])<.001,s;samples.append(s)
   assert not errors,errors;rows.append({'seed':seed,'mode':mode,'samples':samples,'errors':errors});p.close()
 b.close()
(ROOT/'reports/port-freight').mkdir(exist_ok=True);(ROOT/'reports/port-freight/strategies.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'actualControls':True,'ordinaryDemandNoGrants':True,'rows':rows},indent=2));print('PASS actual routing choices, four six-month histories; negative outcomes retained',[(r['seed'],r['mode'],r['samples'][-1]['docks'])for r in rows])
