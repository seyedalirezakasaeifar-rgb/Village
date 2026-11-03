"""A real eligible frontage actor remains visible when its parent centre leaves view."""
import hashlib,json,base64
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageChops
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text();out=ROOT/'reports/current-controls-inspection/agent-edges';out.mkdir(parents=True,exist_ok=True)
probe=r'''window.__actorEdgeCase=({zoom,edge})=>{
 __townTest.reset('settlement',42);__townTest.step(1);closePanel();gameOptions.quality='high';gameOptions.effects=true;gameOptions.traffic=true;gameOptions.reducedMotion=false;cam.zoom=zoom;nightMode=false;dirty=true;draw();
 const options=displayItems.filter(a=>a.b).flatMap(item=>buildingActivity([item]).map(actor=>({item,actor}))),pair=options.find(v=>edge==='left'?v.actor.x-v.item.x>10:v.actor.y-v.item.y>10);if(!pair)throw Error('No real eligible frontage actor');const {item,actor}=pair,boundary=edge==='left'?(item.x+actor.x)/2:(item.y+actor.y)/2;
 cam.x=edge==='left'?boundary+cw/(2*zoom):actor.x;cam.y=edge==='top'?boundary+ch/(2*zoom):actor.y;
 const paint=paintSceneActors;let actualActors=[];paintSceneActors=function(g,actors,visible){actualActors=actors.slice();return paint(g,actors,visible)};
 try{dirty=true;draw();const actual=cv.toDataURL(),model=JSON.stringify(G),present=actualActors.some(a=>a.kind==='vehicle'&&a.v?.style==='pedestrian'&&a.v.id===actor.v.id);
  paintSceneActors=function(g,actors,visible){const list=actors.slice();if(!list.some(a=>a.kind==='vehicle'&&a.v?.style==='pedestrian'&&a.v.id===actor.v.id))list.push(actor);return paint(g,list,visible)};dirty=true;draw();
  return {zoom,edge,actorId:actor.v.id,building:item.b.id,parentCentreOutside:edge==='left'?item.x<boundary:item.y<boundary,actorCentreInside:edge==='left'?actor.x>boundary:actor.y>boundary,actualActorPresent:present,actual,oracle:cv.toDataURL(),modelUnchanged:model===JSON.stringify(G)};
 }finally{paintSceneActors=paint}
};'''
rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':568,'height':320});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
 for zoom in [.65,.9,1.4]:
  for edge in ['left','top']:
   row=p.evaluate('o=>__actorEdgeCase(o)',{'zoom':zoom,'edge':edge});images={}
   import io
   for key in ['actual','oracle']:images[key]=Image.open(io.BytesIO(base64.b64decode(row.pop(key).split(',')[1]))).convert('RGB')
   row['differentPixels']=sum(px!=(0,0,0)for px in ImageChops.difference(images['actual'],images['oracle']).getdata());rows.append(row)
   if zoom==1.4 and edge=='left':images['actual'].save(out/'fixed-actual.png');images['oracle'].save(out/'independent-oracle.png')
   assert row['actualActorPresent']and row['parentCentreOutside']and row['actorCentreInside']and row['modelUnchanged']and row['differentPixels']==0,row
 assert not errors,errors;b.close()
result={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':rows,'errors':errors,'scope':'Real staff frontage sampling; ordinary Canvas renderer, no mesh/style replacement or physical-device acceptance'};(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
