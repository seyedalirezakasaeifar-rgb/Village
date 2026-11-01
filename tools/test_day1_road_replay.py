"""Actual New Town startup followed by paired model replay, complete fields/RNG."""
from pathlib import Path
import sys,json,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
base=subprocess.check_output(['git','show','72419dc:assets/game.js'],cwd=ROOT,text=True);fixed=(ROOT/'assets/game.js').read_text();probe=r'''window.__day1RoadReplay={read:()=>({archive:JSON.parse(archivePayload()),rng:rngState,total:totalMoney()}),step:n=>{__townTest.step(n);return {archive:JSON.parse(archivePayload()),rng:rngState,total:totalMoney()};}};''';rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for code in [base,fixed]:
  p=b.new_page();p.set_content(html);p.evaluate('window.requestAnimationFrame=()=>0');p.add_script_tag(content=code.replace('// SOURCE: 99-instrumentation.js',probe+'// SOURCE: 99-instrumentation.js'));p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();pages.append(p)
 old,new=[p.evaluate('__day1RoadReplay.read()')for p in pages];assert old['rng']==new['rng']and old['total']==new['total'];assert old['archive']['roadMetrics']is None and isinstance(new['archive']['roadMetrics'],dict);old['archive']['roadMetrics']=new['archive']['roadMetrics'];assert old['archive']==new['archive'],'Startup changed more than rebuilt derived metrics'
 for n in [1,29,29,60]:
  pair=[p.evaluate('n=>__day1RoadReplay.step(n)',n)for p in pages];assert pair[0]==pair[1],'Complete model/RNG/cash/route replay diverged';rows.append({'day':pair[1]['archive']['day'],'wholeModelRngMoneyRoutesExact':True,'excludedFields':[],'archiveHash':hashlib.sha256(json.dumps(pair[1]['archive'],sort_keys=True,separators=(',',':')).encode()).hexdigest()})
 b.close()
out={'baseSourceSha256':hashlib.sha256(base.encode()).hexdigest(),'fixedSourceSha256':hashlib.sha256(fixed.encode()).hexdigest(),'actualNewTownStartup':True,'subsequentDirectQaSteps':True,'initialOnlyDifference':'roadMetrics null to deterministic derived snapshot','rows':rows};d=ROOT/'reports/road-canonical-724';d.mkdir(exist_ok=True,parents=True);(d/'day1-fix-replay.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
