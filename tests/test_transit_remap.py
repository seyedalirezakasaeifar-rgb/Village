"""Pure candidate transit migration and atomic failure of the live wrapper."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,json,hashlib
module=ast.parse((ROOT/'tests/test_transit_network.py').read_text())
setup=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe=r'''
window.__transitRemapProbe=()=>{
 const before=archivePayload(),state=G.transit,original=JSON.stringify(state),cash=totalMoney(),map=id=>(id/T|0)*(T+48)+id%T;
 const mapped=remapTransitState(state,map);if(JSON.stringify(state)!==original)throw Error('Pure transform mutated its source');
 if(JSON.stringify(mapped.tracks)!==JSON.stringify(state.tracks.map(map)))throw Error('Guideway not remapped');
 for(let i=0;i<state.routes.length;i++){const a=state.routes[i],b=mapped.routes[i];if(JSON.stringify(b.path)!==JSON.stringify(a.path.map(map))||JSON.stringify(b.stops)!==JSON.stringify(a.mode==='bus'?a.stops.map(map):a.stops)||JSON.stringify(b.offsets)!==JSON.stringify(a.offsets)||a.depot!==b.depot||a.id!==b.id||a.capital!==b.capital||JSON.stringify(a.stats)!==JSON.stringify(b.stats))throw Error('Remap changed institution IDs, offsets, fare or daily accounts');}
 mapped.routes[0].stats.staff.push(999999);if(JSON.stringify(state)!==original)throw Error('Candidate aliases live nested state');
 let threw=false;try{remapTransitTiles(id=>id===state.tracks[2]?-1:map(id));}catch(_){threw=true;}
 if(!threw||archivePayload()!==before)throw Error('Failed live transform changed the running city');
 const candidate=JSON.parse(before);candidate.transit=remapTransitState(candidate.transit,id=>id);candidate.transit.lastDay=candidate.day+1;
 if(hydrateSave(candidate)||archivePayload()!==before)throw Error('Invalid candidate replaced or mutated live town');
 const valid=JSON.parse(before);valid.transit=remapTransitState(valid.transit,id=>id);if(!hydrateSave(valid)||JSON.stringify(G.transit)!==original||totalMoney()!==cash)throw Error('Valid identity migration changed the network accounts');
 const revision=G.transit.revision;remapTransitTiles(id=>id);if(G.transit.revision!==revision+1||G.people.some(p=>p.transitTrip)||totalMoney()!==cash)throw Error('Live wrapper did not invalidate only transient tickets/caches');
 return {pure:true,nestedIndependent:true,failedLiveAtomic:true,invalidArchiveAtomic:true,identityArchive:true,liveInvalidation:true,routes:G.transit.routes.length,tracks:G.transit.tracks.length,total:totalMoney()};
};
'''
source=(ROOT/'assets/game.js').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',setup+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42)");p.evaluate('__transitProbe.setup()');p.evaluate('__transitProbe.rail()');p.evaluate('__townTest.step(1)');result=p.evaluate('__transitRemapProbe()');assert not errors,errors;b.close()
report={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'result':result,'errors':errors};(ROOT/'reports/transit-remap-8.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));print('PASS pure candidate mapper preserves IDs/fares/offsets, deep independence, live/invalid-archive atomicity and explicit live invalidation')
