"""Actual-origin cold persistence of paid civic phases and failed adoption."""
from test_mobile_rendering import ROOT
import functools,http.server,threading,json,hashlib
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();probe=r'''
const phaseContinue=$('continue').onclick;$('continue').onclick=async e=>{await phaseContinue(e);paused=true;hostSuspended=true;acc=0;};
window.__phase={pause:()=>{paused=true;hostSuspended=true;},flush:async()=>{await save();await saveWrites;return autoSaveOK},plan:()=>{const v=civicGatheringVenues()[0];if(!v)throw Error('No venue');const q=reviewCivicGathering({venue:v.b.id,start:G.day+1});if(!authorizeCivicGathering(q).ok)throw Error('No funded event');return q;},cancel:()=>cancelCivicGathering(G.civicCalendar.events[0].id),fault:()=>{const raw=archivePayload(),rng=rngState,original=ensureScenarioProgramme;try{ensureScenarioProgramme=()=>{throw Error('Injected adoption fault')};if(hydrateSave(raw))throw Error('Fault accepted');}finally{ensureScenarioProgramme=original}if(archivePayload()!==raw||rngState!==rng)throw Error('Fault changed committed state');}};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
def canonical(raw):
 g=json.loads(raw)
 for k in ['trafficState','visualState','serviceProvision','privateServiceProvision','stats','roadMetrics']:g.pop(k,None)
 return g
rows=[]
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.route('**/game.js',lambda r:r.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'),content_type='application/javascript'));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.evaluate('__phase.pause()')
  def cold(label):
   assert p.evaluate('__phase.flush()');before=p.evaluate('__townTest.save()');p.reload();p.locator('#continue').click();p.wait_for_function('document.querySelector("#welcome").style.display==="none"');after=p.evaluate('__townTest.save()');assert canonical(before)==canonical(after),{'label':label,'different':[(k,canonical(before).get(k),canonical(after).get(k)) for k in set(canonical(before))|set(canonical(after)) if canonical(before).get(k)!=canonical(after).get(k)]};p.evaluate('__phase.fault()');rows.append({'phase':label,'exactPhysicalCold':True,'failedAdoptionAtomic':True})
  cold('first save');p.evaluate('__townTest.step(2)');p.evaluate('__phase.plan()');cold('paid scheduled gathering');p.evaluate('__townTest.step(1)');cold('active gathering');p.evaluate('__phase.cancel()');cold('cancelled paid gathering');assert p.evaluate('__townTest.validate().ok');b.close()
finally:server.shutdown();server.server_close()
out=ROOT/'reports/current-save';out.mkdir(exist_ok=True);(out/'phases.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'httpOrigin':True,'rows':rows},indent=2)+'\n');print('PASS',rows)
