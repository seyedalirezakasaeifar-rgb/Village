"""Only successful, matching receipts advance civic food provision."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__arrivalSafety=()=>{const original=G,metrics=programmeMetrics;try{
 G=JSON.parse(JSON.stringify(original));delete G.civicProjects;const f=civicProjectGrocer(),m=OUTSIDE_MARKETS[0],s=ensureRegionalTrade(),total=totalMoney();civicProjectStart('food','bridge',f.id);let p=G.civicProjects.active.food;programmeMetrics=()=>({...metrics(),food:100});
 const order=qty=>{const n=dispatchRegional(f,'food',qty,'import',regionalQuote(f,m,'food','import'));if(n!==qty)throw Error('Paid fixture could not reserve cargo');const o=s.shipments.at(-1);p.orders.push(o.id);return o;};
 const cancelled=order(30);cancelRegionalShipment(cancelled.id);G.day++;regionalFreightDay();civicProjectsDay();if(p.arrived!==0||p.status==='complete'||p.orders.length)throw Error('Cancellation counted as arrival');
 p.orders.push(++s.serial);G.day++;regionalFreightDay();civicProjectsDay();if(p.arrived!==0||p.status==='complete'||p.orders.length)throw Error('Missing record counted as arrival');
 const returned=order(30);while(returned.stage!=='outside'){G.day++;regionalFreightDay();civicProjectsDay()}cancelRegionalShipment(returned.id);for(let i=0;i<30&&s.shipments.some(o=>o.id===returned.id);i++){G.day++;regionalFreightDay();civicProjectsDay()}if(p.arrived!==0||p.status==='complete')throw Error('Supplier return counted as arrival');
 const first=order(120),second=order(60);for(let i=0;i<40&&s.shipments.length;i++){G.day++;regionalFreightDay();civicProjectsDay()}if(p.arrived!==180||p.status!=='complete')throw Error('Real deliveries did not earn progress');const receipt=s.recent.find(o=>o.id===first.id);civicProjectRecordArrival(receipt);if(p.arrived!==180)throw Error('Repeated receipt awarded twice');
 // A legacy metadata snapshot can recover a real successful recent receipt;
 // it cannot reconstruct progress merely because an order is absent.
 p.status='active';delete p.completed;p.arrived=60;p.orders=[first.id];p.lastDay=G.day-1;G.civicProjects.lastDay=G.day-1;const saved=JSON.stringify(G);if(!hydrateSave(saved))throw Error('Legacy metadata snapshot rejected');p=G.civicProjects.active.food;programmeMetrics=()=>({...metrics(),food:100});civicProjectsDay();if(p.arrived!==180)throw Error('Legacy successful receipt not recovered');civicProjectRecordArrival(receipt);if(p.arrived!==180)throw Error('Legacy receipt awarded twice');
 const drift=totalMoney()-total,error=Math.max(...goodsBalance().map(a=>Math.abs(a.error)));if(Math.abs(drift)>.001||error>.001)throw Error('Progress changed cash or commodities');return{cancelledRejected:true,missingRejected:true,returnedRejected:true,actualArrived:p.arrived,legacyRecoveredOnce:true,cashDrift:drift,goodsError:error};
}finally{programmeMetrics=metrics;G=original;}};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__arrivalSafety()');b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==hashlib.sha256(source.encode()).hexdigest()
out=ROOT/'reports/civic-projects';(out/'arrival-safety.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledReceiptFixture':True,**r},indent=2)+'\n');print('PASS cancelled/returned/missing cargo never awards civic progress; matching delivery and legacy receipt count exactly once',r)
