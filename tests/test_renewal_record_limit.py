"""Valid historical boundary fixture plus real assessment transitions; no record pruning."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import os,json,hashlib
source=(ROOT/'assets/game.js').read_text();probe=r'''
window.__renewalLimit=()=>{
 __townTest.reset('regional',42);G.autoBuild=false;const funds=Math.min(G.region,2000000);G.region-=funds;G.treasury+=funds;const first=G.firms.find(f=>f.kind==='quarry');if(!brownfieldAssess(first.building).ok||!brownfieldAcquire(first.building).ok||!brownfieldFund(first.building).ok)throw Error('First actual renewal failed');__townTest.step(60);if(!brownfieldReuse(first.building,'park').ok)throw Error('Actual reuse failed');const completed=G.brownfields[0];
 // Compact synthetic historical provenance: clone a genuine completed receipt,
 // assign distinct retired identifiers, then cross the edge with real paid actions.
 while(G.brownfields.length<2999){const copy=JSON.parse(JSON.stringify(completed));copy.id=G.nextId++;copy.newBuilding=G.nextId++;G.brownfields.push(copy);}
 const candidates=G.firms.filter(f=>!f.demolished&&BROWNFIELD_KINDS.includes(f.kind)&&!G.brownfields.some(s=>s.id===f.building)&&brownfieldQuote(f.building).ok);if(candidates.length<2)throw Error('Need two real industrial candidates');
 if(!brownfieldAssess(candidates[0].building).ok)throw Error('3000th assessment refused');const baseline=archivePayload(),cash=totalMoney();if(!hydrateSave(baseline))throw Error('Boundary itself cannot load');const before=archivePayload(),records=JSON.stringify(G.brownfields);
 const result=brownfieldAssess(candidates[1].building),after=archivePayload(),accepted=result.ok,loadable=hydrateSave(after);if(!loadable&&!hydrateSave(before))throw Error('Recovery baseline lost');
 if(!accepted&&(after!==before||records!==JSON.stringify(G.brownfields)||totalMoney()!==cash))throw Error('Rejected assessment mutated obligations/accounts');
 if(!accepted){if(!brownfieldAcquire(candidates[0].building).ok||!brownfieldFund(candidates[0].building).ok)throw Error('Existing at-limit project blocked');const checkpoint=archivePayload(),canon=v=>Array.isArray(v)?v.map(canon):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canon(v[k])])):v;__townTest.step(30);const a=JSON.parse(archivePayload());if(!hydrateSave(checkpoint))throw Error('Replay checkpoint rejected');__townTest.step(30);const b=JSON.parse(archivePayload());for(const g of[a,b]){delete g.trafficState;delete g.visualState;}if(JSON.stringify(canon(a))!==JSON.stringify(canon(b)))throw Error('At-limit replay changed');}return {historicalFixture:true,actualCompletedReceipt:true,atLimit:3000,attemptAccepted:accepted,postAttemptImportable:loadable,rejection:result.reason,existingRecordPreserved:!!G.brownfields.find(s=>s.id===candidates[0].building),existingProjectContinues:!accepted&&G.brownfields.find(s=>s.id===candidates[0].building).status==='ready',bytes:new Blob([before]).size,money:cash};
};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__renewalLimit()');b.close()
negative=os.environ.get('RENEWAL_EXPECT_NEGATIVE')=='1';assert r['attemptAccepted']==negative,r;assert r['postAttemptImportable']!=negative,r;assert r['existingRecordPreserved'],r
out=ROOT/'reports/renewal-limit';out.mkdir(exist_ok=True);(out/('before.json' if negative else 'after.json')).write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'result':r},indent=2)+'\n');print('PASS expected negative' if negative else 'PASS guarded boundary',r)
