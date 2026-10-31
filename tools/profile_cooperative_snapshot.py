"""Per-section plain-state recovery copy cost, retained terminal fixture, host only."""
from pathlib import Path
import sys,json,gzip,subprocess,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
late=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)).decode();source=(ROOT/'assets/game.js').read_text()
probe=r'''window.__snapshotSections=()=>{const rows=[];for(const [key,value]of Object.entries(G)){const samples=[];for(let i=0;i<5;i++){const t=performance.now(),copied=copyCooperativeState(value);samples.push(performance.now()-t);if(i===0&&JSON.stringify(copied)!==JSON.stringify(value))throw Error('Copy differs: '+key);}rows.push({key,jsonBytes:JSON.stringify(value)?.length||0,samples});}return rows;};'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townTest.load(s)',late);rows=p.evaluate('__snapshotSections()');b.close()
rows.sort(key=lambda r:sum(r['samples']),reverse=True);out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'fixture_sha256':hashlib.sha256(late.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'samplesPerSection':5,'rows':rows};(ROOT/'reports/cooperative-snapshot-sections.json').write_text(json.dumps(out,indent=2));print(json.dumps(rows[:10],indent=2))
