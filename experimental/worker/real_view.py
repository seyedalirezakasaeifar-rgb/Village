from pathlib import Path
import sys,json,gzip,subprocess
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode()
bridge=Path('experimental/worker/real-view-bridge.js').read_text()+'''window.bridgeProbe={state:()=>({day:G.day,wage:G.policy.minWage,pop:G.stats.population,frozen:Object.isFrozen(G),construction:G.construction}),lot:()=>buildableCandidates('park').find(p=>canPlace(p.x,p.y,true,'park')),clear:()=>localStorage.removeItem('worker-prototype-test-slot')};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://worker-real.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://worker-real.test/');p.add_script_tag(content=Path('assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js',bridge+'// SOURCE: 99-instrumentation.js'))
 p.evaluate('''async args=>{window.real=await __workerRealView.enable(args.code,args.archive);}''',{'code':Path('experimental/worker/model.generated.js').read_text(),'archive':archive})
 initial=p.evaluate('bridgeProbe.state()');assert initial['frozen']
 p.locator('[data-worker="step"]').click();p.wait_for_function('bridgeProbe.state().day===41682')
 p.locator('[data-worker="policy"]').click();p.wait_for_function('v=>bridgeProbe.state().wage===v',arg=initial['wage']+1)
 lot=p.evaluate('bridgeProbe.lot()');assert lot
 built=p.evaluate('p=>real.command({type:"build",kind:"park",x:p.x,y:p.y})',lot);assert built['built']
 bid=built['model']['buildings'][-1]['id'];inspection=p.evaluate('id=>real.inspect(id)',bid);assert inspection['inspection']['kind']=='park'
 p.locator('[data-worker="council"]').click();p.locator('[data-worker-choice]').last.click();p.wait_for_function("document.getElementById('eventDialog').style.display==='none'")
 p.locator('[data-worker="save"]').click();p.wait_for_function("window.workerRealLastSaveAck?.persisted===true");saved=p.evaluate("JSON.parse(localStorage.getItem('worker-prototype-test-slot'))");assert saved['day']==41682
 # Unsupported production action is visibly rejected rather than mutating stale G.
 before=p.evaluate('bridgeProbe.state()');p.locator('#newTown').click(force=True);assert p.evaluate('bridgeProbe.state()')==before
 p.evaluate('bridgeProbe.clear()');assert not errors,errors
 Path('experimental/worker/real-view-proof.json').write_text(json.dumps({'realRendererFrozenSnapshot':True,'trustedStepPolicyCouncilSaveButtons':True,'actualConstructionAndInspection':True,'unsupportedNewTownBlocked':True,'sourceEpochLoadAvailable':True,'day':saved['day'],'errors':errors,'limitations':['Paused opt-in integration only','Real build function tested via bridge command, not pointer placement trace','Full view snapshots currently required; projection schema incomplete','Unsupported controls explicitly blocked; not a release candidate','Save uses test-only slot; no production envelope/native certification']},indent=2));print('PASS real readonly map, day/policy controls, build/inspect and acknowledged test save');b.close()
