"""Simulate unsupported Chrome83 dvh/inset declarations; retain map geometry."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import re,json,hashlib
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
# Chrome83 ignores these declarations. Current Chromium implements them, so
# remove them before parsing styles; do not change JavaScript or map dimensions.
legacy=re.sub(r'height:100dvh;','',html);legacy=re.sub(r'(?<![-\w])inset\s*:[^;}]*;?','',legacy)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);results=[]
 p=b.new_page(viewport={'width':640,'height':360});p.set_content(legacy.replace('height:100vh;','',1));broken=p.locator('#view').bounding_box();assert broken is None or broken['height']==0,broken;p.close()
 for w,h in [(640,360),(844,390),(360,640)]:
  p=b.new_page(viewport={'width':w,'height':h});p.set_content(legacy);p.add_script_tag(content=source.decode());p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.wait_for_timeout(100);r=p.locator('#view').evaluate('(c)=>({width:c.getBoundingClientRect().width,height:c.getBoundingClientRect().height,pixels:c.width*c.height})');assert r['width']==w and r['height']>=150 and r['pixels']>=w*150,r
  p.locator('[data-panel=construction]').click();box=p.locator('#panel').bounding_box();assert box and box['height']>100,box;results.append({'viewport':[w,h],**r});p.close()
 b.close()
out=ROOT/'reports/development-integration';out.mkdir(exist_ok=True);(out/'legacy-layout.json').write_text(json.dumps({'source_sha256':sha,'simulatedUnsupportedCSS':['dvh','inset'],'layouts':results,'nativeCertification':False},indent=2)+'\n');print('PASS visible nonzero map and usable drawer without dvh/inset',results)
