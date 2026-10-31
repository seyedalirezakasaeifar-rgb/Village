#!/usr/bin/env python3
"""Frozen-candidate active controls; simulated time is never labelled human play time."""
import sys,time,json,hashlib,functools,http.server,threading,gzip
from pathlib import Path
from playwright.sync_api import sync_playwright
from audit_economic_play import PROBE,Quiet
ROOT=Path(__file__).resolve().parents[1];SOURCE=(ROOT/'assets/game.js').read_text();SHA=hashlib.sha256(SOURCE.encode()).hexdigest();OUT=ROOT/'reports/three-city-audit';OUT.mkdir(parents=True,exist_ok=True)
EXTRA=r'''
window.__three={point:(x,y)=>{const a=iso(x,y),r=cv.getBoundingClientRect();return {x:r.left+cw/2+(a[0]-cam.x)*cam.zoom,y:r.top+ch/2+(a[1]+18-cam.y)*cam.zoom,world:a};},extra:()=>({transit:G.transit,places:G.publicPlaces,situations:G.townSituations,migration:G.migration,metrics:roadMetrics(),training:G.civicTraining,private:G.privateServiceProvision}),lot:(kind,near)=>civicProjectLot(kind,near),roadStops:()=>[roadId(21,27),roadId(35,27),roadId(43,27)].filter(id=>G.tiles[id]===1).map(id=>({x:id%T,y:id/T|0})),total:totalMoney};
'''

