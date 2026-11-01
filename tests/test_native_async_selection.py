"""Real archive UI routing stays synchronous without an opt-in endpoint."""
import hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text()
probe=r'''window.__nativeSelection=mode=>{const calls=[],before=archivePayload(),rng=rngState;window.AndroidArchive={writeBackup:a=>calls.push({method:'syncExport',archive:a}),openBackup:()=>calls.push({method:'syncImport'})};delete window.__workerArchiveAsync;if(mode!=='oldApk'){AndroidArchive.requestWorkerExport=()=>calls.push({method:'asyncExport'});AndroidArchive.requestWorkerImport=()=>calls.push({method:'asyncImport'});}if(mode==='endpoint'||mode==='oldApk')window.__workerArchiveAsync={status:()=>({epoch:0}),submit:()=>({accepted:true})};if(mode==='failed')simulationTickFailed=true;try{exportSave();importSave()}finally{simulationTickFailed=false;}const unchanged=before===archivePayload()&&rng===rngState;return {calls,unchanged,exportArchiveExact:calls.some(c=>c.method==='syncExport')?calls.find(c=>c.method==='syncExport').archive===before:null}};'''
rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for mode in ['absent','endpoint','oldApk','failed']:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('m=>__nativeSelection(m)',mode);p.close();methods=[c['method']for c in r['calls']];expected=['asyncExport','asyncImport']if mode=='endpoint'else['syncImport']if mode=='failed'else['syncExport','syncImport'];assert methods==expected and r['unchanged'],(mode,r)
  if mode in ['absent','oldApk']:assert r['exportArchiveExact']
  rows.append({'mode':mode,'methods':methods,'completeArchiveAndRngUnchanged':r['unchanged'],'exportArchiveExact':r['exportArchiveExact']})
 b.close()
print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':rows,'scope':'Injected Android interfaces verify browser dispatch only; no Worker, Android picker or durable native callback is emulated.'},indent=2))
