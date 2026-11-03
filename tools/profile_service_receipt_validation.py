"""Standalone host-only cost sample of the new import metadata validation."""
import ast,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();tree=ast.parse((ROOT/'tests/test_private_services.py').read_text());fixture=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe=r'''window.__receiptCost=kind=>{__privateFixture(kind,100);__townTest.step(1);const data=JSON.parse(archivePayload()),before=JSON.stringify(G),copyBefore=JSON.stringify(data),times=[];for(let batch=0;batch<5;batch++){const start=performance.now();for(let n=0;n<200;n++)if(!normalizeServiceReceiptArchive(data))throw Error('Actual receipt fixture invalid');times.push((performance.now()-start)/200);}if(before!==JSON.stringify(G)||copyBefore!==JSON.stringify(data))throw Error('Read-only validation changed model or same-day receipt data');return {kind,people:data.people.length,households:data.households.length,privateAllocations:Object.values(data.privateServiceProvision.allocations).reduce((n,rows)=>n+Object.keys(rows).length,0),millisecondsPerValidation:times,modelAndReceiptUnchanged:true};};'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();rows=[p.evaluate('kind=>__receiptCost(kind)',kind) for kind in ['school','fire']];b.close()
for row in rows:row['medianMillisecondsPerValidation']=sorted(row['millisecondsPerValidation'])[2]
print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'scope':'Standalone host Chromium, metadata validation only; excludes JSON decode, full hydration, rendering, native IO and large-capacity performance','cases':rows},indent=2))
