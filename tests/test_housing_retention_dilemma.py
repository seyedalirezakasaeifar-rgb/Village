"""A conditional council choice stays tied to one real household and quote."""
from pathlib import Path
import json
from math import ceil
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html

source=(ROOT/'assets/game.js').read_text()
probe='''window.__retention={
 risk:()=>{const h=G.households.find(h=>h.people.length);if(!h)return null;h.cash=0;h.stress=90;h.worklessness=90;h.income=0;h.incomeTax=0;h.netIncomeTrend=0;h.deposits={};G.day=Math.max(30,G.day);return {id:h.id,name:h.name,a:migrationEmigrationAssessment(h)};},
 offer:offerHousingRetentionDilemma, review:reviewCouncilInbox, skills:()=>G.civicProjects?.active?.skills, agenda:()=>openPanel('agenda'), cash:(id,n)=>G.households[id].cash=n,
 total:totalMoney, household:id=>({cash:G.households[id].cash,name:G.households[id].name}),state:()=>G.councilInbox
};
// SOURCE: 99-instrumentation.js'''
source=source.replace('// SOURCE: 99-instrumentation.js',probe)

with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':844,'height':390},has_touch=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html);page.add_script_tag(content=source)
 page.locator('#townSeed').fill('42');page.locator('#newTown').click();page.locator('#pause').click()
 def start_case():
  item=page.evaluate('__retention.risk()');assert item and item['a']['eligible'],item
  assert page.evaluate('__retention.offer()')
  return item
 def open_case():
  page.evaluate('__retention.agenda()')
  assert page.locator('[data-inbox="0"]').inner_text()=='Review and decide'
  page.locator('[data-inbox="0"]').click()
  assert page.locator('#eventTitle').inner_text().startswith('A household may leave: ')

 # The inbox record survives save/load; defer preserves the same case.
 case=start_case();saved=page.evaluate('__townTest.save()');assert page.evaluate('s=>__townTest.load(s)',saved)
 open_case();text=page.locator('#eventText').inner_text()
 assert case['name'] in text and 'local prospects' in text and 'outside comparison' in text
 bridge=page.locator('[data-event-choice="0"]');bridge_text=bridge.inner_text()
 amount=int(bridge_text.split('$')[1].replace(',','').split()[0])
 assert amount==ceil(min(3000,max(1,-case['a']['localSurplus']*14))), (amount,case['a'])
 page.locator('#eventDefer').click();assert not page.locator('#eventDialog').is_visible()
 assert page.evaluate('__retention.state()[0].retentionHousehold')==case['id']
 open_case();page.locator('[data-event-choice="1"]').click()
 project=page.evaluate('__retention.skills()')
 assert project['target']==case['id'] and project['branch']=='network'
 assert not any(x['title'].startswith('A household may leave: ') for x in page.evaluate('__retention.state()'))

 # A separate run chooses the immediate cash bridge. The exact amount goes
 # from city reserve to the named household, conserving combined cash once.
 page.evaluate("__townTest.reset('settlement',42)")
 case=start_case();cash=page.evaluate('__townTest.get().treasury');house_cash=page.evaluate('id=>__retention.household(id).cash',case['id']);total=page.evaluate('__retention.total()')
 open_case();displayed=page.locator('[data-event-choice="0"]').inner_text();amount=int(displayed.split('$')[1].replace(',','').split()[0])
 page.locator('[data-event-choice="0"]').click()
 assert cash-page.evaluate('__townTest.get().treasury')==amount
 assert page.evaluate('id=>__retention.household(id).cash',case['id'])-house_cash==amount
 assert abs(page.evaluate('__retention.total()')-total)<.001
 assert not any(x['title'].startswith('A household may leave: ') for x in page.evaluate('__retention.state()'))
 assert page.evaluate('__townTest.validate().ok')

 # The offer rechecks the household's current condition before a debit.
 page.evaluate("__townTest.reset('settlement',42)")
 case=start_case();cash=page.evaluate('__townTest.get().treasury');open_case()
 page.evaluate('(id)=>__retention.cash(id,9000)',case['id'])
 page.locator('[data-event-choice="0"]').click()
 assert page.evaluate('__townTest.get().treasury')==cash
 assert not page.locator('#eventDialog').is_visible()
 assert any(x['title'].startswith('A household may leave: ') for x in page.evaluate('__retention.state()'))
 page.locator('[data-inbox="0"]').click()
 assert not page.locator('#eventDialog').is_visible()
 assert not any(x['title'].startswith('A household may leave: ') for x in page.evaluate('__retention.state()'))
 assert not errors,errors
 browser.close()
print('PASS pressure-triggered correspondence, save/load and defer, distinct cash-bridge/training paths, exact conserved transfer, stale-quote rejection')
