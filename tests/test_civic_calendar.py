"""Actual square/preparation controls, local participation and bounded render cues."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_text();probe='''
let gatheringTestQuote;
window.__gatherTest={quote:(venue,start)=>{gatheringTestQuote=reviewCivicGathering({venue,start});return {ok:gatheringTestQuote.ok,cost:gatheringTestQuote.cost,eligible:gatheringTestQuote.eligible};},badCapacity:()=>{gatheringTestQuote.capacity++;return authorizeCivicGathering(gatheringTestQuote);},authorize:()=>authorizeCivicGathering(gatheringTestQuote),day:civicGatheringDay,cues:civicGatheringCues,
 poor:()=>{G.region+=G.treasury;G.treasury=0;},pixel:(phase)=>{const previous=acc;try{acc=phase;const canvas=document.createElement('canvas');canvas.width=200;canvas.height=200;const g=canvas.getContext('2d');paintCivicGathering(g,{x:100,y:100},civicGatheringCues()[0]);return canvas.toDataURL();}finally{acc=previous;}}
};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_default_timeout(10000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.step(2)')
 state=lambda:p.evaluate('JSON.parse(__townTest.save())')
 def board():
  p.keyboard.press('Escape');p.locator('[data-panel=overview]').click();p.locator('[data-civic-projects]').click();p.locator('#civicCalendar').evaluate('e=>e.open=true')
 def confirm():p.locator('[data-event-choice="0"]').click()
 board();p.locator('[data-public-place=square]').click();p.locator('#publicPlaceName').fill('Willow Commons');confirm();venue=state()['publicPlaces']['places'][0]['building'];base=p.evaluate('__townTest.save()');initial=p.evaluate('__townTest.get().total');day=state()['day']
 board();p.locator('[data-gathering-review="'+str(venue)+'"]').click();p.keyboard.press('Escape');assert state().get('civicCalendar')is None
 # Actual review pays once and preserves all total cash/goods.
 q=p.evaluate('v=>__gatherTest.quote(v,__townTest.get().day+1)',venue);before=state()['treasury'];p.locator('[data-gathering-review="'+str(venue)+'"]').click();confirm();event=state()['civicCalendar']['events'][0];assert before-state()['treasury']==q['cost'];assert event['paid']==event['cost'];assert not p.evaluate('__gatherTest.authorize().ok');assert abs(p.evaluate('__townTest.get().total')-initial)<.001
 board();p.locator('[data-gathering-review="'+str(venue)+'"]').click();assert int(p.locator('#gatheringStart').input_value())==day+3;p.keyboard.press('Escape')
 # Opening daily participation is informational; no extra jobs/trips/payments.
 p.evaluate('__townTest.step(1)');active=state()['civicCalendar']['events'][0];assert active['status']=='active' and active['daily'];assert active['daily'][0]['attendance']<=active['capacity'];assert active['participants'];saved=p.evaluate('__townTest.save()');p.evaluate('__gatherTest.day()');assert p.evaluate('__townTest.save()')==saved
 pixels=p.evaluate('[__gatherTest.pixel(.1),__gatherTest.pixel(.8),__gatherTest.pixel(.1)]');assert pixels[0]!=pixels[1]and pixels[0]==pixels[2];assert p.evaluate('__townTest.save()')==saved
 board();p.locator('[data-gathering-visit]').click();assert p.evaluate('__gatherTest.cues().length')==1;out=ROOT/'reports/civic-calendar';out.mkdir(parents=True,exist_ok=True);p.screenshot(path=str(out/'willow-commons-active.png'))
 checkpoint=p.evaluate('__townTest.save()');p.evaluate('__townTest.step(3)');expected=state()['civicCalendar'];assert expected['events'][0]['status']=='complete';assert p.evaluate('s=>__townTest.load(s)',checkpoint);p.evaluate('__townTest.step(3)');assert state()['civicCalendar']==expected;assert p.evaluate('__townTest.validate().ok')
 for mutation in ['g.civicCalendar.events[0].paid=-1','g.civicCalendar.events[0].daily[0].attendance=9999','g.civicCalendar.events[0].participants=[999999]']:
  assert p.evaluate('code=>{let g=JSON.parse(__townTest.save());new Function("g",code)(g);return !__townTest.load(JSON.stringify(g));}',mutation)
 # Restore pre-party state for independent funding/stale/cancellation checks.
 assert p.evaluate('s=>__townTest.load(s)',base);p.evaluate('v=>__gatherTest.quote(v,__townTest.get().day+1)',venue);capacity_state=p.evaluate('__townTest.save()');assert not p.evaluate('__gatherTest.badCapacity().ok');assert p.evaluate('__townTest.save()')==capacity_state;p.evaluate('__gatherTest.poor()');p.evaluate('v=>__gatherTest.quote(v,__townTest.get().day+1)',venue);empty=p.evaluate('__townTest.save()');assert not p.evaluate('__gatherTest.authorize().ok');assert p.evaluate('__townTest.save()')==empty
 assert p.evaluate('s=>__townTest.load(s)',base);p.evaluate('v=>__gatherTest.quote(v,__townTest.get().day+1)',venue);p.evaluate('__townTest.step(1)');stale=p.evaluate('__townTest.save()');assert not p.evaluate('__gatherTest.authorize().ok');assert p.evaluate('__townTest.save()')==stale
 board();p.locator('[data-gathering-review="'+str(venue)+'"]').click();confirm();cash=state()['treasury'];p.locator('[data-gathering-cancel]').click();p.keyboard.press('Escape');assert state()['civicCalendar']['events'][0]['status']=='scheduled';p.locator('[data-gathering-cancel]').click();confirm();assert state()['treasury']==cash and state()['civicCalendar']['events'][0]['status']=='cancelled'
 assert abs(p.evaluate('__townTest.get().total')-initial)<.001;assert not errors,errors;(out/'controls.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'quotedPreparation':q,'actualActiveEvent':active,'completedEvent':expected,'cancelRetainsPreparation':True,'failedFundingAndStaleNoMutation':True,'pausedPixelsStableAndActiveAnimation':True,'errors':errors},indent=2)+'\n');b.close()
print('PASS actual named square, reviewed once-only conserved preparation, real local eligibility/participation, animated bounded cue, cancellation/funding/stale rejection, exact replay and malformed archives')
