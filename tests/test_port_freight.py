"""Real reviewed river import, shared handling, accounting and cold continuation."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__portTest={art:()=>{const before=JSON.stringify(G),zoom=cam.zoom;cam.zoom=.23;const far=waterfrontActors(()=>true).length;cam.zoom=.8;const sample=()=>waterfrontActors(()=>true).map(a=>({id:a.id,x:a.x,y:a.y,dx:a.dx,dy:a.dy})),near=sample(),again=sample();cam.zoom=zoom;return {far,near:near.length,stable:JSON.stringify(near)===JSON.stringify(again),unchanged:before===JSON.stringify(G)};},capture:()=>{const o=portCargoPoses()[0],id=o.path[o.inbound?o.path.length-1:0];civicProjectVisit(id%T,id/T|0);__townTest.capture({zoom:.8});},state:()=>({day:G.day,total:totalMoney(),goods:goodsBalance(),valid:validateTown(),shipments:ensureRegionalTrade().shipments,poses:portCargoPoses(),docks:G.firms.filter(f=>f.kind==='wharf').map(f=>({id:f.id,staff:workingStaff(f).length,cargo:f.cargoToday||0,fees:f.handlingFees||0,expenses:f.expenses||0,cash:f.cash,net:f.netProfit||0}))}),step:()=>{__townTest.step(1);},model:()=>{const a=JSON.parse(archivePayload());delete a.trafficState;delete a.visualState;return a;}};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');assert p.evaluate('s=>__townTest.load(s)',p.evaluate('__townTest.save()'));initial=p.evaluate('__portTest.state()');p.locator('[data-panel=economy]').click();p.locator('#portFreightOffice').evaluate('e=>e.open=true');button=p.locator('[data-port-direction=import]:not([disabled])').first;assert button.count(),'No real staffed river import quote';
 for _ in range(8):
  if button.is_disabled():break
  button.click();p.locator('[data-event-choice="0"]').click()
 s=p.evaluate('__portTest.state()');order=s['shipments'][-1];assert order['mode']=='river' and order['market']=='port';assert abs(s['total']-initial['total'])<.001
 saved=p.evaluate('__townTest.save()');p.evaluate('__portTest.step()');expected=p.evaluate('__portTest.model()');assert p.evaluate('s=>__townTest.load(s)',saved);p.evaluate('__portTest.step()');actual=p.evaluate('__portTest.model()');assert actual==expected,('Cold continuation',set(actual)-set(expected),set(expected)-set(actual),[(k,str(expected.get(k))[:120],str(actual.get(k))[:120])for k in set(expected)|set(actual) if expected.get(k)!=actual.get(k)])
 history=[];trajectory=[];boats=0;captured=False;art=None
 for _ in range(60):
  s=p.evaluate('__portTest.state()');assert s['valid']['ok'] and abs(s['total']-initial['total'])<.001 and max(abs(g['error'])for g in s['goods'])<.001,('Daily books',s['day']);active=next((o for o in s['shipments']if o['id']==order['id']),None)
  if not active:break

  if s['poses']and not captured:
   art=p.evaluate('__portTest.art()');assert art['far']==0 and art['stable']and art['unchanged']and art['near']<=10,art;p.evaluate('__portTest.capture()')
   (ROOT/'reports/port-freight').mkdir(exist_ok=True);p.screenshot(path=str(ROOT/'reports/port-freight/paid-river-cargo.png'));captured=True
  history.append(active['stage']);trajectory.append({'day':s['day'],'docks':s['docks']});boats+=len(s['poses']);p.evaluate('__portTest.step()')
 assert not active,'River order failed to arrive';assert boats>0,'No real local water leg observed';assert 'outside'in history  and 'delivering'in history,history
 s=p.evaluate('__portTest.state()');assert abs(s['total']-initial['total'])<.001 and max(abs(g['error'])for g in s['goods'])<.001 and s['valid']['ok'],s
 bad=json.loads(p.evaluate('__townTest.save()'));recent=next(o for o in bad['regionalTrade']['recent']if o['id']==order['id']);recent['waterPath']=[0,10];assert not p.evaluate('g=>__townTest.load(g)',bad);assert not errors,errors;b.close()
(ROOT/'reports/port-freight').mkdir(exist_ok=True);(ROOT/'reports/port-freight/controls.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'order':order,'history':history,'trajectory':trajectory,'observedBoatPoses':boats,'art':art,'final':s,'errors':errors},indent=2));print('PASS real reviewed river order, cold continuation, physical stages, malformed path, cash and goods',history)
