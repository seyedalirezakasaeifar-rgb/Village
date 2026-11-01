"""Trusted host canvas road tap, repair and bounded drag through one shared root."""
from pathlib import Path
import ast,sys,json,hashlib,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();base=(ROOT/'tools/fixtures/current-paid-fixture.js').read_text()
names=['root-capacity-api.js','paid-command-root.js'];bootstrap='\n'.join((ROOT/'experiments'/n).read_text() for n in names)+'\n'+(ROOT/'tools/fixtures/current-paid-owner.js').read_text()+"\nwindow.__gameCapacityRoot=window.__installCurrentPaidTestOwner();const rootAdmission=window.__installPaidCommandLayer();\n"
probe=r'''
window.__roadControl={
 limitProbe:()=>{const before=__rootTxTest.capture(),metrics=__gameCapacityRoot.metrics(),pos=iso(900,900),rect=cv.getBoundingClientRect();pointer.down=true;pointer.activeId=17;pointer.lastRoad=[3,3];let called=false;const handled=rootAdmission.routeRoadStroke({pointerId:17,clientX:rect.left+cw/2+(pos[0]-cam.x)*cam.zoom,clientY:rect.top+ch/2+(pos[1]+TH/2-cam.y)*cam.zoom},()=>{called=true;});if(!handled||called||!__rootTxTest.unchanged(before)||__gameCapacityRoot.metrics().captures!==metrics.captures||rootAdmission.status().last.code!=='stroke-limit')throw Error('Oversized stroke was not rejected before work');return {syntheticApiProbe:true,rejectedBeforeCapture:true,zeroModelCalls:true,unchanged:true};},
 prepare:async(kind,enabled)=>{window.__denyRoad=false;__rootTxTest.prep('construct',false,false);let site=null;
  if(['repair','bridge-repair'].includes(kind)){if(kind==='bridge-repair'){const id=[...waterNetwork().nodes].find(id=>G.tiles[id]===1&&charterOwns(id%T,id/T|0));if(id==null)return {unavailable:'No pre-existing owned bridge (road tile in the actual water-network nodes) exists in this seed42 fixture.'};site={x:id%T,y:id/T|0};}else for(let y=3;y<54&&!site;y++)for(let x=3;x<54;x++)if(G.tiles[roadId(x,y)]===1){site={x,y};break;}ensureRoadWear();G.roadWear[roadId(site.x,site.y)]=40;}
  else{for(let y=3;y<54&&!site;y++)for(let x=3;x<50;x++)if(Array.from({length:5},(_,i)=>roadId(x+i,y)).every(id=>[0,3].includes(G.tiles[id])&&!G.landUse?.[id]&&!buildingAt(id%T,id/T|0))){site={x,y};break;}}
  if(!site)throw Error('No real road control site');if(kind==='mixed')construct('road',site.x+2,site.y);buildMode=['repair','bridge-repair'].includes(kind)?'repair':'road';closePanel();const pos=iso(site.x,site.y);cam={x:pos[0],y:pos[1]+TH/2,zoom:.85};dirty=true;await __rootTxTest.drain();rootAdmission.enable(enabled);const rect=cv.getBoundingClientRect(),screen=(x,y)=>{const p=iso(x,y);return {x:rect.left+cw/2+(p[0]-cam.x)*cam.zoom,y:rect.top+ch/2+(p[1]+TH/2-cam.y)*cam.zoom};};return {start:screen(site.x,site.y),end:screen(site.x+4,site.y),site};
 },
 capture:async deny=>{await __rootTxTest.drain();window.__denyRoad=deny;window.__roadReceipt=JSON.stringify(G.serviceCashEvidence);window.__roadBefore=__rootTxTest.capture();window.__roadMoney=totalMoney();window.__roadMetrics=__gameCapacityRoot.metrics();window.__roadConstructions=G.construction;window.__roadWrites=[];writeIndexedDB=envelope=>{const decoded=JSON.parse(envelope.payload);window.__roadWrites.push({active:rootAdmission.active(),construction:decoded.construction,treasury:decoded.treasury});return Promise.resolve(true);};},
 result:async(deny,enabled,roots=1)=>{await __rootTxTest.drain();const before=window.__roadBefore,metrics=__gameCapacityRoot.metrics(),status=rootAdmission.status(),unchanged=__rootTxTest.unchanged(before);if(Math.abs(totalMoney()-window.__roadMoney)>.001)throw Error('Road control cash drift');if(enabled&&(metrics.captures-window.__roadMetrics.captures!==roots||metrics.certificates-window.__roadMetrics.certificates!==roots))throw Error('Canvas gesture did not use one root '+JSON.stringify({metrics,status}));if(enabled&&(__roadWrites.length!==(deny?0:1)||__roadWrites.some(w=>w.active||w.construction!==G.construction||w.treasury!==G.treasury)))throw Error('Road persistence escaped a complete committed event '+JSON.stringify(__roadWrites));if(deny&&(!unchanged||status.last?.ok||roadBatchDirty))throw Error('Refused road command partially committed');if(JSON.stringify(G.serviceCashEvidence)!==window.__roadReceipt)throw Error('Completed-day receipt changed');const r={model:archivePayload(),rng:rngState,built:G.construction-window.__roadConstructions,status,exactRefusal:deny?unchanged:null,batchFlushed:!roadBatchDirty,cashConserved:true,committedWrites:__roadWrites,pointerReleased:!pointer.down};if(!deny){if(!hydrateSave(archivePayload()))throw Error('Current street command cannot self-import');const once=archivePayload();if(!hydrateSave(once)||archivePayload()!==once)throw Error('Street normalized export not fixed');r.normalized=once;if(JSON.stringify(G.serviceCashEvidence)!==window.__roadReceipt)throw Error('Reload changed completed receipt');}return r;}
};
'''
out={'base':'d2b7086','hostTestOwnerOnly':True,'productionComposition':False,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'experiment_sha256':{n:hashlib.sha256((ROOT/'experiments'/n).read_bytes()).hexdigest() for n in names},'minimalRegistryOwner':bool(os.environ.get('PAID_MINIMAL_OWNER')),'hostTrustedPointer':True,'physicalAndroid':False,'productionEnabled':False,'reservationFaultInjection':True,'cases':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 def page():
  p=b.new_page(viewport={'width':1100,'height':800});p.route('http://road-control.test/**',lambda r:r.fulfill(status=200,content_type='text/html',body=html));p.goto('http://road-control.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bootstrap+base+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__rootTxTest.drain()');return p
 def command(p,kind,enabled,deny):
  pos=p.evaluate('x=>__roadControl.prepare(x.kind,x.enabled)',{'kind':kind,'enabled':enabled});p.mouse.move(**pos['start']);p.evaluate('deny=>__roadControl.capture(deny)',True if kind=='recovery' else deny)
  if kind in ['stroke','mixed','backtrack','subtile','cancel','recovery']:
   p.mouse.down()
   if kind=='subtile':p.mouse.move(pos['start']['x']+.5,pos['start']['y']+.5)
   else:p.mouse.move(**pos['end'])
   if kind=='recovery':p.evaluate('window.__denyRoad=false');p.mouse.move(pos['end']['x']+.2,pos['end']['y'])
   if kind=='backtrack':
    for _ in range(4):p.mouse.move(**pos['start']);p.mouse.move(**pos['end'])
   if kind=='cancel':p.locator('canvas').first.dispatch_event('pointercancel');p.mouse.up()
   else:p.mouse.up()
  else:p.mouse.click(**pos['start'])
  return p.evaluate('x=>__roadControl.result(x.deny,x.enabled,x.roots)',{'deny':deny,'enabled':enabled,'roots':2 if kind=='recovery' else 1})
 for kind in ['tap','repair','stroke','mixed','backtrack','subtile','cancel','recovery']:
  if kind=='bridge-repair':
   p=page();availability=p.evaluate('__roadControl.prepare("bridge-repair",false)');p.close()
   if availability.get('unavailable'):
    out['cases'].append({'kind':kind,'available':False,'reason':availability['unavailable'],'coverageClaimed':False});print('UNAVAILABLE',kind,availability['unavailable'],flush=True);continue
  states=[];results=[]
  for enabled in [False,True]:
   p=page();r=command(p,kind,enabled,False);states.append((r.pop('model'),r['rng'],r.pop('normalized')));results.append(r);p.close()
  assert states[0]==states[1],('Road full model/RNG mismatch',kind)
  assert results[1]['built']==(4 if kind=='mixed' else 5 if kind in ['stroke','backtrack','cancel','recovery'] else 1),(kind,results)
  p=page();r=command(p,'stroke' if kind in ['backtrack','recovery'] else kind,True,True);r.pop('model');p.close();out['cases'].append({'kind':kind,'exactNormalModelRng':True,'normal':results,'forcedRefusal':r});print('PASS',kind,flush=True)
 p=page();p.evaluate('__roadControl.prepare("stroke",true)');bounded=p.evaluate('__roadControl.limitProbe()');out['oversized']=bounded;p.close();b.close()
(ROOT/'reports/current-paid-streets.json').write_text(json.dumps(out,indent=2));print('PASS all road controls')
