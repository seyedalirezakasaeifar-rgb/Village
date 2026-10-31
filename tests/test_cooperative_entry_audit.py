"""Adversarial entry audit. Negative findings are recorded, not hidden as passes."""
import ast,json,hashlib
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text()
tree=ast.parse((ROOT/'tests/test_cooperative_barriers.py').read_text())
probe=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe+=r'''
window.__entryAudit={
 detail:()=>({busy:cooperativeDayBusy(),working:G.day,committed:cooperativeLastCommittedDay(),policy:G.policy.minWage,queue:cooperativeCommands.length,modal:$('eventDialog').style.display,pending:!!pendingEvent}),
 openPetition:()=>{offerCouncilEvent();},
 stale:()=>{const b=document.createElement('button');b.id='entryAuditStale';b.textContent='audit';document.body.appendChild(b);b.click();b.remove();return cooperativeCommands.length;},
 drag:()=>{for(let i=0;i<500;i++)cv.dispatchEvent(new PointerEvent('pointermove',{bubbles:true,pointerId:123,pointerType:'touch',clientX:i,clientY:100}));return cooperativeCommands.length;}
};
'''
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'prototype_commit':'d997da1','cases':{}}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);
 for case in ['publicRead','publicMutation','publicStep','publicModal','staleControl','dragFlood','nativeExport','nativeResume','pause']:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__coopBarrier.prepare()');p.evaluate('__entryAudit.openPetition()');p.evaluate('__coopBarrier.hold()');before=p.evaluate('__entryAudit.detail()')
  if case=='publicRead':result=p.evaluate('__townTest.get()');finding=result['day']!=before['committed']
  elif case=='publicMutation':p.evaluate("__townTest.set('minWage',73)");result=p.evaluate('__entryAudit.detail()');finding=result['policy']==73 and result['busy']
  elif case=='publicStep':p.evaluate('__townTest.step(1)');result=p.evaluate('__entryAudit.detail()');finding=result['working']>before['working'] and result['busy']
  elif case=='publicModal':p.evaluate('__townTest.reviewPetition(0)');result=p.evaluate('__entryAudit.detail()');finding=result['pending'] and result['busy']
  elif case=='staleControl':p.evaluate('__entryAudit.stale()');p.evaluate('__coopBarrier.release()');result=p.evaluate('__cooperativeSimulation.samples().commands');finding=False;assert any(x['status']=='declined' for x in result),result
  elif case=='dragFlood':result=p.evaluate('__entryAudit.drag()');finding=result>=500
  elif case=='nativeExport':result=p.evaluate('__townArchive.export()');assert not p.evaluate('__entryAudit.detail().busy');result={'committed':True};finding=False
  elif case=='nativeResume':p.evaluate('__townArchive.resume()');result=p.evaluate('__entryAudit.detail()');finding=False
  else:p.locator('#pause').click();result=p.evaluate('({state:__entryAudit.detail(),markup:document.querySelector("#pause").innerHTML})');finding='<svg' not in result['markup']
  out['cases'][case]={'before':before,'result':result,'needsAttention':bool(finding)};p.close()
 b.close()
path=ROOT/'reports/cooperative-entry-audit.json';path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v['needsAttention'] for k,v in out['cases'].items()},indent=2))
