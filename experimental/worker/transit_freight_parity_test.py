"""Disabled worker family: normal-resource paid import/recall and depot salvage parity."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text();bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js'])
hook='''paused=true;window.parity={setup:()=>{seed(42);pendingEvent=null;const f=G.firms.find(f=>!f.closed&&formulas[f.kind]?.out==='grain'),m=OUTSIDE_MARKETS[0],before=totalMoney(),q=regionalQuote(f,m,'grain','import');if(dispatchRegional(f,'grain',10,'import',q)!==10)throw Error('Normal funded import failed');const lot=buildableCandidates('business').find(p=>canPlace(p.x,p.y,true,'transit_depot')),depot=lot&&buildTransitFacility('transit_depot',lot.x,lot.y);if(!depot)throw Error('Ordinary treasury depot unavailable');window.targets={cargo:ensureRegionalTrade().shipments.slice(-1)[0].id,site:depot.id};if(Math.abs(totalMoney()-before)>.0001)throw Error('Fixture money drift');recompute();return archivePayload();},load:a=>{if(!hydrateSave(a))throw Error('Load refused');pendingEvent=null;},state:()=>JSON.parse(archivePayload()),click:(action,id)=>{const b=document.createElement('button');if(action==='remove-site'){b.dataset.transitAction=action;b.dataset.site=id;$('panelBody').appendChild(b);}else{b.dataset.logisticsCancel=id;document.body.appendChild(b);}b.click();b.remove();},check:()=>({money:totalMoney(),goods:goodsBalance(),valid:validateTown()})};\n'''
def clean(g):
 for k in ['visualState','trafficState']:g.pop(k,None)
 return g
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for worker in [False,True]:
  p=b.new_page();p.route('http://parity.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://parity.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',(bridge if worker else '')+hook+'// SOURCE: 99-instrumentation.js'));pages.append(p)
 oracle,p=pages;archive=oracle.evaluate('parity.setup()');targets=oracle.evaluate('targets');p.evaluate('''async a=>window.real=await __workerRealView.enable(a.code,a.archive,{initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':code,'archive':archive})
 normalized=p.evaluate('real.command({type:"export"})')['archive'];oracle.evaluate('a=>parity.load(a)',normalized)
 rows=[]
 oracle.evaluate('id=>parity.click("remove-site",id)',targets['site']);reply=p.evaluate('id=>real.command({type:"route",module:"transit-freight",operation:"remove-site",payload:{id}})',targets['site']);expected=clean(oracle.evaluate('parity.state()'));actual=clean(reply['model']);assert actual==expected,[(k,str(expected.get(k))[:250],str(actual.get(k))[:250]) for k in set(actual)|set(expected) if actual.get(k)!=expected.get(k)];rows.append('normal-funded depot removal exact model/RNG')
 oracle.evaluate('id=>parity.click("cancel",id)',targets['cargo']);oracle.locator('[data-event-choice="0"]').click()
 review=p.evaluate('id=>real.command({type:"route",module:"transit-freight",operation:"cargo-cancel-review",payload:{id}})',targets['cargo']);event=next(e['payload'] for e in review['outbox'] if e['type']=='council-event');reply=p.evaluate('id=>real.command({type:"choice",eventId:id,index:0})',event['id']);assert clean(reply['model'])==clean(oracle.evaluate('parity.state()')),'Recall full-model mismatch';rows.append('paid import recall exact model/RNG')
 check=oracle.evaluate('parity.check()');assert check['valid']['ok'];assert max(abs(x['error']) for x in check['goods'])<.001
 Path('experimental/worker/transit-freight-parity-proof.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'ordinaryResources':True,'oracleActualUi':True,'workerActualUi':False,'exact':rows,'accounting':check},indent=2)+'\n');print('PASS',rows);b.close()
