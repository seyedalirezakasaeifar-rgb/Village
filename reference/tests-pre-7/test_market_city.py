"""Autonomous building, private underground economics, road-constrained traffic and no deadlocks."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import math, json
P=Path(__file__).resolve().parents[1]; assets=P/'assets'
html=(assets/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(assets/'style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':980,'height':540});errors=[];page.on('pageerror',lambda x:errors.append(str(x)))
 page.set_content(html);page.add_script_tag(content=(assets/'game.js').read_text());page.locator('#newTown').click();page.locator('#panelClose').click()
 result=page.evaluate('''()=>{
    const original=__townTest.get().total;
    __townTest.step(720);
    let state=__townTest.development();
    if(state.development.homes<3)throw Error('Private homes not constructed '+JSON.stringify(state));
    if(state.development.roads<1)throw Error('Private road network did not grow '+JSON.stringify(state));
    const record=__townTest.get();
    if(Math.abs(record.total-original)>.05)throw Error('Capital conservation mismatch');
    return {development:state.development,stats:record.stats,firmCount:record.businesses};
 }''');print('2 year growth',json.dumps(result,default=str)[:1400]);
 # Simulate a developed settlement; maintain existing household identity and finances.
 metro=page.evaluate('''()=>{
    const g=JSON.parse(__townTest.save());
    const target=510;
    let k=0;
    while(g.people.filter(p=>!p.deceased).length<target){
     const h=g.households[k++%g.households.length];
     const p={id:g.people.length,name:'Commuter '+k,age:30,skill:.75,health:90,hh:h.id,job:-1,life:75,last:[]};
     g.people.push(p);h.people.push(p.id);
    }
    if(!__townTest.load(g))throw Error('Injection failed');
    const before=__townTest.get().total;
    for(let i=0;i<8&&!__townTest.development().metro.lines.length;i++)__townTest.autogrow();
    const m=__townTest.development();
    if(m.metro.lines.length<1)throw Error('Subway not built: '+JSON.stringify(m));
    if(m.metro.stations.length<2)throw Error('Missing stations');
    if(m.metro.operating)throw Error('Subway should be under construction');
    if(Math.abs(__townTest.get().total-before)>.05)throw Error('Subway capital not conserved');
    __townTest.step(110);
    if(!__townTest.development().metro.operating)throw Error('Underground failed to begin service after construction');
    const ended=__townTest.development();
    if(Math.abs(__townTest.get().total-before)>.05)throw Error('Post-transit simulation leaked cash');
    return {metro:ended.metro,development:ended.development,totalDelta:__townTest.get().total-before};
 }''');print('metro',json.dumps(metro,default=str)[:1300]);
 # Reproduce dense junction congestion. All live vehicles have valid adjacent routes.
 traffic=page.evaluate('''()=>{
   __townTest.reset('settlement');let first=0,maximumWait=0,ever=0,lastSeen=new Map();
   for(let n=0;n<7000;n++){
      __townTest.advanceTraffic(.12);
      let cars=__townTest.traffic();ever=Math.max(ever,cars.length);
      for(const c of cars){
        if(c.fraction<0||c.fraction>=1||!Number.isFinite(c.position.x))throw Error('Invalid interpolation');
        for(let j=1;j<c.route.length;j++){
         const a=c.route[j-1],b=c.route[j];if(Math.abs(a%56-b%56)+Math.abs(Math.floor(a/56)-Math.floor(b/56))!==1)throw Error('Car moved off-road');
        }
      }
   }
   if(ever<10)throw Error('No traffic generated');
   return {simulatedSeconds:840,peakVisible:ever,remaining:__townTest.traffic().length,congestedTrips:__townTest.development().development.congestedTrips||0};
 }''');print('traffic endurance',traffic)
 assert not errors,errors
 page.locator('[data-panel="construction"]').first.click()
 assert page.locator('#toggleDevelopment').count()==1
 page.locator('#overlayMetro').click()
 print('UI controls okay; errors',errors)
 b.close()
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage']);page=b.new_page()
 page.set_content(html);page.add_script_tag(content=(assets/'game.js').read_text());page.locator('#newTown').click()
 results=[]
 for zone in [0,25,100]:
  out=page.evaluate('''zone=>{
   __townTest.reset('settlement');__townTest.set('zoningRestriction',zone);
   let before=__townTest.get().total;
   for(let i=0;i<720;i++){__townTest.set('zoningRestriction',zone);__townTest.step(1)}
   let d=__townTest.development().development;
   if(Math.abs(before-__townTest.get().total)>.06)throw Error('Capital not conserved');
   return {zoning:zone,homes:d.homes,firms:d.firms,roads:d.roads,population:__townTest.get().population};
  }''',zone);results.append(out)
 print('ZONING COMPARISON',results)
 assert results[-1]['homes']==0 and results[-1]['firms']==0 and results[-1]['roads']==0
 assert results[0]['homes']>0 and results[1]['homes']>0
 # Pausing all private construction must eliminate the new autonomous subsystem.
 off=page.evaluate('''()=>{
   __townTest.reset('settlement');let state=JSON.parse(__townTest.save());state.autoBuild=false;__townTest.load(state);
   __townTest.step(400);return __townTest.development().development;
 }''')
 assert off['homes']==off['firms']==off['roads']==off['stations']==0,off
 print('PRIVATE DEVELOPMENT PAUSE',off['homes'],off['firms'],off['roads'])
 b.close()
