"""Same real construction/transit actions after synchronous and queued days."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__cooperativeActions=async staged=>{
 chosenScenario='settlement';seed(42);paused=true;const lot=buildableCandidates('business').find(p=>canPlace(p.x,p.y,true,'transit_depot')),depot=buildTransitFacility('transit_depot',lot.x,lot.y),spec={mode:'bus',depot:depot.id,stops:[roadId(27,27),roadId(28,27)],level:1},outcomes=[];
 for(let i=0;i<12;i++){
  const action=()=>{if(i===2){const road=graph().neighbors.keys().next().value,x=road%T,y=road/T|0;for(const [dx,dy]of roadOffsets){const xx=x+dx,yy=y+dy;if(xx>=0&&yy>=0&&xx<T&&yy<T&&[0,3].includes(cityCell(xx,yy))&&!G.landUse?.[roadId(xx,yy)]&&!buildingAt(xx,yy)){const before=G.construction;construct('road',xx,yy);outcomes.push(['road',G.construction>before]);break;}}}if(i===4)outcomes.push(['route',buildTransitRoute(spec,transitQuote(spec))]);if(i===8)outcomes.push(['frequency',setTransitLevel(G.transit.routes[0].id,2)]);};
  if(staged){beginCooperativeDay();await window.__cooperativeSimulation.command('Construction/transit action '+i,action);}else{tick();action();}
 }
 const g=JSON.parse(archivePayload());delete g.trafficState;delete g.visualState;return {archive:JSON.stringify(g),outcomes,rng:rngState,total:totalMoney(),valid:validateTown()};
};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);results=[]
 for staged in [False,True]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();results.append(p.evaluate('s=>__cooperativeActions(s)',staged));p.close()
 b.close()
assert results[0]==results[1],'Queued actions differ from identical committed-boundary actions'
assert results[1]['valid']['ok'] and all(row[1] for row in results[1]['outcomes']),results[1]['outcomes']
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'exactArchiveRngAndActions':True,'outcomes':results[1]['outcomes'],'total':results[1]['total'],'valid':results[1]['valid']};(ROOT/'reports/cooperative-commands-8.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));print('PASS queued real road/route/frequency commands exactly match synchronous archive, RNG, outcomes and conserved balances')
