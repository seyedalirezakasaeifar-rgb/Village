"""Five-year randomized scenario endurance, economic conservation, and state invariants."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import math,time
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage']);page=b.new_page(viewport={'width':844,'height':390})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 html=(root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
 page.set_content(html);page.add_script_tag(content=(root/'assets/game.js').read_text())
 for sc in ['settlement','hardtimes','frontier','industrial']:
  page.evaluate('(sc)=>__townTest.reset(sc)',sc)
  before=page.evaluate('__townTest.get().total')
  t=time.perf_counter();page.evaluate('__townTest.step(1800)');elapsed=time.perf_counter()-t
  result=page.evaluate('''() => {let g=JSON.parse(__townTest.save()); return {day:g.day,pop:g.stats.population,people:g.people.length,home:g.households.length,active:g.firms.filter(f=>!f.closed).length, cases:g.cases.length, council:g.council.approval, elections:g.council.elections, total:__townTest.get().total, minCash:Math.min(...g.firms.map(f=>f.cash), ...g.households.map(h=>h.cash),g.treasury), nanStats:Object.entries(g.stats).filter(([k,v])=>typeof v==='number'&&!Number.isFinite(v)), missingWorkers:g.firms.filter(f=>f.workers.some(id=>!g.people[id]||g.people[id].deceased)).map(f=>f.name), invalidOwners:g.buildings.filter(b=>b.owner>=g.households.length).length, unfilledFamilies:g.households.filter(h=>h.people.length===0).length, news:g.events.length, achieved:g.achievements.length}}''')
  print(sc,round(elapsed,2),'s',result,flush=True)
  assert abs(result['total']-before)<5,(sc,'money leak',result['total']-before)
  assert result['day']==1801 and result['pop']>75 and result['active']>=0
  assert result['elections']>=4 and not result['nanStats'] and not result['missingWorkers'] and result['invalidOwners']==0
  assert result['minCash']>=-1e-5 and not errors,errors
 print('PASS: four five-year scenarios maintained data integrity')
 b.close()
