"""Actual untouched synchronous87811c counterparts of the15 blocked worker buttons.
No worker injection, alternate dispatcher, wallet/model setup or click confirmation.
"""
from pathlib import Path
import sys,json,gzip,re,hashlib,subprocess
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
ref='87811c52cdb9aecd13cd23beebd52f6475c6dd9c';source=Path('assets/game.js').read_text();bridge=Path('experimental/worker/real-view.generated.js').read_text();worker=Path('experimental/worker/model.generated.js').read_text();baseline=json.loads(Path('experimental/worker/independent-a649-review/control-census.json').read_text());targets=[r for r in baseline['uniqueControlShapes'] if r['classification']=='UNRESOLVED' and r['tag']=='BUTTON' and not r['disabled'] and (r['id']=='tutorial' or any(p.get('genericUnsupported') and p.get('label')==r['text'] for p in baseline['actualUnresolvedButtonProbes']))];assert len(targets)==15
probe='''window.syncCompare={state:()=>({day:G.day,active,overlay,tool:buildMode,category:constructionCategory,camera:{...cam},dialog:$('eventDialog').style.display,help:$('helpDialog').style.display,toast:$('toast').textContent,eventTitle:$('eventTitle').textContent,helpTitle:$('helpTitle').textContent,treasury:G.treasury}),archive:()=>archivePayload()};'''
# Existing canonical paid QA fixtures; founding source is established through its actual menu.
paths={'funded1081':'docs/previews/growth-journey/regional-42-planned.json.gz','district32':'experimental/worker/fixtures/district-ordinary-current.json.gz','brownfield209':'experimental/worker/fixtures/brownfield-ready-ordinary-current.json.gz'}
archives={k:gzip.decompress(Path(v).read_bytes()).decode() for k,v in paths.items()};rows=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://sync-control.test/**',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://sync-control.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bridge+probe+'\n// SOURCE: 99-instrumentation.js'));p.evaluate('''async code=>window.real=await __workerRealView.enable(code,null,{realtime:true,startPaused:true,initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',worker);p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.wait_for_function('document.getElementById("welcome").style.display==="none"');p.evaluate('real.settlePanels()');p.evaluate('real.settleSaves()');archives['founding']=p.evaluate('real.command({type:"export"})')['archive']
 def settle():p.evaluate('async()=>{await real.settleRealtime();await real.settlePanels();await real.settleSaves();await real.settleRealtime();await real.settlePanels();}')
 def panel(tab):
  if p.evaluate('syncCompare.state().active')!=tab:p.locator('#tabs [data-panel="'+tab+'"]').click()
  settle()
 def adopt(world):
  p.keyboard.press('Escape');panel('settings');p.locator('#importSave').click();p.locator('#importText').fill(archives[world]);p.locator('#restoreGo').click();p.wait_for_function('document.querySelector("#helpDialog").style.display==="none"');settle()
 def selector(r):
  if r['id']:return '[id='+json.dumps(r['id'])+']'
  key,value=next(iter(r['data'].items()));return '[data-'+re.sub(r'([A-Z])',lambda m:'-'+m.group(1).lower(),key)+'='+json.dumps(value)+']'
 for r in targets:
  adopt(r['world']);panel(r['panel']);p.locator('#panelBody details').evaluate_all('(nodes)=>nodes.forEach(d=>d.open=true)');sel=selector(r);target=p.locator('#panelBody '+sel).first;assert target.count() and target.is_enabled(),sel;before=p.evaluate('syncCompare.state()');target.click();settle();after=p.evaluate('syncCompare.state()');label=r['text'];key=next(iter(r['data']),None)
  if r['id']=='tutorial':working=p.locator('#helpDialog').is_visible()
  elif r['id']=='firstFoodOrder':working=p.locator('#eventDialog').is_visible() and 'Working capital or local capacity' in after['eventTitle']
  elif r['id']=='firstLocalFood':working=after['active']=='construction' and after['category']=='production'
  elif r['id']=='firstTradeAgreement' or key in ['programmePanel','openMonetary']:working=after['active']==('policies' if key=='openMonetary' else 'economy')
  elif key=='decisionRoute':working=after['active']=='economy' and p.locator('#alternativeSuppliers').evaluate('e=>e.open')
  elif key=='urbanLandPlan':working=after['tool']=='urban_plan' and after['active']==''
  elif key=='urbanOverlay':working=after['overlay']=='neighbourhoods' and after['active']==''
  elif key=='urbanRetail':working=p.locator('#eventDialog').is_visible() or bool(after['toast']) and not re.search('unsupported|worker preview',after['toast'],re.I)
  elif key=='waterfrontCamera':working=before['camera']!=after['camera'] or after['active']==''
  elif key=='waterfrontBuild':working=after['active']=='construction'
  elif key=='district':working=after['active']==''
  elif key=='view':working=after['overlay']==r['data']['view'] and after['active']==''
  elif key=='parcelOutlook':working=p.locator('#eventDialog').is_visible() and bool(after['eventTitle'])
  else:working=False
  rows.append({'selector':sel,'label':label,'world':r['world'],'before':before,'after':after,'matchesExpectedSourceBehavior':bool(working),'treasuryUnchangedByUnconfirmedReview':before['treasury']==after['treasury']});print(sel,working,after['toast'],after['eventTitle'],flush=True)
 selection=[];adopt('funded1081');panel('economy');p.locator('#alternativeSuppliers').evaluate('e=>e.open=true')
 for selector in ['#supplierMarket','#supplierGood','#supplierFirm']:
  current=p.locator(selector).input_value();values=p.locator(selector+' option').evaluate_all('(nodes)=>nodes.filter(n=>!n.disabled).map(n=>n.value)');other=next((v for v in values if v!=current),None)
  if other is None:selection.append({'selector':selector,'alternatives':0});continue
  p.locator(selector).select_option(other);settle();selection.append({'selector':selector,'requested':other,'displayedAfterChange':p.locator(selector).input_value(),'retained':p.locator(selector).input_value()==other})
 receipt={'expectedPublicSource':ref,'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerCandidate':True,'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'bridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'actualFoundImportNavigationAndClicks':True,'cases':rows,'workingCandidateControls':sum(r['matchesExpectedSourceBehavior'] for r in rows),'unexpectedSourceFailures':[r for r in rows if not r['matchesExpectedSourceBehavior']],'supplierSelectionComparison':selection,'pageErrors':errors,'scope':'15 previously blocked worker buttons only; a legitimate source prerequisite refusal is distinguished from a generic worker unsupported response'}
 Path('experimental/worker/audit-fixed-control-comparison.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not errors,errors;assert receipt['workingCandidateControls']==15,receipt['unexpectedSourceFailures'];assert all(r.get('retained',True)for r in selection);print('FIXED_COMPARISON',receipt['workingCandidateControls'],'/',len(rows),'observed source behavior');b.close()
