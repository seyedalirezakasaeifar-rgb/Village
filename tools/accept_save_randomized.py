from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import ast,threading,time,os,json,hashlib,random,traceback,datetime,sys
from playwright.sync_api import sync_playwright
ROOT=Path(os.environ.get('SAVE_QA_ROOT',str(Path(__file__).resolve().parents[1])));OUT=Path(os.environ.get('SAVE_QA_OUTPUT',str(ROOT/'reports/save-randomized')));OUT.mkdir(parents=True,exist_ok=True)
SOURCE=(ROOT/'assets/game.js').read_bytes();SHA=hashlib.sha256(SOURCE).hexdigest();SEED=int(os.environ.get('SAVE_QA_SEED','8142026'));SECONDS=int(os.environ.get('SAVE_QA_SECONDS','3600'))
def fixture(name):
 tree=ast.parse((ROOT/'tests'/name).read_text())
 return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
# Reuse existing public fixture definitions without executing their standalone suites.
probe=fixture('test_transit_network.py')+'\n'+fixture('test_save_adversarial.py')
# Composite probe's AST contains a concatenation, so extract only its final literal.
tree=ast.parse((ROOT/'tests/test_save_composite.py').read_text())
assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe+='\n'+ast.literal_eval(assignment.value.right)
probe+=r'''
const qaActualContinue=$('continue').onclick;$('continue').onclick=async e=>{await qaActualContinue(e);paused=true;hostSuspended=true;acc=0;last=performance.now();updateHeader()};
window.__qaRun={
 ready:()=>saveStorePromise,
 flush:async()=>{await saveStorePromise;await saveWrites;return autoSaveOK},
 pause:()=>{paused=true;hostSuspended=true;acc=0;last=performance.now();updateHeader()},
 head:()=>({epoch:saveEpoch,town:saveTown,revision:saveRevision,order:saveOrder,ok:autoSaveOK}),
 snapshot:()=>{const g=JSON.parse(archivePayload());for(const k of ['trafficState','visualState','serviceProvision','privateServiceProvision','stats','roadMetrics'])delete g[k];return g},
 sample:()=>({day:G.day,people:G.people.length,living:G.stats.population,buildings:G.buildings.length,households:G.households.length,cargo:G.regionalTrade?.shipments.length||0,contracts:G.regionalTrade?.contracts.length||0,routes:G.transit.routes.length,fares:G.transit.fares,providers:G.firms.filter(f=>f.privateService&&!f.closed).length,malls:G.firms.filter(f=>f.retailCentre&&!f.closed).length,projects:G.projects.length,civic:G.civicProjects||null,annexations:G.charter.owned.length,valid:validateTown(),money:totalMoney(),goodsError:Math.max(...goodsBalance().map(x=>Math.abs(x.error))),bytes:new Blob([archivePayload()]).size,pending:!!savePendingWrite,active:saveWriteRunning}),
 bootstrap:()=>{
  __saveComposite();const moved=Math.min(G.region,6000000);G.region-=moved;G.treasury+=moved;
  while(G.charter.owned.length<21){const p=ANNEX_PARCELS.find(p=>!G.charter.owned.includes(p.id)&&parcelAdjacent(p));if(!p||!purchaseParcel(p.id,parcelSurvey(p).price))throw Error('Cannot acquire adjoining deed');}
  const f=civicProjectGrocer(),h=civicProjectTargetHousehold(true);if(!civicProjectStart('food','bridge',f.id)||!civicProjectStart('skills','private',h.id)||!civicProjectStart('district','industry','county-ridge'))throw Error('Civic project setup');
  const m=OUTSIDE_MARKETS[0],q=regionalQuote(f,m,'food','import'),before=G.regionalTrade.serial;if(dispatchRegional(f,'food',30,'import',q)>0)G.civicProjects.active.food.orders.push(G.regionalTrade.serial);
  const contract={id:1,name:'Save acceptance paid grain window',firm:G.firms.find(f=>f.kind==='farm').id,market:m.id,good:'grain',status:'active',quantity:40,delivered:0,price:5,deadline:G.day+180};G.regionalTrade.contracts.push(contract);
  const housing=urbanRehousingQuote();if(housing.ok)commissionUrbanRehousing(housing);
  const crop=Object.keys(G.landUse).find(id=>G.landUse[id]===1),quote=crop&&urbanClearanceQuote(+crop%T,+crop/T|0);let clearance=null;if(quote?.ok)clearance=urbanClearance(quote.x,quote.y,quote.total);
  if(!validateTown().ok||!hydrateSave(archivePayload()))throw Error('Composite bootstrap cannot restore');paused=true;hostSuspended=true;return {controlledCatchment:true,all21Deeds:true,realCropTitleClearance:clearance,providerAndMallEscrow:true,civicProjects:3};
 },
 step:n=>__townTest.step(n),
 replay:n=>{const canon=v=>Array.isArray(v)?v.map(canon):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canon(v[k])])):v;const snap=()=>{const g=JSON.parse(archivePayload());delete g.trafficState;delete g.visualState;return canon(g)};const raw=archivePayload(),day=G.day,pending=!!pendingEvent;__townTest.step(n);const a=snap();if(!hydrateSave(raw))throw Error('Replay checkpoint rejected');const restored=snap();__townTest.step(n);const b=snap(),different=Object.keys(a).filter(k=>JSON.stringify(a[k])!==JSON.stringify(b[k]));if(different.length)return {failed:true,days:n,day,pending,raw,restored,a,b,different};return {days:n,exact:true}},
 save:()=>save(),
 corrupt:()=>{const e=JSON.parse(localStorage.getItem('townledger-v6'));e.checksum='injected-corruption';localStorage.setItem('townledger-v6',JSON.stringify(e))},
 quota:async()=>{const real=Storage.prototype.setItem;try{Storage.prototype.setItem=function(){throw new DOMException('QA quota','QuotaExceededError')};await save();await saveWrites;if(!autoSaveOK)throw Error('IDB failed during local quota')}finally{Storage.prototype.setItem=real}},
 bothDenied:async()=>{const set=Storage.prototype.setItem,open=indexedDB.open;const raw=archivePayload();try{Storage.prototype.setItem=function(){throw Error('QA local denial')};indexedDB.open=function(){throw Error('QA indexed denial')};await save();await saveWrites;if(autoSaveOK||archivePayload()!==raw)throw Error('Denied stores lost town or claimed success')}finally{Storage.prototype.setItem=set;indexedDB.open=open}},
 burst:async()=>{for(let i=0;i<25;i++)save();await saveWrites;if(!autoSaveOK||savePendingWrite||saveWriteRunning)throw Error('Burst did not settle')},
 stale:async()=>{await saveWrites;const original=writeIndexedDB,raw=archivePayload();let release;const held=new Promise(r=>release=r);let calls=0;try{writeIndexedDB=async(e,epoch)=>{if(++calls===1)await held;return original(e,epoch)};save();await Promise.resolve();if(!hydrateSave(raw))throw Error('Stale fixture replacement rejected');save();release();await saveWrites;if(!autoSaveOK)throw Error('New timeline failed after stale callback');return {calls,head:saveTown}}finally{release();writeIndexedDB=original}},
 adoptionFailure:()=>{const raw=archivePayload(),rng=rngState,original=ensureScenarioProgramme;try{ensureScenarioProgramme=()=>{throw Error('QA adoption failure')};if(hydrateSave(raw))throw Error('Faulted adoption accepted')}finally{ensureScenarioProgramme=original}if(archivePayload()!==raw||rngState!==rng)throw Error('Adoption failure changed state')},
 corruptImport:choice=>{const raw=archivePayload(),g=JSON.parse(raw),head=JSON.stringify([saveEpoch,saveTown,saveRevision,saveOrder]);switch(choice%8){case 0:g.tiles.pop();break;case 1:g.households[0].cash=-1;break;case 2:g.nextId=1;break;case 3:g.regionalTrade.shipments=[{id:-1}];break;case 4:g.transit.routes[0].path[0]=-1;break;case 5:g.civicProjects.active.food.orders=[g.regionalTrade.serial+999];break;case 6:g.buildings[0].title={kind:'household',id:999999};break;case 7:g.firms[0].stock.grain=-1;break;}if(hydrateSave(g)||archivePayload()!==raw||JSON.stringify([saveEpoch,saveTown,saveRevision,saveOrder])!==head)throw Error('Corrupt import was not atomic')},
 policy:choice=>{G.policy.imports=choice%2===0;recompute();return G.policy.imports},
 cargo:()=>{const f=civicProjectGrocer();if(!f)return 0;const m=OUTSIDE_MARKETS[G.day%OUTSIDE_MARKETS.length];return dispatchRegional(f,'food',1+G.day%8,'import',regionalQuote(f,m,'food','import'))},
 redevelop:()=>{const home=G.buildings.find(b=>['home','apartment','tower'].includes(b.kind)&&G.households.some(h=>h.home===b.id&&h.people.length)&&urbanClearanceQuote(b.x,b.y).ok);if(!home){const q=urbanRehousingQuote();return {available:false,commission:q.ok?commissionUrbanRehousing(q):q.reason}}const q=urbanClearanceQuote(home.x,home.y),people=q.households.map(id=>({id,people:G.households[id].people.slice()})),cleared=urbanClearance(home.x,home.y,q.total);if(cleared.ok){for(const h of people)if(JSON.stringify(G.households[h.id].people)!==JSON.stringify(h.people))throw Error('Clearance lost occupants');if(canPlace(home.x,home.y,true,'park'))construct('park',home.x,home.y)}return {building:home.id,cleared,households:people.map(h=>h.id)}},
 sameDay:async()=>{const day=G.day;for(let i=0;i<3;i++){G.policy.imports=!G.policy.imports;save()}await saveWrites;if(G.day!==day||!autoSaveOK)throw Error('Same-day save failed');return G.policy.imports}
};
'''
if os.environ.get('SAVE_QA_REPRO_03CB')=='1':
 probe=probe.replace("const crop=Object.keys(G.landUse).find(id=>G.landUse[id]===1),quote=crop&&urbanClearanceQuote(+crop%T,+crop/T|0);let clearance=null;if(quote?.ok)clearance=urbanClearance(quote.x,quote.y,quote.total);", "const farm=G.firms.find(f=>f.kind==='farm'&&!f.closed),b=readBuild(farm.building),quote=urbanClearanceQuote(b.x,b.y);let clearance=null;if(quote.ok)clearance=urbanClearance(b.x,b.y,quote.total);")
