"""Real requestAnimationFrame and UI latency test at 2,000 residents / 64x.

Uses an authored synthetic upper-bound town so the test is reproducible and
does not depend on generated endurance-report files. Results are host-browser
measurements, not native Android FPS claims.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import hashlib
import math
import time
import os

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'assets/index.html').read_text()
HTML = HTML.replace(
    '<link rel="stylesheet" href="style.css">',
    '<style>' + (ROOT / 'assets/style.css').read_text() + '</style>',
).replace('<script src="game.js"></script>', '')

# Include every shipped stylesheet; set_content has no asset base URL.
for sheet in ['vale.css','civic7.css','mayor8.css']:
    HTML=HTML.replace('<link rel="stylesheet" href="'+sheet+'">','<style>'+(ROOT/'assets'/sheet).read_text()+'</style>')


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.floor(len(ordered) * fraction))]


def test_live_large_town_ui_and_render_budget():
    source=(ROOT/'assets/game.js').read_bytes();source_sha=hashlib.sha256(source).hexdigest()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path='/usr/bin/chromium',
            args=['--no-sandbox', '--disable-dev-shm-usage'],
        )
        page = browser.new_page(
            viewport={'width': 844, 'height': 390}, device_scale_factor=1
        )
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content(HTML)
        bundle=source.decode()
        if os.environ.get('TOWNLEDGER_LIVE_TRANSIT')=='1':bundle=bundle.replace('// SOURCE: 99-instrumentation.js',(ROOT/'tools/qa_live_network.js').read_text()+'\n// SOURCE: 99-instrumentation.js')
        if os.environ.get('TOWNLEDGER_LIVE_PROFILE')=='1':bundle=bundle.replace('// SOURCE: 99-instrumentation.js',(ROOT/'tools/qa_render_profile.js').read_text()+'\n// SOURCE: 99-instrumentation.js')
        page.add_script_tag(content=bundle)
        page.locator('#newTown').click()
        page.locator('#pause').click()
        town = page.evaluate('''()=>{
          __townTest.reset('settlement',42);
          const g=JSON.parse(__townTest.save());
          const occupied=new Set(g.buildings.flatMap(b=>b.footprint||[b.y*g.gridSize+b.x]));
          const free=[];
          for(let y=3;y<53;y++)for(let x=3;x<53;x++){
            const id=y*g.gridSize+x;
            if(g.tiles[id]===0&&!occupied.has(id)&&!g.landUse?.[id])free.push([x,y]);
          }
          let n=0;
          while(g.people.length<2000&&n<free.length){
            const [x,y]=free[n],id=g.households.length;
            const household={id,name:'Newcomer '+n,cash:500,home:g.nextId,owner:id,
              people:[],income:0,rent:0,food:0,tax:0,aid:0,crimeLoss:0,stress:25,
              security:80,last:[],worklessness:0};
            const building={id:g.nextId++,kind:'home',x,y,value:25000,condition:100,
              owner:id,firm:-1,hh:id};
            g.buildings.push(building);g.homes.push(building.id);
            g.households.push(household);g.region-=500;
            for(let age=0;age<3&&g.people.length<2000;age++){
              const personId=g.people.length;
              g.people.push({id:personId,name:'Resident '+personId,age:26+age*3,
                skill:.5,health:80,hh:id,job:-1,life:70,last:[]});
              household.people.push(personId);
            }
            n++;
          }
          if(g.people.length!==2000||!__townTest.load(g))
            throw Error('Could not load the synthetic 2,000-resident town');
          return {population:g.people.length,households:g.households.length,
            buildings:g.buildings.length,total:__townTest.get().total};
        }''')
        network=page.evaluate('__liveNetworkBuild()') if os.environ.get('TOWNLEDGER_LIVE_TRANSIT')=='1' else None
        if network:town['total']=network['total']
        zoom=float(os.environ.get('TOWNLEDGER_LIVE_ZOOM','.95'))
        page.evaluate('(zoom)=>__townTest.capture({zoom})',zoom)
        page.locator('#panelClose').click()
        page.locator('#speedRange').fill('6')
        page.locator('#pause').click()
        page.wait_for_timeout(700)
        # Measure the warmed interval; retain founding/loading costs separately.
        startup = page.evaluate('''()=>{const p=__townTest.perf(),r={frames:p.frames.slice(),ticks:p.ticks.slice()};p.frames.length=0;p.ticks.length=0;if(window.__liveProfile)window.__liveProfile={};return r;}''')
        start = page.evaluate('__townTest.get()')
        wall_start = time.perf_counter()
        raf = page.evaluate('''()=>new Promise(resolve=>{
          const times=[];let previous=0,started=performance.now();
          function sample(now){
            if(previous)times.push(now-previous);previous=now;
            if(now-started<8000)requestAnimationFrame(sample);
            else resolve(times);
          }
          requestAnimationFrame(sample);
        })''')
        elapsed = time.perf_counter() - wall_start
        end = page.evaluate('__townTest.get()')
        renderer = page.evaluate('''()=>{
          const p=__townTest.perf(),q=(a,t)=>{
            const sorted=a.slice().sort((x,y)=>x-y);
            return sorted[Math.min(sorted.length-1,Math.floor(sorted.length*t))]||0;
          };
          return {drawCount:p.frames.length,drawMedianMs:q(p.frames,.5),
            drawP95Ms:q(p.frames,.95),drawP99Ms:q(p.frames,.99),
            tickMedianMs:q(p.ticks,.5),tickP95Ms:q(p.ticks,.95),
            actualSpeed:p.effective,backlogDays:p.backlog};
        }''')
        ui = []
        for selector in [
            '[data-panel=economy]', '[data-panel=citizens]',
            '[data-panel=businesses]', '[data-panel=settings]',
        ]:
            latency = page.evaluate('''selector=>{
              const button=document.querySelector(selector),start=performance.now();
              button.click();
              return new Promise(resolve=>requestAnimationFrame(()=>
                resolve(performance.now()-start)));
            }''', selector)
            body = page.locator('#panelBody').inner_text()
            ui.append({'panel': selector, 'toNextFrameMs': latency,
                       'panelError': 'Panel error' in body})
            page.locator('#panelClose').click()
        conservation = abs(end['total'] - town['total'])
        assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==source_sha
        result = {
            'source_sha256':source_sha,
            'camera':page.evaluate('__townTest.view().camera'),'viewport': [844, 390], 'network':network,'networkEnd':page.evaluate('__liveNetworkStatus()') if network else None,'zoom':zoom, 'synthetic': town, 'requestedSpeed': 64,
            'elapsedSeconds': elapsed, 'simulatedDays': end['day'] - start['day'],
            'rafP50Ms': percentile(raf, .50), 'rafP95Ms': percentile(raf, .95),
            'rafP99Ms': percentile(raf, .99),
            'rafOver50ms': sum(value > 50 for value in raf),
            'profile':page.evaluate('window.__liveProfile||null'),'renderer': renderer, 'ui': ui, 'foundingAndWarmup':startup,
            'moneyConservationDrift': conservation, 'errors': errors,
        }
        report_path = ROOT / 'reports/v7.0/live-large-town.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(result, indent=2) + '\n'
        )
        assert town['population'] == 2000
        assert result['simulatedDays'] >= 100
        assert conservation < .1
        assert all(not row['panelError'] for row in ui), ui
        assert not errors, errors
        assert renderer['drawP95Ms'] < 50, renderer
        # Paint-only acceptance missed a real service-lookup regression: the
        # renderer passed while simulation fell to 7x and RAF stalled for 1.45s.
        # These remain isolated host checks, not physical Android guarantees.
        assert renderer['actualSpeed'] >= 40, renderer
        assert result['rafP99Ms'] < 500, result['rafP99Ms']
        assert all(row['toNextFrameMs'] < 250 for row in ui), ui
        browser.close()
        print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    test_live_large_town_ui_and_render_budget()
