// Transit's original diorama kit. Pure visual samples and cached legal alignment;
// no fare, passenger, staffing or route-search operation occurs here.
transitFacilityArt=function(g,b,w,d){
 const depot=b.kind==='transit_depot';dioramaFoundation(g,b,w,d);
 if(depot){
  const u=-w*.39,v=-d*.34;dioramaSurface(g,u,v,w*.75,d*.63,0,29,'#acb6a2','brick');
  for(let j=0;j<3;j++){const x=u+.07+j*w*.23;dioramaSurface(g,x,v+d*.63+.02,w*.19,.025,1,18,'#426b6c');for(let z=5;z<18;z+=4)segment(g,point(x,v+d*.63+.05,z),point(x+w*.19,v+d*.63+.05,z),'#93aaa0');dioramaWindow(g,x+.02,v+d*.63+.055,12,'front',w*.15,4,nightMode);}
  for(let j=0;j<3;j++)gable(g,u+j*w*.25,v,w*.25,d*.63,30,8,'#597f83');
  dioramaSurface(g,u+w*.66,v+.03,w*.20,d*.57,0,37,'#cfc5a5');slab(g,u+w*.64,v+.01,w*.24,d*.61,39,'#597b7a');dioramaWindow(g,u+w*.68,v+d*.60+.01,23,'front',w*.15,8,nightMode);
  const q=point(0,v+d*.63+.06,27);g.fillStyle='#365e61';g.fillRect(q[0]-22,q[1]-4,44,7);g.fillStyle='#ecdfb7';g.font='bold 5px Arial';g.textAlign='center';g.fillText('TRANSIT WORKS',q[0],q[1]+1);
  // Marked apron bays are equipment space; no parked paid fleet is invented.
  for(let j=0;j<3;j++){const x=u+.06+j*w*.23;segment(g,point(x,d*.40,1),point(x+w*.18,d*.40,1),'#d7c594',1);}
 }else{
  for(const x of [-.31,.28])dioramaSurface(g,x,-.20,.09,.38,0,27,'#99aa99');
  slab(g,-.47,-.29,.94,.58,27,'#5d7976');slab(g,-.47,-.29,.94,.58,30,'#d3cbb0');
  for(const y of [-.26,.25]){segment(g,point(-.43,y,33),point(.43,y,33),'#7e9b91',2);for(let j=0;j<5;j++)segment(g,point(-.4+j*.2,y,30),point(-.4+j*.2,y,36),'#7a978d');}
  for(const x of [-.37,.33])segment(g,point(x,.20,31),point(x,.20,44),'#607f77',2);
  dioramaHipRoof(g,-.50,-.32,1,.64,43,5,'#517d83');
  for(let j=0;j<7;j++)slab(g,.24,.24+j*.027,.20,.03,2+j*4,'#c3c4a5');
  dioramaSurface(g,-.36,.32,.12,.10,0,17,'#527e7b');const q=point(-.30,.43,11);g.fillStyle='#ead9a3';g.font='bold 6px Arial';g.textAlign='center';g.fillText('M',q[0],q[1]);
 }
};
let transitArtGeometry=null;
function transitInfrastructureItems(visible){
 const state=G.transit;if(!state?.tracks.length)return [];
 if(transitArtGeometry?.tracks!==state.tracks||transitArtGeometry.revision!==state.revision||transitArtGeometry.size!==T){
  const tiles=new Set(state.tracks),items=[];
  for(const id of state.tracks){const a=roadCenter(id);if(id%3===0)items.push({kind:'transitPier',id,x:a[0],y:a[1]+9,a});
   for(const n of [id+1,id+T])if(tiles.has(n)&&Math.abs(id%T-n%T)+Math.abs((id/T|0)-(n/T|0))===1){const b=roadCenter(n);items.push({kind:'guideway',id:id*T*T+n,x:(a[0]+b[0])/2,y:(a[1]+b[1])/2-25,a,b});}
  }transitArtGeometry={tracks:state.tracks,revision:state.revision,size:T,items};
 }return transitArtGeometry.items.filter(i=>visible(i.x,i.y,75)&&(cam.zoom>=.38||i.kind==='guideway'));
}
function paintTransitStructure(g,item){
 const {a,b}=item;if(item.kind==='transitPier'){segment(g,[a[0],a[1]+9],[a[0],a[1]-21],'#698679',4);segment(g,[a[0]-1,a[1]+7],[a[0]-1,a[1]-20],'#b4be9d',1.5);segment(g,[a[0]-6,a[1]-20],[a[0]+6,a[1]-20],'#8f9f88',3);return;}
 segment(g,[a[0],a[1]-21],[b[0],b[1]-21],'#4b6863',13);segment(g,[a[0],a[1]-25],[b[0],b[1]-25],'#b8bda0',12);
 const dx=b[0]-a[0],dy=b[1]-a[1],m=Math.hypot(dx,dy),nx=-dy/m*3.4,ny=dx/m*3.4;
 for(const sign of [-1,1])segment(g,[a[0]+nx*sign,a[1]-27+ny*sign],[b[0]+nx*sign,b[1]-27+ny*sign],'#526f6b',1.5);
 if(cam.zoom>.6)for(let j=1;j<5;j++){const t=j/5,x=a[0]+dx*t,y=a[1]+dy*t-26;segment(g,[x-nx,y-ny],[x+nx,y+ny],'#8b9b80',1);}
}
const transitSceneSpriteBase=drawSceneSprite;
drawSceneSprite=function(g,item){if(item.kind==='guideway'||item.kind==='transitPier')paintTransitStructure(g,item);else transitSceneSpriteBase(g,item);};
// The original infrastructure renderer is retained only for explicit network
// drafting overlays; physical structures now participate in scene depth.
const transitDraftInfrastructureBase=drawTransitInfrastructure;
drawTransitInfrastructure=function(g,visible){
 const snap=overlay==='transit'||buildMode==='transit_route'?transitRenderSnapshot():{routes:G.transit?.routes||[]};g.save();
 if(cam.zoom>=.45){const seen=new Set();for(const r of snap.routes){if(r.mode!=='bus')continue;for(const id of r.stops){if(seen.has(id))continue;seen.add(id);const p=roadCenter(id);if(!visible(p[0],p[1],25))continue;segment(g,[p[0]+12,p[1]+4],[p[0]+12,p[1]-12],'#5e7b67',1.5);g.fillStyle=r.color;g.fillRect(p[0]+9,p[1]-13,6,6);g.fillStyle='#e9dbad';g.fillRect(p[0]+10,p[1]-12,4,1);}}}
 if(overlay==='transit'||buildMode==='transit_route')for(const r of snap.routes){g.globalAlpha=.65;g.strokeStyle=r.color;g.lineWidth=2/cam.zoom;g.beginPath();r.path.forEach((id,i)=>{const p=roadCenter(id),y=p[1]-(r.mode==='elevated'?27:0);i?g.lineTo(p[0],y):g.moveTo(p[0],y)});g.stroke();}
 if(transitDraft)for(let i=0;i<transitDraft.stops.length;i++){const id=transitStopRoad(transitDraft.mode,transitDraft.stops[i]);if(id==null)continue;const p=roadCenter(id);g.globalAlpha=1;g.fillStyle='#f5dda0';g.beginPath();g.arc(p[0],p[1],8,0,Math.PI*2);g.fill();g.fillStyle='#365f59';g.font='bold 9px Arial';g.textAlign='center';g.fillText(i+1,p[0],p[1]+3);}
 g.restore();
};
// Shuttle routes reverse at their terminals. Keep a carriage from snapping its
// facing at the exact route endpoint: a short, eased half turn reads as a
// purposeful station turnaround while retaining the same actual route pose.
function transitTerminalHeading(r,phase,dx,dy){
 const span=r.path.length-1,cycle=span*2,turn=.24;if(span<2)return [dx,dy];
 let progress=null,base=null,reverse=false;
 if(phase>=span-turn&&phase<=span+turn){const a=roadCenter(r.path[span-1]),b=roadCenter(r.path[span]);base=Math.atan2(b[1]-a[1],b[0]-a[0]);progress=(phase-(span-turn))/(turn*2);}
 else if(phase<=turn||phase>=cycle-turn){const a=roadCenter(r.path[0]),b=roadCenter(r.path[1]);base=Math.atan2(b[1]-a[1],b[0]-a[0]);progress=phase<=turn?(phase+turn)/(turn*2):(phase-(cycle-turn))/(turn*2);reverse=true;}
 if(progress==null)return [dx,dy];
 const eased=progress*progress*(3-2*progress),angle=base+Math.PI*(reverse?1+eased:eased),length=Math.hypot(dx,dy)||1;
 return [Math.cos(angle)*length,Math.sin(angle)*length];
}
function transitArtActors(visible,time=frameClock,zoom=cam.zoom){
 if(gameOptions.reducedMotion||!gameOptions.traffic||zoom<.38)return [];
 const poses=transitVehiclePoses(time,zoom),routes=new Map(transitTopology().routes.map(r=>[r.id,r])),ordinals=new Map(),result=[];
 for(const pose of poses){const r=routes.get(pose.route),index=ordinals.get(pose.route)||0;ordinals.set(pose.route,index+1);if(!r||!r.path||r.path.length<2)continue;const count=Math.min(4,r.stats.staff.length/TRANSIT_MODES[r.mode].staff),span=r.path.length-1,phase=(time*(r.mode==='bus'?.48:.85)+index*span*2/count)%(span*2),forward=phase<span,at=forward?phase:span*2-phase,i=Math.min(span-1,Math.floor(at)),t=at-i,points=[Math.max(0,i-1),i,i+1,Math.min(span,i+2)].map(k=>roadCenter(r.path[k])),[previous,a,b,next]=points;
  let x=pose.x,y=pose.y,dx=pose.dx,dy=pose.dy,corner,u;const radius=.18;
  if(t<radius&&i>0){corner=[previous,a,b];u=(t+radius)/(2*radius);}else if(t>1-radius&&i+2<r.path.length){corner=[a,b,next];u=(t-1+radius)/(2*radius);}
  if(corner){const [start,c,end]=corner,s=c.map((v,k)=>v-(v-start[k])*radius),e=c.map((v,k)=>v+(end[k]-v)*radius),p=c.map((v,k)=>(1-u)*(1-u)*s[k]+2*(1-u)*u*v+u*u*e[k]),h=c.map((v,k)=>2*(1-u)*(v-s[k])+2*u*(e[k]-v));x=p[0];y=p[1]-pose.elevation;dx=h[0]*(forward?1:-1);dy=h[1]*(forward?1:-1);}
  [dx,dy]=transitTerminalHeading(r,phase,dx,dy);
  if(visible(x,y,70))result.push({...pose,x,y,dx,dy,kind:'transitArt'});if(result.length>=48)break;
 }return result;
}
function paintTransitVehicle(g,p){
 const metro=p.mode==='elevated',m=Math.hypot(p.dx,p.dy)||1,L=metro?18:16,W=4.5;
 g.save();g.translate(p.x,p.y);g.transform(p.dx/m,p.dy/m,-p.dy/m*1.35,p.dx/m*.45,0,0);
 const wagons=metro?2:1;for(let j=0;j<wagons;j++){const x=metro?(j-.5)*(L*2+2):0;
  g.fillStyle='#344f4944';g.fillRect(x-L-1,-W+3,L*2+3,W*2+2);
  for(const xx of [-L+4,L-5]){g.fillStyle='#2c423d';g.fillRect(x+xx,-W-2,5,3);g.fillRect(x+xx,W-1,5,3);}
  g.fillStyle='#506b60';g.fillRect(x-L,-W,L*2,W*2+2);g.fillStyle='#d9d7ba';g.fillRect(x-L,-W-4,L*2,W*2+2);g.fillStyle=p.color;g.fillRect(x-L,-W+2,L*2,2);
  g.fillStyle='#4e7e80';for(let k=0;k<5;k++)g.fillRect(x-L+3+k*5,-W-3,4,6);
  g.fillStyle='#dce2c9';g.fillRect(x-L+2,-W-4,L*2-4,2);g.fillStyle='#819c8d';g.fillRect(x-4,-W-4,7,2);
  g.fillStyle='#395f63';g.fillRect(x+L-4,-W-3,3,7);g.fillStyle=p.load>0?'#d8bd73':'#93a38a';g.fillRect(x+L-8,-W-3,3,2);
  g.fillStyle=nightMode?'#ffe3a0':'#ddd9b1';g.fillRect(x+L-1,-W,2,2);g.fillRect(x+L-1,W-2,2,2);g.fillStyle='#b36c50';g.fillRect(x-L,-W,1,2);
 }if(metro){g.fillStyle='#4c665b';g.fillRect(-2,-3,4,5);}g.restore();
}
