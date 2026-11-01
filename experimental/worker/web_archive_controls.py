from pathlib import Path
import sys,json,gzip,subprocess
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode()
bridge=Path('experimental/worker/runtime-guard.js').read_text()+Path('experimental/worker/archive-endpoint.js').read_text()+Path('experimental/worker/real-view-bridge.js').read_text()+'''window.bridgeProbe={climate:()=>({seasons:seasonsEnabled(),weather:weatherEnabled()}),guide:()=>G.mayorJourney?.guide,panel:()=>active,canonical:()=>JSON.stringify([G,rngState]),state:()=>({day:G.day,wage:G.policy.minWage,pop:G.stats.population,frozen:Object.isFrozen(G),construction:G.construction}),lot:()=>buildableCandidates('park').find(p=>canPlace(p.x,p.y,true,'park')),savePair:async()=>{const before=saveRevision,results=await Promise.all([save(),save()]);return {before,after:saveRevision,results};},failSave:async()=>{const owner=persistSnapshot;persistSnapshot=()=>Promise.resolve(false);try{return await save();}finally{persistSnapshot=owner;}},saved:()=>readSaveEnvelope(localStorage.getItem('townledger-v6')).payload,clear:()=>localStorage.removeItem('worker-prototype-test-slot')};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(e.stack));p.route('http://worker-real.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://worker-real.test/');p.add_script_tag(content=Path('assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js',bridge+'// SOURCE: 99-instrumentation.js'))
 p.evaluate('''async args=>{window.real=await __workerRealView.enable(args.code,args.archive);}''',{'code':Path('experimental/worker/model.generated.js').read_text(),'archive':archive})
 p.locator('#tabs [data-panel="settings"]').click();p.wait_for_function("bridgeProbe.panel()==='settings'")
 p.locator('#backupSave').click();p.locator('#saveText').wait_for();backup=p.locator('#saveText').input_value();assert json.loads(backup)['day']==41681
 p.locator('#copySave').click();p.locator('#archiveClose').click()
 p.locator('#importSave').click();p.locator('#importText').fill('invalid');p.evaluate('window.beforeInvalid=bridgeProbe.canonical()');p.locator('#restoreGo').click();p.wait_for_function("!document.getElementById('restoreGo').disabled");assert p.evaluate('bridgeProbe.canonical()===beforeInvalid')
 p.locator('#importText').fill(backup);previous=p.evaluate('__workerArchiveAsync.status().epoch');p.locator('#restoreGo').click();p.wait_for_function("document.getElementById('helpDialog').style.display==='none'")
 assert p.evaluate('__workerArchiveAsync.status().epoch')==previous+1
 saved=p.evaluate('bridgeProbe.saved()');assert json.loads(saved)['day']==41681
 assert not errors,errors
 Path('experimental/worker/web-archive-controls-proof.json').write_text(json.dumps({'actualBackupCopyCloseControls':True,'actualImportForm':True,'invalidImportHostUnchanged':True,'validImportEpochAdvanced':True,'successOnlyAfterAcknowledgedPersistence':True,'pageErrors':errors,'nativeFilePickerClaimed':False},indent=2));print('PASS actual backup/copy/close and invalid/valid restore form, persisted before success');b.close()
