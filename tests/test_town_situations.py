"""Place routes use actual controls; snapshots grant nothing and keep negative outcomes."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_default_timeout(10000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source);p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.step(2)')
 state=lambda:p.evaluate('JSON.parse(__townTest.save())')
 def board():
  p.keyboard.press('Escape');p.locator('[data-panel=overview]').click();p.locator('[data-civic-projects]').click()
 board();s=state();print(p.locator('#townSituations').inner_text(),flush=True)
 button=p.locator('[data-situation-choice=retain]');button.evaluate('e=>e.closest("details").open=true');before=state()['treasury'];button.click();p.keyboard.press('Escape');assert state().get('townSituations')is None
 button.evaluate('e=>e.closest("details").open=true');button.click();p.locator('[data-event-choice="0"]').click();assert state()['treasury']==before;assert 'PROPERTY REPORT' in p.locator('#panelBody').inner_text()
 board();p.locator('[data-situation-observe]').click();assert len(state()['townSituations']['active'][0]['observations'])==1;p.locator('[data-situation-observe]').click();assert len(state()['townSituations']['active'][0]['observations'])==1
 p.locator('[data-situation-close]').click();p.keyboard.press('Escape');assert state()['townSituations']['active'];p.locator('[data-situation-close]').click();p.locator('[data-event-choice="0"]').click();assert len(state()['townSituations']['history'])==1
 n=p.locator('[data-situation-choice=bus]');n.evaluate('e=>e.closest("details").open=true');n.click();p.locator('[data-event-choice="0"]').click();assert p.locator('.transit-office').count()==1
 p.evaluate('__townTest.step(8)');board();p.locator('[data-situation-observe]').click();a=state()['townSituations']['active'][0];assert a['observations'][-1]['school']<60,'An unbuilt bus must not fabricate teaching';assert 'not proof' in p.locator('#townSituations').inner_text()
 # Paid food and a real supplier promise create a competing freight situation.
 p.locator('[data-civic-project-review=food]').click();p.locator('[data-event-choice="0"]').click();p.locator('[data-civic-project-order]').click();p.locator('[data-event-choice="0"]').click();p.keyboard.press('Escape');p.locator('[data-panel=economy]').click();p.locator('[data-trade-offer]:not([disabled])').first.click();p.locator('[data-event-choice="0"]').click();p.evaluate('__townTest.step(1)');board()
 freight=p.locator('[data-situation-choice=relief]');freight.evaluate('e=>e.closest("details").open=true');freight.click();p.locator('[data-event-choice="0"]').click();assert p.locator('#eventDialog').is_visible();p.keyboard.press('Escape');assert state()['regionalTrade']['reliefUntil']<state()['day']
 board();p.locator('[data-situation-act]').last.click();p.locator('[data-event-choice="0"]').click();assert state()['regionalTrade']['reliefUntil']==state()['day']+30
 board();p.screenshot(path=str(ROOT/'reports/town-situations-places.png'))
 snap=p.evaluate('__townTest.save()');p.evaluate('__townTest.step(3)');expected=state();assert p.evaluate('s=>__townTest.load(s)',snap);p.evaluate('__townTest.step(3)');assert state()['treasury']==expected['treasury'];assert state()['townSituations']==expected['townSituations']
 for mutation in ['g.townSituations.active[0].firm=1.5','g.townSituations.active[0].baseline.treasury=Infinity','g.townSituations.active[0].choice="freecash"']:
  assert p.evaluate('code=>{let g=JSON.parse(__townTest.save());new Function("g",code)(g);return !__townTest.load(JSON.stringify(g))}',mutation)
 legacy=state();legacy.pop('townSituations');assert p.evaluate('g=>__townTest.load(JSON.stringify(g))',legacy);assert not errors,errors
 out=ROOT/'reports/town-situations';out.mkdir(parents=True,exist_ok=True);(out/'controls.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'recordedUnsuccessfulRoute':a,'errors':errors},indent=2)+'\n');b.close()
print('PASS actual place selection, route/cancel/no purchase, actual office, dated negative outcome, repeated observation guard, close/cancel/history, replay and malformed/legacy archives')
