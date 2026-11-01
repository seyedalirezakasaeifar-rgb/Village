"""Read-only household audit of food shortages after a matched road reopening."""
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright
import hashlib, json

bundleSource=(ROOT/'assets/game.js').read_text()
source=bundleSource
replacements=[
 ("const shoppingOffset=living.length?hash(G.day+G.worldSeed)%living.length:0,shoppingOrder=living.slice(shoppingOffset).concat(living.slice(0,shoppingOffset)),retailReference=foodPriceEstimate();",
  "const shoppingOffset=living.length?hash(G.day+G.worldSeed)%living.length:0,shoppingOrder=living.slice(shoppingOffset).concat(living.slice(0,shoppingOffset)),retailReference=foodPriceEstimate(),foodStoreSnapshot=grocers.map(f=>({firm:f.id,stock:f.stock.food||0,capacity:f.retailCapacity||0,staff:workingStaff(f).length,price:f.price,part:graph().parts[graph().portals.get(f.building)]}));"),
 ("for(const h of shoppingOrder){\n  const home=readBuild(h.home);",
  "for(let shoppingIndex=0;shoppingIndex<shoppingOrder.length;shoppingIndex++){const h=shoppingOrder[shoppingIndex];\n  const home=readBuild(h.home);"),
 ("const reachable=groceryChoices(h,home,grocers),shops=reachable.filter(o=>o.f.stock.food>0&&o.f.retailCapacity>0);if(!reachable.length)",
  "const cashBeforeFood=h.cash,reachable=groceryChoices(h,home,grocers),shopSnapshot=reachable.map(o=>({firm:o.f.id,distance:o.distance,travel:o.travel,price:o.f.price,stock:o.f.stock.food||0,capacity:o.f.retailCapacity||0,workers:workingStaff(o.f).length,part:graph().parts[graph().portals.get(o.f.building)]})),shops=reachable.filter(o=>o.f.stock.food>0&&o.f.retailCapacity>0),purchaseTrace=[];if(!reachable.length)"),
 ("const net=q*f.price,tax=net*P.foodTax/100;h.cash-=net+tax;",
  "purchaseTrace.push({firm:f.id,qty:q,price:f.price,travel,distance,stockBefore:(f.stock.food||0)+q,capacityBefore:(f.retailCapacity||0)+q});const net=q*f.price,tax=net*P.foodTax/100;h.cash-=net+tax;"),
 ("h.stress=clamp(h.stress+(remaining>.1?remaining*.30:-.20),0,100);",
  "h.stress=clamp(h.stress+(remaining>.1?remaining*.30:-.20),0,100);if(window.__foodAuditMode&&window.__foodAuditDays.includes(G.day)&&remaining>.001){const homePort=home&&graph().portals.get(home.id),homePart=homePort==null?null:graph().parts[homePort],reachableIds=new Set(shopSnapshot.map(s=>s.firm));window.__foodAudit.push({day:G.day,hh:h.id,people:h.people.length,home:h.home,homePart,shoppingIndex,shoppingOffset,households:shoppingOrder.length,need,unmet:remaining,cashBeforeFood,cashAfterFood:h.cash,bankFunds:Object.entries(h.deposits||{}).map(([id,v])=>({bank:+id,deposit:v,bankCash:G.banks[+id]?.cash||0,closed:!!G.banks[+id]?.closed})),liquidity:householdLiquidity(h),income:h.income,wages:h.wages,aid:h.aid||0,stress:h.stress,foodTax:P.foodTax,reachable:shopSnapshot,accessibleStock:shopSnapshot.reduce((n,s)=>n+s.stock,0),accessibleCapacity:shopSnapshot.reduce((n,s)=>n+s.capacity,0),inaccessibleStock:foodStoreSnapshot.filter(s=>!reachableIds.has(s.firm)).reduce((n,s)=>n+s.stock,0),allStoreStock:foodStoreSnapshot.reduce((n,s)=>n+s.stock,0),allStores:foodStoreSnapshot.length,initialStoreCapacity:foodStoreSnapshot.reduce((n,s)=>n+s.capacity,0),initialStoreStaff:foodStoreSnapshot.reduce((n,s)=>n+s.staff,0),initialSellableFood:foodStoreSnapshot.reduce((n,s)=>n+Math.min(s.stock,s.capacity),0),storesWithSellableFood:foodStoreSnapshot.filter(s=>s.stock>.001&&s.capacity>.001).length,purchases:purchaseTrace});}")
]
for old,new in replacements:
 if old not in source: raise AssertionError('Instrument point missing: '+old[:80])
 source=source.replace(old,new,1)
