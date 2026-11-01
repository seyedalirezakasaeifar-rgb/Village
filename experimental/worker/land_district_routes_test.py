"""Owned route module: real original UI choices and exact completed model/RNG.
Conserved fixture funding is explicit test setup, not normal-player history.
"""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text()
bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js'])
hook=r'''paused=true;window.landProbe={fixture:kind=>{seed(42);G.autoBuild=false;G.treasury+=200000;G.region-=200000;pendingEvent=null;active='';if(kind==='recharter'){const p=ANNEX_PARCELS.find(p=>p.id==='east-meadow');purchaseParcel(p.id,parcelSurvey(p).price);chooseDistrictFocus(p.id,'neighbourhood');civicProjectStart('district','neighbourhood',p.id);G.day=40;}if(kind==='bridge'){const p=ANNEX_PARCELS.find(p=>p.id==='east-meadow');purchaseParcel(p.id,parcelSurvey(p).price);for(let x=43;x<=63;x++)construct('road',x,15,true);for(let x=69;x<=76;x++)construct('road',x,15,true);flushRoadBatch();invalidateRoads();}return archivePayload();},load:a=>{G=JSON.parse(a);rngState=G.rngState;const metrics=G.roadMetrics;invalidateRoads();G.roadMetrics=metrics;pendingEvent=null;active='';},clearTarget:()=>G.buildings.find(b=>['park','square','school','clinic'].includes(b.kind)&&urbanClearanceQuote(b.x,b.y).ok)?.id,brownfield:()=>G.buildings.find(b=>brownfieldQuote(b.id).ok)?.id,approaches:()=>[...new Set(regionalApproachPlan().flatMap(p=>p.path))].filter(id=>!roadSurface(id)).length,planTarget:()=>G.buildings.find(b=>b.kind==='home').id,damageBridge:()=>{G.bridges[0].condition=50;return archivePayload();},state:()=>{G.rngState=rngState;return JSON.parse(JSON.stringify(G));},click:(selector,attrs)=>{const b=document.createElement('button');for(const [k,v] of Object.entries(attrs||{}))b.setAttribute(k,v);if(selector[0]==='#')b.id=selector.slice(1);$('panelBody').appendChild(b);b.click();b.remove();},choice:i=>{$('eventChoices').querySelector('[data-event-choice="'+i+'"]').click();},road:()=>{for(let y=0;y<T;y++)for(let x=0;x<T;x++){const q=roadRemovalQuote(x,y);if(q.ok&&!q.impact.lost.length)return {x,y};}throw Error('No removable road');},reviewRoad:(x,y)=>reviewRoadRemoval(x,y),reviewBridge:()=>reviewRoadBridge(roadId(63,15)),bridgeId:()=>G.bridges[0].id};'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);errors=[];pages=[]
 for isworker in [False,True]:
  p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://land.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://land.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',(bridge if isworker else '')+hook+'\n// SOURCE: 99-instrumentation.js'));pages.append(p)
 oracle,p=pages;rows=[];neg=[]
 def boot(kind):
  archive=oracle.evaluate('k=>landProbe.fixture(k)',kind);oracle.evaluate('a=>landProbe.load(a)',archive)
  p.evaluate('''async a=>{if(window.real){await real.command({type:"load",archive:a.archive});return;}window.real=await __workerRealView.enable(a.code,a.archive,{initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})}''',{'code':code,'archive':archive})
 def route(op,payload):return p.evaluate('m=>real.command({type:"route",module:"land-district",...m})',{'operation':op,'payload':payload})
 def choose(reply,index):
  event=next(e for e in reply['outbox'] if e['type']=='council-event');return p.evaluate('m=>real.command(m)',{'type':'choice','eventId':event['payload']['id'],'index':index})
 def exact(reply,label):
  expected=oracle.evaluate('landProbe.state()');actual=reply['model']
  if actual!=expected:
   Path('/tmp/land-route-diff.json').write_text(json.dumps({'label':label,'actual':actual,'expected':expected},indent=2));print('DIFF',label,[k for k in set(actual)|set(expected) if actual.get(k)!=expected.get(k)],flush=True)
  assert actual==expected,label
  assert reply['rng']==expected['rngState'];rows.append(label)
 boot('land')
 for parcel,index in [('east-meadow',1),('east-meadow',0)]:
  oracle.evaluate('id=>landProbe.click("[data-parcel-buy]",{"data-parcel-buy":id})',parcel);r=route('parcel-buy',{'parcel':parcel});oracle.evaluate('i=>landProbe.choice(i)',index);reply=choose(r,index);exact(reply,'deed-cancel' if index else 'deed-purchase')
  duplicate=p.evaluate('m=>real.command(m).then(()=>false,e=>e.message)',{'type':'choice','eventId':next(e for e in r['outbox'] if e['type']=='council-event')['payload']['id'],'index':index});assert duplicate;neg.append('duplicate-deed-choice')
 oracle.evaluate('landProbe.click("[data-district-focus]",{"data-district-id":"east-meadow","data-district-focus":"neighbourhood"})');r=route('district-focus',{'parcel':'east-meadow','focus':'neighbourhood'});oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'initial-charter')
 target=oracle.evaluate('landProbe.planTarget()');oracle.evaluate('id=>landProbe.click("[data-urban-plan]",{"data-urban-building":id,"data-urban-plan":"residential"})',target);r=route('urban-plan',{'building':target,'plan':'residential'});oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'urban-plan')
 oracle.evaluate('landProbe.click("[data-urban-rehousing]",{"data-urban-rehousing":""})');r=route('urban-rehousing',{});oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'reserved-rehousing')
 if oracle.evaluate('landProbe.approaches()'):
  oracle.evaluate('landProbe.click("#regionalApproaches",{})');r=route('regional-approaches',{});oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'regional-approaches')
 clear_target=oracle.evaluate('landProbe.clearTarget()');assert clear_target is not None,'No real compensable public site fixture';oracle.evaluate('id=>landProbe.click("[data-urban-clear]",{"data-urban-clear":id})',clear_target);r=route('urban-clear',{'building':clear_target});oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'compensated-public-site-clearance')
 industrial=oracle.evaluate('landProbe.brownfield()');assert industrial is not None,'No actual assessable industrial fixture'
 for action in ['assess','withdraw','assess','acquire','fund']:
  oracle.evaluate('m=>landProbe.click("[data-brownfield-action]",{"data-brownfield-id":m.id,"data-brownfield-action":m.action})',{'id':industrial,'action':action});r=route('brownfield-action',{'id':industrial,'action':action});oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'brownfield-'+action)
 point=oracle.evaluate('landProbe.road()');oracle.evaluate('q=>landProbe.reviewRoad(q.x,q.y)',point);r=route('road-remove-review',point);oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'road-retire')
 assert oracle.evaluate('landProbe.approaches()')>0,'No retired lawful approach to repair';oracle.evaluate('landProbe.click("#regionalApproaches",{})');r=route('regional-approaches',{});oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'regional-approaches-after-road-retirement')
 before=p.evaluate('real.command({type:"export"})')['archive']
 for op,payload in [('parcel-buy',{'parcel':'east-meadow'}),('parcel-buy',{'parcel':'__proto__'}),('bridge-repair',{'id':999999}),('road-remove-review',{'x':-1,'y':0}),('parcel-buy',{'parcel':'north-woods','extra':1})]:
  result=p.evaluate('m=>real.command({type:"route",module:"land-district",...m}).then(()=>false,e=>e.message)',{'operation':op,'payload':payload});assert result;assert p.evaluate('real.command({type:"export"})')['archive']==before;neg.append({'operation':op,'refusal':result})
 boot('bridge');oracle.evaluate('landProbe.reviewBridge()');r=route('bridge-review',{'x':63,'y':15});oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'bridge-build')
 damaged=oracle.evaluate('landProbe.damageBridge()');oracle.evaluate('a=>landProbe.load(a)',damaged);p.evaluate('a=>real.command({type:"load",archive:a})',damaged);damaged_id=oracle.evaluate('landProbe.bridgeId()');oracle.evaluate('id=>landProbe.click("[data-bridge-repair]",{"data-bridge-repair":id})',damaged_id);r=route('bridge-repair',{'id':damaged_id});oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'bridge-repair')
 bridge_id=oracle.evaluate('landProbe.bridgeId()');oracle.evaluate('id=>landProbe.click("[data-bridge-remove]",{"data-bridge-remove":id})',bridge_id);r=route('bridge-remove',{'id':bridge_id});oracle.evaluate('landProbe.choice(1)');exact(choose(r,1),'bridge-keep')
 oracle.evaluate('id=>landProbe.click("[data-bridge-remove]",{"data-bridge-remove":id})',bridge_id);r=route('bridge-remove',{'id':bridge_id});oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'bridge-remove')
 boot('recharter');oracle.evaluate('landProbe.click("[data-civic-recharter]",{"data-civic-recharter":"east-meadow"})');r=route('civic-recharter',{'parcel':'east-meadow'});oracle.evaluate('landProbe.choice(0)');exact(choose(r,0),'civic-recharter-aged-fixture')
 # New isolated worker realm: inject one post-debit model fault, never a production hook.
 p.goto('http://land.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bridge+hook+'\n// SOURCE: 99-instrumentation.js'))
 fault_code=code+"\nlet landFaultArmed=true,landFaultHits=0;const landOriginalRequest=workerRequest;workerRequest=function(m){if(m.type==='land-test-fault-status')return {hits:landFaultHits};return landOriginalRequest(m);};const landOriginalPlan=urbanPlanChange;urbanPlanChange=function(...args){const r=landOriginalPlan(...args);if(r.ok&&landFaultArmed){landFaultArmed=false;landFaultHits++;throw Error('LAND_TEST_POST_DEBIT_FAULT');}return r;};\n"
 archive=oracle.evaluate('landProbe.fixture("land")');oracle.evaluate('a=>landProbe.load(a)',archive)
 p.evaluate('''async a=>window.real=await __workerRealView.enable(a.code,a.archive,{initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':fault_code,'archive':archive})
 target=oracle.evaluate('landProbe.planTarget()');r=route('urban-plan',{'building':target,'plan':'residential'});event=next(e for e in r['outbox'] if e['type']=='council-event')['payload']['id'];before=p.evaluate('real.command({type:"export"})')['archive']
 blocked=p.evaluate('real.command({type:"route",module:"land-district",operation:"urban-rehousing",payload:{}}).then(()=>false,e=>e.message)');assert blocked;assert p.evaluate('real.command({type:"export"})')['archive']==before;neg.append('pending-review-command-unchanged')
 failure=p.evaluate('id=>real.command({type:"choice",eventId:id,index:0}).then(()=>false,e=>e.message)',event);assert failure;assert p.evaluate('real.command({type:"land-test-fault-status"})')["hits"]==1;assert p.evaluate('real.command({type:"export"})')['archive']==before;neg.append('post-debit-fault-full-archive-rng-rollback')
 oracle.evaluate('id=>landProbe.click("[data-urban-plan]",{"data-urban-building":id,"data-urban-plan":"residential"})',target);oracle.evaluate('landProbe.choice(0)');exact(p.evaluate('id=>real.command({type:"choice",eventId:id,index:0})',event),'post-fault-same-review-legitimate-retry')
 r=route('urban-rehousing',{});event=next(e for e in r['outbox'] if e['type']=='council-event')['payload']['id'];p.evaluate('id=>real.command({type:"defer",eventId:id})',event);before=p.evaluate('real.command({type:"export"})')['archive'];failure=p.evaluate('id=>real.command({type:"choice",eventId:id,index:0}).then(()=>false,e=>e.message)',event);assert failure;assert p.evaluate('real.command({type:"export"})')['archive']==before;neg.append('cancelled-review-token-unchanged')
 assert not errors,errors
 Path('experimental/worker/land_district_routes_proof.json').write_text(json.dumps({'productionEnabled':False,'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'moduleSha256':hashlib.sha256(Path('experimental/worker/routes/land-district.js').read_bytes()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'conservedFixtureTreasuryTransfer':200000,'additionalControlledFixtures':['bridge condition50','charter at day1 inspected at day40'],'postDebitInjectedFaultCount':1,'postFaultSameReviewRetryExact':True,'fullModelRngExact':rows,'refusals':neg,'pageErrors':errors,'actualUiBridgeBindingsPending':True,'currentPublicSourcePortPending':True},indent=2)+'\n');print('PASS',rows,flush=True);b.close()
