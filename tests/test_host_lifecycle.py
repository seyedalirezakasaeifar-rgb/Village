"""Browser/native suspend boundary, no wall-gap catch-up, pause preference preserved."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js','''
window.__lifecycleGap=()=>{acc=100;last=performance.now()-600000;};
window.__lifecycleState=()=>({suspended:hostSuspended,paused,queued:acc,clockGap:performance.now()-last});
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("settlement",42)');p.locator('#speedRange').evaluate("e=>{e.value='6';e.dispatchEvent(new Event('input',{bubbles:true}));}");p.locator('#pause').click();p.wait_for_timeout(200)
 p.evaluate('__townArchive.suspend()');before=p.evaluate('__townTest.get().day');p.wait_for_timeout(500);assert p.evaluate('__townTest.get().day')==before
 r=p.evaluate('__lifecycleGap();__townArchive.resume();__lifecycleState()');assert not r['suspended'] and not r['paused'] and r['queued']==0 and r['clockGap']<30,r
 p.locator('#pause').click();r=p.evaluate('__townArchive.suspend();__townArchive.resume();__lifecycleState()');assert r['paused'] and not r['suspended'],r
 p.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>window.__testHidden});window.__testHidden=true;document.dispatchEvent(new Event('visibilitychange'));");r=p.evaluate("__lifecycleGap();window.__testHidden=false;document.dispatchEvent(new Event('visibilitychange'));__lifecycleState()");assert r['queued']==0 and r['clockGap']<30,r;assert not errors,errors;b.close();print('PASS host suspend halts real RAF simulation; resume clears stale clock/queue and preserves user pause')
