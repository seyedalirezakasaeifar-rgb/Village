from pathlib import Path
import subprocess,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];server=subprocess.Popen(['python','-m','http.server','8778','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':844,'height':390});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8778/index.html',wait_until='networkidle');page.locator('#newTown').click();page.locator('#pause').click();before=page.evaluate('__townTest.save()');r=page.evaluate('()=>{const t=performance.now(),s=__cityVisualSnapshot();let k;for(let i=0;i<10;i++)k=__cityVisualSnapshot();return {firstAnd10CachedMs:performance.now()-t,districtCount:Object.keys(s.districts).length,buildings:s.buildings.length,hasTenure:s.buildings.every(b=>b.tenure&&b.stage),incomeBands:[...new Set(Object.values(s.districts).map(d=>d.incomeBand))]};}');after=page.evaluate('__townTest.save()');assert json.loads(before)==json.loads(after);assert r['hasTenure'];assert not errors,errors;r.update({'archiveInvariant':True,'errors':errors});out=ROOT/'docs/previews/newfoundland-families-8';out.mkdir(parents=True,exist_ok=True);(out/'context.json').write_text(json.dumps(r,indent=2)+'\n');print(r);b.close()
finally:server.terminate()
