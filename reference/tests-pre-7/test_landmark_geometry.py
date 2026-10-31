"""Adversarial plot footprint, landmark animation, speed and save tests."""
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
script=(root/'assets/game.js').read_text()
assert script.endswith('})();\n')
script=script[:-6]+'''window.__landmarkTest={
 snapshot:()=>G, getIssues:()=>getFootprintIssues(),
 place:(kind,x,y)=>{if(!canPlace(x,y,true,kind))return null;const site=startDevelopmentProject('firm',{x,y},22000,10,{firmKind:kind,capital:12000});return site?.id},
 isFree:(kind,x,y)=>canPlace(x,y,true,kind), road:(x,y)=>construct('road',x,y,true),
 find:(kind)=>{for(let y=9;y<T-9;y++)for(let x=9;x<T-9;x++)if(canPlace(x,y,true,kind))return [x,y];return null},
 metro:()=>{const site=stationHubs()[0];return site},
 airsite:()=>airfieldCandidate(),
 showAirport:()=>{const site=airfieldCandidate();if(!site)return false;const b=startDevelopmentProject('airport',site,780000,4,{runway:site.runway});if(!b)return false;G.airport={building:b.id,runway:site.runway,operating:true,passengers:10,flights:3,firm:0};for(const id of site.runway)G.landUse[id]=3;b.kind='airport';G.projects=G.projects.filter(p=>p.id!==b.id);invalidateRoads(false);staticDirty=true;dirty=true;const pos=iso(site.x,site.y);cam.x=pos[0];cam.y=pos[1]+60;cam.zoom=.95;return b.id},
 showMetro:()=>{let hubs=stationHubs(),a=hubs[0],b=hubs.find(p=>Math.abs(p.x-a.x)+Math.abs(p.y-a.y)>10);if(!a||!b)return false;let first=stationBuilding(a),second=stationBuilding(b);if(!first||!second)return false;G.metro.stations=[first.id,second.id];G.metro.lines=[{from:first.id,to:second.id,readyDay:0,color:'#dbb975'}];G.metro.operating=true;G.metro.cash=60000;invalidateRoads(false);staticDirty=true;dirty=true;return [first.id,second.id]},
 display:(id)=>{const b=readBuild(id);if(!b)return;const p=iso(b.x,b.y);cam.x=p[0];cam.y=p[1];cam.zoom=.9;staticDirty=true;dirty=true;},
 runFrame:(secs)=>{frameClock+=secs;dirty=true;draw()},
 buildingAt:(x,y)=>buildingAt(x,y)?.id??null,
};
})();\n'''
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1150,'height':680}, device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 html=(root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
 page.set_content(html);page.add_script_tag(content=script)
 page.locator('#newTown').click()
 initial=page.evaluate('__landmarkTest.getIssues()')
 assert not initial, initial
 # Force a depot on an actually suitable 2x2 site, then verify road and building prevention.
 test=page.evaluate('''()=>{
  let pos=__landmarkTest.find('warehouse');if(!pos)throw Error('No 2x2 site');
  const id=__landmarkTest.place('warehouse',...pos),cells=[];
  for(let dy=0;dy<2;dy++)for(let dx=0;dx<2;dx++){
   const x=pos[0]+dx,y=pos[1]+dy;cells.push(__landmarkTest.buildingAt(x,y));
   __landmarkTest.road(x,y);if(__landmarkTest.snapshot().tiles[y*56+x]===1)throw Error('ROAD OVER BUILDING');
  }
  if(cells.some(v=>v!==id))throw Error('Incomplete footprint');
  return {id,site:pos,cells,issues:__landmarkTest.getIssues()};
 }''')
 assert not test['issues'],test
 print('MULTI-TILE ROAD COLLISION PASS:',test,flush=True)
 # Higher speed, pause, save restoration.
 page.locator('#speedRange').fill('6')
 assert page.locator('#speed').inner_text()=='64×'
 beforeFast=page.evaluate('__townTest.get().day')
 page.wait_for_timeout(750)
 afterFast=page.evaluate('__townTest.get().day')
 assert afterFast>beforeFast,(beforeFast,afterFast)
 print('REAL-TIME 64X RESPONSIVE:',beforeFast,'->',afterFast,flush=True)
 stored=page.evaluate('JSON.parse(__townTest.save()).speed')
 assert stored==64
 page.locator('#speedRange').fill('4')
 assert page.locator('#speed').inner_text()=='16×'
 page.evaluate('''()=>{let old=__townTest.save();if(!__townTest.load(old))throw Error('save load failed');}''')
 print('SPEED AND SAVE PASS:',stored,'->',page.locator('#speed').inner_text(),flush=True)
 page.locator('#panelClose').click()
 airport=page.evaluate('__landmarkTest.showAirport()')
 assert airport, 'No valid airfield site found'
 page.evaluate('__landmarkTest.runFrame(7)')
 page.screenshot(path=str(root/'reports/landmark-airfield.png'))
 page.evaluate('__landmarkTest.runFrame(3)')
 page.screenshot(path=str(root/'reports/landmark-airfield-later.png'))
 assert not page.evaluate('__landmarkTest.getIssues()'),page.evaluate('__landmarkTest.getIssues()')
 print('AIRPORT SITE / RENDER PASS:',airport,flush=True)
 metro=page.evaluate('__landmarkTest.showMetro()')
 assert metro,'No valid underground stations found'
 page.evaluate("__landmarkTest.display(%d)"%metro[0]);page.evaluate('__landmarkTest.runFrame(6)')
 page.screenshot(path=str(root/'reports/landmark-metro.png'))
 assert not page.evaluate('__landmarkTest.getIssues()'),page.evaluate('__landmarkTest.getIssues()')
 print('METRO SITES / RENDER PASS:',metro,flush=True)
 assert not errors,errors
 browser.close()
print('PASS landmark footprint, road exclusion, save, acceleration and animation draws')
