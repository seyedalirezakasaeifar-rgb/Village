// Original river craft. Animation samples only staffed fishing or paid cargo;
// its bounded visual clock never draws from the simulation's seeded RNG.
function drawWaterfrontPiers(g,visible){
 for(const f of G.firms){if(!['fishery','wharf'].includes(f.kind))continue;const b=readBuild(f.building);if(!b)continue;const p=iso(b.x+.5,b.y+.5);if(!visible(p[0],p[1],80))continue;const site=waterfrontSite(b.x,b.y,f.kind);if(!site)continue;const water=iso(site.id%T+.5,(site.id/T|0)+.5),dx=water[0]-p[0],dy=water[1]-p[1],length=Math.hypot(dx,dy)||1,px=-dy/length*5,py=dx/length*5;
  polygon(g,[[p[0]+px,p[1]+py],[water[0]+px,water[1]+py],[water[0]-px,water[1]-py],[p[0]-px,p[1]-py]],f.closed?'#897f62':'#b49a6d');
  for(let k=0;k<=6;k++){const t=k/6,x=p[0]+dx*t,y=p[1]+dy*t;segment(g,[x-px,y-py],[x+px,y+py],'#806e50');}
  for(const side of [-1,1]){const x=water[0]+px*side,y=water[1]+py*side;segment(g,[x,y+6],[x,y-5],'#6d6851',2);g.fillStyle='#d2bd88';g.fillRect(x-2,y-5,4,2);}
  if(!f.closed&&f.kind==='wharf'&&(f.cargoToday||0)>0){g.fillStyle='#ceaf72';g.fillRect(water[0]-3,water[1]-6,6,5);g.fillStyle='#8c7654';g.fillRect(water[0],water[1]-6,1,5);}
 }
}
function fishingRoute(site){
 const w=waterNetwork(),path=[site.id],used=new Set(path);let current=site.id;
 for(let i=0;i<8;i++){const next=w.adjacent(current).filter(n=>!used.has(n)).sort((a,b)=>{const ax=a%T,bx=b%T;return ax-bx||a-b;})[0];if(next==null)break;path.push(next);used.add(next);current=next;}
 return path;
}
let waterVesselTown=null,waterVesselClock=0,waterVessels=new Map();
function waterfrontActors(visible){
 if(!gameOptions.traffic||!gameOptions.effects||gameOptions.reducedMotion||gameOptions.quality==='low'||cam.zoom<.32)return [];
 if(waterVesselTown!==G||frameClock<waterVesselClock){waterVessels=new Map();waterVesselTown=G;waterVesselClock=frameClock;}
 const elapsed=Math.min(.25,Math.max(0,frameClock-waterVesselClock));waterVesselClock=frameClock;
 const cap=fastRenderEnabled()?2:gameOptions.quality==='high'?10:6,actors=[],orders=new Map();
 for(const m of (G.waterway?.manifests||[]).slice().reverse())if(!orders.has(m.port))orders.set(m.port,m);
 for(const f of G.firms){if(!['fishery','wharf'].includes(f.kind))continue;const b=readBuild(f.building);if(!b||b.firm!==f.id){waterVessels.delete(f.id);continue;}
  const m=orders.get(f.id),fishing=f.kind==='fishery',working=!f.closed&&workingStaff(f).length>0,hasOrder=working&&(fishing?f.production>0:!!m),token=fishing?G.day:m?.id;
  let vessel=waterVessels.get(f.id);
  if(hasOrder&&(!vessel||!vessel.active&&vessel.lastToken!==token)){
   const site=waterfrontSite(b.x,b.y,f.kind),path=fishing?(site?fishingRoute(site):[]):m.path;
   if(path.length>=2&&(vessel||waterVessels.size<32)){vessel={id:f.id+(fishing?10000:50000),f,path:path.slice(),travel:0,cargo:fishing?'fish':m.good,quantity:fishing?f.production:m.qty,lastToken:token,active:true};waterVessels.set(f.id,vessel);}
  }
  if(vessel&&!vessel.active&&f.closed){waterVessels.delete(f.id);continue;}if(!vessel)continue;const span=vessel.path.length-1;
  // A vessel keeps the same paid load and continuous route across simulation
  // days. New manifests never teleport a boat or change its cargo mid-voyage.
  if(vessel.active){vessel.travel+=elapsed*(fishing?.32:.48);if(vessel.travel>=span*2){vessel.travel=0;vessel.active=false;}}
  const returning=!vessel.active||vessel.travel>span,travel=vessel.travel>span?span*2-vessel.travel:vessel.travel,index=Math.min(span-1,Math.floor(travel)),fraction=travel-index,a=vessel.path[index],c=vessel.path[index+1],p=iso(a%T+.5,(a/T|0)+.5),q=iso(c%T+.5,(c/T|0)+.5),x=p[0]+(q[0]-p[0])*fraction,y=p[1]+(q[1]-p[1])*fraction;
  if(G.tiles[fraction<.5?a:c]===1||!visible(x,y,30))continue;actors.push({kind:'boat',x,y,dx:(q[0]-p[0])*(returning?-1:1),dy:(q[1]-p[1])*(returning?-1:1),returning,...vessel});
 }
 for(const id of waterVessels.keys())if(!G.firms[id]||!readBuild(G.firms[id].building))waterVessels.delete(id);
 return actors.slice(0,cap);
}
function paintWaterBoat(g,a,clock){
 const cargo=a.cargo!=='fish',length=cargo?17:10,width=cargo?6:4,m=Math.hypot(a.dx,a.dy)||1;g.save();g.translate(a.x,a.y);g.transform(a.dx/m,a.dy/m,-a.dy/m*.85,a.dx/m*.65,0,0);
 const wake=.55+Math.sin(clock*5+a.id)*.15;for(let j=0;j<3;j++){g.globalAlpha=(.28-j*.06)*wake;segment(g,[-length-2-j*4,-width-j*2],[-length+3-j*4,width+j*2],'#e3e7c8',1);}g.globalAlpha=1;
 polygon(g,[[-length,-width],[length-3,-width],[length+3,0],[length-3,width],[-length,width],[-length-2,0]],'#425d57');polygon(g,[[-length+1,-width+1],[length-3,-width+1],[length,0],[length-3,width-1],[-length+1,width-1]],cargo?'#c3b88e':'#ad8b5d');
 if(cargo){g.fillStyle='#e4d5ac';g.fillRect(-length+2,-width+1,6,width*2-2);g.fillStyle='#648d91';g.fillRect(-length+6,-width+1,2,width*2-2);if(!a.returning){for(let j=0;j<3;j++){g.fillStyle=['#b77851','#999c68','#cfb36f'][j];g.fillRect(-4+j*5,-width+1,4,width*2-2);g.fillStyle='#76654c';g.fillRect(-4+j*5,-width+1,1,width*2-2);}}}else{g.fillStyle='#718d78';g.fillRect(-3,-2,5,4);g.fillStyle='#d2b088';g.fillRect(-1,-3,2,2);segment(g,[2,-width],[5,-width-5],'#dbd1a4');}
 segment(g,[-length+1,-width],[length-3,-width],'#e1c995');g.restore();
}
function waterfrontPanel(){const state=G.waterway||{},wharves=G.firms.filter(f=>f.kind==='wharf'&&!f.closed),fisheries=G.firms.filter(f=>f.kind==='fishery'&&!f.closed);return `<details class="council-card"><summary>Working waterfront · fisheries & river cargo</summary><p class="desc">Build beside real water and a connected road. Fisheries turn staffed catch into food. Cargo wharves require a river outlet; an enclosed lake can support fishing, but cannot carry regional exports. Exporters compare road and river freight costs. A dock without crews or competitive orders earns nothing.</p><div class="statgrid">${stat('Trading fisheries',fisheries.length)}${stat('Trading cargo wharves',wharves.length)}${stat('River cargo today',policyNumber(state.todayCargo||0))}${stat('Wharf receipts today',money(state.todayFees||0))}</div><p class="desc">A cargo manifest belongs to its paying regional buyer after collection. Boats are bounded samples of those paid voyages and actual fishing work; visual speed does not change inventory or money.</p><button data-waterfront-camera="1">Visit the river landing</button><button data-waterfront-build="1">Choose a waterfront business</button></details>`;}
const waterfrontConstructionBase=renderConstructionFull;renderConstructionFull=function(){return waterfrontConstructionBase()+waterfrontPanel();};
document.addEventListener('click',e=>{if(e.target.closest('[data-waterfront-camera]')){const b=G.buildings.find(b=>b.kind==='wharf')||G.buildings.find(b=>b.kind==='fishery')||{x:5,y:27},p=iso(b.x+.5,b.y+.5);cam={x:p[0]+40,y:p[1],zoom:1.15};closePanel();dirty=true;}if(e.target.closest('[data-waterfront-build]')){constructionCategory='waterfront';openPanel('construction');$('panelBody').scrollTop=0;}});
