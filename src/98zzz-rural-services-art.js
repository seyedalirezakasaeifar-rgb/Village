// Institutions and working-land art. These helpers only read authoritative
// service/firm state; they never recruit, enroll, dispatch or settle payments.
function providerVisualState(b){
 if(!b||!['school','fire'].includes(b.kind))return null;
 const independent=!isPublicFacility(b),f=independent?G.firms[b.firm]:null;
 const connected=graph().portals.has(b.id);
 const active=independent?!f.closed&&(f.clientsToday||0)>0&&(b.kind!=='fire'||(f.serviceCapacity||0)>0&&connected):
 b.kind==='school'?connected&&(G.serviceProvision?.school?.paid||0)>0&&(G.serviceProvision?.school?.coverage||0)>0:
 G.policy.defenseBudget>0&&(G.actualServiceFunding?.fire||0)>0&&connected;
 return {independent,closed:!!f?.closed,active,connected,capacity:f?.serviceCapacity||0,clients:f?.clientsToday||0};
}
const providerAppearanceBase=appearanceKey;
appearanceKey=function(b){const role=['school','fire'].includes(b.kind)?isPublicFacility(b)?':municipal':':independent':'';return providerAppearanceBase(b)+role;};
const providerCivicBase=dioramaCivic;
dioramaCivic=function(g,b,w,d){
 providerCivicBase(g,b,w,d);
 const state=providerVisualState(b);if(!state)return;
 const front=d*.36,bw=w*.78,accent=state.independent?'#aa8751':'#648876',ink=state.independent?'#66533a':'#486b5d';
 // Heraldic shield for municipal premises; a paired lamp/monogram for an
 // independent institution. Marks remain recognizable below text-reading zoom.
 const q=point(w*.26,front+.045,24);
 if(state.independent){dioramaSurface(g,w*.24,front+.025,.065,.04,19,9,'#cbb282');g.fillStyle='#f0dfb5';g.fillRect(q[0]-2,q[1]-4,4,5);g.fillStyle=ink;g.fillRect(q[0]-1,q[1]-3,2,2);}
 else polygon(g,[[q[0]-3,q[1]-5],[q[0]+3,q[1]-5],[q[0]+3,q[1]],[q[0],q[1]+3],[q[0]-3,q[1]]],accent);
 const sign=point(0,front+.045,b.kind==='fire'?26:29);g.fillStyle=ink;g.fillRect(sign[0]-15,sign[1]-4,30,6);g.fillStyle='#f1e2bc';g.textAlign='center';g.font='bold 4px Arial';g.fillText(b.kind==='school'?(state.independent?'ACADEMY':'SCHOOL'):(state.independent?'BRIGADE':'FIRE'),sign[0],sign[1]+.5);
 if(state.independent){
  // Brass entrance lanterns and coloured coping are a stable ownership cue,
  // not evidence of paid teaching or response readiness.
  for(const x of [-bw*.31,bw*.31]){const p=point(x,front+.07,12);segment(g,[p[0],p[1]-3],[p[0],p[1]+2],'#605c44');g.fillStyle=state.closed?'#797d69':'#c9b580';g.fillRect(p[0]-2,p[1]-4,4,4);}
 }
 if(state.closed){const p=point(0,front+.08,10);segment(g,[p[0]-6,p[1]-3],[p[0]+6,p[1]+3],'#a58b61',3);segment(g,[p[0]-6,p[1]+3],[p[0]+6,p[1]-3],'#a58b61',2);}
};
function ruralFoundation(g,b,w,d){
 slab(g,-w*.48,-d*.48,w*.96,d*.96,0,b.kind==='quarry'?'#b2ad90':'#9aa078');
 slab(g,-.07,d*.20,.14,d*.28,1,'#c4b591');
}
function dioramaFarm(g,b,w,d){
 const winter=visualMonth()>=10,bw=w*.74,bd=d*.60,u=-bw/2,v=-bd/2,roof=winter?'#d7ddd0':'#795d4b',wall=b.condition<45?'#a68c70':'#bd8c68';
 ruralFoundation(g,b,w,d);
 dioramaSurface(g,u,v,bw*.67,bd,0,30,wall,'timber');
 // Broken-pitch barn roof: steep lower planes and a shallower ridge.
 const mid=v+bd*.50,lo=30,shoulder=43,top=48;
 polygon(g,[point(u-.03,v-.04,lo),point(u+bw*.70,v-.04,lo),point(u+bw*.70,v+bd*.24,shoulder),point(u-.03,v+bd*.24,shoulder)],tone(roof,.74));
 polygon(g,[point(u-.03,v+bd*.24,shoulder),point(u+bw*.70,v+bd*.24,shoulder),point(u+bw*.70,mid,top),point(u-.03,mid,top)],tone(roof,.88));
 polygon(g,[point(u-.03,mid,top),point(u+bw*.70,mid,top),point(u+bw*.70,v+bd*.76,shoulder),point(u-.03,v+bd*.76,shoulder)],roof);
 polygon(g,[point(u-.03,v+bd*.76,shoulder),point(u+bw*.70,v+bd*.76,shoulder),point(u+bw*.70,v+bd+.04,lo),point(u-.03,v+bd+.04,lo)],tone(roof,.93));
 polygon(g,[point(u+bw*.67,v,lo),point(u+bw*.67,v+bd,lo),point(u+bw*.67,v+bd*.76,shoulder),point(u+bw*.67,mid,top),point(u+bw*.67,v+bd*.24,shoulder)],tone(wall,.72));
 for(const yy of [v+bd*.24,mid,v+bd*.76])segment(g,point(u-.03,yy,yy===mid?top:shoulder),point(u+bw*.70,yy,yy===mid?top:shoulder),'#b69d77');
 // Hayloft, paired barn doors and pale bracing are readable at town zoom.
 dioramaWindow(g,u+.08,v+bd+.015,19,'front',bw*.31,7,nightMode&&!G.firms[b.firm]?.closed);
 dioramaSurface(g,u+bw*.12,v+bd+.02,bw*.40,.025,0,16,'#6e5b43');
 for(const sign of [-1,1])segment(g,point(u+bw*.13,v+bd+.055,sign<0?1:15),point(u+bw*.51,v+bd+.055,sign<0?15:1),'#d4bd8a',2);
 const su=u+bw*.78,sv=v+.03;dioramaSurface(g,su,sv,bw*.22,bd*.40,0,41,'#b6b9a1');dioramaHipRoof(g,su-.02,sv-.02,bw*.26,bd*.44,42,8,'#638381');
 for(let z=9;z<40;z+=9)segment(g,point(su,sv+bd*.40,z),point(su+bw*.22,sv+bd*.40,z),'#8b9b87');
 if(gameOptions.decor){
  for(let j=0;j<4;j++)slab(g,u+bw*.72,v+bd*.55+j*.10,bw*.27,.045,1,winter?'#bec8ad':j%2?'#78834f':'#a6a064');
  for(let j=0;j<3;j++){const q=point(u+bw*.74+j*bw*.08,d*.39,0);segment(g,q,[q[0],q[1]-6],'#c8b789',2);}segment(g,point(u+bw*.74,d*.39,4),point(u+bw*.90,d*.39,4),'#b2a174');
 }
}
function dioramaForestry(g,b,w,d){
 ruralFoundation(g,b,w,d);const u=-w*.35,v=-d*.30;
 dioramaSurface(g,u,v,w*.48,d*.55,0,20,'#a99b75','timber');gable(g,u,v,w*.48,d*.55,21,12,visualMonth()>=10?'#d4dccd':'#58796c');
 dioramaWindow(g,u+.05,v+d*.55+.01,7,'front',w*.15,7,nightMode&&!G.firms[b.firm]?.closed);door(g,u+w*.28,v+d*.55+.02,0,.12);
 // Managed timber stacks share a low cradle rather than scattered decorations.
 for(let j=0;j<4;j++){const yy=d*.19+j*.055;slab(g,w*.01,yy,w*.36,.045,2+j%2*2,'#b59c6c');const q=point(w*.37,yy,3+j%2*2);g.fillStyle='#d4bb86';g.fillRect(q[0]-1,q[1]-2,3,3);}
 for(const x of [w*.06,w*.32])segment(g,point(x,d*.19,0),point(x,d*.19,7),'#69775a',2);
 tree(g,w*.29,-d*.31,b.id+1,.34);
}
function dioramaQuarry(g,b,w,d){
 ruralFoundation(g,b,w,d);
 // Exposed benches and a dark pit instead of a single flat grey tile.
 for(let j=0;j<4;j++){const inset=j*.075;slab(g,-w*.40+inset,-d*.39+inset,w*.80-inset*2,d*.78-inset*2,j*.8,['#c0b69a','#a3a48c','#87927f','#647e71'][j]);}
 for(let j=0;j<3;j++)segment(g,point(-w*.36+j*.05,d*.36-j*.05,j+1),point(w*.34-j*.05,d*.36-j*.05,j+1),'#d1c6a5',1.5);
 const u=w*.13,v=-d*.36;dioramaSurface(g,u,v,w*.21,d*.20,0,19,'#a7b3a0');slab(g,u-.02,v-.02,w*.25,d*.24,21,'#6f8679');
 dioramaSurface(g,-w*.25,d*.20,w*.23,d*.12,2,7,'#8f9d85');segment(g,point(-w*.13,d*.24,8),point(w*.16,-d*.15,15),'#c6b98c',3);segment(g,point(-w*.13,d*.24,6),point(w*.16,-d*.15,13),'#6b7f6b',2);
 for(let j=0;j<4;j++){const q=point(-w*.28+j*w*.14,-d*.04,2);polygon(g,[[q[0]-3,q[1]],[q[0]-1,q[1]-5],[q[0]+4,q[1]-3],[q[0]+5,q[1]+1]],j%2?'#b9b398':'#8f9a84');}
}
function dioramaWaterfront(g,b,w,d){
 const cargo=b.kind==='wharf',u=-w*.34,v=-d*.29,wall=cargo?'#b9ad86':'#b7b79a',roof=visualMonth()>=10?'#d2ddd0':cargo?'#4e7f83':'#648b88';
 slab(g,-w*.46,-d*.44,w*.92,d*.88,1,'#b4aa83');
 // Raised timber platform, tide-stained plinth and a steep weather roof.
 dioramaSurface(g,u,v,w*.62,d*.53,1,4,'#748879','timber');dioramaSurface(g,u,v,w*.62,d*.53,5,cargo?23:19,wall,'timber');gable(g,u-.02,v-.02,w*.66,d*.57,cargo?29:25,12,roof);
 for(const yy of [v+.04,v+d*.48])segment(g,point(u+w*.62,yy,1),point(u+w*.62,yy,15),'#52776d',2);
 dioramaWindow(g,u+.05,v+d*.53+.02,14,'front',w*.19,7,nightMode&&!G.firms[b.firm]?.closed);door(g,u+w*.33,v+d*.53+.02,5,.14);
 if(cargo){
  const x=w*.29,y=-d*.26;segment(g,point(x,y,1),point(x,y,48),'#967f53',3);segment(g,point(x,y,46),point(-w*.22,y,46),'#c5ad74',3);segment(g,point(x,y,37),point(-w*.22,y,46),'#687b65');segment(g,point(-w*.19,y,46),point(-w*.19,y,14),'#536b5f');
  for(let j=0;j<3;j++)dioramaSurface(g,-w*.36+j*w*.22,d*.31,w*.16,d*.12,1,5+j%2*2,['#b18c5c','#c6ae76','#899c83'][j],'timber');
 }else{
  // Net-drying rack and an iced catch bench identify the fishery from its shore.
  for(const x of [-w*.32,w*.10])segment(g,point(x,-d*.32,2),point(x,-d*.32,21),'#b8a77b',2);
  for(let j=0;j<5;j++)segment(g,point(-w*.30+j*w*.08,-d*.32,5),point(-w*.30+j*w*.08,-d*.32,19),'#839a87');segment(g,point(-w*.32,-d*.32,20),point(w*.10,-d*.32,20),'#cfbd91');
  dioramaSurface(g,-w*.25,d*.30,w*.42,d*.12,1,5,'#b0bda4');for(let j=0;j<3;j++){const q=point(-w*.17+j*w*.10,d*.35,7);segment(g,[q[0]-2,q[1]],[q[0]+2,q[1]-2],'#d3dccc',1.5);}
 }
}
const ruralArchitectureBase=architecture;
const RURAL_ART_KINDS=new Set(['farm','forestry','quarry','wharf','fishery']);
architecture=function(g,b,w,d){
 if(b.redevelopment||!RURAL_ART_KINDS.has(b.kind)){ruralArchitectureBase(g,b,w,d);return;}
 if(b.kind==='farm')dioramaFarm(g,b,w,d);else if(b.kind==='forestry')dioramaForestry(g,b,w,d);else if(b.kind==='quarry')dioramaQuarry(g,b,w,d);else dioramaWaterfront(g,b,w,d);
};
const ruralParcelBase=parcelDetails,ruralIdentityBase=architecturalIdentity;
parcelDetails=function(g,b,w,d){if(!RURAL_ART_KINDS.has(b.kind))ruralParcelBase(g,b,w,d);};
architecturalIdentity=function(g,b,w,d){if(!RURAL_ART_KINDS.has(b.kind))ruralIdentityBase(g,b,w,d);};
const providerWorkdayBase=workdayScenes,providerWorkdayPaint=paintWorkdayScene;
workdayScenes=function(items){
 if(!visualDetailBudget().people||!gameOptions.decor||gameOptions.quality==='low')return [];
 const cap=fastRenderEnabled()?3:gameOptions.quality==='high'?12:7,ready=[];
 for(const item of items){if(item.b?.kind!=='fire')continue;const state=providerVisualState(item.b);if(!state?.active)continue;const p=point(item.w*.14,item.d*.45);ready.push({kind:'workday',scene:'readiness',b:item.b,f:G.firms[item.b.firm],x:item.x+p[0],y:item.y+p[1],dx:1,dy:.5});if(ready.length>=2)break;}
 const base=providerWorkdayBase(items).filter(a=>{const state=providerVisualState(a.b);return !state||state.active;});
 return [...ready,...base].slice(0,cap);
};
paintWorkdayScene=function(g,a,clock){
 if(a.scene!=='readiness'){providerWorkdayPaint(g,a,clock);return;}
 // A funded crew checks a coiled hose at its own frontage. This is readiness,
 // not an invented incident or a second economic fire-engine dispatch.
 const q={x:a.x-3,y:a.y,dx:1,dy:.5};vehiclePaint(g,{id:a.b.id,style:'pedestrian',color:'#96724e'},q,0);
 g.save();g.translate(a.x+7,a.y-1);g.strokeStyle='#b8a77b';g.lineWidth=2;g.beginPath();g.ellipse(0,0,5,3,.25,0,Math.PI*2);g.stroke();g.strokeStyle='#807b59';g.lineWidth=1;g.beginPath();g.ellipse(0,0,3,1.6,.25,0,Math.PI*2);g.stroke();segment(g,[4,1],[9,3+Math.sin(clock*1.4+a.b.id)*.6],'#b3a06d',2);g.restore();
};
const emissionWindowBase=dioramaWindow;
dioramaWindow=function(g,u,v,z,side,w=.15,h=8,lit=false,shutters=false){
 emissionWindowBase(g,u,v,z,side,w,h,lit,shutters);
 if(lit&&spriteLightRecorder){const a=point(u,v,z+1),b=point(u+(side==='front'?w:0),v+(side==='side'?w:0),z+1);spriteLightRecorder.push([a[0],a[1],b[0]-a[0],b[1]-a[1],h-2]);}
};
const nightEmissionCanvas=document.createElement('canvas');let nightEmissionKey='';
function paintNightScene(g,items){
 g.setTransform(dpr,0,0,dpr,0,0);g.fillStyle='#172c4992';g.fillRect(0,0,cw,ch);transform();
 if(cam.zoom<.32)return;
 let providerStates='';for(const item of items)if(item.b&&['school','fire'].includes(item.b.kind)){const state=providerVisualState(item.b);providerStates+=item.b.id+':'+state.active+';';}
 const key=viewRasterKey+'|'+providerStates;
 if(nightEmissionKey!==key){
  nightEmissionKey=key;
  if(nightEmissionCanvas.width!==cv.width)nightEmissionCanvas.width=cv.width;if(nightEmissionCanvas.height!==cv.height)nightEmissionCanvas.height=cv.height;
  const n=nightEmissionCanvas.getContext('2d');n.setTransform(1,0,0,1,0,0);n.clearRect(0,0,cv.width,cv.height);n.setTransform(dpr,0,0,dpr,0,0);n.translate(cw/2,ch/2);n.scale(cam.zoom,cam.zoom);n.translate(-cam.x,-cam.y);
  for(const item of items){
   const sprite=spriteFor(item),x=Math.round(item.x-sprite.anchorX),y=Math.round(item.y-sprite.anchorY);
   // Remove a rear building's emission wherever an opaque foreground sprite
   // covers it. A light cannot shine through the front neighbour's roof.
   n.globalCompositeOperation='destination-out';n.drawImage(sprite,x,y);n.globalCompositeOperation='source-over';
   const b=item.b;if(!b||b.redevelopment||b.kind==='worksite'||G.firms[b.firm]?.closed)continue;
   const service=providerVisualState(b);if(service&&!service.active)continue;
   const lights=sprite.lightSources||[];if(!lights.length)continue;
   n.save();n.translate(Math.round(item.x),Math.round(item.y));
   n.fillStyle='#ffda91';for(const [px,py,dx,dy,h] of lights)polygon(n,[[px+dx*.18,py+dy*.18],[px+dx*.82,py+dy*.82],[px+dx*.82,py+dy*.82-h],[px+dx*.18,py+dy*.18-h]],'#ffda91');
   // One cached entrance pool per occupied frontage, not a gradient per pane.
   if(cam.zoom>=.5){const p=point(0,item.d*.37,0),glow=n.createRadialGradient(p[0],p[1],1,p[0],p[1],15);glow.addColorStop(0,'#f5bf663b');glow.addColorStop(1,'#e6ad5200');n.fillStyle=glow;n.fillRect(p[0]-15,p[1]-15,30,30);}
   n.restore();
  }
 }
 g.setTransform(1,0,0,1,0,0);g.drawImage(nightEmissionCanvas,0,0);transform();
}