script=SOURCE.decode().replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/index.html'
START=time.monotonic();UTC=datetime.datetime.now(datetime.timezone.utc);due=UTC+datetime.timedelta(seconds=SECONDS);rng=random.Random(SEED);trace=[];samples=[];errors=[];counts={};reloads=0;replayFailures=[]
summary={'checkpoint':os.environ.get('SAVE_QA_CHECKPOINT','03cb54675880a9b60c0c8d8de5dd0b671d0abff3'),'source_sha256':SHA,'seed':SEED,'httpOrigin':True,'secondsRequested':SECONDS,'startedUTC':UTC.isoformat(),'dueUTC':due.isoformat(),'pid':os.getpid(),'status':'starting'}
def write_status(**kw):
 summary.update(kw);summary.update(elapsedSeconds=round(time.monotonic()-START,2),operations=len(trace),operationCounts=counts,coldReloads=reloads,errors=errors,replayFailures=replayFailures,samples=samples[-120:]);(OUT/'status.json').write_text(json.dumps(summary,indent=2)+'\n')
def emit(op,details):
 record={'index':len(trace),'seconds':round(time.monotonic()-START,3),'op':op,'details':details};trace.append(record);counts[op]=counts.get(op,0)+1
 with (OUT/'operations.jsonl').open('a') as f:f.write(json.dumps(record,separators=(',',':'))+'\n')
 print(record['index'],round(record['seconds']),op,str(details)[:160],flush=True)
