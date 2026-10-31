// Original second-pass diorama architecture. Buildings are composed as small
// readable masses before surface detail; no textures/assets or economic writes.
const DIORAMA_KINDS=new Set(['home','apartment','tower','office','factory','warehouse','sawmill','grocer','bakery','tavern','townhall','courthouse','school','college','clinic','bank','police','fire','park','square']);
function dioramaSurface(g,u,v,w,d,z,h,c,material='plaster'){
 polygon(g,[point(u+w,v,z),point(u+w,v+d,z),point(u+w,v+d,z+h),point(u+w,v,z+h)],tone(c,.70));
 polygon(g,[point(u,v+d,z),point(u+w,v+d,z),point(u+w,v+d,z+h),point(u,v+d,z+h)],c);
 slab(g,u,v,w,d,z+h,tone(c,1.08));
 segment(g,point(u,v+d,z+h),point(u+w,v+d,z+h),tone(c,1.16));
 segment(g,point(u+w,v,z+h),point(u+w,v+d,z+h),tone(c,.91));
 segment(g,point(u,v+d,z),point(u+w,v+d,z),tone(c,.63),2);
 if(!gameOptions.decor||gameOptions.quality==='low')return;
 if(material==='brick')for(let row=3;row<h;row+=4){
  segment(g,point(u,v+d,z+row),point(u+w,v+d,z+row),tone(c,.88));
  segment(g,point(u+w,v,z+row),point(u+w,v+d,z+row),tone(c,.63));
  for(let col=0;col<w*8;col++){const x=u+(col+(row%8===3?.5:0))/8;if(x>u+w)continue;segment(g,point(x,v+d,z+row),point(x,v+d,z+Math.min(h,row+3)),tone(c,.86));}
 }else if(material==='timber')for(let row=4;row<h;row+=5){segment(g,point(u,v+d,z+row),point(u+w,v+d,z+row),tone(c,.85));segment(g,point(u+w,v,z+row),point(u+w,v+d,z+row),tone(c,.60));}
 else {segment(g,point(u,v+d,z+3),point(u+w,v+d,z+3),tone(c,.90));for(const x of [u+.025,u+w-.025])segment(g,point(x,v+d+.006,z+2),point(x,v+d+.006,z+h-2),tone(c,1.06));}
}
function dioramaWindow(g,u,v,z,side,w=.15,h=8,lit=false,shutters=false){
 const du=side==='front'?w:0,dv=side==='side'?w:0;
 polygon(g,[point(u-.01,v-.01,z-1),point(u+du+.015,v+dv+.015,z-1),point(u+du+.015,v+dv+.015,z+h+1),point(u-.01,v-.01,z+h+1)],'#5b6b61');
 windowPane(g,u,v,z,side,lit,w,h);
 if(shutters)for(const k of [-.035,w+.014]){const q=point(side==='front'?u+k:u,side==='side'?v+k:v,z);segment(g,q,[q[0],q[1]-h],side==='front'?'#5c806d':'#426656',2);}
}
function dioramaHipRoof(g,u,v,w,d,z,rise,c){
 const r1=point(u+w*.24,v+d*.5,z+rise),r2=point(u+w*.76,v+d*.5,z+rise),a=point(u-.04,v-.04,z),b=point(u+w+.04,v-.04,z),f=point(u+w+.04,v+d+.05,z),e=point(u-.04,v+d+.05,z);
 polygon(g,[a,b,r2,r1],tone(c,.78));polygon(g,[e,f,r2,r1],c);polygon(g,[b,f,r2],tone(c,.66));polygon(g,[a,e,r1],tone(c,.91));
 for(let t=.25;t<1;t+=.25){const lerp=(a,b)=>a.map((v,k)=>v+(b[k]-v)*t);segment(g,lerp(r1,e),lerp(r2,f),tone(c,.87));}
 segment(g,r1,r2,tone(c,1.25),1.5);segment(g,e,f,tone(c,.61),1.5);
}
function dioramaFoundation(g,b,w,d){
 const p=neighbourhoodMaterial(b),garden=b.kind==='home'||b.kind==='school'||b.kind==='clinic'||b.kind==='park';
 slab(g,-w*.48,-d*.48,w*.96,d*.96,0,garden?'#8e9a71':'#b4af94');
 // A single connected entrance axis and edge planting frame the building.
 slab(g,-.085,d*.24,.17,d*.25,1,'#d0c4a2');
 if(gameOptions.decor)for(const side of [-1,1]){
  const u=side*w*.39,v=d*.39;slab(g,u-.055,v-.05,.11,.10,1,p[1]);
  const q=point(u,v,6);polygon(g,[[q[0]-4,q[1]],[q[0]-3,q[1]-4],[q[0]+2,q[1]-5],[q[0]+4,q[1]-1],[q[0]+1,q[1]+2]],p[0]);
 }
}
// Hash the atlas variant: founding household IDs have regular six-step runs.
// A plain modulo would accidentally repeat one roofline along whole streets.
function houseStyleId(id){return hash((id%120)*17+13)%6;}
function dioramaHouse(g,b,w,d){
 const id=b.id,form=houseStyleId(id),walls=['#e1cc9f','#c2c9ad','#bc8a6a','#ddd6b9','#c4b89a','#b8c8bf'],roofs=['#985a45','#4c7479','#9b694d','#507468','#a37b4f','#5b718a'];
 const wall=b.condition<45?'#b0a68c':walls[form],roof=visualMonth()>=10?'#d6dcd0':roofs[form],lit=nightMode&&b.hh>=0&&!!G.households[b.hh]?.people.some(id=>!G.people[id]?.deceased&&!G.people[id]?.movedAway);
 const bw=w*(form===5?.79:.76),bd=d*(form===2?.65:.71),u=-bw/2,v=-bd/2,H=[24,30,22,25,31,18][form];
 dioramaFoundation(g,b,w,d);
 dioramaSurface(g,u,v,bw,bd,2,H,wall,form===2?'brick':form===5?'timber':'plaster');
 // Six clearly different rooflines: cross-gable, hip, mansard, porch cottage,
 // narrow town house and low timber bungalow. Palette does not replace shape.
 if(form===1)dioramaHipRoof(g,u,v,bw,bd,H+3,15,roof);
 else if(form===2){slab(g,u-.045,v-.045,bw+.09,bd+.09,H+3,tone(roof,.65));dioramaSurface(g,u+.04,v+.04,bw-.08,bd-.08,H+3,7,roof);dioramaHipRoof(g,u+.03,v+.03,bw-.06,bd-.06,H+11,5,roof);}
 else gable(g,u,v,bw,bd,H+3,form===5?9:14,roof);
 if(form===0){const wingU=u+bw*.54,wingV=v+bd*.40;dioramaSurface(g,wingU,wingV,bw*.42,bd*.61,2,H-4,tone(wall,.96));gable(g,wingU,wingV,bw*.42,bd*.61,H-1,10,roof);dioramaWindow(g,wingU+.035,wingV+bd*.62,8,'front',.15,7,lit);}
 const rows=H>26?2:1;
 for(let row=0;row<rows;row++)for(const t of [.10,.66])dioramaWindow(g,u+bw*t,v+bd+.01,7+row*12,'front',bw*.21,8,lit&&(id+row)%3!==0,true);
 for(const t of [.12,.60])dioramaWindow(g,u+bw+.01,v+bd*t,8,'side',bd*.20,7,lit&&id%3===0);
 door(g,-.065,v+bd+.025,2,.13);slab(g,-.10,v+bd+.02,.22,.12,3,'#d9c9a8');slab(g,-.12,v+bd+.12,.26,.08,1,'#b4ab8c');
 if(form===3||form===5){const z=15;slab(g,-bw*.40,v+bd,bw*.80,.16,z,tone(roof,.89));for(const x of [-bw*.36,bw*.36])segment(g,point(x,v+bd+.13,1),point(x,v+bd+.13,z),'#d6c9a6',2);segment(g,point(-bw*.36,v+bd+.13,6),point(-.10,v+bd+.13,6),'#c4b38c');segment(g,point(.10,v+bd+.13,6),point(bw*.36,v+bd+.13,6),'#c4b38c');}
 if(form===4){dioramaSurface(g,u-.015,v+bd*.55,.23,.25,2,12,tone(wall,.96));dioramaHipRoof(g,u-.025,v+bd*.54,.25,.27,15,5,roof);dioramaWindow(g,u+.005,v+bd*.81,5,'front',.16,6,lit);}
 chimney(g,u+.09,v+.07,H+10);
 if(gameOptions.decor){
  // Boundary treatment is kept below the windows at phone scale.
  for(const side of [-1,1]){const q=point(side*w*.43,d*.22,1);segment(g,q,[q[0],q[1]-5],'#d5c8a6',2);}
  for(let j=0;j<3;j++)slab(g,-w*.39+j*.13,d*.37,.09,.06,1,id%2?'#b4a780':'#c1bd9a');
 }
 if(b.condition<75){const q=point(u+bw*.86,v+bd+.02,5);segment(g,q,[q[0]-1,q[1]-7],'#8e8c745e');}
 if(b.condition<45){const q=point(.0,v+bd+.035,11);segment(g,[q[0]-5,q[1]-3],[q[0]+4,q[1]+3],'#8e7959',2);}
}
function dioramaIndustry(g,b,w,d){
 const f=G.firms[b.firm],closed=!!f?.closed,kind=b.kind,brick=closed?'#9f9b86':kind==='factory'?'#b38c6e':kind==='warehouse'?'#b7b8a1':'#a99b75',roof=visualMonth()>=10?'#d1d9cd':kind==='factory'?'#617b79':kind==='warehouse'?'#697f8b':'#776e54';
 const bw=w*.76,bd=d*.70,u=-bw/2,v=-bd/2;
 dioramaFoundation(g,b,w,d);
 if(kind==='factory'){
  dioramaSurface(g,u,v,bw,bd,0,30,brick,'brick');
  // North-light sawtooth roof: bright vertical glazing and long slate slopes.
  for(let j=0;j<3;j++){const x=u+j*bw/3,ww=bw/3;
   polygon(g,[point(x,v,31),point(x+ww,v,31),point(x+ww,v,43),point(x,v,31)],'#587d7a');
   polygon(g,[point(x,v,31),point(x,v+bd,31),point(x+ww,v+bd,43),point(x+ww,v,43)],roof);
   polygon(g,[point(x+ww,v,31),point(x+ww,v+bd,31),point(x+ww,v+bd,43),point(x+ww,v,43)],'#9bb8aa');
   for(let t=.2;t<1;t+=.2)segment(g,point(x+ww,v+bd*t,32),point(x+ww,v+bd*t,42),'#567a73');
   segment(g,point(x+ww,v,43),point(x+ww,v+bd,43),'#b0bba3',1.2);
  }
  dioramaSurface(g,u+.04,v+.02,.12,.14,28,47,'#967c65','brick');slab(g,u+.02,v,.16,.18,76,'#c8ba99');
 }else if(kind==='warehouse'){
  dioramaSurface(g,u,v,bw,bd,0,30,brick,'brick');gable(g,u,v,bw,bd,31,15,roof);
  // Raised centre clerestory differentiates storage from production at a glance.
  dioramaSurface(g,u+bw*.20,v+bd*.31,bw*.58,bd*.28,40,9,'#899b91');
  for(let j=0;j<4;j++)dioramaWindow(g,u+bw*.24+j*bw*.13,v+bd*.60,41,'front',bw*.09,5,nightMode&&!closed);
  gable(g,u+bw*.18,v+bd*.29,bw*.62,bd*.32,50,4,roof);
 }else{
  dioramaSurface(g,u,v,bw*.64,bd,0,25,brick,'timber');gable(g,u,v,bw*.64,bd,26,12,roof);
  slab(g,u+bw*.63,v,bw*.39,bd,22,roof);
  for(const yy of [v+.04,v+bd-.04])segment(g,point(u+bw*.97,yy,0),point(u+bw*.97,yy,22),'#877955',3);
  for(let j=0;j<4;j++)dioramaSurface(g,u+bw*.70,v+.06+j*bd*.18,bw*.25,bd*.12,1,4+j%2*2,'#bca274','timber');
 }
 for(let j=0;j<3;j++)dioramaWindow(g,u+.06+j*bw*.29,v+bd+.01,18,'front',bw*.18,8,nightMode&&!closed);
 dioramaSurface(g,-bw*.22,v+bd+.018,bw*.42,.025,0,14,'#4a655f');for(let z=3;z<14;z+=3)segment(g,point(-bw*.22,v+bd+.05,z),point(bw*.20,v+bd+.05,z),'#829486');
 slab(g,-bw*.25,v+bd,bw*.48,.17,16,'#a6b29b');segment(g,point(-bw*.25,v+bd+.12,1),point(bw*.23,v+bd+.12,1),'#556c5d',3);
 for(const x of [-bw*.25,bw*.22])dioramaSurface(g,x,v+bd+.11,.035,.04,0,6,'#d7ba6d');
 if(gameOptions.decor){for(let j=0;j<2;j++){const xx=u+bw*.80-j*.16;dioramaSurface(g,xx,v+bd*.78,.12,.11,0,5,'#b69b70','timber');}segment(g,point(u+bw*.03,v+bd*.2,28),point(u+bw*.03,v+bd*.2,9),'#738a7d',2);}
 if(f&&f.scale>=1.4){dioramaSurface(g,u+bw*.55,v+bd*.10,.18,.18,38,7,'#849a89');slab(g,u+bw*.53,v+bd*.08,.22,.22,46,'#b4c1aa');segment(g,point(u+bw*.64,v+bd*.19,38),point(u+bw*.64,v+bd*.19,27),'#6d8477',2);}
 if(closed){const q=point(0,v+bd+.07,9);segment(g,[q[0]-7,q[1]-3],[q[0]+6,q[1]+3],'#a78b5e',3);}
}
function dioramaCivic(g,b,w,d){
 const kind=b.kind,bw=w*.78,bd=d*.72,u=-bw/2,v=-bd/2,school=kind==='school'||kind==='college',fire=kind==='fire',police=kind==='police',clinic=kind==='clinic',grand=['townhall','courthouse','bank'].includes(kind);
 const wall=fire?'#bd856c':police?'#a7bbb6':school?'#cfb995':clinic?'#d8d6b7':'#d8cbae',roof=visualMonth()>=10?'#d4dbce':school?'#607e7b':fire?'#685f54':grand?'#526e73':'#6d8584';
 const lit=nightMode&&!(b.firm>=0&&G.firms[b.firm]?.closed);
 const H=32;dioramaFoundation(g,b,w,d);
 dioramaSurface(g,u,v,bw,bd,1,H,wall,school||fire?'brick':'plaster');
 if(fire){
  // Firehouse is a broad apparatus hall with a hose-drying tower.
  slab(g,u-.03,v-.03,bw+.06,bd+.06,H+3,roof);
  dioramaSurface(g,u+bw*.63,v+.03,bw*.30,bd*.35,H+3,20,tone(wall,.96),'brick');dioramaHipRoof(g,u+bw*.60,v,bw*.36,bd*.41,H+24,7,roof);
  for(const x of [-bw*.38,bw*.04]){dioramaSurface(g,x,v+bd+.02,bw*.33,.025,1,20,'#5e6c61');for(let z=5;z<20;z+=4)segment(g,point(x,v+bd+.05,z),point(x+bw*.33,v+bd+.05,z),'#9a9c82');dioramaWindow(g,x+.025,v+bd+.055,14,'front',bw*.25,4,lit);}
 }else if(grand){
  // Classical civic blocks: strong cornice and a deep columned entrance.
  dioramaHipRoof(g,u-.02,v-.02,bw+.04,bd+.04,H+3,12,roof);
  slab(g,u-.035,v+bd-.01,bw+.07,.12,H,'#eee0bd');
  const porticoW=bw*.54;
  for(const x of [-porticoW*.46,-porticoW*.14,porticoW*.18,porticoW*.46]){dioramaSurface(g,x-.02,v+bd+.06,.045,.07,3,21,'#e6dab9');slab(g,x-.04,v+bd+.04,.085,.11,3,'#c1b390');}
  gable(g,-porticoW*.58,v+bd-.01,porticoW*1.16,.18,27,7,'#c8c3a3');
  for(let j=0;j<3;j++)slab(g,-porticoW*.58-j*.025,v+bd+.13+j*.045,porticoW*1.16+j*.05,.065,3-j,'#cfc4a2');
  if(kind!=='bank'){
   dioramaSurface(g,-.11,-.12,.22,.24,H+8,19,'#d3c7a6');dioramaHipRoof(g,-.14,-.15,.28,.30,H+28,11,roof);
   const q=point(.02,.125,H+19);g.fillStyle='#f0e5c5';g.beginPath();g.arc(q[0],q[1],4,0,Math.PI*2);g.fill();segment(g,q,[q[0],q[1]-3],'#4b665f');segment(g,q,[q[0]+2,q[1]+1],'#4b665f');
  }
 }else if(school){
  gable(g,u,v,bw,bd,H+2,13,roof);
  // Entrance belfry and repeated classroom bays make education recognizable.
  dioramaSurface(g,-.10,-.10,.20,.22,H+9,14,'#d9c9a8');gable(g,-.13,-.13,.26,.28,H+24,7,roof);
  const q=point(.02,.13,H+16);g.fillStyle='#6a6750';g.fillRect(q[0]-3,q[1]-5,6,6);g.fillStyle='#d0ac62';g.fillRect(q[0]-1,q[1]-3,3,4);
  for(const x of [u+.025,u+bw*.47,u+bw-.045])dioramaSurface(g,x,v+bd+.01,.035,.05,1,H-2,'#dbcaa7');
 }else{
  dioramaHipRoof(g,u,v,bw,bd,H+2,13,roof);
  if(clinic){const q=point(bw*.20,v+bd+.035,H-5);g.fillStyle='#9d6755';g.fillRect(q[0]-4,q[1]-1,9,3);g.fillRect(q[0]-1,q[1]-4,3,9);}
 }
 if(!fire){
  for(let row=0;row<2;row++)for(let j=0;j<3;j++){if(grand&&j===1)continue;dioramaWindow(g,u+.045+j*bw*.31,v+bd+.02,6+row*15,'front',bw*.19,8,lit&&(j+row)%3!==0);}
  for(let j=0;j<2;j++)dioramaWindow(g,u+bw+.015,v+.08+j*bd*.46,11,'side',bd*.22,10,lit&&j===0);
  door(g,-.07,v+bd+.035,1,.15);
 }
 if(police){const q=point(u+.02,v+bd+.03,0);segment(g,q,[q[0],q[1]-H-8],'#546b61',1.5);polygon(g,[[q[0]+1,q[1]-H-8],[q[0]+12,q[1]-H-5],[q[0]+10,q[1]-H],[q[0]+1,q[1]-H-3]],'#4a7187');}
 // Restrained face sign; it remains legible as a coloured strip when zoomed out.
 const label={school:'SCHOOL',college:'COLLEGE',fire:'FIRE',police:'POLICE',clinic:'CLINIC',bank:'BANK',townhall:'TOWN HALL',courthouse:'COURT'}[kind],q=point(0,v+bd+.045,fire?26:grand?H+1:29);
 g.fillStyle=police?'#3d6270':fire?'#814d3c':'#657865';g.fillRect(q[0]-14,q[1]-4,28,6);g.fillStyle='#f0e3bc';g.textAlign='center';g.font='bold 4px Arial';g.fillText(label,q[0],q[1]+.5);
}
function dioramaShop(g,b,w,d){
 const kind=b.kind,bw=w*.78,bd=d*.68,u=-bw/2,v=-bd/2,closed=G.firms[b.firm]?.closed,wall=closed?'#aaa68f':kind==='bakery'?'#d6b58e':kind==='tavern'?'#c7b89a':'#d5cdb0',roof=visualMonth()>=10?'#d6dcd0':kind==='bakery'?'#9c6248':kind==='tavern'?'#587a78':'#6a7c63',accent=kind==='bakery'?'#aa6a4c':kind==='tavern'?'#547983':'#5b7d5b';
 dioramaFoundation(g,b,w,d);dioramaSurface(g,u,v,bw,bd,1,29,wall,kind==='tavern'?'timber':'plaster');gable(g,u,v,bw,bd,31,13,roof);
 // Upper dwelling above the shop and deep glass storefront provide an urban
 // silhouette distinct from detached homes and municipal service buildings.
 for(const t of [.12,.65])dioramaWindow(g,u+bw*t,v+bd+.02,20,'front',bw*.20,7,nightMode&&!closed,true);
 dioramaSurface(g,u+.025,v+bd+.025,bw-.05,.025,2,12,closed?'#7a8579':'#678f88');
 for(const t of [.03,.31,.67,.94])segment(g,point(u+bw*t,v+bd+.055,2),point(u+bw*t,v+bd+.055,14),'#d9c8a1',1.5);
 door(g,-.05,v+bd+.06,1,.13);
 const awning=kind==='tavern'?.11:.18;
 for(let j=0;j<7;j++)slab(g,u+j*bw/7,v+bd-.01,bw/7,awning,17,j%2?'#eee1bd':accent);
 segment(g,point(u,v+bd+awning,17),point(u+bw,v+bd+awning,17),tone(accent,.70),2);
 const sign=point(0,v+bd+.04,29);g.fillStyle=tone(accent,.85);g.fillRect(sign[0]-15,sign[1]-4,30,6);g.fillStyle='#f0e2b9';g.textAlign='center';g.font='bold 4px Arial';g.fillText(kind==='grocer'?'GROCER':kind==='bakery'?'BAKERY':'THE VALE',sign[0],sign[1]+1);
 if(kind==='bakery')chimney(g,u+.06,v+.05,40);
 if(gameOptions.decor&&!closed){
  if(kind==='tavern'){for(const xx of [-bw*.28,bw*.30]){const q=point(xx,v+bd+.17,3);g.fillStyle='#9a7c53';g.beginPath();g.ellipse(q[0],q[1],4,2,0,0,Math.PI*2);g.fill();segment(g,[q[0],q[1]],[q[0],q[1]+4],'#5a6e59');}}
  else for(let j=0;j<3;j++){const xx=u+.05+j*bw*.27;dioramaSurface(g,xx,v+bd+.11,bw*.21,.12,0,4,'#a88a59','timber');const q=point(xx+bw*.1,v+bd+.16,5);g.fillStyle=kind==='bakery'?'#e1bf78':['#a9583e','#c6a853','#67904e'][j];g.fillRect(q[0]-3,q[1]-2,6,2);}
 }
}
function dioramaUrban(g,b,w,d){
 const kind=b.kind,bw=w*.78,bd=d*.74,u=-bw/2,v=-bd/2,tower=kind==='tower',office=kind==='office',floors=tower?11:office?5:4,H=floors*12,wall=tower?'#c2c5b0':office?'#c0bdad':'#c8ad8d',roof='#526f73';
 dioramaFoundation(g,b,w,d);dioramaSurface(g,u,v,bw,bd,0,H,wall,office?'plaster':'brick');
 for(let row=0;row<floors;row++){
  if(office){slab(g,u-.018,v+bd-.015,bw+.036,.04,row*12+11,'#b4bda7');}
  for(let j=0;j<4;j++){
   dioramaWindow(g,u+.05+j*bw*.24,v+bd+.015,4+row*12,'front',bw*.16,7,nightMode&&(b.id+j+row)%4!==0);
   dioramaWindow(g,u+bw+.015,v+.06+j*bd*.24,4+row*12,'side',bd*.15,7,nightMode&&(b.id+row)%3===0);
  }
  if(!office&&row>0&&row%2===1){slab(g,u+bw*.14,v+bd+.015,bw*.68,.08,row*12+2,'#a4987b');segment(g,point(u+bw*.14,v+bd+.10,row*12+5),point(u+bw*.82,v+bd+.10,row*12+5),'#6b7e6f');}
 }
 slab(g,u-.035,v-.035,bw+.07,bd+.07,H+2,roof);
 if(tower){dioramaSurface(g,u+bw*.17,v+bd*.17,bw*.66,bd*.62,H+3,12,'#abb6a3');slab(g,u+bw*.15,v+bd*.15,bw*.70,bd*.66,H+16,roof);segment(g,point(0,0,H+16),point(0,0,H+33),'#647f76');}
 else if(office){dioramaSurface(g,u+.08,v+.09,bw*.56,bd*.45,H+3,7,'#91a89c');for(let j=0;j<3;j++)slab(g,u+.13+j*bw*.13,v+.14,bw*.10,bd*.25,H+11,'#a7c3af');}
 else{dioramaHipRoof(g,u,v,bw,bd,H+3,13,roof);chimney(g,u+.08,v+.07,H+9);}
 door(g,-.08,v+bd+.03,1,.17);slab(g,-.14,v+bd,.30,.14,15,roof);
}
function dioramaPark(g,b,w,d){
 dioramaFoundation(g,b,w,d);const square=b.kind==='square';slab(g,-w*.44,-d*.44,w*.88,d*.88,1,square?'#c9c0a5':'#799268');
 slab(g,-.075,-d*.44,.15,d*.88,2,'#d5c8a5');slab(g,-w*.44,-.06,w*.88,.12,2,'#d5c8a5');
 if(square){
  slab(g,-.19,-.19,.38,.38,3,'#a7af9b');slab(g,-.15,-.15,.30,.30,5,'#719d9a');dioramaSurface(g,-.035,-.035,.07,.07,5,12,'#c8c9ae');
  for(const k of [-1,1])segment(g,point(0,0,17),point(k*.10,0,7),'#b2d1ba',1.4);
 }else{tree(g,-w*.23,-d*.20,b.id,.55);tree(g,w*.25,-d*.23,b.id+1,.40);slab(g,-w*.36,d*.20,w*.26,d*.12,2,'#9a9f6a');}
 for(const side of [-1,1]){const u=side*w*.24,v=d*.23;slab(g,u-.13,v,.26,.10,6,'#ab8b60');segment(g,point(u-.13,v,10),point(u+.13,v,10),'#cbb180',2);for(const x of [-.10,.10])segment(g,point(u+x,v+.05,1),point(u+x,v+.05,6),'#526e59');}
}
const dioramaArchitectureBase=architecture;
architecture=function(g,b,w,d){
 if(!DIORAMA_KINDS.has(b.kind)||b.kind==='worksite'||b.redevelopment){dioramaArchitectureBase(g,b,w,d);return;}
 if(b.kind==='home')dioramaHouse(g,b,w,d);
 else if(['factory','warehouse','sawmill'].includes(b.kind))dioramaIndustry(g,b,w,d);
 else if(['grocer','bakery','tavern'].includes(b.kind))dioramaShop(g,b,w,d);
 else if(['apartment','tower','office'].includes(b.kind))dioramaUrban(g,b,w,d);
 else if(['park','square'].includes(b.kind))dioramaPark(g,b,w,d);
 else dioramaCivic(g,b,w,d);
};
// These models include their own doors, docks and landscaping. Preserve the
// older kit for sectors not yet re-authored, without stacking unrelated details.
const dioramaParcelBase=parcelDetails,dioramaIdentityBase=architecturalIdentity;
parcelDetails=function(g,b,w,d){if(!DIORAMA_KINDS.has(b.kind))dioramaParcelBase(g,b,w,d);};
architecturalIdentity=function(g,b,w,d){if(!DIORAMA_KINDS.has(b.kind))dioramaIdentityBase(g,b,w,d);};

