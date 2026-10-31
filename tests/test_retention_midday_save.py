"""Candidate-only negative: monthly correspondence must not save a partial day."""
from pathlib import Path
import functools,hashlib,http.server,json,subprocess,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];source=subprocess.check_output(['git','show','726d0a5:assets/game.js'],cwd=ROOT,text=True)
probe=r'''
window.__retentionSaveReady=()=>saveStoreReady;
window.__retentionSaveAudit=()=>{chosenScenario='settlement';seed(42);paused=true;G.day=29;const baseReview=monthlyReview;monthlyReview=function(){const h=G.households[0];h.cash=0;h.deposits={};h.stress=90;h.worklessness=90;h.income=0;h.incomeTax=0;h.netIncomeTrend=0;baseReview();};const captures=[];persistSnapshot=function(payload){const g=JSON.parse(payload);captures.push({day:g.day,lastHistory:g.history[g.history.length-1]?.day??null,rng:g.rngState});return Promise.resolve(true);};tick();return {captures,day:G.day,lastHistory:G.history[G.history.length-1]?.day,rng:rngState,inbox:G.councilInbox};};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();p.wait_for_function('__retentionSaveReady()');result=p.evaluate('__retentionSaveAudit()');b.close()
server.shutdown();assert any(c['day']==result['day']and c['lastHistory']!=result['lastHistory']for c in result['captures']),result;out=ROOT/'reports/integration/retention-review-8';out.mkdir(parents=True,exist_ok=True);(out/'midday-save.json').write_text(json.dumps({'candidate_commit':'726d0a5a76512b6df8662d9c83f921b4a90d00b6','source_sha256':hashlib.sha256(source.encode()).hexdigest(),'candidateOnly':True,'controlledFinancialRiskFixture':True,'storageWriterIntercepted':True,'result':result},indent=2)+'\n');print('CONFIRMED candidate partial-day persistence',result)
