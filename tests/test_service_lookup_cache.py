"""Cached provider forecasts match uncached public access and invalidate safely."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
probe=r'''
window.__serviceCacheProbe=()=>{__townTest.reset('regional',42);G.autoBuild=false;__townTest.step(3);const check=()=>{for(const h of G.households){if(Math.abs(privateSchoolPublicGap(h)-(1-publicCivicCoverage('school',h.id)))>1e-12)throw Error('School cache differs');const b=readBuild(h.home),stations=G.buildings.filter(s=>s.kind==='fire'&&isPublicFacility(s)),d=stations.length?Math.min(...stations.map(s=>roadServiceDistance(b,s))):80,expected=clamp(1-d/58,0,1)*defensePower();if(Math.abs(publicFireResponse(b)-expected)>1e-12)throw Error('Fire cache differs');}};
 check();G.policy.educationBudget=0;G.policy.defenseBudget=0;__townTest.step(1);check();invalidateRoads(false);check();privatePublicSchoolCache=null;const original=serviceAccess;let calls=0;serviceAccess=function(kind){calls++;return original(kind)};for(let repeat=0;repeat<3;repeat++)for(const h of G.households)privateSchoolPublicGap(h);serviceAccess=original;if(calls!==1)throw Error('Repeated household scans: '+calls);return{households:G.households.length,schoolAccessBuildCalls:calls,valid:validateTown()};};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__serviceCacheProbe()');assert r['valid']['ok'];b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-8.0';(out/'service-cache.json').write_text(json.dumps({'source_sha256':sha,**r},indent=2)+'\n');print('PASS service cache equals uncached access after funding/day/road changes; one school access scan across repeated whole-town lookups',r)
