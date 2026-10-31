"""Corrupt the latest autosave; a fresh app session must recover its predecessor."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os,json
R=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox'])
 c=b.new_context();c.add_init_script("Object.defineProperty(window,'indexedDB',{value:null})");p=c.new_page();p.goto((R/'assets/index.html').as_uri());p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click()
 data=p.evaluate('''()=>{__townTest.step(40);__townArchive.suspend();const before=__townTest.get();__townTest.step(20);__townArchive.suspend();const primary=JSON.parse(localStorage.getItem('townledger-v6')),backup=JSON.parse(localStorage.getItem('townledger-v6-backup'));if(JSON.parse(primary.payload).day!==61||JSON.parse(backup.payload).day!==41)throw Error('Unexpected save versions');localStorage.setItem('townledger-v6',JSON.stringify({checksum:'bad',payload:primary.payload}));return {expectedDay:41,expectedTotal:before.total,duplicateLegacy:!!localStorage.getItem('townledger-village-founder-3')};}''')
 assert not data['duplicateLegacy']
 p.close(run_before_unload=False)
 p=c.new_page();p.goto((R/'assets/index.html').as_uri())
 # Closing a page can flush a valid save; corrupt after that flush, before Continue reads it.
 p.evaluate("localStorage.setItem('townledger-v6',JSON.stringify({checksum:'bad',payload:'broken on disk'}))")
 p.locator('#continue').click()
 actual=p.evaluate('__townTest.get()');assert actual['day']==41,(actual['day'],data)
 assert abs(actual['total']-data['expectedTotal'])<.0001
 assert p.evaluate('__townTest.validate().ok')
 result={'corruptPrimaryRejected':True,'previousAutosaveRecovered':True,'recoveredDay':41,'cashRetained':True,'redundantLegacyRemoved':True}
 (R/'reports/final/save-storage.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',result,flush=True);b.close()
