"""Bounded 48-route / 768-stop network, 2,000 riders; no per-frame route search."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
probe=r'''
window.__transitScale=()=>{
 const original=G;try{
 G=JSON.parse(JSON.stringify(G));G.buildings=[];G.households=[];G.people=[];G.firms=[];G.projects=[];G.landUse={};G.fieldOwner={};G.fieldCount={};G.tiles=new Array(T*T).fill(0);G.transit=null;G.region=10000000;G.treasury=5000000;G.day=100;G.nextId=1;G.roadWear=new Array(T*T).fill(100);G.policy.incomeTax=0;G.policy.minWage=24;
 for(let x=10;x<=45;x++){G.tiles[roadId(x,20)]=1;G.tiles[roadId(x,24)]=1;}for(let y=20;y<=24;y++)G.tiles[roadId(45,y)]=1;
 const b=(kind,x,y)=>{const v={id:G.nextId++,kind,x,y,value:10000,condition:100,owner:-1,firm:-1,hh:-1,footprint:footprintFor(x,y,kind)};G.buildings.push(v);return v;};
 const home=b('home',29,19),work=b('office',10,25),stations=[[9,20],[13,19],[17,19],[21,19],[25,19],[29,19],[33,19],[37,19],[41,19],[45,19],[46,22],[45,25],[37,25],[29,25],[21,25],[9,24]].map(([x,y])=>b('elevated_station',x,y).id),depots=[];
 for(let i=0;i<12;i++)depots.push(b('transit_depot',14+i*2,21));
 G.firms=[{id:0,building:work.id,closed:false,cash:0,workers:[]}];
 for(let i=0;i<2192;i++){const driver=i<192;G.households.push({id:i,name:'Fixture '+i,people:[i],home:home.id,cash:100,wages:0,tax:0,incomeTax:0,income:0,travel:0,travelDue:0});G.people.push({id:i,hh:i,age:30,health:100,skill:.8,job:driver?-1:0,publicIncome:0,publicWork:false,publicRole:'',previousPublicRole:''});if(!driver)G.firms[0].workers.push(i);}
 invalidateBuildingIndex();invalidateRoads(false);transitTopologyCache=null;transitDailyCache=null;
 for(let i=0;i<48;i++){const spec={mode:'elevated',depot:depots[i/4|0].id,stops:stations,level:1},q=transitQuote(spec);if(!q.ok||!buildTransitRoute(spec,q))throw Error(JSON.stringify(q));}
 const times=[];for(let i=0;i<5;i++){G.day++;G.people.forEach(p=>{p.publicWork=false;p.publicIncome=0;});const start=performance.now();transitOperatingDay();times.push(performance.now()-start);}
 const beforeHomes=transitRouting().homes.size;const start=performance.now();for(let i=0;i<100;i++){transitVehiclePoses(i,.1);transitVehiclePoses(i,1);}const poseMs=(performance.now()-start)/100;
 return {routes:G.transit.routes.length,nodes:transitRouting().nodes.length,times,poseMs,cacheStable:beforeHomes===transitRouting().homes.size,assigned:G.people.filter(p=>p.transitTrip?.day===G.day).length,drivers:G.transit.daily.staff,denied:G.transit.daily.denied};
 }finally{G=original;invalidateBuildingIndex();invalidateRoads(false);transitTopologyCache=null;transitDailyCache=null;}
};
'''
source=(ROOT/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click()
 result=p.evaluate('__transitScale()');print(json.dumps(result));assert result['routes']==48 and result['nodes']==768,result
 assert result['drivers']==192 and result['assigned']==2000 and result['denied']==0,result
 assert result['cacheStable'] and result['poseMs']<5,result
 assert sorted(result['times'])[2]<300,result
 (ROOT/'reports/transit-scale-8.json').write_text(json.dumps({'source_sha256':hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest(),'result':result,'passed':True},indent=2));b.close();print('PASS bounded 48 routes / 768 stops / 2,000 commuters, alternative-capacity assignment, unique 192 drivers, cached topology and visual-only pose budget')
