"""Diagnostic invalidation callers on the immutable correctness reference; not a timing gate."""
import sys,subprocess,gzip,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=subprocess.check_output(['git','show','2e4ce5c:assets/game.js'],text=True,cwd=ROOT)
probe=r'''const districtInvalidationBase=invalidateUrban,districtBuildBase=urbanSpatial;let districtTrace=[];invalidateUrban=function(){if(urbanCache)districtTrace.push({day:G.day,type:'invalidate',caller:new Error().stack.split('\n').slice(2,4).map(s=>s.trim().replace(/ \(.*$/,''))});return districtInvalidationBase()};urbanSpatial=function(){const previous=urbanCache,c=districtBuildBase();if(c!==previous)districtTrace.push({day:G.day,type:'build',caller:new Error().stack.split('\n').slice(2,4).map(s=>s.trim().replace(/ \(.*$/,''))});return c};window.__districtInvalidation=a=>{__townTest.load(a);closePanel();paused=true;districtTrace=[];__townTest.step(30);return districtTrace};'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();rows=p.evaluate('a=>__districtInvalidation(a)',gzip.decompress((ROOT/'tests/fixtures/retail-refusal-pending-project.json.gz').read_bytes()).decode());b.close()
print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'limits':'Diagnostic stack capture only; not timed benchmark','events':rows},indent=2))
