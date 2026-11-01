"""Unassembled root-refusal prototype: exact-state proof, costs, outer-UI gap."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();experiment=(ROOT/'experiments/paid-root-admission.js').read_text()
probe=r'''
window.__paidRootTest={
 prepare:(operation='construct')=>{__townTest.reset('settlement',42);paused=true;crewDay=-1;crewsUsed=new Map();regionalCrews=0;frameClock=0;traffic=[];intersectionGates.clear();visualState=918273;__inactivePersonCodec.enable(true);for(let i=0;i<2;i++)if(!hydrateSave(archivePayload()))throw Error('Canonical fixture rejected');let site=null;for(let y=2;y<T-2&&!site;y++)for(let x=2;x<T-2;x++)if(canPlace(x,y,true,'grocer')){site={x,y};break;}if(!site)throw Error('No legal actual site');if(operation==='completeDevelopmentProjects'){financeConstruction(buildCost.grocer);if(!startDevelopmentProject('firm',site,types.grocer.cost*10,1,{firmKind:'grocer',capital:12000}))throw Error('Actual funded project rejected');}return site;},
 run:operation=>{const site=__paidRootTest.prepare(operation),start=performance.now();if(operation==='construct')construct('grocer',site.x,site.y);else completeDevelopmentProjects();const ms=performance.now()-start;return {ms,model:archiveLogicalPayload(),rng:rngState};},
 refusal:operation=>{const site=__paidRootTest.prepare(operation),quoteStart=performance.now();G.rootAdmissionPadding='';let wire=archivePayload(),headroom=INACTIVE_CODEC_LIMITS.bytes-new Blob([wire]).size-8192;G.rootAdmissionPadding='a'.repeat(headroom);wire=archivePayload();if(!hydrateSave(wire))throw Error('Near-limit initialized fixture rejected');const wireBytes=new Blob([encodeInactiveLogicalArchive(JSON.stringify(G))]).size,reserveBytes=16384;if(wireBytes>INACTIVE_CODEC_LIMITS.bytes||wireBytes<INACTIVE_CODEC_LIMITS.bytes-32768)throw Error('Near-limit fixture not bounded as intended');
  const quoteAndFixtureMs=performance.now()-quoteStart;const before=JSON.stringify(G),rng=rngState,crew=[crewDay,regionalCrews,JSON.stringify([...crewsUsed])],timeline=[saveEpoch,saveOrder,saveRevision],queue=savePendingWrite;let effects=0,policyCalls=0;
  const persist=persistSnapshot,notify=toast,log=story,idb=writeIndexedDB;persistSnapshot=()=>{effects++;return Promise.resolve(true);};toast=()=>{effects++;};story=()=>{effects++;};writeIndexedDB=()=>{effects++;return Promise.resolve(true);};
  __paidRootPrototype.enable(true,command=>{policyCalls++;return {ok:wireBytes+reserveBytes<=INACTIVE_CODEC_LIMITS.bytes,reason:'Controlled conservative 16KiB root reservation exceeds certified near-limit headroom'};});
  const start=performance.now();let result;try{result=operation==='construct'?construct('grocer',site.x,site.y):completeDevelopmentProjects();}finally{persistSnapshot=persist;toast=notify;story=log;writeIndexedDB=idb;}const ms=performance.now()-start;
  const exact=JSON.stringify(G)===before&&rngState===rng&&JSON.stringify(crew)===JSON.stringify([crewDay,regionalCrews,JSON.stringify([...crewsUsed])])&&JSON.stringify(timeline)===JSON.stringify([saveEpoch,saveOrder,saveRevision])&&savePendingWrite===queue;
  if(!exact||effects||result!==false||policyCalls!==1)throw Error('Root refusal changed model/RNG/crew/persistence/notification state');
  return {operation,wireBytes,reserveBytes,quoteAndFixtureMs,rootMs:ms,policyCalls,effects,exactModelRngCrewChronologyAndQueue:true,status:__paidRootPrototype.status()};
 },
 costs:()=>{const site=__paidRootTest.prepare('construct');__paidRootPrototype.enable(false);let start=performance.now();for(let i=0;i<20000;i++)construct('road',-1,-1,true);const disabledMs=performance.now()-start;__paidRootPrototype.enable(true,()=>({ok:false,reason:'Ordinary-size refusal overhead control'}));start=performance.now();for(let i=0;i<20000;i++)construct('road',-1,-1,true);const refusalMs=performance.now()-start;return {iterations:20000,disabledInvalidCommandMs:disabledMs,enabledPureRefusalMs:refusalMs,fixture:'Invalid/no-op commands isolate entry cost; actual legal commands measured separately'};},
 prepareOuterGap:(direct=false)=>{const site=__paidRootTest.prepare('construct');__paidRootPrototype.enable(true,()=>({ok:false,reason:'Controlled whole-root refusal'}));window.__paidOuter={before:archiveLogicalPayload(),rng:rngState,writes:[],notes:[],oldPersist:persistSnapshot,oldToast:toast};persistSnapshot=payload=>{__paidOuter.writes.push(JSON.parse(payload).payload?.treasury??JSON.parse(payload).treasury);return Promise.resolve(true);};toast=msg=>__paidOuter.notes.push(msg);saveStoreReady=true;showCustomEvent(direct?'CIVIC PROJECT':'PAID ROOT PROBE','Unclassified paid callback','The outer handler charges before its construction callback.',[{title:'Refused construction callback',cost:direct?0:1000,apply:()=>construct('grocer',site.x,site.y)}]);return true;},
 outerResult:()=>{const p=__paidOuter,old=JSON.parse(p.before),result={treasuryDelta:G.treasury-old.treasury,regionDelta:G.region-old.region,propertiesDelta:G.buildings.length-old.buildings.length,rngUnchanged:rngState===p.rng,writes:p.writes.length,notifications:p.notes,dialogClosed:!pendingEvent,rootRefused:__paidRootPrototype.status().last?.refused===true};persistSnapshot=p.oldPersist;toast=p.oldToast;return result;}
};
'''
results={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'experiment_sha256':hashlib.sha256(experiment.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'productionAssembled':False,'providerImplemented':False,'controls':{},'refusals':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--js-flags=--max-old-space-size=384'])
 def page(experimental):
  p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',(experiment if experimental else '')+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();return p
 for operation in ['construct','completeDevelopmentProjects']:
  outputs=[];times=[]
  for enabled in [False,True]:
   p=page(enabled);sample=[]
   for i in range(6):
    v=p.evaluate('op=>__paidRootTest.run(op)',operation);sample.append(v.pop('ms'));outputs.append(v)
   times.append(sample);p.close()
  assert all(v==outputs[0] for v in outputs),'Disabled prototype changes actual command model/RNG '+operation
  results['controls'][operation]={'exactDisabledBaselineEquivalence':True,'baselineMs':times[0],'disabledPrototypeMs':times[1]}
  p=page(True);results['refusals'].append(p.evaluate('op=>__paidRootTest.refusal(op)',operation));p.close()
 p=page(True);results['entryCosts']=p.evaluate('__paidRootTest.costs()');p.close()
 for direct in [False,True]:
  p=page(True);p.evaluate('direct=>__paidRootTest.prepareOuterGap(direct)',direct);p.locator('#eventChoices button').first.click();results['directReviewedCallerGap' if direct else 'outerBoundaryGap']=p.evaluate('__paidRootTest.outerResult()');p.close()
 b.close()
assert results['outerBoundaryGap']['treasuryDelta']==-1000 and results['outerBoundaryGap']['propertiesDelta']==0 and results['outerBoundaryGap']['writes']>0,'Outer paid-handler gap not reached'
assert results['directReviewedCallerGap']['treasuryDelta']==0 and results['directReviewedCallerGap']['propertiesDelta']==0 and results['directReviewedCallerGap']['writes']>0 and results['directReviewedCallerGap']['dialogClosed'],'Direct review caller effects gap not reached'
(ROOT/'reports/paid-root-prototype.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
