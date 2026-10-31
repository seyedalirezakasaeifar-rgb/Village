"""Ordinary-funded employment growth on a purchased, passenger-connected parcel."""
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright
import json, hashlib

source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__parcelEmployment={
 setup:()=>{
  const opening=totalMoney(),p=ANNEX_PARCELS.find(p=>p.id==='east-meadow');
  if(!purchaseParcel(p.id,parcelSurvey(p).price))throw Error('Ordinary East Meadow deed failed');
  const border=[...graph().neighbors.keys()].find(id=>id%T===55&&id/T>=2&&id/T<28&&graph().parts[id]===graph().mainPart);if(border==null)throw Error('No connected original street at district edge');
  const y=border/T|0;if(G.tiles[roadId(56,y)]!==1)construct('road',56,y);
  const outRoad=roadId(56,y),homeSite=Array.from({length:p.w*p.h},(_,i)=>({x:p.x+i%p.w,y:p.y+(i/p.w|0)})).find(q=>canPlace(q.x,q.y,true,'home'));
  if(!homeSite)throw Error('No legal connected cottage lot');construct('home',homeSite.x,homeSite.y);const home=buildingAt(homeSite.x,homeSite.y);if(!home)throw Error('Ordinary cottage purchase failed');
  const network=graph(),employer=G.firms.find(f=>!f.closed&&f.kind==='grocer'&&f.workers.length),goal=network.portals.get(employer.building),depotSite=buildableCandidates('business').find(q=>canPlace(q.x,q.y,true,'transit_depot'));
  const depot=depotSite&&buildTransitFacility('transit_depot',depotSite.x,depotSite.y);if(!depot)throw Error('Could not afford a normal municipal depot');
  const spec={mode:'bus',depot:depot.id,stops:[outRoad,goal],level:2},quote=transitQuote(spec),route=quote.ok&&buildTransitRoute(spec,quote);if(!route)throw Error('Could not authorize the ordinary quoted bus route: '+JSON.stringify(quote));
  __townTest.step(1);const outlook=parcelGrowthOutlook(p.id);if(!outlook)throw Error('Purchased deed has no growth outlook');
  const prehire=G.people.filter(person=>!person.deceased&&!person.movedAway&&person.job<0&&!person.publicWork&&!person.previousPublicRole).map(person=>person.id);
  const farmSite=Array.from({length:p.w*p.h},(_,i)=>({x:p.x+i%p.w,y:p.y+(i/p.w|0)})).find(q=>canPlace(q.x,q.y,true,'farm'));
  if(!farmSite)throw Error('No legal roadside production site');const employedBeforeFarm=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.job>=0).length,treasuryBefore=G.treasury,regionBefore=G.region,totalBefore=totalMoney();construct('farm',farmSite.x,farmSite.y);const building=buildingAt(farmSite.x,farmSite.y),farm=G.firms.find(f=>!f.closed&&f.kind==='farm'&&f.building===building?.id);if(!farm)throw Error('Ordinary enterprise placement failed');
  return {opening,site:homeSite,farmSite,employer:employer.id,route:route.id,routeQuote:{cost:quote.cost,operating:quote.operating,capacity:quote.capacity},jobseekerCount:prehire.length,prehire,employedBeforeFarm,municipalFarmCost:buildCost.farm,regionalOpeningCapital:12000,farmAfterConstruction:{id:farm.id,jobs:farm.jobs,workers:farm.workers.slice(),cash:farm.cash,fields:G.fieldCount[farm.id]||0},treasuryBefore,treasuryAfter:G.treasury,regionBefore,regionAfter:G.region,totalBefore,totalAfter:totalMoney(),outlook:{vacancies:outlook.cityVacancies,fundedVacancies:outlook.fundedVacancies,jobseekers:outlook.jobseekers,offers:outlook.arrival?.offers.length||0,businessDemand:outlook.businessDemand,investorBlocks:outlook.investorBlocks,sites:outlook.employmentSites}};
 },
 snapshot:s=>{const f=G.firms[s.farmAfterConstruction.id];return {day:G.day,treasury:G.treasury,region:G.region,total:totalMoney(),farm:{closed:!!f.closed,jobs:f.jobs,workers:f.workers.slice(),cash:f.cash,fields:G.fieldCount[f.id]||0,production:f.production,sales:f.salesQty,revenue:f.revenue,expenses:f.expenses,netProfit:f.netProfit,lossDays:f.lossDays,outputStock:f.stock.grain},route:G.transit.routes.find(r=>r.id===s.route)?.stats,people:G.people.filter(p=>!p.deceased&&!p.movedAway).length,employed:G.people.filter(p=>!p.deceased&&!p.movedAway&&p.job>=0).length,goods:goodsBalance(),valid:validateTown()};},
};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')

