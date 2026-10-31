"""Original terminal town: monthly inner-loop order/RNG and complete accounts."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,subprocess,gzip,json,hashlib
source=(ROOT/'assets/game.js').read_text();fixture=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)).decode()
m=ast.parse((ROOT/'tests/test_cooperative_simulation.py').read_text());probe=next(ast.literal_eval(n.value) for n in m.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);results=[]
 for mode in ['synchronous','staged']:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townTest.load(s)',fixture);results.append(p.evaluate('m=>__coopTest.run(m,120,false)',mode));p.close()
 b.close()
assert results[0]['archive']==results[1]['archive'] and results[0]['rng']==results[1]['rng'],'Terminal monthly staged order/model diverged'
assert all(x['valid']['ok'] for x in results)
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'fixture_sha256':hashlib.sha256(fixture.encode()).hexdigest(),'days':120,'exactArchive':True,'exactRng':True,'endDay':results[1]['day'],'total':results[1]['money']};(ROOT/'reports/cooperative-terminal-equivalence.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));print('PASS terminal120days exact archives/RNG across original and staged monthly investment/retail/housing decisions')