probe=r'''
window.__foodAuditMode=false;window.__foodAuditDays=[196,211,241,271,301];window.__foodAudit=[];window.__foodAuditHistory=[];
window.__foodAuditRun=(saved,mode)=>{
 if(!__townTest.load(saved))throw Error('Audit checkpoint rejected');
 window.__foodAuditHistory=[];
 const startMoney=totalMoney(),gatewayFn=regionalGateway,gates=Object.fromEntries(OUTSIDE_MARKETS.map(m=>[m.id,gatewayFn(m)])),cut=[...new Set(Object.values(gates))];if(mode==='road')regionalGateway=m=>gates[m.id];
 if(mode==='road'){for(const id of cut)G.tiles[id]=0;invalidateRoads(false);}window.__foodAuditMode=true;window.__foodAudit=[];
 for(let d=1;d<=240;d++){if(mode==='road'&&d===121){for(const id of cut)G.tiles[id]=1;invalidateRoads(false);}__townTest.step(1);if(window.__foodAuditDays.includes(G.day)){const hist=(G.history||[]).slice(-30).filter(x=>Number.isFinite(x.unmetFood)),report=renderEconomy();window.__foodAuditHistory.push({day:G.day,unmet30:hist.reduce((n,x)=>n+Math.max(0,x.unmetFood),0),unmetDays30:hist.filter(x=>x.unmetFood>.01).length,foodNeed:G.market.foodNeed,staffCapacity:G.market.foodStaffCapacity,sellableCapacity:G.market.foodSellableCapacity,retailStock:G.market.foodRetailStock,hasRollingLabel:report.includes('Unfilled food · last 30 recorded days'),hasCapacityLabel:report.includes('Stocked grocer capacity · today'),hasPressure:report.includes('Persistent food shortfall'),hasCapacityPressure:report.includes('Grocer sales capacity:')});}}
 window.__foodAuditMode=false;regionalGateway=gatewayFn;
 const foodHistory=(G.history||[]).slice(-30).filter(x=>Number.isFinite(x.unmetFood)),foodReport=renderEconomy();return {mode,audit:window.__foodAudit,historyAudit:window.__foodAuditHistory,valid:validateTown(),cashDrift:totalMoney()-startMoney,goods:goodsBalance(),endingDay:G.day,endingUnmet:G.market.unmetFood,hardship:G.stats.hardship,historyFoodUnmet:foodHistory.reduce((n,x)=>n+x.unmetFood,0),historyFoodDays:foodHistory.filter(x=>x.unmetFood>.01).length,foodReportHasRolling:foodReport.includes('Unfilled food · last 30 recorded days'),foodReportHasPressure:foodReport.includes('Persistent food shortfall')};
};'''
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html);page.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));page.locator('#newTown').click();page.locator('#pause').click()
 saved=page.evaluate("()=>{__townTest.reset('regional',909);__townTest.step(60);return __townTest.save()}")
 runs={mode:page.evaluate('a=>__foodAuditRun(a.s,a.m)',{'s':saved,'m':mode}) for mode in ('connected','road')}
 browser.close()
assert not errors,errors
for run in runs.values():
 assert run['valid']['ok'] and abs(run['cashDrift'])<.1 and max(abs(x['error']) for x in run['goods'])<.01
 assert all(h['hasRollingLabel'] and h['hasCapacityLabel'] for h in run['historyAudit'])
 assert any(h['unmet30']>1 and h['hasPressure'] for h in run['historyAudit']),run['historyAudit']
 assert all(h['hasCapacityPressure']==(h['foodNeed']>h['sellableCapacity']+.01) for h in run['historyAudit']),run['historyAudit']
 assert all(r['unmet']>.001 for r in run['audit'])
byday={}
for mode,run in runs.items():
 daily={}
 for r in run['audit']:
  d=daily.setdefault(str(r['day']),{'households':0,'people':0,'unmet':0,'noReach':0,'capacityExhausted':0,'cashLimitedCandidates':0,'depositHouseholds':0,'bankDeposits':0,'minCash':float('inf'),'maxCash':0,'minLiquidity':float('inf'),'maxLiquidity':0,'examples':[],'retail':{'stores':r['allStores'],'stock':r['allStoreStock'],'capacity':r['initialStoreCapacity'],'sellable':r['initialSellableFood'],'shopsSelling':r['storesWithSellableFood'],'staff':r['initialStoreStaff']}})
  d['households']+=1;d['people']+=r['people'];d['unmet']+=r['unmet'];d['noReach']+=not bool(r['reachable']);d['capacityExhausted']+=bool(r['reachable'] and r['accessibleCapacity']<=.001 and r['accessibleStock']>.001);d['cashLimitedCandidates']+=r['cashBeforeFood']<r['unmet']*min((x['price']*(1+r['foodTax']/100) for x in r['reachable']),default=float('inf'));d['depositHouseholds']+=any(b['deposit']>0 for b in r['bankFunds']);d['bankDeposits']+=sum(b['deposit'] for b in r['bankFunds']);d['minCash']=min(d['minCash'],r['cashBeforeFood']);d['maxCash']=max(d['maxCash'],r['cashBeforeFood']);d['minLiquidity']=min(d['minLiquidity'],r['liquidity']);d['maxLiquidity']=max(d['maxLiquidity'],r['liquidity'])
  if len(d['examples'])<3:d['examples'].append(r)
 byday[mode]=daily
output={'source_sha256':hashlib.sha256(bundleSource.encode()).hexdigest(),'runs':runs,'byDay':byday}
out=ROOT/'reports/food-shortage-recovery';out.mkdir(exist_ok=True);(out/'household-access-audit.json').write_text(json.dumps(output,indent=2)+'\n')
(ROOT/'docs/evidence/food-shortage-recovery8/household-access-audit.json').write_text(json.dumps(output,indent=2)+'\n')
for mode,days in byday.items():
 for day,d in days.items():print(mode,day,'unmet households/people/qty',d['households'],d['people'],round(d['unmet'],1),'noReach',d['noReach'],'capacity exhausted',d['capacityExhausted'],'cash constrained',d['cashLimitedCandidates'],'deposit HH',d['depositHouseholds'],'deposits',round(d['bankDeposits'],1),'cash min/max',round(d['minCash'],1),round(d['maxCash'],1),'liquidity min/max',round(d['minLiquidity'],1),round(d['maxLiquidity'],1),'town stock/capacity/sellable/staff',round(d['retail']['stock']),round(d['retail']['capacity']),round(d['retail']['sellable']),d['retail']['staff'],'shops able to sell',d['retail']['shopsSelling'])
print('PASS matched household purchase trace, daily goods conservation, town validity and cash invariants')
