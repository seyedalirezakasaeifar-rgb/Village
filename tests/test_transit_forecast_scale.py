"""Synthetic 2,000-resident size benchmark; funded setup is not player balance evidence."""
import ast,json,hashlib
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
m=ast.parse((ROOT/'tests/test_transit_live_performance.py').read_text());probe=next(ast.literal_eval(n.value) for n in m.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe+='''\nwindow.__forecastScale=()=>{const before=JSON.stringify(G),spec=G.transit.routes[0],start=performance.now(),r=transitRouteReport(spec.id),elapsed=performance.now()-start,again=performance.now(),cached=transitRouteReport(spec.id);return {population:G.people.length,routes:G.transit.routes.length,totalMs:elapsed,calculationMs:r.calculationMs,cachedMs:performance.now()-again,pure:before===JSON.stringify(G),sameStamp:cached.stamp===r.stamp,ok:r.ok,fares:r.fares,capacity:r.service.capacity,work:r.demand.counts};};'''
source=(ROOT/'assets/game.js').read_text();out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'rows':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for count in [12,48]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__transitLive.large()');p.evaluate('(n)=>__transitLive.build(n)',count);r=p.evaluate('__forecastScale()');assert r['ok'] and r['pure'] and r['sameStamp'],r;out['rows'].append(r);p.close()
 b.close()
(ROOT/'reports/transit-forecast-scale-8.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
