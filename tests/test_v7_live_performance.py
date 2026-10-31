from pathlib import Path
from playwright.sync_api import sync_playwright
import os,json,time,hashlib
R=Path(__file__).resolve().parents[1];digest=hashlib.sha256((R/'assets/game.js').read_bytes()).hexdigest();rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox']);p=b.new_page(viewport={'width':1280,'height':720});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto((R/'assets/index.html').as_uri());p.locator('#newTown').click();p.locator('#pause').click()
 for name in ['settlement','regional']:
  raw=(R/f'reports/final/{name}-endurance-town.json').read_text();assert p.evaluate('s=>__townTest.load(s)',raw)
  if p.locator('#panel').evaluate('e=>e.classList.contains("show")'):p.locator('#panelClose').click()
  p.locator('#speedRange').fill('6');p.locator('#pause').click();start=p.evaluate('__townTest.get()');t=time.monotonic();p.wait_for_timeout(10000);elapsed=time.monotonic()-t;end=p.evaluate('__townTest.get()');click=time.monotonic();p.locator('[data-panel=economy]').click();latency=(time.monotonic()-click)*1000;p.locator('#pause').click();assert 'Panel error' not in p.locator('#panelBody').inner_text();perf=p.evaluate('''()=>{const p=__townTest.perf(),q=(a,t)=>{a=a.slice().sort((a,b)=>a-b);return a[Math.min(a.length-1,Math.floor(a.length*t))]||0};return {drawMedian:q(p.frames,.5),drawP95:q(p.frames,.95),tickMedian:q(p.ticks,.5),tickP95:q(p.ticks,.95),displayedRate:p.effective}}''');row={'town':name,'population':start['population'],'requestedRate':64,'measuredRate':(end['day']-start['day'])*1.65/elapsed,'completedDays':end['day']-start['day'],'seconds':elapsed,'economyClickMs':latency,'cpuTimings':perf};rows.append(row);print(json.dumps(row),flush=True);assert __import__('math').isfinite(row['measuredRate']) and row['measuredRate']>20;assert abs(end['total']-start['total'])<.1
 assert not errors,errors;b.close()
assert hashlib.sha256((R/'assets/game.js').read_bytes()).hexdigest()==digest
(R/'reports/v7.0/live-performance.json').write_text(json.dumps({'source_sha256':digest,'hostBrowserOnly':True,'physicalAndroid':False,'rows':rows,'errors':errors},indent=2))
