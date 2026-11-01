"""Actual paid owner versus original current-source UI, using funded QA archives.
Run after building the published worker modules against --model-root current source.
No generated fixture funding, people, crop titles, drivers or stocks are injected.
"""
from pathlib import Path
import argparse,json,hashlib,sys,gzip,subprocess
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--model-root',default='/tmp/land-current-model');ap.add_argument('--family',choices=['all','farm','brownfield'],default='all');ap.add_argument('--worker-root');ap.add_argument('--farm',default=str(Path(__file__).parent/'fixtures/farm-ordinary-current.json.gz'));ap.add_argument('--brownfield',default=str(Path(__file__).parent/'fixtures/brownfield-ready-ordinary-current.json.gz'));args=ap.parse_args();root=Path(args.model_root)
worker_root=Path(args.worker_root) if args.worker_root else root
source=(root/'assets/game.js').read_text();code=(worker_root/'experimental/worker/model.generated.js').read_text();bridge=''.join((worker_root/'experimental/worker'/n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js'])
base_worker_sha256=hashlib.sha256(code.encode()).hexdigest()
code+="\nconst landAuditRequest=workerRequest;workerRequest=function(m){if(m.type==='land-test-root-status')return __rootAdmission.status();if(m.type==='land-test-fence'){simulationTickActive=m.active;return {active:simulationTickActive};}return landAuditRequest(m);};\n"
hook=r'''paused=true;window.landCompletion={load:async a=>{if(!hydrateSave(a))throw Error('Original restore refused funded fixture');paused=true;pendingEvent=null;active='';await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);frameClock=G.trafficState.clock;trafficElapsed=G.trafficState.elapsed;return archivePayload();},state:()=>{G.rngState=rngState;return JSON.parse(JSON.stringify(G));},archive:()=>archivePayload(),farm:id=>urbanFarmRenewalQuote(id),control:attrs=>{const b=document.createElement('button');for(const [k,v] of Object.entries(attrs))b.setAttribute(k,v);document.body.appendChild(b);b.click();b.remove();},brownfield:()=>brownfieldSites()[0],openBrownfield:()=>openPanel('construction'),choose:i=>{frameClock=G.trafficState.clock;trafficElapsed=G.trafficState.elapsed;$('eventChoices').querySelector('[data-event-choice="'+i+'"]').click();},step:n=>{frameClock=G.trafficState.clock;trafficElapsed=G.trafficState.elapsed;__townTest.step(n);return JSON.parse(archivePayload());},fence:(id,flag)=>{const q=urbanFarmRenewalQuote(id),before=archivePayload();if(!q.ok)throw Error(q.reason);if(flag==='active')simulationTickActive=true;else simulationTickFailed=true;let result;try{result=urbanFarmRenewal(cityDemand(),id,q.reviewKey);}finally{simulationTickActive=false;simulationTickFailed=false;}return {result,unchanged:before===archivePayload()};},inspect:()=>({valid:validateTown(),goods:goodsBalance(),cash:totalMoney(),projects:G.projects.map(p=>({id:p.id,kind:p.kind,urbanRenewal:p.urbanRenewal,remaining:p.remaining,building:readBuild(p.id)}))})};'''
def read_archive(path):
 p=Path(path);return gzip.decompress(p.read_bytes()).decode() if p.suffix=='.gz' else p.read_text()
rows=[];negative=[];normalization=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);pages=[]
 for worker in [False,True]:
  p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://land-completion.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://land-completion.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',(bridge if worker else '')+hook+'\n// SOURCE: 99-instrumentation.js'));pages.append(p)
 oracle,p=pages
 def init(archive):
  canonical=oracle.evaluate('a=>landCompletion.load(a)',archive)
  raw=json.loads(archive);new=json.loads(canonical)
  if raw!=new:normalization.append({'stage':'fixture-original-hydration','changedKeys':[k for k in set(raw)|set(new) if raw.get(k)!=new.get(k)]})
  p.evaluate('''async a=>{if(window.real){await real.command({type:'load',archive:a.archive});return;}window.real=await __workerRealView.enable(a.code,a.archive,{initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Actual command owner unavailable');}});}''',{'code':code,'archive':canonical})
  return canonical
 def route(op,payload):return p.evaluate('m=>real.command({type:"route",module:"land-district",...m})',{'operation':op,'payload':payload})
 def choose(r,index):
  event=next(e for e in r['outbox'] if e['type']=='council-event')['payload']['id']
  try:return p.evaluate('m=>real.command(m)',{'type':'choice','eventId':event,'index':index})
  except Exception:
   print('ROOT_FAILURE',p.evaluate('real.command({type:"land-test-root-status"})'),flush=True);raise
 def exact(r,label):
  expected=oracle.evaluate('landCompletion.state()');actual=r['model']
  if actual!=expected:
   Path('/tmp/land-completion-diff.json').write_text(json.dumps({'label':label,'actual':actual,'expected':expected}));print('DIFF',label,[k for k in set(actual)|set(expected) if actual.get(k)!=expected.get(k)],flush=True)
  assert actual==expected,label;assert r['rng']==expected['rngState'];rows.append(label)
 quote={}
 if args.family!='brownfield':
  farm_archive=read_archive(args.farm);init(farm_archive);farm_opening_total=oracle.evaluate('landCompletion.inspect().cash');farm_id=8;quote=oracle.evaluate('id=>landCompletion.farm(id)',farm_id);assert quote['ok'],quote
  for flag in ['active','failed']:
   result=oracle.evaluate('a=>landCompletion.fence(a.id,a.flag)',{'id':farm_id,'flag':flag});assert result['unchanged'] and not result['result']['ok'];negative.append({'currentSourceFence':flag,'atomic':True})
  for index in [1,0]:
   oracle.evaluate('landCompletion.control({"data-urban-farm-renew":"8"})');r=route('urban-farm-renew',{'firm':farm_id});
   if index==0:
    before=p.evaluate('real.command({type:"export"})')['archive'];event=next(e for e in r['outbox'] if e['type']=='council-event')['payload']['id'];p.evaluate('real.command({type:"land-test-fence",active:true})');failure=p.evaluate('id=>real.command({type:"choice",eventId:id,index:0}).then(()=>false,e=>e.message)',event);p.evaluate('real.command({type:"land-test-fence",active:false})');assert failure;assert p.evaluate('real.command({type:"export"})')['archive']==before;negative.append({'actualPaidOwnerForcedActiveTickFence':True,'atomic':True})
   oracle.evaluate('i=>landCompletion.choose(i)',index);exact(choose(r,index),'eligible-farm-cancel' if index else 'eligible-farm-relocation')
  committed=p.evaluate('real.command({type:"export"})')['archive'];expected_raw=oracle.evaluate('landCompletion.archive()');assert json.loads(committed)==json.loads(expected_raw)
  # Compare actual original hydrate normalization explicitly, never hide worksite fields.
  normalized=oracle.evaluate('a=>landCompletion.load(a)',expected_raw);raw=json.loads(expected_raw);new=json.loads(normalized);diffs=[k for k in set(raw)|set(new) if raw.get(k)!=new.get(k)];normalization.append({'stage':'immediate-farm-worksite-hydration','changedKeys':diffs})
  init(normalized);exact(p.evaluate('real.command({type:"snapshot"})'),'farm-worksite-canonical-load')
  # Same current model ticks, same original source order; owner ordinary-day scope.
  oracle.evaluate('landCompletion.step(12)');exact(p.evaluate('real.command({type:"step",days:12})'),'farm-worksite-12-day-exact-replay')
  farm_inspection=oracle.evaluate('landCompletion.inspect()');assert farm_inspection['valid']['ok'];assert max(abs(row['error']) for row in farm_inspection['goods'])<.05;assert abs(farm_inspection['cash']-farm_opening_total)<.05
 if args.family!='farm':
  ready=read_archive(args.brownfield);initial=init(ready);site=oracle.evaluate('landCompletion.brownfield()');assert site['status']=='ready' and site['remaining']==0
  for kind in ['park','home','grocer']:
   init(initial);r=route('brownfield-action',{'id':site['id'],'action':kind});oracle.evaluate('m=>landCompletion.control({"data-brownfield-action":m.kind,"data-brownfield-id":m.id})',{'kind':kind,'id':site['id']});oracle.evaluate('landCompletion.choose(0)');exact(choose(r,0),'brownfield-reuse-'+kind)
   committed=p.evaluate('real.command({type:"export"})')['archive'];raw=oracle.evaluate('landCompletion.archive()');assert json.loads(committed)==json.loads(raw);normalized=oracle.evaluate('a=>landCompletion.load(a)',raw);normalization.append({'stage':'brownfield-'+kind+'-hydrate','changedKeys':[k for k in json.loads(raw) if json.loads(raw).get(k)!=json.loads(normalized).get(k)]});init(normalized);exact(p.evaluate('real.command({type:"snapshot"})'),'brownfield-'+kind+'-canonical-load')
 assert not errors,errors
 receipt={'productionEnabled':False,'modelCommit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD']).decode().strip(),'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerModelSourceSha256':hashlib.sha256((worker_root/'assets/game.js').read_bytes()).hexdigest(),'sameSourceComposition':worker_root==root,'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'baseWorkerSha256':base_worker_sha256,'workerCompositionBase':'97b761e1a0c4f1719e8374c538273e6b1bdc421f','moduleSha256':hashlib.sha256(Path('experimental/worker/routes/land-district.js').read_bytes()).hexdigest(),'fixtureSha256':{k:hashlib.sha256(read_archive(v).encode()).hexdigest() for k,v in [('farm',args.farm),('brownfieldReady',args.brownfield)]},'fixtureFundingInjection':False,'deterministicOracleVisualClockAtChoiceAndStep':True,'fixtureOriginalHydrationIncludesTwoPausedRenderFrames':True,'exactCompleteModelRng':rows,'normalization':normalization,'negative':negative,'farm':{k:quote[k] for k in ['farm','building','fields','workers','stock','destination','relocationCost','ownerPremium'] if k in quote},'pageErrors':errors,'farmGoodsMaxError':max(abs(row['error']) for row in farm_inspection['goods']) if args.family!='brownfield' else None,'farmCashDrift':farm_inspection['cash']-farm_opening_total if args.family!='brownfield' else None,'originalSourceHandlerClicks':True,'visibleOriginalControlJourney':False,'actualWorkerUiBindingsCertified':False,'saveFailureRetryCertified':False}
 Path('experimental/worker/land_district_'+args.family+'_completion_proof.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS',rows,flush=True);b.close()
