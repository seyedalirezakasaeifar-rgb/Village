#!/usr/bin/env python3
"""Finite active-play audit: real controls, normal settlement, no grants or model patches.
Clock is accelerated via tick() only; 1x-equivalent minutes use 1.65 sec/day.
Read-only probes expose the same legal lot survey/metrics used by the shipped UI.
"""
from pathlib import Path
import argparse,functools,http.server,threading,json,hashlib,time,math
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'assets/game.js').read_text();SHA=hashlib.sha256(SOURCE.encode()).hexdigest()
PROBE=r'''
window.__playAudit={
 advance:n=>{let done=0;for(;done<n;done++){if(pendingEvent)break;const openIds=new Set(G.firms.filter(f=>!f.closed).map(f=>f.id));const watched=(G.regionalTrade?.contracts||[]).filter(c=>c.status==='active').map(c=>({id:c.id,firm:c.firm,good:c.good,stock:G.firms[c.firm]?.stock[c.good]||0}));tick();for(const f of G.firms)if(f.closed&&openIds.has(f.id)){const projects=Object.values(G.civicProjects?.active||{}).filter(p=>p.building===f.building);window.__playAudit.failureTrace.push({day:G.day,firm:f.id,name:f.name,kind:f.kind,cash:f.cash,revenue:f.revenue||0,netProfit:f.netProfit||0,projects:projects.map(p=>({kind:p.kind,target:p.target,status:p.status,completed:p.completed,proof:p.proof,display:civicProjectCard(p)})),townSignal:marketSignal().title,mayorPressures:mayorPressureCards().map(p=>p.title)});}for(const w of watched){const c=G.regionalTrade.contracts.find(c=>c.id===w.id),f=G.firms[w.firm],sent=(G.regionalTrade.shipments||[]).filter(o=>o.firm===w.firm&&o.good===w.good&&o.direction==='export'&&o.started===G.day);window.__playAudit.contractTrace.push({day:G.day,id:w.id,firm:w.firm,good:w.good,status:c?.status,stockBefore:w.stock,stockAfter:f?.stock[w.good]||0,production:f?.production||0,ordinaryDispatch:sent.filter(o=>!o.contract).reduce((n,o)=>n+o.qty,0),contractDispatch:sent.filter(o=>o.contract===w.id).reduce((n,o)=>n+o.qty,0),arrived:c?.delivered||0});}for(const p of Object.values(G.civicProjects?.active||{})){if(p.kind!=='district'||G.day-p.started>60)continue;window.__playAudit.projectTrace.push({day:G.day,target:p.target,projectStatus:p.status,plan:G.districtProgrammes?.[p.target],firms:G.firms.filter(f=>{const b=readBuild(f.building);return b&&parcelForTile(b.x,b.y)?.id===p.target;}).map(f=>({id:f.id,kind:f.kind,closed:!!f.closed,workers:workingStaff(f).length,revenue:f.revenue||0,netProfit:f.netProfit||0,cash:f.cash,production:f.production||0,salesQty:f.salesQty||0}))});}}updateHeader();if(active)renderPanel(active);dirty=true;draw();return{done,day:G.day,pending:pendingEvent?{type:pendingEvent.type,title:pendingEvent.title}:null};},
 lot:(kind,parcelId,near)=>{const p=ANNEX_PARCELS.find(p=>p.id===parcelId),anchor=near||(p?{x:p.x+Math.floor(p.w/2),y:p.y+Math.floor(p.h/2)}:{x:42,y:42});return civicProjectLot(kind,anchor,parcelId||null);},
 shoreSpur:parcelId=>{const p=ANNEX_PARCELS.find(p=>p.id===parcelId),net=graph(),sites=[],choices=[];for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)if(canPlace(x,y,false,'wharf'))sites.push({x,y});for(const id of net.neighbors.keys()){const x=id%T,y=id/T|0;if(net.parts[id]!==net.mainPart||parcelForTile(x,y)?.id!==parcelId)continue;for(const site of sites){const goal={x:site.x+1,y:site.y};for(const horizontalFirst of [true,false]){const cells=[];let xx=x,yy=y,valid=true;const walk=axis=>{while(axis==='x'?xx!==goal.x:yy!==goal.y){if(axis==='x')xx+=Math.sign(goal.x-xx);else yy+=Math.sign(goal.y-yy);const next=roadId(xx,yy);if(!charterOwns(xx,yy)||![0,1,3].includes(G.tiles[next])||buildingAt(xx,yy)||G.landUse?.[next]){valid=false;return;}if(G.tiles[next]!==1)cells.push(next);}};walk(horizontalFirst?'x':'y');if(valid)walk(horizontalFirst?'y':'x');if(valid&&cells.length)choices.push({site,cells,cost:cells.length*150});}}}choices.sort((a,b)=>a.cells.length-b.cells.length||a.site.y-b.site.y);return choices[0]||null;},
 facts:()=>{const metrics=programmeMetrics(),trade=G.regionalTrade||{},districts=Object.fromEntries((G.charter?.owned||[]).map(id=>[id,{plan:G.districtProgrammes?.[id]||null,metrics:districtMetrics(id)}]));return{day:G.day,year:G.year,regionalDemand:G.regionalDemand,achievements:G.achievements,availableOffers:civicProjectOffers(),treasury:G.treasury,debt:G.debt,region:G.region,total:totalMoney(),population:G.stats.population,stats:G.stats,metrics,householdLiquidity:G.households.filter(h=>h.people.length).map(h=>({id:h.id,residents:h.people.length,liquidity:householdLiquidity(h),income:h.income,tax:h.tax})),policy:G.policy,districts,projects:G.civicProjects||null,projectObservations:Object.fromEntries(Object.entries(G.civicProjects?.active||{}).map(([k,p])=>[k,civicProjectObservation(p)])),journey:G.mayorJourney||null,programme:G.scenarioProgramme||null,contracts:trade.contracts||[],shipments:(trade.shipments||[]).length,lateShipments:(trade.shipments||[]).filter(o=>o.due<G.day).length,delivered:trade.delivered||0,loading:regionalHandlingCapacity(),firms:G.firms.map(f=>({id:f.id,name:f.name,kind:f.kind,privateService:f.privateService||null,building:f.building,closed:!!f.closed,workers:workingStaff(f).length,jobs:f.jobs,cash:f.cash,production:f.production||0,salesQty:f.salesQty||0,netProfit:f.netProfit||0,profitTrend:f.marginTrend||0,revenue:f.revenue||0,stock:f.stock,clients:f.clientsToday||0})),buildings:G.buildings.map(b=>({id:b.id,kind:b.kind,x:b.x,y:b.y,owner:b.owner})),inbox:G.councilInbox||[],events:G.events.slice(0,18),training:{public:G.civicTrainingCompletions||0,private:G.privateTrainingCompletions||0},valid:validateTown()};}
};
window.__playAudit.failureTrace=[];window.__playAudit.projectTrace=[];window.__playAudit.contractTrace=[];window.__playAudit.controls=[];document.addEventListener('click',e=>{const b=e.target.closest('button');if(b)window.__playAudit.controls.push({day:G?.day||0,id:b.id,dataset:{...b.dataset},text:b.innerText.slice(0,160)});},true);
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass

def run(pw,url,strategy,out,end_minutes):
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':844,'height':390},has_touch=True);page.set_default_timeout(8000)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/game.js',lambda route:route.fulfill(status=200,content_type='application/javascript',body=SOURCE.replace('// SOURCE: 99-instrumentation.js',PROBE+'\n// SOURCE: 99-instrumentation.js')))
 page.goto(url+'/assets/index.html');page.locator('#townSeed').fill('42');page.locator('#newTown').click();page.locator('#pause').click()
 result={'strategy':strategy,'source_sha256':SHA,'seed':42,'clock_seconds_per_simulated_day':1.65,'method':'Fresh UI-founded town; purchases/policies/borrowing through actual controls; time-only tick acceleration; no fixture grants, account injections, forced staffing or automatic council choices.','actions':[],'checkpoints':[],'errors':errors}
 facts=lambda:page.evaluate('__playAudit.facts()')
 def panel(name):
  button=page.locator('[data-panel='+name+']')
  if page.locator('#panel').evaluate('e=>e.classList.contains("show")') and 'active' in (button.get_attribute('class') or ''):return
  button.click()
 def board():
  panel('overview');page.locator('[data-civic-projects]').click()
 def act(label,callback,reason=''):
  a=facts()
  try:outcome=callback()
  except Exception as error:
   result['blocked']={'action':label,'day':a['day'],'reason':str(error),'status':'not completed; action outcome must be checked against captured state','state':facts()};(out/(strategy+'-blocked.json')).write_text(json.dumps(result,indent=2)+'\n');page.screenshot(path=str(out/(strategy+'-blocked.png')));raise
  b=facts();result['actions'].append({'day':a['day'],'equivalentMinute':(a['day']-1)*1.65/60,'action':label,'reason':reason,'treasuryBefore':a['treasury'],'treasuryAfter':b['treasury'],'debtBefore':a['debt'],'debtAfter':b['debt'],'regionDelta':b['region']-a['region'],'populationDelta':b['population']-a['population'],'outcome':outcome})
 def advance(day):
  a=facts();n=max(0,day-a['day']);start=time.monotonic()
  while n:
   batch=min(n,90);r=page.evaluate('n=>__playAudit.advance(n)',batch)
   if r['done']!=batch:raise RuntimeError('Unexpected unresolved dialog: '+str(r))
   n-=batch
  return time.monotonic()-start
 def checkpoint(label):
  d=facts();d['label']=label;d['equivalentMinutes']=(d['day']-1)*1.65/60;d['playerActionsSoFar']=len(result['actions']);result['checkpoints'].append(d)
  if label in ['first commitments','10 minutes equivalent','30 minutes equivalent','60 minutes equivalent']:
   panel('overview');page.locator('#panelClose').click();page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');page.screenshot(path=str(out/(strategy+'-'+label.replace(' ','-')+'.png')))
 def confirm():page.locator('[data-event-choice="0"]').click()
 def choose_direction(direction):
  panel('agenda');button=page.locator('[data-mayor-direction='+direction+']');
  if not button.is_visible():page.get_by_text('Compare another direction',exact=True).click()
  button.click();confirm()
 def choose_food(local):
  board();page.locator('[data-civic-project-review=food]').click();page.locator('[data-event-choice="'+('1' if local else '0')+'"]').click()
  if local:page.locator('[data-civic-project-build=bakery]').click();confirm()
  else:page.locator('[data-civic-project-order]').click();confirm()
 def policies(settings):
  panel('policies')
  for k,v in settings.items():
   el=page.locator('[data-policy='+k+']');el.evaluate('e=>e.closest("details").open=true');el.fill(str(v))
  if page.locator('#enactPolicy').is_enabled():page.locator('#enactPolicy').click()
 def district(parcel,focus):
  board();page.locator('[data-civic-project-review=district]').click();page.locator('#projectParcel').select_option(parcel);page.locator('#projectFocus').select_option(focus);page.locator('#projectDistrictAdopt').click()
  page.locator('[data-civic-project-deed]').click();confirm();page.locator('[data-civic-project-charter]').click();confirm()
  if page.locator('[data-civic-project-road]').count():page.locator('[data-civic-project-road]').click();confirm()
 def pilot(kind):
  board();button=page.locator('[data-civic-project-build='+kind+']')
  if not button.count():return {'quoted':False,'reason':'No construction offer; inspect an existing pilot or prerequisites'}
  before=facts();button.click()
  if not page.locator('#eventDialog').is_visible():
   page.screenshot(path=str(out/(strategy+'-'+kind+'-no-site-day-'+str(before['day'])+'-action-'+str(len(result['actions']))+'.png')));return {'quoted':False,'reason':page.locator('#toast').inner_text()}
  title=page.locator('#eventTitle').inner_text();confirm();after=facts();return {'quoted':True,'quote':title,'newBuildings':len(after['buildings'])-len(before['buildings'])}
 def ensure_capital(cost,max_debt=50000):
  while facts()['treasury']<cost+5000 and facts()['debt']<max_debt:
   before=facts()['treasury'];panel('treasury');page.locator('#borrow').click()
   if facts()['treasury']<=before:return False
  return facts()['treasury']>=cost
 def build(kind,parcel,near=None):
  cost={'home':20000,'school':6900,'clinic':8000}[kind]
  lot=page.evaluate('o=>__playAudit.lot(o.kind,o.parcel,o.near)',{'kind':kind,'parcel':parcel,'near':near})
  if not lot:return {'built':False,'reason':'No legal connected lot','kind':kind,'parcel':parcel}
  if not ensure_capital(cost):return {'built':False,'reason':'Cash/credit cannot fund site','kind':kind,'parcel':parcel}
  panel('construction');page.locator('[data-build-category='+('housing' if kind=='home' else 'services')+']').click();page.locator('[data-build='+kind+']').click()
  # Standard zoom/pan controls move the survey into view through camera-only instrumentation.
  # It changes presentation coordinates, never placement legality or model state.
  page.evaluate('o=>__townTest.capture({zoom:.85,x:(o.x-o.y)*36+(80*72+140)/2,y:(o.x+o.y)*18+57})',lot)
  camera=page.evaluate('__townTest.view().camera');box=page.locator('#view').bounding_box();x,y=lot['x'],lot['y'];sx=box['x']+box['width']/2+camera['zoom']*((x-y)*36+(80*72+140)/2-camera['x']);sy=box['y']+box['height']/2+camera['zoom']*((x+y)*18+50-camera['y'])
  before=facts();page.mouse.click(sx,sy);page.keyboard.press('Escape');after=facts()
  return {'built':len(after['buildings'])>len(before['buildings']),'kind':kind,'lot':lot,'municipalCashChange':after['treasury']-before['treasury'],'residentsCreated':after['population']-before['population']}
 def shore_spur(parcel):
  plan=page.evaluate('id=>__playAudit.shoreSpur(id)',parcel)
  if not plan:return {'built':False,'reason':'No simple legal shore spur surveyed'}
  if not ensure_capital(plan['cost']):return {'built':False,'reason':'Cash/credit limit'}
  panel('construction');page.locator('[data-build=road]').click();before=facts()
  for tile in plan['cells']:
   x,y=tile%80,tile//80;page.evaluate('o=>__townTest.capture({zoom:.85,x:(o.x-o.y)*36+(80*72+140)/2,y:(o.x+o.y)*18+57})',{'x':x,'y':y});camera=page.evaluate('__townTest.view().camera');box=page.locator('#view').bounding_box();sx=box['x']+box['width']/2+camera['zoom']*((x-y)*36+(80*72+140)/2-camera['x']);sy=box['y']+box['height']/2+camera['zoom']*((x+y)*18+50-camera['y']);page.mouse.click(sx,sy)
  page.keyboard.press('Escape');after=facts();return {'built':after['treasury']<before['treasury'],'survey':plan,'cashChange':after['treasury']-before['treasury']}
 def repay_surplus():
  n=0
  while facts()['debt']>=5000 and facts()['metrics']['reserve']>40:
   before=facts()['debt'];panel('treasury');page.locator('#repay').click()
   if facts()['debt']>=before:break
   n+=1
  return {'principalPayments':n,'remainingDebt':facts()['debt']}
 def review(minute):
  current=facts();result.setdefault('reviews',[]).append({'minute':minute,'day':current['day'],'observedTreasury':current['treasury'],'observedCoverage':{k:current['metrics'][k] for k in ['food','medical','school','reserve']},'availableOffers':[o['kind'] for o in current['availableOffers']],'activeProjectStatuses':{k:p['status'] for k,p in (current['projects']or{}).get('active',{}).items()}})
  if strategy=='trade' and minute==10:
   act('Reinvest in care and targeted learning without raising income tax',lambda:policies({'healthBudget':110,'serviceVoucherBudget':80}),'Observed care access is below the 65% public target; preserve the trade identity while purchasing targeted teaching.')
   def invite():
    board();page.locator('[data-civic-project-review=skills]').click();page.get_by_text('Invite independent teaching',exact=True).click();page.locator('[data-private-invite=school]').click();return {'invitationFeedback':page.locator('#toast').inner_text()}
   act('Invite independent teaching for the named learner household',invite)
   def larger_agreement():
    panel('economy');card=page.locator('[data-trade-offer]:not([disabled])').first;preview=card.locator('..').inner_text();card.click();confirm();return {'displayedOffer':preview}
   act('Try the larger agreement unlocked by the trade park',larger_agreement)
  if strategy=='trade' and minute==20:
   def diversify_contract():
    panel('economy');card=page.locator('[data-trade-offer=port]:not([disabled])');preview=card.locator('..').inner_text();card.click();confirm();return {'displayedOffer':preview}
   act('Compare a different regional buyer rather than repeat one supplier',diversify_contract)
  if strategy=='community' and minute==20:act('Repay municipal principal while retaining forty authorized spending days',repay_surplus)
  if minute==30:
   old=(current['projects']or{}).get('active',{}).get('district')
   if old and old['status']=='complete':
    if strategy=='trade':
     act('Broaden the town direction to a working river',lambda:choose_direction('river'))
     act('Buy Lower River Reach and commission the working-waterfront gateway',lambda:district('river-reach','waterfront'))
     act('Try a shoreline fishery from the project survey',lambda:pilot('fishery'))
     act('Try an outlet wharf from the project survey',lambda:pilot('wharf'))
     # If the generic interior gateway fails, recover with a visible, paid road spur.
     if not facts()['districts']['river-reach']['metrics']['fishery']:
      act('Draw a legal paid shore spur after the site survey fails',lambda:shore_spur('river-reach'))
      act('Commission the fishery after connecting the shore',lambda:pilot('fishery'))
      act('Commission the cargo wharf after connecting the shore',lambda:pilot('wharf'))
     if not any(b['kind']=='wharf' and 2<=b['x']<28 and 56<=b['y']<78 for b in facts()['buildings']):
      act('Extend a second legal shore connection for the missing wharf',lambda:shore_spur('river-reach'))
      act('Retry the outlet wharf after the second shore connection',lambda:pilot('wharf'))
     for i in range(2):
      details={};act('Build an inland waterfront cottage '+str(i+1),lambda:details.update(build('home','river-reach')),'Add real nearby residents instead of assuming empty docks come with crews.');result['actions'][-1]['placement']=details
    else:
     act('Expand the community identity to East Meadow',lambda:district('east-meadow','neighbourhood'))
     act('Commission the second neighbourhood grocer',lambda:pilot('grocer'))
     act('Commission the second neighbourhood bakery',lambda:pilot('bakery'))
     for i in range(4):
      details={};act('Build East Meadow cottage '+str(i+1),lambda:details.update(build('home','east-meadow')));result['actions'][-1]['placement']=details
      if not details.get('built'):break
     details={};act('Put a public school within the new neighbourhood',lambda:details.update(build('school','east-meadow')));result['actions'][-1]['placement']=details
  if minute==45:
   if strategy=='trade' and 'river-reach' in current['districts'] and current['districts']['river-reach']['metrics']['staffed']<2:
    for i in range(2):
     details={};act('Try another nearby waterfront workforce cottage '+str(i+1),lambda:details.update(build('home','river-reach')));result['actions'][-1]['placement']=details
     if not details.get('built'):break
   if strategy=='community' and current['metrics']['school']<75:act('Adjust teaching funds to the larger resident base',lambda:policies({'educationBudget':420,'healthBudget':300}))
 checkpoint('founding')
 act('Choose the town direction',lambda:choose_direction('exchange' if strategy=='trade' else 'community'))
 act('Commission the food route',lambda:choose_food(strategy=='community'),'Trade uses paid imported stock; community commits municipal capital to a local producer.')
 advance(13)
 if strategy=='trade':
  def agreement():
   panel('economy');page.locator('[data-trade-offer]:not([disabled])').first.click();confirm()
  act('Broker the first available export agreement',agreement)
  act('Acquire County Ridge, designate trade park and build its gateway',lambda:district('county-ridge','industry'))
  act('Commission the district factory',lambda:pilot('factory'))
  act('Commission the district freight depot',lambda:pilot('warehouse'))
 else:
  act('Fund reachable services with higher local taxes',lambda:policies({'incomeTax':18,'profitTax':18,'educationBudget':280,'healthBudget':220,'roadBudget':80}),'A public-service route spends recurring cash instead of early industrial capital.')
  def school_project():
   board();page.locator('[data-civic-project-review=skills]').click();confirm()
  act('Adopt the existing-school teaching promise',school_project)
 checkpoint('first commitments')
 advance(60);checkpoint('day 60')
 if strategy=='community':
  act('Acquire Orchard Downs, designate mixed neighbourhood and build its gateway',lambda:district('orchard-downs','neighbourhood'))
  act('Commission the neighbourhood grocer',lambda:pilot('grocer'))
  act('Commission the neighbourhood bakery',lambda:pilot('bakery'))
  for i in range(4):
   details={}
   act('Build neighbourhood cottage '+str(i+1),lambda:details.update(build('home','orchard-downs')),'Use normal municipal credit only if cash is insufficient; stop at the real lender limit.')
   result['actions'][-1]['placement']=details
   if not details.get('built'):break
  for kind in ['school','clinic']:
   details={};act('Build reachable neighbourhood '+kind,lambda:details.update(build(kind,'orchard-downs')));result['actions'][-1]['placement']=details
 advance(90);checkpoint('day 90')
 if strategy=='trade':
  m=facts()['districts']['county-ridge']['metrics']
  if m['staffed']<2:
   act('Improve commuter access for understaffed pilots',lambda:policies({'transitBudget':90}))
   details={};act('Add one commuter cottage inside the original charter',lambda:details.update(build('home',None,{'x':53,'y':42})));result['actions'][-1]['placement']=details
 advance(180);checkpoint('day 180')
 # One reviewed recovery decision; do not paper over persistent deficits with grants.
 if strategy=='community' and facts()['districts']['orchard-downs']['metrics']['staffed']<2:
  act('Improve access to the neighbourhood workplaces',lambda:policies({'transitBudget':90}))
 if strategy=='trade' and facts()['districts']['county-ridge']['metrics']['staffed']<2:
  details={};act('Try a second commuter cottage if normal finance permits',lambda:details.update(build('home',None,{'x':53,'y':42})));result['actions'][-1]['placement']=details
 for minutes in [10,20,30,45,60]:
  if minutes>end_minutes:break
  advance(1+round(minutes*60/1.65));checkpoint(str(minutes)+' minutes equivalent');review(minutes);checkpoint(str(minutes)+' minutes after review')
 final=facts();result['controls']=page.evaluate('__playAudit.controls');result['contractTrace']=page.evaluate('__playAudit.contractTrace');result['projectTrace']=page.evaluate('__playAudit.projectTrace');result['failureTrace']=page.evaluate('__playAudit.failureTrace');result['final']=final;result['cashConservationDrift']=final['total']-result['checkpoints'][0]['total'];result['actualAutomationSeconds']=None
 if errors:result['blocked']='Page errors: '+repr(errors)
 (out/(strategy+'.json')).write_text(json.dumps(result,indent=2)+'\n');browser.close();print(strategy,final['day'],final['treasury'],final['stats']['employment'],final['metrics']['school'],final['districts'],flush=True)
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--strategy',choices=['trade','community','both'],default='both');parser.add_argument('--end-minutes',type=int,default=60);args=parser.parse_args()
 out=ROOT/'reports/active-play-audit';out.mkdir(parents=True,exist_ok=True);server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();start=time.monotonic()
 try:
  with sync_playwright() as pw:
   for strategy in ['trade','community'] if args.strategy=='both' else [args.strategy]:run(pw,'http://127.0.0.1:'+str(server.server_port),strategy,out,args.end_minutes)
 finally:server.shutdown()
 assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==SHA,'Production source changed during read-only audit'
 print('Audit automation seconds',round(time.monotonic()-start,1),flush=True)
if __name__=='__main__':main()
