"""Exact model equivalence against the immutable eb2e88c transit implementation.

The oracle is the previous module, not a copy of the optimized algorithm. Identical
other game modules run in separate pages. This verifies changes in routing caches,
funding, road wear, topology, timetable, service edits, fare tickets and capacity.
"""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,json,hashlib,statistics

def probe_from(name):
 tree=ast.parse((ROOT/'tests'/name).read_text())
 return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))

source=(ROOT/'assets/game.js').read_text()
reference=(ROOT/'tests/fixtures/transit-reference-eb2e88c.js').read_text()
start=source.index('// SOURCE: 46-transit-network.js')
end=source.index('// SOURCE:',start+10)
baseline=source[:start]+'// SOURCE: 46-transit-network.js\n'+reference+'\n'+source[end:]
capacity=probe_from('test_transit_capacity.py')
extra=r'''
 const transitions=[],dest=b('home',25,19);invalidateBuildingIndex();invalidateRoads(false);
 for(let i=0;i<4;i++){const id=G.people.length;G.households.push({id,name:'Bus driver',people:[id],home:driverHome.id,cash:100,wages:0,tax:0,incomeTax:0,income:0,travel:0,travelDue:0});G.region-=100;G.people.push({id,hh:id,age:30,health:100,skill:.8,job:-1,publicIncome:0,publicWork:false,publicRole:'',previousPublicRole:''});}
 const bs={mode:'bus',depot:depot.id,stops:[roadId(10,20),roadId(25,20)],level:2},bus=buildTransitRoute(bs,transitQuote(bs));if(!bus)throw Error('No bus');
 const advance=()=>{G.day++;G.people.forEach(p=>{p.publicWork=false;p.publicIncome=0;});transitOperatingDay();};
 const capture=name=>{const journey=transitJourney(a,dest),available=transitJourney(a,dest,1),pair=transitJourney(a,dest,2);transitions.push({name,journey,available,pair,transit:JSON.parse(JSON.stringify(G.transit)),money:totalMoney(),treasury:G.treasury,region:G.region,people:G.people.map(p=>({id:p.id,publicWork:p.publicWork,publicIncome:p.publicIncome,trip:p.transitTrip})),households:G.households.map(h=>({cash:h.cash,travel:h.travel,travelDue:h.travelDue,income:h.income}))});};
 advance();capture('bus funded');advance();capture('unchanged timetable');
 const ticket=transitJourney(a,dest);if(!ticket)throw Error('No bus itinerary');ticket.settled=true;ticket.routes.push(999);const independent=transitJourney(a,dest);if(independent.settled||independent.routes.includes(999))throw Error('Shared mutable ticket template');
 const full=transitJourney(a,dest),bsNow=G.transit.routes.find(r=>r.id===bus.id);if(!transitReserve(full,bsNow.stats.capacity))throw Error('Could not reserve available capacity');capture('capacity exhausted');
 advance();capture('next day restores capacity');G.roadWear.fill(30);advance();capture('worn street timetable');
 G.region+=G.treasury;G.treasury=0;advance();capture('no funding');G.region-=500000;G.treasury=500000;
 const busBroken=roadId(18,20);G.tiles[busBroken]=0;invalidateRoads(false);advance();capture('closed street');
 G.tiles[busBroken]=1;invalidateRoads(false);advance();capture('street reopened');
 const edit={...bs,stops:[roadId(10,20),roadId(30,20)]};if(!buildTransitRoute(edit,transitQuote(edit,bus.id),bus.id))throw Error('Edit failed');advance();capture('route edited');
 if(!setTransitLevel(bus.id,1))throw Error('Frequency edit failed');advance();capture('frequency reduced');
 if(!setTransitLevel(bus.id,0))throw Error('Suspension failed');capture('suspended');deleteTransitRoute(bus.id);capture('retired');
'''
capacity=capacity.replace('return {funded,repeated,disrupted,unfunded,parallel,transfers};',extra+'\nreturn {funded,repeated,disrupted,unfunded,parallel,transfers,transitions};')
scale=probe_from('test_transit_scale.py')
scale=scale.replace('return {routes:',"return {projection:{transit:G.transit,treasury:G.treasury,region:G.region,people:G.people.map(p=>({id:p.id,publicWork:p.publicWork,publicIncome:p.publicIncome,trip:p.transitTrip})),households:G.households.map(h=>({cash:h.cash,travel:h.travel,travelDue:h.travelDue,income:h.income}))},routes:")

def load_page(browser,code,probe):
 page=browser.new_page(viewport={'width':844,'height':390});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);page.add_script_tag(content=code.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));page.locator('#newTown').click();assert not errors,errors;page.locator('#pause').click();page.evaluate("__townTest.reset('settlement',42)");return page

out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'reference_commit':'eb2e88c','reference_module_sha256':hashlib.sha256(reference.encode()).hexdigest(),'cases':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 pages=[load_page(browser,code,capacity) for code in [baseline,source]]
 compared=[p.evaluate('__transitCapacity()') for p in pages]
 assert compared[0]==compared[1],'Controlled model or invalidation results differ from eb2e88c'
 out['exact_transition_cases']=[s['name'] for s in compared[0]['transitions']]
 for p in pages:p.close()
 for routes in [8,12,48]:
  pr=scale.replace('i<12;i++)depots',f'i<{(routes+3)//4};i++)depots').replace('i<2192;',f'i<{2000+routes*4};').replace('i<192;',f'i<{routes*4};').replace('for(let i=0;i<48;i++)',f'for(let i=0;i<{routes};i++)').replace('i<5;i++', 'i<12;i++')
  rows=[];models=[]
  for label,code in [('baseline',baseline),('optimized',source)]:
   page=load_page(browser,code,pr);value=page.evaluate('__transitScale()');models.append(value.pop('projection'));assert value['drivers']==routes*4 and value['nodes']==routes*16,value;rows.append({'implementation':label,'times':value.pop('times'),'poseMs':value.pop('poseMs'),'state':value});page.close()
  assert models[0]==models[1],f'Exact accounts, fares, tickets, staff or service differs for {routes} routes'
  assert rows[0]['state']==rows[1]['state'],rows
  row={'routes':routes,'riders':2000,'baseline':rows[0],'optimized':rows[1],'exact_equivalence':True}
  for k in ['baseline','optimized']:row[k]['median_ms']=statistics.median(row[k]['times'][1:])
  row['speedup']=row['baseline']['median_ms']/max(.01,row['optimized']['median_ms']);out['cases'].append(row);print(json.dumps({k:row[k] for k in ['routes','speedup','exact_equivalence']}),flush=True)
 browser.close()
(ROOT/'reports/transit-optimization-8.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));print('PASS exact previous-module equivalence: model/accounts/tickets/capacity, 12 invalidation transitions, 8/12/48 routes and 2,000 riders')
