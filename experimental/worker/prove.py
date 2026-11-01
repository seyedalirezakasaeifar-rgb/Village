from pathlib import Path
import sys,json
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
root=Path('.')
def model(g):
 return {k:v for k,v in g.items() if k not in ('trafficState','visualState')}

with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 p=b.new_page();p.set_content(html);p.add_script_tag(content=(root/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js', '''save=()=>true;window.workerOracle={climate:(key,value)=>{changePreference(key,value);G.rngState=rngState;return JSON.parse(JSON.stringify(G));},package:values=>{draftPolicy=values;enactPolicyPackage();G.rngState=rngState;return JSON.parse(JSON.stringify(G));},step:n=>{for(let i=0;i<n;i++)tick();G.rngState=rngState;return JSON.parse(JSON.stringify(G));},policy:(key,value)=>{const old=G.policy[key];G.policy[key]=value;journalPolicy(key,old,value);recompute();}};
// SOURCE: 99-instrumentation.js'''));p.locator('#newTown').click();p.locator('#pause').click()
 archive=p.evaluate('__townTest.save()')
 code=(root/'experimental/worker/model.generated.js').read_text()
 p.evaluate('''code=>{window.w=new Worker(URL.createObjectURL(new Blob([code],{type:'application/javascript'})));window.workerErrors=[];w.onerror=e=>workerErrors.push(e.message);let serial=0,epoch=0,command=0;window.ask=m=>new Promise((resolve,reject)=>{const id=++serial;const h=e=>{if(e.data.id===id){w.removeEventListener('message',h);if(e.data.ok)epoch=e.data.result.epoch;resolve(e.data);}};w.addEventListener('message',h);w.postMessage({epoch,command:++command,...m,id});setTimeout(()=>reject(Error(JSON.stringify(workerErrors))),10000);});}''',code)
 result=p.evaluate("a=>ask({type:'load',archive:a})",archive);assert result['ok'],result
 result=p.evaluate("ask({type:'step',days:31})");assert result['ok'],result
 oracle=p.evaluate('workerOracle.step(31)');assert model(oracle)==model(result['result']['model']),[(k,str(oracle[k])[:100],str(result['result']['model'].get(k))[:100]) for k in oracle if oracle[k]!=result['result']['model'].get(k)]
 value=oracle['policy']['minWage']+1
 command=p.evaluate("v=>ask({type:'policy',key:'minWage',value:v})",value);assert command['ok'],command
 p.evaluate("v=>workerOracle.policy('minWage',v)",value)
 result=p.evaluate("ask({type:'step',days:30})");assert result['ok'],result
 oracle=p.evaluate('workerOracle.step(30)');assert model(oracle)==model(result['result']['model']),[(k,str(oracle[k])[:100],str(result['result']['model'].get(k))[:100]) for k in oracle if oracle[k]!=result['result']['model'].get(k)]
 packaged=p.evaluate("ask({type:'policy-package',values:{healthBudget:123.45,educationBudget:234.56}})");assert packaged['ok'] and packaged['result']['enacted'],packaged
 oracle=p.evaluate('values=>workerOracle.package(values)',{'healthBudget':123.45,'educationBudget':234.56});assert model(oracle)==model(packaged['result']['model']),'Actual policy-package parity differs'
 for key in ['seasons','weather']:
  changed=p.evaluate("key=>ask({type:'climate',key,value:true})",key);assert changed['ok'],changed
  oracle=p.evaluate('key=>workerOracle.climate(key,true)',key);assert model(oracle)==model(changed['result']['model']),'Climate source parity differs'
 exported=p.evaluate("ask({type:'export'})");assert exported['ok'] and model(json.loads(exported['result']['archive']))==model(oracle)
 stale=p.evaluate("ask({type:'choice',eventId:-1})");assert not stale['ok'] and 'Stale' in stale['error']
 receipt={'days':61,'exactFullModel':True,'exactRng':True,'policyCommand':True,'actualPolicyPackageEvidenceExact':True,'actualClimateFunctionParity':True,'exportHandshake':True,'staleRejected':True,'day':oracle['day'],'outbox':result['result']['outbox']}
 timing=p.evaluate("""async()=>{async function sample(work){let gaps=[],last=performance.now();const timer=setInterval(()=>{const t=performance.now();gaps.push(t-last);last=t;},8);await new Promise(r=>setTimeout(r,20));const t=performance.now();await work();const ms=performance.now()-t;await new Promise(r=>setTimeout(r,20));clearInterval(timer);return {ms,daysPerSecond:60*1000/ms,maxMainTimerGap:Math.max(...gaps)};}const sync=await sample(()=>workerOracle.step(60));const worker=await sample(()=>ask({type:'step',days:60}));return {sync,worker};}""")
 receipt['timing']=timing
 import hashlib
 receipt['sourceSha256']=hashlib.sha256((root/'assets/game.js').read_bytes()).hexdigest()
 receipt['visualEnvelopeExcluded']=['trafficState','visualState']
 Path('experimental/worker/proof.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
 b.close()
