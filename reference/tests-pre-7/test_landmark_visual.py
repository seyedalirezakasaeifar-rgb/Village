from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
s=(root/'assets/game.js').read_text();s=s[:-6]+'''window.__visualTest={focus:(kind)=>{const b=G.buildings.find(b=>b.kind===kind&&footprintOf(b).length>1);if(!b)return false;const p=iso(b.x,b.y);cam.x=p[0];cam.y=p[1];cam.zoom=1.0;dirty=true;staticDirty=true;draw();return {x:b.x,y:b.y,id:b.id};},cleanup:()=>{closePanel();dirty=true;draw()}};
})();'''
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1280,'height':720});errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
 html=(root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','');page.set_content(html);page.add_script_tag(content=s);page.locator('#newTown').click();page.evaluate('__visualTest.cleanup()');print(page.evaluate("__visualTest.focus('farm')"));page.screenshot(path=str(root/'reports/farm-visual.png'))
 assert not errs,errs
 b.close()
