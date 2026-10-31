"""Native suspend must park presentation and autosaves, even while visible.

The native host may retain a visible WebView/RAF while a document picker or
activity transition is in flight. A suspend saves once; background RAFs must not
keep rebuilding UI or enqueue further save revisions. Resume keeps user pause.
"""
from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
probe=r'''
const schedulerCalls={header:0,panel:0,save:0,draw:0};
const schedulerHeader=updateHeader;updateHeader=function(){schedulerCalls.header++;return schedulerHeader()};
const schedulerPanel=renderPanel;renderPanel=function(...a){schedulerCalls.panel++;return schedulerPanel(...a)};
const schedulerSave=save;save=function(){schedulerCalls.save++;return schedulerSave()};
const schedulerDraw=draw;draw=function(){schedulerCalls.draw++;return schedulerDraw()};
window.__scheduler={
 ready:()=>saveStorePromise,
 suspend:async()=>{await window.__townArchive.suspend();for(const key of Object.keys(schedulerCalls))schedulerCalls[key]=0;lastAutosave=performance.now()-gameOptions.autoSave*1000-1;lastPanel=0;lastHeader=0;dirty=true;},
 state:()=>({calls:{...schedulerCalls},day:G.day,paused,suspended:hostSuspended,order:saveOrder}),
 resume:()=>window.__townArchive.resume()
};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.evaluate('__scheduler.ready()');p.locator('#newTown').click();p.locator('#panelClose').click();p.locator('[data-panel=economy]').click();p.locator('body').click(position={'x':2,'y':2});p.evaluate('__scheduler.suspend()');before=p.evaluate('__scheduler.state()');p.wait_for_timeout(1800);after=p.evaluate('__scheduler.state()');assert after['day']==before['day'] and after['order']==before['order'],(before,after);assert after['calls']==dict.fromkeys(['header','panel','save','draw'],0),after
 p.evaluate('__scheduler.resume()');p.wait_for_timeout(1800);resumed=p.evaluate('__scheduler.state()');assert resumed['day']>after['day'] and resumed['calls']['header']>0 and resumed['calls']['draw']>0,resumed;p.locator('#pause').click();p.evaluate('__scheduler.suspend()');p.evaluate('__scheduler.resume()');p.wait_for_timeout(200);assert p.evaluate('__scheduler.state().paused');assert not errors,errors;b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/session-performance';out.mkdir(exist_ok=True);(out/'scheduler-idle.json').write_text(json.dumps({'source_sha256':sha,'before':before,'suspended':after,'resumed':resumed,'errors':errors},indent=2)+'\n');print('PASS native suspension parks UI, draw and recurring saves; resume advances and preserves user pause')
