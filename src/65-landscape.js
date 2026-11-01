// Original code-native pixel art. One unit = one owned 72 × 36 isometric tile.
// All architectural forms use the same projection, anchor and sunlight direction.
let spriteLightRecorder=null;
let nightMode=false,displayItems=[],buildingItemsById=new Map(),atlas=new Map(),atlasBytes=0,sceneSignature='',lastSceneMonth=0,landscapeRevision=0;
function clearAtlas(){atlas.clear();atlasBytes=0;}
const viewRaster=document.createElement('canvas'),viewBackgroundRaster=document.createElement('canvas'),viewUnderlayRaster=document.createElement('canvas');let viewRasterKey='',viewBackgroundKey='',viewBuildings=[];
const SEASONS=[{grass:['#8f9b69','#929f6d','#96a36f','#9ba773','#9da875'],dark:'#788b58',leaf:['#536c41','#69844a','#809650'],water:'#6b9895'},
 {grass:['#7c994f','#819e52','#86a558','#8aaa5e','#8eaa60'],dark:'#6b7f48',leaf:['#315b3c','#4e7d42','#83a34e'],water:'#4c9297'},
 {grass:['#a4a070','#a7a272','#aba676','#ada877','#b0a97b'],dark:'#8c905d',leaf:['#885e40','#b28144','#ceab5a'],water:'#759593'},
 {grass:['#d4d8cc','#d8dbd0','#dce0d4','#dfe2d9','#e1e4db'],dark:'#c0cdc2',leaf:['#627a6b','#8c9e88','#c9d4c3'],water:'#86a5a6'}];
