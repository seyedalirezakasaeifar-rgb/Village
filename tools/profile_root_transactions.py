"""Sequential real paid-command costs on founding and public terminal-session states."""
from pathlib import Path
import sys,subprocess,gzip,json,hashlib,statistics
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
import os
source=Path(os.environ.get('ROOT_SOURCE_JS',str(ROOT/'assets/game.js'))).read_text();late=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)).decode()
bootstrap=(ROOT/'experiments/root-capacity-api.js').read_text()+'\n'+(ROOT/'experiments/game-capacity-root-adapter.js').read_text()+'\n'+(ROOT/'experiments/paid-command-root.js').read_text()+"\nwindow.__installGameCapacityRoot({oracleOnly:true});const rootAdmission=window.__installPaidCommandLayer();\n"
probe=r'''
window.__rootProfile={
 prepare:async(late,kind,enabled,near)=>{await saveStorePromise;
  rootAdmission.enable(false);__inactivePersonCodec.enable(true);if(late){if(!hydrateSave(late))throw Error('Published late fixture rejected');}else __townTest.reset('settlement',42);paused=true;active='';crewDay=-1;crewsUsed=new Map();regionalCrews=0;
  const business=late?'farm':'grocer';let site=null;for(let y=2;y<T-2&&!site;y++)for(let x=2;x<T-2;x++)if(canPlace(x,y,true,business)){site={x,y};break;}if(!site||G.treasury<buildCost[business])throw Error('Real fixture has no affordable legal '+business+' site');
  if(kind==='completion'){financeConstruction(buildCost[business]);if(!startDevelopmentProject('firm',site,types[business].cost*10,1,{firmKind:business,capital:12000}))throw Error('Funded completion setup failed');recompute();}
  archiveLogicalPayload();if(near){G.rootCapacityPadding='';const raw=encodeInactiveLogicalArchive(JSON.stringify(G));G.rootCapacityPadding='x'.repeat(INACTIVE_CODEC_LIMITS.bytes-new Blob([raw]).size);encodeInactiveLogicalArchive(JSON.stringify(G));}
  saveStoreReady=true;writeIndexedDB=()=>Promise.resolve(true);rootAdmission.enable(enabled);window.__rootProfileSite=site;window.__rootProfileBusiness=business;
  await saveWrites;return {day:G.day,people:G.people.length,population:G.stats.population,households:G.households.length,firms:G.firms.length,routes:G.transit.routes.length,wireBytes:new Blob([encodeInactiveLogicalArchive(JSON.stringify(G))]).size};
 },
 run:async kind=>{const start=performance.now(),heapBefore=performance.memory?.usedJSHeapSize;if(kind==='construct')construct(__rootProfileBusiness,__rootProfileSite.x,__rootProfileSite.y);else completeDevelopmentProjects();const synchronousMs=performance.now()-start,status=rootAdmission.status().last;await Promise.resolve();await saveWrites;const throughSaverMs=performance.now()-start;await new Promise(resolve=>requestAnimationFrame(resolve));return {elapsedMs:synchronousMs,throughSaverMs,nextFrameMs:performance.now()-start,status,heapBefore,heapAfter:performance.memory?.usedJSHeapSize};}
};
'''
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'late_fixture_sha256':hashlib.sha256(late.encode()).hexdigest(),'late_fixture_commit':'833afee','hostChromium':True,'physicalAndroid':False,'oracleOnly':True,'productionDefaultEnabled':False,'experiment_sha256':{name:hashlib.sha256((ROOT/'experiments'/name).read_bytes()).hexdigest() for name in ['root-capacity-api.js','game-capacity-root-adapter.js','paid-command-root.js']},'samples':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-precise-memory-info','--js-flags=--max-old-space-size=768'])
 for fixture in ['founding','terminal']:
  for kind in ['construct','completion']:
   for enabled in [False,True]:
    samples=[];state=None
    for _ in range(int(os.environ.get('ROOT_PROFILE_SAMPLES','5'))):
     p=b.new_page();p.route('http://root-cost.test/**',lambda r:r.fulfill(status=200,content_type='text/html',body=html));p.goto('http://root-cost.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bootstrap+probe+'\n// SOURCE: 99-instrumentation.js'));state=p.evaluate('x=>__rootProfile.prepare(x.late,x.kind,x.enabled,false)',{'late':late if fixture=='terminal' else None,'kind':kind,'enabled':enabled});value=p.evaluate('kind=>__rootProfile.run(kind)',kind)
     if enabled and not value['status']['ok']:raise AssertionError(value)
     samples.append(value);p.close()
    out['samples'].append({'fixture':fixture,'kind':kind,'enabled':enabled,'state':state,'medianMs':statistics.median(v['elapsedMs'] for v in samples),'runs':samples});(ROOT/'reports/root-transaction-costs.json').write_text(json.dumps(out,indent=2));print(fixture,kind,enabled,out['samples'][-1]['medianMs'],flush=True)
  p=b.new_page();p.route('http://root-cost.test/**',lambda r:r.fulfill(status=200,content_type='text/html',body=html));p.goto('http://root-cost.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bootstrap+probe+'\n// SOURCE: 99-instrumentation.js'));state=p.evaluate('x=>__rootProfile.prepare(x.late,"construct",true,true)',{'late':late if fixture=='terminal' else None});value=p.evaluate('__rootProfile.run("construct")');assert value['status']['ok'] or value['status']['code']=='capacity';out['samples'].append({'fixture':fixture,'kind':'near-budget-accepted-after-shrink' if value['status']['ok'] else 'near-budget-refusal','enabled':True,'state':state,'runs':[value]});p.close()
 b.close()
(ROOT/'reports/root-transaction-costs.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
