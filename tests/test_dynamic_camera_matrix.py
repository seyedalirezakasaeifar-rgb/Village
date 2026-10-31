"""Seeded cache/camera matrix. Independent full-scene actor oracle, finite host acceptance."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,json,hashlib,os
source=(ROOT/'assets/game.js').read_text();out=ROOT/'docs/previews/camera-matrix';out.mkdir(parents=True,exist_ok=True)
large=next(ast.literal_eval(n.args[0]) for n in ast.walk(ast.parse((ROOT/'tests/test_v7_live_large_town.py').read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='evaluate' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str) and 'while(g.people.length<2000' in n.args[0].value)
probe=r'''window.__matrixStates=()=>{const closed=G.firms.find(f=>f.kind==='factory'&&!f.closed);if(closed)liquidateFirm(closed,'Controlled visual closure fixture');const quarry=G.firms.find(f=>f.kind==='quarry'&&!f.closed);let site=null;if(quarry){liquidateFirm(quarry,'Controlled visual renewal fixture');const id=quarry.building,a=brownfieldAssess(id),b=a.ok&&brownfieldAcquire(id),c=b?.ok&&brownfieldFund(id);site={assessed:a.ok,acquired:!!b?.ok,funded:!!c?.ok};}const redevelopment=urbanRedevelopment({...cityDemand(),residents:2000,confidence:60,hardship:20,homeDemand:30,housingPressure:65});staticDirty=true;dirty=true;draw();return {closed:closed?.building,site,redevelopment};};window.__matrixMotion=(night)=>{gameOptions.reducedMotion=false;gameOptions.quality='high';applyPresentationOptions();fit();cam.zoom=1.2;const a=transitArtActors(()=>true).find(a=>a.mode==='bus');if(!a)return false;__townTest.capture({x:a.x,y:a.y,zoom:1.2,night});return true;};window.__paletteMatrix=()=>ANNEX_PARCELS.every(p=>{const m=neighbourhoodMaterial({x:p.x+1,y:p.y+1});return Array.isArray(m)&&m.length===2;});window.__cameraMatrix=(index)=>{
 const focus=displayItems.filter(a=>a.kind==='brownfield'||a.b&&['home','tower','factory','wharf','elevated_station','transit_depot','brownfield'].includes(a.b.kind)),preferred=[displayItems.find(a=>a.kind==='brownfield'),displayItems.find(a=>a.b?.redevelopment),displayItems.find(a=>a.b?.kind==='tower'),displayItems.find(a=>a.kind==='guideway'),displayItems.find(a=>a.b?.kind==='elevated_station'),displayItems.find(a=>a.b?.kind==='wharf')],item=(index<6&&preferred[index])||focus[(index*137+17)%focus.length]||displayItems[0],zooms=[1.6,.4,.2,.65,1.15,.32],zoom=zooms[index%zooms.length];
 gameOptions.quality=index%4===0?'low':'high';gameOptions.reducedMotion=index%5===0;applyPresentationOptions();fit();__townTest.capture({x:item.x+((index*41)%103)-50.3,y:item.y+((index*17)%71)-35.7,zoom,night:!!(index%2)});
 const state=JSON.stringify(G),first=cv.toDataURL();dirty=true;draw();const pausedStable=first===cv.toDataURL();
 // A complete cache invalidation must reconstruct the same committed scene.
 viewRasterKey='';viewBackgroundKey='';nightEmissionKey='';atlas.clear();atlasBytes=0;staticDirty=true;dirty=true;draw();const coldStable=first===cv.toDataURL();
 let oracle={channels:0,max:0,actors:0};
 if(viewUnderlayRaster.width){const actors=transitArtActors(()=>true).filter(a=>Math.abs(a.x-cam.x)<cw/cam.zoom/2+30&&Math.abs(a.y-cam.y)<ch/cam.zoom/2+30);if(visualDetailBudget().traffic)actors.push({kind:'vehicle',v:{id:12345,style:'truck',color:'#b99d61'},x:item.x+35,y:item.y-1,dx:1,dy:.5});
  if(actors.length){const make=()=>{const c=document.createElement('canvas');c.width=cv.width;c.height=cv.height;const g=c.getContext('2d');g.imageSmoothingEnabled=false;return{c,g};},ref=make(),got=make(),ground=g=>{drawWaterLife(g,()=>true);drawWaterfrontPiers(g,()=>true);drawRegionalGates(g,()=>true);drawTransitInfrastructure(g,()=>true);};
   ref.g.drawImage(viewUnderlayRaster,0,0);mapPaintTransform(ref.g);ground(ref.g);const decks=viewBuildings.filter(a=>a.kind==='guideway').map(item=>({item,bounds:scenePaintBounds(item)})),layers=viewBuildings.map(a=>({a,y:a.y})).concat(actors.map(a=>({a,y:sceneActorPaintY(a,decks)}))).sort((a,b)=>a.y-b.y);for(const v of layers)paintSceneLayer(ref.g,v.a);
   got.g.drawImage(viewRaster,0,0);mapPaintTransform(got.g);ground(got.g);paintSceneActors(got.g,actors,()=>true);
   const expected=ref.g.getImageData(0,0,cv.width,cv.height).data,actual=got.g.getImageData(0,0,cv.width,cv.height).data;for(const a of actors){const r=scenePaintBounds(a),x=Math.max(0,Math.floor(((r[0]-cam.x)*zoom+cw/2)*dpr)),y=Math.max(0,Math.floor(((r[1]-cam.y)*zoom+ch/2)*dpr)),right=Math.min(cv.width,Math.ceil(((r[2]-cam.x)*zoom+cw/2)*dpr)),bottom=Math.min(cv.height,Math.ceil(((r[3]-cam.y)*zoom+ch/2)*dpr));for(let yy=y;yy<bottom;yy++)for(let xx=x;xx<right;xx++)for(let c=0;c<4;c++){const p=(yy*cv.width+xx)*4+c,d=Math.abs(expected[p]-actual[p]);if(d>2)oracle.channels++;oracle.max=Math.max(oracle.max,d);}}
   oracle.actors=actors.length;oracle.modes=actors.map(a=>a.mode||a.kind);if(oracle.channels)window.__matrixFailure={reference:ref.c.toDataURL(),actual:got.c.toDataURL()};
  }
 }
 return{index,zoom,night:nightMode,quality:gameOptions.quality,reducedMotion:gameOptions.reducedMotion,dpr,camera:{...cam},pausedStable,coldStable,unchanged:state===JSON.stringify(G),oracle,atlasBytes,brownfieldBytes:brownfieldArtAtlas.size*72*96*4,repairBytes:(viewUnderlayRaster.width*viewUnderlayRaster.height+actorRepairRaster.width*actorRepairRaster.height)*4,viewportBytes:cv.width*cv.height*8};
};'''
results=[];errors=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);
 for width,height,dpr in [(640,360,1),(844,390,2),(1280,720,3)]:
  p=b.new_page(viewport={'width':width,'height':height},device_scale_factor=dpr);p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',(ROOT/'tools/qa_live_network.js').read_text()+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.keyboard.press('Escape');p.evaluate(large);network=p.evaluate('__liveNetworkBuild()');p.evaluate('__townTest.step(3)');assert p.evaluate('__paletteMatrix()');states=p.evaluate('__matrixStates()')
  for i in range(12):
   r=p.evaluate('__cameraMatrix',i);r['viewport']=[width,height,dpr];r['warmDrawMeanMs']=p.evaluate('__townTest.renderBench(8)');results.append(r);print(width,dpr,i,r['oracle'],r['pausedStable'],r['coldStable'],flush=True)
   if not(r['pausedStable'] and r['coldStable'] and r['unchanged'] and not r['oracle']['channels'] and r['atlasBytes']<=48*1024*1024 and r['brownfieldBytes']<=884736 and r['repairBytes']<=r['viewportBytes']):
    import base64
    for name,data in (p.evaluate('window.__matrixFailure||{}')).items():(out/(str(width)+'-'+str(i)+'-'+name+'.png')).write_bytes(base64.b64decode(data.split(',')[1]))
    (out/'failure.json').write_text(json.dumps(r,indent=2));raise AssertionError(r)
  p.screenshot(path=str(out/(str(width)+'-controls.png')))
  if width==640:
   from PIL import Image
   import io,time
   private=ROOT.parent/'scratch/camera-matrix';private.mkdir(parents=True,exist_ok=True)
   for night in [False,True]:
    assert p.evaluate('__matrixMotion',night);p.locator('#pause').click();frames=[];start=__import__('time').monotonic()
    for n in range(24):frames.append(Image.open(io.BytesIO(p.locator('#view').screenshot())).convert('RGB'));p.wait_for_timeout(60)
    p.locator('#pause').click();elapsed=__import__('time').monotonic()-start;frames[0].save(private/('transit-night.gif' if night else 'transit-day.gif'),save_all=True,append_images=frames[1:],duration=round(elapsed/24*1000),loop=0)
  p.close()
 b.close()
assert not errors,errors
(out/'checks.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':results,'network':network,'visualStates':states,'errors':errors,'fixture':'Authored 2000 residents, paid 21 deeds and three transit routes. Redevelopment demand is authored to reach the real paid project path. Oracle truck is a controlled render-only silhouette.'},indent=2)+'\n')
