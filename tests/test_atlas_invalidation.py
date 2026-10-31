"""Repeated light/quality changes reset the sprite byte budget with its contents."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest();script=source.decode().replace('// SOURCE: 99-instrumentation.js',"window.__atlasState=()=>({count:atlas.size,bytes:atlasBytes,actual:[...atlas.values()].reduce((n,c)=>n+c.width*c.height*4,0)});\n// SOURCE: 99-instrumentation.js")
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("regional",42)');p.locator('[data-panel=settings]').click();archive=p.evaluate('__townTest.save()');rows=[]
 for i in range(12):
  r=p.evaluate('document.querySelector("#nightView").click();__atlasState()');assert r['count']==0 and r['bytes']==0,r;p.wait_for_timeout(30);r=p.evaluate('__atlasState()');assert r['count']>0 and r['bytes']==r['actual'] and r['bytes']<=48*1024*1024,r;rows.append(r)
 p.locator('[data-preference=quality]').select_option('high');p.wait_for_timeout(30);r=p.evaluate('__atlasState()');assert r['bytes']==r['actual'];assert p.evaluate('__townTest.validate().ok');assert p.evaluate('__townTest.save()')==archive;b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-visual-acceptance';out.mkdir(parents=True,exist_ok=True);(out/'atlas.json').write_text(json.dumps({'source_sha256':sha,'lightChanges':rows,'qualityReset':r},indent=2)+'\n');print('PASS12 actual light switches and quality change preserve exact bounded sprite byte accounting')
