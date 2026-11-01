"""Accepted model transaction invalidation refreshes visual context, no scan/draw."""
from pathlib import Path
import subprocess,json
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
source=(R/'assets/game.js').read_text();probe='''window.__revisionProbe=()=>{const first=__cityVisualSnapshot(),cached=cityVisualContext(),rev=__cityVisualRevision(),day=G.day,h=G.households.find(h=>h.cash>2),bank=G.banks.find(b=>!b.closed),before=totalMoney();if(!h||!bank)throw Error('fixture requires funded household/bank');const paid=depositTransfer(h,bank,1),next=__cityVisualSnapshot(),fresh=cityVisualContext(),after=__townTest.save(),again=__cityVisualSnapshot();const result={paid,sameDay:G.day===day,revisionChanged:rev!==next.revision,cacheReplaced:cached!==fresh,cachedStable:fresh===cityVisualContext(),semantics:next.districtSemanticsAccepted,totalInvariant:before===totalMoney(),descriptorExact:next.buildings.every(b=>JSON.stringify(b.architecture)===JSON.stringify(urbanBuildingDescriptor(b.id))),readInvariant:after===__townTest.save()};simulationBusy=true;result.partialGuard=__cityVisualSnapshot()===null&&__cityVisualRevision()==='';simulationBusy=false;return result;};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
server=subprocess.Popen(['python','-m','http.server','8796','--bind','127.0.0.1'],cwd=R/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(body=script,content_type='application/javascript'));p.goto('http://127.0.0.1:8796/index.html');p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__revisionProbe()');assert r['paid']==1 and all(v is True for k,v in r.items()if k!='paid'),r;assert not errors,errors;r['errors']=errors;(R/'docs/previews/webgl-current-model-8/committed-revision.json').write_text(json.dumps(r,indent=2));print(r);b.close()
finally:server.terminate()
