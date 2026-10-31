"""Matched physical economy with naive versus compensated commodity counters."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib,json,os,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'));from test_mobile_rendering import html
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest();days=int(os.environ.get('TOWNLEDGER_PRECISION_DAYS','25166'));start=source.index('function goodsEntry(');end=source.index('function expectedCommodityStock(',start);naive=source[:start]+"function goodsEntry(good,category,qty){if(!(qty>0)||!G.goodsAccounts?.[good])return;G.goodsAccounts[good][category]+=qty;}\n"+source[end:];out=ROOT/'reports/development-ledger-precision';out.mkdir(exist_ok=True);results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for name,script in [('naive',naive),('compensated',source)]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("regional",42)')
  for district in ['river-reach','east-meadow']:
   p.locator('[data-panel=construction]').click();p.locator('#charterOffice>summary').click();p.locator('[data-parcel-buy='+district+']').click();p.locator('[data-event-choice="0"]').click();p.locator('#panelClose').click()
  t=time.monotonic();p.evaluate('n=>__townTest.step(n)',days);g=json.loads(p.evaluate('__townTest.save()'));goods=p.evaluate('__townTest.goods()');physical={k:g[k] for k in ['day','people','households','firms','treasury','region','loans','banks','tiles','goodsPrices','rngState']};fingerprint=hashlib.sha256(json.dumps(physical,separators=(',',':')).encode()).hexdigest();r={'kind':name,'source_sha256':sha,'evaluated_source_sha256':hashlib.sha256(script.encode()).hexdigest(),'day':g['day'],'population':g['stats']['population'],'seconds':time.monotonic()-t,'physical_sha256':fingerprint,'maxGoodsError':max(abs(x['error']) for x in goods),'goods':goods};results.append(r);(out/'long-comparison.json').write_text(json.dumps({'source_sha256':sha,'runs':results},indent=2)+'\n');print(name,r['day'],r['maxGoodsError'],fingerprint,flush=True);p.close()
 b.close()
assert results[0]['physical_sha256']==results[1]['physical_sha256'],'Numerical ledger changed physical economy'
assert results[1]['maxGoodsError']<.001 and results[1]['maxGoodsError']<results[0]['maxGoodsError']*.01,results
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
print('PASS identical physical economy, at least 100x lower commodity-ledger residual')
