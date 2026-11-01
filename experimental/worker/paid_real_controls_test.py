"""Actual council UI plus one shared reference owner. Production remains disabled."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text();bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js'])
hook='''window.paidUiOracle={setup:()=>{seed(42);paused=true;for(let i=0;i<19;i++)tick();active='';$('welcome').style.display='none';return archivePayload();},canonical:()=>JSON.parse(archivePayload())};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for name,extra in [('oracle',hook),('worker',bridge+'window.paidUiView={active:()=>active,model:()=>JSON.parse(JSON.stringify(G)),frozen:()=>Object.isFrozen(G)};\n')]:
  p=b.new_page();p.route('http://paid-ui.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://paid-ui.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',extra+'// SOURCE: 99-instrumentation.js'));pages.append(p)
 p,q=pages;archive=p.evaluate('paidUiOracle.setup()');q.evaluate('async a=>window.real=await __workerRealView.enable(a.code,a.archive)',{'code':code,'archive':archive});ready=q.evaluate('real.command({type:"paid-test-init"})');assert ready['testOnly']
 for page in pages:page.locator('#tabs [data-panel="agenda"]').click()
 q.wait_for_function('paidUiView.active()==="agenda"');q.evaluate('real.settlePanels()')
 for page in pages:page.locator('#convene').click()
 q.wait_for_function('document.querySelector("#eventDialog").style.display==="flex"');q.evaluate('real.settlePanels()')
 expectedTitle=p.locator('#eventTitle').inner_text();assert q.locator('#eventTitle').inner_text()==expectedTitle
 # First real enabled action; acknowledgment controls closing and saving.
 index=p.locator('#eventChoices button').evaluate_all('(bs)=>bs.findIndex(b=>!b.disabled)');p.locator('#eventChoices button').nth(index).click();q.locator('#eventChoices [data-worker-choice]').nth(index).click();q.wait_for_function('document.querySelector("#eventDialog").style.display==="none"');q.evaluate('real.settlePanels()');q.evaluate('real.settleSaves()')
 expected=p.evaluate('paidUiOracle.canonical()');actual=q.evaluate('real.command({type:"export"})')['model'];assert actual==expected,[(k,str(actual.get(k))[:160],str(expected.get(k))[:160]) for k in expected if actual.get(k)!=expected.get(k)]
 assert q.evaluate('paidUiView.frozen()');saved=q.evaluate('localStorage.getItem("townledger-v6")');assert saved
 Path('experimental/worker/paid-real-controls-proof.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'actualAgendaTab':True,'actualConveneButton':True,'actualChoiceButton':True,'eventTitle':expectedTitle,'fullModelRngExact':True,'hostSnapshotFrozen':True,'originalStorageWriterUsed':True,'referenceOwnerOnly':True,'productionAdmission':False},indent=2)+'\n');print('PASS actual council UI/shared reference root exact model/RNG and original writer');b.close()
