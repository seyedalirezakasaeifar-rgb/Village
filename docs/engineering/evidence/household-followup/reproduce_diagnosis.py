import sys,json
sys.path.insert(0,'tests')
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text()
probe='''window.__householdDiagnosis=()=>{const raw=archivePayload(),g=JSON.parse(raw),p=g.people[0],original=g.households[p.hh],target=g.households[(p.hh+1)%g.households.length];const candidate=JSON.parse(raw);candidate.people[0].hh=target.id;return{day:g.day,person:{id:p.id,hh:p.hh,deceased:p.deceased||false,movedAway:p.movedAway||false,job:p.job},original:{id:original.id,members:original.people,home:original.home,cash:original.cash},target:{id:target.id,members:target.people,home:target.home},rostersContaining:g.households.filter(h=>h.people.includes(p.id)).map(h=>h.id),accepted:hydrateSave(candidate)};};'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('hardtimes',42);__townTest.step(720)");print(json.dumps(p.evaluate('__householdDiagnosis()'),indent=2));b.close()
