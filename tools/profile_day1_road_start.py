"""Bounded host synchronous start timing, actual New Town click, no APK claim."""
from pathlib import Path
import sys,json,subprocess,hashlib,statistics
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
base=subprocess.check_output(['git','show','72419dc:assets/game.js'],cwd=ROOT,text=True)
# Assemble the source-only candidate in memory, keeping the tracked distribution unchanged.
fixed=base.replace("centerTownCamera();invalidateRoads();buildMode='';","centerTownCamera();invalidateRoads();G.roadMetrics=roadMetrics();buildMode='';",1)
assert hashlib.sha256(fixed.encode()).hexdigest()=='d3ed25306c7c4754485d0691d04d9d4f9739dccafc1d2efbaa909762977a7081'
hook=r'''const timingStart=start,timingRoad=roadMetrics;let timingActive=false,timingRows=[];roadMetrics=function(){const t=performance.now();try{return timingRoad.apply(this,arguments);}finally{if(timingActive)timingRows.push(performance.now()-t);}};start=function(){timingActive=true;timingRows=[];const t=performance.now();try{return timingStart.apply(this,arguments);}finally{window.day1StartTiming={startMs:performance.now()-t,roadCalls:timingRows.length,roadMs:timingRows.slice(),rng:rngState};timingActive=false;}};'''
rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for n in range(6):
  pair=[]
  for variant,source in [('baseline',base),('fixed',fixed)]:
   p=b.new_page();p.set_content(html);p.evaluate('window.requestAnimationFrame=()=>0');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'));p.locator('#townSeed').fill('42');p.locator('#newTown').click();r=p.evaluate('day1StartTiming');r.update({'repeat':n,'variant':variant});rows.append(r);pair.append(r);p.close()
  assert pair[0]['rng']==pair[1]['rng']and pair[1]['roadCalls']==pair[0]['roadCalls']+1
 b.close()
out={'baseSourceSha256':hashlib.sha256(base.encode()).hexdigest(),'fixedSourceSha256':hashlib.sha256(fixed.encode()).hexdigest(),'hostSynchronousStartOnly':True,'nativeOrColdAppStartupClaim':False,'noOtherBenchmarksConcurrent':True,'rows':rows,'summary':{v:{'medianStartMs':statistics.median([r['startMs']for r in rows if r['variant']==v]),'maxStartMs':max(r['startMs']for r in rows if r['variant']==v),'roadCallsPerStart':rows[0 if v=='baseline' else 1]['roadCalls']}for v in ['baseline','fixed']}};d=ROOT/'reports/road-canonical-724';d.mkdir(exist_ok=True,parents=True);(d/'start-timing.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['summary'],indent=2))
