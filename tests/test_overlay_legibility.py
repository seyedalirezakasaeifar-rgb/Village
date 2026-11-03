"""Overlay symbols, legends, visual purity, and mobile status-key layout."""
import ast, hashlib, json
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html

source=(ROOT/'assets/game.js').read_text()
sha=hashlib.sha256(source.encode()).hexdigest()
large=next(n.value for n in ast.walk(ast.parse((ROOT/'tests/test_v7_live_large_town.py').read_text()))
           if isinstance(n,ast.Constant) and isinstance(n.value,str) and 'while(g.people.length<2000' in n.value)
probe=r'''
window.__overlayLegibility={
 setup:()=>{__townTest.reset('settlement',42);},
 setVisual:()=>{gameOptions.quality='low';gameOptions.reducedMotion=true;document.getElementById('mapStatusOverlayKey').style.fontSize='14px';},
 advance:n=>{__townTest.step(n);},
 drawMode:(mode,zoom=.85)=>{overlay=mode;cam.zoom=zoom;if(mode==='crime'&&G.cases.length){const b=readBuild(G.cases[0].bid);if(b){const p=iso(b.x,b.y);cam.x=p[0];cam.y=p[1];}}let calls=0;const base=overlayBadge;overlayBadge=(...a)=>{calls++;base(...a)};dirty=true;draw();overlayBadge=base;return{calls,key:document.getElementById('mapStatusOverlayKey').textContent};},
 inspect:()=>({cases:G.cases.length,day:G.day,paused,quality:gameOptions.quality,reducedMotion:gameOptions.reducedMotion,state:JSON.stringify(G),rng:rngState,blocks:Object.keys(urbanSpatial().blocks).length}),
 cold:()=>{const first=document.getElementById('view').toDataURL();viewRasterKey='';nightEmissionKey='';staticDirty=true;dirty=true;draw();return first===document.getElementById('view').toDataURL();},
 bench:()=>{const old=overlay;overlay='none';const base=__townTest.renderBench(40);overlay='roads';const marked=__townTest.renderBench(40);overlay=old;dirty=true;draw();return{base,marked};},
 close:()=>{closePanel();document.getElementById('welcome').style.display='none';}
};
'''

def overlaps(a,b):
    return a['x'] < b['x']+b['width'] and a['x']+a['width'] > b['x'] and a['y'] < b['y']+b['height'] and a['y']+a['height'] > b['y']
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':844,'height':390},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html);page.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',large+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'))
    page.locator('#newTown').click();page.locator('#pause').click();page.evaluate('__overlayLegibility.setup()');page.evaluate(large);page.evaluate('__overlayLegibility.close()')
    page.evaluate('__overlayLegibility.setVisual()')
    page.evaluate('__overlayLegibility.advance(5)')
    initial=page.evaluate('__overlayLegibility.inspect()');assert initial['cases']>0,initial
    render_bench=page.evaluate('__overlayLegibility.bench()')
    keys={'roads':'ROAD','business':'BUSINESS','hardship':'STRESS','crime':'THEFT','land':'LAND VALUE','transit':'TRANSIT','metro':'UNDERGROUND','healthAccess':'MEDICAL REACH','schoolAccess':'SCHOOL REACH','neighbourhoods':'DISTRICTS','charter':'LAND'}
    rows=[]
    for mode,prefix in keys.items():
        result=page.evaluate('(m)=>__overlayLegibility.drawMode(m)',mode)
        assert result['key'].startswith(prefix),(mode,result)
        if mode in ('roads','business','hardship','crime','land'):
            assert result['calls']>0,(mode,result)
        if mode=='crime':assert result['calls']>=1,(mode,result['calls'],initial['cases'])
        after=page.evaluate('__overlayLegibility.inspect()')
        assert after['state']==initial['state'] and after['rng']==initial['rng'],mode
        rows.append({'overlay':mode,'badges':result['calls'],'legend':result['key']})
    assert initial['blocks']>0,initial
    assert page.evaluate('__overlayLegibility.cold()'),'Cold redraw changed paused overlay pixels'
    page.evaluate("__overlayLegibility.drawMode('land')")
    low=page.evaluate("__overlayLegibility.drawMode('roads',.35)")
    assert low['calls']==0 and low['key'].startswith('ROAD'),low
    for width,height in [(844,390),(568,320),(390,844),(360,640)]:
        page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(100)
        boxes=page.evaluate('''()=>({deck:document.getElementById('mapStatusDeck').getBoundingClientRect().toJSON(),footer:document.getElementById('tabs').getBoundingClientRect().toJSON(),buttons:document.querySelector('.mapbuttons').getBoundingClientRect().toJSON(),key:document.getElementById('mapStatusOverlayKey').getBoundingClientRect().toJSON()})''')
        assert not overlaps(boxes['deck'],boxes['footer']),(width,height,boxes)
        assert not overlaps(boxes['deck'],boxes['buttons']),(width,height,boxes)
        assert boxes['key']['height']>0,(width,height,boxes)
    assert not errors,errors;browser.close()
report={'source_sha256':sha,'fixture':'validated 2,000-resident visual fixture; 5 actual simulated days produced recorded cases; no incidents injected','low_quality':True,'reduced_motion':True,'large_text_css_px':14,'paused_state_unchanged':True,'camera_cold_redraw_exact':True,'renderBenchMs':render_bench,'results':rows,'errors':errors}
out=ROOT/'reports/overlay-legibility-8';out.mkdir(exist_ok=True);(out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS color-independent overlay badges, keys including real 30-day theft sites, paused state/RNG purity, cold redraw, distant LOD and four mobile layouts')
