import os
"""Actual original669 direct controls versus one-root serializable worker family."""
from pathlib import Path
import sys,json,subprocess,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
oracleCommit=os.environ.get('WORKER_ORACLE_COMMIT','669c908706af997375680674390e46fd132a970a');original=subprocess.check_output(['git','show',oracleCommit+':assets/game.js']).decode();source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text();bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js'])
hook='''paused=true;window.directProbe={fixture:()=>{seed(42);G.treasury+=10000;G.region-=10000;pendingEvent=null;active='treasury';return archivePayload();},load:a=>{G=JSON.parse(a);rngState=G.rngState;const metrics=G.roadMetrics;invalidateRoads();G.roadMetrics=metrics;pendingEvent=null;active='treasury';},apply:m=>{const b=document.createElement('button');b.id=m.control;if(m.control==='ambition')b.dataset.ambition=m.ambition;if(m.control==='enactPolicy')draftPolicy={...m.values};$('panelBody').appendChild(b);b.click();b.remove();return JSON.parse(archivePayload());},ambition:()=>AMBITIONS[1].id};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[];errors=[]
 for kind,src in [('oracle',original),('worker',source)]:
  p=b.new_page();p.route('http://direct.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://direct.test/');p.on('pageerror',lambda e:errors.append(str(e)));p.add_script_tag(content=src.replace('// SOURCE: 99-instrumentation.js',(bridge if kind=='worker' else '')+hook+'// SOURCE: 99-instrumentation.js'));pages.append(p)
 oracle,p=pages;archive=oracle.evaluate('directProbe.fixture()');oracle.evaluate('a=>directProbe.load(a)',archive);p.evaluate('''async a=>window.real=await __workerRealView.enable(a.code,a.archive,{initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':code,'archive':archive});p.evaluate('real.command({type:"prepare-panel",panel:"treasury",context:{selected:null,people:"all",firms:"all",query:"",category:"all",draft:{},transitRoute:null}})')
 operations=[{'control':'borrow'},{'control':'repay'},{'control':'toggleDevelopment'},{'control':'toggleDevelopment'},{'control':'ambition','ambition':oracle.evaluate('directProbe.ambition()')},{'control':'enactPolicy','values':{'minWage':14}}];rows=[]
 for m in operations:
  expected=oracle.evaluate('m=>directProbe.apply(m)',m);reply=p.evaluate('m=>real.command({type:"panel-control",...m})',m);actual=reply['model']
  for key in ['visualState','trafficState']:actual.pop(key,None);expected.pop(key,None)
  assert actual==expected,m
  assert reply['paid']['committed'];rows.append(m);p.evaluate('real.settleSaves()')
 before=p.evaluate('real.command({type:"export"})')['archive']
 for m in [{'control':'unknown'},{'control':'ambition','ambition':'arbitrary'},{'control':'enactPolicy','values':{'minWage':1e99}},{'control':'enactPolicy','values':{}},{'control':'enactPolicy','values':{'minWage':14}}]:
  result=p.evaluate('m=>real.command({type:"panel-control",...m}).then(()=>false,e=>e.message)',m);assert result;assert p.evaluate('real.command({type:"export"})')['archive']==before
 assert not errors,errors
 Path('experimental/worker/direct-family-proof.json').write_text(json.dumps({'productionEnabled':False,'oracleCommit':oracleCommit,'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'operationsExactFullModelRng':rows,'invalidOrNoopDtosRefuseUnchanged':5,'pageErrors':errors},indent=2)+'\n');print('PASS six direct operations exact original669 model/RNG; five invalid/no-op DTOs refuse unchanged');b.close()
