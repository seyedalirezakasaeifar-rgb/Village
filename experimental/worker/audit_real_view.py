"""Audit real presentation against immutable authoritative snapshots; no production enable."""
from pathlib import Path
import sys,json,gzip,subprocess
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode()
hook='''window.workerViewAudit=a=>{paused=true;G=JSON.parse(a);rngState=G.rngState;invalidateRoads();function freeze(v){if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.freeze(v);for(const x of Object.values(v))freeze(x);}return v;}freeze(G);const rows=[];for(const [name,action] of [['header',()=>updateHeader()],['real map',()=>{dirty=true;draw();}],['construction panel',()=>renderPanel('construction')],['policy panel',()=>renderPanel('policies')],['agenda panel',()=>renderPanel('agenda')]]){try{const t=performance.now();action();rows.push({name,ok:true,ms:performance.now()-t});}catch(e){rows.push({name,ok:false,error:String(e),stack:e.stack});}}return rows;};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=Path('assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'))
 rows=p.evaluate('a=>workerViewAudit(a)',archive);Path('experimental/worker/real-view-audit.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows));b.close()
