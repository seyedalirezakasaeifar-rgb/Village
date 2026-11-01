import sys,ast,json,subprocess,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
base='ecbc945c4aeeb99d27d0cf7b7cd8ee63651af785';source=subprocess.check_output(['git','show',base+':assets/game.js'],text=True)
def get_probe(name):
 t=ast.parse((ROOT/'tests'/name).read_text());return next(ast.literal_eval(n.value) for n in t.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='probe' for x in n.targets))
probe=get_probe('test_private_services.py')+'\n'+get_probe('test_service_receipt_continuation.py')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();rows=[p.evaluate('kind=>__receiptRoundtrip(kind)',kind) for kind in ['school','fire']];b.close()
print(json.dumps({'base':base,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':rows},indent=2))
assert all(not x['privateReceiptPreserved'] and not x['publicReceiptPreserved'] and not x['sameDayCashUnchanged'] for x in rows)
print('CONFIRMED untouched base loses paid receipts and the same-day exactly-once cash guard')
