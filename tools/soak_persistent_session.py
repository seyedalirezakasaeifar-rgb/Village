"""Real-origin saves, cold Continue cycles, real RAF, menus and bounded queues.

TOWNLEDGER_PERSIST_SECONDS defaults to1800; sample interval defaults to30s.
No simulation-step helper or forced GC is used during play.
"""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import threading,time,os,json,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest();seconds=max(30,int(os.environ.get('TOWNLEDGER_PERSIST_SECONDS','1800')));interval=max(5,int(os.environ.get('TOWNLEDGER_PERSIST_SAMPLE','30')));out=ROOT/'reports/development-persistence';out.mkdir(exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/index.html'
probe='''
const actualContinue=$('continue').onclick;$('continue').onclick=async e=>{await actualContinue(e);paused=true;acc=0;last=performance.now();updateHeader()};
window.__persistentSession={flush:async()=>{await saveStorePromise;await saveWrites;return autoSaveOK},snapshot:()=>({day:G.day,population:G.stats.population,buildings:G.buildings.length,people:G.people.length,households:G.households.length,valid:validateTown(),order:saveOrder,revision:saveRevision,town:saveTown,pending:!!savePendingWrite,active:saveWriteRunning,atlas:atlas.size,atlasBytes,waterVessels:waterVessels.size,waterManifests:G.waterway?.manifests.length||0,goodsError:Math.max(...goodsBalance().map(v=>Math.abs(v.error))),payloadBytes:new Blob([archivePayload()]).size}),physical:()=>{const g=JSON.parse(archivePayload());delete g.trafficState;delete g.serviceProvision;delete g.stats;delete g.roadMetrics;return g}};
'''
script=source.decode().replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js');samples=[];errors=[];reloads=0
canonical=lambda obj:hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':640,'height':360},has_touch=True);p.set_default_timeout(15000);p.route('**/game.js',lambda r:r.fulfill(body=script,content_type='application/javascript'));p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);p.goto(url);p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("regional",42)');p.locator('#panelClose').click()
  for district in ['river-reach','east-meadow']:
   p.locator('[data-panel=construction]').click();p.locator('#charterOffice>summary').click();p.locator('[data-parcel-buy='+district+']').click();p.locator('[data-event-choice="0"]').click();p.locator('#panelClose').click()
  assert p.evaluate('__persistentSession.flush()');p.locator('#speedRange').fill(os.environ.get('TOWNLEDGER_PERSIST_SPEED','4'));p.locator('#pause').click();started=time.monotonic();next_sample=0;index=0;panels=['economy','community','agenda','citizens','policies','banking','construction','settings','businesses','treasury','journal','overview']
  while time.monotonic()-started<seconds:
   p.wait_for_timeout(500);elapsed=time.monotonic()-started
   if elapsed<next_sample:continue
   p.locator(f'[data-panel={panels[index%len(panels)]}]').click();assert 'Panel error' not in p.locator('#panelBody').inner_text();p.locator('#panelClose').click()
   if index%4==3:
    p.locator('#pause').click();p.locator('[data-panel=settings]').click();p.locator('#saveNow').click();assert p.evaluate('__persistentSession.flush()');before=p.evaluate('__persistentSession.physical()');head=p.evaluate('__persistentSession.snapshot()');p.reload();p.locator('#continue').click();p.wait_for_function('document.querySelector("#welcome").style.display==="none"');after=p.evaluate('__persistentSession.physical()');
    if canonical(before)!=canonical(after):(out/'cold-mismatch.json').write_text(json.dumps({'source_sha256':sha,'before':before,'after':after},indent=2)+'\n')
    assert canonical(before)==canonical(after),{'reload':reloads,'beforeDay':before['day'],'afterDay':after['day'],'differentKeys':[k for k in before if before[k]!=after.get(k)]};assert p.evaluate('__persistentSession.snapshot().town')==head['town'];reloads+=1;p.locator('#panelClose').click();p.locator('#pause').click()
   sample=p.evaluate('__persistentSession.snapshot()');sample['seconds']=round(elapsed,1);assert sample['valid']['ok'] and sample['goodsError']<.001 and sample['atlas']<=600 and sample['atlasBytes']<=48*1024*1024 and sample['waterVessels']<=32 and sample['waterManifests']<=48,sample;assert not errors,errors;samples.append(sample);assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
   result={'source_sha256':sha,'httpOrigin':True,'requestedSeconds':seconds,'elapsedSeconds':time.monotonic()-started,'coldReloads':reloads,'comparison':'all exported town fields except transient traffic/service/road caches and derived stats; sorted canonical SHA256','samples':samples,'errors':errors};(out/'persistent-session.json').write_text(json.dumps(result,indent=2)+'\n');print(round(elapsed),sample['day'],sample['population'],'saved order',sample['order'],'reloads',reloads,flush=True);next_sample+=interval;index+=1
  p.locator('#pause').click();assert p.evaluate('__persistentSession.flush()');assert not errors,errors;b.close()
finally:server.shutdown();server.server_close()
print('PASS real-origin RAF/menu/saving/cold Continue session; exact physical archive comparison, no Android performance claim')
