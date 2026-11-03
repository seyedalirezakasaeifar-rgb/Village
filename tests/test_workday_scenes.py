"""Operating activity, viewport budgets, accessibility and render independence."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js','''
window.__workdayProbe=()=>{const options={...gameOptions},oldZoom=cam.zoom,oldPause=paused,oldSpeed=speed;try{
 gameOptions.effects=true;gameOptions.decor=true;gameOptions.reducedMotion=false;gameOptions.quality='high';cam.zoom=1;paused=true;dirty=true;draw();const observer=new MutationObserver(()=>{});observer.observe($('pause'),{attributes:true,childList:true,subtree:true});for(let i=0;i<20;i++)updateHeader();const headerMutations=observer.takeRecords().length;observer.disconnect();const all=workdayScenes(displayItems),types=all.map(a=>a.scene),cap=all.length;
 const first=all.find(a=>a.f);let noClosed=true;if(first){const was=first.f.closed;first.f.closed=true;noClosed=!workdayScenes([all.find(a=>a.f===first.f)]).some(a=>a.f===first.f);first.f.closed=was;}
 gameOptions.quality='balanced';paused=false;speed=64;const fast=workdayScenes(displayItems).length;gameOptions.reducedMotion=true;const reduced=workdayScenes(displayItems).length;gameOptions.reducedMotion=false;gameOptions.effects=false;const disabled=workdayScenes(displayItems).length;
 return {types,cap,fast,reduced,disabled,noClosed,headerMutations};
 }finally{Object.assign(gameOptions,options);cam.zoom=oldZoom;paused=oldPause;speed=oldSpeed;dirty=true;}};
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.step(5)');before=p.evaluate('__townTest.get().total');r=p.evaluate('__workdayProbe()');assert r['types'] and r['cap']<=12 and r['fast']<=3 and r['reduced']==r['disabled']==0 and r['noClosed'] and r['headerMutations']==0,r;assert p.evaluate('__townTest.get().total')==before;assert not errors,errors;b.close();print('PASS productive/funded workday scenes, closure, quality budgets, reduced motion and cash independence',r)
