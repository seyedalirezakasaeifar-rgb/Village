"""Periodic DOM/archive tasks yield after frames; direct actions stay immediate.
Real loopback storage checks pre-serialization coalescing and stale-town guards.
"""
from pathlib import Path
import functools,hashlib,http.server,json,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
probe=r'''
let guardFrame=0,guardArmed=false;const guardCalls={panel:[],save:[]};
const guardFrameBase=frame;frame=function(now){guardFrame++;try{return guardFrameBase(now)}finally{guardFrame--}};
const guardPanelBase=renderPanel;renderPanel=function(tab){if(guardArmed)guardCalls.panel.push({frame:guardFrame,tab,day:G.day});return guardPanelBase(tab)};
const guardSaveBase=save;save=function(){if(guardArmed)guardCalls.save.push({frame:guardFrame,day:G.day});return guardSaveBase()};
window.__periodic={
 ready:()=>saveStorePromise,
 arm:()=>{guardCalls.panel.length=0;guardCalls.save.length=0;guardArmed=true;lastPanel=0;lastAutosave=performance.now()-gameOptions.autoSave*1000-1;},
 reset:()=>{guardCalls.panel.length=0;guardCalls.save.length=0;guardArmed=true;},
 state:()=>({calls:guardCalls,panelPending:!!periodicPanelTimer,savePending:!!periodicSaveTimer,revision:saveRevision,ok:autoSaveOK,valid:validateTown(),total:totalMoney()}),
 burst:()=>{for(let i=0;i<200;i++)queuePeriodicSave()},
 focus:()=>{queuePeriodicPanel();const input=document.createElement('input');input.id='guardDraft';input.value='unsaved input';$('panelBody').appendChild(input);input.focus()},
 manual:()=>{queuePeriodicSave();$('saveNow').click();return guardCalls.save.length},
 failStorage:()=>{const set=Storage.prototype.setItem,write=writeIndexedDB;Storage.prototype.setItem=()=>{throw Error('Injected quota failure')};writeIndexedDB=()=>Promise.resolve(false);window.__restorePeriodicStorage=()=>{Storage.prototype.setItem=set;writeIndexedDB=write};},
 stale:()=>{queuePeriodicPanel();queuePeriodicSave();__townTest.reset('settlement',101);lastPanel=performance.now();lastAutosave=performance.now();return {panel:guardCalls.panel.length,save:guardCalls.save.length}},
 busy:()=>{queuePeriodicPanel();queuePeriodicSave();simulationBusy=true},
 finishBusy:()=>{simulationBusy=false;lastPanel=performance.now();lastAutosave=performance.now()},
 suspend:async()=>{queuePeriodicPanel();queuePeriodicSave();await __townArchive.suspend()},
};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();rows={}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')));p.goto('http://127.0.0.1:'+str(server.server_port)+'/index.html');p.evaluate('__periodic.ready()');p.locator('#newTown').click();p.locator('#panelClose').click();p.locator('[data-panel=economy]').click();p.locator('#panelTitle').click();p.wait_for_timeout(200);p.evaluate('__periodic.arm()');p.wait_for_function('__periodic.state().calls.panel.length>=1&&__periodic.state().calls.save.length>=1');rows['periodic']=p.evaluate('__periodic.state()');assert all(v['frame']==0 for a in rows['periodic']['calls'].values() for v in a),rows['periodic'];p.locator('#pause').click();p.locator('#panelClose').click()
 p.evaluate('__periodic.reset();__periodic.burst()');p.wait_for_function('!__periodic.state().savePending');rows['burst']=p.evaluate('__periodic.state()');# Paused periodic autosaves are cancelled, preserving explicit pause's own save.
 assert len(rows['burst']['calls']['save'])==0,rows['burst']
 p.locator('#pause').click();p.evaluate('__periodic.reset();__periodic.burst()');p.wait_for_function('!__periodic.state().savePending');rows['runningBurst']=p.evaluate('__periodic.state()');assert len(rows['runningBurst']['calls']['save'])==1,rows['runningBurst'];p.locator('[data-panel=settings]').click();p.evaluate('__periodic.reset()');immediate=p.evaluate('__periodic.manual()');assert immediate==1,immediate;p.wait_for_function('!__periodic.state().savePending&&!document.querySelector("#saveNow").disabled');rows['manual']=p.evaluate('__periodic.state()');assert len(rows['manual']['calls']['save'])==1 and rows['manual']['ok'],rows['manual'];p.evaluate('__periodic.reset();__periodic.failStorage();__periodic.manual()');p.wait_for_function('!__periodic.state().savePending&&!document.querySelector("#saveNow").disabled');rows['failedManual']=p.evaluate('__periodic.state()');assert len(rows['failedManual']['calls']['save'])==2 and not rows['failedManual']['ok'],rows['failedManual'];p.evaluate('__restorePeriodicStorage()');p.locator('#saveNow').click();p.wait_for_function('!document.querySelector("#saveNow").disabled');assert p.evaluate('__periodic.state().ok');p.locator('#panelClose').click()
 p.locator('[data-panel=economy]').click();p.evaluate('__periodic.reset();__periodic.focus()');p.wait_for_timeout(100);rows['focus']=p.evaluate('__periodic.state()');assert not rows['focus']['calls']['panel'],rows['focus'];p.locator('#panelTitle').click();p.evaluate('__periodic.reset()');p.evaluate('__periodic.suspend()');p.wait_for_timeout(100);rows['suspended']=p.evaluate('__periodic.state()');assert len(rows['suspended']['calls']['save'])==1 and not rows['suspended']['calls']['panel'],rows['suspended'];p.evaluate('__townArchive.resume();__periodic.reset();__periodic.busy()');p.wait_for_timeout(100);rows['busy']=p.evaluate('__periodic.state()');assert not rows['busy']['calls']['panel'] and not rows['busy']['calls']['save'],rows['busy'];p.evaluate('__periodic.finishBusy();__periodic.reset()');counts=p.evaluate('__periodic.stale()');p.wait_for_timeout(100);rows['stale']=p.evaluate('__periodic.state()');assert len(rows['stale']['calls']['panel'])==counts['panel'] and len(rows['stale']['calls']['save'])==counts['save'],(counts,rows['stale']);assert rows['stale']['valid']['ok'] and not errors,errors;b.close()
server.shutdown();assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/session-performance';out.mkdir(exist_ok=True);(out/'periodic-presentation.json').write_text(json.dumps({'source_sha256':sha,'rows':rows,'errors':errors},indent=2)+'\n');print('PASS post-frame periodic tasks, immediate durable Save, coalesced requests, focus and town/suspend guards')
