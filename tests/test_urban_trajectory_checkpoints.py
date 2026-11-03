"""Real multi-year checkpoints keep addresses, capacity, titles and accounts."""
from pathlib import Path
import json,gzip,hashlib
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text();probe=r'''
window.__urbanCheckpoint=()=>{const issues=[];for(const h of G.households){if(!h.people.length)continue;const b=readBuild(h.home);if(!b||!['home','apartment','tower'].includes(b.kind))issues.push('Missing residential address '+h.id);}for(const b of G.buildings){if(!['home','apartment','tower'].includes(b.kind))continue;const actual=G.households.filter(h=>h.people.length&&h.home===b.id).map(h=>h.id),capacity=b.kind==='tower'?9:b.kind==='apartment'?4:1;if(actual.length>capacity)issues.push('Housing capacity '+b.id+':'+actual.length+'/'+capacity);if(b.kind==='home'&&actual.length&&b.hh!==actual[0])issues.push('Cottage address roster '+b.id);if(b.kind!=='home'){const roster=(b.units||[]).filter(id=>G.households[id]?.people.length);if(roster.length!==actual.length||roster.some(id=>!actual.includes(id)))issues.push('Apartment address roster '+b.id);}if(b.relocationReserve&&actual.length)issues.push('Occupied reserve '+b.id);}return {day:G.day,population:G.stats.population,total:totalMoney(),issues,valid:validateTown()};};
'''
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
 for file in sorted((ROOT/'docs/previews/urban8/trajectories').glob('regional-*.json.gz')):
  assert p.evaluate('a=>__townTest.load(a)',gzip.decompress(file.read_bytes()).decode()),file.name
  start=p.evaluate('__urbanCheckpoint()');assert not start['issues'] and start['valid']['ok'],(file.name,start);p.evaluate('__townTest.step(60)');end=p.evaluate('__urbanCheckpoint()');assert not end['issues'] and end['valid']['ok'] and abs(end['total']-start['total'])<.1,(file.name,end);rows.append({'archive':file.name,'before':start,'after':end})
 b.close()
assert len(rows)==6
(ROOT/'docs/previews/urban8/trajectory-checkpoints.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'checkpoints':rows},indent=2)+'\n');print('PASS six natural six-year checkpoints and 60-day continuation, complete housing-address/capacity/roster checks and cash/goods conservation')
