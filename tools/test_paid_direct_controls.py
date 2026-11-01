"""Actual direct panel controls: exact normal outcome and forced reservation refusal."""
from pathlib import Path
import ast,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text()
parsed=ast.parse((ROOT/'tools/test_root_transactions.py').read_text());base=next(ast.literal_eval(n.value) for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
bootstrap='\n'.join((ROOT/'experiments'/n).read_text() for n in ['root-capacity-api.js','game-capacity-root-adapter.js','paid-command-root.js'])+"\nwindow.__installGameCapacityRoot({oracleOnly:true,certifyReservations:()=>window.__denyDirect?{ok:false,reason:'Test capacity reservation refusal'}:{ok:true}});const rootAdmission=window.__installPaidCommandLayer();\n"
probe=r'''
window.__direct={
 prepare:async(action,enabled,deny)=>{window.__denyDirect=false;__rootTxTest.prep('construct',false,false);
  if(action==='land'){const p=ANNEX_PARCELS.find(p=>!G.charter.owned.includes(p.id)&&parcelAdjacent(p)),quote=parcelSurvey(p),add=Math.max(0,quote.price+10000-G.treasury);G.treasury+=add;G.region-=add;window.__directParcel=p.id;}
  if(action==='repay'){G.debt+=5000;G.treasury+=5000;G.region-=5000;}
  if(action==='private-provider'){G.policy.privateServices=1;G.policy.educationBudget=0;G.policy.defenseBudget=0;G.policy.privateTuitionCap=20;G.policy.privateFireFeeCap=5;G.serviceProvision=null;G.policy.businessRegulation=0;G.policy.commercialRate=0;G.policy.profitTax=0;for(const h of G.households){const add=Math.max(0,h.people.length*12000-h.cash);h.cash+=add;G.region-=add;}for(const p of G.people)if(p.age>=18&&p.age<=60)p.skill=.6;const teacher=G.people.find(p=>privateQualified(p,{privateService:'school'})&&!p.publicWork&&!p.previousPublicRole);if(!teacher)throw Error('No eligible teacher fixture');if(teacher.job>=0)G.firms[teacher.job].workers=G.firms[teacher.job].workers.filter(id=>id!==teacher.id);teacher.job=-1;}
  openPanel(action==='policy'?'policies':action==='private-provider'?'community':['ambition','named-place'].includes(action)?'agenda':action==='land'?'construction':action==='toggleDevelopment'?'construction':'treasury');
  if(action==='policy'){draftPolicy.incomeTax=G.policy.incomeTax+1;draftPolicy.healthBudget=G.policy.healthBudget+20;renderPanel('policies');}
  await __rootTxTest.drain();rootAdmission.enable(enabled);return {projects:G.projects.length,parcel:window.__directParcel};
 },
 capture:async deny=>{await __rootTxTest.drain();window.__denyDirect=deny;window.__directDialog=$('eventDialog').innerHTML;window.__directPending=pendingEvent;window.__directBefore=__rootTxTest.capture();window.__directDraft=draftPolicy;window.__directDraftText=JSON.stringify(draftPolicy);window.__directMarkup=$('panelBody').innerHTML;window.__directMoney=totalMoney();window.__directProjects=G.projects.length;window.__directMetrics=__gameCapacityRoot.metrics();return {projects:G.projects.length};
 },
 result:async(deny,enabled)=>{await __rootTxTest.drain();const metrics=__gameCapacityRoot.metrics(),s=window.__directBefore,status=rootAdmission.status(),unchanged=__rootTxTest.unchanged(s);if(Math.abs(totalMoney()-window.__directMoney)>.001)throw Error('Control created or destroyed cash');if(deny&&enabled&&(!unchanged||draftPolicy!==window.__directDraft||JSON.stringify(draftPolicy)!==window.__directDraftText||$('panelBody').innerHTML!==window.__directMarkup||$('eventDialog').innerHTML!==window.__directDialog||pendingEvent!==window.__directPending||status.last?.ok))throw Error('Direct control refusal changed committed state or draft/UI '+JSON.stringify({unchanged,status}));if(enabled&&(metrics.captures-window.__directMetrics.captures!==1||metrics.certificates-window.__directMetrics.certificates!==1))throw Error('Direct control did not use one shared root');const result={model:archiveLogicalPayload(),rng:rngState,projects:G.projects.length,projectsBefore:window.__directProjects,status,unchanged,referenceIdentity:deny&&enabled?unchanged:null,cashConserved:true};if(!deny&&!hydrateSave(archivePayload()))throw Error('Accepted direct control cannot self-import');return result;}
};
'''
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'productionEnabled':False,'reservationFaultInjection':True,'commonRoot':'__capacityAdmissionProtocol.shared','experiment_sha256':{n:hashlib.sha256((ROOT/'experiments'/n).read_bytes()).hexdigest() for n in ['root-capacity-api.js','game-capacity-root-adapter.js','paid-command-root.js']},'cases':[]}
selectors={'policy':'#enactPolicy','borrow':'#borrow','repay':'#repay','toggleDevelopment':'#toggleDevelopment','ambition':'[data-ambition]','private-provider':'[data-private-invite="school"]','land':'#eventChoices button','named-place':'#eventChoices button'}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 def page():
  p=b.new_page();p.route('http://direct-controls.test/**',lambda r:r.fulfill(status=200,content_type='text/html',body=html));p.goto('http://direct-controls.test/');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bootstrap+base+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__rootTxTest.drain()');return p
 def prepare(p,action,enabled,deny):
  value=p.evaluate('x=>__direct.prepare(x.action,x.enabled,false)',{'action':action,'enabled':enabled})
  if action=='land':
   p.locator('#charterOffice summary').first.click();p.locator('[data-parcel-buy="'+value['parcel']+'"]').click()
  if action=='named-place':
   p.locator('[data-public-place="square"]').click();p.locator('#publicPlaceName').fill('Marché du Port – Édifice 2026')
  if action=='toggleDevelopment':p.locator('#panelBody details').evaluate_all('(rows)=>rows.forEach(r=>r.open=true)')
  p.evaluate('x=>__direct.capture(x)',deny)
 for action,selector in selectors.items():
  states=[];samples=[]
  for enabled in [False,True]:
   p=page();prepare(p,action,enabled,False);p.locator(selector).first.click();r=p.evaluate('x=>__direct.result(false,x)',enabled);states.append((r.pop('model'),r['rng']));samples.append(r);p.close()
  assert states[0]==states[1],('Normal direct-control full model/RNG mismatch',action)
  if action=='private-provider':assert samples[1]['projects']>samples[1]['projectsBefore'],('Provider control did not create funded investment',samples)
  p=page();prepare(p,action,True,True);p.locator(selector).first.click();r=p.evaluate('__direct.result(true,true)');r.pop('model');p.close();out['cases'].append({'action':action,'exactNormalModelRng':True,'normal':samples,'forcedReservationRefusal':r});print('PASS',action,flush=True)
 b.close()
(ROOT/'reports/paid-direct-controls.json').write_text(json.dumps(out,indent=2));print('PASS all direct controls')
