"""6.0 regression gates against the actual assembled browser game, not mocks."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, os, time, hashlib

ROOT=Path(__file__).resolve().parents[1]
reports=Path(os.environ.get('TOWNLEDGER_REPORTS',str(ROOT/'reports')))
reports.mkdir(exist_ok=True)
results={}
def record(name,value):
    results[name]=value
    (reports/'release-tests.json').write_text(json.dumps(results,indent=2)+'\n')
    print(name,json.dumps(value)[:1800],flush=True)

record('source_sha256',hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest())
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files'])
    page=browser.new_page(viewport={'width':1280,'height':720})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'assets/index.html').as_uri())
    page.locator('#newTown').click()
    page.locator('#panelClose').click()
    page.locator('#pause').click()
    assert page.locator('#pauseBanner').is_visible()
    record('determinism_and_continuation',page.evaluate('''()=>{
       function core(){const g=JSON.parse(__townTest.save());delete g.trafficState;delete g.visualState;return JSON.stringify(g,Object.keys(g).sort());}
       function normalized(){const g=JSON.parse(__townTest.save());delete g.trafficState;delete g.visualState;return g;}
       __townTest.reset('settlement',101);__townTest.step(180);const a=normalized();
       __townTest.reset('settlement',101);__townTest.renderBench(80);__townTest.step(180);const b=normalized();
       if(JSON.stringify(a)!==JSON.stringify(b))throw Error('Economic replay changed with rendering');
       const saved=__townTest.save();__townTest.step(120);const end=normalized();
       if(!__townTest.load(saved))throw Error('Save rejected');__townTest.step(120);const replay=normalized();
       // Object key insertion order may differ during migration, so compare recursively.
       function canonical(v){if(Array.isArray(v))return v.map(canonical);if(v&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])]));return v;}
       if(JSON.stringify(canonical(end))!==JSON.stringify(canonical(replay))){const changed=[...new Set([...Object.keys(end),...Object.keys(replay)])].filter(k=>JSON.stringify(canonical(end[k]))!==JSON.stringify(canonical(replay[k])));throw Error('Continuation differs: '+changed.join(','));}
       return {sameSeed:true,renderIndependent:true,continuedDays:120,valid:__townTest.validate()};
    }'''))
    record('malformed_save_atomicity',page.evaluate('''()=>{
      const original=__townTest.save(),g=JSON.parse(original);g.investors[0].cash=-10;
      if(__townTest.load(g))throw Error('Negative investor accepted');
      if(__townTest.save()!==original)throw Error('Rejected save changed live town');
      const f=JSON.parse(original);f.freight=[{from:999999,to:1,good:'food',qty:2,remaining:1}];
      if(__townTest.load(f))throw Error('Orphan shipment accepted');
      const future=JSON.parse(original);future.schema=99;if(__townTest.load(future))throw Error('Future schema accepted');
      return {investorRejected:true,cargoRejected:true,futureRejected:true,townPreserved:true};
    }'''))
    # Compare the same initial agents, terrain and random stream at each zoning rule.
    sensitivity=[]
    for seed in [42,101,909]:
      for zone in [0,100]:
        row=page.evaluate('''({seed,zone})=>{__townTest.reset('settlement',seed);__townTest.set('zoningRestriction',zone);const total=__townTest.get().total,t=performance.now();__townTest.step(720);const g=JSON.parse(__townTest.save());const valid=__townTest.validate();if(!valid.ok)throw Error(valid.issues.join(';'));if(Math.abs(total-valid.total)>.05)throw Error('Cash drift');return {seed,zone,population:g.stats.population,homes:g.development.homes,firms:g.development.firms,privateSpend:g.development.privateSpend||0,moneyDelta:valid.total-total,ms:performance.now()-t};}''',{'seed':seed,'zone':zone})
        sensitivity.append(row)
      assert sensitivity[-2]['homes']>sensitivity[-1]['homes']
    record('replicated_zoning',sensitivity)
    # Economic cargo remains reserved in flight, even when the road is severed.
    record('cargo_ownership',page.evaluate('''()=>{
      __townTest.reset('settlement',42);__townTest.step(2);let g=JSON.parse(__townTest.save());
      if(!g.freight.length)throw Error('No real consignments');
      const s=g.freight.find(s=>s.path.length>4);if(!s)throw Error('No routed shipment');
      const before=__townTest.get().total,qty=s.qty,freightId=s.id;
      const from=g.firms[s.from],site=g.buildings.find(b=>b.id===from.building);
      const footprint=site.footprint||[site.y*56+site.x];for(const id of footprint){for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const n=id+dx+dy*56;if(g.tiles[n]===1)g.tiles[n]=0;}}
      if(!__townTest.load(g))throw Error('Severed road town rejected');__townTest.step(1);
      const after=JSON.parse(__townTest.save());const held=after.freight.find(x=>x.id===freightId);
      // Alternative access may exist, so a delay is not guaranteed in this town.
      if(!held||held.qty!==qty||held.delayed<1)throw Error('Blocked cargo was not retained with its owner');
      if(Math.abs(__townTest.get().total-before)>.05)throw Error('Cargo route break created money');
      return {consignments:g.freight.length,sampledUnits:qty,remaining:!!held,delayed:held?.delayed||0,cashConserved:true};
    }'''))
    # Restore an unmodified 5.6 save produced by the supplied baseline.
    old=browser.new_page()
    old.goto((ROOT/'reference/v5.6/assets/index.html').as_uri())
    old.locator('#newTown').click()
    legacy=old.evaluate('__townTest.save()')
    previous=json.loads(legacy)
    assert page.evaluate('(text)=>__townTest.load(text)',legacy)
    migrated=page.evaluate('''()=>{const v=__townTest.validate();__townTest.step(30);return {v,after:__townTest.validate(),schema:JSON.parse(__townTest.save()).schema}}''')
    assert migrated['v']['population']==previous['stats']['population'] and migrated['after']['ok']
    record('legacy_56_migration',migrated)
    old.close()
    # Pause must preserve the rendered world and transport positions.
    page.evaluate("__townTest.reset('settlement',42)")
    first=page.screenshot()
    page.wait_for_timeout(500)
    second=page.screenshot()
    assert first==second,'Paused view changed'
    record('true_pause',{'identicalScreenshots':True,'milliseconds':500})
    page.locator('#pause').click()
    traffic=page.evaluate('''()=>{
      __townTest.reset('settlement',42);let maximumWait=0,peak=0,completed=0;
      for(let i=0;i<16000;i++){__townTest.advanceTraffic(.10);const cars=__townTest.traffic();maximumWait=Math.max(maximumWait,...cars.map(v=>v.wait||0));peak=Math.max(peak,cars.length);}
      const v=__townTest.validate();if(!v.ok)throw Error(v.issues.join(';'));if(maximumWait>30)throw Error('Persistent traffic blockage '+maximumWait);
      return {seconds:1600,maximumWait,peak,valid:v.ok};
    }''')
    record('traffic_progress',traffic)
    page.locator('#pause').click()
    endurance=[]
    for scenario,seed,years,zone in ([] if os.environ.get('TOWNLEDGER_CORE_ONLY') else [('settlement',42,50,25),('frontier',101,25,0),('industrial',909,25,15),('hardtimes',42,10,55),('regional',42,5,20)]):
      page.evaluate('''({scenario,seed,zone})=>{__townTest.reset(scenario,seed);__townTest.set('zoningRestriction',zone)}''',{'scenario':scenario,'seed':seed,'zone':zone})
      total=page.evaluate('__townTest.get().total')
      start=time.perf_counter()
      for year in range(0,years,5):
        out=page.evaluate('''()=>{__townTest.step(1800);let g=JSON.parse(__townTest.save()),v=__townTest.validate();if(!v.ok)throw Error(v.issues.join(';'));return {day:g.day,population:g.stats.population,homes:g.development.homes,redevelopments:g.development.redevelopments,towers:g.development.towers,airfields:g.development.airfields,stations:g.development.stations,openFirms:g.stats.businesses,failures:g.finance.failures,total:v.total,peakDrift:g.accounts.maxError}}''')
        assert abs(out['total']-total)<.1
        print('endurance checkpoint',scenario,year+5,out,flush=True)
      out.update(scenario=scenario,seed=seed,years=years,seconds=time.perf_counter()-start)
      endurance.append(out)
      (reports/(scenario+'-endurance-town.json')).write_text(page.evaluate('__townTest.save()'))
    record('long_run_endurance',endurance)
    if endurance:
      regional=endurance[-1]
      assert regional['towers']>0 and regional['airfields']>0 and regional['stations']>=2,regional
    assert not errors,errors
    record('browser_errors',errors)
    browser.close()
print('PASS release gates',flush=True)
