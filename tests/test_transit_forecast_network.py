"""Controlled capacity/transfer oracle for forecast fares and actual conservation."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,json,hashlib
m=ast.parse((ROOT/'tests/test_transit_capacity.py').read_text());probe=next(ast.literal_eval(n.value) for n in m.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe=probe.replace("closed:false,cash:0,workers:[]", "closed:false,cash:0,kind:'office',name:'Controlled workplace',jobs:300,wage:24,workers:[]")
probe=probe.replace("const route=buildTransitRoute(spec,quote);", "const beforeForecast=JSON.stringify(G),proposal=transitProposalReport(spec);if(beforeForecast!==JSON.stringify(G))throw Error('Capacity forecast changed live accounts');const route=buildTransitRoute(spec,quote);")
probe=probe.replace("return {funded,repeated,disrupted,unfunded,parallel,transfers};", "const aBefore=JSON.stringify(G),leftReport=transitRouteReport(lr.id),rightReport=transitRouteReport(rr.id);if(aBefore!==JSON.stringify(G))throw Error('Transfer forecasts settled real fares');return {funded,repeated,disrupted,unfunded,parallel,transfers,proposal,leftReport,rightReport};")
source=(ROOT/'assets/game.js').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__transitCapacity()');r=result['proposal'];assert r['demand']['counts']['boarded']==199 and r['demand']['counts']['denied']==101,r
 assert r['service']['operatingCost']==result['funded']['stats']['expenses']==157
 assert r['fares']=={'low':248.75,'high':248.75} and r['fares']['low']==result['funded']['fares'],r
 left,right=result['leftReport'],result['rightReport'];assert left['fares']['low']==right['fares']['low']==187.5,(left,right)
 assert left['fares']['low']+right['fares']['low']==result['transfers']['fares']==375,result
 assert left['demand']['counts']['boarded']==right['demand']['counts']['boarded']==300,result
 b.close()
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledCapacityAndTransfers':True,'singleRoute':r,'left':left,'right':right,'actualFareTotal':result['transfers']['fares'],'noEconomicWrites':True};(ROOT/'reports/transit-forecast-network-8.json').write_text(json.dumps(out,indent=2));print('PASS snapshot199boarded/101denied/$248.75 matches actual service;300transfer riders share$375 once; forecasts do not pay real fares')
