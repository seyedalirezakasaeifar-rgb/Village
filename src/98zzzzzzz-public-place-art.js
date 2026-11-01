// Named public places are real properties. This layer reads the bounded place
// API only; neighbourhood observation/fees/trade never run during painting.
let namedPlaceArtIndex=null;
function namedPlaceFor(b){
 if(!b||(b.kind!=='square'&&b.kind!=='warehouse'))return null;
 const state=G.publicPlaces,places=state?.places;
 if(!namedPlaceArtIndex||namedPlaceArtIndex.state!==state||namedPlaceArtIndex.places!==places||namedPlaceArtIndex.count!==(places?.length||0)){
  const entries=new Map();for(const p of publicPlaceCues())entries.set(p.x+','+p.y,p);
  namedPlaceArtIndex={state,places,count:places?.length||0,entries};
 }
 const p=namedPlaceArtIndex.entries.get(b.x+','+b.y);
 return p&&p.kind===b.kind&&readBuild(p.building)?.kind===p.kind?p:null;
}
const placeAppearanceBase=appearanceKey;
appearanceKey=function(b){return placeAppearanceBase(b)+(namedPlaceFor(b)?':named-place':'');};
const namedSquareBase=dioramaPark;
dioramaPark=function(g,b,w,d){
 const place=namedPlaceFor(b);if(!place||b.kind!=='square'){namedSquareBase(g,b,w,d);return;}
 // A civic court, not six invented shops: open circulation, seating, a public
 // notice canopy and a small basin fit entirely inside the actual title.
 slab(g,-w*.47,-d*.47,w*.94,d*.94,1,'#c5bea0');
 for(let j=-3;j<=3;j++){const x=j*w*.12;segment(g,point(x,-d*.43,2),point(x,d*.43,2),'#b0ad91');}
 for(let j=-2;j<=2;j++){const y=j*d*.16;segment(g,point(-w*.43,y,2),point(w*.43,y,2),'#d8ceb0');}
 slab(g,-w*.13,-d*.13,w*.26,d*.26,3,'#9cae9a');slab(g,-w*.10,-d*.10,w*.20,d*.20,5,'#719e98');
 dioramaSurface(g,-.025,-.025,.05,.05,5,9,'#ccd1b1');for(const side of [-1,1])segment(g,point(0,0,14),point(side*.07,0,7),'#b9d9c0',1.3);
 for(const side of [-1,1]){const x=side*w*.27,y=d*.29;slab(g,x-.10,y,.20,.07,5,'#aa8e62');segment(g,point(x-.10,y,9),point(x+.10,y,9),'#c7ad7b',2);for(const leg of [-.07,.07])segment(g,point(x+leg,y+.04,1),point(x+leg,y+.04,5),'#61765e');}
 // The notice kiosk is municipal furniture, not a new vendor or enterprise.
 dioramaSurface(g,-w*.35,-d*.35,w*.21,.035,2,11,'#aa9b72');slab(g,-w*.39,-d*.38,w*.29,d*.15,15,'#628379');
 const q=point(-w*.25,-d*.30,9);g.fillStyle='#e4d7b3';g.fillRect(q[0]-3,q[1]-4,6,5);g.fillStyle='#79917a';g.fillRect(q[0]-2,q[1]-3,4,1);
 for(const x of [-w*.35,w*.35]){slab(g,x-.045,-d*.02,.09,.12,2,'#b7ab87');const q=point(x,d*.02,5);g.fillStyle='#789368';g.beginPath();g.ellipse(q[0],q[1],3,2,0,0,Math.PI*2);g.fill();}
 for(const side of [-1,1]){const q=point(side*w*.36,side*d*.16,10);segment(g,[q[0],q[1]+9],[q[0],q[1]-2],'#627c64',1.5);g.fillStyle=nightMode?'#f1d08b':'#b6b59a';g.fillRect(q[0]-2,q[1]-4,4,4);if(nightMode&&spriteLightRecorder)spriteLightRecorder.push([q[0]-2,q[1],4,0,4]);}
};
const loadingCourtIdentityBase=architecturalIdentity;
architecturalIdentity=function(g,b,w,d){
 loadingCourtIdentityBase(g,b,w,d);if(b.kind!=='warehouse'||!namedPlaceFor(b))return;
 // Receiving apron and a dispatch notice distinguish working land from the
 // open paved square without inventing parked freight or extra throughput.
 const y=d*.40;for(const x of [-w*.27,w*.23])segment(g,point(x,y-.08,1),point(x,y+.04,1),'#d6bf7f',1.5);
 const q=point(w*.31,d*.33,12);segment(g,[q[0],q[1]+9],[q[0],q[1]-1],'#69816a',1.5);g.fillStyle='#ccb782';g.fillRect(q[0]-4,q[1]-4,8,5);g.fillStyle='#56766a';g.fillRect(q[0]-3,q[1]-3,6,1);
};
function drawNamedPlaces(g,visible){
 if(!gameOptions.streetNames||!gameOptions.decor||cam.zoom<.5||cam.zoom>1.55)return;
 const z=cam.zoom,placed=[];g.save();
 for(const p of publicPlaceCues()){
  if(!p.present||placed.length>=3)continue;const b=readBuild(p.building);if(!b)continue;const q=iso(b.x,b.y),item=buildingItemsById.get(b.id),x=item?item.x:q[0],y=item?item.y+(item.w+item.d)*9+5:q[1]+41;if(!visible(x,y,0))continue;
  const chars=Array.from(p.name),text=chars.length>25?chars.slice(0,24).join('')+'…':p.name,gap=7/z;g.font='bold '+(8/z)+'px Arial';const width=Math.min(150/z,g.measureText(text).width+10/z);
  if(placed.some(r=>Math.abs(r.x-x)<(r.width+width)/2+gap&&Math.abs(r.y-y)<22/z))continue;
  g.fillStyle=p.kind==='square'?'#3f6558ed':'#5c6553ed';g.fillRect(x-width/2,y-8/z,width,12/z);g.fillStyle='#f0e1b8';g.textAlign='center';g.fillText(text,x,y+1/z,width-6/z);placed.push({x,y,width});
 }g.restore();
}
const placeAmbientBase=neighbourhoodAmbient;
neighbourhoodAmbient=function(items){
 if(!visualDetailBudget().people||!gameOptions.decor||gameOptions.quality==='low')return [];
 const base=placeAmbientBase(items),cap=gameOptions.quality==='high'?7:4;
 if(!G.stats.population)return base;
 for(const item of items){const b=item.b;if(b?.kind!=='square'||!namedPlaceFor(b))continue;
  // One decorative public-space stroll replaces a generic ambient sample. It
  // does not claim an observed visit or a shopper/purchase from nearby firms.
  const angle=frameClock*.20+b.id,p=point(Math.cos(angle)*item.w*.24,Math.sin(angle)*item.d*.24),dx=(-Math.sin(angle)*item.w-Math.cos(angle)*item.d)*36,dy=(-Math.sin(angle)*item.w+Math.cos(angle)*item.d)*18;
  return [{kind:'vehicle',v:{id:910000+b.id,style:'pedestrian',color:'#9a8766',ambient:true},x:item.x+p[0],y:item.y+p[1],dx,dy},...base.filter(a=>a.v.id!==900000+b.id)].slice(0,cap);
 }return base;
};
