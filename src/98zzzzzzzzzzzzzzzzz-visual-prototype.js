// Isolated art-direction prototype. Enable with ?cityArt=prototype; simulation
// and picking retain the same parcels and isometric projection.
if(new URLSearchParams(location.search).get('cityArt')==='prototype'||window.CITY_REDESIGN){
 window.CITY_REDESIGN=true;
 document.documentElement.classList.add('city-art-prototype');
 const priorArchitecture=architecture;
 const kit=new Set(['home','apartment','office','grocer','bakery','tavern','factory','warehouse','townhall','school','fire']);
 architecture=function(g,b,w,d){
  if(!kit.has(b.kind)||b.redevelopment){priorArchitecture(g,b,w,d);return;}
  const residential=b.kind==='home',urban=['apartment','office'].includes(b.kind),industry=['factory','warehouse'].includes(b.kind),id=b.id||0;
  const bw=w*(residential?.92:.82),bd=d*(residential?.83:.74),u=-bw/2,v=-bd/2;
  const masonry=['#c7b79c','#bba58d','#dfd4bd','#a99a86'][id%4],roof=['#343e48','#50504a','#694b3e'][id%3];
  // Broad quiet material planes replace the tiny pastel cottage vocabulary.
  slab(g,-w*.48,-d*.48,w*.96,d*.96,1,'#8c9182');
  slab(g,u-.08,v-.08,bw+.16,bd+.16,3,'#555a50');
  const floors=urban?3+(id%3):industry?1:residential?2:2,H=industry?38:residential?(id%3===0?37:27):floors*20;
  box(g,u,v,bw,bd,4,H,masonry,'#b9b6a6');
  // Deep cornices, inset glazing and structural bays keep facades legible.
  for(let f=0;f<floors;f++){
   if(residential&&f>0&&H<35)continue;const z=residential?8+f*17:10+f*20,columns=residential?2:3;
   for(let j=0;j<columns;j++){
    const x=u+.09+j*(bw-.15)/columns,ww=(bw-.22)/columns;
    polygon(g,[point(x,v+bd+.008,z),point(x+ww,v+bd+.008,z),point(x+ww,v+bd+.008,z+12),point(x,v+bd+.008,z+12)],'#3a3e39');
    polygon(g,[point(x+.025,v+bd+.015,z+2),point(x+ww-.025,v+bd+.015,z+2),point(x+ww-.025,v+bd+.015,z+11),point(x+.025,v+bd+.015,z+11)],nightMode?'#f5c47d':'#47636c');
    segment(g,point(x,v+bd+.04,z),point(x+ww,v+bd+.04,z),'#dfcfac',2);
    const y=v+.10+j*(bd-.15)/columns;
    polygon(g,[point(u+bw+.01,y,z),point(u+bw+.01,y+ww,z),point(u+bw+.01,y+ww,z+11),point(u+bw+.01,y,z+11)],nightMode?'#cd9c5e':'#314952');
   }
   if(urban)slab(g,u-.035,v-.035,bw+.07,bd+.07,z+15,'#746f63');
  }
  if(residential){
   if(id%3===0)gable(g,u-.03,v-.04,bw+.06,bd+.08,H+5,17,roof);else if(id%3===1){slab(g,u-.05,v-.05,bw+.10,bd+.10,H+7,roof);box(g,u+.08,v+.08,bw*.4,bd*.35,H+8,4,'#797e72');}else dioramaHipRoof(g,u-.04,v-.04,bw+.08,bd+.08,H+5,14,roof);
   box(g,u+bw*.12,v+bd*.17,.11,.12,H+10,20,'#7d6d5b');
   // A deep covered entry and broad steps give houses a grounded human scale.
   box(g,-.12,v+bd+.01,.25,.15,3,18,'#77786b');slab(g,-.18,v+bd+.01,.36,.23,24,roof);
   for(let j=0;j<3;j++)slab(g,-.17,v+bd+.16+j*.055,.34,.06,6-j*2,'#b1ac95');
  }else if(['townhall','school','fire'].includes(b.kind)){
   slab(g,u-.08,v-.08,bw+.16,bd+.16,H+7,roof);
   if(b.kind==='townhall'){box(g,-.17,-.14,.34,.28,H+8,27,'#c4baa3');gable(g,-.19,-.16,.38,.32,H+35,13,roof);const p=point(.17,.15,H+23);g.fillStyle='#eadcbc';g.beginPath();g.arc(p[0],p[1],5,0,Math.PI*2);g.fill();segment(g,[p[0],p[1]],[p[0],p[1]-3],'#33474a');}
   else if(b.kind==='school'){gable(g,u-.04,v-.04,bw+.08,bd+.08,H+8,16,roof);box(g,u+bw*.72,v+.10,.15,.16,H+9,20,'#806752');}
   else{for(let j=0;j<2;j++)box(g,u+.08+j*bw*.46,v+bd+.02,bw*.35,.02,4,20,'#53615b');box(g,u+bw*.73,v+.1,.21,.28,H+6,23,'#a29178');}
  }else if(industry){
   for(let j=0;j<3;j++)gable(g,u+j*bw/3,v,bw/3,bd,H+5,12,roof);
   for(let j=0;j<2;j++)box(g,u+.08+j*bw*.46,v+bd+.01,bw*.34,.03,3,23,'#424b48');
   box(g,u+bw*.77,v+.12,.12,.14,H+5,22,'#716b5e');
  }else if(urban){
   slab(g,u-.06,v-.06,bw+.12,bd+.12,H+7,roof);box(g,u+.12,v+.12,bw*.55,bd*.50,H+8,9,'#878c80');
  }else{
   slab(g,u-.055,v-.055,bw+.11,bd+.11,H+7,roof);
   const awning=b.kind==='bakery'?'#934e38':b.kind==='grocer'?'#385d50':'#5b4d60';
   slab(g,u-.03,v+bd+.015,bw+.06,.23,22,awning);segment(g,point(u-.03,v+bd+.245,22),point(u+bw+.03,v+bd+.245,22),'#e2caa0',3);
   box(g,u+.10,v+bd+.02,bw*.76,.02,4,15,'#263f46');
  }
  // Contact line belongs to the legal footprint; no invented extension lots.
  segment(g,point(u,v+bd,3),point(u+bw,v+bd,3),'#303f3580',3);
 };
 const prototypeTreeBase=tree;
 tree=function(g,u,v,id,scale=1){
  const p=point(u,v);g.save();g.translate(...p);g.scale(scale,scale);
  g.fillStyle='#233e342b';g.beginPath();g.ellipse(10,5,24,8,.25,0,Math.PI*2);g.fill();
  segment(g,[0,3],[1,-36],'#5c5141',4);segment(g,[1,-17],[-9,-31],'#5c5141',2);
  const evergreen=id%4===0;
  if(evergreen){for(let j=0;j<3;j++)polygon(g,[[-19+j*3,-13-j*13],[0,-46-j*8],[19-j*3,-13-j*13]],['#315449','#3d6150','#507354'][j]);}
  else for(const [x,y,r] of [[-10,-30,16],[11,-31,17],[0,-45,18]]){g.fillStyle='#345a45';g.beginPath();g.ellipse(x+2,y+4,r,r*.79,0,0,Math.PI*2);g.fill();g.fillStyle=['#5d7c50','#6f8956','#80965e'][id%3];g.beginPath();g.ellipse(x-2,y-2,r*.88,r*.70,0,0,Math.PI*2);g.fill();}
  g.restore();
 };
 const tileBase=diamond;
 diamond=function(g,x,y,fill,stroke){tileBase(g,x,y,fill,stroke);if(!stroke){g.strokeStyle=fill;g.lineWidth=2.4;g.stroke();}};
 const oldPalette=seasonPalette;
 seasonPalette=function(){const p=oldPalette();return {...p,grass:['#7b886e','#7b886e','#7b886e','#7b886e','#7b886e'],water:'#467d86',dark:'#60765b'};};
 const style=document.createElement('style');style.textContent='.city-art-prototype #mapStatusDeck{width:220px;opacity:.94}.city-art-prototype .topbar{box-shadow:0 2px 12px #132d3030}.city-art-prototype #tabs button{font-family:Arial,sans-serif;font-weight:500}';document.head.appendChild(style);
 if(typeof bridgePaint==='function')bridgePaint=function(g,item){
  const a=item.first,b=item.last,n=item.bridge.cells.length+1,dx=(b[0]-a[0])/n,dy=(b[1]-a[1])/n,L=Math.hypot(dx,dy),nx=-dy/L*14,ny=dx/L*14;
  const start=[a[0]+dx*.65,a[1]+dy*.65-17],end=[b[0]-dx*.65,b[1]-dy*.65-17];
  const ribbon=(p,q,z,c)=>polygon(g,[[p[0]+nx,p[1]+ny+z],[q[0]+nx,q[1]+ny+z],[q[0]-nx,q[1]-ny+z],[p[0]-nx,p[1]-ny+z]],c);
  // Abutments sit at the real water/land interfaces, below both road ramps.
  for(const [p,sign] of [[a,1],[b,-1]]){const x=p[0]+dx*.48*sign,y=p[1]+dy*.48*sign;polygon(g,[[x+nx,y+ny],[x-nx,y-ny],[x-nx,y-ny-18],[x+nx,y+ny-18]],'#746f5e');segment(g,[x+nx,y+ny-18],[x-nx,y-ny-18],'#c0b79b',4);}
  for(let i=1;i<n-1;i+=2){const p=[a[0]+dx*(i+.5),a[1]+dy*(i+.5)];polygon(g,[[p[0]-7,p[1]+3],[p[0]+7,p[1]+3],[p[0]+6,p[1]-16],[p[0]-6,p[1]-16]],'#6f7568');segment(g,[p[0]-5,p[1]-15],[p[0]+5,p[1]-15],'#b4b299',3);}
  ribbon(start,end,7,'#4b554d');ribbon(start,end,0,'#b0ac94');
  for(const [p,q] of [[a,start],[end,b]]){ribbon(p,q,4,'#737565');ribbon(p,q,0,'#aaa58c');segment(g,p,q,'#56635d',22);}
  segment(g,start,end,item.closed?'#666354':'#4f5b56',23);
  if(!item.closed){g.setLineDash([9,11]);segment(g,start,end,'#d6c99c',1.2);g.setLineDash([]);}
  for(const side of [-1,1]){const p=[start[0]+nx*side,start[1]+ny*side],q=[end[0]+nx*side,end[1]+ny*side];segment(g,p,q,'#c5bea4',3);segment(g,[p[0],p[1]-5],[q[0],q[1]-5],'#52665d',2);for(let i=0;i<=n;i++){const t=i/n,x=p[0]+(q[0]-p[0])*t,y=p[1]+(q[1]-p[1])*t;segment(g,[x,y],[x,y-6],'#52665d',1.4);}}
  if(item.closed)for(const p of [a,b]){segment(g,[p[0]-8,p[1]-4],[p[0]+8,p[1]-12],'#c68b56',3);segment(g,[p[0]-8,p[1]-12],[p[0]+8,p[1]-4],'#c68b56',3);}
 };

}
