"""New land/water controls stay reachable at small phone sizes."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
sha=hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest();results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width,height in [(320,568),(568,320),(844,390)]:
  p=b.new_page(viewport={'width':width,'height':height},has_touch=True,is_mobile=True);p.set_content(html);p.add_script_tag(content=(ROOT/'assets/game.js').read_text());p.locator('#newTown').click();p.locator('#pause').click();p.locator('[data-panel=construction]').click();summary=p.locator('#charterOffice>summary');summary.scroll_into_view_if_needed();box=summary.bounding_box();assert box['height']>=44,(width,height,'land summary',box);summary.click()
  controls=p.locator('#charterOffice button:not([disabled])');counts=controls.count()
  for i in range(counts):
   item=controls.nth(i);item.scroll_into_view_if_needed();rect=item.bounding_box();assert rect['height']>=44 and rect['width']>=44,(width,height,item.inner_text(),rect);assert rect['x']>=0 and rect['x']+rect['width']<=width+.5,(width,height,rect)
  p.locator('[data-parcel-buy=east-meadow]').click();assert p.locator('#eventDialog').is_visible();p.locator('#eventDefer').scroll_into_view_if_needed();p.locator('#eventDefer').click();assert p.locator('#eventDialog').is_hidden()
  water=p.locator('summary',has_text='Working waterfront');water.scroll_into_view_if_needed();assert water.bounding_box()['height']>=44;water.click();p.locator('[data-waterfront-build]').click();assert p.locator('[data-build=wharf]').is_visible() and p.locator('[data-build=fishery]').is_visible();results.append({'viewport':[width,height],'landControls':counts,'confirmationCancel':True,'waterfrontCategory':True});p.close()
 b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-working-river';out.mkdir(exist_ok=True);(out/'mobile-expansion.json').write_text(json.dumps({'source_sha256':sha,'results':results},indent=2)+'\n');print('PASS 44px reachable land/water controls, purchase cancel and building categories at 320x568, 568x320 and 844x390')
