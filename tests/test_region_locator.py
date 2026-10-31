"""Actual mobile locator controls, snapshot reuse, state independence and budget."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_text();out=ROOT/'docs/previews/region-locator';out.mkdir(parents=True,exist_ok=True)
probe=r'''window.__locatorProbe=()=>{const before=JSON.stringify(G),builds=regionLocatorBuilds;const start=performance.now();for(let i=0;i<200;i++)updateRegionLocator();return {unchanged:before===JSON.stringify(G),cacheBuilds:regionLocatorBuilds-builds,meanMs:(performance.now()-start)/200,bytes:regionLocatorBase.width*regionLocatorBase.height*8,marks:regionLocatorMarks.length};};window.__locatorState=()=>({x:cam.x,y:cam.y,zoom:cam.zoom,rw:RW,rh:RH});'''
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');p.evaluate("__townTest.reset('settlement',42)");p.locator('#regionLocatorToggle').click();assert p.locator('#regionLocatorToggle').get_attribute('aria-expanded')=='true';c=p.locator('#regionLocator canvas');box=c.bounding_box();assert box['x']>=0 and box['y']>=0 and box['x']+box['width']<=844 and box['y']+box['height']<=390
 before=p.evaluate('__townTest.save()');old=p.evaluate('__locatorState()');c.click(position={'x':box['width']*.7,'y':box['height']*.4});now=p.evaluate('__locatorState()');assert abs(now['x']/now['rw']-.7)<.01 and abs(now['y']/now['rh']-.4)<.01 and now['zoom']==old['zoom'];c.focus();p.keyboard.press('ArrowLeft');assert p.evaluate('__locatorState().x')<now['x'];assert p.evaluate('__townTest.save()')==before
 results=[]
 for zoom in [1.1,.2]:
  p.evaluate('(zoom)=>__townTest.capture({zoom})',zoom);r=p.evaluate('__locatorProbe()');assert r['unchanged'] and r['cacheBuilds']==0 and r['bytes']==652288,r;results.append({'zoom':zoom,**r});p.locator('#view').screenshot(path=str(out/('far.png' if zoom<.3 else 'near.png')))
 p.screenshot(path=str(out/'mobile-controls.png'));p.keyboard.press('Escape');assert p.locator('#regionLocator').is_hidden();assert not errors,errors;b.close()
(out/'checks.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'results':results,'errors':errors},indent=2)+'\n');print(results)
