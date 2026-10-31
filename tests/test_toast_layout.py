"""Transient feedback fits the map and never takes its centre or touch events."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_bytes();script=source.decode().replace('// SOURCE: 99-instrumentation.js',"window.__toastProbe=()=>toast('Policy package enacted. Let time pass to observe the effects.');\n// SOURCE: 99-instrumentation.js");rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w,h in [(844,390),(640,360),(568,320),(360,640)]:
  p=b.new_page(viewport={'width':w,'height':h});p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.evaluate('__toastProbe()');r=p.locator('#toast').bounding_box();c=p.locator('#view').bounding_box();assert r and c and r['x']>=0 and r['x']+r['width']<=w and r['y']>=c['y'] and r['y']+r['height']<=c['y']+c['height'],(r,c);centre=(c['x']+c['width']/2,c['y']+c['height']/2);assert not (r['x']<=centre[0]<=r['x']+r['width'] and r['y']<=centre[1]<=r['y']+r['height']),r;assert p.locator('#toast').evaluate("e=>getComputedStyle(e).pointerEvents")=='none';rows.append({'viewport':[w,h],'toast':r,'map':c});p.close()
 b.close()
out=ROOT/'reports/development-visual-acceptance';out.mkdir(parents=True,exist_ok=True);(out/'toast.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source).hexdigest(),'css_sha256':hashlib.sha256((ROOT/'assets/civic7.css').read_bytes()).hexdigest(),'layouts':rows},indent=2)+'\n');print('PASS map-contained, centre-free, nonblocking feedback in four mobile layouts')