function productionVent(item){
 if(item.b.kind==='factory')return point(-item.w*.38+.10,-item.d*.35+.09,78);
 if(item.b.kind==='sawmill')return point(-item.w*.23,-item.d*.10,36);
 if(item.b.kind==='bakery')return point(-item.w*.39+.10,-item.d*.34+.09,53);
 return [-12,-48];
}
// Shadows follow the new massing. Taller rooflines, stepped urban crowns and
// slender factory stacks cast distinct silhouettes using one fixed sun vector.
paintCastShadows=function(g,items){
 if(!gameOptions.effects||nightMode)return;
 for(const item of items){
  if(item.kind==='tree'){g.fillStyle='#304b4225';g.beginPath();g.ellipse(item.x+16,item.y+5,18,6,.25,0,Math.PI*2);g.fill();continue;}
  const b=item.b;if(!b||b.kind==='park'||b.kind==='square'||b.kind==='quarry')continue;
  const kind=b.redevelopment?'worksite':b.kind,H=kind==='home'?[38,45,34,40,46,27][houseStyleId(b.id)]:kind==='tower'?148:kind==='apartment'?64:kind==='office'?70:kind==='factory'?43:kind==='warehouse'?54:kind==='sawmill'?38:['townhall','courthouse'].includes(kind)?69:kind==='school'||kind==='college'?63:kind==='fire'?62:kind==='worksite'?25:44;
  const x=item.x,y=item.y,w=item.w*.72,d=item.d*.68,base=[point(-w*.5,d*.5),point(w*.5,d*.5),point(w*.5,-d*.5)],project=q=>[x+q[0]+H*.67,y+q[1]+H*.24];
  polygon(g,[[x+base[0][0],y+base[0][1]],[x+base[1][0],y+base[1][1]],[x+base[2][0],y+base[2][1]],project(base[2]),project(base[1]),project(base[0])],'#29473d25');
  // Close contact is darker than the long cast shadow, grounding each parcel.
  polygon(g,[[x+base[0][0],y+base[0][1]],[x+base[1][0],y+base[1][1]],[x+base[1][0]+6,y+base[1][1]+2],[x+base[0][0]+6,y+base[0][1]+2]],'#29473d22');
  if(kind==='factory'){const q=point(-item.w*.38+.10,-item.d*.35+.09);polygon(g,[[x+q[0]-2,y+q[1]],[x+q[0]+2,y+q[1]],[x+q[0]+54,y+q[1]+19],[x+q[0]+50,y+q[1]+19]],'#29473d24');}
 }
};
// A small original tree nursery: conifers, upright poplars, broad orchard trees
// and pale-barked crowns. Shared season colours tie gardens to the wider valley.
tree=function(g,u,v,id,scale=1){
 const p=point(u,v),palette=seasonPalette(),form=id%4,seed=hash(id*317+19),winter=visualMonth()>=10;
 g.save();g.translate(...p);g.scale(scale,scale);
 const bark=form===3?'#b6b79a':'#786b4e',shade=form===3?'#707e68':'#564f3d';
 segment(g,[0,3],[1,form===1?-45:-33],shade,4);segment(g,[-1,2],[0,form===1?-43:-32],bark,2);
 const crown=(x,y,rx,ry,color,index)=>{
  polygon(g,[[x-rx,y-ry*.25],[x-rx*.70,y-ry*.75],[x-rx*.2,y-ry],[x+rx*.60,y-ry*.78],[x+rx,y-ry*.15],[x+rx*.82,y+ry*.57],[x+rx*.20,y+ry],[x-rx*.65,y+ry*.65]],color);
  polygon(g,[[x-rx*.92,y-ry*.25],[x-rx*.65,y-ry*.75],[x-rx*.2,y-ry*.96],[x+rx*.55,y-ry*.74],[x+rx*.28,y-ry*.35],[x-rx*.28,y-ry*.17]],tone(color,1.18));
  segment(g,[x-rx*.5,y+ry*.7],[x+rx*.2,y+ry*.9],tone(color,.79),2);
  if(gameOptions.decor&&gameOptions.quality!=='low')for(let j=0;j<7;j++){const h=hash(seed+index*73+j*29),xx=x+(h%Math.max(2,Math.floor(rx*1.3)))-rx*.65,yy=y+(h>>>8)%Math.max(2,Math.floor(ry*1.2))-ry*.65;g.fillStyle=j%3===0?tone(color,1.26):tone(color,.87);g.fillRect(Math.round(xx),Math.round(yy),3,2);}
 };
 if(form===0){
  for(let j=0;j<4;j++){const width=10+j*2,y=-59+j*10;polygon(g,[[0,y],[-width,y+22],[width,y+22]],palette.leaf[j%3]);polygon(g,[[0,y],[-width,y+22],[-2,y+18],[3,y+7]],tone(palette.leaf[j%3],1.17));segment(g,[-width+2,y+22],[width-2,y+22],tone(palette.leaf[j%3],.78));}
 }else if(form===1){
  for(const [x,y,rx,ry] of [[0,-47,8,13],[-4,-33,10,12],[5,-26,10,12],[0,-17,9,9]])crown(x,y,rx,ry,palette.leaf[(Math.abs(y)+id)%3],Math.abs(y));
 }else{
  for(const side of [-1,1]){segment(g,[0,-16],[side*12,-31],shade,2);segment(g,[0,-25],[side*9,-40],bark,1.5);}
  const lobes=form===2?[[-10,-28,13,10],[9,-30,14,11],[-3,-40,14,11],[0,-20,13,9]]:[[-7,-37,11,12],[6,-42,12,12],[-9,-25,11,10],[9,-26,13,11],[0,-18,10,9]];
  for(let j=0;j<lobes.length;j++){const [x,y,rx,ry]=lobes[j];crown(x,y,rx,ry,palette.leaf[j%3],j);}
  if(form===2&&visualMonth()<10)for(let j=0;j<5;j++){const h=hash(seed+j*13);g.fillStyle='#bd7a4a';g.fillRect(h%24-12,-33+(h>>>7)%16,2,2);}
 }
 if(winter)for(let j=0;j<3;j++){g.fillStyle='#e9ede0';g.fillRect(-8+j*5,-39+(j%2)*10,8,2);}
 g.restore();
};
