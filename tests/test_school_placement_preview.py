"""Read-only public-school catchment preview, constraints, and cancelled placement."""
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright
import hashlib, json

source = (ROOT / 'assets/game.js').read_text()
probe = r'''
window.__schoolPreviewCases=(scenario,seed)=>{
 __townTest.reset(scenario,seed);G.autoBuild=false;
 const net=graph(),homePorts=G.households.map(h=>net.portals.get(h.home)).filter(Number.isInteger),lots=[];
 for(let y=3;y<T-4;y++)for(let x=3;x<T-4;x++)if(canPlace(x,y,true,'school')){
  const roads=[];for(const id of footprintFor(x,y,'school')){const xx=id%T,yy=id/T|0;for(const [dx,dy]of roadOffsets){const ax=xx+dx,ay=yy+dy;if(ax>=0&&ax<T&&ay>=0&&ay<T){const rid=roadId(ax,ay);if(G.tiles[rid]===1)roads.push(rid);}}}
  const port=roads.find(id=>net.parts[id]===net.mainPart)??roads[0];if(port==null)continue;const ds=homePorts.map(h=>roadDistance(port,h)).filter(Number.isFinite);if(ds.length)lots.push({x,y,mean:ds.reduce((a,b)=>a+b,0)/ds.length});
 }
 lots.sort((a,b)=>a.mean-b.mean);const near=lots[0],far=lots[lots.length-1];if(!near||!far)throw Error('Missing reachable school sites');
 const unchanged=()=>JSON.stringify(G),archive=()=>archivePayload(),rng=()=>rngState;
 const before=unchanged(),saved=archive(),random=rng(),a=schoolPlacementPreview(near.x,near.y),text=schoolPlacementHint(near.x,near.y),b=schoolPlacementPreview(far.x,far.y),repeat=schoolPlacementPreview(near.x,near.y);
 if(JSON.stringify(G)!==before||archivePayload()!==saved||rngState!==random)throw Error('Preview mutated town, archive or RNG');
 if(JSON.stringify(a)!==JSON.stringify(repeat))throw Error('Candidate preview cache is not stable');
 if(!text.includes('new reach')||!text.includes('need')||!text.includes('no service promise'))throw Error('Preview wording omits a key distinction');
 const uiBefore=unchanged(),uiRng=rng();buildMode='school';pointer.hover={x:near.x,y:near.y};$('placementHint').style.display='block';dirty=true;draw();const visibleHint=$('placementHint').textContent,rect=$('placementHint').getBoundingClientRect(),mobileHintBox={width:rect.width,height:rect.height};if(!visibleHint.includes('School ·')||!$('placementHint').classList.contains('school-placement'))throw Error('Map placement hint did not expose the school preview');if(JSON.stringify(G)!==uiBefore||rngState!==uiRng)throw Error('Map preview draw changed simulation');
 const overlap={newlyReachable:a.newlyReachable,incrementalPlaces:a.incrementalPlaces,existingReach:a.existingReach,projectedReach:a.projectedReach};
 // Controlled test-only isolated street: one real road tile beside a legal empty
 // footprint, with no road neighbors or connected households.
 let disconnected=null;outer:for(let y=3;y<T-4;y++)for(let x=3;x<T-4;x++)if(canPlace(x,y,false,'school')){
  const own=new Set(footprintFor(x,y,'school'));for(const id of own){const xx=id%T,yy=id/T|0;for(const [dx,dy]of roadOffsets){const ax=xx+dx,ay=yy+dy;if(ax<2||ay<2||ax>=T-2||ay>=T-2)continue;const rid=roadId(ax,ay);if(G.tiles[rid]!==0||own.has(rid))continue;let lonely=true;for(const [rdx,rdy]of roadOffsets){const rx=ax+rdx,ry=ay+rdy;if(rx>=0&&rx<T&&ry>=0&&ry<T&&G.tiles[roadId(rx,ry)]===1)lonely=false;}if(lonely){disconnected={x,y,road:rid,old:G.tiles[rid]};break outer;}}}}
 if(!disconnected)throw Error('Could not find a vacant disconnected school-road test site');
 G.tiles[disconnected.road]=1;invalidateRoads(false);const isolated=schoolPlacementPreview(disconnected.x,disconnected.y);G.tiles[disconnected.road]=disconnected.old;invalidateRoads(false);
 if(Math.abs(isolated.projectedReach-schoolPlacementPreview(disconnected.x,disconnected.y).existingReach)>.001)throw Error('Disconnected school preview promised places '+JSON.stringify({projected:isolated.projectedReach,current:schoolPlacementPreview(disconnected.x,disconnected.y).existingReach,site:disconnected}));
 const underfundedTreasury=G.treasury;G.treasury=buildCost.school-1;const cashShort=schoolPlacementPreview(near.x,near.y);G.treasury=underfundedTreasury;
 const eligible=G.people.filter(p=>p.job<0&&!p.deceased&&!p.movedAway&&qualifiedForService(p,'school'));const oldJobs=eligible.map(p=>p.job);for(const p of eligible)p.job=0;const noLocalStaff=schoolPlacementPreview(near.x,near.y);eligible.forEach((p,i)=>p.job=oldJobs[i]);
 const cancelledBefore=unchanged(),cancelledArchive=archive(),cancelledRng=rng();buildMode='school';pointer.hover={x:near.x,y:near.y};schoolPlacementHint(near.x,near.y);closeBuildTool();if(JSON.stringify(G)!==cancelledBefore||archivePayload()!==cancelledArchive||rngState!==cancelledRng)throw Error('Cancelled placement changed simulation state');
 if(!cashShort||cashShort.affordable||noLocalStaff.eligibleLocalStaff!==0)throw Error('Affordability/staffing guard failed');
 if(isolated.newlyReachable!==0||isolated.incrementalPlaces!==0)throw Error('Disconnected candidate reported service access');
 return {source_sha256:'',near,far,hint:visibleHint,mobileHintBox,nearPreview:a,farPreview:b,overlap,disconnected:{site:disconnected,preview:isolated},cashShort:{affordable:cashShort.affordable,treasury:cashShort.treasury,cost:cashShort.cost},noLocalStaff:{eligible:noLocalStaff.eligibleLocalStaff,actualCoverage:noLocalStaff.actualCoverage,staffing:noLocalStaff.staffing},cancelled:{unchanged:true,archiveUnchanged:true,rngUnchanged:true},stateValid:validateTown().ok};
};'''

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':390,'height':844}, device_scale_factor=2)
    page.set_default_timeout(120000)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(html)
    page.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js', probe + '\n// SOURCE: 99-instrumentation.js'))
    page.locator('#newTown').click(); page.locator('#pause').click()
    rows=[]
    for scenario,seed in [('settlement',42),('regional',42)]:
        result = page.evaluate('o=>__schoolPreviewCases(o.scenario,o.seed)',{'scenario':scenario,'seed':seed})
        assert result['stateValid'] and not errors, errors
        box=result['mobileHintBox']
        assert 300<box['width']<=390*.92+1 and box['height']<140,box
        result['mobileHintBox']=box
        assert result['nearPreview']['siteMeanDistance'] < result['farPreview']['siteMeanDistance']
        assert result['disconnected']['preview']['siteMeanDistance'] is None
        rows.append(result)
    rows[0]['source_sha256'] = hashlib.sha256(source.encode()).hexdigest()
    out = ROOT / 'reports/school-placement-preview'
    out.mkdir(exist_ok=True)
    (out / 'results.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'rows':rows}, indent=2) + '\n')
    browser.close()
print('PASS read-only near/far/disconnected preview, overlap, staffing, affordability, cancellation and RNG checks')