function seasonPalette(){return SEASONS[Math.floor((visualMonth()-1)/3)%4];}
function visualPick(a){return a[Math.floor(visualRandom()*a.length)];}
function point(u,v,z=0){return [Math.round((u-v)*36),Math.round((u+v)*18-z)];}
function polygon(g,points,color,stroke=null){g.fillStyle=color;g.beginPath();points.forEach((p,i)=>i?g.lineTo(...p):g.moveTo(...p));g.closePath();g.fill();if(stroke){g.strokeStyle=stroke;g.lineWidth=1;g.stroke();}}
function segment(g,a,b,color,width=1){g.strokeStyle=color;g.lineWidth=width;g.beginPath();g.moveTo(...a);g.lineTo(...b);g.stroke();}
function tone(c,m){const rgb=c.slice(1).match(/../g).map(x=>Math.max(0,Math.min(255,Math.round(parseInt(x,16)*m))));return '#'+rgb.map(x=>x.toString(16).padStart(2,'0')).join('');}
function slab(g,u,v,w,d,z,color){polygon(g,[point(u,v,z),point(u+w,v,z),point(u+w,v+d,z),point(u,v+d,z)],color);}
function box(g,u,v,w,d,z,h,c,top){
 polygon(g,[point(u+w,v,z),point(u+w,v+d,z),point(u+w,v+d,z+h),point(u+w,v,z+h)],tone(c,.79));
 polygon(g,[point(u,v+d,z),point(u+w,v+d,z),point(u+w,v+d,z+h),point(u,v+d,z+h)],c);
 if(gameOptions.decor&&gameOptions.quality!=='low'){
  for(const side of ['front','side']){g.save();g.beginPath();const verts=side==='front'?[point(u,v+d,z),point(u+w,v+d,z),point(u+w,v+d,z+h),point(u,v+d,z+h)]:[point(u+w,v,z),point(u+w,v+d,z),point(u+w,v+d,z+h),point(u+w,v,z+h)];verts.forEach((p,i)=>i?g.lineTo(...p):g.moveTo(...p));g.closePath();g.clip();
   for(let row=1;row<h/5;row++){const zz=z+row*5;segment(g,side==='front'?point(u,v+d,zz):point(u+w,v,zz),point(u+w,v+d,zz),tone(c,side==='front'?.94:.73));
    for(let col=0;col<Math.ceil((side==='front'?w:d)*5);col++){let t=(col+(row%2)*.5)/5;if(t>(side==='front'?w:d))continue;segment(g,side==='front'?point(u+t,v+d,zz):point(u+w,v+t,zz),side==='front'?point(u+t,v+d,zz+4):point(u+w,v+t,zz+4),tone(c,side==='front'?.90:.70));}
   }g.restore();
  }
 }
 slab(g,u,v,w,d,z+h,top||tone(c,1.12));
 segment(g,point(u,v+d,z),point(u+w,v+d,z),tone(c,.64));
}
function windowPane(g,u,v,z,side,lit=false,w=.115,h=7){
 const du=side==='front'?w:0,dv=side==='side'?w:0;
 const p=[point(u,v,z),point(u+du,v+dv,z),point(u+du,v+dv,z+h),point(u,v,z+h)];
 polygon(g,p,'#e2d1ac');
 const inset=.018;polygon(g,[point(u+du*.15,v+dv*.15,z+1),point(u+du*.85,v+dv*.85,z+1),point(u+du*.85,v+dv*.85,z+h-1),point(u+du*.15,v+dv*.15,z+h-1)],lit?'#efc676':'#6b8782');
 segment(g,point(u+du*.5,v+dv*.5,z+1),point(u+du*.5,v+dv*.5,z+h-1),'#c7c3aa');
 if(gameOptions.decor){segment(g,point(u-du*.12,v-dv*.12,z-1),point(u+du*1.12,v+dv*1.12,z-1),'#ebe0b8',2);for(const t of [-.25,1.12]){const q=point(u+du*t,v+dv*t,z);g.fillStyle='#49634d';g.fillRect(q[0]-1,q[1]-h,2,h);}}

}
function door(g,u,v,z=0,w=.15){polygon(g,[point(u,v,z),point(u+w,v,z),point(u+w,v,z+13),point(u,v,z+13)],'#574c3d');const p=point(u+w*.8,v,z+6);g.fillStyle='#d5b46e';g.fillRect(p[0],p[1],1,2);}
function gable(g,u,v,w,d,z,rise,color){
 const ridge=v+d/2;
 polygon(g,[point(u-.04,v-.04,z),point(u+w+.04,v-.04,z),point(u+w+.04,ridge,z+rise),point(u-.04,ridge,z+rise)],tone(color,.83));
 polygon(g,[point(u-.04,ridge,z+rise),point(u+w+.04,ridge,z+rise),point(u+w+.04,v+d+.05,z),point(u-.04,v+d+.05,z)],color);
 polygon(g,[point(u+w,v,z),point(u+w,v+d,z),point(u+w,ridge,z+rise)],tone(color,.66));
 for(let t=.2;t<1;t+=.2)segment(g,point(u-.02,ridge+(d/2+.04)*t,z+rise*(1-t)),point(u+w+.04,ridge+(d/2+.04)*t,z+rise*(1-t)),tone(color,.91));
 if(gameOptions.decor&&gameOptions.quality!=='low'){
  for(let row=1;row<6;row++){const t=row/6,yy=ridge+(d/2+.04)*t,zz=z+rise*(1-t);for(let col=0;col<Math.ceil(w*11);col++){const xx=u+col/11+(row%2)/22;if(xx>u+w)continue;segment(g,point(xx,yy,zz),point(xx,yy+(d/2+.04)/6,zz-rise/6),tone(color,col%3?1.09:.84));}}
 }
 segment(g,point(u-.05,ridge,z+rise),point(u+w+.05,ridge,z+rise),tone(color,1.28),1.3);
}
function chimney(g,u,v,z){box(g,u,v,.075,.09,z,11,'#aa856b','#cbb698');}
function tree(g,u,v,id,scale=1){
 const p=point(u,v),s=seasonPalette(),r=hash(id);g.save();g.translate(...p);g.scale(scale,scale);
 polygon(g,[[-2,2],[15,5],[23,1],[6,-2]],'#56654938');
 g.fillStyle='#6a5842';g.fillRect(-2,-18,4,22);g.fillStyle='#8f7655';g.fillRect(-1,-18,1,22);
 if(r%4===0){for(let j=0;j<4;j++){polygon(g,[[0,-53+j*9],[-15+j,-27+j*8],[15-j,-27+j*8]],s.leaf[j%3]);segment(g,[-8+j,-30+j*8],[0,-45+j*9],tone(s.leaf[1],1.12));}}
 else{const crowns=[[-6,-31,12], [5,-36,12],[-10,-23,11],[7,-24,13],[0,-19,11]];for(let k=0;k<crowns.length;k++){let [x,y,n]=crowns[k];polygon(g,[[x-n,y-4],[x-n+4,y-10],[x+2,y-12],[x+n,y-5],[x+n-1,y+4],[x+4,y+9],[x-n+3,y+6]],s.leaf[k%3]);}
  g.fillStyle=tone(s.leaf[2],1.08);for(let i=0;i<13;i++){let n=hash(r+i*713);g.fillRect((n%21)-10,-41+(n>>>9)%21,3,2);}}
 if(gameOptions.decor&&gameOptions.quality!=='low'&&r%4!==0){for(let k=0;k<20;k++){const n=hash(id*319+k*71),x=n%27-14,y=-43+(n>>>7)%23;g.fillStyle=k%4===0?tone(s.leaf[2],1.18):tone(s.leaf[1],1.10);g.fillRect(x,y,3,1);g.fillRect(x+1,y-1,2,1);if(id%7===0&&k%7===0){g.fillStyle='#bc6745';g.fillRect(x,y+3,2,2);}}}
 if(visualMonth()>=10){g.fillStyle='#edf0e6';for(let j=0;j<4;j++)g.fillRect(-10+j*6,-35+(j%2)*5,9,2);}g.restore();
}
function architecture(g,b,w,d){
 if(['transit_depot','elevated_station'].includes(b.kind)){transitFacilityArt(g,b,w,d);return;}
 const id=b.id,kind=b.redevelopment?'worksite':b.kind,v=id%8,winter=visualMonth()>=10,occupied=(b.hh>=0&&G.households[b.hh]?.people.length)||b.units?.some(id=>G.households[id]?.people.length),closed=b.firm>=0&&G.firms[b.firm]?.closed;
 const stone=['#dbca9e','#d4b78b','#c6c6a0','#e4d0aa'],roofs=['#9f553d','#617b78','#aa6d45','#466c59','#bd884a','#627f8e','#886050','#b0774b'];
 const wall=closed?'#9d9a85':kind==='home'?['#dcc596','#b9c7a4','#b77c59','#9fb6b7','#d7c39a','#cbc5a3','#cfae84','#b6bc8e'][id%8]:kind==='police'?'#a3b5ae':kind==='fire'?'#bf7856':stone[id%4],roof=winter?'#c4cfc1':roofs[id%8],lit=nightMode&&!!occupied;
 const bw=w*.73,bd=d*.70,u=-bw/2,vv=-bd/2;
 slab(g,-w/2+.03,-d/2+.03,w-.06,d-.06,0,kind==='farm'?'#a49b71':'#aaad8c');
 // Garden and footpath are contained by the legal parcel, never painted on roads.
 slab(g,-.07,bd/2,.14,Math.max(.04,(d-bd)/2),1,'#bfb69c');
 if(kind==='home'){
  const heights=[22,28,20,32,21,26,19,24],H=heights[id%8];
  const wide=id%8===2?bw*.95:id%8===3?bw*.67:bw*.85,deep=id%8===5?bd*.7:bd*.9;
  const a=-wide/2,c=-deep/2;
  box(g,a,c,wide,deep,1,H,wall);
  if(id%8===3){box(g,a,c,wide,deep,H+1,8,wall);gable(g,a,c,wide,deep,H+9,10,roof);}
  else if(id%8===4){slab(g,a-.04,c-.04,wide+.08,deep+.08,H+2,tone(roof,.8));box(g,a+.05,c+.05,wide-.10,deep-.10,H+2,6,roof);slab(g,a+.04,c+.04,wide-.08,deep-.08,H+9,tone(roof,1.15));}
  else gable(g,a,c,wide,deep,H+1,id%8===2?8:14,roof);
  for(let i=0;i<2;i++){windowPane(g,a+.07+i*wide*.5,c+deep+.01,H>25?16:10,'front',lit||id%11===0,.12,7);windowPane(g,a+wide+.01,c+.07+i*deep*.45,10,'side',lit,.12,7);}
  door(g,-.05,c+deep+.02,1,.12);
  if(gameOptions.decor){
   // Exposed timber, doorstep and ridge details make individual cottages legible.
   if(id%3===0){for(const x of [a+.02,a+wide-.025])segment(g,point(x,c+deep+.025,1),point(x,c+deep+.025,H),'#7a6849',2);segment(g,point(a,c+deep+.025,H-2),point(a+wide,c+deep+.025,H-2),'#7a6849',2);}
   slab(g,-.09,c+deep+.025,.20,.10,2,'#d5c49d');slab(g,-.11,c+deep+.10,.24,.09,1,'#b1a58a');
   if(id%4===0){box(g,a+wide*.55,c+deep*.45,.18,.18,H+6,8,wall);gable(g,a+wide*.55,c+deep*.45,.18,.18,H+14,5,roof);windowPane(g,a+wide*.56,c+deep*.45+.19,H+7,'front',lit,.13,5);}
  }

  if(id%8===1||id%8===5){box(g,a-.07,c+deep-.10,wide*.45,.24,0,12,tone(wall,.96));gable(g,a-.07,c+deep-.10,wide*.45,.24,12,6,roof);windowPane(g,a-.02,c+deep+.15,4,'front',lit,.12,5);}
  if(id%8===6){slab(g,a-.04,c+deep,wide+.08,.13,14,roof);for(const k of [0,.85])segment(g,point(a+k*wide,c+deep+.1,0),point(a+k*wide,c+deep+.1,14),'#927d59',1);}
  if(id%8===7){for(let f=5;f<H;f+=7)segment(g,point(a,c+deep+.01,f),point(a+wide,c+deep+.01,f),'#9c8d72');}
  chimney(g,a+.10,c+.05,H+8);
  if(id%3===0){for(let t=0;t<5;t++){const p=point(-.43+t*.14,.43);g.fillStyle='#d9c9a5';g.fillRect(p[0],p[1]-7,2,7);}segment(g,point(-.43,.43,3),point(.34,.43,3),'#cfbd96');}
  if(id%3===1){for(let j=0;j<5;j++){const p=point(-.40+j*.065,.27);g.fillStyle=['#c2a45f','#bf8072','#d6cba3'][j%3];g.fillRect(p[0],p[1]-2,2,2);}}
  if(id%5===0)tree(g,-.37,-.36,id,.32);
 }else if(kind==='apartment'||kind==='tower'||kind==='office'){
  const floors=kind==='tower'?11:kind==='office'?5:4,H=floors*12;
  box(g,u,vv,bw,bd,0,H,kind==='tower'?'#aaa995':'#bfac91');
  for(let f=0;f<floors;f++){segment(g,point(u,vv+bd,12*f),point(u+bw,vv+bd,12*f),'#9c927e');for(let i=0;i<4;i++){windowPane(g,u+.08+i*bw*.23,vv+bd+.01,4+f*12,'front',nightMode&&(id+i+f)%3!==0,.16,6);windowPane(g,u+bw+.01,vv+.10+i*bd*.22,4+f*12,'side',nightMode&&(id+f)%4===0,.15,6);}}
  slab(g,u-.03,vv-.03,bw+.06,bd+.06,H+2,'#5c716d');box(g,u+.1,vv+.12,bw*.45,bd*.4,H+2,6,'#8a9587');door(g,-.08,vv+bd+.01,0,.16);
 }else if(kind==='farm'){
  box(g,-.6,-.58,.89,.90,0,31,'#a56f52');gable(g,-.6,-.58,.89,.90,31,21,winter?'#d6d9ca':'#665e54');
  polygon(g,[point(-.38,.33,0),point(.04,.33,0),point(.04,.33,22),point(-.38,.33,22)],'#654f3e');
  segment(g,point(-.38,.34,1),point(.04,.34,22),'#c5b18b',2);segment(g,point(.04,.34,1),point(-.38,.34,22),'#c5b18b',2);
  box(g,.34,-.62,.27,.31,0,43,'#b7b5a0','#dfd4b9');gable(g,.34,-.62,.27,.31,43,9,'#7b8276');
  for(let j=0;j<4;j++)slab(g,.32,-.08+j*.18,.40,.07,1,j%2?'#6e8250':'#b5a05d');
  for(let j=0;j<8;j++){const p=point(-.86+j*.23,.87);segment(g,[p[0],p[1]],[p[0],p[1]-7],'#a28c66',2);}segment(g,point(-.86,.87,4),point(.80,.87,4),'#c6b48b');
 }else if(kind==='worksite'||b.redevelopment){
  slab(g,u,vv,bw,bd,0,'#b8a582');
  // Keep the scaffold sprite stable; a live progress bar is drawn separately.
  // Repainting every visible building whenever a worksite crosses a stage was
  // making large towns miss the 50 ms redraw budget.
  const h=18;box(g,u+.05,vv+.05,bw-.1,bd-.1,0,h,'#bba98a');
  for(let i=0;i<4;i++){const x=u+i*bw/3;segment(g,point(x,vv+bd,0),point(x,vv+bd,h+8),'#927d58',2);}segment(g,point(u,vv+bd,h+5),point(u+bw,vv+bd,h+5),'#d8bd83',2);
  segment(g,point(.28,-.15,0),point(.28,-.15,69),'#bf9e5a',2);segment(g,point(-.35,-.15,66),point(.72,-.15,66),'#d1b16a',2);segment(g,point(.61,-.15,66),point(.61,-.15,40),'#5a6250');
 }else if(kind==='park'||kind==='square'){
  slab(g,-.42,-.42,.84,.84,1,kind==='square'?'#c4bba1':'#79925e');
  if(kind==='square'){box(g,-.12,-.12,.24,.24,2,4,'#b2b59e','#82a4a0');box(g,-.025,-.025,.05,.05,7,13,'#c8c7ad');}
  else{tree(g,-.17,-.17,id,.60);slab(g,-.42,.16,.84,.11,1,'#c9bb93');}
  box(g,.14,.29,.28,.08,2,3,'#8a7351');
 }else if(kind==='factory'||kind==='warehouse'||kind==='sawmill'){
  box(g,u,vv,bw,bd,0,30,'#a99d83');
  for(let j=0;j<3;j++)gable(g,u+j*bw/3,vv,bw/3,bd,31,kind==='factory'?13:6,roof);
  for(let i=0;i<4;i++)windowPane(g,u+.08+i*bw*.22,vv+bd+.01,15,'front',nightMode&&!closed,.19,7);
  box(g,u+.06,vv+.03,.13,.15,27,kind==='factory'?49:26,'#8e7e68');
  box(g,u+bw+.06,vv+.30,.26,.27,0,8,'#b39c73');
  door(g,u+bw*.4,vv+bd+.02,0,.25);
 }else if(kind==='metro_station'){
  slab(g,-.84,-.83,1.68,1.66,1,'#b9b49c');box(g,-.63,-.50,1.06,.70,0,23,'#beb79c');gable(g,-.63,-.50,1.06,.70,23,13,roof);
  for(let j=0;j<4;j++)windowPane(g,-.5+j*.24,.21,7,'front',nightMode,.16,9);
  box(g,.49,-.49,.20,.20,0,17,'#5c766e');const p=point(.50,-.48,21);g.fillStyle='#efdfb4';g.font='bold 7px serif';g.fillText('M',p[0],p[1]);
  slab(g,-.54,.40,.8,.28,1,'#65756d');for(let k=0;k<5;k++)segment(g,point(-.54,.40+k*.05,1),point(.26,.40+k*.05,1),'#aaa88f');
 }else if(kind==='airport'){
  box(g,-.72,-.65,1.2,.65,0,20,'#c2baa0');slab(g,-.76,-.69,1.28,.73,22,roof);for(let j=0;j<5;j++)windowPane(g,-.6+j*.2,.01,7,'front',nightMode,.15,9);
  box(g,.5,-.62,.23,.23,0,48,'#aaa894');box(g,.43,-.69,.37,.37,48,10,'#779795');slab(g,.39,-.73,.45,.45,60,'#5f7470');
 }else if(kind==='wharf'||kind==='fishery'){
  box(g,-.34,-.29,.61,.53,1,kind==='wharf'?20:16,'#a99670');gable(g,-.34,-.29,.61,.53,kind==='wharf'?21:17,9,'#648887');door(g,-.08,.25,1,.15);windowPane(g,.28,-.18,8,'side',nightMode,.14,6);
  for(let j=0;j<3;j++){box(g,-.34+j*.20,.30,.15,.12,0,4,'#b79b63');segment(g,point(-.33+j*.20,.31,4),point(-.20+j*.20,.42,4),'#dcc39a');}
  if(kind==='wharf'){segment(g,point(.32,-.25,0),point(.32,-.25,37),'#8d8159',2);segment(g,point(.32,-.25,35),point(-.30,-.25,35),'#c4ad78',2);segment(g,point(-.26,-.25,35),point(-.26,-.25,9),'#535e51');}else{for(let k=0;k<4;k++)segment(g,point(-.30+k*.13,-.30,4),point(-.30+k*.13,-.30,12),'#c7bea0');}
 }else if(kind==='quarry'){
  slab(g,-.38,-.38,.76,.76,1,'#a4aa95');slab(g,-.29,-.29,.58,.58,2,'#8e9685');slab(g,-.17,-.16,.34,.33,3,'#727e73');box(g,.1,-.4,.2,.17,0,14,'#b8ad86');
 }else if(kind==='forestry'){
  box(g,-.24,-.24,.48,.48,0,15,'#a58c65');gable(g,-.24,-.24,.48,.48,15,8,roof);tree(g,-.35,-.34,id,.45);for(let j=0;j<4;j++)box(g,-.37+j*.17,.32,.13,.10,0,4,'#b2a078');
 }else{
  const civic=['townhall','school','clinic','courthouse','college','bank'].includes(kind),H=civic?32:25;
  box(g,u,vv,bw,bd,0,H,kind==='fire'?'#b4836a':wall);gable(g,u,vv,bw,bd,H+1,civic?13:10,roof);
  const rows=civic?2:1;for(let row=0;row<rows;row++)for(let j=0;j<3;j++){windowPane(g,u+.05+j*bw*.30,vv+bd+.01,5+row*15,'front',nightMode&&!closed,.12,7);}
  for(let j=0;j<2;j++)windowPane(g,u+bw+.01,vv+.1+j*bd*.45,12,'side',nightMode&&!closed,.13,7);
  door(g,-.07,vv+bd+.02,0,.14);
  if(kind==='townhall'||kind==='courthouse'){box(g,-.1,-.12,.20,.22,H+4,20,'#c5b799');gable(g,-.1,-.12,.20,.22,H+24,11,'#5d776e');const p=point(.03,.11,H+15);g.fillStyle='#e6d7b1';g.fillRect(p[0]-3,p[1]-3,6,6);segment(g,[p[0],p[1]],[p[0],p[1]-2],'#49584e');}
  if(kind==='grocer'||kind==='bakery'||kind==='tavern'){
   for(let j=0;j<6;j++)slab(g,u+j*bw/6,vv+bd,bw/6,.17,16,j%2?'#e5d8b2':kind==='grocer'?'#637d65':kind==='tavern'?'#9d7751':'#a5725a');
   const p=point(.04,vv+bd+.03,23);g.fillStyle='#544e3e';g.font='5px monospace';g.textAlign='center';g.fillText(kind==='grocer'?'MARKET':kind==='bakery'?'BAKERY':'THE VALE',p[0],p[1]);
   box(g,u-.03,vv+bd+.18,.18,.12,0,7,'#9e8662');
  }
  if(kind==='mill'){chimney(g,u+.04,vv+.05,H+8);box(g,u+bw+.02,vv+.05,.12,.15,5,23,'#8f8b70');}
  if(kind==='fire'){polygon(g,[point(-.2,vv+bd+.01,0),point(.2,vv+bd+.01,0),point(.2,vv+bd+.01,19),point(-.2,vv+bd+.01,19)],'#725749');}
  if(gameOptions.decor&&['school','college','bank','police'].includes(kind)){
   const ink=kind==='police'?'#335c6c':kind==='bank'?'#725937':'#79694a';
   if(kind==='bank'){for(let j=0;j<4;j++){const x=u+.035+j*bw*.29;box(g,x,vv+bd+.01,.045,.075,0,H-2,'#d9cdab');}slab(g,u-.04,vv+bd-.01,bw+.08,.17,H-1,'#e1d4b0');}
   const sign=point(0,vv+bd+.05,H-1);g.fillStyle=ink;g.fillRect(sign[0]-12,sign[1]-4,24,6);g.fillStyle='#eee1bc';g.font='4px monospace';g.textAlign='center';g.fillText(kind==='police'?'POLICE':kind==='bank'?'BANK':kind==='school'?'SCHOOL':'COLLEGE',sign[0],sign[1]+1);
   if(kind==='school'||kind==='college'){box(g,-.08,-.10,.16,.18,H+7,15,'#d6c49d');gable(g,-.10,-.12,.20,.22,H+22,7,roof);const bell=point(.025,.09,H+12);g.fillStyle='#7c6846';g.fillRect(bell[0]-2,bell[1]-5,4,5);g.fillStyle='#cba657';g.fillRect(bell[0]-1,bell[1]-3,2,3);}
   if(kind==='police'){const flag=point(u-.08,vv+bd,0);segment(g,flag,[flag[0],flag[1]-H-4],'#5f6f61');g.fillStyle='#536c84';g.fillRect(flag[0]+1,flag[1]-H-3,7,4);g.fillStyle='#d9bd74';g.fillRect(flag[0]+3,flag[1]-H-2,2,2);}
  }
  if(gameOptions.decor&&kind==='tavern'){const q=point(u-.06,vv+bd+.06,20);segment(g,q,[q[0]-7,q[1]],'#594a37',2);g.fillStyle='#72563c';g.fillRect(q[0]-10,q[1]+1,8,8);g.fillStyle='#e2bf71';g.fillRect(q[0]-8,q[1]+3,3,4);}
  if(gameOptions.decor&&(kind==='grocer'||kind==='bakery')){for(let j=0;j<3;j++){box(g,u+.1+j*.14,vv+bd+.12,.12,.11,0,4,'#ad8652');const q=point(u+.15+j*.14,vv+bd+.16,4);g.fillStyle=kind==='grocer'?['#b65036','#d0ae4b','#5a7c45'][j]:'#dfbd79';g.fillRect(q[0]-3,q[1]-2,6,2);}}
  if(kind==='clinic'){const p=point(0,vv+bd+.03,H-5);g.fillStyle='#a86e55';g.fillRect(p[0]-3,p[1]-1,7,2);g.fillRect(p[0],p[1]-4,2,8);}
 }
 if(gameOptions.decor&&['home','grocer','bakery','tavern','clinic','school'].includes(kind)){
  // Garden border, stone edging, planted beds and a porch rail fit the parcel.
  for(const side of [-1,1]){const u=side*.39;for(let j=0;j<4;j++){const v=-.36+j*.21,q=point(u,v,0);g.fillStyle='#42643d';g.fillRect(q[0]-3,q[1]-4,6,4);g.fillStyle='#7c9848';g.fillRect(q[0]-2,q[1]-5,4,2);if((id+j)%3){g.fillStyle=['#efc575','#ce8270','#d4cae1'][(id+j)%3];g.fillRect(q[0],q[1]-5,2,2);}}}
  if(kind==='home'){for(let j=0;j<7;j++){const x=-.46+j*.15;if(Math.abs(x)<.13)continue;const q=point(x,.46);segment(g,[q[0],q[1]],[q[0],q[1]-6],'#ded1a5',2);}segment(g,point(-.46,.46,3),point(-.15,.46,3),'#ab966e');segment(g,point(.15,.46,3),point(.46,.46,3),'#ab966e');}
 }
 // Visual decline is tied to property condition and business closure.
 if(closed||b.condition<45){for(let j=0;j<5;j++){const p=point((hash(id+j)%50)/100-.25,.34);g.fillStyle='#6c7853';g.fillRect(p[0],p[1]-3,2,4);}const p=point(0,bd/2+.02,10);g.fillStyle='#a5906d';g.fillRect(p[0]-5,p[1],10,3);}
}
function streetProp(g,kind){
 if(kind===0){box(g,-.05,-.05,.10,.10,0,3,'#7a7c61');segment(g,[0,0],[0,-28],'#586c5a',2);g.fillStyle='#4c5f50';g.fillRect(-4,-30,8,2);g.fillStyle=nightMode?'#f7d482':'#d4c9a1';g.fillRect(-3,-28,6,6);g.fillStyle='#5a6a54';g.fillRect(-4,-22,8,2);polygon(g,[[-5,-30],[0,-34],[5,-30]],'#596b55');}
 else if(kind===1){for(const u of [-.21,.14])box(g,u,.01,.04,.10,0,6,'#5a674d');box(g,-.24,-.07,.48,.18,5,2,'#ad8b59');box(g,-.24,-.07,.48,.025,7,6,'#b19362');segment(g,point(-.24,-.07,10),point(.24,-.07,10),'#ddbf83');}
 else{box(g,-.15,-.12,.30,.24,0,6,'#a3926c');for(let j=0;j<7;j++){const q=point((j%3-1)*.1,Math.floor(j/3)*.07-.06,7);g.fillStyle='#527442';g.fillRect(q[0]-2,q[1]-3,4,4);g.fillStyle=['#d98e77','#e3c77a','#c5b7d2'][j%3];g.fillRect(q[0]-1,q[1]-4,3,2);}}
}
function spriteFor(item){
 const season=Math.floor((visualMonth()-1)/3),b=item.b,variant=b?(b.kind==='home'?b.id%120:b.id%24):0;
 // IDs with identical authored massing, paving and night windows share pixels.
 const cacheVariant=b?.kind==='home'&&!b.redevelopment?[houseStyleId(variant),variant%2,nightMode?variant%3:0].join(':'):variant;
 const key=item.kind==='streetprop'?`prop:${item.id%3}:${nightMode}`:item.kind==='tree'?`tree:${season}:${item.id%11}`:`${b.kind}:${cacheVariant}:${item.w}:${item.d}:${season}:${nightMode}:${b.condition<45}:${b.firm>=0&&G.firms[b.firm]?.closed}:${b.redevelopment?'renewal':''}:${appearanceKey(b)}:${parcelForTile(b.x,b.y)?.id||'founding'}`;
 if(atlas.has(key)){const cached=atlas.get(key);atlas.delete(key);atlas.set(key,cached);return cached;}
 // Tight, conservative sprite envelopes avoid uploading acres of transparent
 // pixels whenever a dense viewport changes. Geometry keeps its world anchor.
 const side=item.kind==='building'?Math.ceil((item.w+item.d)*18+20):36,top=item.kind==='building'?(b.kind==='tower'?192:112):72,bottom=item.kind==='building'?Math.ceil((item.w+item.d)*18+24):24;
 const c=document.createElement('canvas');c.width=side*2;c.height=top+bottom;c.anchorX=side;c.anchorY=top;const g=c.getContext('2d');g.translate(c.anchorX,c.anchorY);const previousLights=spriteLightRecorder;spriteLightRecorder=[];
 if(item.kind==='streetprop')streetProp(g,item.id%3);else if(item.kind==='tree')tree(g,0,0,item.id%11,.83);else{polygon(g,[point(-item.w*.4,-item.d*.4),point(item.w*.6,-item.d*.4),point(item.w*.9,item.d*.3),point(0,item.d*.7)],'#48523f30');architecture(g,b.kind==='worksite'||b.redevelopment?b:{...b,id:variant},item.w,item.d);parcelDetails(g,b,item.w,item.d);architecturalIdentity(g,b,item.w,item.d);}
 c.lightSources=spriteLightRecorder;spriteLightRecorder=previousLights;
 atlas.set(key,c);atlasBytes+=c.width*c.height*4;while(atlas.size>600||atlasBytes>48*1024*1024){const oldest=atlas.keys().next().value,retired=atlas.get(oldest);atlasBytes-=retired.width*retired.height*4;atlas.delete(oldest);}return c;
}
function drawSceneSprite(g,item){if(item.kind==='tree'&&cam.zoom<.30){g.fillStyle=seasonPalette().leaf[item.id%3];g.beginPath();g.ellipse(item.x,item.y-18,19,13,0,0,Math.PI*2);g.fill();return;}const sprite=spriteFor(item);g.drawImage(sprite,Math.round(item.x-sprite.anchorX),Math.round(item.y-sprite.anchorY));}
function prepareScene(){
 displayItems=[];const occupied=new Set(G.buildings.flatMap(b=>footprintOf(b)));
 for(let y=0;y<T;y++)for(let x=0;x<T;x++){const id=roadId(x,y);if(G.tiles[id]===3&&!occupied.has(id)&&!G.landUse?.[id]&&hash(id+G.worldSeed)%4!==0){const [px,py]=iso(x,y);displayItems.push({kind:'tree',id,x:px,y:py+18,w:1,d:1});}}
 for(const b of G.buildings){const fp=footprintOf(b),xs=fp.map(id=>id%T),ys=fp.map(id=>id/T|0),w=Math.max(...xs)-Math.min(...xs)+1,d=Math.max(...ys)-Math.min(...ys)+1;const [x,y]=iso(b.x+(w-1)/2,b.y+(d-1)/2);displayItems.push({kind:'building',id:b.id,b,x,y:y+18,w,d});}
 if(gameOptions.decor&&gameOptions.quality!=='low')for(let y=2;y<T-2;y++)for(let x=2;x<T-2;x++){
  const id=roadId(x,y);if(G.tiles[id]!==0||occupied.has(id)||G.landUse?.[id]||hash(id+G.worldSeed)%13!==0)continue;
  if(![roadId(x-1,y),roadId(x+1,y),roadId(x,y-1),roadId(x,y+1)].some(n=>G.tiles[n]===1))continue;
  const [px,py]=iso(x,y);displayItems.push({kind:'streetprop',id,x:px,y:py+18,w:1,d:1});
 }
 displayItems.sort((a,b)=>a.y-b.y||a.id-b.id);buildingItemsById=new Map(displayItems.filter(item=>item.b).map(item=>[item.id,item]));sceneSignature=G.buildings.length+':'+G.month+':'+G.construction;
}
function fastRenderEnabled(){return !!G&&!paused&&speed>=64&&gameOptions.quality!=='high'}
function diamondFast(g,x,y,fill){const p=iso(x,y);g.beginPath();g.moveTo(p[0],p[1]);g.lineTo(p[0]+TW/2,p[1]+TH/2);g.lineTo(p[0],p[1]+TH);g.lineTo(p[0]-TW/2,p[1]+TH/2);g.closePath();g.fillStyle=fill;g.fill()}
let groundBaseTown=null,groundBaseStyle='',groundTileState=null,lastGroundOverview=null;
function drawGround(){
 const fastRender=fastRenderEnabled();
 // Uploading a changed full-world bitmap can stall software Canvas. At 64×,
 // retain a half-resolution ground layer; buildings and labels stay independent.
 groundScale=Math.min(fastRender?.5:1,Math.sqrt((fastRender?2200000:9000000)/(RW*RH)));
 if(cam.zoom<.24&&gameOptions.quality!=='high')groundScale=Math.min(groundScale,dpr*.21);
 const width=Math.round(RW*groundScale),height=Math.round(RH*groundScale),baseStyle=[visualMonth(),width,height,fastRender,gameOptions.decor,gameOptions.quality,JSON.stringify(G.airport?.runway||[])].join('|'),fullTerrain=groundBaseTown!==G||groundBaseStyle!==baseStyle;
 if(bitmap.width!==width||bitmap.height!==height){bitmap.width=width;bitmap.height=height;}
 const s=seasonPalette(),net=graph(),occupied=new Set(G.buildings.flatMap(b=>footprintOf(b))),nextState=new Uint16Array(T*T),chunks=new Map();
 // Retain unchanged terrain even after every deed is owned. Repaint dirty
 // projected chunks under a pixel-aligned clip, replaying the same ordered art.
 const chunkW=256,chunkH=128,chunkStride=Math.ceil(RW/chunkW)+2;
 for(let y=0;y<T;y++)for(let x=0;x<T;x++){
  const id=roadId(x,y),road=G.roadClasses?.[id],state=G.tiles[id]|((G.landUse?.[id]||0)<<3)|(occupied.has(id)?128:0)|(charterOwns(x,y)?256:0)|(road==='arterial'?512:road==='collector'?1024:0);nextState[id]=state;
  if(fullTerrain||groundTileState?.[id]===state)continue;const p=iso(x,y);
  for(let cy=Math.floor((p[1]-24)/chunkH);cy<=Math.floor((p[1]+60)/chunkH);cy++)for(let cx=Math.floor((p[0]-64)/chunkW);cx<=Math.floor((p[0]+64)/chunkW);cx++)chunks.set((cy+1)*chunkStride+cx+1,[cx*chunkW,cy*chunkH]);
 }
 groundTileState=nextState;if(!fullTerrain&&!chunks.size)return;
 const intersects=(x,y)=>{for(let cy=Math.floor((y-24)/chunkH);cy<=Math.floor((y+60)/chunkH);cy++)for(let cx=Math.floor((x-64)/chunkW);cx<=Math.floor((x+64)/chunkW);cx++)if(chunks.has((cy+1)*chunkStride+cx+1))return true;return false;};
 bg.save();if(!fullTerrain){bg.setTransform(1,0,0,1,0,0);bg.beginPath();for(const [x,y] of chunks.values()){const l=Math.floor(x*groundScale),t=Math.floor(y*groundScale),r=Math.ceil((x+chunkW)*groundScale),b=Math.ceil((y+chunkH)*groundScale);bg.rect(l,t,r-l,b-t);}bg.clip();}bg.setTransform(groundScale,0,0,groundScale,0,0);
 bg.fillStyle='#5d7967';bg.fillRect(0,0,RW,RH);groundBaseTown=G;groundBaseStyle=baseStyle;
 const fastGrass=s.grass.map(c=>tone(c,.92));
 for(let y=0;y<T;y++)for(let x=0;x<T;x++){
  const id=roadId(x,y),type=G.tiles[id],h=hash(id+G.worldSeed),p=iso(x,y),lu=G.landUse?.[id];if(!fullTerrain&&!intersects(p[0],p[1]))continue;
  // Unowned outer belts need survey detail, not full urban ground decoration.
  if(!charterOwns(x,y)&&type!==2){diamondFast(bg,x,y,type===3?fastGrass[1]:fastGrass[2]);continue;}
  const tileColor=type===2?s.water:type===1?'#b3b09a':lu===1?(visualMonth()>=10?'#c8cbb5':visualMonth()>=7?'#b4a36d':'#99a06a'):lu===2?'#aa9b7b':lu===3?'#7b827a':s.grass[(Math.floor(Math.sin(x*.18+y*.11)*1.4+Math.cos(y*.22)*.8)+7)%5];
  if(fastRender)diamondFast(bg,x,y,!charterOwns(x,y)&&type!==2?(type===3?fastGrass[1]:fastGrass[2]):tileColor);else diamond(bg,x,y,tileColor);
  if(!fastRender&&!charterOwns(x,y)&&type!==2){polygon(bg,[[p[0],p[1]],[p[0]+36,p[1]+18],[p[0],p[1]+36],[p[0]-36,p[1]+18]],'#a5ac8430');}
  if(!fastRender&&type===2){bg.fillStyle='#b5cdc0';if(h%3===0)bg.fillRect(p[0]-12+(h%17),p[1]+16,9,1);if(x<T-1&&G.tiles[id+1]!==2){segment(bg,[p[0]+35,p[1]+18],[p[0],p[1]+35],'#bdbaa0',3);}}
  else if(!fastRender&&type!==1&&!occupied.has(id)&&!lu){for(let j=0;j<3;j++){let k=hash(h+j*37);bg.fillStyle=j===0?s.dark:tone(s.grass[2],1.04);bg.fillRect(p[0]-15+(k%30),p[1]+9+((k>>>8)%16),2+(k%3),1);}if(h%37===0&&visualMonth()<10){bg.fillStyle=visualMonth()<4?'#e2d5ad':'#c9b486';bg.fillRect(p[0]+5,p[1]+21,2,2);}}
  if(!fastRender&&gameOptions.decor&&gameOptions.quality!=='low'&&type===0&&!occupied.has(id)&&!lu){
   // Sparse wildflowers and small blade clusters, arranged by the town seed.
   if(h%9===0){for(let j=0;j<5;j++){const k=hash(h+j*37),xx=p[0]-12+(k%23),yy=p[1]+12+((k>>>7)%11);bg.fillStyle='#597c40';bg.fillRect(xx,yy,1,4);bg.fillStyle=['#e8d38d','#d2b1be','#bdc8df'][h%3];bg.fillRect(xx-1,yy-1,3,2);}}
   if(h%13===0){for(let j=0;j<4;j++){const xx=p[0]-9+j*5,yy=p[1]+19+j%2;bg.fillStyle='#658344';bg.fillRect(xx,yy,1,3);bg.fillRect(xx+1,yy-1,1,2);}}
  }
  if(!fastRender&&type===2&&gameOptions.decor){if(h%4===0){bg.fillStyle='#87b7ad';bg.fillRect(p[0]-10,p[1]+20,13,1);bg.fillStyle='#477f88';bg.fillRect(p[0]+4,p[1]+15,8,1);}}
  livingTerrain(bg,x,y,type,h);
  if(lu===1){for(let j=-2;j<=2;j++){segment(bg,[p[0]-19+j*4,p[1]+17+j*2],[p[0]+9+j*4,p[1]+31+j*2],visualMonth()>=10?'#acb59b':visualMonth()>=7?'#dbc48a':'#677e4e',2);}}
  if(lu===3){segment(bg,[p[0]-25,p[1]+6],[p[0]+25,p[1]+31],'#aeb6a7',1);segment(bg,[p[0]-20,p[1]+12],[p[0]+20,p[1]+32],'#d7d6bc',1);}
 }
 drawAirfieldGround(bg);
 // Streets have sidewalks and a visible hierarchy, with crossings at junctions.
 for(const [id,links] of net.neighbors){const a=roadCenter(id);for(const n of links){if(n<id)continue;const q=roadCenter(n),kind=G.roadClasses?.[id]||'local',width=kind==='arterial'?32:kind==='collector'?26:20;
  segment(bg,a,q,'#c4bfa6',width+9);if(!fastRender)segment(bg,a,q,'#7e8881',width+3);segment(bg,a,q,'#717d77',width);if(!fastRender&&kind!=='local'){bg.setLineDash([4,8]);segment(bg,a,q,'#d5c99d',1);bg.setLineDash([]);}
 }}
 for(const [id,links] of net.neighbors){if(links.length<3)continue;const a=roadCenter(id);bg.fillStyle='#717d77';bg.beginPath();bg.ellipse(...a,17,9,0,0,Math.PI*2);bg.fill();
  if(!fastRender)for(const n of links){const q=roadCenter(n),dx=q[0]-a[0],dy=q[1]-a[1],l=Math.hypot(dx,dy),ux=dx/l,uy=dy/l,nx=-uy,ny=ux;for(let j=0;j<4;j++){const x=a[0]+ux*(21+j*3),y=a[1]+uy*(21+j*3);segment(bg,[x+nx*6,y+ny*6],[x-nx*6,y-ny*6],'#d4d3b8',1.4);}}
 }
 bg.restore();
}
let groundSignature='',groundRevision=0,groundScale=1;
function drawStatic(){
 const signature=[G.worldSeed,visualMonth(),gameOptions.decor,gameOptions.quality,fastRenderEnabled(),
  G.tiles.join(''),JSON.stringify(G.landUse||{}),JSON.stringify(G.roadClasses||{}),
  JSON.stringify(G.airport?.runway||[]),G.charter?.revision||0,cam.zoom<.24].join('|');
 if(signature!==groundSignature){drawGround();groundSignature=signature;groundRevision++;}
 prepareScene();landscapeRevision++;staticDirty=false;lastSceneMonth=visualMonth();lastGroundOverview=cam.zoom<.24;
}
let fastRenderMode=false;
function fit(){const bounds=cv.getBoundingClientRect(),fast=fastRenderEnabled();if(fast!==fastRenderMode){fastRenderMode=fast;staticDirty=true;viewRasterKey='';viewBackgroundKey='';}dpr=Math.min(window.devicePixelRatio||1,gameOptions.quality==='high'?1.5:gameOptions.quality==='low'?1:1.25)*(fast?0.75:1);cw=Math.max(1,bounds.width);ch=Math.max(1,bounds.height);cv.width=Math.round(cw*dpr);cv.height=Math.round(ch*dpr);dirty=true;}
function transform(){ctx.setTransform(dpr,0,0,dpr,0,0);ctx.translate(cw/2,ch/2);ctx.scale(cam.zoom,cam.zoom);ctx.translate(-cam.x,-cam.y);}
function vehiclePaint(g,v,p,clock){
 if(v.style==='pedestrian'){
  const facing=p.dx>=0?1:-1,phase=clock*7+v.id,swing=Math.sin(phase)*2,x=Math.round(p.x),y=Math.round(p.y),skin=['#d6b38b','#c79570','#9d7358'][v.id%3];
  g.fillStyle='#324c3c40';g.fillRect(x-3,y+1,7,2);g.fillStyle='#394a42';g.fillRect(x-2,y-1+Math.round(swing),2,3);g.fillRect(x+1,y-1-Math.round(swing),2,3);
  g.fillStyle=v.color;g.fillRect(x-2,y-7,5,6);g.fillStyle=tone(v.color,.75);g.fillRect(x+2,y-6,1,5);g.fillStyle=skin;g.fillRect(x-1,y-11,4,4);g.fillRect(x-3,y-5+Math.round(swing*.5),1,4);g.fillRect(x+3,y-5-Math.round(swing*.5),1,4);g.fillStyle='#63523d';g.fillRect(x-1,y-12,4,2);if(p.dy>=0){g.fillStyle='#384d44';g.fillRect(x+(facing>0?2:0),y-9,1,1);}else{g.fillStyle='#63523d';g.fillRect(x-1,y-11,4,3);}return;
 }
 g.save();g.translate(Math.round(p.x),Math.round(p.y));
 const magnitude=Math.hypot(p.dx,p.dy)||1,dx=p.dx/magnitude,dy=p.dy/magnitude;
 // Project a horizontal vehicle plane. Rotating the body, cab and all four wheels
 // together avoids the old fixed-orientation body with a moving headlight.
 g.transform(dx,dy,-dy*1.35,dx*.45,0,0);
 const truck=v.style==='truck',tractor=v.style==='tractor',L=truck?14:tractor?10:11,W=tractor?5:4;
 g.fillStyle='#283c3644';g.fillRect(-L-1,-W+2,L*2+3,W*2+2);
 for(const x of [-L+3,L-4])for(const y of [-W-2,W-1]){g.fillStyle='#2e3834';g.fillRect(x-2,y,5,3);g.fillStyle='#9b9e86';g.fillRect(x,y+1,2,1);}
 g.fillStyle=tone(v.color,.68);g.fillRect(-L,-W,L*2,W*2+2);g.fillStyle=truck?'#bda77b':v.color;g.fillRect(-L,-W-2,L*2,W*2);
 g.fillStyle=tone(v.color,1.23);g.fillRect(-L+1,-W-2,L*2-2,1);
 if(truck){g.fillStyle='#dccca0';g.fillRect(-L,-W-2,L+2,W*2);g.fillStyle='#826b50';for(let j=-L+3;j<0;j+=3)g.fillRect(j,-W-2,1,W*2);}
 const cab=truck?5:0;g.fillStyle='#d1cdb0';g.fillRect(cab-4,-W-3,8,W*2);g.fillStyle='#5d989d';g.fillRect(cab+2,-W-3,3,W*2);g.fillStyle='#436b6c';g.fillRect(cab-4,-W-3,2,W*2);g.fillStyle=tone(v.color,1.1);g.fillRect(cab-1,-W-3,3,W*2);
 g.fillStyle='#ffe5a0';g.fillRect(L-1,-W,2,2);g.fillRect(L-1,W-3,2,2);g.fillStyle='#b94d39';g.fillRect(-L,-W,2,2);g.fillRect(-L,W-3,2,2);
 if(v.emergency){g.fillStyle=Math.floor(clock*5)%2?'#e79950':'#c94d41';g.fillRect(cab,-W-5,3,2);}g.restore();
}
function atmosphere(g,sx,sy,ww,hh){
 if(!gameOptions.effects||gameOptions.reducedMotion)return;
 const active=(weatherEnabled()&&(G.weather==='rain'||G.weather==='storm'))||visualMonth()>=10;
 if(active)for(let j=0;j<70;j++){const h=hash(j+G.worldSeed),x=sx+(h%1000)/1000*ww,y=sy+(((h>>>10)%1000)/1000*hh+frameClock*(visualMonth()>=10?12:120))%hh;g.strokeStyle=visualMonth()>=10?'#f8f7e399':'#dce3cf66';g.lineWidth=1;g.beginPath();g.moveTo(x,y);g.lineTo(x+(visualMonth()>=10?1:4),y+(visualMonth()>=10?1:9));g.stroke();}
 for(const item of viewBuildings){if(item.kind!=='building'||item.x<sx-100||item.x>sx+ww+100||item.y<sy-100||item.y>sy+hh+130)continue;const b=item.b;if(b.firm<0||G.firms[b.firm]?.closed||!workingStaff(G.firms[b.firm]).length||!(G.firms[b.firm]?.production>0)||!['factory','mill','bakery','sawmill'].includes(b.kind))continue;const vent=typeof productionVent==='function'?productionVent(item):[-12,-48];for(let j=0;j<3;j++){const t=(frameClock*.30+j*.40+b.id*.13)%1;g.fillStyle=`rgba(224,221,195,${.30*(1-t)})`;g.fillRect(Math.round(item.x+vent[0]+t*17),Math.round(item.y+vent[1]-t*24),3+Math.floor(t*6),3+Math.floor(t*5));}}
}
function drawConstructionProgress(g,visible){
 for(const project of G.projects){
  const item=buildingItemsById.get(project.id);if(!item||!visible(item.x,item.y,65))continue;
  const duration=Math.max(1,project.duration||30),progress=clamp(1-project.remaining/duration,0,1),x=Math.round(item.x),y=Math.round(item.y-39);
  g.fillStyle='#27372f';g.fillRect(x-15,y-2,30,4);g.fillStyle='#d4b779';g.fillRect(x-14,y-1,Math.round(28*progress),2);
 }
}
function draw(){
 if(!G||!dirty)return;dirty=false;document.body.classList.toggle('surveying-region',overlay==='charter');$('gameRoot').classList.toggle('building-map',!!buildMode);updateRegionSurvey();if(lastGroundOverview!==(cam.zoom<.24))staticDirty=true;if(staticDirty||lastSceneMonth!==visualMonth())drawStatic();
 ctx.setTransform(1,0,0,1,0,0);ctx.fillStyle='#6d8774';ctx.fillRect(0,0,cv.width,cv.height);
 const sx=cam.x-cw/(2*cam.zoom),sy=cam.y-ch/(2*cam.zoom),ww=cw/cam.zoom,hh=ch/cam.zoom;
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.imageSmoothingEnabled=false;transform();ctx.imageSmoothingEnabled=false;
 const visible=(x,y,m=120)=>x>=sx-m&&x<=sx+ww+m&&y>=sy-m&&y<=sy+hh+m;
 // Retain the camera's static composition. Moving actors only redraw intersecting
 // foreground objects, preserving depth without repainting every house each frame.
 let states='';for(const a of displayItems)if(a.b)states+=`${a.b.kind}:${a.b.condition<45}:${a.b.firm>=0&&G.firms[a.b.firm]?.closed}:${a.b.redevelopment?1:0}:${appearanceKey(a.b)};`;
 const backgroundKey=[cam.x,cam.y,cam.zoom,cw,ch,dpr,groundRevision].join('|');
 if(backgroundKey!==viewBackgroundKey){
  if(viewBackgroundRaster.width!==cv.width)viewBackgroundRaster.width=cv.width;if(viewBackgroundRaster.height!==cv.height)viewBackgroundRaster.height=cv.height;
  const bgView=viewBackgroundRaster.getContext('2d',{alpha:false});bgView.imageSmoothingEnabled=false;bgView.setTransform(dpr,0,0,dpr,0,0);bgView.fillStyle='#5d7967';bgView.fillRect(0,0,cw,ch);bgView.drawImage(bitmap,sx*groundScale,sy*groundScale,ww*groundScale,hh*groundScale,0,0,cw,ch);viewBackgroundKey=backgroundKey;
 }
 const key=[cam.x,cam.y,cam.zoom,cw,ch,dpr,nightMode,gameOptions.streetNames,landscapeRevision,states,G.transit?.revision||0].join('|');
 if(key!==viewRasterKey){
  if(viewRaster.width!==cv.width)viewRaster.width=cv.width;if(viewRaster.height!==cv.height)viewRaster.height=cv.height;const vg=viewRaster.getContext('2d',{alpha:false});vg.imageSmoothingEnabled=false;
  // The cached background already has backing-store dimensions. Copy it at
  // identity before applying the logical-pixel transform for world sprites.
  vg.setTransform(1,0,0,1,0,0);vg.drawImage(viewBackgroundRaster,0,0);vg.setTransform(dpr,0,0,dpr,0,0);vg.translate(cw/2,ch/2);vg.scale(cam.zoom,cam.zoom);vg.translate(-cam.x,-cam.y);
  drawStreetNames(vg,sx,sy,ww,hh);
  viewBuildings=displayItems.filter(item=>{
   if(item.kind==='streetprop'&&cam.zoom<.4)return false;
   const building=item.kind==='building',treeItem=item.kind==='tree';
   const xMargin=building?132:treeItem?24:38,topMargin=building?172:treeItem?64:55,bottomMargin=building?84:treeItem?34:28;
   return item.x>=sx-xMargin&&item.x<=sx+ww+xMargin&&item.y>=sy-bottomMargin&&item.y<=sy+hh+topMargin;
  });
  viewBuildings.push(...transitInfrastructureItems(visible));viewBuildings.sort((a,b)=>a.y-b.y);
  paintCastShadows(vg,viewBuildings);
  const actorDetail=!gameOptions.reducedMotion&&((gameOptions.traffic&&cam.zoom>=.32)||(gameOptions.effects&&cam.zoom>=.62));if(actorDetail){if(viewUnderlayRaster.width!==cv.width)viewUnderlayRaster.width=cv.width;if(viewUnderlayRaster.height!==cv.height)viewUnderlayRaster.height=cv.height;const ug=viewUnderlayRaster.getContext('2d',{alpha:false});ug.setTransform(1,0,0,1,0,0);ug.drawImage(viewRaster,0,0);}else{viewUnderlayRaster.width=0;viewUnderlayRaster.height=0;actorRepairRaster.width=0;actorRepairRaster.height=0;}
  for(const item of viewBuildings)drawSceneSprite(vg,item);
  viewRasterKey=key;
 }
 ctx.setTransform(1,0,0,1,0,0);ctx.drawImage(viewRaster,0,0);transform();
 drawWaterLife(ctx,visible);drawWaterfrontPiers(ctx,visible);drawRegionalGates(ctx,visible);drawTransitInfrastructure(ctx,visible);
 const visibleParcels=viewBuildings.filter(item=>visible(item.x,item.y,0)),actors=[...transitArtActors(visible),...neighbourhoodAmbient(visibleParcels),...buildingActivity(visibleParcels),...workdayScenes(visibleParcels),...waterfrontActors(visible),...regionalCargoActors().filter(a=>visible(a.x,a.y,15))];if(visualDetailBudget().traffic)for(const v of traffic){const p=vehiclePosition(v);if(visible(p.x,p.y,15))actors.push({kind:'vehicle',v,...p});}actors.sort((a,b)=>a.y-b.y);

 if(actors.length)paintSceneActors(ctx,actors,visible);
 drawConstructionProgress(ctx,visible);drawInspectedRoute(ctx);drawSelectedWaterRoute(ctx);drawDistrictLife(ctx,visible);drawNamedPlaces(ctx,visible);


 drawCharterBounds(ctx);drawUrbanOverlay(ctx,visible);paintTownLight(ctx);
 if(cam.zoom>=.45)atmosphere(ctx,sx,sy,ww,hh);
 drawAviation(ctx);
 if(overlay==='metro')drawMetroOverlay(ctx);
 if(overlay==='roads'||overlay==='business'||overlay==='hardship'||overlay==='crime'||overlay==='land')for(const item of displayItems){if(item.kind!=='building'||!visible(item.x,item.y))continue;const b=item.b,f=G.firms[b.firm],h=G.households[b.hh],net=graph();let color=overlay==='roads'?(net.portals.has(b.id)?'#9ecb95':'#bb7760'):overlay==='business'?(f?(f.closed?'#b66856':f.profit>0?'#a1c67d':'#d6b46c'):null):overlay==='hardship'?(h?(h.stress>50?'#b96c56':'#a9ca87'):null):overlay==='land'?(b.value>90000?'#c38864':b.value>45000?'#d0b776':'#9fc087'):null;if(!color)continue;ctx.globalAlpha=.7;diamond(ctx,b.x,b.y,color);ctx.globalAlpha=1;}
 drawServiceAccess(ctx);
 if(selected?.id){const b=readBuild(selected.id);if(b){const p=iso(b.x,b.y);ctx.strokeStyle='#f4e2a5';ctx.lineWidth=2;ctx.beginPath();ctx.ellipse(p[0],p[1]+18,32,16,0,0,Math.PI*2);ctx.stroke();}}
 if(buildMode&&buildMode!=='transit_route'&&pointer.hover){const {x,y}=pointer.hover;if(['fishery','wharf'].includes(buildMode))headerText('placementHint',types[buildMode].n+' · '+money(buildCost[buildMode])+' · '+waterfrontPlacementMessage(x,y,buildMode));if(x>=0&&x<T&&y>=0&&y<T){const valid=buildMode==='road_remove'?cityCell(x,y)===1&&charterOwns(x,y):buildMode==='road'?[0,3].includes(cityCell(x,y))&&charterOwns(x,y)&&!buildingAt(x,y)&&!G.landUse?.[roadId(x,y)]&&G.treasury>=buildCost.road:buildMode==='repair'?cityCell(x,y)===1:canPlace(x,y,true,buildMode);ctx.globalAlpha=.60;for(const id of footprintFor(x,y,buildMode))diamond(ctx,id%T,id/T|0,buildMode==='road_remove'?(valid?'#d07757':'#775750'):(valid?'#c8dea4':'#c48069'));ctx.globalAlpha=1;}}
 if(nightMode)paintNightScene(ctx,viewBuildings);
}
