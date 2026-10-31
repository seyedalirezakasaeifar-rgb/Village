#!/usr/bin/env python3
"""Use real saved cohorts to test readable port and municipal-finance recovery."""
import json,gzip,threading,functools,http.server,time
from playwright.sync_api import sync_playwright
from accept_corrected_planning import ROOT,OUT,SOURCE,SHA,PROBE,EXTRA,Quiet

def main():
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
 try:
  with sync_playwright()as pw:
   b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
   for kind in ['port','district']:
    original=json.load(gzip.open(OUT/(kind+'.json.gz')));p=b.new_page(viewport={'width':844,'height':390});p.set_default_timeout(6000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(status=200,content_type='application/javascript',body=SOURCE.replace('// SOURCE: 99-instrumentation.js',PROBE+EXTRA+'\n// SOURCE: 99-instrumentation.js')));p.goto('http://127.0.0.1:'+str(server.server_port)+'/assets/index.html');p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townTest.load(s)',original['save']);r={'kind':kind,'source_sha256':SHA,'before':p.evaluate('__playAudit.facts()'),'observations':[],'errors':errors}
    def panel(tab):
     if p.locator('#panel').evaluate('e=>e.classList.contains("show")')and'active'in(p.locator('[data-panel='+tab+']').get_attribute('class')or''):return
     p.locator('[data-panel='+tab+']').click()
    def advance(days):
     target=p.evaluate('__townTest.get().day')+days
     while p.evaluate('__townTest.get().day')<target:
      a=p.evaluate('n=>__playAudit.advance(n)',min(15,target-p.evaluate('__townTest.get().day')))
      if a['pending']:p.locator('#eventDefer').click()
    try:
     if kind=='port':
      dock=original['newDock'];panel('economy');p.locator('#portFreightOffice').evaluate('e=>e.open=true');r['currentDockComparison']=p.locator('#portFreightOffice').inner_text();button=p.locator('[data-port-dock="'+str(dock)+'"][data-port-direction=import]:not([disabled])').first;button.click();r['paidReview']=p.locator('#eventText').inner_text();before=p.evaluate('__townTest.save()');p.keyboard.press('Escape');r['cancelNoFinancialChange']=p.evaluate('__townTest.save()')==before
      p.locator('#portFreightOffice').evaluate('e=>e.open=true');p.locator('[data-port-dock="'+str(dock)+'"][data-port-direction=import]:not([disabled])').first.click();before=p.evaluate('__corrected.shipments().serial');p.locator('[data-event-choice="0"]').click();r['newPaidOrders']=p.evaluate('id=>__corrected.shipments().shipments.filter(o=>o.id>id)',before);r['targetTrace']=[];ids=[o['id']for o in r['newPaidOrders']]
      for _ in range(35):
       advance(1);r['targetTrace'].append(p.evaluate('ids=>({day:__townTest.get().day,pending:__corrected.shipments().shipments.filter(o=>ids.includes(o.id)),recent:__corrected.shipments().recent.filter(o=>ids.includes(o.id)),ports:__corrected.ports()})',ids))
      r['arrivals']=list({o['id']:o for row in r['targetTrace']for o in row['recent']if o['status']=='Delivered'}.values());r['after']=p.evaluate('__playAudit.facts()');r['portsAfter']=p.evaluate('__corrected.ports()');panel('economy');p.locator('#portFreightOffice').evaluate('e=>e.open=true');p.locator('#portFreightOffice').scroll_into_view_if_needed();p.screenshot(path=str(OUT/'port-paid-recovery.png'))
     else:
      panel('overview');r['visibleCashRunway']=p.locator('#panelBody').inner_text();panel('policies');settings={'incomeTax':18,'profitTax':18,'educationBudget':210,'healthBudget':140}
      for key,value in settings.items():
       e=p.locator('[data-policy='+key+']');e.evaluate('e=>e.closest("details").open=true');e.fill(str(value))
      p.locator('#enactPolicy').click();panel('treasury');p.locator('#borrow').click();r['reviewedPolicyRecovery']=settings;r['afterOneOrdinaryBorrow']=p.evaluate('__townTest.get()')
      for _ in range(3):advance(30);r['observations'].append(p.evaluate('__playAudit.facts()'))
      r['after']=p.evaluate('__playAudit.facts()');panel('overview');p.screenshot(path=str(OUT/'district-real-runway-recovery.png'))
     r['status']='Real controls and settlement completed';r['valid']=p.evaluate('__townTest.validate()')
    except Exception as e:r['status']='Blocked/uncertain';r['reason']=str(e).split('Call log:')[0];r['after']=p.evaluate('__playAudit.facts()')
    results.append(r);p.close()
   b.close()
 finally:server.shutdown()
 with gzip.open(OUT/'recovery.json.gz','wt')as f:json.dump(results,f)
 print([(r['kind'],r['status'],r.get('reason'))for r in results])
if __name__=='__main__':main()
