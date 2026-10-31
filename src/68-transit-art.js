// Original initial transit art. Poses are cosmetic; they cannot deliver passengers or collect fares.
function transitFacilityArt(g,b,w,d){
 if(b.kind==='transit_depot'){
  slab(g,-w/2,-d/2,w,d,0,'#8b9690');box(g,-.78,-.68,1.35,1.05,1,25,'#8daaa9','#c5c7b3');
  for(let i=0;i<3;i++){const u=-.68+i*.41;box(g,u,.38,.30,.025,1,16,'#314b50','#82999a');for(let k=3;k<16;k+=4)segment(g,point(u,.41,k),point(u+.30,.41,k),'#6c8587');}
  box(g,.32,-.65,.42,.90,1,32,'#c3b492','#799ca0');windowPane(g,.36,.27,17,'front',nightMode,.25,9);
  for(let i=0;i<2;i++){box(g,-.60+i*.65,.60,.44,.17,1,7,i?'#dcad66':'#6ebcc0','#e8e1c4');windowPane(g,-.57+i*.65,.78,4,'front',false,.34,3);}
  const p=point(-.12,.44,23);g.fillStyle='#edf0d3';g.font='bold 6px sans-serif';g.fillText('CITY TRANSIT',p[0]-22,p[1]);
 }else{
  slab(g,-.48,-.48,.96,.96,0,'#adb5aa');for(const [u,v] of [[-.31,-.28],[.30,.28]])box(g,u,v,.13,.14,0,28,'#7c9698','#c3cfca');
  slab(g,-.49,-.24,.98,.48,28,'#d0d1b9');box(g,-.47,-.22,.94,.44,29,3,'#a6bebb','#d5dfd2');
  for(let i=0;i<4;i++)segment(g,point(-.40+i*.25,.23,31),point(-.40+i*.25,.23,40),'#5c7d83',1.2);
  slab(g,-.52,-.30,1.04,.60,42,'#65a6b3');slab(g,-.46,-.25,.92,.50,43,'#c6dbd5');
  for(let i=0;i<6;i++)slab(g,.25,.28+i*.032,.20,.034,i*4,'#b9c9c2');
  box(g,-.40,.32,.18,.11,1,16,'#4f8998','#9ac7c4');const p=point(-.36,.45,10);g.fillStyle='#fff2c3';g.font='bold 7px sans-serif';g.fillText('E',p[0],p[1]);
 }
}
function drawTransitInfrastructure(g,visible){
 if(!G.transit&&!transitDraft)return;const state=ensureTransit();g.save();g.lineJoin='round';g.lineCap='round';
 // Guideways are continuous over legal street rights of way. Cull individual supports at regional zoom.
 if(state.tracks.length){const tracks=new Set(state.tracks);for(const id of state.tracks){const [x,y]=roadCenter(id);if(!visible(x,y,70))continue;
  if(cam.zoom>=.38&&id%3===0){segment(g,[x,y+13],[x,y-16],'#607c80',5);segment(g,[x+2,y+12],[x+2,y-15],'#adc4bd',2);}
  for(const next of [id+1,id+T])if(tracks.has(next)&&Math.abs(id%T-next%T)+Math.abs((id/T|0)-(next/T|0))===1){const q=roadCenter(next);segment(g,[x,y-21],[q[0],q[1]-21],'#4e7077',13);segment(g,[x,y-25],[q[0],q[1]-25],'#c2d2c6',11);segment(g,[x,y-28],[q[0],q[1]-28],'#6f969b',3);}
 }}
 if(overlay==='transit'||buildMode==='transit_route'){
  for(const r of transitTopology().routes){g.globalAlpha=r.stats?.operating?.85:.45;g.strokeStyle=r.color;g.lineWidth=r.mode==='bus'?3:4;g.beginPath();let started=false;for(const id of r.path||[]){const p=roadCenter(id);if(!started){g.moveTo(p[0],p[1]-(r.mode==='elevated'?27:0));started=true;}else g.lineTo(p[0],p[1]-(r.mode==='elevated'?27:0));}g.stroke();
   for(const id of r.stopRoads){const p=roadCenter(id);if(!visible(p[0],p[1],30))continue;g.fillStyle=r.color;g.beginPath();g.arc(p[0],p[1]+(r.mode==='elevated'?-27:0),5,0,Math.PI*2);g.fill();g.strokeStyle='#233c41';g.lineWidth=1;g.stroke();}
  }
  if(transitDraft){g.globalAlpha=1;for(let i=0;i<transitDraft.stops.length;i++){const id=transitStopRoad(transitDraft.mode,transitDraft.stops[i]);if(id==null)continue;const p=roadCenter(id);g.fillStyle='#fff0b3';g.beginPath();g.arc(p[0],p[1],10,0,Math.PI*2);g.fill();g.fillStyle='#27484c';g.font='bold 11px sans-serif';g.textAlign='center';g.fillText(String(i+1),p[0],p[1]+4);}}
 }
 g.restore();
}
function drawTransitVehicles(g,visible){for(const pose of transitVehiclePoses()){if(!visible(pose.x,pose.y,60))continue;g.save();g.translate(pose.x,pose.y);g.rotate(Math.atan2(pose.dy,pose.dx));
 const metro=pose.mode==='elevated',wagons=metro?2:1,length=metro?22:24;g.fillStyle='#183c4240';g.fillRect(-length/2+3,3+(metro?18:2),length*wagons,7);
 for(let i=0;i<wagons;i++){const at=i*(length+2)-length*wagons/2;g.fillStyle='#294d54';g.fillRect(at,-6,length,12);g.fillStyle=pose.color;g.fillRect(at+1,-6,length-2,9);g.fillStyle='#e1e7ce';g.fillRect(at+2,-4,length-4,5);g.fillStyle='#406b78';for(let j=0;j<4;j++)g.fillRect(at+3+j*4,-3,3,3);g.fillStyle='#173e48';g.fillRect(at+length-4,-5,3,8);g.fillStyle=nightMode?'#f3d392':'#d6e4d1';g.fillRect(at+length-1,-5,2,2);g.fillRect(at+length-1,3,2,2);}
 g.restore();}}
