"""Current-public bridge safety, maintenance, archive and UI cancellation regression."""
from pathlib import Path
import ast
import json
import hashlib
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html

source=(ROOT/'assets/game.js').read_text()
tree=ast.parse((ROOT/'tests/test_road_bridge.py').read_text())
probe=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
audit=r'''window.__bridgePublicAudit={
 guards:()=>{const g=G,bank=roadId(63,15),cells=[1984,1985,1986,1987,1988],answer={};
  const own=g.charter.owned,rev=g.charter.revision;g.charter.owned=own.filter(id=>id!=='east-meadow');g.charter.revision=own.length-1;charterOwnershipCache=null;answer.unowned=bridgeCandidateFromBank(bank);g.charter.owned=own;g.charter.revision=rev;charterOwnershipCache=null;
  const oldWater=g.waterway;g.waterway={version:1,serial:1,manifests:[{id:1,path:[cells[2]]}],exports:0,fees:0};answer.navigation=bridgeCandidateFromBank(bank);g.waterway=oldWater;
  const dock={id:999999,kind:'wharf',x:66,y:15,footprint:[cells[2]],firm:-1};g.buildings.push(dock);invalidateBuildingIndex();answer.dock=bridgeCandidateFromBank(bank);g.buildings.pop();invalidateBuildingIndex();
  return answer;},
 snapshot:()=>({save:__bridgeTest.save(),money:totalMoney(),treasury:G.treasury,region:G.region,spending:G.cumulative.spending,bridgeCount:G.bridges?.length||0,condition:G.bridges?.[0]?.condition,tiles:G.bridges?.[0]?.cells.map(id=>G.tiles[id]),water:G.bridges?.[0]?.cells.map(id=>waterNetwork().nodes.has(id)),road:G.bridges?.[0]?.cells.map(id=>roadSurface(id)),shipment:G.regionalTrade?.shipments.map(o=>({id:o.id,stage:o.stage,activePath:o.activePath,path:o.path})),issues:validateTown().issues}),
 drain:()=>{const cash=G.treasury;G.region+=cash;G.treasury=0;const before=totalMoney();for(let i=0;i<215;i++)maintainRoadBridges();invalidateRoads();const b=G.bridges[0];return {before,money:totalMoney(),condition:b.condition,closed:!roadSurface(b.cells[0]),water:b.cells.every(id=>waterNetwork().nodes.has(id)),accounts:{treasury:G.treasury,region:G.region}};},
 point:(x,y)=>{const p=iso(x,y),r=cv.getBoundingClientRect();cam={x:p[0],y:p[1]+18,zoom:1};dirty=true;draw();return [r.left+cw/2,r.top+ch/2];},
 quoteRemoval:(x,y)=>roadRemovalQuote(x,y),repairQuote:id=>bridgeRepairQuote(id),allocate:n=>{if(G.region<n)return false;G.region-=n;G.treasury+=n;return true;},shipment:id=>{const o=G.regionalTrade.shipments.find(v=>v.id===id);return o&&{day:G.day,stage:o.stage,activePath:o.activePath.slice(),cells:G.bridges[0].cells.slice(),money:totalMoney(),save:__townTest.save(),quote:bridgeRemovalQuote(G.bridges[0].id),valid:validateTown()};},failedTick:()=>{const b=G.bridges[0],r=bridgeRepairQuote(b.id),d=bridgeRemovalQuote(b.id),road=roadRemovalQuote(44,15),before=__townTest.save();simulationTickFailed=true;const results={build:commitRoadBridge(1983,'failed-tick'),repair:repairRoadBridge(b.id,r.key),decommission:decommissionBridge(b.id,d.key),road:retireRoadTile(44,15,road.key)};simulationTickFailed=false;return {results,before,after:__townTest.save()};},step:n=>__townTest.step(n),load:s=>__townTest.load(s)
};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n'+audit+'\n// SOURCE: 99-instrumentation.js')
def model_without_dialog_audit(payload):
    model=json.loads(payload)
    for key in ('events','journal','roadMetrics','councilInbox'):
        model.pop(key,None)
    return model
result={'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':844,'height':390});page.set_default_timeout(10000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html);page.add_script_tag(content=script);page.locator('#newTown').click();page.locator('#pause').click()
 initial=page.evaluate('__bridgeTest.setup()');assert initial['quote']['ok']
 guards=page.evaluate('__bridgePublicAudit.guards()')
 assert not guards['unowned']['ok'] and not guards['navigation']['ok'] and not guards['dock']['ok'],guards
 assert 'town-owned road' in guards['unowned']['reason'].lower() or 'owned' in guards['unowned']['reason'].lower(),guards
 assert 'safe short span' in guards['navigation']['reason'].lower(),guards
 assert 'safe short span' in guards['dock']['reason'].lower(),guards
 # Cancel through the production review dialog and compare the complete saved model.
 page.locator('[data-panel=construction]').click();page.locator('[data-bridge-build]').scroll_into_view_if_needed();page.locator('[data-bridge-build]').click();point=page.evaluate('__bridgePublicAudit.point(63,15)');page.mouse.click(*point)
 assert page.locator('#eventDialog').is_visible();before_cancel=page.evaluate('__bridgePublicAudit.snapshot()');page.locator('[data-event-choice="1"]').click();after_cancel=page.evaluate('__bridgePublicAudit.snapshot()')
 assert model_without_dialog_audit(before_cancel['save'])==model_without_dialog_audit(after_cancel['save']) and before_cancel['money']==after_cancel['money'] and after_cancel['bridgeCount']==0
 # Authorize through the same live map path and verify ordinary capital accounting.
 page.locator('[data-panel=construction]').click();page.locator('[data-bridge-build]').scroll_into_view_if_needed();page.locator('[data-bridge-build]').click();point=page.evaluate('__bridgePublicAudit.point(63,15)');page.mouse.click(*point);page.locator('[data-event-choice="0"]').click()
 built=page.evaluate('__bridgePublicAudit.snapshot()');assert built['bridgeCount']==1 and built['tiles']==[4]*5 and built['water']==[True]*5 and built['road']==[True]*5,built
 assert abs(built['money']-initial['total'])<.001 and abs(built['treasury']-(initial['treasury']-13450))<.001 and abs(built['region']-(initial['accounts']['region']+13450))<.001,built
 failed_tick=page.evaluate('__bridgePublicAudit.failedTick()');assert all(not v['ok'] and 'recover' in v['reason'].lower() for v in failed_tick['results'].values()) and failed_tick['before']==failed_tick['after'],failed_tick
 # A normal retirement quote is also review-only until the mayor confirms it.
 removal=page.evaluate('__bridgePublicAudit.quoteRemoval(44,15)');assert removal['ok'],removal
 page.locator('[data-panel=construction]').click();page.locator('[data-road-remove-tool]').scroll_into_view_if_needed();page.locator('[data-road-remove-tool]').click();point=page.evaluate('__bridgePublicAudit.point(44,15)');page.mouse.click(*point)
 assert page.locator('#eventDialog').is_visible();road_before=page.evaluate('__bridgePublicAudit.snapshot()');page.locator('[data-event-choice="1"]').click();road_after=page.evaluate('__bridgePublicAudit.snapshot()')
 assert model_without_dialog_audit(road_before['save'])==model_without_dialog_audit(road_after['save']) and road_before['bridgeCount']==road_after['bridgeCount']==1
 # Move the contractor's liquid cash to reserve without changing total funds;
 # then exercise the production maintenance rule and paid repair dialog.
 closure=page.evaluate('__bridgePublicAudit.drain()');assert closure['condition']<25 and closure['closed'] and closure['water'] and abs(closure['before']-closure['money'])<.001,closure
 closed=page.evaluate('__bridgePublicAudit.snapshot()');assert closed['condition']<25 and closed['road']==[False]*5 and closed['water']==[True]*5,closed
 repair_quote=page.evaluate('id=>__bridgePublicAudit.repairQuote(id)',1);assert repair_quote['ok'] and repair_quote['cost']>0
 page.locator('[data-panel=construction]').click();repair=page.locator('[data-bridge-repair="1"]');repair.scroll_into_view_if_needed();repair.click();assert page.locator('#eventDialog').is_visible()
 repair_before=page.evaluate('__bridgePublicAudit.snapshot()');page.locator('[data-event-choice="1"]').click();repair_cancel=page.evaluate('__bridgePublicAudit.snapshot()');assert model_without_dialog_audit(repair_before['save'])==model_without_dialog_audit(repair_cancel['save'])
 repair=page.locator('[data-bridge-repair="1"]')
 if not repair.is_visible(): page.locator('[data-panel=construction]').click()
 repair=page.locator('[data-bridge-repair="1"]');repair.scroll_into_view_if_needed();repair.click();page.locator('[data-event-choice="0"]').click()
 unaffordable=page.evaluate('__bridgePublicAudit.snapshot()');assert unaffordable['condition']==closed['condition'] and unaffordable['treasury']==0
 assert page.evaluate('(n)=>__bridgePublicAudit.allocate(n)',repair_quote['cost'])
 repair=page.locator('[data-bridge-repair="1"]')
 if not repair.is_visible(): page.locator('[data-panel=construction]').click()
 repair=page.locator('[data-bridge-repair="1"]');repair.scroll_into_view_if_needed();repair.click();page.locator('[data-event-choice="0"]').click()
 repaired=page.evaluate('__bridgePublicAudit.snapshot()');assert repaired['condition']==100 and repaired['road']==[True]*5 and repaired['water']==[True]*5 and abs(repaired['money']-closed['money'])<.001,repaired
 # Verify shipping is actually in the bridge span during delivery, then save/load
 # that state; an in-flight paid load must keep the crossing protected.
 assert page.evaluate('(n)=>__bridgePublicAudit.allocate(n)',50000)
 journey=page.evaluate('__bridgeTest.settleOnEastBank()');assert journey['quantity']==60 and all(id in journey['path'] for id in initial['quote']['cells']),journey
 state=None
 for _ in range(70):
  page.evaluate('__bridgePublicAudit.step(1)');state=page.evaluate('__bridgePublicAudit.shipment(1)')
  if state and state['stage']=='delivering' and all(id in state['activePath'] for id in state['cells']):break
 assert state and state['stage']=='delivering' and all(id in state['activePath'] for id in state['cells']),state
 assert not state['quote']['ok'] and 'consignment' in state['quote']['reason'].lower(),state
 restored=page.evaluate('s=>{if(!__bridgePublicAudit.load(s))return null;return __bridgePublicAudit.shipment(1)}',state['save']);assert restored
 assert restored['stage']=='delivering' and all(id in restored['activePath'] for id in restored['cells']) and restored['valid']['ok'] and abs(restored['money']-state['money'])<.001,restored
 assert not errors,errors
 result.update({'fixture':{'span':initial['quote']['cells'],'capital':initial['quote']['cost'],'upkeep':initial['quote']['maintenance']},'protectedCases':{k:{'ok':v['ok'],'reason':v.get('reason')} for k,v in guards.items()},'failedTickGuards':{'buildRepairDecommissionRoadRetirement':True,'saveByteEqual':True},'uiBridgeCancel':{'economicModelAndRngUnchanged':True,'expectedAuditOnlyChanges':['council decision event','decision journal entry','council inbox entry','lazy road metrics cache']},'roadRetirementCancel':{'economicModelAndRngUnchanged':True},'closureAndRepair':{'conditionAfterUnderfundedMaintenance':closure['condition'],'closedRoadSurface':closure['closed'],'waterRemainedOpen':closure['water'],'unaffordableRepairBlocked':True,'repairedCondition':repaired['condition'],'totalMoneyPreserved':True},'freightMidDeliverySaveLoad':{'day':state['day'],'stage':restored['stage'],'pathContainsAllBridgeCells':True,'removalBlocked':True,'moneyPreserved':True},'errors':errors})
 out=ROOT/'docs/previews/urban8';out.mkdir(parents=True,exist_ok=True);(out/'road-bridge-public-regression.json').write_text(json.dumps(result,indent=2)+'\n');browser.close()
print('PASS current-public bridge guards, UI cancellation, closure/repair, and mid-delivery save/load')
