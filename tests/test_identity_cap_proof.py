"""Evidence-only lifetime entity admission boundaries. No production changes."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib,os
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__identityProof=()=>{
 const results={};
 for(const kind of ['households','firms']){
 __townTest.reset('settlement',42);__townTest.step(30);
 const template=JSON.parse(JSON.stringify(G[kind][0]));
 while(G[kind].length<3000){const row={...JSON.parse(JSON.stringify(template)),id:G[kind].length};if(kind==='households'){row.people=[];row.home=-1;row.cash=0;row.deposits={};}else{row.closed=true;row.demolished=true;row.building=-1;row.workers=[];row.attendingWorkers=[];row.cash=0;row.stock={};}G[kind].push(row);}
 if(!hydrateSave(archivePayload()))throw Error(kind+' accepted historical boundary rejected');
 let pos;for(let y=2;y<T-2&&!pos;y++)for(let x=2;x<T-2&&!pos;x++)if(canPlace(x,y,true,kind==='firms'?'grocer':'home'))pos={x,y};if(!pos)throw Error('No construction slot');
 const actualDay=G.day;G.day=1;let created;if(kind==='firms')created=createFirm('grocer',pos.x,pos.y);else{const b={id:G.nextId++,kind:'home',...pos,value:50000,condition:100,owner:-1,firm:-1,hh:-1};G.tiles[b.y*T+b.x]=0;G.buildings.push(b);G.homes.push(b.id);invalidateRoads();created=addHouseholdAt(b,1700);}
 G.day=actualDay;if(!created||G[kind].length!==3001)throw Error(kind+' real creator did not cross boundary');
 const raw=archivePayload(),rng=rngState;const rejected=!hydrateSave(raw);if(!rejected||archivePayload()!==raw||rngState!==rng)throw Error(kind+' boundary/atomicity mismatch');
 const original=hydrateSave;try{hydrateSave=eval('('+original.toString().replace('data.households.length>3000','data.households.length>3001').replace('data.firms.length>3000','data.firms.length>3001')+')');if(!hydrateSave(raw))throw Error(kind+' has a second structural defect');}finally{hydrateSave=original;}
 results[kind]={allOtherValidatorsPass:true,acceptedHistorical:3000,actualCreator:kind==='firms'?'createFirm':'addHouseholdAt',createdId:created.id,total:3001,ownArchiveRejected:true,rejectionAtomic:true,bytes:new Blob([raw]).size};
 }
 __townTest.reset('settlement',42);const samples=[];for(let i=0;i<=window.proofYears;i++){if(i)__townTest.step(360);samples.push({year:i,households:G.households.length,empty:G.households.filter(h=>!h.people.length).length,firms:G.firms.length,closed:G.firms.filter(f=>f.closed).length,demolished:G.firms.filter(f=>f.demolished).length,people:G.people.length,living:G.people.filter(p=>!p.deceased&&!p.movedAway).length});}results.natural=samples;return results;
};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('(years)=>window.proofYears=years',0 if os.environ.get('PROOF_BOUNDARY_ONLY') else 20);r=p.evaluate('__identityProof()');b.close()
out=ROOT/'reports/identity-cap-proof';out.mkdir(exist_ok=True);(out/('boundary.json' if os.environ.get('PROOF_BOUNDARY_ONLY') else 'result.json')).write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'result':r},indent=2)+'\n');print('PASS',json.dumps(r))
