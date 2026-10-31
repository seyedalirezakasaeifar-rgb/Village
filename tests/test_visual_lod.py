"""Distant actors must skip per-agent work while the economy still progresses."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
probe=r'''
window.__lodProbe=()=>{paused=false;gameOptions.quality='balanced';gameOptions.traffic=true;gameOptions.effects=true;gameOptions.reducedMotion=false;
 const before=JSON.stringify({traffic,trafficClock,trafficElapsed,vehicleSerial}),rows=[];
 for(const zoom of [.08,.2,.44]){cam.zoom=zoom;for(let i=0;i<100;i++)trafficUpdate(.1);const unreadable=new Proxy([],{get(){throw Error('Distant actor iterated parcels')}});if(buildingActivity(unreadable).length||workdayScenes(unreadable).length||waterfrontActors(()=>{throw Error('Distant boat work')}).length)throw Error('Distant actors drawn');if(zoom<.3)paintCastShadows({},unreadable);rows.push({zoom,budget:visualDetailBudget(),subpixelShadowsSkipped:zoom<.3});}
 if(JSON.stringify({traffic,trafficClock,trafficElapsed,vehicleSerial})!==before)throw Error('Hidden traffic advanced');
 const day=G.day;__townTest.step(30);if(G.day!==day+30)throw Error('LOD stopped economy');
 cam.zoom=1;paused=false;for(let i=0;i<100;i++)trafficUpdate(.1);if(vehicleSerial===0)throw Error('Nearby traffic did not return');paused=true;
 return{rows,nearbyVehicles:traffic.length,day:G.day,valid:validateTown()};};
'''
# Boats remain worthwhile at0.44, so test distant boats separately at0.2.
probe=probe.replace("||waterfrontActors(()=>{throw Error('Distant boat work')}).length", "||(zoom<.32&&waterfrontActors(()=>{throw Error('Distant boat work')}).length)")
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__lodProbe()');assert result['valid']['ok'];b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-8.0';out.mkdir(exist_ok=True);(out/'visual-lod.json').write_text(json.dumps({'source_sha256':sha,**result},indent=2)+'\n');print('PASS visual LOD skips distant actor loops, near traffic returns, aggregate economy advances',result)
