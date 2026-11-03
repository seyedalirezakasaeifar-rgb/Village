"""Purchased southern riverbank becomes genuine connected, productive territory."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
script=source.decode().replace('// SOURCE: 99-instrumentation.js',r'''
window.__annexNetworkProbe=()=>{const original=G;try{G=JSON.parse(JSON.stringify(original));invalidateRoads();const total=totalMoney(),p=ANNEX_PARCELS.find(p=>p.id==='river-reach'),bought=purchaseParcel(p.id,parcelSurvey(p).price);if(!bought)throw Error('Southern deed unaffordable');
 const net=graph();let plan=null;
 for(let y=58;y<75&&!plan;y++)for(let x=3;x<10&&!plan;x++){
  if(!canPlace(x,y,false,'fishery'))continue;
  for(const [dx,dy] of roadOffsets){const start=roadId(x+dx,y+dy),allowed=id=>{const xx=id%T,yy=id/T|0;return xx>=2&&yy>=2&&xx<T-2&&yy<T-2&&charterOwns(xx,yy)&&[0,1,3].includes(G.tiles[id])&&!buildingAt(xx,yy)&&!G.landUse[id]&&!(xx===x&&yy===y);};if(!allowed(start))continue;
   const queue=[start],parent=new Map([[start,-1]]);let end=null;for(let i=0;i<queue.length&&i<6400;i++){const at=queue[i];if(net.parts[at]===net.mainPart){end=at;break;}for(const [ax,ay] of roadOffsets){const nx=at%T+ax,ny=(at/T|0)+ay,id=roadId(nx,ny);if(nx<0||ny<0||nx>=T||ny>=T||parent.has(id)||!allowed(id))continue;parent.set(id,at);queue.push(id);}}
   if(end!=null){const path=[];for(let at=end;at!==-1;at=parent.get(at))path.push(at);plan={x,y,path};break;}
  }
 }
 if(!plan)throw Error('No viable new waterfront connection');const stub=plan.path[plan.path.length-1];construct('road',stub%T,stub/T|0,true);flushRoadBatch();const count=G.firms.length;construct('fishery',plan.x,plan.y,true);const f=G.firms[G.firms.length-1],b=readBuild(f.building),disconnected=!regionalUtilityAccess(b)&&f.workers.length===0;let roads=1;for(const id of plan.path)if(G.tiles[id]!==1){construct('road',id%T,id/T|0,true);roads++;}flushRoadBatch();const linked=graph().parts[graph().portals.get(b.id)]===graph().mainPart;const repeat=G.treasury;construct('fishery',plan.x,plan.y,true);const repeated=G.firms.length===count+1&&G.treasury===repeat;
 // Recruitment is endogenous: allow real job assignment rather than inventing crew.
 assignJobs();const crews=f.workers.length;const connected=regionalUtilityAccess(b);let production=0;for(let i=0;i<35;i++){tick();production+=f.production||0;}
 const result={bought,territory:[plan.x,plan.y],roads,linked,disconnected,connected,repeated,crews,production,drift:totalMoney()-total,valid:validateTown().ok,goods:goodsBalance().every(v=>Math.abs(v.error)<.001),saved:JSON.parse(archivePayload()).charter.owned};return result;
 }finally{G=original;invalidateRoads();staticDirty=true;dirty=true;}};
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("settlement",42)');r=p.evaluate('__annexNetworkProbe()');assert all(r[k] for k in ['bought','linked','disconnected','connected','repeated','valid','goods']),r;assert r['territory'][1]>=56 and r['roads']>0 and r['crews']>0 and r['production']>0 and abs(r['drift'])<.001 and 'river-reach' in r['saved'],r;assert not errors,errors;b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-working-river';out.mkdir(exist_ok=True);(out/'annexation-network.json').write_text(json.dumps({'source_sha256':sha,'probe':r},indent=2)+'\n');print('PASS mayor-bought outer riverbank, paid road extension, real crew recruitment and productive fishery, utility connectivity, repeat placement, 35-day accounting',r)
