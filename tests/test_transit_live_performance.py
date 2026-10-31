"""Whole-game 64x + actual buses + optional integrated graphics, RAF and UI.

TOWNLEDGER_TRANSIT_BENCH_ROOT can select a separate source worktree containing the
final graphics commit. Both engine versions use that same graphics/economy. The
48-route pure 2,000-rider routing benchmark remains a separate stress test; this
fixture measures actual complete game frames, paid bus operations and UI.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,hashlib,os,time,math
ROOT=Path(__file__).resolve().parents[1]
SOURCE_ROOT=Path(os.environ.get('TOWNLEDGER_TRANSIT_BENCH_ROOT',str(ROOT)))
source=(SOURCE_ROOT/'assets/game.js').read_text();digest=hashlib.sha256(source.encode()).hexdigest()
html=(SOURCE_ROOT/'assets/index.html').read_text().replace('<script src="game.js"></script>','')
for sheet in ['style.css','vale.css','civic7.css','mayor8.css']:
 html=html.replace('<link rel="stylesheet" href="'+sheet+'">','<style>'+(SOURCE_ROOT/'assets'/sheet).read_text()+'</style>')
reference=(ROOT/'tests/fixtures/transit-reference-eb2e88c.js').read_text()
start=source.index('// SOURCE: 46-transit-network.js');end=source.index('// SOURCE:',start+10)
baseline=source[:start]+'// SOURCE: 46-transit-network.js\n'+reference+'\n'+source[end:]
probe=r'''
window.__transitLive={
 large:()=>{
  chosenScenario='settlement';seed(42);const g=JSON.parse(archivePayload()),occupied=new Set(g.buildings.flatMap(b=>b.footprint||[b.y*g.gridSize+b.x])),free=[];
  for(let y=3;y<53;y++)for(let x=3;x<53;x++){const id=y*g.gridSize+x;if(g.tiles[id]===0&&!occupied.has(id)&&!g.landUse?.[id])free.push([x,y]);}
  let n=0;while(g.people.length<2000&&n<free.length){const [x,y]=free[n],id=g.households.length,h={id,name:'Newcomer '+n,cash:500,home:g.nextId,owner:id,people:[],income:0,rent:0,food:0,tax:0,aid:0,crimeLoss:0,stress:25,security:80,last:[],worklessness:0},b={id:g.nextId++,kind:'home',x,y,value:25000,condition:100,owner:id,firm:-1,hh:id};g.buildings.push(b);g.homes.push(b.id);g.households.push(h);g.region-=500;
   for(let age=0;age<3&&g.people.length<2000;age++){const pid=g.people.length;g.people.push({id:pid,name:'Resident '+pid,age:26+age*3,skill:.5,health:80,hh:id,job:-1,life:70,last:[]});h.people.push(pid);}n++;}
  if(g.people.length!==2000||!hydrateSave(g))throw Error('Large fixture rejected');return {population:G.stats.population,households:G.households.length,buildings:G.buildings.length,total:totalMoney()};
 },
 build:count=>{
  const injection=Math.min(G.region,2000000);G.region-=injection;G.treasury+=injection;const depots=[];
  for(let i=0;i<Math.ceil(count/8);i++){let lot=null;for(let y=2;y<T-3&&!lot;y++)for(let x=2;x<T-3&&!lot;x++)if(canPlace(x,y,true,'transit_depot'))lot={x,y};if(!lot)throw Error('No depot footprint');depots.push(buildTransitFacility('transit_depot',lot.x,lot.y));}
  const node=(x,y)=>roadId(x,y),corridors=[[node(15,27),node(27,27),node(43,27)],[node(27,13),node(27,27),node(27,43)],[node(15,21),node(27,21),node(43,21)],[node(15,35),node(27,35),node(43,35)],[node(15,13),node(27,13),node(43,13)],[node(15,43),node(27,43),node(43,43)],[node(21,13),node(21,27),node(21,35)],[node(35,13),node(35,27),node(35,43)],[node(15,13),node(15,27),node(15,43)],[node(43,13),node(43,27),node(43,43)]];
  for(let i=0;i<count;i++){const spec={mode:'bus',depot:depots[i/8|0].id,stops:corridors[i%corridors.length],level:1},q=transitQuote(spec);if(!q.ok||!buildTransitRoute(spec,q))throw Error('Live bus quote failed: '+JSON.stringify(q));}
  tick();return {routes:count,depots:depots.length,drivers:G.transit.daily.staff,rides:G.transit.daily.rides,capacity:G.transit.routes.reduce((sum,r)=>sum+r.stats.capacity,0),total:totalMoney()};
 },
 status:()=>({routes:G.transit.routes.length,operating:G.transit.routes.filter(r=>r.stats.operating).length,drivers:G.transit.daily.staff,rides:G.transit.daily.rides,fares:G.transit.fares,capacity:G.transit.routes.reduce((sum,r)=>sum+r.stats.capacity,0),nodeCount:transitRouting().nodes.length,treasury:G.treasury,valid:validateTown()})
};
'''

def q(a,p):
 a=sorted(a);return a[min(len(a)-1,math.floor(len(a)*p))] if a else 0

result={'source_sha256':digest,'engine_module_sha256':hashlib.sha256((SOURCE_ROOT/'src/46-transit-network.js').read_bytes()).hexdigest(),'source_root':str(SOURCE_ROOT),'physicalAndroid':False,'hostChromium':True,'rows':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for routes,implementation in [(0,'optimized'),(8,'baseline'),(8,'optimized'),(12,'baseline'),(12,'optimized'),(48,'baseline'),(48,'optimized')]:
  page=browser.new_page(viewport={'width':844,'height':390},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);code=source if implementation=='optimized' else baseline;page.add_script_tag(content=code.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));page.locator('#newTown').click();page.locator('#pause').click();assert not errors,errors
  town=page.evaluate('__transitLive.large()');network=page.evaluate('(n)=>__transitLive.build(n)',routes);page.locator('#panelClose').click();page.locator('#speedRange').fill('6');page.locator('#pause').click();page.wait_for_timeout(700)
  page.evaluate('()=>{const p=__townTest.perf();p.frames.length=0;p.ticks.length=0;}');initial=page.evaluate('__townTest.get()');started=time.perf_counter()
  raf=page.evaluate('''()=>new Promise(resolve=>{const times=[];let previous=0,started=performance.now();function sample(now){if(previous)times.push(now-previous);previous=now;if(now-started<8000)requestAnimationFrame(sample);else resolve(times);}requestAnimationFrame(sample);})''')
  elapsed=time.perf_counter()-started;final=page.evaluate('__townTest.get()');perf=page.evaluate('''()=>{const p=__townTest.perf();return {frames:p.frames,ticks:p.ticks,effective:p.effective,backlog:p.backlog};}''');ui=[]
  for panel in ['economy','citizens','construction','settings']:
   latency=page.evaluate('''panel=>{const start=performance.now();document.querySelector('[data-panel='+panel+']').click();return new Promise(resolve=>requestAnimationFrame(()=>resolve(performance.now()-start)));}''',panel);body=page.locator('#panelBody').inner_text();ui.append({'panel':panel,'toNextFrameMs':latency,'error':'Panel error' in body});page.locator('#panelClose').click()
  page.locator('#pause').click();status=page.evaluate('__transitLive.status()');row={'implementation':implementation,'routes':routes,'initialTown':town,'initialNetwork':network,'endNetwork':status,'requestedSpeed':64,'elapsedSeconds':elapsed,'simulatedDays':final['day']-initial['day'],'measuredRate':(final['day']-initial['day'])*1.65/elapsed,'effectiveRate':perf['effective'],'tickMedianMs':q(perf['ticks'],.5),'tickP95Ms':q(perf['ticks'],.95),'drawMedianMs':q(perf['frames'],.5),'drawP95Ms':q(perf['frames'],.95),'rafP95Ms':q(raf,.95),'rafP99Ms':q(raf,.99),'ui':ui,'moneyDrift':abs(final['total']-town['total']),'errors':errors};result['rows'].append(row);(ROOT/'reports/transit-live-8.json').write_text(json.dumps(result,indent=2));print(json.dumps(row),flush=True)
  assert row['moneyDrift']<.1 and not errors and status['valid']['ok'] and all(not u['error'] for u in ui),row
  if implementation=='optimized':
   assert row['simulatedDays']>=100 and row['effectiveRate']>=40 and row['measuredRate']>=55,row
   assert row['rafP99Ms']<500 and all(u['toNextFrameMs']<250 for u in ui),row
   assert row['drawP95Ms']<50,row
  page.close()
 browser.close()
assert hashlib.sha256((SOURCE_ROOT/'assets/game.js').read_bytes()).hexdigest()==digest
print('PASS complete 2,000-resident game at requested 64x with funded 8/12/48-route networks, actual UI, RAF, painting, conservation and unchanged source')
