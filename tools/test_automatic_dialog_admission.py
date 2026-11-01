from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();api=(ROOT/'experiments/root-capacity-api.js').read_text();adapter=(ROOT/'experiments/automatic-day-admission.js').read_text()
probe=r'''
window.__dialogAdmission=async()=>{
 __townTest.reset('settlement',42);__townTest.step(30);__inactivePersonCodec.enable(true);
 const snapshots=[];save=()=>{snapshots.push(archiveLogicalPayload());return Promise.resolve(true);};
 const a=__automaticDayAdmission;if(!a.enable())throw Error('Activation refused');
 const event=COUNCIL_EVENTS[0],base=dailyEconomy;let applied=0,requested,inside=false;
 dailyEconomy=function(){base();showCustomEvent(event.type,event.title,event.text,[{title:'Review later',cost:0,apply:()=>applied++}]);inside=$('eventDialog').style.display==='none';requested=save();};
 tick();dailyEconomy=base;const final=archiveLogicalPayload();if(!inside||$('eventDialog').style.display!=='flex'||applied||!pendingEvent||!G.councilInbox.some(e=>e.title===event.title))throw Error('Dialog was early/missing or applied choice');
 if(!await requested||snapshots.length!==1||snapshots[0]!==final||!G.history.some(h=>h.day===G.day))throw Error('Dialog persisted an incomplete day');
 const day=G.day;tick();if(G.day!==day)throw Error('Blocking dialog did not block next day');
 closeCouncilDialog();const before=archiveLogicalPayload(),beforeRng=rngState,dialogHTML=$('eventChoices').innerHTML;
 dailyEconomy=function(){base();try{showCustomEvent(event.type,event.title,event.text,[{title:'Must disappear',apply:()=>applied++}]);requested=save();__capacityAdmissionProtocol.shared.refuse('Injected event refusal');}catch(_){}};
 tick();dailyEconomy=base;if(archiveLogicalPayload()!==before||rngState!==beforeRng||pendingEvent||$('eventDialog').style.display!=='none'||$('eventChoices').innerHTML!==dialogHTML||await requested||applied)throw Error('Caught dialog refusal escaped');
 a.retry();tick();if(G.day!==day+1)throw Error('Retry failed after event refusal');
 const regular=a.certificate();
 // Force worst legal source descriptions; this must become explicit refusal,
 // never truncate names or silently delete the corresponding cargo owners.
 const name=G.people[0].name;G.people[0].name='\\\"\u0001🌊'.repeat(10000);const longName=G.people[0].name;a.disable();const longAccepted=a.enable();const longCertificate=a.certificate();if(longAccepted||G.people[0].name!==longName)throw Error('Long visual reason reserve not enforced');G.people[0].name=name;
 // Actual import defaults, rather than a per-entity guessed reserve.
 for(const f of G.firms)delete f.unitCost;G.normalizationPadding='';const raw=archivePayload();G.normalizationPadding='x'.repeat(INACTIVE_CODEC_LIMITS.bytes-new Blob([raw]).size-64);const untouched=JSON.stringify(G),oldRng=rngState;
 if(a.enable()||JSON.stringify(G)!==untouched||rngState!==oldRng||!/budget/.test(a.status().last.reason))throw Error('Normalization expansion was admitted or changed live state');

 return {dialogOnlyVisibleAfterCommit:true,choiceNotExecuted:true,coalescedSaveMatchesCompletedDay:true,pendingDialogBlocksNextDay:true,caughtRefusalRestoresModelRngAndDOM:true,rejectedSaveFalse:true,retryPass:true,longNameReserveRefusesWithoutTruncation:true,exactImportNormalizationExpansionRefusedAtomically:true,regularCertificate:regular,longNameCertificate:longCertificate,productionAssembled:false};
};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',api+'\n'+adapter+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__dialogAdmission()');b.close()
out={'base_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'adapter_sha256':hashlib.sha256(adapter.encode()).hexdigest(),'result':r};target=ROOT/'reports/automatic-day-admission';target.mkdir(exist_ok=True);(target/'dialog-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