def run(pw,url,strategy):
 start=time.monotonic();browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=browser.new_page(viewport={'width':844,'height':390},has_touch=True);p.set_default_timeout(5000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(status=200,content_type='application/javascript',body=SOURCE.replace('// SOURCE: 99-instrumentation.js',PROBE+EXTRA+'\n// SOURCE: 99-instrumentation.js')));p.goto(url+'/assets/index.html');p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click()
 result={'strategy':strategy,'candidate':'31987fc','source_sha256':SHA,'seed':42,'actions':[],'checkpoints':[],'errors':errors,'limitations':['Service-budget scaling and migration refinements pending on frozen candidate.','Control automation is active decision evidence, not measured human enjoyment or hours of human play.']}
 facts=lambda:p.evaluate('__playAudit.facts()')
 def panel(tab):
  if p.locator('#panel').evaluate('e=>e.classList.contains("show")')and'active'in(p.locator('[data-panel='+tab+']').get_attribute('class')or''):return
  p.locator('[data-panel='+tab+']').click()
 def board():panel('overview');p.locator('[data-civic-projects]').click()
 def confirm():p.locator('[data-event-choice="0"]').click()
 def act(label,fn):
  a=facts();t=time.monotonic()
  try:detail=fn();status='executed; inspect state deltas'
  except Exception as e:
   detail=str(e).split('Call log:')[0];status='blocked/uncertain; actual post-state retained';p.screenshot(path=str(OUT/(strategy+'-blocked-'+str(len(result['actions']))+'.png')))
   if p.locator('#eventDialog').is_visible():p.keyboard.press('Escape')
  b=facts();result['actions'].append({'label':label,'day':a['day'],'simulated1xMinutes':(a['day']-1)*1.65/60,'automationSeconds':time.monotonic()-t,'status':status,'detail':detail,'cashDelta':b['treasury']-a['treasury'],'debtDelta':b['debt']-a['debt'],'populationDelta':b['population']-a['population'],'newBuildings':len(b['buildings'])-len(a['buildings']),'toast':p.locator('#toast').inner_text()});print(strategy,a['day'],label,status,flush=True)
 def advance(target):
  while facts()['day']<target:
   n=min(90,target-facts()['day']);r=p.evaluate('n=>__playAudit.advance(n)',n)
   if r['pending']:
    result['actions'].append({'day':r['day'],'label':'Defer council petition for review','detail':r['pending'],'status':'deferred via actual control'});p.locator('#eventDefer').click()
 def checkpoint(label):
  a=facts();a['extra']=p.evaluate('__three.extra()');a['label']=label;a['simulated1xMinutes']=(a['day']-1)*1.65/60;a['automationElapsedSeconds']=time.monotonic()-start;a['controlsSoFar']=len(p.evaluate('__playAudit.controls'));result['checkpoints'].append(a);board();p.screenshot(path=str(OUT/(strategy+'-'+label+'.png')))
 def policy(settings):
  panel('policies')
  for key,value in settings.items():
   el=p.locator('[data-policy='+key+']');el.evaluate('e=>e.closest("details").open=true');el.fill(str(value))
  p.locator('#enactPolicy').click()
 def direction(key):
  panel('agenda');el=p.locator('[data-mayor-direction='+key+']');el.evaluate('e=>e.closest("details").open=true');el.click();confirm()
 def food(local=False):
  board();p.locator('[data-civic-project-review=food]').click();p.locator('[data-event-choice="'+('1'if local else'0')+'"]').click();p.locator('[data-civic-project-build=bakery]'if local else'[data-civic-project-order]').click();confirm()
 def district(parcel,focus):
  board();p.locator('[data-civic-project-review=district]').click();p.locator('#projectParcel').select_option(parcel);p.locator('#projectFocus').select_option(focus);p.locator('#projectDistrictAdopt').click();p.locator('[data-civic-project-deed]').click();confirm();p.locator('[data-civic-project-charter]').click();confirm();p.locator('[data-civic-project-road]').click();confirm()
 def pilot(kind):board();p.locator('[data-civic-project-build='+kind+']').click();confirm()
 def capital(cost):
  for _ in range(10):
   a=facts()
   if a['treasury']>=cost+5000:return True
   if a['debt']>=50000:return False
   panel('treasury');p.locator('#borrow').click()
   if facts()['treasury']<=a['treasury']:return False
  return False
 def mapclick(x,y):
  a=p.evaluate('o=>__three.point(o.x,o.y)',{'x':x,'y':y});p.evaluate('a=>__townTest.capture({x:a[0],y:a[1]+18,zoom:.85})',a['world']);a=p.evaluate('o=>__three.point(o.x,o.y)',{'x':x,'y':y});p.mouse.click(a['x'],a['y'])
 def build(kind,near):
  lot=p.evaluate('o=>__three.lot(o.kind,o.near)',{'kind':kind,'near':near})
  if not lot:return {'reason':'No legally connected lot'}
  costs={'home':20000,'school':6900,'clinic':8000,'transit_depot':9000,'bakery':3600}
  if not capital(costs[kind]):return {'reason':'Cash/authorized debt limit reached'}
  panel('construction');category='housing'if kind=='home'else'services'if kind in ['school','clinic','transit_depot']else'commerce';p.locator('[data-build-category='+category+']').click();p.locator('[data-build='+kind+']').click();mapclick(lot['x'],lot['y']);p.keyboard.press('Escape');return lot
 def bus():
  panel('construction');p.locator('[data-transit-action=new-bus]').click();p.locator('#transitLevel').select_option('1');p.locator('[data-transit-action=map]').click();stops=p.evaluate('__three.roadStops()')
  for stop in stops:mapclick(stop['x'],stop['y'])
  panel('construction');p.locator('[data-transit-action=quote]').click();preview=p.locator('.transit-office').inner_text();p.locator('[data-transit-action=build]').click();return preview
 def agreement(food=False):
  panel('economy')
  if food:
   p.locator('#alternativeSuppliers').evaluate('e=>e.open=true');p.locator('#supplierMarket').select_option('port');p.locator('#supplierGood').select_option('food');button=p.locator('#alternativeSuppliers [data-trade-offer]')
  else:button=p.locator('[data-trade-offer]:not([disabled])').first
  button.click();text=p.locator('#eventText').inner_text();confirm();return text
 def place(kind):
  board();p.locator('[data-public-place='+kind+']').click();p.locator('#publicPlaceName').fill({'port':'Harbour Exchange','transit':'Station Commons','local':'Neighbourhood Market'}[strategy]);confirm()
 initial=facts();checkpoint('founding');act('Choose coherent direction',lambda:direction('river'if strategy=='port'else'community'));act('Choose paid imported buffer or municipal local producer',lambda:food(strategy=='local'));advance(14)
 if strategy=='port':
  act('Acquire and connect real river-front development',lambda:district('river-reach','waterfront'));act('Establish fishery',lambda:pilot('fishery'));act('Establish regional wharf',lambda:pilot('wharf'));act('Broker a feasible first regional promise',agreement)
 elif strategy=='transit':
  act('Commit recurring teaching, care and street funds',lambda:policy({'educationBudget':280,'healthBudget':220,'roadBudget':80,'incomeTax':18}));act('Purchase actual transit depot',lambda:build('transit_depot',{'x':35,'y':30}));act('Review and authorize a basic bus corridor',bus)
 else:
  act('Reinvest locally in a public market square',lambda:place('square'));act('Fund public teaching rather than early outside capacity',lambda:policy({'educationBudget':280,'healthBudget':160,'incomeTax':18}));act('Adopt real teaching commitment',lambda:(board(),p.locator('[data-civic-project-review=skills]').click(),confirm()))
 checkpoint('early-commitments');advance(90)
 if strategy=='port':act('Support actual dock workforce through existing commuter policy',lambda:policy({'transitBudget':90}));act('Try nearby waterfront housing within ordinary capital limit',lambda:build('home',{'x':12,'y':62}))
 elif strategy=='transit':act('Use a public square instead of a new loading property',lambda:place('square'));act('Compare actual fee-funded school proposal',lambda:(panel('community'),p.locator('[data-private-invite=school]').click()))
 else:
  act('Acquire mixed neighbourhood instead of trade park',lambda:district('orchard-downs','neighbourhood'));act('Establish neighbourhood grocer',lambda:pilot('grocer'));act('Establish neighbourhood bakery',lambda:pilot('bakery'));act('Try connected nearby housing with actual borrowing limit',lambda:build('home',{'x':66,'y':40}))
 for minute in [10,30,60,120]:
  advance(1+round(minute*60/1.65));checkpoint(str(minute)+'-minutes-equivalent')
  a=facts()
  if minute==10:
   act('Inspect original household and provider consequences',lambda:(panel('community'),p.locator('#panelBody').inner_text()[:5000]))
   if strategy=='port':act('Diversify to actual food buyer while retaining reserve',lambda:agreement(True));act('Compare freight handling investment against public capital',lambda:place('warehouse'))
   elif strategy=='transit':
    act('Inspect actual corridor riders, denied demand and driver payroll',lambda:(panel('construction'),p.locator('.transit-office').inner_text()))
    act('Try expanding mixed neighbourhood with remaining ordinary capital',lambda:district('county-ridge','neighbourhood'))
   else:act('Try local food export surplus through alternate supplier UI',lambda:agreement(True));act('Review independent teaching without a municipal grant',lambda:(panel('community'),p.locator('[data-private-invite=school]').click()))
  if minute==30:
   if a['metrics']['reserve']<30:act('Recover recurring runway by reducing school authorization, sacrificing coverage',lambda:policy({'educationBudget':120,'healthBudget':110}))
   elif strategy=='transit':act('Expand service on existing corridor after checking actual demand',lambda:(panel('construction'),p.locator('[data-transit-level]').filter(has_text='Frequent').first.click()))
   else:act('Reinvest available cash in reachable learning',lambda:policy({'educationBudget':420,'healthBudget':220}))
   act('Review dated place outcomes without claiming causality',lambda:(board(),p.locator('#publicLife').inner_text()))
  if minute==60:
   act('Review lost roles and recovery options in town agenda',lambda:(board(),p.locator('#panelBody').inner_text()[:10000]))
   if strategy=='port':
    act('Review paid recharter if waterfront role failed',lambda:(board(),p.locator('[data-civic-recharter]').click(),p.keyboard.press('Escape')))
   elif strategy=='transit':act('Suspend the paid bus route to compare cost and access',lambda:(panel('construction'),p.locator('[data-transit-level$=":0"]').first.click()))
   else:act('Try another local household service commitment if offered',lambda:(board(),p.locator('[data-civic-project-review=skills]').click(),confirm()))
 checkpoint('final-after-review');result['controls']=p.evaluate('__playAudit.controls');result['closures']=p.evaluate('__playAudit.failureTrace');result['providerTrace']=p.evaluate('__playAudit.providerTrace');result['contractTrace']=p.evaluate('__playAudit.contractTrace');result['cashDrift']=facts()['total']-initial['total'];result['automationSeconds']=time.monotonic()-start;result['save']=p.evaluate('__townTest.save()');result['errors']=errors;result['finalValidate']=p.evaluate('__townTest.validate()');assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==SHA
 with gzip.open(OUT/(strategy+'.json.gz'),'wt')as f:json.dump(result,f)
 browser.close();print('FINISHED',strategy,'seconds',result['automationSeconds'],'cashDrift',result['cashDrift'],flush=True)

if __name__=='__main__':
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright()as pw:
   for strategy in (sys.argv[1:]or['port','transit','local']):run(pw,'http://127.0.0.1:'+str(server.server_port),strategy)
 finally:server.shutdown()
