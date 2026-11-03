"""Actual planning/annexation controls at desktop and narrow mobile sizes."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();out=ROOT/'docs/previews/urban8';out.mkdir(parents=True,exist_ok=True)
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w,h in [(1280,800),(390,844),(320,568)]:
  p=b.new_page(viewport={'width':w,'height':h},has_touch=w<500);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto((ROOT/'assets/index.html').as_uri());p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42);__townTest.step(60)");p.locator('[data-panel=construction]').click();p.locator('#urbanPlanningOffice>summary').click();p.screenshot(path=str(out/f'planning-{w}.png'));p.locator('[data-urban-overlay]').click();p.evaluate('__townTest.capture()');p.screenshot(path=str(out/f'neighbourhoods-{w}.png'));p.locator('[data-panel=construction]').click();p.locator('#charterOffice>summary').click();p.locator('[data-charter-overview]').click();p.evaluate('__townTest.capture()');p.screenshot(path=str(out/f'region-{w}.png'));p.locator('#surveyDistrict').select_option('belt-102-102');p.locator('#surveyReview').click();assert p.locator('[data-parcel-card=belt-102-102]').is_visible();assert p.locator('[data-parcel-buy=belt-102-102]').is_disabled();overflow=p.evaluate('document.documentElement.scrollWidth>innerWidth');assert not overflow and not errors,(overflow,errors);rows.append({'viewport':[w,h],'planningControls':True,'neighbourhoodMap':True,'fullAtlasSurvey':True,'farParcelReviewed':True,'detachedPurchaseDisabled':True,'horizontalOverflow':overflow,'errors':errors});p.close()
 b.close()
(out/'viewports.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'viewports':rows},indent=2)+'\n');print(json.dumps(rows,indent=2))
