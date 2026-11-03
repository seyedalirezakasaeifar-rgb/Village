"""Durable operating chapters: real invoices, returned cargo, failed private entry and public recovery.
The approaching cargo fixture books a real paid order; it grants no resources.
"""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();OUT=ROOT/'reports/civic-turnarounds';OUT.mkdir(parents=True,exist_ok=True)
probe='''
window.__chapterProbe={waiting:()=>civicCampaignWaitingFood(),observation:()=>G.civicCampaign?.active?civicCampaignObservation(G.civicCampaign.active):null,
 bookPaidLoad:()=>{const before=totalMoney(),ids=[];for(const f of G.firms.filter(f=>f.kind==='grocer'&&!f.closed).sort((a,b)=>b.cash-a.cash).slice(0,1))for(const m of OUTSIDE_MARKETS.slice(0,1))for(let i=0;i<1;i++){const n=dispatchRegional(f,'food',60,'import',regionalQuote(f,m,'food','import'));if(n)ids.push(fromEnd(G.regionalTrade.shipments).id);}return{ids,cashDrift:totalMoney()-before};},
 tryIncompleteReceipt:()=>{const p=G.civicCampaign.active,before=p.arrived;civicProjectRecordArrival({id:p.reference.id,status:'Delivered',qty:p.reference.quantity});return p.arrived===before;},
 repeatReceipt:()=>{const p=G.civicCampaign.active,o=G.regionalTrade.recent.find(o=>o.id===p.reference.id&&o.status==='Delivered'),before=p.arrived;if(o)civicProjectRecordArrival(o);return p.arrived===before;},
 learner:()=>civicRenewalHousehold(),total:()=>totalMoney()};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_default_timeout(10000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click()
 state=lambda:p.evaluate('JSON.parse(__townTest.save())')
 def panel(name):
  if p.locator('#panel').evaluate('e=>e.classList.contains("show")') and 'active'in(p.locator('[data-panel='+name+']').get_attribute('class')or''):return
  p.locator('[data-panel='+name+']').click()
 def board():panel('overview');p.locator('[data-civic-projects]').click()
 def confirm():p.locator('[data-event-choice="0"]').click()
 def step(n):assert not p.evaluate('__townTest.get().pending');p.evaluate('n=>__townTest.step(n)',n)
 def policy(k,v):
  panel('policies');f=p.locator('[data-policy='+k+']');f.evaluate('e=>e.closest("details").open=true');f.fill(str(v));p.locator('#enactPolicy').click()
 total=p.evaluate('__chapterProbe.total()')
 # Earn the later chapter through actual paid food and funded learning.
 board();p.locator('[data-civic-project-review=food]').click();confirm();p.locator('[data-civic-project-order]').click();confirm();step(24)
 board();p.locator('[data-civic-project-review=skills]').click();confirm();p.locator('[data-civic-project-budget]').click();confirm();p.locator('#enactPolicy').click();step(180)
 assert state()['civicProjects']['active']['food']['status']=='complete'and state()['civicProjects']['active']['skills']['status']=='complete'
 # A known, fully paid handling peak makes an actual pending load selectable.
 panel('economy');p.locator('#logisticsOffice').evaluate('e=>e.open=true');p.locator('[data-logistics-routing=interchange]').click()
 peak=p.evaluate('__chapterProbe.bookPaidLoad()');assert len(peak['ids'])==1 and abs(peak['cashDrift'])<.001
 for _ in range(15):
  if p.evaluate('__chapterProbe.waiting()'):break
  step(1)
 waiting=p.evaluate('__chapterProbe.waiting()');assert waiting,peak
 board();p.locator('[data-campaign-review=essentials]').click();confirm();tracked=state()['civicCampaign']['active']['reference'];assert tracked['kind']=='shipment'
 assert p.evaluate('__chapterProbe.tryIncompleteReceipt()'),'Missing metadata must not create usable delivery'
 p.locator('[data-campaign-operations]').click();p.locator('[data-logistics-priority=essentials]').click();assert state()['regionalTrade']['priority']=='essentials'
 board();p.locator('[data-logistics-cancel="'+str(tracked['id'])+'"]').click();confirm();step(25)
 failed=state()['civicCampaign']['active'];assert failed['arrived']==0 and failed['receiptDay']is None and failed['status']=='active'
 assert p.evaluate('__chapterProbe.observation().setback')
 board();p.locator('[data-campaign-withdraw]').click();p.keyboard.press('Escape');assert state()['civicCampaign']['active']
 p.locator('[data-campaign-withdraw]').click();confirm();assert state()['civicCampaign']['active']is None and state()['civicCampaign']['history'][0]['status']=='withdrawn'
 # Another real consignment can recover; extra shifts remain an explicit economic choice.
 p.evaluate('__chapterProbe.bookPaidLoad()')
 for _ in range(15):
  if p.evaluate('__chapterProbe.waiting()'):break
  step(1)
 board();p.locator('[data-campaign-review=essentials]').click();confirm();before=state();p.locator('[data-campaign-shift]').click();p.keyboard.press('Escape');assert state()['regionalTrade']['reliefUntil']==before['regionalTrade']['reliefUntil']
 board();p.locator('[data-campaign-shift]').click();confirm()
 step(20);delivered=state()['civicCampaign']['active'];assert delivered['status']=='complete'and delivered['arrived']==delivered['reference']['quantity']and delivered['receiptDay']
 assert p.evaluate('__chapterProbe.repeatReceipt()')
 # Real policy retreat creates a different eligible household's access gap.
 policy('educationBudget',0);step(1);next_house=p.evaluate('__chapterProbe.learner()');assert next_house and next_house['access']['coverage']<.4
 board();p.locator('[data-civic-project-review=skills]').click();p.get_by_text('Invite independent teaching',exact=True).click();renewal=state()['civicProjects']['active']['skills'];assert renewal['continuity']and renewal['target']!=state()['civicProjects']['history'][0].get('target',-1)
 p.locator('[data-private-invite=school]').click();policy('serviceVoucherBudget',100);step(85)
 private=state()['civicProjects']['active']['skills'];assert private['status']=='active' and private['privateLearnerDays']==0,private
 # On this integration baseline no private investor clears the real viability checks.
 # No fictitious purchase earns progress: recover through a reviewed public route.
 board();p.locator('[data-civic-project-replan=skills]').click();confirm();policy('educationBudget',280);step(75)
 public=state()['civicProjects']['active']['skills'];assert public['continuity']and public['publicLearnerDays']>0 and public['status']=='complete',public
 checkpoint=p.evaluate('__townTest.save()');step(7);expected=state();assert p.evaluate('(s)=>__townTest.load(s)',checkpoint);step(7);actual=state()
 for key in ['day','treasury','civicProjects','civicCampaign','regionalTrade']:assert actual[key]==expected[key],key
 # Optional UI data migrate; malformed scopes/counts are rejected before changing the town.
 valid=state()
 for mutate in ['g.civicCampaign.active.reference.firm=1.5','g.civicCampaign.active.arrived=1e13','g.civicProjects.active.skills.learnerDays=-1']:
  assert p.evaluate('code=>{const g=JSON.parse(__townTest.save());new Function("g",code)(g);return !__townTest.load(JSON.stringify(g));}',mutate),mutate
 legacy=state();legacy.pop('civicCampaign',None);assert p.evaluate('(s)=>__townTest.load(JSON.stringify(s))',legacy)
 assert p.evaluate('__townTest.validate().ok');assert abs(p.evaluate('__chapterProbe.total()')-total)<.01;assert not errors,errors
 (OUT/'operating-chapters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledOrderUsesPaidBookings':peak,'returnedTrackedOrderNeverCredited':failed,'deliveredChapter':delivered,'privateEntryWithoutTeaching':private,'publicContinuity':public,'replayDays':7,'errors':errors},indent=2)+'\n')
 print('PASS real unlocked chapters, paid load/return/no false receipt, actual queue priority and reviewed shift, successful delivery once, real failed private entry and reviewed public recovery, exact replay and legacy/corrupt UI archives',flush=True)
 b.close()
