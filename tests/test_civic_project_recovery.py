"""Both food strategies and a school promise achieve real paid outcomes; recovery is explicit."""
from pathlib import Path
import functools,http.server,threading,json,hashlib,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
OUT=ROOT/'reports/civic-projects';OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':844,'height':390});page.set_default_timeout(8000)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:'+str(server.server_port)+'/assets/index.html');page.locator('#townSeed').fill('42');page.locator('#newTown').click();page.locator('#pause').click()
 state=lambda:page.evaluate('JSON.parse(__townTest.save())')
 total=page.evaluate('__townTest.get().total')
 page.locator('[data-civic-projects]').click();page.locator('[data-civic-project-review=food]').click();page.locator('[data-event-choice="0"]').click()
 # An explicit real import restriction blocks this route without charging the shop.
 page.locator('[data-panel=policies]').click();page.locator('#tradeToggle').click();page.locator('#enactPolicy').click()
 page.locator('[data-panel=overview]').click();page.locator('[data-civic-projects]').click();assert page.locator('[data-civic-project-order]').is_disabled()
 before=state();page.locator('[data-civic-project-replan=food]').click();page.locator('[data-event-choice="1"]').click();assert state()['treasury']==before['treasury'];assert state()['civicProjects']['history'][-1]['status']=='replanned'
 # Local production offers a distinct capital-and-labour commitment under closed imports.
 page.locator('[data-civic-project-build=bakery]').click();coords=[int(n) for n in re.search(r'grid (\d+), (\d+)',page.locator('#eventTitle').inner_text()).groups()];page.locator('[data-event-choice="1"]').click()
 # Cancelling a surveyed build consumes no capital and clears the placement tool.
 page.keyboard.press('Escape');assert state()['treasury']==before['treasury'];assert state()['civicProjects']['active']['food']['firm'] is None
 page.locator('[data-panel=overview]').click();page.locator('[data-civic-projects]').click();page.locator('[data-civic-project-build=bakery]').click();page.locator('[data-event-choice="1"]').click()
 camera=page.evaluate('__townTest.view().camera');box=page.locator('#view').bounding_box();grid=state()['gridSize'];x,y=coords
 sx=box['x']+box['width']/2+camera['zoom']*((x-y)*36+(grid*72+140)/2-camera['x']);sy=box['y']+box['height']/2+camera['zoom']*((x+y)*18+50-camera['y'])
 page.mouse.click(sx,sy);commissioned=state();firm_id=commissioned['civicProjects']['active']['food']['firm'];assert firm_id is not None
 assert abs(before['treasury']-commissioned['treasury']-3600+commissioned['policy']['permitFee'])<.001
 page.evaluate('__townTest.step(60)');local=state()['civicProjects']['active']['food']
 # This constraint may not support a profitable bakery: report the result honestly, then recover.
 local_under_restriction=local.copy()
 if local['status']!='complete':
  page.locator('[data-panel=overview]').click();page.locator('[data-civic-projects]').click();assert page.locator('[data-project-card=food] .civic-project-setback').count() or local['net']>=0
  page.locator('[data-panel=policies]').click();page.locator('#tradeToggle').click();page.locator('#enactPolicy').click();page.evaluate('__townTest.step(90)');local=state()['civicProjects']['active']['food']
 assert local['status']=='complete',local
 assert local['output']>=120 and local['sales']>=100 and local['net']>=0 and local['proof']
 assert len(state()['firms'])>=len(commissioned['firms'])
 # Fund a real adult term, preserving the teaching promise while doing other projects.
 page.locator('[data-panel=overview]').click();page.locator('[data-civic-projects]').click();page.locator('[data-civic-project-review=skills]').click();page.locator('[data-event-choice="0"]').click();start=state()
 page.locator('[data-civic-project-budget]').click();page.locator('[data-event-choice="0"]').click();page.locator('#enactPolicy').click()
 page.evaluate('__townTest.step(180)');after=state();skills=after['civicProjects']['active']['skills'];assert skills['status']=='complete',skills
 assert after.get('civicTrainingCompletions',0)>skills['trainingBaseline'];assert skills['proof']
 assert abs(page.evaluate('__townTest.get().total')-total)<.01;assert page.evaluate('__townTest.validate().ok')
 # Historical proof stays stable through later policy changes and an archive restoration.
 proof=skills['proof'];saved=page.evaluate('__townTest.save()');page.evaluate('__townTest.step(10)');assert state()['civicProjects']['active']['skills']['proof']==proof
 assert page.evaluate('(s)=>__townTest.load(s)',saved)
 # Restoring while a survey is open clears its transient selectors and focus layer.
 page.locator('[data-panel=agenda]').click();page.locator('[data-civic-project-review=district]').click();assert page.locator('#projectParcel').count()==1
 assert page.evaluate('(s)=>__townTest.load(s)',saved);assert page.locator('.civic-project-survey').count()==0;assert page.locator('#eventDialog').is_hidden()
 assert not errors,errors
 (OUT/'recovery.json').write_text(json.dumps({'source_sha256':hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest(),'realPolicyRestriction':True,'replannedWithoutRefund':True,'localUnderClosedImports':local_under_restriction,'localCertificate':local,'skillsCertificate':skills,'trainingTermsCompleted':after.get('civicTrainingCompletions',0),'foodSiteCost':3600,'additionalTeachingDaily':after['policy']['educationBudget']-start['policy']['educationBudget'],'moneyDrift':page.evaluate('__townTest.get().total')-total,'errors':errors},indent=2)+'\n')
 print('PASS distinct local-production strategy, actual import restriction and replanning, paid bakery output/sales/cost recovery, adult training and usable access certificate, conserved cash, stable historical proof and survey cleanup on restore',flush=True)
 b.close()
server.shutdown()
