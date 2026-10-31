"""Numbered land survey, accessible review and contextual shore placement."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
script=source.decode().replace('// SOURCE: 99-instrumentation.js',r'''
window.__surveyProbe=()=>({focus:parcelFocus,labels:charterLabelLayout().map(a=>({id:a.p.id,text:a.text,compact:a.compact,box:a.box,x:a.x,y:a.y})),camera:{...cam}});
window.__inlandSite=()=>{for(let y=21;y<33;y++)for(let x=20;x<35;x++)if(canPlace(x,y,true,'home')){const q=iso(x,y),sx=cw/2+(q[0]-cam.x)*cam.zoom,sy=ch/2+(q[1]+18-cam.y)*cam.zoom;if(sx<80||sx>cw-80||sy<70||sy>ch-30)continue;return{x,y,world:iso(x,y),reason:waterfrontPlacementMessage(x,y,'fishery')};}};
window.__waterClickProbe=()=>{overlay='none';centerTownCamera();cam.zoom=1;const actors=waterfrontActors(()=>true),a=actors.find(a=>a.cargo!=='fish');if(!a)return null;cam.x=a.x;cam.y=a.y;dirty=true;draw();return {id:a.f.building,x:cw/2,y:ch/2};};
// SOURCE: 99-instrumentation.js''')
results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width,height in [(844,390),(568,320),(320,568)]:
  p=b.new_page(viewport={'width':width,'height':height});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("settlement",42)');p.locator('[data-panel=construction]').click();p.locator('#charterOffice>summary').click();p.locator('[data-charter-overview]').click();p.evaluate('__townTest.capture()');r=p.evaluate('__surveyProbe()');assert len(r['labels'])==5 and all(a['compact'] for a in r['labels']),r
  boxes=[a['box'] for a in r['labels']];canvas=p.locator('#view').bounding_box();hud=p.locator('#regionSurvey').bounding_box()
  for a in r['labels']:
   assert 0<=a['box']['x'] and a['box']['x']+a['box']['w']<=canvas['width'] and 0<=a['box']['y'] and a['box']['y']+a['box']['h']<=canvas['height'],(width,height,r)
   assert not(hud['x']<=canvas['x']+a['x']<=hud['x']+hud['width'] and hud['y']<=canvas['y']+a['y']<=hud['y']+hud['height']),(width,height,a,hud)
  for i,a in enumerate(boxes):
   for c in boxes[i+1:]:assert not(a['x']<c['x']+c['w'] and a['x']+a['w']>c['x'] and a['y']<c['y']+c['h'] and a['y']+a['h']>c['y']),r
  assert p.locator('#regionSurvey').is_visible() and p.locator('#surveyDistrict').bounding_box()['height']>=44 and p.locator('#surveyReview').bounding_box()['height']>=44
  for district in ['river-reach','orchard-downs','county-ridge','high-common','east-meadow']:
   p.locator('#surveyDistrict').select_option(district);p.evaluate('__townTest.capture()');assert p.evaluate('__surveyProbe().focus')==district
  p.locator('#surveyReview').click();assert p.locator('[data-parcel-card=east-meadow]').is_visible();p.locator('#panelClose').click();p.keyboard.press('Escape');p.evaluate('__townTest.capture()');assert p.locator('#regionSurvey').is_hidden();assert not errors,errors
  results.append({'viewport':[width,height],'numberedPins':5,'districtsReviewed':5,'overlap':False});p.close()
 p=b.new_page(viewport={'width':844,'height':390});p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("settlement",42)');p.locator('[data-panel=construction]').click();p.locator('[data-build-category=waterfront]').click();p.locator('[data-build=fishery]').click();site=p.evaluate('__inlandSite()');cam=p.evaluate('__townTest.view().camera');box=p.locator('#view').bounding_box();sx=box['x']+box['width']/2+(site['world'][0]-cam['x'])*cam['zoom'];sy=box['y']+box['height']/2+(site['world'][1]+18-cam['y'])*cam['zoom'];p.mouse.move(sx,sy);p.evaluate('__townTest.capture()');assert 'connected water' in p.locator('#placementHint').inner_text();before=p.evaluate('__townTest.get().treasury');p.mouse.click(sx,sy);assert p.evaluate('__townTest.get().treasury')==before and 'connected water' in p.locator('#toast').inner_text();assert p.evaluate('__townArchive.back()');assert p.locator('#placementHint').is_hidden();p.evaluate('__townTest.step(5)');boat=p.evaluate('__waterClickProbe()');assert boat;box=p.locator('#view').bounding_box();p.mouse.click(box['x']+boat['x'],box['y']+boat['y']);assert 'PAID REGIONAL CARGO VOYAGE' in p.locator('#panelBody').inner_text(),p.locator('#panelBody').inner_text();b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-survey-play';out.mkdir(exist_ok=True);(out/'survey.json').write_text(json.dumps({'source_sha256':sha,'viewports':results,'shoreFeedbackAndBoatInspection':True},indent=2)+'\n');print('PASS nonoverlapping numbered region survey, 44px selection/review, all five previews, return to town, real inland hover/tap rejection and boat inspection')
