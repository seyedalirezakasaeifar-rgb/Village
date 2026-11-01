from pathlib import Path
import sys,json,gzip,subprocess
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode()
bridge=Path('experimental/worker/runtime-guard.js').read_text()+Path('experimental/worker/archive-endpoint.js').read_text()+Path('experimental/worker/real-view-bridge.js').read_text()+'''window.bridgeProbe={panel:()=>active,canonical:()=>JSON.stringify([G,rngState]),state:()=>({day:G.day,wage:G.policy.minWage,pop:G.stats.population,frozen:Object.isFrozen(G),construction:G.construction}),lot:()=>buildableCandidates('park').find(p=>canPlace(p.x,p.y,true,'park')),savePair:async()=>{const before=saveRevision,results=await Promise.all([save(),save()]);return {before,after:saveRevision,results};},failSave:async()=>{const owner=persistSnapshot;persistSnapshot=()=>Promise.resolve(false);try{return await save();}finally{persistSnapshot=owner;}},saved:()=>readSaveEnvelope(localStorage.getItem('townledger-v6')).payload,clear:()=>localStorage.removeItem('worker-prototype-test-slot')};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(e.stack));p.route('http://worker-real.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://worker-real.test/');p.add_script_tag(content=Path('assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js',bridge+'// SOURCE: 99-instrumentation.js'))
 p.evaluate('''async args=>{window.real=await __workerRealView.enable(args.code,args.archive);}''',{'code':Path('experimental/worker/model.generated.js').read_text(),'archive':archive})
 rows=[]
 selectors=['[data-procurement]','#borrow','#repay','#toggleDevelopment','[data-private-invite]','[data-parcel-buy]','[data-civic-project-build]','[data-bridge-remove]','[data-bridge-repair]','[data-trade-offer]','[data-logistics-priority]','[data-civic-recharter]','[data-brownfield-action]']
 for tab in ['overview','economy','construction','agenda','treasury','banking','businesses','citizens','journal','settings','community','policies']:
  buttons=p.locator('#tabs [data-panel="'+tab+'"]')
  if not buttons.count():continue
  buttons.click();p.wait_for_function('t=>bridgeProbe.panel()===t',arg=tab)
  row={'panel':tab,'panelError':'Panel error:' in p.locator('#panelBody').inner_text(),'paidRejections':[]}
  for selector in selectors:
   candidates=p.locator('#panelBody '+selector)
   if not candidates.count() or not candidates.first.is_visible() or not candidates.first.is_enabled():continue
   p.evaluate('window.beforeHost=bridgeProbe.canonical()')
   worker_before=p.evaluate('async()=>JSON.stringify((await real.inspect(1)).model)')
   candidates.first.click();p.wait_for_timeout(20)
   assert p.evaluate('bridgeProbe.canonical()===beforeHost'),(tab,selector,'host mutated')
   worker_after=p.evaluate('async()=>JSON.stringify((await real.inspect(1)).model)');assert worker_before==worker_after,(tab,selector,'worker mutated')
   row['paidRejections'].append({'selector':selector,'hostUnchanged':True,'workerUnchanged':True})
  rows.append(row)
 p.evaluate('window.beforeSpeed=bridgeProbe.canonical()');p.locator('#speedRange').focus();p.locator('#speedRange').press('End');assert p.evaluate('bridgeProbe.canonical()===beforeSpeed')
 receipt={'speedInputHostUnchanged':True,'panels':rows,'pageErrors':errors,'testedPaidRejections':sum(len(r['paidRejections']) for r in rows),'source':'d2b7086','limits':['Only actually rendered/enabled controls count','Not complete paid routing or native acceptance']}
 Path('experimental/worker/control-coverage-proof.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt));b.close()
