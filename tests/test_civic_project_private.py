"""Private project route reuses the provider API and counts actual purchased learning.
Starting affordability/qualification conditions are a controlled fixture; invitation,
construction, fees, learning and project completion use the real operating model.
"""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();probe='''
window.__projectPrivateSetup=()=>{__townTest.reset('settlement',42);G.autoBuild=false;G.policy.privateServices=1;G.policy.educationBudget=0;G.policy.serviceVoucherBudget=100;for(const p of G.people)if(p.age>=18&&p.age<=60)p.skill=.6;G.policy.privateTuitionCap=4;__townTest.step(1);return totalMoney();};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_default_timeout(8000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();total=p.evaluate('__projectPrivateSetup()')
 state=lambda:p.evaluate('JSON.parse(__townTest.save())')
 p.locator('[data-civic-projects]').click();p.locator('[data-civic-project-review=skills]').click();p.get_by_text('Invite independent teaching',exact=True).click();adopted=state();assert adopted['civicProjects']['active']['skills']['branch']=='private'
 treasury=adopted['treasury'];p.locator('[data-private-invite=school]').click();invited=state();pending=[q for q in invited['projects'] if q.get('privateService')=='school'];assert pending and pending[0]['serviceEscrow']==6000
 assert invited['treasury']==treasury;assert abs(p.evaluate('__townTest.get().total')-total)<.001
 saved=p.evaluate('__townTest.save()');assert p.evaluate('(s)=>__townTest.load(s)',saved)
 p.evaluate('__townTest.step(240)');after=state();project=after['civicProjects']['active']['skills'];assert after.get('privateTrainingCompletions',0)>project['trainingBaseline'];assert project['learning']>=30,project
 assert project['status']=='complete',project
 assert not after.get('civicTrainingCompletions',0),'A public term must not be needed to finish the independent route'
 assert project['proof'] and 'fee-funded' in project['proof'];assert abs(p.evaluate('__townTest.get().total')-total)<.01;assert p.evaluate('__townTest.validate().ok');assert not errors,errors
 out=ROOT/'reports/civic-projects';out.mkdir(parents=True,exist_ok=True);(out/'private-route.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledStartingConditions':True,'actualInvitationAndOperatingModel':True,'municipalCapitalAtInvitation':invited['treasury']-treasury,'reservedPrivateWorkingCapital':pending[0]['serviceEscrow'],'privateTerms':after.get('privateTrainingCompletions',0),'project':project,'errors':errors},indent=2)+'\n');b.close()
print('PASS independently financed project invitation, real escrow/construction/fees, purchased household learning and private term certificate, no public-course requirement, save/restore and conserved cash')
