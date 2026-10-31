"""Controlled long-commute fixture: capacity, transfers, funding and strict conservation."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
probe=r'''
window.__transitCapacity=()=>{
 const original=G,originalRng=rngState,originalVisual=visualState;try{
 G=JSON.parse(JSON.stringify(G));G.buildings=[];G.households=[];G.people=[];G.firms=[];G.projects=[];G.landUse={};G.fieldOwner={};G.fieldCount={};G.tiles=new Array(T*T).fill(0);G.transit=null;G.region=1000000;G.treasury=250000;G.day=100;G.nextId=1;G.cumulative.spending=0;G.roadWear=new Array(T*T).fill(100);G.policy.incomeTax=0;G.policy.minWage=24;
 for(let x=10;x<=45;x++){G.tiles[roadId(x,20)]=1;G.tiles[roadId(x,24)]=1;}for(let y=20;y<=24;y++)G.tiles[roadId(45,y)]=1;
 const b=(kind,x,y)=>{const v={id:G.nextId++,kind,x,y,value:10000,condition:100,owner:-1,firm:-1,hh:-1,footprint:footprintFor(x,y,kind)};G.buildings.push(v);return v;};
 const home=b('apartment',11,18),work=b('office',11,25),driverHome=b('home',13,19),a=b('elevated_station',9,20),z=b('elevated_station',9,24),depot=b('transit_depot',10,21);
 // Apartment's 2x2 footprint borders the north road, and the office borders the south.
 G.firms=[{id:0,building:work.id,closed:false,cash:0,workers:[]}];
 for(let i=0;i<304;i++){const driver=i<4,h={id:i,name:'Fixture '+i,people:[i],home:driver?driverHome.id:home.id,cash:100,wages:0,tax:0,incomeTax:0,income:0,travel:0,travelDue:0},p={id:i,hh:i,age:30,health:100,skill:.8,job:driver?-1:0,publicIncome:0,publicWork:false,publicRole:'',previousPublicRole:''};G.households.push(h);G.people.push(p);if(!driver)G.firms[0].workers.push(i);}
 invalidateBuildingIndex();invalidateRoads(false);transitTopologyCache=null;transitDailyCache=null;
 const spec={mode:'elevated',depot:depot.id,stops:[a.id,z.id],level:1},quote=transitQuote(spec),before=totalMoney();if(!quote.ok)throw Error(JSON.stringify(quote));const route=buildTransitRoute(spec,quote);if(!route)throw Error('Route build failed');
 const noTransit=G.people.filter(p=>p.job>=0&&workerCanCommute(p,G.firms[0])).length;
 transitOperatingDay();const stats={...route.stats,staff:route.stats.staff.slice()},assigned=G.people.filter(p=>p.transitTrip),attending=G.people.filter(p=>p.job>=0&&workerCanCommute(p,G.firms[0])).length;
 for(const p of assigned)transitCollectFare(G.households[p.hh],p.transitTrip);
 const funded={stats,assigned:assigned.length,attending,denied:G.transit.daily.denied,fares:G.transit.daily.revenue,after:totalMoney(),before,noTransit};
 // Same day must not pay wages or allocate capacity twice.
 const snapshot=JSON.stringify(G.transit),moneyBefore=totalMoney();transitOperatingDay();const repeated=JSON.stringify(G.transit)===snapshot&&Math.abs(totalMoney()-moneyBefore)<.000001;
 // Break one owned road segment. Rail remains a physical asset but cannot run.
 const broken=roadId(45,22);G.tiles[broken]=0;invalidateRoads(false);G.day++;G.people.forEach(p=>{p.publicWork=false;p.publicIncome=0;});transitOperatingDay();const disrupted={capacity:route.stats.capacity,status:route.stats.status,poses:transitVehiclePoses(1,1).length};
 G.tiles[broken]=1;invalidateRoads(false);G.day++;G.people.forEach(p=>{p.publicWork=false;p.publicIncome=0;});
 G.region+=G.treasury;G.treasury=0;transitOperatingDay();const unfunded={capacity:route.stats.capacity,assigned:G.people.filter(p=>p.transitTrip?.day===G.day).length,attending:G.people.filter(p=>p.job>=0&&workerCanCommute(p,G.firms[0])).length};
 // Restore operating cash and add a second actual train route; overflow must use it.
 G.region-=200000;G.treasury+=200000;const second=buildTransitRoute(spec,transitQuote(spec));
 for(let i=0;i<4;i++){const id=G.people.length;G.households.push({id,name:'Relief driver',people:[id],home:driverHome.id,cash:100,wages:0,tax:0,incomeTax:0,income:0,travel:0,travelDue:0});G.region-=100;G.people.push({id,hh:id,age:30,health:100,skill:.8,job:-1,publicIncome:0,publicWork:false,publicRole:'',previousPublicRole:''});}
 G.day++;G.people.forEach(p=>{p.publicWork=false;p.publicIncome=0;});transitOperatingDay();const parallel={assigned:G.people.filter(p=>p.transitTrip?.day===G.day).length,denied:G.transit.daily.denied,second:second.stats.reserved};
 deleteTransitRoute(route.id);deleteTransitRoute(second.id);const middle=b('elevated_station',46,22);invalidateBuildingIndex();invalidateRoads(false);
 const left={...spec,stops:[a.id,middle.id]},right={...spec,stops:[middle.id,z.id]},lr=buildTransitRoute(left,transitQuote(left)),rr=buildTransitRoute(right,transitQuote(right));if(!lr||!rr)throw Error('Transfer routes could not be built');
 G.day++;G.people.forEach(p=>{p.publicWork=false;p.publicIncome=0;});transitOperatingDay();const transferring=G.people.filter(p=>p.transitTrip?.day===G.day);for(const p of transferring)transitCollectFare(G.households[p.hh],p.transitTrip);
 const transfers={assigned:transferring.length,twoLeg:transferring.filter(p=>p.transitTrip.routes.length===2).length,fares:G.transit.daily.revenue,rides:G.transit.daily.rides,boardings:G.transit.routes.map(r=>r.stats.boardings)};
 return {funded,repeated,disrupted,unfunded,parallel,transfers};
 }finally{G=original;rngState=originalRng;visualState=originalVisual;invalidateBuildingIndex();invalidateRoads(false);transitTopologyCache=null;transitDailyCache=null;}
};
'''
source=(ROOT/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click()
 result=p.evaluate('__transitCapacity()');print(json.dumps(result));f=result['funded'];assert f['noTransit']==0,result
 assert f['assigned']==f['attending']==f['stats']['capacity'] and f['assigned']>0,result
 assert f['assigned']+f['denied']==300,result
 assert abs(f['fares']-f['assigned']*1.25)<.000001,result
 assert abs(f['before']-f['after'])<.000001,result
 assert result['repeated'],result
 assert result['disrupted']['capacity']==result['disrupted']['poses']==0,result
 assert result['unfunded']=={'capacity':0,'assigned':0,'attending':0},result
 assert result['parallel']['assigned']==300 and result['parallel']['denied']==0 and result['parallel']['second']>0,result
 assert result['transfers']=={'assigned':300,'twoLeg':300,'fares':375,'rides':300,'boardings':[300,300]},result
 assert not errors,errors;(ROOT/'reports/transit-capacity-8.json').write_text(json.dumps({'source_sha256':hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest(),'result':result,'passed':True},indent=2));b.close();print('PASS funded rail changes actual job attendance, bounded peak capacity/denial, exact fares, payroll/capital conservation, same-day idempotence, physical disruption and no-funding alternative')
