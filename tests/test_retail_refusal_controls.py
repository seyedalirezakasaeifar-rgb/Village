"""Actual invitation on earned two-year city explains its pending funded project."""
import gzip,hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text();archive=gzip.decompress((ROOT/'tests/fixtures/retail-refusal-pending-project.json.gz').read_bytes()).decode()
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townTest.load(s)',archive)
 p.locator('[data-panel=construction]').click();p.locator('#urbanPlanningOffice>summary').click();before=p.evaluate('__townTest.save()');state=json.loads(before);assert state['day']==721 and state['stats']['population']==765 and any(q.get('retailCentre')for q in state['projects'])
 p.locator('[data-urban-retail]').click();text=p.locator('#toast').inner_text();assert text=='A retail centre is already under construction. Let its funded project finish before inviting another.',text
 assert p.evaluate('__townTest.save()')==before and p.locator('#eventDialog').is_hidden() and not errors
 print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'fixture':'d2b7086 regional seed42 day721; two ordinary-resource years, no grants','day':state['day'],'population':state['stats']['population'],'visibleReason':text,'completeArchiveUnchanged':True,'errors':errors},indent=2));b.close()
