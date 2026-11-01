"""Actual-model registration example and fail-closed unknown/schema command gates."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text();bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js']);hook='''paused=true;window.moduleFixture=()=>{seed(42);pendingEvent=null;return archivePayload();};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('http://route.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://route.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bridge+hook+'// SOURCE: 99-instrumentation.js'));archive=p.evaluate('moduleFixture()');p.evaluate('''async a=>window.real=await __workerRealView.enable(a.code,a.archive,{initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':code,'archive':archive})
 rows=[]
 for operation,value,control,attribute in [('routing','river','routing','routePreference'),('priority','essentials','priority','priority'),('routing','automatic','routing','routePreference'),('priority','balanced','priority','priority')]:
  reply=p.evaluate('m=>real.command({type:"route",module:"transit-freight",...m})',{'operation':operation,'payload':{'value':value}})
  assert reply['paid']['committed'];assert reply['model']['regionalTrade'][attribute]==value
  frozen=p.evaluate('real.command({type:"export"})')['archive']
  for payload in [{'value':value},{'value':'invalid'},{'value':value,'extra':True}]:
   result=p.evaluate('m=>real.command({type:"route",module:"transit-freight",...m}).then(()=>false,e=>e.message)',{'operation':operation,'payload':payload});assert result
   assert p.evaluate('real.command({type:"export"})')['archive']==frozen
  rows.append({'operation':operation,'value':value,'duplicateAndSchemaRollback':True})
 for operation,payload in [('retire',{'id':999999}),('remove-site',{'id':999999}),('remove-guideway',{}),('stop-relief',{})]:
  frozen=p.evaluate('real.command({type:"export"})')['archive'];result=p.evaluate('m=>real.command({type:"route",module:"transit-freight",...m}).then(()=>false,e=>e.message)',{'operation':operation,'payload':payload});assert result
  assert p.evaluate('real.command({type:"export"})')['archive']==frozen
 assert not errors,errors
 Path('experimental/worker/transit-freight-proof.json').write_text(json.dumps({'productionEnabled':False,'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'operations':rows,'absentTargetsRollback':4,'actualUiTested':False,'pageErrors':errors},indent=2)+'\n');print('PASS transit/freight direct DTO routing and unchanged refusals');b.close()
