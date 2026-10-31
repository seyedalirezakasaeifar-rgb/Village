from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
out=ROOT/'reports/development-local-services';out.mkdir(parents=True,exist_ok=True);source=(ROOT/'assets/game.js').read_bytes()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390},device_scale_factor=2);p.set_content(html);p.add_script_tag(content=source.decode());p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('regional',42);__townTest.step(180)");p.wait_for_timeout(3400);p.locator('[data-panel=community]').click();p.screenshot(path=str(out/'services-landscape.png'));p.locator('[data-service-access=health]').click();p.screenshot(path=str(out/'medical-access-landscape.png'));p.locator('[data-panel=community]').click();p.locator('[data-service-policy=health]').click();p.screenshot(path=str(out/'medical-policy-landscape.png'));b.close()
(out/'captures.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source).hexdigest(),'scenario':'regional','seed':42,'day':181,'viewport':[844,390],'density':2},indent=2)+'\n')
