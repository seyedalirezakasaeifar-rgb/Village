"""Independent actual-panel control census; route matching is not behavioral proof.
Uses actual founding/import/navigation with no injected economic state.
"""
from pathlib import Path
import sys,json,gzip,re,hashlib,subprocess
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();bridge=Path('experimental/worker/real-view.generated.js').read_text();worker=Path('experimental/worker/model.generated.js').read_text();bindings=json.loads(Path('experimental/worker/route-bindings.generated.json').read_text());hand=Path('experimental/worker/real-view-bridge.js').read_text();safe=re.search(r"const safe=(\[[^;]+?)\.includes\(b.id\)\|\|(\[[^;]+?)\.some\(k=>b.dataset",hand);safeids=json.loads(safe[1].replace("'",'"'));safedata=json.loads(safe[2].replace("'",'"'));coreids=set(re.findall(r"b\.id==='([^']+)'",hand));coredata=set(re.findall(r"b\.dataset\.([A-Za-z]+)",hand))|{'panel','house','firm','inspect','ambition'}
for a in re.findall(r"(\[(?:'[^']+'(?:,)?)+\])\.includes\(b.id\)",hand):coreids.update(json.loads(a.replace("'",'"')))
probe='''window.censusProbe={active:()=>active,frame:()=>({day:G?.day,rng:G?.rngState,frozen:!!G&&Object.isFrozen(G),paused,toast:$('toast').textContent,dialog:$('helpDialog').style.display}),model:()=>JSON.stringify(G)};'''
rows=[];errors=[];world_archives={};button_probes=[];selection_probes=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://census.test/**',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://census.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bridge+probe+'\n// SOURCE: 99-instrumentation.js'));p.evaluate('''async code=>window.real=await __workerRealView.enable(code,null,{realtime:true,startPaused:true,initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',worker)
 def settle():p.evaluate('async()=>{await real.settleRealtime();await real.settlePanels();await real.settleSaves();}')
 def panel(tab):
  if p.evaluate('censusProbe.active()')!=tab:p.locator('#tabs [data-panel="'+tab+'"]').click()
  settle();assert 'Panel error:' not in p.locator('#panelBody').inner_text(),tab
 def capture(world,tab):
  p.locator('#panelBody details').evaluate_all('(nodes)=>nodes.forEach(d=>d.open=true)')
  controls=p.evaluate('''a=>[...document.querySelectorAll('#panelBody button,#panelBody input,#panelBody select,#panelBody [data-house],#panelBody [data-firm],#panelBody [data-inspect]')].filter(e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden').map(e=>{const data={...e.dataset},matched=a.bindings.filter(b=>b.selector&&e.matches(b.selector)),r=e.getBoundingClientRect();return {tag:e.tagName,id:e.id,data,text:(e.textContent||e.getAttribute('aria-label')||'').trim().slice(0,120),type:e.type,disabled:!!e.disabled,visibleInViewport:r.bottom>0&&r.top<innerHeight,registered:matched.map(b=>({event:b.event,module:b.module,operation:b.operation}))};})''',{'bindings':bindings})
  for c in controls:
   if c['registered']:kind='registered-family'
   elif c['id'] in coreids or set(c['data'])&coredata:kind='explicit-bridge-or-local-view'
   elif c['id'] in safeids or set(c['data'])&set(safedata):kind='source-local-view-allowlist'
   elif c['tag'] in ['INPUT','SELECT'] and (c['id'] in ['searchPeople','surveyDistrict'] or set(c['data'])&{'policy','cabinet','serviceBudget','cityView'}):kind='source-input-view-or-draft'
   else:kind='UNRESOLVED'
   c.update(world=world,panel=tab,classification=kind);rows.append(c)
 for world in ['founding','funded1081','district32','brownfield209']:
  if world=='founding':p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.wait_for_function('document.querySelector("#welcome").style.display==="none"');settle()
  else:
   path={'funded1081':'docs/previews/growth-journey/regional-42-planned.json.gz','district32':'experimental/worker/fixtures/district-ordinary-current.json.gz','brownfield209':'experimental/worker/fixtures/brownfield-ready-ordinary-current.json.gz'}[world];archive=gzip.decompress(Path(path).read_bytes()).decode();panel('settings');p.locator('#importSave').click();p.locator('#importText').fill(archive);p.locator('#restoreGo').click();p.wait_for_function('document.querySelector("#helpDialog").style.display==="none"');settle()
  world_archives[world]=p.evaluate('real.command({type:"export"})')['archive']
  for tab in ['overview','economy','agenda','community','policies','treasury','banking','citizens','businesses','construction','journal','settings']:panel(tab);capture(world,tab)
 # Do not trust a safe-looking label: actually exercise a visible unresolved Help control.
 panel('settings');before=p.evaluate('real.command({type:"export"})')['archive'];p.locator('#tutorial').click();settle();manual=p.evaluate('censusProbe.frame()');after=p.evaluate('real.command({type:"export"})')['archive'];manual.update(authoritativeArchiveUnchanged=before==after,helpVisible=p.locator('#helpDialog').is_visible(),helpTitle=p.locator('#helpTitle').inner_text())
 unique={}
 for r in rows:
  key=json.dumps([r['id'],sorted(r['data'].keys()),r['classification']],sort_keys=True)
  if key not in unique:unique[key]=r
 # Exercise every unresolved enabled button, not merely its static classification.
 def adopt(text):
  p.keyboard.press('Escape');settle();panel('settings');p.locator('#importSave').click();p.locator('#importText').fill(text);p.locator('#restoreGo').click();p.wait_for_function('document.querySelector("#helpDialog").style.display==="none"');settle()
 for r in list(unique.values()):
  if r['classification']!='UNRESOLVED' or r['tag']!='BUTTON' or r['disabled'] or r['id']=='tutorial':continue
  adopt(world_archives[r['world']]);panel(r['panel']);p.locator('#panelBody details').evaluate_all('(nodes)=>nodes.forEach(d=>d.open=true)')
  if r['id']:selector='[id='+json.dumps(r['id'])+']'
  else:
   key,value=next(iter(r['data'].items()));attr='data-'+re.sub(r'([A-Z])',lambda m:'-'+m.group(1).lower(),key);selector='['+attr+'='+json.dumps(value)+']'
  target=p.locator('#panelBody '+selector).first
  if not target.count():button_probes.append({'selector':selector,'world':r['world'],'panel':r['panel'],'presentOnReplay':False});continue
  before=p.evaluate('real.command({type:"export"})')['archive'];target.click();settle();frame=p.evaluate('censusProbe.frame()');after=p.evaluate('real.command({type:"export"})')['archive'];button_probes.append({'selector':selector,'label':r['text'],'world':r['world'],'panel':r['panel'],'presentOnReplay':True,'after':frame,'genericUnsupported':bool(re.search('unsupported|unavailable in.*worker',frame['toast'],re.I)),'authoritativeArchiveUnchanged':before==after,'legacyChoices':p.locator('#eventDialog [data-event-choice]').count(),'workerChoices':p.locator('#eventDialog [data-worker-choice]').count()})
 adopt(world_archives['funded1081']);panel('economy');p.locator('#alternativeSuppliers').evaluate('d=>d.open=true')
 for selector in ['#supplierMarket','#supplierGood','#supplierFirm']:
  current=p.locator(selector).input_value();values=p.locator(selector+' option').evaluate_all('(nodes)=>nodes.filter(n=>!n.disabled).map(n=>n.value)');other=next((v for v in values if v!=current),None)
  if other is None:selection_probes.append({'selector':selector,'alternatives':0});continue
  before=p.evaluate('real.command({type:"export"})')['archive'];p.locator(selector).select_option(other);settle();selection_probes.append({'selector':selector,'requested':other,'displayedAfterSettled':p.locator(selector).input_value(),'retained':p.locator(selector).input_value()==other,'authoritativeArchiveUnchanged':p.evaluate('real.command({type:"export"})')['archive']==before})
 receipt={'candidateCommit':'a649a55ccb752b6f1fd170e9f0689edb92dff34c','sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(worker.encode()).hexdigest(),'bridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'actualFoundImportAndPanelNavigation':True,'expandedDisclosureStateOnly':True,'records':len(rows),'uniqueControlShapes':list(unique.values()),'unresolved':[r for r in unique.values() if r['classification']=='UNRESOLVED'],'actualManualProbe':manual,'actualUnresolvedButtonProbes':button_probes,'actualAlternativeSelectionProbes':selection_probes,'pageErrors':errors,'classificationIsNotBehavioralAcceptance':True}
 Path('experimental/worker/independent-control-census.json').write_text(json.dumps(receipt,indent=2)+'\n');print('CENSUS',len(rows),'shapes',len(unique),'unresolved',len(receipt['unresolved']),'manual',manual,flush=True);assert not errors,errors;b.close()
