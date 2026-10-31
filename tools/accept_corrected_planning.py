#!/usr/bin/env python3
"""Bounded actual-control followup; no injected resources or forced economic success."""
import json,gzip,hashlib,time,functools,http.server,threading
from playwright.sync_api import sync_playwright
from audit_economic_play import ROOT,PROBE,Quiet
SOURCE=(ROOT/'assets/game.js').read_text();SHA=hashlib.sha256(SOURCE.encode()).hexdigest();OUT=ROOT/'reports/corrected-planning';OUT.mkdir(parents=True,exist_ok=True)
EXTRA='''window.__corrected={plan:()=>districtFollowthroughPlan(G.civicProjects.active.district),point:(x,y)=>{const a=iso(x,y),r=cv.getBoundingClientRect();return{x:r.left+cw/2+(a[0]-cam.x)*cam.zoom,y:r.top+ch/2+(a[1]+18-cam.y)*cam.zoom};},ports:()=>G.firms.filter(f=>f.kind==='wharf').map(f=>({id:f.id,cash:f.cash,closed:f.closed,workers:workingStaff(f).length,expense:f.expenses,fees:f.handlingFees,cargo:f.cargoToday})),shipments:()=>G.regionalTrade};'''

def run(pw,url,kind):
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_default_timeout(6000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(status=200,content_type='application/javascript',body=SOURCE.replace('// SOURCE: 99-instrumentation.js',PROBE+EXTRA+'\n// SOURCE: 99-instrumentation.js')));p.goto(url+'/assets/index.html');p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();result={'candidate':'23f0b19','source_sha256':SHA,'strategy':kind,'actions':[],'observations':[],'errors':errors,'method':'Fresh UI town, ordinary credit/purchases/routing and ticks; no grants or forced workers. Automation time is not human play time.'};start=time.monotonic();facts=lambda:p.evaluate('__playAudit.facts()');initial=facts()['total']
 def panel(tab):
  if p.locator('#panel').evaluate('e=>e.classList.contains("show")')and'active'in(p.locator('[data-panel='+tab+']').get_attribute('class')or''):return
  p.locator('[data-panel='+tab+']').click()
 def board():panel('overview');p.locator('[data-civic-projects]').click()
 def confirm():p.locator('[data-event-choice="0"]').click()
 def action(label,fn):
  a=facts()
  try:detail=fn();status='executed; inspect state deltas'
  except Exception as e:detail=str(e).split('Call log:')[0];status='blocked/uncertain; post-state retained';p.keyboard.press('Escape')
  c=facts();result['actions'].append({'label':label,'day':a['day'],'cashDelta':c['treasury']-a['treasury'],'debtDelta':c['debt']-a['debt'],'populationDelta':c['population']-a['population'],'detail':detail,'status':status,'toast':p.locator('#toast').inner_text()});print(kind,a['day'],label,status,flush=True)
 def advance(target):
  while facts()['day']<target:
   r=p.evaluate('n=>__playAudit.advance(n)',min(30,target-facts()['day']))
   if r['pending']:p.locator('#eventDefer').click()
 def observe(label):
  result['observations'].append({'label':label,'facts':facts(),'ports':p.evaluate('__corrected.ports()'),'trade':p.evaluate('__corrected.shipments()')});board();p.screenshot(path=str(OUT/(kind+'-'+label+'.png')))
 def direction(d):panel('agenda');el=p.locator('[data-mayor-direction='+d+']');el.evaluate('e=>e.closest("details").open=true');el.click();confirm()
 def district(parcel,focus):
  board();p.locator('[data-civic-project-review=district]').click();p.locator('#projectParcel').select_option(parcel);p.locator('#projectFocus').select_option(focus);p.locator('#projectDistrictAdopt').click();p.locator('[data-civic-project-deed]').click();confirm();p.locator('[data-civic-project-charter]').click();confirm();p.locator('[data-civic-project-road]').click();confirm()
 def pilot(name):board();p.locator('[data-civic-project-build='+name+']').click();confirm()
 def route(mode):panel('economy');p.locator('#logisticsOffice').evaluate('e=>e.open=true');p.locator('[data-logistics-routing='+mode+']').click()
 action('Choose direction before the work begins',lambda:direction('river'if kind=='port'else'community'));advance(32)
 if kind=='port':
  observe('existing-roles-not-new-work');action('Buy river tract and complete its paired purpose street quote',lambda:district('river-reach','waterfront'));action('Commission the new fishery',lambda:pilot('fishery'));action('Commission the new wharf',lambda:pilot('wharf'));advance(35);observe('new-pier')
  def inspect():
   panel('economy');office=p.locator('#portFreightOffice');office.evaluate('e=>e.open=true');office.scroll_into_view_if_needed();text=office.inner_text();p.screenshot(path=str(OUT/'port-real-prospects.png'));return text
  action('Read competing river and road costs, duration, dock break-even and retained stock',inspect)
  dock=max(a['id']for a in p.evaluate('__corrected.ports()'));result['newDock']=dock
  def order(cancel=False):
   panel('economy');p.locator('#portFreightOffice').evaluate('e=>e.open=true');button=p.locator('[data-port-dock="'+str(dock)+'"][data-port-direction=import]:not([disabled])').first;button.click();text=p.locator('#eventText').inner_text()
   if cancel:p.keyboard.press('Escape')
   else:confirm()
   return text
  action('Decline a reviewed real pier load before spending',lambda:order(True));action('Commission one enterprise-paid food buffer through the new pier',order);action('Choose the existing river-preference policy for new Greyhaven cargo',lambda:route('river'));observe('paid-river-order')
  for day in [65,95,125,185,215]:advance(day);observe('day-'+str(day))
  action('Inspect whether the chosen pier earned its operating costs',inspect)
 else:
  action('Choose the mixed tract and reviewed full purpose street connection',lambda:district('orchard-downs','neighbourhood'));plan=p.evaluate('__corrected.plan()');result['initialPlan']=plan
  def borrow_for(cost):
   for _ in range(5):
    a=facts()
    if a['treasury']>=cost:return True
    if a['debt']>=50000:return False
    panel('treasury');p.locator('#borrow').click()
    if facts()['treasury']<=a['treasury']:return False
   return False
  def finish(label):
   board();el=p.locator('[data-district-finish]').filter(has_text=label).first
   if not el.count():return {'reason':'Current unmet need no longer proposes this capital site'}
   before=facts();cost={'Cottage':20000,'Grocer':4300,'Bakery':3600,'Clinic':8000,'School':6900}[label]
   if not borrow_for(cost):return {'reason':'Ordinary cash/credit limit reached; defer this purchase','cash':facts()['treasury'],'debt':facts()['debt']}
   board();el=p.locator('[data-district-finish]').filter(has_text=label).first;el.click();quote=p.locator('#eventText').inner_text();confirm();return quote
  action('Cancel the first exact housing purchase',lambda:(p.locator('[data-district-finish]').filter(has_text='Cottage').first.click(),p.keyboard.press('Escape')))
  for i in range(4):action('Purchase normal home '+str(i+1)+' inside the actual project tract',lambda:finish('Cottage'))
  for name in ['Grocer','Bakery']:action('Purchase only the missing '+name+' site',lambda name=name:finish(name))
  observe('homes-and-work');advance(35);result['afterOccupancyPlan']=p.evaluate('__corrected.plan()')
  for name in ['Clinic','School']:action('Reassess actual local coverage before '+name+' capital',lambda name=name:finish(name))
  def funding():
   board();p.locator('[data-district-budget=educationBudget]').click();before=facts()['policy']['educationBudget'];p.locator('[data-policy=educationBudget]').fill('280');el=p.locator('[data-policy=healthBudget]');el.evaluate('e=>e.closest("details").open=true');el.fill('220');preview=p.locator('#panelBody').inner_text();p.locator('#enactPolicy').click();return {'previousSchoolAuthorization':before,'preview':preview[:5000]}
  action('Review scalable service authorization and explicitly enact a recurring package',funding)
  for day in [65,95,125,185,215]:advance(day);observe('day-'+str(day))
  result['finalPlan']=p.evaluate('__corrected.plan()')
 result['automationSeconds']=time.monotonic()-start;result['cashDrift']=facts()['total']-initial;result['valid']=p.evaluate('__townTest.validate()');result['controls']=p.evaluate('__playAudit.controls');result['save']=p.evaluate('__townTest.save()');assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==SHA
 with gzip.open(OUT/(kind+'.json.gz'),'wt')as f:json.dump(result,f)
 b.close();print('FINISHED',kind,result['automationSeconds'],result['valid'],flush=True)
if __name__=='__main__':
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright()as pw:
   for kind in ['port','district']:run(pw,'http://127.0.0.1:'+str(server.server_port),kind)
 finally:server.shutdown()
