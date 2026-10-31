from pathlib import Path
from playwright.sync_api import sync_playwright
import json,time,hashlib
R=Path(__file__).resolve().parents[1];out={'source_sha256':hashlib.sha256((R/'assets/game.js').read_bytes()).hexdigest()}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390},has_touch=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto((R/'assets/index.html').as_uri());p.locator('#newTown').click();p.locator('#pause').click()
 # Damaged 6.0 town, not a fresh prosperous town.
 save=(R/'tests/fixtures/v60-distressed-town.json').read_text();assert p.evaluate('s=>__townTest.load(s)',save)
 before=p.evaluate('__townTest.get()');p.evaluate('__townTest.step(720)');after=p.evaluate('__townTest.get()');v=p.evaluate('__townTest.validate()');assert v['ok'],v;assert after['employment']>70 and after['businesses']>20;assert abs(after['total']-before['total'])<.05
 out['legacy_depression_recovery']={'before':{k:before[k] for k in ['employment','businesses','regional']},'after720days':{k:after[k] for k in ['employment','businesses','regional']},'cashDrift':after['total']-before['total'],'banks':p.evaluate('__townTest.finance().banks.filter(b=>!b.closed).length')}
 # Nine historic failures can no longer permanently bar all bank market entry.
 out['bank_reentry']=p.evaluate('''()=>{__townTest.reset('settlement',42);const g=JSON.parse(__townTest.save());for(let i=3;i<9;i++)g.banks.push({...g.banks[0],id:i,cash:0,closed:true});if(!__townTest.load(JSON.stringify(g)))throw Error('fixture rejected');for(const b of __townTest.finance().banks)if(!b.closed)__townTest.bankFailure(b.id);__townTest.step(360);const f=__townTest.finance();if(f.banks.filter(b=>!b.closed).length<2)throw Error('Bank reentry blocked by history');return {historicalSlots:f.banks.length,active:f.banks.filter(b=>!b.closed).length,valid:__townTest.validate()};}''')
 # Historical loan count cannot make operating expenses grow without bound.
 out['bounded_bank_cost']=p.evaluate('''()=>{__townTest.reset('settlement',42);const g=JSON.parse(__townTest.save());for(const b of g.banks)b.loansOriginated=500000;__townTest.load(JSON.stringify(g));__townTest.step(360);const f=__townTest.finance();if(f.indicators.failures)throw Error('Historical loan counter bank failure');return {failures:f.indicators.failures,active:f.banks.filter(b=>!b.closed).length,cashDrift:__townTest.get().total-g.accounts.baseline};}''')
 # Climate, presentation and mobile settings persist without triggering extra economic days.
 p.locator('[data-panel=settings]').click();day=p.evaluate('__townTest.get().day');assert p.locator('[data-option=seasons]').get_attribute('aria-pressed')=='false';p.locator('[data-option=seasons]').click();assert p.evaluate('JSON.parse(__townTest.save()).climateSeasons')
 p.locator('[data-option=seasons]').click();p.locator('[data-option=largeText]').click();p.locator('[data-preference=quality]').select_option('low');p.locator('[data-option=traffic]').click();assert p.evaluate('__townTest.get().day')==day
 p.screenshot(path=str(R/'reports/v6.1/mobile-settings.png'));p.reload();p.locator('#continue').click();p.locator('#pause').click();p.locator('[data-panel=settings]').click();assert p.locator('[data-option=largeText]').get_attribute('aria-pressed')=='true';assert p.locator('[data-option=traffic]').get_attribute('aria-pressed')=='false';assert p.locator('[data-preference=quality]').input_value()=='low';out['settings']={'persistent':True,'climateSaved':True,'noUnpausedDays':True}
 p.locator('[data-option=largeText]').click();p.locator('[data-option=traffic]').click();p.locator('[data-preference=quality]').select_option('balanced');p.locator('#panelClose').click();
 # Turning tangent must change, and vehicle shape must use heading.
 p.locator('#pause').click();p.wait_for_timeout(4000);p.locator('#pause').click();out['traffic']=p.evaluate('__townTest.traffic()');assert out['traffic'];assert len({round(v['position']['dx'],2) for v in out['traffic']})>1
 assert not errors,errors;out['pageErrors']=errors
 (R/'reports/v6.1/regressions.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='traffic'},indent=2));b.close()
