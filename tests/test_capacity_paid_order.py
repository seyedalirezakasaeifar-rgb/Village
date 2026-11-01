"""Negative proof: whole paid construct action is outside creator-only admission."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_text();probe=r'''
window.__paidCapacity=()=>{__townTest.reset('settlement',42);__townTest.step(30);__inactivePersonCodec.enable(true);G.capacityPadding='';const max=INACTIVE_CODEC_LIMITS.bytes,base=new Blob([archivePayload()]).size;G.capacityPadding='x'.repeat(max-base-64);let good=archivePayload();if(!hydrateSave(good))throw Error('Initial candidate');let failure=null;for(let attempt=0;attempt<15&&!failure;attempt++){let site;for(let y=2;y<T-2&&!site;y++)for(let x=2;x<T-2&&!site;x++)if(canPlace(x,y,true,'grocer'))site={x,y};if(!site)throw Error('No site');const before={treasury:G.treasury,region:G.region,firms:G.firms.length,nextId:G.nextId,rng:rngState};construct('grocer',site.x,site.y);let error='';try{good=archivePayload()}catch(e){error=String(e)}if(error)failure={action:'construct grocer',attempt:attempt+1,error,before,after:{treasury:G.treasury,region:G.region,firms:G.firms.length,nextId:G.nextId,rng:rngState}};}
 if(!failure||failure.after.firms!==failure.before.firms+1||failure.after.treasury>=failure.before.treasury)throw Error('Paid failure not reproduced');if(!hydrateSave(good))throw Error('Last good recovery failed');return {...failure,lastGoodBytes:new Blob([good]).size,recoverySucceeded:true};};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__paidCapacity()');b.close()
out=ROOT/'reports/capacity-status';out.mkdir(exist_ok=True);(out/'paid-order-negative.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'unsafePaidOrder':r},indent=2)+'\n');print('PASS negative proof',r)
