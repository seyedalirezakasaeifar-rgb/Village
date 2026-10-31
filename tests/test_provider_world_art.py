"""Real fee clients drive institution activity; rural kit and night state stay visual."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,json,hashlib
fixture=next(ast.literal_eval(n.value) for n in ast.parse((ROOT/'tests/test_private_services.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='probe' for x in n.targets))
source=(ROOT/'assets/game.js').read_text();out=ROOT/'reports/provider-world';out.mkdir(parents=True,exist_ok=True)
probe=r'''window.__providerArtCheck=id=>{
 const f=G.firms[id],b=readBuild(f.building),item=buildingItemsById.get(b.id),before=JSON.stringify(G),state=providerVisualState(b);
 const scenes=()=>workdayScenes([item]).map(a=>a.scene),active=scenes();
 const old={clients:f.clientsToday,capacity:f.serviceCapacity,closed:f.closed};f.clientsToday=0;const unpaid=scenes();f.clientsToday=old.clients;f.serviceCapacity=0;const unstaffed=scenes();f.serviceCapacity=old.capacity;f.closed=true;const closed=scenes();f.closed=old.closed;
 const capture=()=>{dirty=true;draw();return cv.toDataURL()};nightMode=true;const one=capture(),two=capture();nightMode=false;dirty=true;draw();
 let sources=0,finite=true;for(const sprite of atlas.values())for(const light of sprite.lightSources||[]){sources++;finite=finite&&light.length===5&&light.every(Number.isFinite);}
 const oldZoom=cam.zoom;cam.zoom=.2;paintNightScene(ctx,new Proxy([],{get(){throw Error('Far night iterated items')}}));cam.zoom=oldZoom;
 return{sources,finite,state,active,unpaid,unstaffed,closed,independent:!isPublicFacility(b),appearance:appearanceKey(b),unchanged:before===JSON.stringify(G),stable:one===two,lights:nightEmissionCanvas.width*nightEmissionCanvas.height,valid:validateTown()};
};window.__ruralArtCheck=()=>{const before=JSON.stringify(G),rows=[];for(const kind of RURAL_ART_KINDS){const item=displayItems.find(i=>i.b?.kind===kind);if(!item)throw Error('Missing '+kind);const sprite=spriteFor(item),data=sprite.getContext('2d').getImageData(0,0,sprite.width,sprite.height).data;let n=0;for(let i=3;i<data.length;i+=4)if(data[i])n++;rows.push({kind,pixels:n,lights:(sprite.lightSources||[]).length});}return{rows,unchanged:before===JSON.stringify(G),seasons:seasonsEnabled()};};'''
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click()
 for kind in ['school','fire']:
  f=p.evaluate('k=>__privateFixture(k,100)',kind);p.evaluate('__townTest.step(1)');p.evaluate('__townTest.capture({zoom:1})');r=p.evaluate('__providerArtCheck',f['firm']);assert r['finite'] and r['sources']<=600*88 and r['state']['active'] and r['independent'] and r['stable'] and r['unchanged'] and r['valid']['ok'],r
  scene='teaching' if kind=='school' else 'readiness';assert scene in r['active'] and scene not in r['unpaid'] and scene not in r['closed'],r
  if kind=='fire':assert scene not in r['unstaffed'],r
  rows.append({'kind':kind,**r})
 p.evaluate("__townTest.reset('settlement',42)");p.evaluate('__townTest.capture({zoom:.8})');rural=p.evaluate('__ruralArtCheck()');assert rural['unchanged'] and not rural['seasons'] and len(rural['rows'])==5 and all(r['pixels']>100 for r in rural['rows']),rural
 assert not errors,errors;b.close()
(out/'checks.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledFeeFixtures':True,'providers':rows,'rural':rural,'errors':errors},indent=2)+'\n');print('PASS fee-client teaching/readiness, unpaid/closed/unstaffed guards, independent identity, rural kit, pause stability, no economic writes, seasons off')
