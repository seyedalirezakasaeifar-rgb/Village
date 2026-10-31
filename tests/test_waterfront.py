"""Productive shore sites, finite shared catch, paid/competitive cargo and boats."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
probe=r'''
window.__waterfrontProbe=()=>{const original=G,options={...gameOptions},clock=frameClock;try{
 G=JSON.parse(JSON.stringify(original));invalidateRoads();const fish=G.firms.find(f=>f.kind==='fishery'),wharf=G.firms.find(f=>f.kind==='wharf');if(!fish||!wharf)throw Error('Founding working waterfront missing');
 const b=readBuild(wharf.building),site=waterfrontSite(b.x,b.y,'wharf'),outlet=waterOutletPath(site.id),total=totalMoney(),cash=wharf.cash;
 waterDayTown=null;prepareWaterfrontDay();const seller=G.firms.find(f=>f.kind==='farm'),road=exportRoutes(seller).find(r=>r.mode==='road'),river=exportRoutes(seller).find(r=>r.mode==='river');
 const held=seller.stock.grain,sold=settleRegionalExport(seller,'grain',Math.min(20,held),2);const receipt=wharf.cash-cash,manifest=G.waterway.manifests.find(m=>m.started===G.day&&m.port===wharf.id&&m.good==='grain');
 const cashConserved=Math.abs(totalMoney()-total)<.00001,goodsTransferred=Math.abs(held-seller.stock.grain-sold)<.00001&&manifest?.qty>=sold;
 wharf.closed=true;const noClosedRoute=!exportRoutes(seller).some(r=>r.mode==='river');wharf.closed=false;const workers=wharf.workers,attending=wharf.attendingWorkers;wharf.workers=[];wharf.attendingWorkers=[];waterDayTown=null;prepareWaterfrontDay();const noUnstaffedRoute=!exportRoutes(seller).some(r=>r.mode==='river');wharf.workers=workers;wharf.attendingWorkers=attending;waterDayTown=null;prepareWaterfrontDay();
 // A finite handling budget is shared by actual exports and then road fallback.
 const capacity=wharf.cargoCapacity;for(const route of operatingWharves)route.remaining=3;const prior=wharf.cargoToday;settleRegionalExport(seller,'grain',Math.min(12,seller.stock.grain),2);const bounded=wharf.cargoToday-prior<=3.000001;
 const landRejected=!waterfrontSite(27,27,'fishery')&&!canPlace(28,25,false,'wharf');
 const lake=waterNetwork().components.find(c=>!c.gates.length&&c.cells.length>=8);let lakeFish=false,lakeWharf=false;
 for(const cell of lake.cells){for(const [dx,dy] of roadOffsets){const x=cell%T+dx,y=(cell/T|0)+dy;if(cityCell(x,y)!==2){lakeFish=!!waterfrontSite(x,y,'fishery');lakeWharf=!!waterfrontSite(x,y,'wharf');if(lakeFish)break;}}if(lakeFish)break;}
 // Repeated fisheries share the same ecological stock; no new money or fish.
 const twins=[];for(let i=0;i<10;i++)twins.push({...fish,id:1000+i,workers:fish.workers.slice(),attendingWorkers:fish.attendingWorkers?.slice()});waterDayTown=null;prepareWaterfrontDay([fish,...twins,wharf]);const allowance=[fish,...twins].reduce((n,f)=>n+f.fishingAllowance,0),naturalLimit=waterNetwork().components[fish.waterPart].catchCapacity,shared=allowance<=naturalLimit+.000001;
 Object.assign(gameOptions,{effects:true,traffic:true,reducedMotion:false,quality:'high'});cam.zoom=1;const economicBefore=JSON.stringify(G),rng=rngState;frameClock=15;const actors=waterfrontActors(()=>true),validBoat=actors.some(a=>a.cargo==='grain'||a.cargo==='fish'),high=actors.length;const barge=actors.find(a=>a.cargo!=='fish'),sameClock=waterfrontActors(()=>true).find(a=>a.id===barge?.id),pausedStable=!!barge&&sameClock.x===barge.x&&sameClock.y===barge.y;let continuous=false;if(barge){const record=G.waterway.manifests.slice().reverse().find(m=>m.port===barge.f.id),oldId=record.id,oldGood=record.good;record.id+=1000;record.good='manufactures';frameClock+=.1;const next=waterfrontActors(()=>true).find(a=>a.id===barge.id);continuous=!!next&&next.cargo===barge.cargo&&Math.hypot(next.x-barge.x,next.y-barge.y)<8;record.id=oldId;record.good=oldGood;}gameOptions.reducedMotion=true;const reduced=waterfrontActors(()=>true).length;gameOptions.reducedMotion=false;gameOptions.quality='low';const low=waterfrontActors(()=>true).length;
 return {site:!!site,outletLength:outlet.length,outletAtBoundary:[0,T-1].includes(outlet[outlet.length-1]/T|0),roadQuote:road.unit,riverQuote:river?.unit,sold,receipt,cashConserved,goodsTransferred,noClosedRoute,noUnstaffedRoute,bounded,capacity,landRejected,lakeFish,lakeWharf,shared,allowance,naturalLimit,validBoat,pausedStable,continuous,high,reduced,low,visualIndependent:economicBefore===JSON.stringify(G)&&rng===rngState};
 }finally{G=original;Object.assign(gameOptions,options);frameClock=clock;invalidateRoads();staticDirty=true;dirty=true;}};
'''
script=source.decode().replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("settlement",42)');p.evaluate('__townTest.step(5)');r=p.evaluate('__waterfrontProbe()')
 for key in ['site','outletAtBoundary','cashConserved','goodsTransferred','noClosedRoute','noUnstaffedRoute','bounded','landRejected','lakeFish','shared','validBoat','pausedStable','continuous','visualIndependent']:assert r[key],(key,r)
 assert not r['lakeWharf'] and r['sold']>0 and r['receipt']>0 and r['riverQuote']<r['roadQuote'] and r['high']<=10 and r['reduced']==r['low']==0,r
 saved=p.evaluate('__townTest.save()');g=json.loads(saved);assert g['waterway']['exports']>0 and any(f.get('production',0)>0 for f in g['firms'] if f['kind']=='fishery');assert p.evaluate('s=>__townTest.load(s)',saved);assert p.evaluate('__townTest.validate().ok')
 for change in ['g.waterway.manifests[0].qty=-1','g.waterway.manifests[0].path=[1,2]','g.waterway.manifests[0].ownership="town"','g.waterway.manifests[0].port=0','g.waterway.serial=-1']:
  assert p.evaluate('''code=>{const raw=__townTest.save(),g=JSON.parse(raw);new Function('g',code)(g);return !__townTest.load(g)&&__townTest.save()===raw;}''',change),change
 p.locator('[data-panel=construction]').click();p.locator('[data-build-category=waterfront]').click();assert p.locator('[data-build=wharf]').count()==1 and p.locator('[data-build=fishery]').count()==1
 p.locator('#panelClose').click();p.evaluate('__townTest.capture({x:92,y:470,zoom:1.15})')
 # Find river camera through its actual interface, then capture original pixels.
 p.locator('[data-panel=construction]').click();p.locator('summary',has_text='Working waterfront').click();p.locator('[data-waterfront-camera]').click();p.wait_for_timeout(100);out=ROOT/'reports/development-waterfront';out.mkdir(exist_ok=True);p.screenshot(path=str(out/'working-river-844x390.png'))
 before=p.evaluate('__townTest.get().total');p.evaluate('__townTest.step(360)');assert p.evaluate('__townTest.validate().ok');assert abs(p.evaluate('__townTest.get().total')-before)<.001;assert max(abs(x['error']) for x in p.evaluate('__townTest.goods()'))<.001;assert not errors,errors;b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
(out/'waterfront.json').write_text(json.dumps({'source_sha256':sha,'probe':r,'durationDays':365,'cashAndGoodsConserved':True},indent=2)+'\n');print('PASS productive fisheries, shared catch, staffed paid cargo, cheaper routes, road fallback, lake/outlet restrictions, saved manifests, bounded purposeful boats, UI, 365-day cash/goods')
