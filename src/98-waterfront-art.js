// Original river craft. Animation samples only staffed fishing or paid cargo;
// its bounded visual clock never draws from the simulation's seeded RNG.
function drawWaterfrontPiers(g,visible){
 for(const f of G.firms){if(!['fishery','wharf'].includes(f.kind))continue;const b=readBuild(f.building);if(!b)continue;const p=iso(b.x+.5,b.y+.5);if(!visible(p[0],p[1],80))continue;const site=waterfrontSite(b.x,b.y,f.kind);if(!site)continue;const water=iso(site.id%T+.5,(site.id/T|0)+.5),dx=water[0]-p[0],dy=water[1]-p[1],length=Math.hypot(dx,dy)||1,px=-dy/length*5,py=dx/length*5;
  polygon(g,[[p[0]+px,p[1]+py],[water[0]+px,water[1]+py],[water[0]-px,water[1]-py],[p[0]-px,p[1]-py]],f.closed?'#897f62':'#b49a6d');
  for(let k=0;k<=6;k++){const t=k/6,x=p[0]+dx*t,y=p[1]+dy*t;segment(g,[x-px,y-py],[x+px,y+py],'#806e50');}
  for(const side of [-1,1]){const x=water[0]+px*side,y=water[1]+py*side;segment(g,[x,y+6],[x,y-5],'#6d6851',2);g.fillStyle='#d2bd88';g.fillRect(x-2,y-5,4,2);}
  if(!f.closed&&f.kind==='wharf'&&(f.cargoToday||0)>0&&workingStaff(f).length){const moving=gameOptions.effects&&!gameOptions.reducedMotion,phase=moving?(frameClock*.13+f.id*.17)%1:.5,t=.25+(phase<.5?phase*2:2-phase*2)*.7,x=p[0]+dx*t,y=p[1]+dy*t;segment(g,[x-5,y+1],[x+5,y+1],'#5e6a58',2);g.fillStyle='#4a584c';g.fillRect(x-4,y+2,2,2);g.fillRect(x+3,y+2,2,2);if(phase<=.5){g.fillStyle='#ceaf72';g.fillRect(x-3,y-6,6,6);g.fillStyle='#8c7654';g.fillRect(x,y-6,1,6);}}
 }
}
function fishingRoute(site){
 const w=waterNetwork(),path=[site.id],used=new Set(path);let current=site.id;
 for(let i=0;i<8;i++){const next=w.adjacent(current).filter(n=>!used.has(n)).sort((a,b)=>{const ax=a%T,bx=b%T;return ax-bx||a-b;})[0];if(next==null)break;path.push(next);used.add(next);current=next;}
 return path;
}
function waterRoutePose(path,travel,returning=false){
 const span=path.length-1,index=Math.min(span-1,Math.floor(travel)),fraction=travel-index,r=.18,cell=id=>[id%T+.5,(id/T|0)+.5];let a=cell(path[index]),b=cell(path[index+1]),position=[a[0]+(b[0]-a[0])*fraction,a[1]+(b[1]-a[1])*fraction],tangent=[b[0]-a[0],b[1]-a[1]],corner=null,u=0;
 if(fraction>1-r&&index+2<path.length){corner=[a,b,cell(path[index+2])];u=(fraction-(1-r))/(2*r);}else if(fraction<r&&index>0){corner=[cell(path[index-1]),a,b];u=(fraction+r)/(2*r);}
 if(corner){const [before,at,after]=corner,start=[at[0]-(at[0]-before[0])*r,at[1]-(at[1]-before[1])*r],end=[at[0]+(after[0]-at[0])*r,at[1]+(after[1]-at[1])*r];position=start.map((v,k)=>(1-u)*(1-u)*v+2*(1-u)*u*at[k]+u*u*end[k]);tangent=start.map((v,k)=>2*(1-u)*(at[k]-v)+2*u*(end[k]-at[k]));}
 const p=iso(...position),sign=returning?-1:1;return {x:p[0],y:p[1],gx:position[0],gy:position[1],dx:(tangent[0]-tangent[1])*36*sign,dy:(tangent[0]+tangent[1])*18*sign};
}
let waterVesselTown=null,waterVesselClock=0,waterVessels=new Map();
function waterfrontActors(visible,presentation=null){
 if(!(presentation?.budget||visualDetailBudget()).boats)return [];
 if(waterVesselTown!==G||frameClock<waterVesselClock){waterVessels=new Map();waterVesselTown=G;waterVesselClock=frameClock;}
 const elapsed=Math.min(.25,Math.max(0,frameClock-waterVesselClock));waterVesselClock=frameClock;
 const cap=presentation?.cap??(fastRenderEnabled()?2:gameOptions.quality==='high'?10:6),actors=[],orders=new Map();
 for(const m of (G.waterway?.manifests||[]).slice().reverse())if(!orders.has(m.port))orders.set(m.port,m);
 for(const f of G.firms){if(!['fishery','wharf'].includes(f.kind))continue;const b=readBuild(f.building);if(!b||b.firm!==f.id){waterVessels.delete(f.id);continue;}
  const m=orders.get(f.id),fishing=f.kind==='fishery',working=!f.closed&&workingStaff(f).length>0,hasOrder=working&&(fishing?f.production>0:!!m),token=fishing?G.day:m?.id;
  let vessel=waterVessels.get(f.id);
  if(hasOrder&&(!vessel||!vessel.active&&vessel.lastToken!==token)){
   const site=waterfrontSite(b.x,b.y,f.kind),path=fishing?(site?fishingRoute(site):[]):m.path;
   if(path.length>=2&&(vessel||waterVessels.size<32)){vessel={id:f.id+(fishing?10000:50000),f,path:path.slice(),travel:0,cargo:fishing?'fish':m.good,quantity:fishing?f.production:m.qty,lastToken:token,active:true,turned:false,turnRemaining:0};waterVessels.set(f.id,vessel);}
  }
  if(vessel&&!vessel.active&&f.closed){waterVessels.delete(f.id);continue;}if(!vessel)continue;const span=vessel.path.length-1;
  // A vessel keeps the same paid load and continuous route across simulation
  // days. New manifests never teleport a boat or change its cargo mid-voyage.
  if(vessel.active){if(vessel.turnRemaining>0)vessel.turnRemaining=Math.max(0,vessel.turnRemaining-elapsed);else{vessel.travel+=elapsed*(fishing?.32:.48);if(!vessel.turned&&vessel.travel>=span){vessel.travel=span;vessel.turned=true;vessel.turnRemaining=1.2;}if(vessel.travel>=span*2){vessel.travel=0;vessel.active=false;}}}
  const returning=!vessel.active||vessel.travel>span||vessel.turned&&vessel.travel===span&&vessel.turnRemaining===0,travel=vessel.travel>span?span*2-vessel.travel:vessel.travel,pose=waterRoutePose(vessel.path,travel,returning);
  if(vessel.turnRemaining>0){const angle=Math.atan2(pose.dy,pose.dx)+Math.PI*(1-vessel.turnRemaining/1.2),length=Math.hypot(pose.dx,pose.dy);pose.dx=Math.cos(angle)*length;pose.dy=Math.sin(angle)*length;}
  if(G.tiles[Math.floor(pose.gy)*T+Math.floor(pose.gx)]===1||!visible(pose.x,pose.y,30))continue;actors.push({kind:'boat',...pose,returning,...vessel});
 }
 for(const id of waterVessels.keys())if(!G.firms[id]||!readBuild(G.firms[id].building))waterVessels.delete(id);
 return actors.slice(0,cap);
}
function paintWaterBoat(g,a,clock){
 const cargo=a.cargo!=='fish',length=cargo?17:10,width=cargo?6:4,m=Math.hypot(a.dx,a.dy)||1;g.save();g.translate(a.x,a.y+(gameOptions.reducedMotion?0:Math.sin(clock*1.7+a.id)*.45));g.transform(a.dx/m,a.dy/m,-a.dy/m*.85,a.dx/m*.65,0,0);
 const alpha=g.globalAlpha,wake=.55+Math.sin(clock*5+a.id)*.15;if(a.active)for(let j=0;j<3;j++){g.globalAlpha=alpha*(.28-j*.06)*wake;segment(g,[-length-2-j*4,-width-j*2],[-length+3-j*4,width+j*2],'#e3e7c8',1);}g.globalAlpha=alpha;
 polygon(g,[[-length,-width],[length-3,-width],[length+3,0],[length-3,width],[-length,width],[-length-2,0]],'#425d57');polygon(g,[[-length+1,-width+1],[length-3,-width+1],[length,0],[length-3,width-1],[-length+1,width-1]],cargo?'#c3b88e':'#ad8b5d');
 if(cargo){g.fillStyle='#e4d5ac';g.fillRect(-length+2,-width+1,6,width*2-2);g.fillStyle='#648d91';g.fillRect(-length+6,-width+1,2,width*2-2);if(!a.returning){for(let j=0;j<3;j++){g.fillStyle=['#b77851','#999c68','#cfb36f'][j];g.fillRect(-4+j*5,-width+1,4,width*2-2);g.fillStyle='#76654c';g.fillRect(-4+j*5,-width+1,1,width*2-2);}}}else{g.fillStyle='#718d78';g.fillRect(-3,-2,5,4);g.fillStyle='#d2b088';g.fillRect(-1,-3,2,2);segment(g,[2,-width],[5,-width-5],'#dbd1a4');}
 if(!cargo&&a.active&&a.travel>(a.path.length-1)*.7&&a.travel<(a.path.length-1)*1.3){const sway=Math.sin(clock*2+a.id);polygon(g,[[0,-width],[7,-width-8+sway],[-5,-width-10+sway]],'#b9c6a050');for(let j=0;j<4;j++)segment(g,[0,-width],[-5+j*4,-width-9+sway],'#c4c9a780');}segment(g,[-length+1,-width],[length-3,-width],'#e1c995');g.restore();
}
function waterfrontPanel(){const state=G.waterway||{},wharves=G.firms.filter(f=>f.kind==='wharf'&&!f.closed),fisheries=G.firms.filter(f=>f.kind==='fishery'&&!f.closed);return `<details class="council-card"><summary>Working waterfront · fisheries & river cargo</summary><p class="desc">Build beside real water and a connected road. Fisheries turn staffed catch into food. Cargo wharves require a river outlet; an enclosed lake can support fishing, but cannot carry regional exports. Exporters compare road and river freight costs. A dock without crews or competitive orders earns nothing.</p><div class="statgrid">${stat('Trading fisheries',fisheries.length)}${stat('Trading cargo wharves',wharves.length)}${stat('River cargo today',policyNumber(state.todayCargo||0))}${stat('Wharf receipts today',money(state.todayFees||0))}</div><p class="desc">A cargo manifest belongs to its paying regional buyer after collection. Boats show paid cargo voyages and fishing trips. Export ownership passes to the regional buyer on collection; follow the accounts to see stock and payments.</p><button data-waterfront-camera="1">Visit the river landing</button><button data-waterfront-build="1">Choose a waterfront business</button></details>`;}
const waterfrontConstructionBase=renderConstructionFull;renderConstructionFull=function(){return waterfrontConstructionBase()+waterfrontPanel();};
document.addEventListener('click',e=>{if(e.target.closest('[data-waterfront-camera]')){const b=G.buildings.find(b=>b.kind==='wharf')||G.buildings.find(b=>b.kind==='fishery')||{x:5,y:27},p=iso(b.x+.5,b.y+.5);cam={x:p[0]+40,y:p[1],zoom:1.15};closePanel();dirty=true;}if(e.target.closest('[data-waterfront-build]')){constructionCategory='waterfront';openPanel('construction');$('panelBody').scrollTop=0;}});

