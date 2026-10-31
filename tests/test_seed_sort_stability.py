"""A seed must not depend on how an engine schedules comparator calls."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
script=source.decode().replace('// SOURCE: 99-instrumentation.js','''
window.__sortSeedProbe=(scenario,seedValue)=>{const original=Array.prototype.sort;try{
 const snapshot=()=>{const g=JSON.parse(archivePayload());delete g.trafficState;delete g.visualState;return g;};
 chosenScenario=scenario;seed(seedValue);const normal=snapshot();
 Array.prototype.sort=function(compare){const cmp=compare||((a,b)=>String(a)<String(b)?-1:String(a)>String(b)?1:0);for(let i=1;i<this.length;i++){const value=this[i];let j=i-1;while(j>=0&&cmp(this[j],value)>0){this[j+1]=this[j];j--;}this[j+1]=value;}return this;};
 chosenScenario=scenario;seed(seedValue);const alternate=snapshot();
 return {scenario,seed:seedValue,same:JSON.stringify(normal)===JSON.stringify(alternate),normalTotal:normal.accounts.baseline,alternateTotal:alternate.accounts.baseline,normalRng:normal.rngState,alternateRng:alternate.rngState};
 }finally{Array.prototype.sort=original;}};
// SOURCE: 99-instrumentation.js''')
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click()
 for scenario in ['settlement','frontier','hardtimes','industrial','regional']:
  for seed in [42,101,909]:
   r=p.evaluate('o=>__sortSeedProbe(o.scenario,o.seed)',{'scenario':scenario,'seed':seed});rows.append(r);assert r['same'],r
 b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-map-and-seeds';out.mkdir(parents=True,exist_ok=True);(out/'seed-sort.json').write_text(json.dumps({'source_sha256':sha,'rows':rows},indent=2)+'\n');print('PASS 15 authored starts identical under native and alternate stable insertion sorting')
