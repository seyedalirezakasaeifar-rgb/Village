"""Check mobile layouts and density-independent map composition in Chromium."""
from pathlib import Path
import io, json
from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(ROOT/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
# Include every shipped stylesheet; set_content has no asset base URL.
for sheet in ['vale.css','civic7.css']:
    html=html.replace('<link rel="stylesheet" href="'+sheet+'">','<style>'+(ROOT/'assets'/sheet).read_text()+'</style>')


def run():
    images=[]; results=[]
    out=ROOT/'reports'/json.loads((ROOT/'release.json').read_text())['version'];out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        for width,height,density in [(844,390,1),(844,390,2),(720,360,2),(640,360,2),(568,320,2),(390,844,2),(360,640,2)]:
            page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=density,has_touch=True)
            errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            page.set_content(html);page.add_script_tag(content=(ROOT/'assets/game.js').read_text())
            page.locator('#newTown').click();page.locator('#pause').click()
            page.evaluate("__townTest.reset('settlement',42)")
            page.locator('#panelClose').click()
            page.evaluate('__townTest.capture({zoom:.7})');page.wait_for_timeout(100)
            shot=page.locator('canvas').first.screenshot()
            if width==844: images.append(Image.open(io.BytesIO(shot)).convert('RGB').resize((844,285)))
            page.screenshot(path=str(out/f'town-{width}x{height}-dpr{density}.png'))
            # A hidden root overflow must not conceal the time controls or tabs.
            for selector in ['#pause','#speedRange','#tabs button']:
                for control in page.locator(selector).all():
                    box=control.bounding_box()
                    assert box and box['x']>=0 and box['y']>=0 and box['x']+box['width']<=width+1 and box['y']+box['height']<=height+1,(selector,box,width,height)
                    assert control.evaluate('(e)=>{const r=e.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return e===hit||e.contains(hit)}'),selector
            for panel in page.locator('#tabs button').evaluate_all('(items)=>items.map(b=>b.dataset.panel)'):
                page.locator('[data-panel='+panel+']').click()
                assert page.locator('#panel').is_visible(),panel
                assert 'Panel error' not in page.locator('#panelBody').inner_text()
                page.keyboard.press('Escape')
                assert not page.locator('#panel').is_visible()
            overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
            assert not overflow,(width,height)
            assert not errors,errors
            results.append({'viewport':[width,height],'density':density,'overflow':overflow,'errors':errors})
            page.close()
        browser.close()
    difference=sum(ImageStat.Stat(ImageChops.difference(*images)).mean)/3
    assert difference<18, difference
    result={'layouts':results,'densityMeanPixelDifference':difference}
    (out/'mobile-rendering.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result)

if __name__=='__main__':run()
