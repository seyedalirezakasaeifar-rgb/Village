"""Public route capital, daily capacity, wages, fare conservation, migration and controls."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__transitProbe={
 state:()=>JSON.parse(JSON.stringify(ensureTransit())),
 valid:()=>Object.fromEntries([validateTransit,validateCivicState,validateCreditState,validateScenarioProgramme,validateCharter,validateMayorJourney,validatePrivateServices,validateDistrictProgrammes,validateRegionalTrade,validateWaterfrontArchive,validateGoodsAccounting].map(f=>[f.name,f(G)])),
 setup:()=>{
  G.autoBuild=false;const injection=Math.min(G.region,250000);G.region-=injection;G.treasury+=injection;
  const lot=buildableCandidates('business').find(c=>canPlace(c.x,c.y,true,'transit_depot'));
  const depot=lot&&buildTransitFacility('transit_depot',lot.x,lot.y);if(!depot)throw Error('No depot lot');
  // Reassign existing residents to unemployment, rather than inventing drivers or money.
  const drivers=G.people.filter(p=>p.age>=18&&p.age<=70).slice(0,12);
  for(const p of drivers){if(G.firms[p.job])G.firms[p.job].workers=G.firms[p.job].workers.filter(id=>id!==p.id);p.job=-1;p.skill=.8;p.previousPublicRole='';p.searchAfter=G.day+1000;}
  const spec={mode:'bus',depot:depot.id,stops:[roadId(15,27),roadId(21,27),roadId(27,27),roadId(35,27),roadId(43,27)],level:2};const quote=transitQuote(spec),before=totalMoney(),route=buildTransitRoute(spec,quote);
  return {depot,spec,quote,route,before,after:totalMoney()};
 },
 quote:(s,id=-1)=>transitQuote(s,id),build:(s,q)=>buildTransitRoute(s,q),edit:(s,q,id)=>buildTransitRoute(s,q,id),level:(id,n)=>setTransitLevel(id,n),retire:id=>deleteTransitRoute(id),remove:id=>removeTransitFacility(id),
 mutate:fn=>eval(fn),
 draw:()=>{overlay='transit';dirty=true;draw();},
 journeys:()=>{const found=[];for(const p of G.people){if(p.job<0)continue;const h=G.households[p.hh],home=readBuild(h.home),work=readBuild(G.firms[p.job].building),j=transitJourney(home,work);if(j)found.push({id:p.id,trip:j,allocated:p.transitTrip});}return found;},
 poses:zoom=>transitVehiclePoses(10,zoom),
 cancel:()=>({draft:!!transitDraft,mode:buildMode}),
 xy:(x,y)=>{const p=iso(x,y),r=cv.getBoundingClientRect();return {x:r.left+cw/2+(p[0]-cam.x)*cam.zoom,y:r.top+ch/2+(p[1]+18-cam.y)*cam.zoom};},
 draft:()=>transitDraft&&({stops:transitDraft.stops.slice(),mode:transitDraft.mode}),
 rail:()=>{
  const places=buildableCandidates('business').filter(c=>canPlace(c.x,c.y,true,'elevated_station'));let a=null,b=null;
  for(const p of places){const candidate=buildTransitFacility('elevated_station',p.x,p.y);if(!candidate)continue;if(!a)a=candidate;else{const path=routeBetween(a,candidate);if(path.length>=10){b=candidate;break;}removeTransitFacility(candidate.id);}}
  if(!a||!b)throw Error('No rail station pair');const depot=G.buildings.find(b=>b.kind==='transit_depot'),spec={mode:'elevated',depot:depot.id,stops:[a.id,b.id],level:1},quote=transitQuote(spec);return {spec,quote,route:buildTransitRoute(spec,quote)};
 }
};
'''
source=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':800});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42)")
 initial=p.evaluate('__townTest.get().total');setup=p.evaluate('__transitProbe.setup()');assert setup['quote']['ok'] and setup['route'],setup
 assert abs(setup['before']-setup['after'])<.000001,setup
 assert not p.evaluate('(v)=>__transitProbe.build(v.spec,v.quote)',setup),'Repeated quote spent twice'
 assert not p.evaluate('(id)=>__transitProbe.remove(id)',setup['depot']['id']),'Removed depot still in use'
 p.evaluate('__townTest.step(1)');state=p.evaluate('__transitProbe.state()');print('day one',json.dumps(state));assert state['routes'][0]['stats']['operating'],state
 assert state['daily']['staff']==4,state
 assert p.evaluate('__transitProbe.poses(.1).length')==0
 assert p.evaluate('__transitProbe.poses(1).length')==2
 journeys=p.evaluate('__transitProbe.journeys()');assert journeys,journeys
 assert p.evaluate('__townTest.validate().ok'),p.evaluate('__townTest.validate()')
 assert abs(initial-p.evaluate('__townTest.get().total'))<.0001
 print('validators',p.evaluate('__transitProbe.valid()'));saved=p.evaluate('__townTest.save()');assert p.evaluate('(s)=>__townTest.load(s)',saved)
 p.evaluate('__townTest.step(5)');continued=p.evaluate('__townTest.save()');assert p.evaluate('(s)=>__townTest.load(s)',saved);p.evaluate('__townTest.step(5)');assert p.evaluate('__townTest.save()')==continued,'Deterministic continuation diverged'
 assert abs(initial-p.evaluate('__townTest.get().total'))<.0001
 edited={**setup['spec'],'stops':[setup['spec']['stops'][0],setup['spec']['stops'][2],setup['spec']['stops'][-1]]};rid=setup['route']['id']
 eq=p.evaluate('(v)=>__transitProbe.quote(v.spec,v.id)',{'spec':edited,'id':rid});assert eq['ok'] and eq['cost']==0
 assert p.evaluate('(v)=>!!__transitProbe.edit(v.spec,v.q,v.id)',{'spec':edited,'q':eq,'id':rid})
 assert not p.evaluate('(v)=>__transitProbe.edit(v.spec,v.q,v.id)',{'spec':edited,'q':eq,'id':rid})
 assert not p.evaluate('(v)=>__transitProbe.quote({...v,stops:[0,1]}).ok',edited)
 p.evaluate('__townTest.step(1)')
 # Every malformed archive must leave the running town exactly unchanged.
 for change in ['g.transit.routes[0].vehicles=999','g.transit.routes[0].stops=[-1,2]','g.transit.routes[0].stats.capacity=-2','g.transit.tracks=[-1]','g.transit.daily.revenue=null','g.transit.routes[0].offsets=[0,0]','g.transit.lastDay=g.day+1','g.transit.routes[0].stats.staff=[3,3]' ]:
  assert p.evaluate('(change)=>{const before=__townTest.save(),g=JSON.parse(before);eval(change);return !__townTest.load(g)&&__townTest.save()===before;}',change),change
 # Player route office: review first, no funds spent picking/cancelling stops.
 p.locator('[data-panel=construction]').click();p.locator('[data-transit-action=new-bus]').click();assert p.locator('#transitLevel').is_visible();p.locator('[data-transit-action=map]').click();assert p.evaluate('__transitProbe.cancel().draft')
 point=p.evaluate('__transitProbe.xy(21,27)');p.mouse.click(point['x'],point['y']);assert len(p.evaluate('__transitProbe.draft().stops'))==1
 point=p.evaluate('__transitProbe.xy(35,27)');p.mouse.click(point['x'],point['y']);assert len(p.evaluate('__transitProbe.draft().stops'))==2
 p.locator('[data-panel=construction]').click();p.locator('[data-transit-action=quote]').click();assert p.locator('[data-transit-action=build]').is_visible();p.locator('[data-transit-action=cancel]').click();p.locator('#panelClose').click()
 p.locator('[data-panel=construction]').click();p.locator('[data-transit-action=new-bus]').click();p.locator('[data-transit-action=map]').click()
 p.keyboard.press('Escape');assert p.evaluate('__transitProbe.cancel()')=={'draft':False,'mode':''}
 p.locator('[data-panel=construction]').click();p.locator('[data-transit-action=new-bus]').click();p.locator('[data-transit-action=map]').click();assert p.evaluate('__townArchive.back()');assert not p.evaluate('__transitProbe.cancel().draft')
 # Service suspension preserves owned fleet but never runs vehicles or accepts riders.
 rid=setup['route']['id'];assert p.evaluate('(id)=>__transitProbe.level(id,0)',rid);p.evaluate('__townTest.step(1)');assert not p.evaluate('__transitProbe.state().routes[0].stats.operating');assert not p.evaluate('__transitProbe.poses(1).length')
 assert p.evaluate('(id)=>__transitProbe.level(id,1)',rid);p.evaluate('__townTest.step(1)');assert p.evaluate('__transitProbe.state().routes[0].stats.operating')
 rail=p.evaluate('__transitProbe.rail()');assert rail['quote']['ok'] and rail['route'],rail
 p.evaluate('__townTest.step(1)');assert p.evaluate('__transitProbe.state().routes[1].stats.operating')
 p.evaluate('__transitProbe.draw()');p.screenshot(path=str(ROOT/'reports/transit-network-desktop.png'))
 assert p.evaluate('__townTest.validate().ok'),p.evaluate('__townTest.validate()')
 rail_saved=p.evaluate('__townTest.save()');assert p.evaluate('(s)=>__townTest.load(s)',rail_saved)
 assert p.evaluate('(id)=>__transitProbe.retire(id)',rid);assert not p.evaluate('(id)=>__transitProbe.retire(id)',rid)
 assert abs(initial-p.evaluate('__townTest.get().total'))<.0001
 p.set_viewport_size({'width':390,'height':844});p.locator('[data-panel=construction]').click();p.screenshot(path=str(ROOT/'reports/transit-network-mobile.png'));assert p.locator('.transit-office').is_visible();assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
 assert not errors,errors
 (ROOT/'reports/transit-network-8.json').write_text(json.dumps({'source_sha256':hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest(),'passed':True,'screenshots':['transit-network-desktop.png','transit-network-mobile.png'],'opening_route':state,'browser_errors':errors},indent=2))
 print('PASS public depot/routes, quoted capital, repeat action protection, daily staffing/capacity, real journey routing, far LOD, conservation, exact replay, archive rejection, cancel/Back, suspension, elevated infrastructure and fleet resale')
 b.close()
