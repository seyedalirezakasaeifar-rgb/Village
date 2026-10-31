"""Observe actual paid project delivery even when the 36-row recent log rolls over."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_text()
probe='''
window.__projectDeliveryOverflow=()=>{const original=G;try{
 G=JSON.parse(JSON.stringify(original));delete G.civicProjects;const f=civicProjectGrocer(),m=OUTSIDE_MARKETS[0],q=regionalQuote(f,m,'food','import'),total=totalMoney();
 if(!q)throw Error('Fixture has no connected market');civicProjectStart('food','bridge',f.id);
 const p=G.civicProjects.active.food,s=ensureRegionalTrade();if(dispatchRegional(f,'food',120,'import',q)!==120)throw Error('Project lot unavailable');const id=fromEnd(s.shipments).id;if(dispatchRegional(f,'food',60,'import',q)!==60)throw Error('Project second lot unavailable');p.orders=[id,fromEnd(s.shipments).id];
 for(let n=0;n<42;n++)if(dispatchRegional(f,'food',1,'import',q)!==1)throw Error('Overflow fixture could not pay for real cargo');
 for(let day=0;day<60&&s.shipments.length;day++){G.day++;regionalFreightDay();}
 if(s.recent.some(o=>o.id===id))throw Error('Fixture failed to overflow recent log');
 if(p.arrived!==180||p.orders.length)throw Error('Project lost delivery after bounded log overflow');regionalFreightDay();if(p.arrived!==180)throw Error('Delivery counted twice');
 if(Math.abs(totalMoney()-total)>.001)throw Error('Observer changed cash');const goodsError=Math.max(...goodsBalance().map(a=>Math.abs(a.error)));if(goodsError>.001)throw Error('Observer changed physical goods');
 if(!validateCivicProjects(G))throw Error('Observed project archive invalid');const metricBase=programmeMetrics;try{programmeMetrics=()=>({food:100});f.closed=true;if(civicProjectObservation(p).met)throw Error('Closed shop received a usable-food certificate');f.closed=false;if(!civicProjectObservation(p).met)throw Error('Staffed shop with commissioned arrivals and adequate food cannot complete');}finally{programmeMetrics=metricBase;f.closed=false;}
 return{commissionedArrival:p.arrived,recentRows:s.recent.length,realPaidDeliveries:s.delivered,cashDelta:totalMoney()-total,goodsError};
}finally{G=original;}};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':844,'height':390});page.set_content(html);page.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));page.locator('#townSeed').fill('42');page.locator('#newTown').click();page.locator('#pause').click();result=page.evaluate('__projectDeliveryOverflow()');b.close()
out=ROOT/'reports/civic-projects';out.mkdir(parents=True,exist_ok=True);(out/'freight-observer.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledStressFixture':True,**result},indent=2)+'\n')
print('PASS 44 actual paid deliveries overflowing recent log, commissioned arrival exactly once, unchanged cash/goods and valid archive')
