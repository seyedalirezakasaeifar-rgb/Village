"""Actual previously unclassified preference/draft widgets; no financial enactment."""
from pathlib import Path
import sys,json,hashlib,http.server,threading,functools
sys.path.insert(0,'tests')
from playwright.sync_api import sync_playwright
root=Path.cwd();source=(root/'assets/game.js').read_text();bridge=(root/'experimental/worker/real-view.generated.js').read_text();code=(root/'experimental/worker/model.generated.js').read_text();probe='''window.inputReview={model:()=>JSON.stringify(G),draft:()=>({...draftPolicy}),active:()=>active};''';script=source.replace('// SOURCE: 99-instrumentation.js',bridge+probe+'\n// SOURCE: 99-instrumentation.js')
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();rows=[];errors=[]
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(body=script,content_type='application/javascript'));p.goto('http://127.0.0.1:'+str(server.server_port)+'/index.html');p.evaluate('''async code=>window.real=await __workerRealView.enable(code,null,{realtime:true,startPaused:true,initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',code);p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.wait_for_function('document.querySelector("#welcome").style.display==="none"')
  def settle():p.evaluate('async()=>{await real.settleRealtime();await real.settlePanels();await real.settleSaves();}')
  def panel(tab):
   if p.evaluate('inputReview.active()')!=tab:p.locator('#tabs [data-panel="'+tab+'"]').click()
   settle()
  panel('policies')
  for key,value in [('healthBudget','1234.5'),('educationBudget','2345.5')]:
   selector='[data-service-budget-amount="'+key+'"]';p.locator(selector).evaluate('(b)=>{for(let d=b.parentElement;d;d=d.parentElement)if(d.tagName==="DETAILS")d.open=true;}');before=p.evaluate('real.command({type:"export"})')['archive'];p.locator(selector).fill(value);p.locator(selector).press('Tab');settle();row={'control':selector,'expected':float(value),'draftValue':p.evaluate('k=>inputReview.draft()[k]',key),'visibleValue':p.locator(selector).input_value(),'authorityUnchanged':before==p.evaluate('real.command({type:"export"})')['archive']};rows.append(row)
  panel('settings')
  for selector,value in [('#musicVolume','31'),('#musicMood','quiet'),('[data-preference="quality"]','low'),('[data-renderer="city"]','webgl')]:
   target=p.locator(selector);target.evaluate('(b)=>{for(let d=b.parentElement;d;d=d.parentElement)if(d.tagName==="DETAILS")d.open=true;}');options=target.locator('option').evaluate_all('(ns)=>ns.map(n=>n.value)')
   if options and value not in options:value=next(v for v in options if v!=target.input_value())
   before=p.evaluate('real.command({type:"export"})')['archive']
   if options:target.select_option(value)
   else:
    target.focus();target.press('Home')
    for _ in range(int(value)):target.press('ArrowRight')
    target.dispatch_event('change')
   settle();p.wait_for_timeout(300);rows.append({'control':selector,'requested':value,'displayed':p.locator(selector).input_value(),'authorityUnchanged':before==p.evaluate('real.command({type:"export"})')['archive']})
  panel('overview');p.locator('[data-mayor-agenda]').click();settle();rows.append({'control':'[data-mayor-agenda]','expectedPanel':'agenda','actualPanel':p.evaluate('inputReview.active()')});assert rows[-1]['actualPanel']=='agenda'
  assert not errors,errors
  Path('experimental/worker/independent-remaining-inputs.json').write_text(json.dumps({'candidateCommit':'a2f49fbd3994f27042a2c56c34500af80ef7a9c8','sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'bridgeSha256':hashlib.sha256(bridge.encode()).hexdigest(),'actualInputsNoFinancialEnactment':True,'cases':rows,'pageErrors':errors,'notPerformanceOrAudibilityClaim':True},indent=2)+'\n');print(rows,flush=True);b.close()
finally:server.shutdown()
