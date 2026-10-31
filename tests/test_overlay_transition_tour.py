import ast, json, hashlib, base64, gc, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html
root=ROOT
source=(root/'assets/game.js').read_text(); sha=hashlib.sha256(source.encode()).hexdigest()
large=next(n.value for n in ast.walk(ast.parse((root/'tests/test_v7_live_large_town.py').read_text())) if isinstance(n,ast.Constant) and isinstance(n.value,str) and 'while(g.people.length<2000' in n.value)
probe=r'''window.__tour={
 prepare:()=>{document.getElementById('welcome').style.display='none';gameOptions.reducedMotion=true;gameOptions.quality='low';applyPresentationOptions();},
 targets:()=>{const byKind=k=>displayItems.find(a=>a.kind===k||a.b?.kind===k);const list=[byKind('home'),byKind('factory'),byKind('wharf'),byKind('elevated_station'),byKind('brownfield'),byKind('retailCentre'),byKind('market_square'),byKind('school'),byKind('tower')].filter(Boolean);return list.map(a=>({x:a.x,y:a.y,kind:a.kind==='building'?a.b?.kind:a.kind}));},
 reset:()=>{const before=cv.toDataURL(),state=JSON.stringify(G),rng=rngState;viewRasterKey='';viewBackgroundKey='';nightEmissionKey='';atlas.clear();atlasBytes=0;staticDirty=true;dirty=true;draw();return{pixelMatch:before===cv.toDataURL(),stateMatch:state===JSON.stringify(G),rngMatch:rng===rngState};},
 stats:()=>({overlay,night:nightMode,zoom:cam.zoom,quality:gameOptions.quality,reducedMotion:gameOptions.reducedMotion,
 key:$('mapStatusOverlayKey').textContent,keyNodes:$('mapStatusToggle').querySelectorAll('#mapStatusOverlayKey').length,
 dom:document.getElementsByTagName('*').length,atlasBytes,atlasEntries:atlas.size,brownfieldBytes:brownfieldArtAtlas.size*72*96*4,
 nightEmissionBytes:nightEmissionCanvas.width*nightEmissionCanvas.height*4,nightEmissionKeyLength:nightEmissionKey.length,
 viewRasterBytes:viewRaster.width*viewRaster.height*4,underlayBytes:viewUnderlayRaster.width*viewUnderlayRaster.height*4,
 repairBytes:actorRepairRaster.width*actorRepairRaster.height*4,heap:performance.memory?.usedJSHeapSize||0,
 trafficActors:transitArtActors(()=>true).length,drawCalls:__tourDraws}),
 render:(mode,z,night,quality,reduced,x,y)=>{gameOptions.quality=quality;gameOptions.reducedMotion=reduced;applyPresentationOptions();overlay=mode;__townTest.capture({x,y,zoom:z,night});updateMapOverlayKey();dirty=true;draw();const a=cv.toDataURL(),before=JSON.stringify(G),rng=rngState;dirty=true;draw();const paused=a===cv.toDataURL()&&before===JSON.stringify(G)&&rng===rngState;return{paused,key:$('mapStatusOverlayKey').textContent,pixels:a};}
};window.__tourDraws=0;const __tourDraw=draw;draw=function(){__tourDraws++;return __tourDraw.apply(this,arguments)};'''
error=[];rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--js-flags=--expose-gc'])
 p=b.new_page(viewport={'width':844,'height':390},device_scale_factor=1);p.on('pageerror',lambda e:error.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',(root/'tools/qa_live_network.js').read_text()+'\n'+large+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'))
 p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');p.evaluate(large);p.evaluate('window.__liveNetworkBuild()');p.evaluate('__townTest.step(5)');cdp=p.context.new_cdp_session(p);
 p.evaluate('window.__tour.prepare()')
 # Make fixture locations cover public realm, waterfront, rail and a dense street.
 targets=p.evaluate('window.__tour.targets()')
 if len(targets)<4: raise AssertionError(('fixture lacks representative sites',targets))
 modes=['roads','business','hardship','crime','land','transit','metro','healthAccess','schoolAccess','neighbourhoods','charter','none']
 keys=['ROAD','BUSINESS','STRESS','THEFT','LAND VALUE','TRANSIT','UNDERGROUND','MEDICAL REACH','SCHOOL REACH','DISTRICTS','LAND','']
 layouts=[(844,390,1),(568,320,1),(390,844,2),(360,640,1)]
 p.evaluate('if(window.gc)gc()');heap0=p.evaluate('performance.memory?.usedJSHeapSize||0')
 for i in range(96):
  cycle=i//12;step=i%12;mode=modes[step];target=targets[(cycle+step)%len(targets)]
  width,height,dpr=layouts[(cycle+step//4)%len(layouts)]
  cdp.send('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':dpr,'mobile':False});p.wait_for_timeout(16);observed=p.evaluate('({w:innerWidth,h:innerHeight,dpr:devicePixelRatio})');assert observed=={'w':width,'h':height,'dpr':dpr},(observed,width,height,dpr)
  z=[1.25,.65,.32,.22][(cycle+step//3)%4];night=(cycle+step)%2==1;quality='low' if cycle%2 else 'high';reduced=cycle%3==0
  r=p.evaluate('([m,z,n,q,rm,x,y])=>__tour.render(m,z,n,q,rm,x,y)',[mode,z,night,quality,reduced,target['x'],target['y']])
  if not r['paused']: raise AssertionError(('paused pixel/state instability',i,mode,target))
  if not r['key'].startswith(keys[step]): raise AssertionError(('stale legend',i,mode,r['key']))
  s=p.evaluate('__tour.stats()');s.update({'i':i,'mode':mode,'site':target['kind'],'viewport':[width,height,dpr],'observed_viewport':observed,'night':night})
  if s['keyNodes']!=1: raise AssertionError(('overlay legend DOM duplication',s))
  if s['atlasBytes']>48*1024*1024 or s['brownfieldBytes']>884736 or s['repairBytes']>(width*height*dpr*dpr*8): raise AssertionError(('cache envelope',s))
  rows.append(s)
  # Preserve source pixels + interface for six deliberately varied transition states.
  if i in (0,1,5,6,7,9,10,11,24,39,64,95):
   out=root/'docs/previews/overlay-tour-8';out.mkdir(parents=True,exist_ok=True)
   name=f'{width}x{height}-{mode}-'+('night' if night else 'day')+f'-{i}'
   (out/(name+'.png')).write_bytes(base64.b64decode(r['pixels'].split(',')[1]))
 # Force a full cache reset and verify same pixels/state on current paused view.
 cold=p.evaluate('window.__tour.reset()')
 final=p.evaluate('__tour.stats()');final['heapAfterGc']=p.evaluate('if(window.gc)gc();performance.memory?.usedJSHeapSize||0')
 out=root/'docs/previews/overlay-tour-8';out.mkdir(parents=True,exist_ok=True)
 data={'cold_cache_reset':cold,'source_sha256':sha,'steps':len(rows),'cycles':8,'overlays':modes,'layout_rotation':layouts,'start_heap_after_gc':heap0,'end_state':final,'min_heap':min((x['heap'] for x in rows),default=0),'max_heap':max((x['heap'] for x in rows),default=0),'max_dom_nodes':max(x['dom'] for x in rows),'min_dom_nodes':min(x['dom'] for x in rows),'max_atlas_bytes':max(x['atlasBytes'] for x in rows),'max_night_emission_bytes':max(x['nightEmissionBytes'] for x in rows),'errors':error,'states':rows}
 (out/'tour.json').write_text(json.dumps(data,indent=2)+'\n')
 assert not error,error
 assert cold['pixelMatch'] and cold['stateMatch'] and cold['rngMatch'],cold
 assert all(x['keyNodes']==1 for x in rows)
 # DOM variation from responsive UI is allowed but must not accumulate across cycles.
 first=max(x['dom'] for x in rows[:12]);last=max(x['dom'] for x in rows[-12:]);assert last<=first+20,(first,last)
 assert final['heapAfterGc']<=heap0+40*1024*1024,(heap0,final['heapAfterGc'])
 print(json.dumps({'source':sha,'steps':len(rows),'keynodes':sorted(set(x['keyNodes'] for x in rows)),'DOM_minmax':[min(x['dom'] for x in rows),max(x['dom'] for x in rows)],'heap_start_end':[heap0,final['heapAfterGc']],'atlas_peak':max(x['atlasBytes'] for x in rows),'night_cache_peak':max(x['nightEmissionBytes'] for x in rows),'errors':error}))
 p.close();b.close()
