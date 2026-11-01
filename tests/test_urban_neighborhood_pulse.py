"""Resident work flows and 90-day neighbourhood activity stay factual/read-only."""
from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html

source=(ROOT/'assets/game.js').read_text()
probe=r'''window.__neighborhoodPulse={
 seed:days=>{__townTest.reset('settlement',42);if(days)__townTest.step(days);const b=Object.values(urbanSpatial().blocks).find(v=>v.households.length);return {day:G.day,key:b?.key||null,block:b,history:JSON.parse(JSON.stringify(G.urban?.activity||[])),trend:urbanActivityDelta(b?.key),valid:validateTown()};},
 inspect:key=>{const b=urbanSpatial().blocks[key],home=G.buildings.find(v=>v.kind==='home'&&b?.buildings.includes(v.id));if(!home)return null;selected={id:home.id};openPanel('inspect');return {html:$('panelBody').innerText,pulse:urbanNeighborhoodPulse(key),save:__townTest.save()};},
 state:()=>({money:totalMoney(),rng:rngState,goods:JSON.stringify(goodsBalance()),activity:JSON.stringify(G.urban?.activity||[])}),
 toggleBlocked:key=>{const h=G.households.find(v=>{const b=readBuild(v.home);return b&&urbanBlockKey(b.x,b.y)===key&&v.people.length}),p=h&&G.people[h.people.find(id=>G.people[id]?.job>=0)];if(!p)return null;const before=urbanNeighborhoodPulse(key);p.commuteBlocked=!p.commuteBlocked;const after=urbanNeighborhoodPulse(key);p.commuteBlocked=!p.commuteBlocked;return {person:p.id,before,after};},
 overlay:()=>overlay,snapshot:()=>__townTest.save(),load:s=>__townTest.load(s),step:n=>__townTest.step(n),validate:()=>validateTown(),tryHydrate:s=>hydrateSave(s),
};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
result={'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1280,'height':800});page.set_default_timeout(20000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html);page.add_script_tag(content=script);page.locator('#newTown').click();page.locator('#pause').click()
 town=page.evaluate('__neighborhoodPulse.seed(180)');assert town['valid']['ok'],town['valid'];assert len(town['history'])==2,town['history'];assert town['history'][1]['day']-town['history'][0]['day']==90
 key=town['key'];trend=town['trend'];prior=town['history'][0]['blocks'].get(key,{'residents':0,'occupiedHomes':0,'staffedJobs':0,'jobCapacity':0});latest=town['history'][1]['blocks'].get(key,{'residents':0,'occupiedHomes':0,'staffedJobs':0,'jobCapacity':0})
 assert trend and trend['residents']==latest['residents']-prior['residents'] and trend['occupiedHomes']==latest['occupiedHomes']-prior['occupiedHomes'] and trend['staffedJobs']==latest['staffedJobs']-prior['staffedJobs'],(trend,prior,latest)
 before=page.evaluate('__neighborhoodPulse.state()');view=page.evaluate('k=>__neighborhoodPulse.inspect(k)',key);after=page.evaluate('__neighborhoodPulse.state()')
 assert view,repr(view);assert before==after,repr((before,after));panel_text=view['html'].lower();assert 'neighbourhood life & needs' in panel_text,view['html'];assert 'last 90 days' in panel_text;assert 'work in this neighbourhood' in panel_text;assert 'map medical reach' in panel_text and 'map school reach' in panel_text
 flow=page.evaluate('k=>__neighborhoodPulse.toggleBlocked(k)',key);assert flow and flow['after']['blocked']==flow['before']['blocked']+1 and flow['after']['local']+flow['after']['elsewhere']==flow['before']['local']+flow['before']['elsewhere']-1,flow
 # Actual control enters the existing medical-access overlay; no paid command.
 page.get_by_role('button',name='Map medical reach').click();assert page.evaluate('__neighborhoodPulse.overlay()')=='healthAccess';assert page.locator('#panel').is_hidden()
 # Phone readability: content remains in the scrollable panel, with no page-wide overflow.
 page.set_viewport_size({'width':360,'height':780});page.evaluate('k=>__neighborhoodPulse.inspect(k)',key)
 overflow=page.evaluate('({body:document.documentElement.scrollWidth>innerWidth,panel:document.querySelector("#panelBody").scrollWidth>document.querySelector("#panelBody").clientWidth,buttons:[...document.querySelectorAll("#panelBody [data-urban-local-access]")].map(b=>({w:b.getBoundingClientRect().width,h:b.getBoundingClientRect().height}))})')
 assert not overflow['body'] and not overflow['panel'],overflow
 assert all(v['w']>0 and v['h']>0 for v in overflow['buttons']),overflow
 archive=page.evaluate('__neighborhoodPulse.snapshot()');state=page.evaluate('__neighborhoodPulse.state()');page.evaluate("__neighborhoodPulse.seed(0)");assert page.evaluate('s=>__neighborhoodPulse.load(s)',archive);loaded=page.evaluate('__neighborhoodPulse.state()');assert state==loaded,(state,loaded)
 first=page.evaluate('__neighborhoodPulse.step(30);__neighborhoodPulse.snapshot()');assert page.evaluate('s=>__neighborhoodPulse.load(s)',archive);page.evaluate('__neighborhoodPulse.step(30)');second=page.evaluate('__neighborhoodPulse.snapshot()');assert json.loads(first)==json.loads(second),'30-day continuation diverged after pulse archive reload'
 # Older version-1 urban archives without the optional activity ledger remain loadable.
 legacy=json.loads(archive);legacy.get('urban',{}).pop('activity',None);legacy_text=json.dumps(legacy);page.evaluate("__neighborhoodPulse.seed(0)");assert page.evaluate('s=>__neighborhoodPulse.load(s)',legacy_text);assert page.evaluate('__neighborhoodPulse.validate()').get('ok')
 # Malformed new bounded history is rejected atomically.
 bad=json.loads(archive);bad['urban']['activity'][1]['blocks'][key]['residents']=-1;bad_text=json.dumps(bad);live=page.evaluate('__neighborhoodPulse.snapshot()');assert page.evaluate('s=>__neighborhoodPulse.tryHydrate(s)',bad_text) is False;assert json.loads(live)==json.loads(page.evaluate('__neighborhoodPulse.snapshot()'))
 assert not errors,errors;result.update({'day':town['day'],'block':key,'samples':[s['day'] for s in town['history']],'trend':trend,'workFlow':flow,'readOnlyMoneyRngGoodsActivityStable':True,'actualOverlay':'healthAccess','phoneLayout':overflow,'archiveReplay30dExact':True,'legacyWithoutPulseAccepted':True,'malformedPulseRejectedAtomically':True,'errors':errors});browser.close()
(ROOT/'docs/previews/urban8').mkdir(parents=True,exist_ok=True)
(ROOT/'docs/previews/urban8/neighborhood-pulse.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS 90-day neighbourhood activity, resident work records, access-map action, read-only view and exact archive continuation')