def canonical(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
write_status()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);context=browser.new_context(viewport={'width':640,'height':360});page=context.new_page();page.set_default_timeout(30000);page.route('**/game.js',lambda r:r.fulfill(body=script,content_type='application/javascript'));page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(url);page.evaluate('__qaRun.ready()');page.locator('#townSeed').fill('42');page.locator('#newTown').click();page.evaluate('__qaRun.pause()');emit('bootstrap',page.evaluate('__qaRun.bootstrap()'));page.evaluate('__qaRun.save()');page.evaluate('__qaRun.flush()');baseline=page.evaluate('__qaRun.sample().money');write_status(status='running',baselineMoney=baseline)
  def cold():
   global reloads
   page.evaluate('__qaRun.pause()');assert page.evaluate('__qaRun.flush()');before=page.evaluate('__qaRun.snapshot()');oldhead=page.evaluate('__qaRun.head()');page.reload();page.evaluate('__qaRun.ready()');page.locator('#continue').click();page.wait_for_function('document.querySelector("#welcome").style.display==="none"');after=page.evaluate('__qaRun.snapshot()');reloads+=1
   if canonical(before)!=canonical(after):
    (OUT/'cold-failure-private.json').write_text(json.dumps({'before':before,'after':after}));raise AssertionError({'coldMismatch':[k for k in before if before[k]!=after.get(k)]})
   assert page.evaluate('__qaRun.head().town')==oldhead['town'];return {'day':after['day'],'canonical':canonical(after),'order':oldhead['order']}
  # Ensure all fault classes execute once before weighted random scheduling.
  mandatory=['step','replay','import','adoption','quota','corruptStore','bothDenied','stale','burst','sameDay','cargo','cold','redevelop']
  index=0;next_report=0
  if os.environ.get('SAVE_QA_REPRO_03CB')=='1':mandatory.remove('redevelop')
  operations=mandatory[:];weights=[36,5,12,3,4,4,2,3,5,4,5,5]+([] if os.environ.get('SAVE_QA_REPRO_03CB')=='1' else [2])
  while time.monotonic()-START<SECONDS:
   op=mandatory[index] if index<len(mandatory) else rng.choices(operations,weights=weights)[0];index+=1
   if op=='step':n=rng.randint(1,12);page.evaluate('n=>__qaRun.step(n)',n);detail={'days':n}
   elif op=='replay':
    detail=page.evaluate('n=>__qaRun.replay(n)',rng.randint(1,12))
    if detail.get('failed'):
     (OUT/('replay-failure-private-'+str(len(replayFailures)%3)+'.json')).write_text(json.dumps(detail))
     negative={'replayDay':detail['day'],'days':detail['days'],'pending':detail['pending'],'different':detail['different']};replayFailures.append(negative)
     if os.environ.get('SAVE_QA_CONTINUE_REPLAY')!='1':raise AssertionError(negative)
     assert page.evaluate('raw=>__townTest.load(raw)',detail['raw']);detail=negative;op='replay-negative'
   elif op=='import':choice=rng.randrange(8);page.evaluate('n=>__qaRun.corruptImport(n)',choice);detail={'fault':choice}
   elif op=='adoption':page.evaluate('__qaRun.adoptionFailure()');detail={'atomic':True}
   elif op=='quota':page.evaluate('__qaRun.quota()');detail=cold()
   elif op=='corruptStore':page.evaluate('__qaRun.save()');page.evaluate('__qaRun.flush()');page.evaluate('__qaRun.corrupt()');detail=cold()
   elif op=='bothDenied':page.evaluate('__qaRun.bothDenied()');page.evaluate('__qaRun.save()');page.evaluate('__qaRun.flush()');detail={'activePreserved':True}
   elif op=='stale':detail=page.evaluate('__qaRun.stale()');detail.update(cold())
   elif op=='burst':page.evaluate('__qaRun.burst()');detail={'requests':25}
   elif op=='sameDay':detail={'imports':page.evaluate('__qaRun.sameDay()')};detail.update(cold())
   elif op=='cargo':detail={'paidQty':page.evaluate('__qaRun.cargo()')}
   elif op=='redevelop':detail=page.evaluate('__qaRun.redevelop()')
   else:page.evaluate('__qaRun.save()');detail=cold()
   page.evaluate('__qaRun.pause()');emit(op,detail);sample=page.evaluate('__qaRun.sample()');assert sample['valid']['ok'],sample['valid'];assert sample['goodsError']<.001,sample;assert abs(sample['money']-baseline)<.05,{'cashDrift':sample['money']-baseline};assert sample['bytes']<=8*1024*1024,sample;assert sample['cargo']<=240 and sample['routes']<=48 and sample['projects']<=1000,sample;assert not errors,errors;assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==SHA
   if time.monotonic()-START>=next_report:samples.append({'seconds':round(time.monotonic()-START,2),**sample});write_status(status='running');next_report+=30
   page.wait_for_timeout(750)
  page.evaluate('__qaRun.save()');emit('finalCold',cold());sample=page.evaluate('__qaRun.sample()');samples.append({'seconds':round(time.monotonic()-START,2),**sample});write_status(status='completed_with_replay_failures' if replayFailures else 'passed',finalMoneyDrift=sample['money']-baseline);browser.close()
except Exception as e:
 errors.append(repr(e));(OUT/'failure.txt').write_text(traceback.format_exc());write_status(status='failed');print(traceback.format_exc(),flush=True);sys.exit(1)
finally:server.shutdown();server.server_close()
print('COMPLETE immutable randomized save acceptance; replay failures',len(replayFailures),SHA,len(trace),'operations',reloads,'cold reloads',flush=True)
