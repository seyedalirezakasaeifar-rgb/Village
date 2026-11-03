"""Fixed seeded phone compositions for UI hierarchy comparisons."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
label=sys.argv[1] if len(sys.argv)>1 else 'after';assert label in ['before','after'];out=ROOT/'docs/previews/map-hierarchy';out.mkdir(parents=True,exist_ok=True);source=(ROOT/'assets/game.js').read_bytes();rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width,height in [(640,360),(720,360),(844,390),(360,640)]:
  p=b.new_page(viewport={'width':width,'height':height},device_scale_factor=2,has_touch=True);p.set_content(html);p.add_script_tag(content=source.decode());p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("settlement",42);__townTest.step(30)');p.locator('#panelClose').click();p.evaluate('__townTest.capture({zoom:.7});document.querySelector("#gameRoot").classList.add("map-used")');p.wait_for_timeout(3500);p.screenshot(path=str(out/f'{label}-{width}x{height}.png'));rows.append({'viewport':[width,height],'day':31,'seed':42});p.close()
 b.close()
(out/(label+'-provenance.json')).write_text(json.dumps({'source_sha256':hashlib.sha256(source).hexdigest(),'asset_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'assets').glob('*') if p.is_file()},'runtime':'Chromium host; not Android','density':2,'rows':rows},indent=2)+'\n')
