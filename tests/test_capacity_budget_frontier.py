"""Exact byte/node admission frontier; negative candidates preserve live state."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_text();probe=r'''
window.__budgetFrontier=()=>{__townTest.reset('settlement',42);__townTest.step(30);__inactivePersonCodec.enable(true);if(!hydrateSave(archivePayload()))throw Error('Baseline');const base=archivePayload(),limits=INACTIVE_CODEC_LIMITS,rows=[];const nodeCount=v=>1+(v&&typeof v==='object'?Object.keys(v).reduce((n,k)=>n+nodeCount(v[k]),0):0);
 for(const kind of ['bytes','nodes'])for(const delta of [-1,0,1]){const candidate=JSON.parse(base);let target=limits[kind]+delta;if(kind==='bytes'){candidate.payload.bytePadding='';const n=new Blob([JSON.stringify(candidate)]).size;candidate.payload.bytePadding='x'.repeat(target-n);}else{candidate.payload.nodePadding=[];candidate.payload.nodePadding=Array(target-nodeCount(candidate)).fill(null);}const raw=JSON.stringify(candidate),actual=kind==='bytes'?new Blob([raw]).size:nodeCount(candidate);if(actual!==target)throw Error('Wrong frontier '+kind);const snapshot=archiveLogicalPayload(),rng=rngState,epoch=saveEpoch,started=performance.now(),accepted=hydrateSave(raw),ms=performance.now()-started;if(accepted!==(delta<=0))throw Error('Wrong acceptance '+kind+' '+delta);if(!accepted&&(archiveLogicalPayload()!==snapshot||rngState!==rng||saveEpoch!==epoch))throw Error('Non-atomic frontier');rows.push({kind,delta,actual,accepted,ms});}
 return rows;};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__budgetFrontier()');b.close()
out=ROOT/'reports/capacity-status';out.mkdir(exist_ok=True);(out/'frontier.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'frontier':r},indent=2)+'\n');print('PASS',r)
