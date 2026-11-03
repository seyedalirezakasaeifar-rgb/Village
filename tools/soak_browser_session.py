"""Timed real-RAF session, UI/save cycling, cache bounds and optional V8 heap probes.

Default ten minutes. Duration can be raised for overnight QA. The live run is
not accelerated with __townTest.step and does not use forced GC during play.
"""
from pathlib import Path
import os,sys,time,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest();duration=max(60,int(os.environ.get('TOWNLEDGER_SOAK_SECONDS','600')));expand=os.environ.get('TOWNLEDGER_SOAK_EXPAND')=='1';out=ROOT/'reports/development-player-loop';out.mkdir(parents=True,exist_ok=True);samples=[];errors=[]
script=source.decode().replace('// SOURCE: 99-instrumentation.js','''
window.__sessionSnapshot=()=>({day:G.day,population:G.stats.population,buildings:G.buildings.length,households:G.households.length,people:G.people.length,journal:G.journal.length,events:G.events.length,observations:G.observations.length,transactions:G.transactions.length,loans:G.loans.length,atlas:atlas.size,atlasBytes,serviceCaches:serviceAccessCaches.size,traffic:traffic.length,valid:validateTown(),sourceVersion:G.version,gridSize:G.gridSize,chartered:G.charter?.owned.length||0,waterVessels:waterVessels.size,waterManifests:G.waterway?.manifests.length||0,riverExports:G.waterway?.exports||0,goodsError:Math.max(...goodsBalance().map(v=>Math.abs(v.error)))});
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':844,'height':390},has_touch=True);p.set_default_timeout(10000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#panelClose').click();p.locator('#pause').click();p.evaluate('__townTest.reset("regional",42)')
 if expand:
  for district in ['river-reach','east-meadow']:
   p.locator('[data-panel=construction]').click();p.locator('#charterOffice>summary').click();p.locator('[data-parcel-buy='+district+']').click();p.locator('[data-event-choice="0"]').click();p.locator('#panelClose').click()
 cdp=p.context.new_cdp_session(p);cdp.send('Performance.enable');cdp.send('HeapProfiler.collectGarbage');initial=cdp.send('Runtime.getHeapUsage');p.locator('#speedRange').evaluate("e=>{e.value='4';e.dispatchEvent(new Event('input',{bubbles:true}));}");p.locator('#pause').click();started=time.monotonic();next_sample=0;panels=['economy','community','agenda','citizens','policies','banking','construction','settings'];index=0
 while time.monotonic()-started<duration:
  p.wait_for_timeout(1000)
  elapsed=time.monotonic()-started
  if elapsed<next_sample:continue
  target=panels[index%len(panels)];p.locator(f'[data-panel={target}]').click();assert 'Panel error' not in p.locator('#panelBody').inner_text()
  if target=='settings':p.locator('[data-preference=quality]').select_option(['low','high','balanced'][(index//len(panels))%3])
  p.locator('#panelBody').evaluate('e=>e.scrollTop=e.scrollHeight');p.locator('#panelClose').click()
  if index%3==2:
   # Pause for a genuine archive round trip; then resume actual RAF scheduling.
   p.locator('#pause').click();raw=p.evaluate('__townTest.save()');assert p.evaluate('s=>__townTest.load(s)',raw);p.locator('#pause').click()
  sample=p.evaluate('__sessionSnapshot()');sample['seconds']=round(elapsed,1);sample['heap']=cdp.send('Runtime.getHeapUsage');assert sample['valid']['ok'],sample['valid'];assert sample['atlas']<=600 and sample['atlasBytes']<=48*1024*1024 and sample['serviceCaches']<=2 and sample['observations']<=1200 and sample['traffic']<=80 and sample['loans']<=2500 and sample['waterVessels']<=32 and sample['waterManifests']<=48 and sample['goodsError']<.001 and sample['gridSize']==80 and (not expand or sample['chartered']>=2),sample
  samples.append(sample);assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha;assert not errors,errors
  (out/'browser-session.json').write_text(json.dumps({'source_sha256':sha,'expanded':expand,'durationRequested':duration,'initialHeapAfterGC':initial,'samples':samples,'errors':errors},indent=2)+'\n');print(round(elapsed),sample['day'],sample['population'],'heap',round(sample['heap']['usedSize']/1048576,1),'MiB',flush=True);next_sample+=30;index+=1
 p.locator('#pause').click();cdp.send('HeapProfiler.collectGarbage');final=cdp.send('Runtime.getHeapUsage');r={'source_sha256':sha,'expanded':expand,'elapsedSeconds':time.monotonic()-started,'initialHeapAfterGC':initial,'finalHeapAfterGC':final,'samples':samples,'errors':errors};(out/'browser-session.json').write_text(json.dumps(r,indent=2)+'\n');assert not errors,errors;b.close()
print('PASS timed real-RAF session, menu/archive cycles, invariants and bounded named caches; heap growth must be interpreted against town growth')
