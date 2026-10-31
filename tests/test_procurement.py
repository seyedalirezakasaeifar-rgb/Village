"""Actual two-stage authorization, atomic failures and conserved settlement."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__procurementTest=()=>{
 __townTest.reset('settlement',42);__townTest.step(25);const f=G.firms.find(f=>f.kind==='farm'),spec={firmId:f.id,marketId:'port',good:'grain',milestones:[{quantity:10,deadline:G.day+15},{quantity:10,deadline:G.day+30}]},before=JSON.stringify(G),rng=rngState,review=reviewRegionalProcurement(spec);if(!review.ok)throw Error(review.reason);if(before!==JSON.stringify(G)||rng!==rngState)throw Error('Review mutated state');
 const invalid=reviewRegionalProcurement({...spec,milestones:[spec.milestones[0],{quantity:-1,deadline:G.day+30}]});if(invalid.ok||before!==JSON.stringify(G))throw Error('Partial invalid stage mutated state');
 const stale=reviewRegionalProcurement(spec);G.policy.roadBudget++;const changed=JSON.stringify(G);if(authorizeRegionalProcurement(stale).ok||changed!==JSON.stringify(G))throw Error('Stale acceptance');G.policy.roadBudget--;
 const originalContracts=G.regionalTrade.contracts;G.regionalTrade.contracts=[{status:'active',quantity:10,delivered:0},{status:'active',quantity:10,delivered:0}];const slotState=JSON.stringify(G);if(reviewRegionalProcurement(spec).ok||slotState!==JSON.stringify(G))throw Error('Combined slot preflight failed');G.regionalTrade.contracts=originalContracts;
 const r=reviewRegionalProcurement(spec),total=totalMoney(),accepted=authorizeRegionalProcurement(r);if(!accepted.ok)throw Error(accepted.reason);const saved=archivePayload(),committed=JSON.stringify(G);if(authorizeRegionalProcurement(r).ok||committed!==JSON.stringify(G))throw Error('Double acceptance');
 const ids=accepted.contractIds;__townTest.step(10);if(G.regionalTrade.shipments.some(o=>o.contract===ids[1]))throw Error('Future stage dispatched early');
 const cargo=JSON.stringify(G.regionalTrade.shipments);cancelRegionalAgreement(ids[0]);if(cargo!==JSON.stringify(G.regionalTrade.shipments)||ids.some(id=>G.regionalTrade.contracts.find(c=>c.id===id).status==='active'))throw Error('Cancellation discarded cargo or left sibling active');__townTest.step(45);if(Math.abs(totalMoney()-total)>.001)throw Error('Cash drift');
 if(!hydrateSave(saved))throw Error('Group archive rejected');const malformed=JSON.parse(saved);malformed.regionalTrade.contracts=malformed.regionalTrade.contracts.filter(c=>c.id!==ids[1]);const atomic=archivePayload();if(hydrateSave(malformed)||archivePayload()!==atomic)throw Error('Orphan import accepted');
 __townTest.step(40);const final=G.regionalTrade.contracts.filter(c=>ids.includes(c.id));if(final.some(c=>c.status!=='fulfilled'))throw Error('Actual order failed '+JSON.stringify(final));if(Math.abs(totalMoney()-total)>.001||Math.max(...goodsBalance().map(x=>Math.abs(x.error)))>.001)throw Error('Books failed');
 const checkpoint=archivePayload();__townTest.step(30);const next=archivePayload();if(!hydrateSave(checkpoint))throw Error('Continuation load failed');__townTest.step(30);if(archivePayload()!==next)throw Error('Replay differs');return {final,cashDrift:totalMoney()-total,goods:goodsBalance(),valid:validateTown()};};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_default_timeout(120000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__procurementTest()');assert result['valid']['ok']and not errors;b.close()
out=ROOT/'reports/procurement';out.mkdir(exist_ok=True);(out/'acceptance.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'result':result,'errors':errors},indent=2));print('PASS atomic stages, pure review, stale/repeat rejection, delayed second stage, cancellation, orphan rejection, real fulfillment, replay and books')
