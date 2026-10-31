"""A real policy recession and a funded, lower-cost recovery from the same town."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os,json
R=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox']);p=b.new_page();p.goto((R/'assets/index.html').as_uri());p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click()
 result=p.evaluate('''()=>{
  __townTest.reset('settlement',101);__townTest.step(360);const start=__townTest.get();
  __townTest.set('minWage',80);__townTest.set('profitTax',35);__townTest.step(1080);
  const recession=__townTest.get(),saved=__townTest.save(),before=recession.total;
  __townTest.step(1080);const unchanged=__townTest.get();
  if(!__townTest.load(saved))throw Error('Recession save rejected');
  __townTest.set('minWage',28);__townTest.set('profitTax',12);__townTest.set('permitFee',0);__townTest.set('aidBudget',300);__townTest.set('zoningRestriction',15);
  __townTest.step(1080);const recovery=__townTest.get(),v=__townTest.validate();if(!v.ok)throw Error(v.issues.join(';'));
  if(Math.abs(before-recovery.total)>.05)throw Error('Recovery created cash');
  return {start:{population:start.population,employment:start.employment,firms:start.businesses},recession:{population:recession.population,employment:recession.employment,firms:recession.businesses},unchanged:{population:unchanged.population,employment:unchanged.employment,firms:unchanged.businesses},recovery:{population:recovery.population,employment:recovery.employment,firms:recovery.businesses,hardship:recovery.hardship},cashDelta:recovery.total-before};
 }''')
 assert result['recovery']['employment']>result['unchanged']['employment'] or result['recovery']['firms']>result['unchanged']['firms'],result
 (R/'reports/final/recovery.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',json.dumps(result),flush=True);b.close()
