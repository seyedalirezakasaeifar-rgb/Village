"""New public road commands cannot spend or mutate an interrupted simulation day."""
from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text()
probe=r'''window.__bridgeFence=async kind=>{
 __townTest.reset('settlement',42);G.autoBuild=false;const parcel=ANNEX_PARCELS.find(p=>p.id==='east-meadow');if(!purchaseParcel(parcel.id,parcelSurvey(parcel).price))throw Error('Deed fixture failed');
 for(let x=43;x<=63;x++)construct('road',x,15,true);for(let x=69;x<=76;x++)construct('road',x,15,true);flushRoadBatch();invalidateRoads();const bank=roadId(63,15);
 if(kind==='repair'||kind==='decommission'){const q=bridgeCandidateFromBank(bank);if(!commitRoadBridge(bank,q.key).ok)throw Error('Bridge fixture failed');G.bridges[0].condition=50;G.bridgeRevision++;invalidateRoads(false);}
 const original=regionalFreightDay;regionalFreightDay=()=>{throw Error('Injected bridge integration day failure')};try{tick();throw Error('Tick should fail')}catch(e){if(e.message!=='Injected bridge integration day failure')throw e}finally{regionalFreightDay=original;}
 const q=kind==='build'?bridgeCandidateFromBank(bank):kind==='repair'?bridgeRepairQuote(G.bridges[0].id):kind==='decommission'?bridgeRemovalQuote(G.bridges[0].id):roadRemovalQuote(76,15);if(!q.ok)throw Error('Fresh post-fault quote unavailable: '+kind+' '+q.reason);
 const before=archivePayload(),timeline=JSON.stringify([saveEpoch,saveTown,saveRevision,saveOrder]),cash=G.treasury;
 const result=kind==='build'?commitRoadBridge(bank,q.key):kind==='repair'?repairRoadBridge(G.bridges[0].id,q.key):kind==='decommission'?decommissionBridge(G.bridges[0].id,q.key):retireRoadTile(76,15,q.key);
 return {kind,accepted:result.ok,unchanged:archivePayload()===before,timelineUnchanged:timeline===JSON.stringify([saveEpoch,saveTown,saveRevision,saveOrder]),treasuryDelta:G.treasury-cash,saveResult:await save(),publicExport:window.__townArchive.export()===null,reason:result.reason};
};'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
 results=[p.evaluate('kind=>__bridgeFence(kind)',kind) for kind in ['build','repair','decommission','road-retirement']];b.close()
print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':results},indent=2),flush=True)
assert all(not r['accepted'] and r['unchanged'] and r['timelineUnchanged'] and r['treasuryDelta']==0 and r['saveResult'] is False and r['publicExport'] for r in results),results
print('PASS paid road/bridge commands reject interrupted-day state without cash, topology or chronology mutation')
