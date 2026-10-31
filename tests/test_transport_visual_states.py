"""Transport transition continuity and stable appearance state invalidation."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json
source=(ROOT/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js','''window.__motionProbe=()=>{
 const r={a:[0,0],b:[600,300],dx:600,dy:300,length:Math.hypot(600,300)},gate=[200,220],jumps=[];
 for(const edge of [8,18,66,75,85]){const a=aviationPose(r,gate,edge-.0001),b=aviationPose(r,gate,edge+.0001);jumps.push({edge,distance:Math.hypot(a.pos[0]-b.pos[0],a.pos[1]-b.pos[1]),alt:Math.abs(a.alt-b.alt)});}
 const poses=[];for(let t=0;t<90;t+=.25){const p=aviationPose(r,gate,t);if(p)poses.push(p);}
 const pedestrian=setPurposeStyle({},'pedestrian'),car=setPurposeStyle({},'car'),truck=setPurposeStyle({},'truck');
 const b=G.buildings.find(b=>b.firm>=0),f=G.firms[b.firm],old={condition:b.condition,scale:f.scale,closed:f.closed};b.condition=100;f.closed=false;f.scale=1;const maintained=appearanceKey(b);b.condition=60;const worn=appearanceKey(b);b.condition=100;f.scale=1.5;const invested=appearanceKey(b);f.closed=true;const closed=appearanceKey(b);b.condition=old.condition;Object.assign(f,{scale:old.scale,closed:old.closed});
 return {jumps,poses,pedestrian,car,truck,keys:[maintained,worn,invested,closed]};};
// SOURCE: 99-instrumentation.js''')
source=source.replace('// SOURCE: 99-instrumentation.js',"window.__tripAccountingProbe=()=>{const before=G.transport.arrived,total=totalMoney(),was=paused;paused=false;for(let i=0;i<240;i++)trafficUpdate(.25);paused=was;return {before,after:G.transport.arrived,delta:totalMoney()-total};};window.__tripProbe=()=>{const v=spawnPurposeTrip();if(!v)return false;const p=vehiclePosition(v);return inspectTripAt(p.x,p.y);};\n// SOURCE: 99-instrumentation.js")
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__motionProbe()')
 assert all(j['distance']<1 and j['alt']<1 for j in r['jumps']),r['jumps']
 assert all(all(isinstance(v,(float,int)) for v in q['pos']+q['heading']) and q['alt']>=0 for q in r['poses'])
 assert r['pedestrian']['speed']<r['truck']['speed']<r['car']['speed']
 assert len(set(r['keys']))==4
 assert p.evaluate('__tripProbe()')
 assert p.locator('#panelTitle').inner_text()=='Journey Inspector'
 assert 'Panel error' not in p.locator('#panelBody').inner_text()
 p.locator('[data-trip-close]').click();assert not p.locator('#panel').is_visible()
 result=p.evaluate('__tripAccountingProbe()');assert result['before']==result['after'] and abs(result['delta'])<.0001,result
 b.close();print('PASS runway/taxi/touchdown continuity, purpose speeds and vacancy/condition/investment cache states')
