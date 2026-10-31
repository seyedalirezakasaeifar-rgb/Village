"""Same host, same regional start; real wall-clock 64x and UI-latency comparison.
CDP 4x CPU throttling is a synthetic workload, not Android performance evidence.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os,time,json,hashlib
R=Path(__file__).resolve().parents[1];rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 for release,path in [('6.0',R/'reference/v6.0/assets'),('6.1',R/'assets')]:
  for throttle in [1,4]:
   p=b.new_page(viewport={'width':1280,'height':720});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto((path/'index.html').as_uri());p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('regional',42);__townTest.step(360)");p.locator('#panelClose').click();p.locator('#speedRange').fill('6');c=p.context.new_cdp_session(p);c.send('Emulation.setCPUThrottlingRate',{'rate':throttle});p.locator('#pause').click();start=p.evaluate('__townTest.get().day');t=time.monotonic();p.wait_for_timeout(8000);elapsed=time.monotonic()-t;end=p.evaluate('__townTest.get().day');tt=time.monotonic();p.locator('[data-panel=settings]').click();latency=(time.monotonic()-tt)*1000;p.locator('#pause').click();perf=p.evaluate('''()=>{const a=__townTest.perf();return {drawMedian:a.frames.slice().sort((a,b)=>a-b)[a.frames.length/2|0],tickMedian:a.ticks.slice().sort((a,b)=>a-b)[a.ticks.length/2|0],displayedSpeed:a.effective}}''');row={'release':release,'cpuThrottle':throttle,'completedDays':end-start,'wallSeconds':elapsed,'measuredSpeed':(end-start)*1.65/elapsed,'panelClickMs':latency,'perf':perf,'errors':errors};rows.append(row);print(json.dumps(row),flush=True);assert not errors
   if release=='6.1' and throttle==1:assert row['measuredSpeed']>48,row
   p.close()
 b.close()
(R/'reports/v6.1/performance-comparison.json').write_text(json.dumps({'source_sha256':hashlib.sha256((R/'assets/game.js').read_bytes()).hexdigest(),'rows':rows,'androidMeasured':False},indent=2)+'\n')
