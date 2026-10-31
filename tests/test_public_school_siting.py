"""Exercise ordinary public-school siting, funding, access and migration forecasts."""
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright
import hashlib, json

source = (ROOT / 'assets/game.js').read_text()
probe = r'''
window.__schoolSiting=(scenario,seed,mode)=>{
 __townTest.reset(scenario,seed);G.autoBuild=false;G.policy.educationBudget=0;G.policy.defenseBudget=0;
 const homes=G.households.filter(h=>h.people.length).map(h=>({h,b:readBuild(h.home)})).filter(x=>x.b);
 const candidates=[];for(let y=2;y<T-3;y++)for(let x=2;x<T-3;x++)if(canPlace(x,y,true,'school')){
   const probeId=G.nextId, pseudo={id:probeId,kind:'school',x,y,footprint:footprintFor(x,y,'school')};
   // Road distance is measured through the same live network as actual service catchments.
   G.buildings.push(pseudo);invalidateRoads(false);const port=graph().portals.get(probeId),distances=homes.map(({b})=>{const hp=graph().portals.get(b.id);return port==null||hp==null?Infinity:roadDistance(port,hp)}).filter(Number.isFinite);
   G.buildings.pop();invalidateRoads(false);if(distances.length)candidates.push({x,y,mean:distances.reduce((a,b)=>a+b,0)/distances.length,min:Math.min(...distances),max:Math.max(...distances)});
 }
 candidates.sort((a,b)=>a.mean-b.mean);const site=mode==='near'?candidates[0]:candidates[candidates.length-1];if(!site||G.treasury<buildCost.school)throw Error('No ordinary legal school site');
 const preAccess=serviceAccess('school'),pre={schoolAccess:preAccess.coverage,households:homes.length,treasury:G.treasury,facilities:G.buildings.filter(b=>b.kind==='school'&&isPublicFacility(b)).length};construct('school',site.x,site.y,true);
 const school=G.buildings.find(b=>b.kind==='school'&&b.x===site.x&&b.y===site.y);if(!school)throw Error('Ordinary construction did not produce school');
 const afterAccess=serviceAccess('school'),afterBuild={treasury:G.treasury,access:afterAccess,addedReachByHousehold:afterAccess.households.map(h=>({id:h.id,before:preAccess.households.find(v=>v.id===h.id)?.served||0,after:h.served,delta:h.served-(preAccess.households.find(v=>v.id===h.id)?.served||0)})),estimate:publicServiceBudgetEstimate('school'),forecast:homes.map(({h,b})=>({id:h.id,liquidity:migrationSpendable(h).spendable,services:migrationServiceAt(b),assessment:migrationAssessment(b,[{age:12,skill:.5,health:90}],2500).services,access:householdServiceReport(h.id)}))};
 G.policy.educationBudget=1000;G.civicStaffing=G.civicStaffing||{};assignJobs();__townTest.step(1);
 const funded={treasury:G.treasury,provision:G.serviceProvision?.school,access:serviceAccess('school'),school:readBuild(school.id),homeCoverage:homes.map(({h})=>({id:h.id,coverage:localCivicCoverage('school',h.id),migration:migrationAssessment(readBuild(h.home),[{age:12,skill:.5,health:90}],2500).services}))};
 // Isolate this actual school to compare a connected site with the same site after its
 // adjacent street links are interrupted. Other facilities are restored immediately.
 const otherSchools=G.buildings.filter(b=>b.kind==='school'&&b.id!==school.id),allBuildings=G.buildings,schoolRoads=new Set();for(const id of footprintOf(school)){const x=id%T,y=id/T|0;for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const xx=x+dx,yy=y+dy;if(xx>=0&&xx<T&&yy>=0&&yy<T&&G.tiles[roadId(xx,yy)]===1)schoolRoads.add(roadId(xx,yy));}}
 G.buildings=G.buildings.filter(b=>b.kind!=='school'||b.id===school.id);invalidateRoads(false);const isolatedSite={connected:serviceAccess('school').coverage,households:serviceAccess('school').households.map(h=>({id:h.id,served:h.served,distance:h.distance}))};const removedRoadTiles=[...schoolRoads].map(id=>[id,G.tiles[id]]);for(const [id]of removedRoadTiles)G.tiles[id]=0;invalidateRoads(false);const disconnectedSite={connected:serviceAccess('school').coverage,households:serviceAccess('school').households.map(h=>({id:h.id,served:h.served,distance:h.distance}))};for(const [id,tile]of removedRoadTiles)G.tiles[id]=tile;invalidateRoads(false);const reconnectedIsolated=serviceAccess('school').coverage;G.buildings=allBuildings;invalidateRoads(false);const restoredSite=serviceAccess('school').coverage;
 const before=totalMoney(),save=archivePayload();__townTest.step(10);const future=archivePayload();if(!hydrateSave(save))throw Error('School siting archive restore failed');__townTest.step(10);if(archivePayload()!==future)throw Error('School siting replay mismatch');
 const privateBefore=G.firms.filter(f=>f.privateService==='school'&&!f.closed).length;G.policy.educationBudget=0;seekPrivateServiceInvestment('school');const privateInvited=G.projects.filter(p=>p.privateService==='school').map(p=>({remaining:p.remaining,escrow:p.serviceEscrow}));
 return {scenario,seed,mode,site,pre,afterBuild,funded,isolatedSite,disconnectedSite,reconnectedIsolated,restoredSite,disconnectedRoadTiles:removedRoadTiles.length,privateBefore,privateInvited,cashDrift:totalMoney()-before,goods:goodsBalance(),valid:validateTown()};
};'''

rows = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page()
    page.set_default_timeout(180000)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(html)
    page.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js', probe + '\n// SOURCE: 99-instrumentation.js'))
    page.locator('#newTown').click(); page.locator('#pause').click()
    for scenario, seed in [('settlement', 42), ('regional', 42)]:
        for mode in ['near', 'far']:
            row = page.evaluate('o=>__schoolSiting(o.scenario,o.seed,o.mode)', {'scenario':scenario,'seed':seed,'mode':mode})
            assert row['valid']['ok'] and abs(row['cashDrift']) < 1
            assert max(abs(item['error']) for item in row['goods']) < .001
            assert row['funded']['provision']['paid'] <= 1000
            assert abs(row['funded']['provision']['coverage']-row['funded']['provision']['accessCoverage']) < 1e-8
            assert row['disconnectedSite']['connected'] == 0
            assert abs(row['isolatedSite']['connected']-row['reconnectedIsolated']) < 1e-8
            assert all(abs(h['migration']['school']-row['funded']['provision']['coverage']) < 1e-8 for h in row['funded']['homeCoverage'])
            rows.append(row)
            print(scenario, mode, 'school access', row['funded']['access']['coverage'], 'coverage', row['funded']['provision']['coverage'], flush=True)
    settlement = {r['mode']:r for r in rows if r['scenario']=='settlement'}
    assert settlement['near']['isolatedSite']['connected'] > settlement['far']['isolatedSite']['connected']
    assert any(r['privateInvited'] for r in rows if r['scenario']=='regional')
    assert not errors, errors
    browser.close()

out = ROOT / 'reports/public-school-siting'
out.mkdir(exist_ok=True)
(out / 'results.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'rows':rows,'errors':errors},indent=2)+'\n')
print('PASS ordinary public-school siting, funded access, forecast, ledger and replay')
