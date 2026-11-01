// Isolated art-direction prototype. Enable with ?cityArt=prototype; simulation
// and picking retain the same parcels and isometric projection.
if(new URLSearchParams(location.search).get('cityArt')==='prototype'||window.CITY_REDESIGN){
 document.documentElement.classList.add('city-art-prototype');
 const priorArchitecture=architecture;
 const kit=new Set(['home','apartment','office','grocer','bakery','tavern','factory','warehouse']);
 architecture=function(g,b,w,d){
  if(!kit.has(b.kind)||b.redevelopment){priorArchitecture(g,b,w,d);return;}
  const residential=b.kind==='home',urban=['apartment','office'].includes(b.kind),industry=['factory','warehouse'].includes(b.kind),id=b.id||0;
  const bw=w*(residential?.72:.82),bd=d*(residential?.66:.74),u=-bw/2,v=-bd/2;
  const masonry=['#c7b79c','#bba58d','#dfd4bd','#a99a86'][id%4],roof=['#343e48','#50504a','#694b3e'][id%3];
  // Broad quiet material planes replace the tiny pastel cottage vocabulary.
  slab(g,-w*.48,-d*.48,w*.96,d*.96,1,'#8c9182');
  slab(g,u-.08,v-.08,bw+.16,bd+.16,3,'#555a50');
  const floors=urban?3+(id%3):industry?1:residential?2:2,H=industry?38:floors*20;
  box(g,u,v,bw,bd,4,H,masonry,'#b9b6a6');
  // Deep cornices, inset glazing and structural bays keep facades legible.
  for(let f=0;f<floors;f++){
   const z=10+f*20,columns=residential?2:3;
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
   gable(g,u-.03,v-.04,bw+.06,bd+.08,H+5,19,roof);
   box(g,u+bw*.12,v+bd*.17,.11,.12,H+10,20,'#7d6d5b');
   // A deep covered entry and broad steps give houses a grounded human scale.
   box(g,-.12,v+bd+.01,.25,.15,3,18,'#77786b');slab(g,-.18,v+bd+.01,.36,.23,24,roof);
   for(let j=0;j<3;j++)slab(g,-.17,v+bd+.16+j*.055,.34,.06,6-j*2,'#b1ac95');
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
 const oldPalette=seasonPalette;
 seasonPalette=function(){const p=oldPalette();return {...p,grass:['#738569','#78896c','#7b8c6e','#718267','#819071'],water:'#467d86',dark:'#60765b'};};
 const style=document.createElement('style');style.textContent='.city-art-prototype #mapStatusDeck{width:220px;opacity:.94}.city-art-prototype .topbar{box-shadow:0 2px 12px #132d3030}.city-art-prototype #tabs button{font-family:Arial,sans-serif;font-weight:500}';document.head.appendChild(style);
}
