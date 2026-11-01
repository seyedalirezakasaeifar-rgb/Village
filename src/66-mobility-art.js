// Direction-aware regional aviation, road markings and pedestrian animation.
function runwayGeometry(){
 const r=G.airport?.runway;if(!r||r.length<4)return null;
 const avg=(a,b)=>{const p=roadCenter(a),q=roadCenter(b);return [(p[0]+q[0])/2,(p[1]+q[1])/2]};
 const a=avg(r[0],r[1]),b=avg(fromEnd(r,2),fromEnd(r)),dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);
 return {a,b,dx,dy,length,nx:-dy/length,ny:dx/length};
}
function drawAirfieldGround(g){
 const r=runwayGeometry();if(!r||!G.airport?.firm&&G.airport?.firm!==0)return;
 const {a,b,dx,dy,length,nx,ny}=r;
 segment(g,a,b,'#bab498',57);segment(g,a,b,'#4d5958',45);segment(g,[a[0]+nx*19,a[1]+ny*19],[b[0]+nx*19,b[1]+ny*19],'#b5b8a0',1);segment(g,[a[0]-nx*19,a[1]-ny*19],[b[0]-nx*19,b[1]-ny*19],'#b5b8a0',1);
 g.setLineDash([8,9]);segment(g,a,b,'#e7e5cc',2);g.setLineDash([]);
 for(const t of [.06,.94])for(const off of [-13,-7,7,13]){const x=a[0]+dx*t+nx*off,y=a[1]+dy*t+ny*off;segment(g,[x-dx/length*6,y-dy/length*6],[x+dx/length*6,y+dy/length*6],'#e7e5cc',3);}
 const terminal=readBuild(G.airport.building);if(terminal){const gate=iso(terminal.x,terminal.y);gate[1]+=64;segment(g,gate,a,'#a39f8b',13);segment(g,gate,a,'#d2ba68',1);}
}
function paintRegionalAircraft(g,x,y,dx,dy,altitude,clock,gear=true){
 const length=Math.hypot(dx,dy)||1,ux=dx/length,uy=dy/length;
 // Shadow stays on the ground while the aeroplane climbs.
 g.save();g.translate(x+altitude*.13,y+8);g.transform(ux,uy,-uy*1.4,ux*.55,0,0);g.globalAlpha=clamp(.30-altitude*.0012,.04,.30);g.fillStyle='#233c36';g.beginPath();g.ellipse(0,0,29,20,0,0,Math.PI*2);g.fill();g.restore();
 g.save();g.translate(Math.round(x),Math.round(y-altitude));g.transform(ux,uy,-uy*1.4,ux*.55,0,0);
 const poly=(p,c)=>polygon(g,p,c);
 // A short-haul high-wing twin turboprop: straight wing, two nacelles, cabin,
 // cockpit, tailplane, fin and landing gear, all sharing one heading.
 if(gear){g.fillStyle='#273e3a';g.fillRect(-3,-10,5,3);g.fillRect(-3,7,5,3);g.fillRect(18,-1,4,3);}
 poly([[-23,-12],[-17,-12],[-13,-3],[-13,3],[-17,12],[-23,12],[-20,0]],'#c8d1c6');
 poly([[7,-29],[-1,-29],[-8,-5],[-8,5],[-1,29],[7,29],[5,6],[5,-6]],'#d8decb');
 segment(g,[5,-27],[5,27],'#91a6a0');
 for(const side of [-1,1]){const v=side*14;poly([[-4,v-3],[9,v-3],[13,v-1],[13,v+1],[8,v+3],[-4,v+3]],'#7e9a97');g.fillStyle='#d4c9a2';g.fillRect(8,v-3,4,6);const turn=clock*27,span=Math.sin(turn)*7;segment(g,[13,v-span],[13,v+span],'#505e5866',2);segment(g,[13-2,v+span*.25],[13+2,v-span*.25],'#b4bdab',1);}
 poly([[-27,-2],[-18,-4],[17,-4],[26,-2],[29,0],[25,3],[17,5],[-18,4],[-27,2]],'#dce1cf');
 poly([[-23,2],[19,2],[26,0],[25,3],[17,5],[-18,4]],'#789a99');
 poly([[19,-3],[25,-1],[25,1],[19,2],[16,0]],'#385d67');
 for(let j=0;j<6;j++){g.fillStyle='#4b7380';g.fillRect(-12+j*4,-3,2,2);g.fillStyle='#e8e2c7';g.fillRect(-12+j*4,-1,2,1);}
 poly([[-23,0],[-22,-11],[-17,-11],[-14,0]],'#789b9a');poly([[-22,-11],[-17,-11],[-17,-7],[-22,-7]],'#c8b56e');
 g.fillStyle='#bc5444';g.fillRect(-1,-29,3,2);g.fillStyle='#6ba57d';g.fillRect(-1,27,3,2);g.restore();
}
function aviationPose(r,gate,phase){
 const a=r.a,b=r.b,lerp=(p,q,t)=>[p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t];let pos,heading=[r.dx,r.dy],alt=0,gear=true;
 const taxi=(p,q,c1,c2,t)=>{const u=1-t;return {pos:[0,1].map(k=>u*u*u*p[k]+3*u*u*t*c1[k]+3*u*t*t*c2[k]+t*t*t*q[k]),heading:[0,1].map(k=>3*u*u*(c1[k]-p[k])+6*u*t*(c2[k]-c1[k])+3*t*t*(q[k]-c2[k]))};};
 if(phase<8){const bend=Math.min(.15,Math.hypot(a[0]-gate[0],a[1]-gate[1])/r.length*.35);({pos,heading}=taxi(gate,a,lerp(gate,a,.35),[a[0]-r.dx*bend,a[1]-r.dy*bend],phase/8));}
 else if(phase<18){const t=(phase-8)/10;pos=lerp(a,b,t*t);alt=Math.max(0,t-.55)*110;}
 else if(phase<32){const u=phase-18;pos=[b[0]+r.dx*(u*.2+u*u*.005),b[1]+r.dy*(u*.2+u*u*.005)];alt=49.5+u*11;gear=false;}
 else if(phase<50)return null;
 else if(phase<66){const t=(phase-50)/16;pos=[a[0]-r.dx*(1-t)*4,a[1]-r.dy*(1-t)*4];alt=(1-t)*(1-t)*140;gear=t>.55;}
 else if(phase<75){const t=(phase-66)/9;pos=lerp(a,b,2.25*t-1.5*t*t+.25*t*t*t);}
 else if(phase<85){const bend=Math.min(.15,Math.hypot(b[0]-gate[0],b[1]-gate[1])/r.length*.35);({pos,heading}=taxi(b,gate,[b[0]+r.dx*bend,b[1]+r.dy*bend],lerp(b,gate,.7),(phase-75)/10));}
 else{pos=gate;heading=[gate[0]-b[0],gate[1]-b[1]];}
 return {pos,heading,alt,gear};
}
function drawAviation(g){
 const air=G.airport,r=runwayGeometry();if(!air?.operating||!r)return;
 const terminal=readBuild(air.building);if(!terminal)return;const gate=iso(terminal.x,terminal.y);gate[1]+=64;
 const phase=gameOptions.reducedMotion?88:frameClock%90,pose=aviationPose(r,gate,phase);if(!pose)return;
 const {pos,heading,alt,gear}=pose;
 paintRegionalAircraft(g,...pos,...heading,alt,frameClock,gear);
}
function drawStreetNames(g,sx,sy,ww,hh){
 if(!gameOptions.streetNames||!G.streetNames||cam.zoom<.48)return;
 const zoom=cam.zoom,compact=zoom<.82,minLength=zoom<.64?22:compact?17:12;
 const rank={local:1,collector:2,arterial:3,through:4},streets=new Map();
 for(const [key,name] of Object.entries(G.streetNames)){
  const id=+key;if(!roadSurface(id))continue;
  if(!streets.has(name))streets.set(name,[]);streets.get(name).push(id);
 }
 const candidates=[];
 for(const [name,ids] of streets){
  if(ids.length<minLength)continue;
  const roadRank=ids.reduce((best,id)=>Math.max(best,rank[G.roadClasses?.[id]]||0),0);
  if(compact&&roadRank<2)continue;
  const mid=ids[Math.floor(ids.length*.55)],p=roadCenter(mid);
  if(p[0]<sx-100||p[0]>sx+ww+100||p[1]<sy-100||p[1]>sy+hh+100)continue;
  const a=roadCenter(ids[0]),b=roadCenter(fromEnd(ids));
  candidates.push({name,ids,p,a,b,roadRank});
 }
 candidates.sort((a,b)=>b.roadRank-a.roadRank||b.ids.length-a.ids.length||a.name.localeCompare(b.name));
 const maxLabels=compact?Math.max(4,Math.floor(cw*ch/55000)):Math.max(8,Math.floor(cw*ch/30000));
 const placed=[],screenFont=compact?8:9,fontSize=screenFont/zoom;
 g.font=`bold ${fontSize}px Arial`;g.textAlign='center';
 for(const item of candidates){
  if(placed.length>=maxLabels)break;
  const text=item.name.toUpperCase(),screenX=(item.p[0]-sx)*zoom,screenY=(item.p[1]-sy)*zoom;
  const width=g.measureText(text).width*zoom,height=screenFont+4;
  if(placed.some(box=>Math.abs(box.x-screenX)<(box.width+width)/2+7&&Math.abs(box.y-screenY)<Math.max(box.height,height)+2))continue;
  let angle=Math.atan2(item.b[1]-item.a[1],item.b[0]-item.a[0]);if(angle>Math.PI/2||angle<-Math.PI/2)angle+=Math.PI;
  g.save();g.translate(...item.p);g.rotate(angle);g.font=`bold ${fontSize}px Arial`;g.textAlign='center';g.strokeStyle='#50615a';g.lineWidth=2/zoom;g.strokeText(text,0,-3/zoom);g.fillStyle='#efe8ce';g.fillText(text,0,-3/zoom);g.restore();
  placed.push({x:screenX,y:screenY,width,height});
 }
}