def canonical(raw):
    state=json.loads(raw);state.pop('trafficState',None);state.pop('visualState',None)
    state['fieldCount']={k:v for k,v in state.get('fieldCount',{}).items() if v}
    return json.dumps(state,sort_keys=True,separators=(',',':'))

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1280,'height':850});errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    page.set_content(html);page.add_script_tag(content=script);page.locator('#newTown').click();page.locator('#pause').click();page.evaluate("__townTest.reset('settlement',42)")
    setup=page.evaluate('__parcelEmployment.setup()')
    assert setup['routeQuote']['cost']>0 and setup['routeQuote']['capacity']>0
    assert setup['farmAfterConstruction']['jobs']==4 and len(setup['farmAfterConstruction']['workers'])==4
    assert set(setup['farmAfterConstruction']['workers'])<=set(setup['prehire'])
    assert setup['treasuryAfter']<setup['treasuryBefore'] and setup['regionAfter']<setup['regionBefore']
    assert setup['outlook']['vacancies']==0 and setup['outlook']['fundedVacancies']==0 and setup['outlook']['jobseekers']>0
    assert setup['outlook']['businessDemand']>=0 and setup['outlook']['sites']
    assert any('business-demand index' in reason for reason in setup['outlook']['investorBlocks'])
    page.evaluate('__townTest.step(120)');end=page.evaluate('s=>__parcelEmployment.snapshot(s)',setup)
    assert not end['farm']['closed'] and end['farm']['workers'] and set(end['farm']['workers'])<=set(setup['prehire'])
    # The roadside farm has a productive base site. Additional field titles are
    # a later, separate cooperative expansion and are not required for this
    # ordinary startup to produce; don't mistake the fieldCount for its output.
    assert end['farm']['production']>0 and end['farm']['sales']>0, (setup,end)
    assert end['farm']['netProfit']>0 and end['farm']['cash']>setup['farmAfterConstruction']['cash']
    assert end['employed']>setup['employedBeforeFarm']
    assert end['route']['operating'] and end['route']['staff'] and end['route']['capacity']>0
    assert end['valid']['ok'] and max(abs(row['error']) for row in end['goods'])<.001
    checkpoint=page.evaluate('__townTest.save()');page.evaluate('__townTest.step(30)');continuation=page.evaluate('__townTest.save()')
    assert page.evaluate('s=>__townTest.load(s)',checkpoint);page.evaluate('__townTest.step(30)')
    replay=page.evaluate('__townTest.save()');assert canonical(replay)==canonical(continuation)
    assert not errors,errors
    result={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'ordinaryOpening':setup,'after120Days':end,
            'additionalPaidWorkersAtEnd':len(end['farm']['workers']),'allSurvivorsWerePreviouslyUnemployed':True,
            'cashMovement':'municipal construction and regional working capital were paid; grain sales, wages, fares and exports follow normal account flows',
            'goodsConserved':True,'validatorPassed':True,'exactThirtyDayReplay':True,'errors':errors}
    out=ROOT/'reports/development-8.0/expanded-parcel-employment.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));browser.close()
