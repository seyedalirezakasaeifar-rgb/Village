"""Standalone sync header equivalence and scoped strict persistence validation."""
from pathlib import Path
import sys,json,subprocess,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];base=subprocess.check_output(['git','show','87811c5:assets/game.js'],text=True);fixed=(R/'assets/game.js').read_text();out=R/'reports/sync-header-save';out.mkdir(exist_ok=True,parents=True)
hook=r'''
let syncValidatorCalls=0,syncSnapshotCalls=0;const strictSyncRead=readSaveEnvelope,fullSyncSnapshot=economySnapshot;readSaveEnvelope=v=>{syncValidatorCalls++;return strictSyncRead(v);};economySnapshot=(...a)=>{syncSnapshotCalls++;return fullSyncSnapshot(...a);};
window.syncGate={seed:n=>{seed(n);paused=true;pendingEvent=null;return archivePayload();},header:(text,n)=>{G=JSON.parse(text);rngState=G.rngState;const input=[{foodDisconnected:2,unmetFood:999,hardship:70,employment:30},{foodDisconnected:0,unmetFood:999,hardship:70,employment:30},{foodDisconnected:0,unmetFood:0,hardship:70,employment:30},{foodDisconnected:0,unmetFood:0,hardship:0,employment:30},{foodDisconnected:0,unmetFood:0,hardship:0,employment:99}][n];Object.assign(G.market,input);Object.assign(G.stats,{hardship:input.hardship,employment:input.employment});const before=archivePayload(),beforeRng=rngState;liveStatusTown=null;syncSnapshotCalls=0;updateHeader();if(archivePayload()!==before||rngState!==beforeRng)throw Error('Header mutated model/RNG');return {text:[$('marketHeadline').textContent,$('marketDetail').textContent],archive:archivePayload(),snapshotCalls:syncSnapshotCalls};},prepare:(text,corrupt)=>{const backup=JSON.stringify(saveEnvelope(text)),primary=JSON.stringify(saveEnvelope(text));localStorage.setItem('townledger-v6-backup',backup);localStorage.setItem('townledger-v6',corrupt?primary.replace('"checksum":"','"checksum":"BAD'):primary);syncValidatorCalls=0;return backup;},persist:async text=>{const identity=readSaveEnvelope,p=persistSnapshot(text,saveEpoch),syncCalls=syncValidatorCalls,ok=await p,calls=syncValidatorCalls,stored=readSaveEnvelope(localStorage.getItem('townledger-v6'));return {ok,syncCalls,validatorUnchanged:identity===readSaveEnvelope,freshRead:syncValidatorCalls===calls+1,payloadExact:stored?.payload===text,order:stored?.order,backup:localStorage.getItem('townledger-v6-backup')};}};
'''
rows=[];saves=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for code in [base,fixed]:
  p=b.new_page();p.route('http://sync-gate.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://sync-gate.test/');p.evaluate('window.requestAnimationFrame=()=>0');p.add_script_tag(content=code.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'));pages.append(p)
 for seed in [42,91,909]:
  archive=pages[0].evaluate('syncGate.seed',seed);pages[1].evaluate('syncGate.seed',seed)
  for n in range(5):
   pair=[p.evaluate('v=>syncGate.header(v.text,v.n)',{'text':archive,'n':n}) for p in pages];assert pair[0]['text']==pair[1]['text'];assert json.loads(pair[0]['archive'])==json.loads(pair[1]['archive']);assert pair[1]['snapshotCalls']==(0 if n<4 else 1);rows.append({'seed':seed,'branch':n,'text':pair[1]['text'],'exactModelRng':True,'fullSnapshotCallsBase':pair[0]['snapshotCalls'],'fullSnapshotCallsCandidate':pair[1]['snapshotCalls']})
 for variant,p in zip(['base','candidate'],pages):
  archive=p.evaluate('syncGate.seed',42)
  for corrupt in [False,True]:
   backup=p.evaluate('v=>syncGate.prepare(v.text,v.corrupt)',{'text':archive,'corrupt':corrupt});r=p.evaluate('syncGate.persist',archive);assert r['ok'] and r['validatorUnchanged'] and r['freshRead'] and r['payloadExact'];assert r['syncCalls']==(3 if variant=='base' else 2),r
   if corrupt:assert r['backup']==backup
   r.pop('backup');saves.append({'variant':variant,'corruptPrimary':corrupt,**r})
 b.close()
(out/'functional.json').write_text(json.dumps({'baseSHA256':hashlib.sha256(base.encode()).hexdigest(),'candidateSHA256':hashlib.sha256(fixed.encode()).hexdigest(),'syntheticHeaderInputs':True,'headers':rows,'strictPersistence':saves,'workerEnabled':False},indent=2)+'\n');print('PASS 15 exact model/RNG header cases; valid/corrupt backup chronology and strict fresh persistence readback')