let selectedWaterTrip=null;
function inspectWaterTripAt(x,y){
 const radius=22/Math.max(.32,cam.zoom),boat=waterfrontActors(()=>true).filter(a=>Math.hypot(a.x-x,a.y-y)<radius).sort((a,b)=>Math.hypot(a.x-x,a.y-y)-Math.hypot(b.x-x,b.y-y))[0];if(!boat)return false;
 selectedWaterTrip={firm:boat.f.id,token:boat.lastToken,cargo:boat.cargo,quantity:boat.quantity,path:boat.path.slice(),returning:boat.returning};selected={id:boat.f.building};openPanel('inspect');dirty=true;return true;
}
function drawSelectedWaterRoute(g){
 if(!selectedWaterTrip)return;if(!selected||readBuild(selected.id)?.firm!==selectedWaterTrip.firm){selectedWaterTrip=null;return;}
 const path=waterVessels.get(selectedWaterTrip.firm)?.path||selectedWaterTrip.path;g.save();g.strokeStyle='#f2d492';g.lineWidth=2/Math.max(.32,cam.zoom);g.setLineDash([5/cam.zoom,4/cam.zoom]);g.beginPath();path.forEach((id,i)=>{const q=iso(id%T+.5,(id/T|0)+.5);i?g.lineTo(...q):g.moveTo(...q)});g.stroke();g.restore();
}
function selectedWaterInfo(){const live=selectedWaterTrip&&waterVessels.get(selectedWaterTrip.firm);return live?{cargo:live.cargo,quantity:live.quantity,journey:!live.active?'Moored at its landing':live.turnRemaining>0?'Turning at the destination':live.travel>live.path.length-1?'Returning to its landing':'Outbound from its landing'}:selectedWaterTrip?{...selectedWaterTrip,journey:'Previously selected voyage'}:null;}
const waterInspectBase=renderInspectFull;renderInspectFull=function(){const info=selectedWaterInfo();return (info&&readBuild(selected?.id)?.firm===selectedWaterTrip.firm?head(info.cargo==='fish'?'Fishing trip':'Paid regional cargo voyage')+strip('Sampled load',policyNumber(info.quantity)+' '+(info.cargo==='fish'?'food units':info.cargo))+strip('Journey',info.journey)+tip('The highlighted route follows connected water. The business accounts below record the actual catch or paid freight.'):'' )+waterInspectBase();};

function drawWaterLife(g,visible){
 if(!gameOptions.effects||gameOptions.reducedMotion||gameOptions.quality==='low'||cam.zoom<.32)return;
 const cap=fastRenderEnabled()?3:gameOptions.quality==='high'?14:8;let count=0;
 for(const id of waterNetwork().nodes){if(G.tiles[id]!==2||hash(id)%9!==0)continue;const p=iso(id%T+.5,(id/T|0)+.5);if(!visible(p[0],p[1],20))continue;const phase=(frameClock*.24+(hash(id)%101)/101)%1,light=Math.sin(phase*Math.PI);g.globalAlpha=light*.35;
  segment(g,[p[0]-11+phase*5,p[1]+5-phase*2],[p[0]+7+phase*5,p[1]-4-phase*2],'#deead0',1);g.globalAlpha=light*.18;segment(g,[p[0]-6,p[1]+8],[p[0]+13,p[1]-1],'#c8dfc8',1);g.globalAlpha=1;if(++count>=cap)break;
 }
}
