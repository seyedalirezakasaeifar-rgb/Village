from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js', 'window.__freshSeed=(sc,n)=>{chosenScenario=sc;seed(n)};\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
 r=p.evaluate('''()=>{const canon=v=>Array.isArray(v)?v.map(canon):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canon(v[k])])):v;const snap=()=>{const g=JSON.parse(__townTest.save());delete g.trafficState;delete g.visualState;return canon(g)};const result=[];for(const sc of ['settlement','regional','hardtimes','industrial'])for(const seed of [42,101,909]){__freshSeed(sc,seed);const before=snap(),raw=__townTest.save();if(!__townTest.load(raw))throw Error('Rejected');const after=snap(),changed=Object.keys(before).filter(k=>JSON.stringify(before[k])!==JSON.stringify(after[k]));if(changed.length)throw Error(sc+seed+': '+changed+JSON.stringify(Object.keys(after.stats).filter(k=>before.stats[k]!==after.stats[k]).map(k=>[k,before.stats[k],after.stats[k]])));result.push({scenario:sc,seed,exact:true});}return result;}''');b.close()
print('PASS',r);out=ROOT/'reports/fresh-save';out.mkdir(exist_ok=True);(out/'result.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':r},indent=2))
