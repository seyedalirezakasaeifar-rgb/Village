"""Reproduce the original cargo candidate history defect in memory; exit zero means defect reproduced."""
import sys,subprocess,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text()
for name in ['98-trade-ui.js','98x-logistics-ui.js']:
 source=source.replace((ROOT/'src'/name).read_text(),subprocess.check_output(['git','show','2e8b51f:src/'+name],text=True,cwd=ROOT),1)
probe=r'''window.__recentReview=()=>{const f=G.firms.find(f=>!f.closed&&formulas[f.kind]?.out==='grain'),m=OUTSIDE_MARKETS[0],q=regionalQuote(f,m,'grain','import');dispatchRegional(f,'grain',12,'import',q);const id=G.regionalTrade.shipments.at(-1).id;let o;for(let i=0;i<60&&!o;i++){__townTest.step(1);o=G.regionalTrade.recent.find(o=>o.id===id)}if(!o)throw Error('No actual completed record');return{day:G.day,record:o,timing:regionalCargoTiming(o,G.day+5)}};'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__recentReview()');b.close()
print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),**result},indent=2))
assert result['record']['status']=='Delivered' and 'past estimate' in result['timing']['schedule'] and result['timing']['checkpoint'] is not None,result['timing']
print('REPRODUCED held original cargo-history disclosure; current fixed UI is not replaced on disk')
