"""Real reviewed river export: actual departure, sea visibility and arrival."""
from pathlib import Path
import subprocess,json,time,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews/webgl-export-8';OUT.mkdir(parents=True,exist_ok=True)
source=(ROOT/'assets/game.js').read_text();probe=r'''window.__exportCycle={orders:()=>G.regionalTrade.shipments.map(o=>({id:o.id,direction:o.direction,mode:o.mode,stage:o.stage})),state:id=>({day:G.day,active:G.regionalTrade.shipments.find(o=>o.id===id)?.stage||null,recent:G.regionalTrade.recent.find(o=>o.id===id)?.status||null}),boat:id=>__cityVisualActors('near',{minX:0,maxX:127,minZ:0,maxZ:127}).find(a=>a.id==='vessel:'+(900000+id))||null};''';script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js');server=subprocess.Popen(['python','-m','http.server','8790','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1000,'height':700});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(body=script,content_type='application/javascript'));p.goto('http://127.0.0.1:8790/index.html?cityArt=webgl&cityQuality=low');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.wait_for_function('window.__webglTaste');prior={o['id']for o in p.evaluate('__exportCycle.orders()')};p.locator('[data-panel=economy]').click();p.locator('#portFreightOffice').evaluate('e=>e.open=true');button=p.locator('[data-port-direction=export]:not([disabled])').first
  # Founding producers may have no finished inventory yet. Wait through real
  # paid production days; never inject export stock just to make a shot.
  waited=0
  while not button.count() and waited<8:
   p.evaluate('__townTest.step(1)');p.locator('#panelClose').click();p.locator('[data-panel=economy]').click();p.locator('#portFreightOffice').evaluate('e=>e.open=true');waited+=1
  assert button.count(),('No affordable export after actual production',p.locator('#portFreightOffice').inner_text()[:500]);prior={o['id']for o in p.evaluate('__exportCycle.orders()')};button.click();p.locator('[data-event-choice="0"]').click();p.keyboard.press('Escape');order=next(o for o in p.evaluate('__exportCycle.orders()')if o['id']not in prior);assert order['direction']=='export'and order['mode']=='river';target=order['id'];history=[];started=time.monotonic();p.locator('#pause').click();observed=False;captured=False;completed=False;lastFocus=None
  while time.monotonic()-started<60:
   p.wait_for_timeout(160);state=p.evaluate('(id)=>__exportCycle.state(id)',target);boat=p.evaluate('(id)=>__exportCycle.boat(id)',target);row={'elapsed':round(time.monotonic()-started,3),**state,'boat':boat};history.append(row)
   if boat:
    observed=True
    if lastFocus is None or abs(boat['x']-lastFocus['x'])+abs(boat['z']-lastFocus['z'])>5:p.evaluate('(a)=>__webglTaste.focus(a.x,a.z,1.8)',boat);lastFocus=boat
    if not captured and len([h for h in history if h['boat']])>2:p.screenshot(path=str(OUT/'actual-outbound-river-load.png'));captured=True
   choices=p.locator('[data-event-choice]:not([disabled])')
   if choices.count()and choices.first.is_visible():choices.first.click()
   if state['recent']:completed=True;break
  p.locator('#pause').click();assert observed and completed,(order,history[-1]);assert history[-1]['recent']=='Delivered',history[-1];assert any(h['active']=='outside'and not h['boat']for h in history),'No actual beyond-outlet sea interval observed';assert p.evaluate('__cityVisualSave()');assert not errors,errors;result={'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'order':order,'actualProductionDaysBeforeQuote':waited,'normalClockSeconds':round(time.monotonic()-started,3),'departureVesselObserved':observed,'beyondOutletSeaIntervalHidden':True,'terminalStatus':history[-1]['recent'],'cycle':history,'save':True,'errors':errors};(OUT/'cycle.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS reviewed river export normal-clock departure/sea/Delivered; actualboat hidden beyondoutlet');b.close()
finally:server.terminate()
