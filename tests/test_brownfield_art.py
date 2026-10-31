"""Original static renewal kit follows funded project descriptors without rendering work."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();out=ROOT/'docs/previews/brownfield-art';out.mkdir(parents=True,exist_ok=True)
probe=r'''window.__brownArt={start:()=>{const f=G.firms.find(f=>f.kind==='quarry'&&!f.closed);liquidateFirm(f,'Controlled graphics fixture closure');window.__brownId=f.building;return brownfieldAssess(f.building);},acquire:()=>brownfieldAcquire(__brownId),fund:()=>brownfieldFund(__brownId),ready:()=>{const s=brownfieldSites()[0];for(let i=0;i<100&&s.status!=='ready';i++)__townTest.step(1);return s.status;},reuse:kind=>brownfieldReuse(__brownId,kind),capture:(zoom=1.9,night=false)=>{const s=brownfieldSites()[0],p=iso(s.x,s.y);__townTest.capture({x:p[0],y:p[1],zoom,night});const before=JSON.stringify(G),first=cv.toDataURL();for(let i=0;i<5;i++){dirty=true;draw();}return{status:s.status,unchanged:before===JSON.stringify(G),stable:first===cv.toDataURL(),items:displayItems.filter(a=>a.kind==='brownfield').length,tiles:s.tiles.length,siteCacheBytes:brownfieldArtAtlas.size*72*96*4,atlasBytes};}};'''
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':520});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');p.evaluate("__townTest.reset('regional',42)");assert p.evaluate('__brownArt.start().ok');results=[]
 for stage,action in [('assessed',None),('acquired','__brownArt.acquire().ok'),('remediating','__brownArt.fund().ok'),('ready',"__brownArt.ready()==='ready'")]:
  if action:assert p.evaluate(action),stage
  r=p.evaluate('__brownArt.capture()');assert r['unchanged'] and r['stable'] and r['items']<=r['tiles'] and r['siteCacheBytes']<=884736,r;results.append(r);p.locator('#view').screenshot(path=str(out/(stage+'.png')))
 ready=p.evaluate('__townTest.save()')
 for kind in ['park','home','grocer']:
  assert p.evaluate('s=>__townTest.load(s)',ready);assert p.evaluate('(kind)=>__brownArt.reuse(kind).ok',kind);r=p.evaluate('__brownArt.capture()');assert r['unchanged'] and r['stable'];p.locator('#view').screenshot(path=str(out/(kind+'.png')))
 r=p.evaluate('__brownArt.capture(.2)');assert r['unchanged'] and r['stable'];far_bench=p.evaluate('__townTest.renderBench(100)');p.evaluate('__brownArt.capture(1.9,true)');p.locator('#view').screenshot(path=str(out/'night.png'));bench=p.evaluate('__townTest.renderBench(100)');assert not errors,errors;b.close()
(out/'checks.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'stages':results,'renderBenchMs':bench,'farRenderBenchMs':far_bench,'errors':errors,'fixture':'Controlled quarry closure; actual paid acquisition, ground works and reuse; no grants.'},indent=2)+'\n');print(results,bench)
