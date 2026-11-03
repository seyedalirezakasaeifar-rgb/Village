"""Exact pixel/emission equivalence for shared house geometry cache signatures."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();out=ROOT/'docs/previews/visual-acceptance';out.mkdir(parents=True,exist_ok=True)
probe=r'''window.__houseAtlasCheck=()=>{
 const before=JSON.stringify(G),oldNight=nightMode,shared=spriteFor,unshared=eval('('+spriteFor.toString().replace(/const cacheVariant=[^;]+;/,'const cacheVariant=variant;')+')'),images=[];let cases=0;
 const specimen=id=>({kind:'building',id,b:{kind:'home',id,x:22,y:22,hh:0,firm:-1,condition:100},x:0,y:0,w:1,d:1});
 let oldBytes=0,newBytes=0;
 for(const night of [false,true])for(const condition of [100,65,30]){
  nightMode=night;clearAtlas();const expected=[];for(let id=0;id<120;id++){const item=specimen(id);item.b.condition=condition;const c=unshared(item);expected.push([c.toDataURL(),JSON.stringify(c.lightSources)]);}oldBytes=Math.max(oldBytes,atlasBytes);
  clearAtlas();for(let id=0;id<120;id++){const item=specimen(id);item.b.condition=condition;const c=shared(item);if(c.toDataURL()!==expected[id][0]||JSON.stringify(c.lightSources)!==expected[id][1])throw Error('House pixels differ '+[id,condition,night]);cases++;}newBytes=Math.max(newBytes,atlasBytes);
 }
 nightMode=oldNight;clearAtlas();staticDirty=true;dirty=true;draw();return{cases,oldBytes,newBytes,savedFraction:1-newBytes/oldBytes,unchanged:before===JSON.stringify(G)};
};'''
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__houseAtlasCheck()');assert r['cases']==720 and r['unchanged'] and r['savedFraction']>.5,r;b.close()
r['source_sha256']=hashlib.sha256(source.encode()).hexdigest();(out/'house-cache-equivalence.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
