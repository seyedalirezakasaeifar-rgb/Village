"""Finite local-only continuity capture of one paid expanded QA city."""
from pathlib import Path
import sys,ast,json,hashlib,time,io
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
from PIL import Image
source=(ROOT/'assets/game.js').read_text();out=ROOT.parent/'scratch/city-continuity';out.mkdir(parents=True,exist_ok=True)
large=next(ast.literal_eval(n.args[0]) for n in ast.walk(ast.parse((ROOT/'tests/test_v7_live_large_town.py').read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='evaluate' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str) and 'while(g.people.length<2000' in n.args[0].value)
probe=r'''window.__continuity={cargo:()=>portCargoPoses().length,states:()=>{const f=G.firms.find(f=>f.kind==='quarry'&&!f.closed);if(!f)throw Error('No actual quarry');liquidateFirm(f,'Controlled audit closure');const id=f.building,a=brownfieldAssess(id),b=a.ok&&brownfieldAcquire(id),c=b?.ok&&brownfieldFund(id);if(!c?.ok)throw Error('Paid renewal unavailable');return {id,status:brownfieldSites()[0].status};},schedule:()=>{const b=readBuild(G.publicPlaces.places.find(p=>p.kind==='square').building);return authorizeCivicGathering(reviewCivicGathering({venue:b.id,start:G.day+1}));},sites:()=>{const find=k=>G.buildings.find(b=>b.kind===k),positions={};for(const [name,b] of [['neighbourhood',find('home')],['rail',find('elevated_station')],['waterfront',find('wharf')],['farms',find('farm')],['renewal',brownfieldSites()[0]],['gathering',readBuild(G.publicPlaces.places.find(p=>p.kind==='square').building)]]){if(!b)throw Error('Missing '+name);const p=iso(b.x,b.y);positions[name]={x:p[0],y:p[1],zoom:name==='farms'?.7:1.1};}return positions;},capture:opts=>__townTest.capture(opts),pauseCheck:()=>{const before=JSON.stringify(G),a=cv.toDataURL();dirty=true;draw();const stable=a===cv.toDataURL();viewRasterKey='';viewBackgroundKey='';nightEmissionKey='';staticDirty=true;dirty=true;draw();return{stable,coldStable:a===cv.toDataURL(),unchanged:before===JSON.stringify(G),atlasBytes,gatheringBytes:gatheringArtBytes,brownfieldBytes:brownfieldArtAtlas.size*72*96*4};},reduce:value=>{gameOptions.reducedMotion=value;applyPresentationOptions();fit();dirty=true;draw();},status:()=>({day:G.day,grid:T,deeds:G.charter.owned.length,people:G.people.length,routes:G.transit.routes.map(r=>({mode:r.mode,operating:r.stats.operating})),cargo:portCargoPoses().length,calendar:civicGatheringCues(),renewal:brownfieldArtDescriptors()})};'''
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390},device_scale_factor=2);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',(ROOT/'tools/qa_live_network.js').read_text()+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');p.evaluate(large);network=p.evaluate('__liveNetworkBuild()');p.evaluate('__townTest.step(3)')
 p.locator('[data-panel=economy]').click();p.locator('#portFreightOffice').evaluate('e=>e.open=true');button=p.locator('[data-port-direction=import]:not([disabled])').first
 for i in range(6):
  if not button.count() or button.is_disabled():break
  button.click();p.locator('[data-event-choice="0"]').click()
 p.keyboard.press('Escape')
 for i in range(30):
  if p.evaluate('__continuity.cargo()'):break
  p.evaluate('__townTest.step(1)')
 assert p.evaluate('__continuity.cargo()'),'No actual paid river cargo'
 p.evaluate('__continuity.states()');p.locator('[data-panel=overview]').click();p.locator('[data-civic-projects]').click();p.locator('[data-public-place=square]').click();p.locator('#publicPlaceName').fill('Willow Commons');p.locator('[data-event-choice="0"]').click();p.keyboard.press('Escape');assert p.evaluate('__continuity.schedule().ok');p.evaluate('__townTest.step(1)');sites=p.evaluate('__continuity.sites()');start_status=p.evaluate('__continuity.status()');checks=[];captures=[];checkpoint=p.evaluate('__townTest.save()');(out/'checkpoint.json').write_text(checkpoint)
 for name,target in sites.items():
  p.evaluate('__continuity.capture',target);checks.append({'site':name,'mode':'paused',**p.evaluate('__continuity.pauseCheck()')})
  for night in [False,True]:
   assert p.evaluate('s=>__townTest.load(s)',checkpoint);p.evaluate('__continuity.capture',{**target,'night':night});p.locator('#pause').click();frames=[];started=time.monotonic()
   for frame in range(12):
    if frame<4:p.evaluate('__continuity.capture',{**target,'zoom':.25+(.85*frame/3),'x':target['x']+60*(1-frame/3)})
    frames.append(Image.open(io.BytesIO(p.locator('#view').screenshot())).convert('RGB'));p.wait_for_timeout(60)
   p.locator('#pause').click();elapsed=time.monotonic()-started;file=out/(name+('-night' if night else '-day')+'.gif');frames[0].save(file,save_all=True,append_images=frames[1:],duration=round(elapsed/len(frames)*1000),loop=0);frames[8].save(out/(name+('-night' if night else '-day')+'-sample.png'));captures.append({'file':str(file),'frames':len(frames),'seconds':elapsed});checks.append({'site':name,'night':night,**p.evaluate('__continuity.pauseCheck()')})
  p.evaluate('__continuity.reduce',True);checks.append({'site':name,'mode':'reduced',**p.evaluate('__continuity.pauseCheck()')});p.evaluate('__continuity.reduce',False)
 assert all(r['stable'] and r['coldStable'] and r['unchanged'] for r in checks),checks
 assert not errors,errors;final_status=p.evaluate('__continuity.status()');b.close()
(out/'checks.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'network':network,'start':start_status,'end':final_status,'checks':checks,'captures':captures,'errors':errors,'fixture':'One authored 2000-resident expanded city; actual paid imports, transit, renewal and gathering. Each short day/night shot replays the same committed city checkpoint; motion uses ordinary unpaused simulation. Camera/lighting transitions are QA controls.'},indent=2)+'\n');print('PASS',len(checks),'checks',len(captures),'local motion captures')
