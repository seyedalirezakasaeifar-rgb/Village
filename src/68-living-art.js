// Original illustrated-diorama layer. Static material detail is cached; live
// activity has a strict viewport budget and follows staffed, productive sites.
function livingTerrain(g,x,y,type,h){
 if(!gameOptions.decor||gameOptions.quality==='low'||fastRenderEnabled())return;
 const p=iso(x,y);
 if(type===2){
  // Each shore follows an actual land/water boundary in the isometric grid.
  const edges=[[-1,0,[-36,18],[0,0]],[0,-1,[0,0],[36,18]],[1,0,[36,18],[0,36]],[0,1,[0,36],[-36,18]]];
  for(const [dx,dy,a,b] of edges){const xx=x+dx,yy=y+dy;if(xx<0||yy<0||xx>=T||yy>=T||G.tiles[roadId(xx,yy)]===2||G.tiles[roadId(xx,yy)]===4)continue;
   const from=[p[0]+a[0],p[1]+a[1]],to=[p[0]+b[0],p[1]+b[1]];
   segment(g,from,to,'#b6b895',5);segment(g,from,to,'#d2c6a3',2);
   for(let j=1;j<5;j++){const t=j/5,px=from[0]+(to[0]-from[0])*t,py=from[1]+(to[1]-from[1])*t;g.fillStyle=j%2?'#7e9670':'#a9ac84';g.fillRect(px-2,py-1,4,2);if((h+j)%3===0){segment(g,[px,py],[px-2,py-8],'#537c55');segment(g,[px+2,py],[px+3,py-6],'#7b955c');}}
  }
  if(h%3===0){segment(g,[p[0]-15,p[1]+20],[p[0]+8,p[1]+9],'#9fc0b0',1);segment(g,[p[0]-8,p[1]+25],[p[0]+17,p[1]+13],'#699f9f',1);}
 }else if(type===0&&!G.landUse?.[roadId(x,y)]&&h%5===0){
  // Soft patches avoid a uniform lawn while preserving parcel and road edges.
  polygon(g,[[p[0]-17,p[1]+14],[p[0]-2,p[1]+8],[p[0]+16,p[1]+18],[p[0]+2,p[1]+26]],h%2?'#7c945631':'#b8ba7130');
  for(let j=0;j<4;j++){const px=p[0]-9+j*6,py=p[1]+17+(j%2)*3;segment(g,[px,py],[px+1,py-4],'#718747',1);}
 }
}
function parcelDetails(g,b,w,d){
 if(!gameOptions.decor||gameOptions.quality==='low'||b.kind==='worksite'||b.redevelopment)return;
 const f=G.firms[b.firm],shop=f&&['grocer','bakery','tavern','office'].includes(b.kind),front=point(0,d*.38,0);
 if(shop){
  const color=b.kind==='grocer'?'#5e8462':b.kind==='bakery'?'#b87552':b.kind==='tavern'?'#597c83':'#8b7658';
  const left=point(-w*.24,d*.37,18),right=point(w*.24,d*.37,18);
  polygon(g,[left,right,[right[0],right[1]+6],[left[0],left[1]+6]],color);
  for(let j=0;j<5;j++){const t=(j+.5)/5,px=left[0]+(right[0]-left[0])*t,py=left[1]+(right[1]-left[1])*t;segment(g,[px,py],[px,py+5],'#ecdbb5',2);}
  g.fillStyle='#d3bd8f';g.fillRect(front[0]-4,front[1]-4,8,3);g.fillStyle='#637953';g.fillRect(front[0]-3,front[1]-6,6,3);
 }
 if(f&&!f.closed&&['warehouse','factory','mill','sawmill','contractor'].includes(b.kind)){
  for(let j=0;j<3;j++){const q=point(w*.31-j*.11,d*.30,0);box(g,w*.29-j*.11,d*.30,.09,.10,0,5+j%2*3,j%2?'#ae9063':'#c2a579');segment(g,[q[0]-2,q[1]-4],[q[0]+2,q[1]-2],'#796c50');}
 }
}
function paintTownLight(g){
 if(!gameOptions.effects||nightMode)return;
 // One screen-sized wash: warm sun and cool distance, never per-tile animation.
 const wash=g.createLinearGradient(0,0,cw,ch);wash.addColorStop(0,'#ffe7a516');wash.addColorStop(.5,'#e5edc000');wash.addColorStop(1,'#355d7020');
 g.setTransform(dpr,0,0,dpr,0,0);g.fillStyle=wash;g.fillRect(0,0,cw,ch);transform();
}
function buildingActivity(items){
 const actors=[];
 if(!visualDetailBudget().people)return actors;
 const cap=fastRenderEnabled()?5:gameOptions.quality==='high'?20:12;let count=0;
 for(const item of items){const b=item.b,f=b&&G.firms[b.firm];if(!f||f.closed||!workingStaff(f).length||!(f.production>0||f.revenue>0)||++count>cap)continue;
  const id=f.workers[0],phase=(frameClock*.14+b.id*.173)%1,t=phase<.5?phase*2:(1-phase)*2;
  const door=point(0,item.d*.38,0),road=graph().portals.get(b.id);if(road==null)continue;const target=roadCenter(road),x=item.x+door[0],y=item.y+door[1];
  // A short staff errand remains between the frontage and its connected sidewalk.
  const q={x:x+(target[0]-x)*t*.55,y:y+(target[1]-y)*t*.55,dx:target[0]-x,dy:target[1]-y};
  actors.push({kind:'vehicle',v:{id,style:'pedestrian',color:['#876c51','#536f6e','#8e755b','#687b55'][b.id%4]},...q});
 }
 return actors;
}
function paintCastShadows(g,items){
 if(!gameOptions.effects||nightMode||cam.zoom<.30)return;
 for(const item of items){
  if(item.kind==='tree'){g.fillStyle='#344f4326';g.beginPath();g.ellipse(item.x+15,item.y+5,17,6,.25,0,Math.PI*2);g.fill();continue;}
  if(!item.b)continue;
  const height=item.b.kind==='tower'?95:item.b.kind==='apartment'?65:['home','worksite'].includes(item.b.kind)?30:48,dx=height*.72,dy=height*.25,x=item.x,y=item.y,w=item.w,d=item.d;
  const foot=[[x-17*w,y+3*d],[x+18*w,y+13*d],[x+18*w+dx,y+13*d+dy],[x-17*w+dx,y+3*d+dy]];
  polygon(g,foot,'#304b4530');
  polygon(g,[[x-14*w,y+4*d],[x+14*w,y+11*d],[x+14*w+dx*.7,y+11*d+dy*.7],[x-14*w+dx*.7,y+4*d+dy*.7]],'#304b4514');
 }
}
