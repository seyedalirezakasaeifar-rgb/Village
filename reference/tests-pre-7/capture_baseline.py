"""Controlled comparisons: identical saved world, original 5.6 renderer vs 6.0.
Only a camera/debug hook is injected into 5.6; its renderer and UI are unchanged.
The larger fixture is a town developed by 6.0, not a claimed natural 5.6 result.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os,json
R=Path(__file__).resolve().parents[1];out=R/'reports/final';ref=R/'reference/v5.6/assets'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox'])
 new=b.new_page();new.goto((R/'assets/index.html').as_uri());new.locator('#townSeed').fill('42');new.locator('#newTown').click();new.locator('#pause').click();village=new.evaluate('__townTest.save()');new.close()
 old=b.new_page(viewport={'width':1280,'height':720})
 html=(ref/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(ref/'style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
 old.set_content(html)
 src=(ref/'game.js').read_text();src=src[:-6]+"window.__baselineView=(o)=>{if(o.month)G.month=o.month;if(o.x)cam.x=o.x;if(o.y)cam.y=o.y;if(o.zoom)cam.zoom=o.zoom;overlay='none';staticDirty=true;dirty=true;updateHeader();draw();};\n})();"
 old.add_script_tag(content=src);old.locator('#newTown').click();old.locator('#panelClose').click();old.locator('#pause').click()
 assert old.evaluate('(s)=>__townTest.load(s)',village)
 old.evaluate('__baselineView({month:1,zoom:1.20})');old.wait_for_timeout(300);old.screenshot(path=str(out/'before-village-5.6.png'))
 g=json.loads((out/'regional-endurance-town.json').read_text());assert old.evaluate('(s)=>__townTest.load(s)',json.dumps(g))
 old.evaluate('__baselineView({x:2086,y:1068,month:4,zoom:.70})');old.wait_for_timeout(300);old.screenshot(path=str(out/'before-city-5.6.png'))
 air=next(x for x in g['buildings'] if x['kind']=='airport');cells=g['airport']['runway']+air.get('footprint',[air['y']*56+air['x']]);xs=[(i%56-i//56)*36+2086 for i in cells];ys=[(i%56+i//56)*18+50 for i in cells]
 old.evaluate('(o)=>__baselineView(o)',{'x':(min(xs)+max(xs))/2,'y':(min(ys)+max(ys))/2,'month':4,'zoom':1.3});old.wait_for_timeout(300);old.screenshot(path=str(out/'before-airfield-5.6.png'))
 print('PASS three controlled before scenes using original renderer and identical save geometry',flush=True);b.close()
