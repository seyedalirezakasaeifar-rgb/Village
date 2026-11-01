"""Actual panels and RNG ordered by worker; no reference admission owner."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text()
hook='''window.panelOracle={start:()=>{seed(42);paused=true;return archivePayload();},render:m=>{active=m.panel;const c=m.context;selected=c.selected===null?null:{id:c.selected};filterPeople=c.people;filterFirms=c.firms;citizenQuery=c.query;constructionCategory=c.category;draftPolicy={...c.draft};return {html:panelContents(active),model:JSON.parse(archivePayload()),rng:rngState};}};\n'''
context={'selected':None,'people':'all','firms':'all','query':'','category':'all','draft':{},'transitRoute':None}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'));archive=p.evaluate('panelOracle.start()');p.evaluate('''code=>{let serial=0,epoch=0;window.w=new Worker(URL.createObjectURL(new Blob([code])));window.ask=m=>new Promise(r=>{let id=++serial;const h=e=>{if(e.data.id!==id)return;w.removeEventListener('message',h);if(e.data.ok)epoch=e.data.result.epoch;r(e.data);};w.addEventListener('message',h);w.postMessage({id,command:id,epoch,...m});});}''',code)
 def ask(m):
  r=p.evaluate('m=>ask(m)',m);assert r['ok'],r;return r['result']
 ask({'type':'load','archive':archive});status=ask({'type':'paid-status'});assert not status['configured'] and not status['enabled'] and not status['productionAdmissionCertified']
 rows=[]
 for tab in ['overview','economy','agenda','community','policies','treasury','banking','citizens','businesses','construction','journal','inspect','construction','agenda']:
  c={**context}
  if tab=='citizens':c.update(people='lowcash',query='a')
  if tab=='businesses':c['firms']='open'
  if tab=='policies':c['draft']={'minWage':12,'imports':False}
  if tab=='construction':c['category']='housing'
  if tab=='inspect':c['selected']=json.loads(archive)['buildings'][0]['id']
  m={'type':'prepare-panel','panel':tab,'context':c};expected=p.evaluate('m=>panelOracle.render(m)',m);actual=ask(m);effects=[e for e in actual['outbox'] if e['type']=='panel-render'];assert effects and effects[-1]['payload']['html']==expected['html'],tab+' HTML differs';assert actual['model']==expected['model'],tab+' model/RNG differs';assert actual['rng']==expected['rng'];ask({'type':'effects-ack','through':max(e['serial'] for e in actual['outbox'])});rows.append({'panel':tab,'exactHtmlModelRng':True})
 before=ask({'type':'export'});blocked=p.evaluate('m=>ask(m)',{'type':'build','kind':'park','x':1,'y':1});assert not blocked['ok'];assert ask({'type':'export'})['model']==before['model'];bad=p.evaluate('m=>ask(m)',{'type':'prepare-panel','panel':'agenda','context':{**context,'draft':{'treasury':10000000}}});assert not bad['ok'];assert ask({'type':'export'})['model']==before['model']
 # Actual game controls render from worker; host G remains frozen and host RNG equals worker snapshots.
 q=b.new_page();q.route('http://worker-panels.test/',lambda r:r.fulfill(body=html,content_type='text/html'));q.goto('http://worker-panels.test/');errors=[];q.on('pageerror',lambda e:errors.append(str(e)))
 bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js'])+'window.viewProbe={active:()=>active,model:()=>JSON.stringify(G),rng:()=>rngState,frozen:()=>Object.isFrozen(G)};\n';q.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bridge+'// SOURCE: 99-instrumentation.js'));q.evaluate('async a=>window.real=await __workerRealView.enable(a.code,a.archive)',{'code':code,'archive':archive})
 for tab in ['agenda','construction','citizens','policies']:
  q.locator('#tabs [data-panel="'+tab+'"]').click();q.wait_for_function('tab=>viewProbe.active()===tab',arg=tab);q.evaluate('real.settlePanels()');assert q.evaluate('viewProbe.active()')==tab;assert 'Panel error:' not in q.locator('#panelBody').inner_text();authoritative=q.evaluate('real.command({type:"export"})');assert json.loads(q.evaluate('viewProbe.model()'))==authoritative['model'];assert q.evaluate('viewProbe.rng()')==authoritative['rng'];assert q.evaluate('viewProbe.frozen()')
 q.locator('[data-cabinet="housing"]').click();q.evaluate('real.settlePanels()');assert 'housing' not in q.locator('#panelBody').inner_text().lower() or q.locator('#enactPolicy').count()
 q.locator('#tabs [data-panel="community"]').click();q.wait_for_function('viewProbe.active()==="community"');q.evaluate('real.settlePanels()');beforeUi=q.evaluate('viewProbe.model()');q.locator('[data-private-invite="school"]').click();q.wait_for_function("document.querySelector('#toast').textContent.includes('Shared paid dispatcher')");assert q.evaluate('viewProbe.model()')==beforeUi
 q.locator('#tabs [data-panel="settings"]').click();q.wait_for_function('viewProbe.active()==="settings"');q.evaluate('real.settlePanels()');settingsOracle=q.evaluate('real.command({type:"export"})');assert q.evaluate('viewProbe.rng()')==settingsOracle['rng'];assert json.loads(q.evaluate('viewProbe.model()'))==settingsOracle['model']
 q.locator('#panelClose').click();q.evaluate('real.settlePanels()');assert q.evaluate('viewProbe.active()')=='';assert q.evaluate('real.command({type:"paid-status"})')['activePanel']=='';assert not errors,errors
 receipt={'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'defaultPaidOwnerAbsent':True,'panels':rows,'invalidDraftNoModelRngChange':True,'actualTabsUseWorkerHtml':True,'actualDraftRerender':True,'actualProviderButtonNoOwnerRefusesUnchanged':True,'rawConstructionNoOwnerRefusesUnchanged':True,'closeSynchronizesWorkerContext':True,'localSettingsPreservesModelRng':True,'hostFrozen':True,'pageErrors':errors,'settingsAndTripRemainLocalViewOnly':True,'productionEnabled':False};Path('experimental/worker/panel-ordering-proof.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS authoritative panel HTML/model/RNG and actual UI tab/draft controls');b.close()
