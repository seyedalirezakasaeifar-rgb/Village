"""Real road-maintenance phase, committed tree isolation, faults and measured costs."""
from pathlib import Path
import sys,json,gzip,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();cow=(ROOT/'experiments/cow-phase.js').read_text();late=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)).decode()
probe=r'''
window.__cowPhaseProof=()=>{
 const live=G,serialized=JSON.stringify(G),root=JSON.parse(serialized),store=createPhaseCowStore(root),rows=[];let oracle=JSON.parse(serialized),faults=0;
 const clean=()=>{roadNetwork=null;roadGraphOwner=null;cacheBuildingsFor=null;};
 try{
  for(let round=0;round<8;round++){
   G=oracle;clean();let t=performance.now();graph();const oracleWarmMs=performance.now()-t;t=performance.now();maintainRoads();const oraclePhaseMs=performance.now()-t;
   const committed=store.current,before=JSON.stringify(committed);t=performance.now();const tx=store.begin();const beginMs=performance.now()-t;G=tx.draft;clean();t=performance.now();graph();const draftWarmMs=performance.now()-t;t=performance.now();maintainRoads();const draftPhaseMs=performance.now()-t;
   if(JSON.stringify(committed)!==before)throw Error('Committed read model changed during phase');const result=tx.commit();if(JSON.stringify(result.root)!==JSON.stringify(oracle))throw Error('Real phase differs from synchronous oracle');let expired=false;try{tx.draft.day;}catch(e){expired=true;}if(!expired)throw Error('Expired draft remained usable');rows.push({round,beginMs,oracleWarmMs,oraclePhaseMs,draftWarmMs,draftPhaseMs,commitMs:result.commitMs,metrics:result.metrics});
  }
  for(const faultAfter of [1,3,25,100]){const committed=store.current,before=JSON.stringify(committed),tx=store.begin({faultAfter});G=tx.draft;clean();let failed=false;try{maintainRoads();}catch(e){if(!e.message.includes('Injected phase fault'))throw e;failed=true;}if(!failed)throw Error('Fault not reached');tx.rollback();if(JSON.stringify(store.current)!==before)throw Error('Rollback changed committed data');faults++;}
  const resumedOracle=JSON.parse(JSON.stringify(store.current));G=resumedOracle;clean();maintainRoads();const resumed=store.begin();G=resumed.draft;clean();maintainRoads();if(JSON.stringify(resumed.commit().root)!==JSON.stringify(resumedOracle))throw Error('Post-fault continuation differs');
  let aliasRejected=false,cycleRejected=false;const shared={value:1};try{createPhaseCowStore({a:shared,b:shared});}catch(e){aliasRejected=true;}const cycle={};cycle.self=cycle;try{createPhaseCowStore(cycle);}catch(e){cycleRejected=true;}if(!aliasRejected||!cycleRejected||Object.isFrozen(shared))throw Error('Unsafe initial ownership audit');
  const tx=store.begin();G=tx.draft;let unsupported='';const previousMarket=marketOpen,previousRng=rngState;try{dailyEconomy();}catch(e){unsupported=e.message;}finally{marketOpen=previousMarket;rngState=previousRng;tx.rollback();}if(!unsupported.includes('Unsupported container replacement'))throw Error('Broader phase did not reject unsupported ownership: '+unsupported);
  let readMutation='';G=store.current;try{ensureSystems();}catch(e){readMutation=e.message;}
  return {auditMs:store.auditMs,rows,faults,committedIsolation:true,exactEightPhaseContinuation:true,postFaultContinuationExact:true,aliasRejected,cycleRejected,unsupportedDailyEconomy:unsupported,existingEnsureOnReadModel:readMutation,defaultGameUnchanged:JSON.stringify(live)===serialized};
 }finally{G=live;clean();}
};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',cow+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townTest.load(s)',late);result=p.evaluate('__cowPhaseProof()');b.close()
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'prototype_sha256':hashlib.sha256(cow.encode()).hexdigest(),'fixture_sha256':hashlib.sha256(late.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,**result};(ROOT/'reports/cow-phase-proof.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
