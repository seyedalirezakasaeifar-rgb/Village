"""Exact proposal and full-model oracle against 03cb546's complete service module."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import ast,json,hashlib,functools,http.server,threading,os
from test_mobile_rendering import ROOT
source=(ROOT/'assets/game.js').read_text()
a=source.index('// SOURCE: 16-private-services.js');b=source.index('// SOURCE: 18-region-charter.js',a)
reference=source[:a]+'// SOURCE: 16-private-services.js\n'+(ROOT/'tests/fixtures/private-services-03cb546.js').read_text()+'\n'+source[b:]
a=reference.index('// SOURCE: 40-development.js');b=reference.index('// SOURCE: ',a+10)
reference=reference[:a]+'// SOURCE: 40-development.js\n'+(ROOT/'tests/fixtures/development-03cb546.js').read_text()+'\n'+reference[b:]
m=ast.parse((ROOT/'tests/test_v7_live_large_town.py').read_text());large=next(ast.literal_eval(n.value.args[0]) for n in ast.walk(m) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='town' for t in n.targets))
legacy_sites=(ROOT/'tests/fixtures/development-03cb546.js').read_text().split('function buildableCandidates(')[1].split('function privateContract(')[0]
legacy_sites='function referenceBuildableCandidates('+legacy_sites
probe=legacy_sites+r'''window.__projectionOracle=()=>{
 const geometry={},rankings=[];for(let pass=0;pass<3;pass++){const state=rngState,old=referenceBuildableCandidates('housing'),expectedRng=rngState;rngState=state;const fresh=buildableCandidates('housing',geometry);if(JSON.stringify(old)!==JSON.stringify(fresh)||rngState!==expectedRng)throw Error('Geometry/ranking/RNG mismatch');rankings.push(fresh.length);}
 const started=performance.now(),base=privateProposalBase(),sites=buildableCandidates('housing').slice(0,50),providers=[null,...G.firms.filter(f=>f.privateService).map(f=>f.id)];let pairs=0;
 for(const kind of ['school','fire'])for(const exclude of providers){const context={base,kind,exclude,clients:new Map()};for(const site of sites){const a=privateServiceDemand(kind,site,exclude),b=privateServiceDemand(kind,site,exclude,context);if(a!==b)throw Error('Demand mismatch '+kind+' '+exclude+' '+site.x+','+site.y);pairs++;for(const staff of [1,2]){const fee=privateServiceFee(kind,a,staff,36),x=privateServiceForecast(kind,site,fee,staff,exclude,36),y=privateServiceForecast(kind,site,fee,staff,exclude,36,context);if(JSON.stringify(x)!==JSON.stringify(y))throw Error('Forecast mismatch '+JSON.stringify({kind,exclude,site,x,y}));pairs++;}}}
 return {pairs,rankings,sites:sites.length,exclusions:providers.length,comparisonMs:performance.now()-started};
};

window.__projectionProviders=i=>{
 for(const kind of ['school','fire']){let f=G.firms.find(f=>f.privateService===kind);if(!f){const b=G.buildings.find(b=>b.kind===kind&&!(b.firm>=0));if(!b)continue;f=createFirm(kind,b.x,b.y,true,()=>b);G.region-=f.cash;f.privateService=kind;f.serviceFee=kind==='school'?3:.8;f.jobs=2;b.title={kind:'firm',id:f.id};}f.closed=i%2===1;}
 G.privateServiceProvision={allocations:{},vouchers:0};for(const f of G.firms.filter(f=>f.privateService)){const own={};for(const h of G.households.slice(0,8))own[h.id]={served:1,paid:2,subsidy:.5};G.privateServiceProvision.allocations[f.id]=own;}
 G.civicTraining=G.people.filter(p=>privateEligiblePupil(p)).slice(0,20).map(p=>({person:p.id,days:10}));
};
window.__proposalModel=()=>{const g=JSON.parse(archivePayload());delete g.trafficState;delete g.visualState;return g;};
window.__proposalTransition=i=>{
 G.autoBuild=true;G.policy.privateServices=1;G.policy.educationBudget=[0,280,50,0][i%4];G.policy.defenseBudget=[0,250,40,0][i%4];G.policy.serviceVoucherBudget=[100,0,500,30][i%4];G.policy.privateTuitionCap=[4,2,8,1][i%4];G.policy.privateFireFeeCap=[1,3,.5,2][i%4];
 for(const h of G.households){if(i===1){h.cash=Math.min(h.cash,100*h.people.length);h.income=0;}if(i===2){h.cash+=1000;h.income+=80;}}
 for(const p of G.people)if(p.age>=18&&p.age<=60)p.skill=[.6,.3,.8,.55][i%4];
 recompute();const answer=seekPrivateServiceInvestment();return {answer,model:__proposalModel()};
};
window.__proposalBench=()=>{const snapshot=archivePayload(),times=[],answers=[];for(let i=0;i<5;i++){if(!hydrateSave(snapshot))throw Error('restore');const t=performance.now();answers.push(seekPrivateServiceInvestment());times.push(performance.now()-t);}return {times,answers};};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
direct_only=os.environ.get('PROPOSAL_DIRECT_ONLY')=='1'
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'reference_commit':'03cb546','histories':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for scenario,seed,dense in [('settlement',42,False),('settlement',101,False),('hardtimes',909,False),('regional',42,True)]:
  pages=[];errors=[]
  for code in [reference,source]:
   p=browser.new_page(viewport={'width':844,'height':390});p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',(lambda payload:lambda route:route.fulfill(content_type='application/javascript',body=payload))(code.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('([s,n])=>__townTest.reset(s,n)',[scenario,seed])
   if dense:p.evaluate(large)
   pages.append(p)
  if direct_only:
   rows=[]
   for transition in range(4):
    pages[1].evaluate('__proposalTransition',transition);pages[1].evaluate('__projectionProviders',transition);rows.append(pages[1].evaluate('__projectionOracle()'))
   out['histories'].append({'scenario':scenario,'seed':seed,'dense':dense,'direct':rows});print('PASS direct projections',scenario,seed,rows,flush=True)
   for p in pages:p.close()
   continue
  checks=[]
  for transition in range(4):
   models=[p.evaluate('__proposalTransition',transition) for p in pages]
   assert models[0]==models[1],('proposal',scenario,seed,transition,[k for k in models[0]['model'] if models[0]['model'][k]!=models[1]['model'].get(k)])
   for month in range(3):
    for p in pages:p.evaluate('__townTest.step(30)')
    models=[p.evaluate('__proposalModel()') for p in pages]
    assert models[0]==models[1],('history',scenario,seed,transition,month,[k for k in models[0] if models[0][k]!=models[1].get(k)])
    checks.append(models[0]['day'])
  benches=[p.evaluate('__proposalBench()') for p in pages]
  assert benches[0]['answers']==benches[1]['answers'];assert not errors,errors
  row={'scenario':scenario,'seed':seed,'dense':dense,'exactCheckpoints':checks,'directPairs':pages[1].evaluate('__projectionOracle()'),'reference':benches[0],'optimized':benches[1]};out['histories'].append(row);print('PASS',scenario,seed,dense,'12 exact monthly checkpoints',benches,flush=True)
  for p in pages:p.close()
 browser.close()
server.shutdown();(ROOT/('reports/private-proposal-direct-8.json' if direct_only else 'reports/private-proposal-equivalence-8.json')).write_text(json.dumps(out,indent=2))
print('PASS exact proposal/RNG/accounts/goods/providers/projects histories under changing staffing, fees, public competition, vouchers and household budgets')
