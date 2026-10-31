"""A mayor's reserved home survives ordinary immigration and private renewal."""
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
import json,hashlib
source=(ROOT/'assets/game.js').read_text();probe=r'''
window.__reserveLifecycle=()=>({day:G.day,treasury:G.treasury,total:totalMoney(),reserved:G.buildings.filter(b=>b.relocationReserve).map(b=>({id:b.id,kind:b.kind,owner:b.owner,title:b.title,hh:b.hh,occupied:G.households.filter(h=>h.home===b.id&&h.people.length).map(h=>h.id)})),pending:G.projects.filter(p=>p.municipalRehousing).map(p=>p.id),valid:validateTown()});
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1280,'height':800});p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('regional',42);__townTest.step()");start=p.evaluate('__reserveLifecycle()');p.locator('[data-panel=construction]').click();p.locator('#urbanPlanningOffice>summary').click();p.locator('[data-urban-rehousing]').click();p.locator('[data-event-choice="0"]').click();funded=p.evaluate('__reserveLifecycle()');assert funded['treasury']==start['treasury']-20000 and len(funded['pending'])==1
 rows=[]
 for quarter in range(4):
  p.evaluate('__townTest.step(90)');s=p.evaluate('__reserveLifecycle()');assert len(s['reserved'])==1 and s['reserved'][0]['id']==funded['pending'][0],s
  home=s['reserved'][0];assert home['kind']=='home' and home['owner']==-1 and home['title']['kind']=='municipal' and home['hh']==-1 and not home['occupied'],s
  assert s['valid']['ok'] and abs(s['total']-start['total'])<.1;assert p.evaluate('a=>__townTest.load(a)',p.evaluate('__townTest.save()')),'Occupied reserve corrupted archive';rows.append(s)
 b.close()
out=ROOT/'docs/previews/urban8/reservation-lifecycle.json';out.write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'authoredScenario':'regional seed42','normalImmigrationAndPrivateDevelopment':True,'samples':rows},indent=2)+'\n');print('PASS actual reserved-home authorisation survives a year of normal immigration, household formation, private investment and save restore')
