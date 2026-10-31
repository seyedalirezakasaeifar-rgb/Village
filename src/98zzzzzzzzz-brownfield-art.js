// Original finite site kit. Static descriptors drive appearance; drawing never works land.
let brownfieldArtTown=null,brownfieldArtSignature='';
function brownfieldArtDescriptors(){return brownfieldSites().map(brownfieldDescriptor);}
function refreshBrownfieldArt(){const key=JSON.stringify(brownfieldArtDescriptors());if(brownfieldArtTown!==G||key!==brownfieldArtSignature){brownfieldArtTown=G;brownfieldArtSignature=key;staticDirty=true;dirty=true;}}
const brownfieldArtAssess=brownfieldAssess;brownfieldAssess=function(...args){const r=brownfieldArtAssess(...args);if(r.ok)refreshBrownfieldArt();return r;};
const brownfieldArtAcquire=brownfieldAcquire;brownfieldAcquire=function(...args){const r=brownfieldArtAcquire(...args);if(r.ok)refreshBrownfieldArt();return r;};
const brownfieldArtFund=brownfieldFund;brownfieldFund=function(...args){const r=brownfieldArtFund(...args);if(r.ok)refreshBrownfieldArt();return r;};
const brownfieldArtReuse=brownfieldReuse;brownfieldReuse=function(...args){const r=brownfieldArtReuse(...args);if(r.ok)refreshBrownfieldArt();return r;};
const brownfieldArtDay=brownfieldDay;brownfieldDay=function(){brownfieldArtDay();refreshBrownfieldArt();};
const brownfieldArtPrepare=prepareScene;prepareScene=function(){brownfieldArtPrepare();const sites=brownfieldArtDescriptors(),reserved=new Set();for(const s of sites)if(['acquired','remediating','ready'].includes(s.status))for(const id of s.footprint)reserved.add(id);displayItems=displayItems.filter(a=>!(['tree','streetprop'].includes(a.kind)&&reserved.has(a.id)));
 for(const s of sites){const full=['acquired','remediating','ready'].includes(s.status),tiles=full?s.footprint:[s.y*T+s.x];for(const id of tiles){const x=id%T,y=id/T|0,p=iso(x,y);displayItems.push({kind:'brownfield',id:1000000+id,x:p[0],y:p[1]+18,w:1,d:1,site:s,first:id===tiles[0],northFence:!tiles.includes(id-T),westFence:!tiles.includes(id-1)});}}
 displayItems.sort((a,b)=>a.y-b.y||a.id-b.id);
};
function paintBrownfieldSite(g,a){
 const s=a.site,state=s.status,full=['acquired','remediating','ready'].includes(state);g.save();g.translate(a.x,a.y);
 if(full){slab(g,-.49,-.49,.98,.98,0,state==='ready'?'#b8ad87':'#94866b');if(cam.zoom>=.4){
  // Secure the legal tile footprint without suggesting demolition beyond its boundary.
  for(const edge of [a.northFence?[-.46,-.46,.46,-.46]:null,a.westFence?[-.46,-.46,-.46,.46]:null].filter(Boolean)){segment(g,point(edge[0],edge[1],2),point(edge[2],edge[3],2),'#6f7a68',1);for(let n=0;n<4;n++){const t=n/3,x=edge[0]+(edge[2]-edge[0])*t,y=edge[1]+(edge[3]-edge[1])*t;segment(g,point(x,y,0),point(x,y,10),'#aeb29b',1);}}
  if(state==='remediating'){box(g,-.28,-.23,.28,.28,0,4,'#b8aa84');box(g,.09,-.20,.23,.25,0,3,'#706f61');if(a.first){slab(g,-.08,.05,.30,.18,1,'#484f45');box(g,-.04,.05,.18,.16,2,7,'#b59a57');segment(g,point(.04,.1,9),point(.22,.13,16),'#c8ab68',3);segment(g,point(.22,.13,16),point(.34,.14,5),'#a88f57',2);}}
  else if(state==='ready'){for(let j=0;j<3;j++)segment(g,point(-.32,-.18+j*.18,1),point(.32,-.18+j*.18,1),'#cbc19e',1);}
 }}
 if(a.first&&cam.zoom>=.4){const p=point(.16,.40,0);segment(g,[p[0],p[1]],[p[0],p[1]-13],'#665b46',2);g.fillStyle=state==='ready'||state==='reused'?'#637f67':state==='assessed'?'#a99d80':'#bca06b';g.fillRect(p[0]-7,p[1]-15,14,7);g.fillStyle='#eee0b9';g.fillRect(p[0]-5,p[1]-13,state==='assessed'?4:10,1);if(state==='remediating'){const duration=20+Math.min(40,Math.floor(s.industrialAgeDays/30));g.fillStyle='#334c40';g.fillRect(p[0]-5,p[1]-10,Math.max(0,Math.round(10*(1-s.remaining/duration))),1);}}
 g.restore();
}
// Reuse the same opaque mask for night emission occlusion and moving-actor repair.
const brownfieldArtAtlas=new Map(),brownfieldArtSpriteFor=spriteFor;
spriteFor=function(a){if(a.kind!=='brownfield')return brownfieldArtSpriteFor(a);const s=a.site,duration=20+Math.min(40,Math.floor(s.industrialAgeDays/30)),progress=Math.max(0,Math.round(10*(1-s.remaining/duration))),key=[s.status,progress,a.first,a.northFence,a.westFence,cam.zoom>=.4].join(':');if(brownfieldArtAtlas.has(key))return brownfieldArtAtlas.get(key);const c=document.createElement('canvas');c.width=72;c.height=96;c.anchorX=36;c.anchorY=72;const g=c.getContext('2d');g.translate(36,72);paintBrownfieldSite(g,{...a,x:0,y:0});brownfieldArtAtlas.set(key,c);while(brownfieldArtAtlas.size>32)brownfieldArtAtlas.delete(brownfieldArtAtlas.keys().next().value);return c;};
const brownfieldArtCachedDraw=drawSceneSprite;drawSceneSprite=function(g,a){if(a.kind!=='brownfield')return brownfieldArtCachedDraw(g,a);const c=spriteFor(a);g.drawImage(c,Math.round(a.x-c.anchorX),Math.round(a.y-c.anchorY));};
