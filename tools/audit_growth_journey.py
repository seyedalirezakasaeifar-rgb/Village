"""Integrated natural urban trajectories. No agent/cash/stock/land injections.

Uses authored scenario/seed resets, actual mayor buttons and clock acceleration.
Council letters follow the test clock's first-affordable normal choice rule.
"""
from pathlib import Path
import os,json,hashlib,gzip,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
seeds=[int(s) for s in os.environ.get('TOWNLEDGER_URBAN_SEEDS','42,101,909').split(',')]
years=int(os.environ.get('TOWNLEDGER_URBAN_YEARS','6'));scenario=os.environ.get('TOWNLEDGER_URBAN_SCENARIO','regional');arms=os.environ.get('TOWNLEDGER_URBAN_ARMS','market').split(',')
out=ROOT/'reports/urban-trajectories'/os.environ.get('TOWNLEDGER_URBAN_RUN','pilot');out.mkdir(parents=True,exist_ok=True)
probe=r'''
window.__urbanAudit={snapshot:()=>{const blocks=Object.values(urbanSpatial().blocks).map(b=>({key:b.key,buildings:b.buildings.length,residents:b.residents,jobs:b.jobs,farms:b.farms,retail:b.retail,income:b.perPersonIncome,rentBurden:b.rentBurden,condition:b.condition,band:b.incomeBand,character:G.urban.districts[b.key]?.character||b.character,changed:G.urban.districts[b.key]?.changed||null}));return {day:G.day,population:G.stats.population,treasury:G.treasury,debt:G.debt,region:G.region,employment:G.stats.employment,hardship:G.stats.hardship,confidence:G.stats.marketConfidence,food:G.market.unmetFood,school:G.serviceProvision?.school?.coverage||0,health:G.serviceProvision?.health?.coverage||0,blocks,households:G.households.filter(h=>h.people.length).map(h=>({id:h.id,home:h.home,people:h.people.length,income:Math.max(0,h.income-h.tax),rent:h.rent,liquid:householdLiquidity(h),stress:h.stress,relocated:h.lastRelocated||null,utility:h.utilityConnected,owner:readBuild(h.home)?.owner===h.id,school:localCivicCoverage('school',h.id)})),retail:G.firms.filter(f=>f.kind==='grocer').map(f=>({id:f.id,mall:!!f.retailCentre,closed:!!f.closed,opened:f.openedDay||1,closedDay:f.closedDay||null,cash:f.cash,jobs:f.jobs,staff:f.workers.length,price:f.price,sales:f.salesTrend,net:f.netProfit,revenue:f.revenue,food:f.stock.food||0,margin:f.marginTrend,expected:f.retailExpectedNet||null,catchment:f.retailCatchment||null})),farms:G.firms.filter(f=>f.kind==='farm').map(f=>{const b=readBuild(f.building);return{id:f.id,closed:!!f.closed,x:b?.x,y:b?.y,density:b?urbanDescriptor(b.x,b.y).density:null,fields:G.fieldCount[f.id]||0,production:f.production,rated:f.ratedOutput,stock:f.stock.grain||0,cash:f.cash,staff:f.workers.length,relocated:b?.lastRelocated||null}}),projects:G.projects.map(p=>({kind:p.kind,mall:!!p.retailCentre,renewal:!!p.urbanRenewal,rehousing:!!p.municipalRehousing,remaining:p.remaining})),districts:JSON.parse(JSON.stringify(G.urban.districts)),renewals:G.urban.renewals.slice(),owned:G.charter.owned.slice(),parcels:G.charter.owned.map(id=>({id,...districtMetrics(id)})),landPurchases:G.cumulative.landPurchases||0,houseMoves:G.transactions.filter(t=>t.reason==='Voluntary move to an affordable connected dwelling').map(t=>({day:t.day,amount:t.amount})),valid:validateTown()};},parcelCandidates:()=>ANNEX_PARCELS.filter(p=>!G.charter.owned.includes(p.id)&&parcelAdjacent(p)).map(p=>({id:p.id,price:parcelSurvey(p).price})),connection:id=>{const p=ANNEX_PARCELS.find(p=>p.id===id),net=graph(),cx=p.x+p.w/2,cy=p.y+p.h/2,prev=new Map(),queue=[];for(const at of net.neighbors.keys())if(net.parts[at]===net.mainPart){prev.set(at,-1);queue.push(at);}let end=null;for(let n=0;n<queue.length;n++){const at=queue[n],x=at%T,y=at/T|0;if(x>=p.x&&x<p.x+p.w&&y>=p.y&&y<p.y+p.h&&Math.abs(x-cx)+Math.abs(y-cy)<8){end=at;break;}for(const [dx,dy] of roadOffsets){const xx=x+dx,yy=y+dy,next=roadId(xx,yy);if(xx<2||yy<2||xx>=T-2||yy>=T-2||prev.has(next)||!charterOwns(xx,yy)||![0,1,3].includes(G.tiles[next])||G.landUse[next]||buildingAt(xx,yy))continue;prev.set(next,at);queue.push(next);}}if(end==null)return[];const path=[];for(let at=end;at>=0;at=prev.get(at))if(G.tiles[at]!==1)path.push({x:at%T,y:at/T|0});return path.reverse();},serviceSite:kind=>{const service=kind==='school'?'school':'health',homes=G.households.filter(h=>h.people.length).map(h=>({b:readBuild(h.home),need:h.people.length*(1-localCivicCoverage(service,h.id))})).filter(v=>v.b&&v.need>0),net=graph();let best=null;for(let y=3;y<T-3;y++)for(let x=3;x<T-3;x++){if(!canPlace(x,y,true,kind)||!roadOffsets.some(([dx,dy])=>net.parts[roadId(x+dx,y+dy)]===net.mainPart))continue;let score=0;for(const v of homes){const d=Math.abs(v.b.x-x)+Math.abs(v.b.y-y);if(d<12)score+=v.need*(1-d/12);}if(score>0&&(!best||score>best.score))best={x,y,score};}return best;},placed:(x,y,kind)=>kind==='road'?G.tiles[roadId(x,y)]===1:buildingAt(x,y)?.kind===kind,projectedPoint:(x,y)=>{const q=iso(x,y);return{x:q[0],y:q[1]+18};}};
'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
results={'source_sha256':sha,'baseCommit':'6e8665e3cdee520148f44947e49cdc8e7ddae4c6','scenario':scenario,'years':years,'seeds':seeds,'clockPolicy':'First affordable normal council choice; no injected funds/agents/land/stock.','runs':[]}
if os.environ.get('TOWNLEDGER_URBAN_RESUME')=='1' and (out/'audit.json').exists():
 prior=json.loads((out/'audit.json').read_text());assert prior['source_sha256']==sha and prior['years']==years and prior['scenario']==scenario
 results['runs']=[r for r in prior['runs'] if len(r['samples'])==years*4 and 'seconds' in r and (out/f"{scenario}-{r['seed']}-{r['arm']}.json.gz").exists()]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for seed in seeds:
  for arm in arms:
   if any(r['seed']==seed and r['arm']==arm for r in results['runs']):continue
   p=browser.new_page(viewport={'width':1280,'height':800});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/assets/game.js',lambda route:route.fulfill(status=200,content_type='application/javascript',body=script));p.goto((ROOT/'assets/index.html').as_uri());p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('s=>__townTest.reset("'+scenario+'",s)',seed)
   run={'seed':seed,'arm':arm,'samples':[],'actions':[],'started':time.time()};total=p.evaluate('__townTest.get().total')
   def place(kind,site):
    if not p.locator('[data-panel=construction]').evaluate('e=>e.classList.contains("active")'):p.locator('[data-panel=construction]').click()
    p.locator('[data-build-category=all]').click();button=p.locator('[data-build='+kind+']')
    if button.is_disabled():return False
    button.click();point=p.evaluate('s=>__urbanAudit.projectedPoint(s.x,s.y)',site);p.evaluate('a=>__townTest.capture({x:a.x,y:a.y,zoom:.9})',point);box=p.locator('#view').bounding_box();p.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2);p.keyboard.press('Escape');return p.evaluate('s=>__urbanAudit.placed(s.x,s.y,s.kind)',{**site,'kind':kind})
   for quarter in range(years*4):
    p.evaluate('__townTest.step(90)');snap=p.evaluate('__urbanAudit.snapshot()');assert snap['valid']['ok'],snap['valid'];assert abs(snap['valid']['total']-total)<.1;assert not errors,errors
    run['samples'].append(snap)
    # Real proposal controls, no forced success. Every rejected invitation remains in evidence.
    if quarter%2==0:
     p.locator('[data-panel=construction]').click();p.locator('#urbanPlanningOffice>summary').click();p.locator('[data-urban-retail]').click();message=p.locator('#toast').inner_text();run['actions'].append({'day':snap['day'],'action':'retail invitation','message':message})
    # Planned arm spends only actual available cash, retaining a disclosed reserve.
    if arm=='planned' and quarter in [1,3,5,7,9,11]:
     candidates=p.evaluate('__urbanAudit.parcelCandidates()');choice=next((q for q in candidates if snap['treasury']>q['price']+40000),None)
     if choice:
      if not p.locator('#panel').evaluate('e=>e.classList.contains("show")'):p.locator('[data-panel=construction]').click()
      office=p.locator('#charterOffice');
      if not office.evaluate('e=>e.open'):office.locator(':scope>summary').click()
      p.locator('[data-parcel-buy='+choice['id']+']').click();p.locator('[data-event-choice="0"]').click();run['actions'].append({'day':snap['day'],'action':'annexation','id':choice['id'],'paid':choice['price']})
      # Select an actual charter and pay for a legal street connection.
      p.get_by_text('District commitments & development programmes',exact=True).click();focus='industry' if quarter in [5,17] else 'neighbourhood';focus_button=p.locator('[data-district-id="'+choice['id']+'"][data-district-focus="'+focus+'"]');focus_button.locator('..').locator(':scope>summary').click();focus_button.click();p.locator('[data-event-choice="0"]').click();path=p.evaluate('id=>__urbanAudit.connection(id)',choice['id']);built=0
      for cell in path[:80]:
       if not place('road',cell):break
       built+=1
      run['actions'].append({'day':snap['day'],'action':'connected district charter','id':choice['id'],'focus':focus,'roadTiles':built,'roadCapital':built*150,'proposedRoadTiles':len(path)})
    if arm=='planned' and quarter%4==3 and snap['treasury']>80000:
     for kind,coverage,key,increase in [('school',snap['school'],'educationBudget',100),('clinic',snap['health'],'healthBudget',70)]:
      if coverage>=.65:continue
      site=p.evaluate('k=>__urbanAudit.serviceSite(k)',kind)
      if not site or not place(kind,site):continue
      p.locator('[data-panel=policies]').click();p.get_by_text('Government services',exact=True).click();slider=p.locator('input[data-policy='+key+']');value=float(slider.input_value());limit=float(slider.get_attribute('max'));target=min(limit,value+increase);
      if target>value:slider.fill(str(int(target)));p.locator('#enactPolicy').click()
      run['actions'].append({'day':snap['day'],'action':'funded local service','kind':kind,'site':site,'policy':key,'authorization':target})

    if p.locator('#panel').evaluate('e=>e.classList.contains("show")'):p.locator('#panelClose').click()
    if quarter%4==3:
     print(scenario,seed,arm,'year',(quarter+1)//4,'population',snap['population'],'treasury',round(snap['treasury']),'malls',sum(f['mall'] and not f['closed'] for f in snap['retail']),'grocers',sum(not f['closed'] for f in snap['retail']),'hardship',snap['hardship'],flush=True)
    results['runs']=results['runs']+[run] if quarter==0 else results['runs'];(out/'audit.json').write_text(json.dumps(results,indent=2)+'\n')
   run['seconds']=time.time()-run.pop('started');run['errors']=errors;run['final']=p.evaluate('__urbanAudit.snapshot()');archive=p.evaluate('__townTest.save()');(out/f'{scenario}-{seed}-{arm}.json.gz').write_bytes(gzip.compress(archive.encode(),mtime=0));p.close()
 browser.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
(out/'audit.json').write_text(json.dumps(results,indent=2)+'\n');print('Saved',out,flush=True)
