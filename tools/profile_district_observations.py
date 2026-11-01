"""Paired host-only whole-day cost attribution; not a device/FPS acceptance gate."""
import gzip,hashlib,json,subprocess,statistics
from playwright.sync_api import sync_playwright
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
BASE='848bf1bfb8fdddc3155ba5a7773348d28073ade4';base=subprocess.check_output(['git','show',BASE+':assets/game.js'],cwd=ROOT,text=True);current=(ROOT/'assets/game.js').read_text();archive=gzip.decompress((ROOT/'tests/fixtures/retail-refusal-pending-project.json.gz').read_bytes()).decode()
probe=r'''let districtCold=0,districtCalls=0,districtCPU=0,districtTickCPU=0;const districtSpatialBase=urbanSpatial,districtTickBase=tick;
urbanSpatial=function(...args){const previous=urbanCache,start=performance.now(),result=districtSpatialBase(...args);districtCalls++;if(result!==previous){districtCold++;districtCPU+=performance.now()-start}return result};
tick=function(...args){const start=performance.now();try{return districtTickBase(...args)}finally{districtTickCPU+=performance.now()-start}};
window.__districtCost={run:({archive,days})=>{if(!__townTest.load(archive))throw Error('Fixture rejected');closePanel();paused=true;const money=totalMoney();districtCold=0;districtCalls=0;districtCPU=0;districtTickCPU=0;const start=performance.now();__townTest.step(days);const wall=performance.now()-start;return {days,wallMs:wall,tickCPUms:districtTickCPU,coldSpatialBuilds:districtCold,spatialCalls:districtCalls,coldSpatialCPUms:districtCPU,moneyError:totalMoney()-money,valid:validateTown().ok}}};'''
result={'base':BASE,'base_source_sha256':hashlib.sha256(base.encode()).hexdigest(),'source_sha256':hashlib.sha256(current.encode()).hexdigest(),'fixture':'765-person ordinary-resource regional seed42 day721','samples':[]}
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages={}
 for label,source in [('base',base),('candidate',current)]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('a=>__districtCost.run(a)',{'archive':archive,'days':7});pages[label]=p
 for days in [20,30]:
  for repeat in range(3):
   for label in (['base','candidate']if repeat%2==0 else['candidate','base']):
    row=pages[label].evaluate('a=>__districtCost.run(a)',{'archive':archive,'days':days});assert row['valid']and abs(row['moneyError'])<.001,row;result['samples'].append({'label':label,'repeat':repeat,**row})
 b.close()
result['medians']=[{'days':days,'label':label,**{key:statistics.median(x[key]for x in result['samples']if x['days']==days and x['label']==label)for key in ['wallMs','tickCPUms','coldSpatialBuilds','coldSpatialCPUms']}}for days in [20,30]for label in ['base','candidate']]
result['limits']='Alternating repeated host Chromium samples, same initial archive, seven-day warmups; synchronous test-step includes header update. No renderer/GPU/input/native/large-world/thermal certification.'
print(json.dumps(result,indent=2))
