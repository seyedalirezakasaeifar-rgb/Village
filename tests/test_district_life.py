"""Bounded overview caching and ambient life respect paid/state/LOD boundaries."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();out=ROOT/'reports/district-life';out.mkdir(parents=True,exist_ok=True)
probe=r'''window.__districtLifeCheck=()=>{
 const before=JSON.stringify(G),oldZoom=cam.zoom,oldMotion=gameOptions.reducedMotion;cam.zoom=1.15;const items=displayItems.filter(a=>a.b?.kind==='home'),actors=neighbourhoodAmbient(items),again=neighbourhoodAmbient(items);
 gameOptions.reducedMotion=true;const reduced=neighbourhoodAmbient(new Proxy([],{get(){throw Error('Reduced motion iterated households')}}));gameOptions.reducedMotion=false;cam.zoom=.2;const far=neighbourhoodAmbient(new Proxy([],{get(){throw Error('Far actors iterated households')}}));
 const a=overviewFreight(),b=overviewFreight();cam.zoom=oldZoom;gameOptions.reducedMotion=oldMotion;
 return {ambient:actors.length,cap:gameOptions.quality==='high'?7:4,stable:JSON.stringify(actors)===JSON.stringify(again),far:far.length,reduced:reduced.length,cacheReused:a===b,overview:a.map(r=>({market:r.market,inbound:r.inbound,outbound:r.outbound,points:r.points.length})),unchanged:before===JSON.stringify(G)};
};'''
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.evaluate("__townTest.reset('settlement',42)");p.evaluate('__townTest.step(20)');r=p.evaluate('__districtLifeCheck()');assert r['unchanged'] and r['stable'] and r['cacheReused'] and r['far']==r['reduced']==0 and 0<r['ambient']<=r['cap'],r
 for name,z in [('overview',.25),('middle',.55),('near',1.15)]:
  p.evaluate('(z)=>__townTest.capture({zoom:z})',z);p.locator('#view').screenshot(path=str(out/(name+'.png')))
 assert not errors,errors;b.close()
r.update(source_sha256=hashlib.sha256(source.encode()).hexdigest(),errors=errors);(out/'checks.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
