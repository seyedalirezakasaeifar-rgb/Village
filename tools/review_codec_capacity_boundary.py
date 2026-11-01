"""Independent invocation of the retained real-creator wire-capacity witness only."""
from pathlib import Path
import sys,ast,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();old=(ROOT/'src/89-inactive-person-codec.js').read_text();optimized=subprocess.check_output(['git','show','d1f963a:src/89-inactive-person-codec.js'],cwd=ROOT,text=True);assert old in source;source=source.replace(old,optimized,1)
profile=subprocess.check_output(['git','show','1d73dfda:tests/profile_identity_codec.py'],cwd=ROOT,text=True);tree=ast.parse(profile);extra=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.AugAssign) and isinstance(n.target,ast.Name) and n.target.id=='setup');probe=extra[extra.index('window.__sharedBoundary='):]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__sharedBoundary()');b.close()
out={'candidate':'d1f963afc24dc932e91c48bb72253583b3390429','source_sha256':hashlib.sha256(source.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'fixture':'Synthetic near-budget padding, actual createFirm helper; not a naturally evolved city or paid UI construction test','result':result};(ROOT/'reports/codec-capacity-independent-review.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
