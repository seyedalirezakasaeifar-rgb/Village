"""Compensated commodity entries retain tiny paid quantities and validated carry."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
script=source.decode().replace('// SOURCE: 99-instrumentation.js',r'''
window.__goodsPrecision=()=>{const original=G;try{G=JSON.parse(JSON.stringify(original));G.goodsAccounts.grain.imports=1e9;G.goodsCompensation={};let naive=1e9;for(let i=0;i<1000000;i++){goodsEntry('grain','imports',.1);naive+=.1;}const expected=1e9+100000;return {naiveError:naive-expected,compensatedError:G.goodsAccounts.grain.imports-expected,carry:G.goodsCompensation.grain.imports,valid:validateGoodsAccounting(G)};}finally{G=original;}};
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("settlement",42)');raw=p.evaluate('__townTest.save()');r=p.evaluate('__goodsPrecision()');assert abs(r['naiveError'])>.01 and r['compensatedError']==0 and r['valid'],r;assert p.evaluate('__townTest.save()')==raw;p.evaluate('__townTest.step(120)');raw=p.evaluate('__townTest.save()');assert p.evaluate('s=>__townTest.load(s)',raw)
 for change in ['g.goodsCompensation.grain.imports=1','g.goodsCompensation.grain.bad=0','g.goodsCompensation={missing:{imports:0}}','g.goodsAccounts.food.produced=-1']:
  assert p.evaluate('''code=>{const before=__townTest.save(),g=JSON.parse(before);new Function('g',code)(g);return !__townTest.load(g)&&__townTest.save()===before;}''',change),change
 assert p.evaluate('''()=>{const g=JSON.parse(__townTest.save());delete g.goodsCompensation;return __townTest.load(g)&&__townTest.validate().ok;}''');b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-ledger-precision';out.mkdir(exist_ok=True);(out/'precision.json').write_text(json.dumps({'source_sha256':sha,**r,'atomicInvalidCarryRejection':True,'legacyWithoutCarry':True},indent=2)+'\n');print('PASS million tiny quantities, analytical sum, finite roundoff bounds, exact archive, atomic invalid carry/counter rejection and legacy migration',r)
