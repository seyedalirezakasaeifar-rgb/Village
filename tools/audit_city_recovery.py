#!/usr/bin/env python3
"""Read-only acceptance continuation: operate actual recovery controls on audited saves."""
import gzip,json,time,threading,functools,http.server,sys
from playwright.sync_api import sync_playwright
from audit_three_cities import ROOT,OUT,SOURCE,SHA,PROBE,EXTRA,Quiet

def main():
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
 try:
  with sync_playwright()as pw:
   b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
   for strategy in (sys.argv[1:]or['port','transit','local']):
    original=json.load(gzip.open(OUT/(strategy+'.json.gz')));p=b.new_page(viewport={'width':844,'height':390});p.set_default_timeout(6000);p.route('**/game.js',lambda r:r.fulfill(status=200,content_type='application/javascript',body=SOURCE.replace('// SOURCE: 99-instrumentation.js',PROBE+EXTRA+'\n// SOURCE: 99-instrumentation.js')));p.goto('http://127.0.0.1:'+str(server.server_port)+'/assets/index.html');p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townTest.load(s)',original['save']);r={'strategy':strategy,'source_sha256':SHA,'before':p.evaluate('__playAudit.facts()')}
    def panel(tab):
     p.keyboard.press('Escape');p.locator('[data-panel='+tab+']').click()
    try:
     if strategy=='port':
      r['reviewSteps']=[];beforeOpen=sum(f['kind']=='wharf'and not f['closed']for f in r['before']['firms'])
      for attempt in range(3):
       panel('overview');p.locator('[data-civic-projects]').click();r['availableRecoveryText']=p.locator('#panelBody').inner_text();p.locator('[data-civic-project-build=wharf]').first.click();r['reviewSteps'].append(p.locator('#eventText').inner_text());p.locator('[data-event-choice="0"]').click()
       current=p.evaluate('__playAudit.facts()')
       if sum(f['kind']=='wharf'and not f['closed']for f in current['firms'])>beforeOpen:break
     elif strategy=='transit':
      panel('construction');button=p.locator('[data-transit-level$=":0"]').first;button.evaluate('e=>e.closest("details").open=true');button.click();r['suspended']=p.evaluate('__three.extra().transit');panel('construction');button=p.locator('[data-transit-level$=":2"]').first;button.evaluate('e=>e.closest("details").open=true');button.click();r['frequencyPreview']=p.locator('.transit-office').inner_text();build=p.locator('[data-transit-action=build]');
      if build.count():build.click()
     else:
      panel('overview');p.locator('[data-civic-projects]').click();r['availableProjects']=p.locator('#panelBody').inner_text();r['continuation']='Inspect actual school/care gap and public reserve; no repeated household counter adopted.'
      r['gap']=p.evaluate('__playAudit.facts().districts');r['placementAttempts']=[]
      for kind in ['home','home','home','home','clinic','school']:
       lot=p.evaluate('kind=>__playAudit.lot(kind,"orchard-downs")',kind)
       if not lot:r['placementAttempts'].append({'kind':kind,'reason':'No legal connected lot inside actual project tract'});continue
       panel('construction');p.locator('[data-build-category='+('housing'if kind=='home'else'services')+']').click();p.locator('[data-build='+kind+']').click();a=p.evaluate('o=>__three.point(o.x,o.y)',lot);p.evaluate('a=>__townTest.capture({x:a[0],y:a[1]+18,zoom:.85})',a['world']);a=p.evaluate('o=>__three.point(o.x,o.y)',lot);p.mouse.click(a['x'],a['y']);p.keyboard.press('Escape');r['placementAttempts'].append({'kind':kind,'lot':lot,'cash':p.evaluate('__townTest.get().treasury')})
     target=p.evaluate('__townTest.get().day')+60
     while p.evaluate('__townTest.get().day')<target:
      a=p.evaluate('n=>__playAudit.advance(n)',min(15,target-p.evaluate('__townTest.get().day')))
      if a['pending']:p.locator('#eventDefer').click()
     r['after']=p.evaluate('__playAudit.facts()');r['transitAfter']=p.evaluate('__three.extra().transit');r['result']='real controls and sixty further settlement days completed'
    except Exception as e:r['result']='Recovery blocked/uncertain';r['reason']=str(e).split('Call log:')[0];r['after']=p.evaluate('__playAudit.facts()')
    p.screenshot(path=str(OUT/(strategy+'-recovery.png')));results.append(r);p.close()
   b.close()
 finally:server.shutdown()
 with gzip.open(OUT/((sys.argv[1]+'-recovery.json.gz')if len(sys.argv)==2 else'recovery.json.gz'),'wt')as f:json.dump(results,f)
 print([(r['strategy'],r['result'],r.get('reason'))for r in results])
if __name__=='__main__':main()
