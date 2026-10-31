"""Trusted queued controls and native/save/import barriers at suspended day stages."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text()
probe=r'''
let cooperativeHarnessHold=false;const harnessPump=cooperativePump;cooperativePump=function(sync){if(cooperativeHarnessHold&&!sync)return;return harnessPump(sync);};
window.__coopBarrier={
 prepare:()=>{chosenScenario='settlement';seed(42);paused=true;for(let i=0;i<28;i++)tick();return archivePayload();},
 hold:(stage='dailyEconomy')=>{cooperativeHarnessHold=true;if(!beginCooperativeDay())throw Error('Busy');for(let i=0;i<10000;i++){const next=cooperativeJob.iterator.next();if(next.done)throw Error('No such stage '+stage);if(next.value===stage)break;}return {day:G.day,displayed:cooperativeLastCommittedDay(),header:$('date').textContent,treasury:G.treasury,policy:G.policy.minWage};},
 release:()=>{cooperativeHarnessHold=false;cooperativePost();return afterCommittedDay(()=>({day:G.day,busy:cooperativeDayBusy(),treasury:G.treasury,policy:G.policy.minWage,paused,queue:cooperativeCommands.length,token:cooperativeToken}));},
 state:()=>({day:G.day,busy:cooperativeDayBusy(),paused,policy:G.policy.minWage,queue:cooperativeCommands.length,header:$('date').textContent,bank:JSON.stringify(G.banks),total:totalMoney(),token:cooperativeToken}),
 save:()=>{window.__barrierSaved=false;window.__barrierSavePromise=save().then(ok=>{window.__barrierSaved=true;return ok;});},
 saved:()=>window.__barrierSaved,
 freeze:()=>{cooperativeHarnessHold=true;},
 oracle:()=>{tick();return JSON.parse(archivePayload());},
 startAt:index=>{cooperativeHarnessHold=true;beginCooperativeDay();for(let i=0;i<index;i++){const n=cooperativeJob.iterator.next();if(n.done)return false;}return true;},
 stages:()=>{const it=stagedTick(),a=[];for(let n=it.next();!n.done;n=it.next())a.push(n.value);return a;},
 export:()=>JSON.parse(window.__townArchive.export()),
 poison:()=>{const old=cooperativeJob.iterator;cooperativeJob.iterator={next:()=>{throw Error('Injected continuation fault');}};return old;}
};
'''
def economic(s):
 s=dict(s);s.pop('trafficState',None);s.pop('visualState',None);return s
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'boundaries':[],'errors':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();saved=p.evaluate('__coopBarrier.prepare()');assert p.evaluate('s=>__townTest.load(s)',saved);expected=p.evaluate('__coopBarrier.oracle()');assert p.evaluate('s=>__townTest.load(s)',saved);stages=p.evaluate('__coopBarrier.stages()');assert p.evaluate('s=>__townTest.load(s)',saved)
 # Every yield, including each monthly household filter/assessment, must export a completed equivalent day.
 for index in range(1,len(stages)+1):
  assert p.evaluate('s=>__townTest.load(s)',saved);assert p.evaluate('i=>__coopBarrier.startAt(i)',index);actual=p.evaluate('__coopBarrier.export()');assert economic(actual)==economic(expected),(index,stages[index-1]);assert not p.evaluate('__coopBarrier.state().busy');out['boundaries'].append(stages[index-1])
 # Actual policy draft input + enact click remains queued until a committed day.
 assert p.evaluate('s=>__townTest.load(s)',saved);p.locator('[data-panel=policies]').click();p.locator('[data-policy=minWage]').evaluate('e=>e.closest("details")&&(e.closest("details").open=true)');p.locator('[data-policy=minWage]').fill('27');p.locator('#enactPolicy').click();p.locator('[data-policy=minWage]').evaluate('e=>e.closest("details").open=true');p.evaluate('__coopBarrier.hold()');held=p.evaluate('__coopBarrier.state()');p.locator('[data-policy=minWage]').fill('28');p.locator('#enactPolicy').click();during=p.evaluate('__coopBarrier.state()');assert during['busy'] and during['policy']==held['policy'] and during['header']==held['header'] and during['queue']>0,(held,during);after=p.evaluate('__coopBarrier.release()');assert after['policy']==28 and after['queue']==0,after;out['trustedPolicyReplay']=True
 # Pause gives immediate truthful feedback, then save waits for completion.
 p.evaluate('__coopBarrier.hold()');p.locator('#pause').click();before=p.evaluate('__coopBarrier.state()');assert not before['paused'];p.locator('#pause').click();assert p.evaluate('__coopBarrier.state().paused');p.evaluate('__coopBarrier.save()');assert not p.evaluate('__coopBarrier.saved()');p.evaluate('__coopBarrier.release()');p.wait_for_function('__coopBarrier.saved()');out['pauseAndSaveBarrier']=True
 # Native suspension and malformed import cannot leave a scheduled continuation alive.
 p.evaluate('__coopBarrier.hold()');p.evaluate('__townArchive.suspend()');suspended=p.evaluate('__coopBarrier.state()');assert not suspended['busy'];p.evaluate('__townArchive.resume()');p.evaluate('__coopBarrier.hold()');assert not p.evaluate('__townArchive.restore("{\\\"version\\\":3}")');assert not p.evaluate('__coopBarrier.state().busy');out['nativeSuspendAndMalformedImport']=True
 # Native Back must return the actual dismissal result before acknowledging Android.
 p.evaluate('__coopBarrier.hold()');assert p.evaluate('__townArchive.back()');assert not p.evaluate('__coopBarrier.state().busy');out['nativeBackActualResult']=True
 # Failure restores the preceding completed snapshot, disables the experiment, and reports declined inputs.
 prior=p.evaluate('__townTest.save()');p.evaluate('__coopBarrier.hold()');p.evaluate('__coopBarrier.poison()');p.evaluate('__cooperativeSimulation.finish("fault-test")');assert economic(json.loads(p.evaluate('__townTest.save()')))==economic(json.loads(prior));assert not p.evaluate('__cooperativeSimulation.status().enabled');out['faultRollback']=True
 b.close()
(ROOT/'reports/cooperative-barriers-8.json').write_text(json.dumps(out,indent=2));print(json.dumps({**out,'boundaries':len(out['boundaries'])},indent=2));print('PASS every suspended boundary exports complete equivalent day, trusted policy replay, pause/save/native/import barriers, and fault rollback')
