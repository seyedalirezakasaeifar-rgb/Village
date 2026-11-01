"""Actual original New Town / Options Save / cold Continue, every archive field."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
import sys,json,hashlib,argparse,subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('--expect-mismatch',action='store_true');ap.add_argument('--live-days',type=int,default=0);ap.add_argument('--legacy-v60',action='store_true');args=ap.parse_args();source=subprocess.check_output(['git','show','72419dc:assets/game.js'],cwd=ROOT,text=True) if args.expect_mismatch else (ROOT/'assets/game.js').read_text()
probe=r'''window.__actualRoadCold={read:()=>JSON.parse(archivePayload()),wait:async()=>{await saveStorePromise;await saveWrites;}};'''
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'assets')));Thread(target=server.serve_forever,daemon=True).start()
def diff(a,b,path=''):
 if type(a)!=type(b):return [{'path':path,'before':a,'after':b}]
 if isinstance(a,dict):return sum([diff(a.get(k),b.get(k),path+'.'+k) for k in a.keys()|b.keys()],[])
 if isinstance(a,list):return [{'path':path,'beforeLength':len(a),'afterLength':len(b)}]if len(a)!=len(b)else sum([diff(x,y,path+'['+str(i)+']')for i,(x,y)in enumerate(zip(a,b))],[])
 return []if a==b else [{'path':path,'before':a,'after':b}]
try:
 with sync_playwright()as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();
  if not args.live_days:p.add_init_script('window.requestAnimationFrame=()=>0')
  p.route('**/game.js',lambda r:r.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'),content_type='text/javascript'));p.goto('http://127.0.0.1:'+str(server.server_port)+'/index.html');p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();
  if args.live_days:
   p.locator('#speedRange').fill('3');p.locator('#speedRange').dispatch_event('change');p.locator('#pause').click();p.wait_for_function('n=>__actualRoadCold.read().day>=n',arg=1+args.live_days,polling=25);p.locator('#pause').click()
  if args.legacy_v60:
   legacy=subprocess.check_output(['git','show','525e47d:tests/fixtures/v60-distressed-town.json'],cwd=ROOT,text=True);p.locator('[data-panel=settings]').click();p.locator('#importSave').click();p.locator('#importText').fill(legacy);p.locator('#restoreGo').click();p.wait_for_function('document.getElementById("helpDialog").style.display==="none"',polling=10)
  p.locator('[data-panel=settings]').click();p.locator('#saveNow').click();p.wait_for_function('!document.querySelector("#saveNow").disabled',polling=10);p.evaluate('__actualRoadCold.wait()');before=p.evaluate('__actualRoadCold.read()');
  if args.live_days:p.add_init_script('window.requestAnimationFrame=()=>0')
  p.reload();p.locator('#continue').wait_for(state='visible');p.locator('#continue').click();after=p.evaluate('__actualRoadCold.read()');b.close()
finally:server.shutdown()
out={'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'realUiControls':True,'rafDisabledToFreezeCompletedDay':not bool(args.live_days),'actualLiveDaysRequested':args.live_days,'legacyV60NormalizedThroughUiBeforeSave':args.legacy_v60,'dayBefore':before['day'],'dayAfter':after['day'],'excludedFields':[],'differences':diff(before,after),'exact':before==after};dest=ROOT/'reports/road-canonical-724';dest.mkdir(exist_ok=True,parents=True);(dest/('actual-newtown-cold-before.json' if args.expect_mismatch else ('actual-legacy-v60-cold.json' if args.legacy_v60 else 'actual-live-committed-cold.json' if args.live_days else 'actual-newtown-cold-after.json'))).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert out['exact']!=args.expect_mismatch,out
