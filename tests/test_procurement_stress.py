"""Bounded actual orders with competition and labelled disruptions."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__procurementStress=o=>{
 __townTest.reset(o.scenario,42);__townTest.step(25);const total=totalMoney(),s=G.regionalTrade,f=G.firms.find(f=>f.kind==='farm'&&!f.closed),start=G.day,opening=G.stats.population;
 const ordinary=reviewRegionalProcurement({firmId:f.id,marketId:'port',good:'grain',milestones:[{quantity:10,deadline:G.day+30}]});const competitor=authorizeRegionalProcurement(ordinary);if(!competitor.ok)throw Error(competitor.reason);
 let spec={firmId:f.id,marketId:'port',good:'grain',milestones:[{quantity:50,deadline:G.day+15},{quantity:100,deadline:G.day+30}]};let review=reviewRegionalProcurement(spec);const originalReason=review.ok?null:review.reason;if(!review.ok){spec={...spec,milestones:[{quantity:10,deadline:G.day+15},{quantity:10,deadline:G.day+30}]};review=reviewRegionalProcurement(spec);}const food=G.firms.find(f=>formulas[f.kind]?.out==='food'&&!f.closed),foodReview=food?reviewRegionalProcurement({...spec,firmId:food.id,good:'food'}):null;
 if(!review.ok)return {opening,admitted:false,reason:review.reason,foodEligible:foodReview?.ok};const accepted=authorizeRegionalProcurement(review);if(!accepted.ok)throw Error(accepted.reason);const ids=accepted.contractIds,stages=[],roads=[];let cancellation=null,closure=null;
 for(let i=0;i<60;i++){
 if(i===2&&o.mode==='delay'){const b=readBuild(f.building);for(const [dx,dy]of roadOffsets){const x=b.x+dx,y=b.y+dy,id=y*T+x;if(G.tiles[id]===1){roads.push({x,y});G.tiles[id]=0;}}invalidateRoads(false);}
 if(i===20&&o.mode==='delay'){for(const r of roads)construct('road',r.x,r.y,true);flushRoadBatch();}
 if(i===16&&o.mode==='cancel'){const before=JSON.stringify(s.shipments);cancelRegionalAgreement(ids[1]);cancellation={cargoUnchanged:before===JSON.stringify(s.shipments),statuses:s.contracts.filter(c=>ids.includes(c.id)).map(c=>c.status)};}
 if(i===2&&o.mode==='closure'){const loan=bankLoan('firm',f.id,5000,360);closure={loanApproved:!!loan};liquidateFirm(f,'Controlled procurement supplier closure');closure.loans=G.loans.filter(l=>l.ownerType==='firm'&&l.ownerId===f.id).map(l=>({...l}));}
 __townTest.step(1);if(!validateTown().ok||Math.abs(totalMoney()-total)>.001||Math.max(...goodsBalance().map(x=>Math.abs(x.error)))>.001)throw Error('Books or town invalid');
 if(i%5===0)stages.push({day:G.day,hardship:G.stats.hardship,foodStocks:G.firms.reduce((n,f)=>n+(f.stock.food||0),0),contracts:s.contracts.filter(c=>ids.includes(c.id)).map(c=>({...c})),cargo:s.shipments.filter(x=>ids.includes(x.contract)).map(x=>({id:x.id,stage:x.stage,status:x.status,qty:x.qty}))});
 }
 let retention=null;if(o.mode==='normal'){const keep=archivePayload();__townTest.reset(o.scenario,42);__townTest.step(25);const rf=G.firms.find(f=>f.kind==='farm'),rs=G.regionalTrade,rspec={firmId:rf.id,marketId:'port',good:'grain',milestones:[{quantity:10,deadline:G.day+15},{quantity:10,deadline:G.day+30}]},ra=authorizeRegionalProcurement(reviewRegionalProcurement(rspec));__townTest.step(1);const cargo=rs.shipments.filter(x=>ra.contractIds.includes(x.contract));if(!cargo.length)throw Error('Retention fixture lacks actual cargo');cancelRegionalAgreement(ra.contractIds[0]);while(rs.contracts.length<24)rs.contracts.push({id:++rs.serial,name:'Synthetic completed history only',firm:rf.id,market:'port',good:'grain',quantity:10,delivered:10,price:1,deadline:G.day,status:'fulfilled'});const rr=authorizeRegionalProcurement(reviewRegionalProcurement({...rspec,milestones:[{quantity:10,deadline:G.day+15},{quantity:10,deadline:G.day+30}]}));retention={authorized:rr.ok,retained:ra.contractIds.every(id=>rs.contracts.some(c=>c.id===id)),cargoRetained:cargo.every(x=>rs.shipments.includes(x)),count:rs.contracts.length};if(!retention.authorized||!retention.retained||!retention.cargoRetained||retention.count>24)throw Error('Retention broke live group');if(!hydrateSave(keep))throw Error('Retention fixture restore failed');}const final=s.contracts.filter(c=>ids.includes(c.id)).map(c=>({...c}));if(o.mode==='normal'&&final.some(c=>c.status!=='fulfilled'))throw Error('Normal order missed');if(cancellation&&!cancellation.cargoUnchanged)throw Error('Cancellation deleted cargo');
 const checkpoint=archivePayload();__townTest.step(10);const future=archivePayload();if(!hydrateSave(checkpoint))throw Error('Archive rejected');__townTest.step(10);if(archivePayload()!==future)throw Error('Replay mismatch');return {opening,admitted:true,originalReason,foodEligible:foodReview?.ok,foodReason:foodReview?.reason,final,stages,cancellation,closure,roads,retention,cashDrift:totalMoney()-total,goods:goodsBalance(),claims:G.regionalTrade.claims};};
'''
rows=[];out=ROOT/'reports/procurement-stress';out.mkdir(exist_ok=True)
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_default_timeout(180000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
 for scenario in ['settlement','regional']:
  for mode in ['normal','cancel','closure','delay']:
   row={'scenario':scenario,'mode':mode};rows.append(row)
   try:row['result']=p.evaluate('o=>__procurementStress(o)',{'scenario':scenario,'mode':mode});row['status']='complete'
   except Exception as e:row['status']='failed';row['failure']=str(e)
   (out/'results.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'rows':rows,'errors':errors},indent=2));print(scenario,mode,row['status'],row.get('failure',''),flush=True)
 b.close()
assert all(r['status']=='complete'for r in rows)and not errors
