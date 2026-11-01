"""Current actual council choices: baseline versus shared host test owner, not production composition."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
names=['root-capacity-api.js','paid-command-root.js'];source=(ROOT/'assets/game.js').read_text()
bootstrap='\n'.join((ROOT/'experiments'/n).read_text() for n in names)+'\n'+(ROOT/'tools/fixtures/current-paid-owner.js').read_text()+"\nwindow.__gameCapacityRoot=window.__installCurrentPaidTestOwner();const rootAdmission=window.__installPaidCommandLayer();\n"+(ROOT/'tools/fixtures/current-paid-fixture.js').read_text()
probe=r'''
window.__currentCouncil={list:()=>COUNCIL_EVENTS.map(e=>({title:e.title,count:e.choices.length})),open:async(i,enabled)=>{await __rootTxTest.drain();__rootTxTest.prep('construct',false,false);rootAdmission.enable(enabled);window.__councilReceipt=JSON.stringify(G.serviceCashEvidence);const e=COUNCIL_EVENTS[i];showCustomEvent(e.type,e.title,e.text,e.choices);await __rootTxTest.drain();},result:async()=>{await __rootTxTest.drain();if(JSON.stringify(G.serviceCashEvidence)!==window.__councilReceipt)throw Error('Completed-day service payments rewritten');const model=archivePayload(),rng=rngState;if(!hydrateSave(model))throw Error('Council outcome cannot reload');const normalized=archivePayload();if(!hydrateSave(normalized)||archivePayload()!==normalized)throw Error('Council normalized archive not fixed');return {model,rng,normalized,valid:validateTown()};}};
'''
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'runtime_sha256':{n:hashlib.sha256((ROOT/'experiments'/n).read_bytes()).hexdigest() for n in names},'hostTestOwnerOnly':True,'productionComposition':False,'cases':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 def page():
  p=b.new_page();p.route('http://current-council.test/**',lambda r:r.fulfill(status=200,content_type='text/html',body=html));p.goto('http://current-council.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bootstrap+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__rootTxTest.drain()');return p
 left,right=page(),page();events=left.evaluate('__currentCouncil.list()')
 for i,e in enumerate(events):
  for j in range(e['count']):
   values=[]
   for p,enabled in [(left,False),(right,True)]:
    p.evaluate('x=>__currentCouncil.open(x.i,x.enabled)',{'i':i,'enabled':enabled});p.locator('[data-event-choice="'+str(j)+'"]').click();r=p.evaluate('__currentCouncil.result()');assert r['valid']['ok'],(e,j,r['valid']);values.append((r['model'],r['rng'],r['normalized']))
   assert values[0]==values[1],('Current council full model/RNG/normalized mismatch',e,j)
   out['cases'].append({'event':e['title'],'choice':j,'exactModelRngAndNormalized':True,'completedPaymentsPreserved':True})
 left.close();right.close();b.close()
(ROOT/'reports/current-paid-council.json').write_text(json.dumps(out,indent=2));print('PASS',len(out['cases']),'current actual council choices with exact model/RNG/normalized reload and receipts')
