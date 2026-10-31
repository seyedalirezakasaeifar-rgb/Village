"""Controlled route failures: no resource grants; stock/cash remain conserved."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__portFaults=()=>{
 __townTest.reset('settlement',42);G.autoBuild=false;const initial=totalMoney(),m=OUTSIDE_MARKETS.find(m=>m.id==='port'),f=G.firms.find(f=>f.kind==='grocer'),w=G.firms.find(f=>f.kind==='wharf'),s=ensureRegionalTrade(),checks=[];
 const step=(block=false)=>{G.day++;prepareWaterfrontDay();if(block)for(const d of operatingWharves)d.remaining=0;regionalFreightDay();};
 const order=()=>{const q=regionalQuote(f,m,'food','import',w.id);if(!q||q.mode!=='river')throw Error('No staffed river quote');if(!dispatchRegional(f,'food',60,'import',q))throw Error('No working capital');return s.shipments[s.shipments.length-1];};
 const check=label=>{const error=Math.max(...goodsBalance().map(g=>Math.abs(g.error))),drift=totalMoney()-initial;if(error>.001||Math.abs(drift)>.001)throw Error(label+' books '+error+' '+drift);checks.push({label,error,drift});};
 const quoteState=JSON.stringify(G);portFreightProspect(f,'food','import',w.id);
 const comparisons=G.firms.filter(x=>!x.closed&&graph().portals.has(x.building)).map(x=>{const river=regionalQuote(x,m,'food','import',w.id),road=portRoadQuote(x,m,'food','import');return {firm:x.id,river:river?.freight,road:road?.freight,riverDays:river?.days,roadDays:road?.days};});
 if(JSON.stringify(G)!==quoteState)throw Error('Read-only freight quotes changed town state');
 let o=order();cancelRegionalShipment(o.id);step();if(s.shipments.some(x=>x.id===o.id))throw Error('Early return failed');check('early cancel');
 o=order();for(let i=0;i<30&&o.stage!=='unloading';i++)step(true);if(o.stage!=='unloading')throw Error('No finite shared-capacity queue');const before=o.handled;if(before!==0)throw Error('Zero remaining capacity loaded cargo');if(!rerouteRegionalShipment(o.id,-1)||o.mode!=null||o.waterPath!=null)throw Error('Water-to-road reroute failed');for(let i=0;i<40&&s.shipments.some(x=>x.id===o.id);i++)step();if(s.shipments.some(x=>x.id===o.id))throw Error('Rerouted cargo stuck');check('shared capacity and paid road transfer');
 o=order();step();w.closed=true;const absent=regionalQuote(f,m,'food','import',w.id);if(absent)throw Error('Closed dock offered new water loads');for(let i=0;i<60&&s.shipments.some(x=>x.id===o.id);i++)step();if(s.shipments.some(x=>x.id===o.id))throw Error('Closed dock stranded cargo without recovery');check('closure recovery');w.closed=false;step();
 const exported=ensureWaterfront().exports,delivered=s.delivered;if(!dispatchRegional(f,'food',20,'export',regionalQuote(f,m,'food','export',w.id)))throw Error('Export not funded');o=s.shipments[s.shipments.length-1];for(let i=0;i<40&&s.shipments.some(x=>x.id===o.id);i++)step();if(s.shipments.some(x=>x.id===o.id)||s.delivered!==delivered+1||ensureWaterfront().exports!==exported+20)throw Error('Water export did not settle exactly once');check('owned export and delayed buyer settlement');
 s.routePreference='interchange';const preference=regionalQuote(f,m,'food','import');if(preference.mode==='river')throw Error('Road preference ignored');const bad=JSON.parse(archivePayload());bad.regionalTrade.recent.find(x=>x.mode==='river').outsideDays=-1;if(hydrateSave(bad))throw Error('Malformed voyage accepted');check('invalid voyage atomic rejection');const arrivals=s.recent.filter(x=>x.mode==='river'&&x.depot===w.id&&x.status==='Delivered'),beforeReport=JSON.stringify(G),report=waterfrontFirmReport(w),sample=arrivals.length+' loads · '+policyNumber(arrivals.reduce((n,x)=>n+x.qty,0))+' units';if(!report.includes(sample)||beforeReport!==JSON.stringify(G))throw Error('Inspector arrival sample or quote purity incorrect');check('inspector counts only successful arrivals');return {checks,comparisons,claims:s.claims.length};
};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__portFaults()');assert not errors,errors;b.close()
(ROOT/'reports/port-freight').mkdir(exist_ok=True);(ROOT/'reports/port-freight/faults.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledFaults':True,'result':result,'errors':errors},indent=2));print('PASS',result)
