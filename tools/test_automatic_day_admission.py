from pathlib import Path
import sys,json,hashlib,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();api=(ROOT/'experiments/root-capacity-api.js').read_text();adapter=(ROOT/'experiments/automatic-day-admission.js').read_text()
probe=r'''
window.__autoTest=async()=>{
 __townTest.reset('settlement',42);__townTest.step(90);const oracle=archiveLogicalPayload();
 __townTest.reset('settlement',42);__inactivePersonCodec.enable(true);
 const a=__automaticDayAdmission;if(a.status().enabled)throw Error('Enabled by default');if(!a.enable())throw Error('Initial refused '+JSON.stringify(a.status()));
 __townTest.step(90);if(archiveLogicalPayload()!==oracle)throw Error('Granted day diverged from synchronous oracle');
 const completed=archiveLogicalPayload();if(a.step(saveEpoch-1)!==false||archiveLogicalPayload()!==completed)throw Error('Stale day command ran');const oldTown=G,oldPerson=G.people[0],oldRng=rngState;
 // Force the next whole day beyond byte reserve without crossing raw wire cap.
 G.capacityTestPadding='x'.repeat(INACTIVE_CODEC_LIMITS.bytes-a.certificate().bytes-a.certificate().reserveBytes+1000);
 const stable=archiveLogicalPayload();tick();if(a.status().last.ok||archiveLogicalPayload()!==stable||G!==oldTown||G.people[0]!==oldPerson||rngState!==oldRng||!paused||acc!==0)throw Error('Whole day refusal not exact');
 const last=a.status().last;tick();if(a.status().last!==last||archiveLogicalPayload()!==stable)throw Error('Refused day retried automatically');
 delete G.capacityTestPadding;a.retry();tick();if(G.day!==92)throw Error('Explicit retry failed');
 const cert=a.certificate(),beforeAuthoritative=JSON.stringify({rng:rngState,transport:G.transport,freight:G.freight,regional:G.regionalTrade});
 // Existing meaningful cargo/routes remain; suppress only creation of additional
 // disposable traffic actors at a documented count, without consuming RNG.
 const oldTraffic=traffic;traffic=Array.from({length:80},(_,i)=>({id:i,path:[1,2],segment:0,fraction:0}));const v=beginVehicle();if(v!==null||traffic.length!==80||JSON.stringify({rng:rngState,transport:G.transport,freight:G.freight,regional:G.regionalTrade})!==beforeAuthoritative)throw Error('Visual cap altered authoritative state');traffic=oldTraffic;
 if(!archivePayload())throw Error('Committed export failed');
 const beforeFault=archiveLogicalPayload(),economy=dailyEconomy;let pendingSave;
 dailyEconomy=function(){economy();pendingSave=save();G.treasury--;random();__capacityAdmissionProtocol.shared.refuse('Injected mid-day capacity refusal');};
 tick();dailyEconomy=economy;if(archiveLogicalPayload()!==beforeFault||await pendingSave)throw Error('Partial mid-day persistence escaped');
 a.disable();G.capacityTestPadding='';G.capacityTestPadding='x'.repeat(INACTIVE_CODEC_LIMITS.bytes-new Blob([archivePayload()]).size-16);const near=archiveLogicalPayload();if(a.enable()||archiveLogicalPayload()!==near)throw Error('16-byte visual headroom admitted');delete G.capacityTestPadding;

 return {oracleDays:90,exactArchiveAndRng:true,wholeDayBudgetRefusal:true,midDaySaveDiscarded:true,staleDayCommandRejected:true,insufficientVisualReserveRefusedBeforeDay:true,objectIdentityPreserved:true,noAutomaticRetry:true,explicitRetry:true,visualActorCap:80,authoritativeCargoUntouched:true,certificate:cert,productionAssembled:false};
};
'''
days=int(os.environ.get('ADMISSION_DAYS','90'));probe=probe.replace('step(90)',f'step({days})').replace('G.day!==92',f'G.day!=={days+2}').replace('oracleDays:90',f'oracleDays:{days}')
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',api+'\n'+adapter+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__autoTest()');b.close()
target=ROOT/'reports/automatic-day-admission';target.mkdir(exist_ok=True);out={'base_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'adapter_sha256':hashlib.sha256(adapter.encode()).hexdigest(),'result':r};(target/'result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
