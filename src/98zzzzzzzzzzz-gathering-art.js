// Gathering decoration is cached with the actual square; representative residents
// enter the normal ground-actor compositor. No attendance or payments are changed.
let gatheringArtTown=null,gatheringArtSignature='',gatheringArtIndex=new Map();
const gatheringArtSprites=new Map();let gatheringArtBytes=0;
function refreshGatheringArt(){
 const active=new Map(civicGatheringCues().map(e=>[e.id,e])),entries=[];
 for(const e of civicCalendarView().events){if(readBuild(e.venue)?.kind!=='square')continue;const cue=active.get(e.id)||{id:e.id,venue:e.venue,x:e.x,y:e.y,name:e.name,start:e.start,end:e.end,capacity:e.capacity,attendance:0,status:e.status};entries.push(cue);}
 const signature=JSON.stringify(entries);if(gatheringArtTown===G&&signature===gatheringArtSignature)return;
 gatheringArtTown=G;gatheringArtSignature=signature;gatheringArtIndex=new Map();
 const priority={active:3,scheduled:2,complete:1,cancelled:0,failed:0};for(const e of entries){const previous=gatheringArtIndex.get(e.venue);if(!previous||(priority[e.status]||0)>=(priority[previous.status]||0))gatheringArtIndex.set(e.venue,e);}
 viewRasterKey='';nightEmissionKey='';dirty=true;
}
const gatheringArtPrepare=prepareScene;prepareScene=function(){gatheringArtPrepare();refreshGatheringArt();};
const gatheringArtAuthorize=authorizeCivicGathering;authorizeCivicGathering=function(...args){const r=gatheringArtAuthorize(...args);if(r.ok)refreshGatheringArt();return r;};
const gatheringArtCancel=cancelCivicGathering;cancelCivicGathering=function(...args){const r=gatheringArtCancel(...args);if(r)refreshGatheringArt();return r;};
const gatheringArtDay=civicGatheringDay;civicGatheringDay=function(){gatheringArtDay();refreshGatheringArt();};
function gatheringArtResidents(item,cue){
 if(cue.status!=='active'||!cue.attendance||!visualDetailBudget().people||!gameOptions.traffic||cam.zoom<.62)return [];
 const n=Math.min(cue.attendance,fastRenderEnabled()?3:8),phase=(G.day+acc/1.65)*6,result=[];
 for(let i=0;i<n;i++){const p=point(-.28+(i%4)*.16,.29+Math.floor(i/4)*.10),walk=Math.sin(phase+i*1.7)*.65;result.push({kind:'vehicle',v:{id:930000+cue.id*8+i,style:'pedestrian',color:['#647f76','#b4825d','#85779b','#9eaa87'][i%4],ambient:true},x:item.x+p[0]+walk,y:item.y+p[1],dx:1,dy:.5});}
 return result;
}
// The public painter remains useful for isolated QA. Actual square draws use its
// cached static layer, while its crowd is submitted separately to scene depth.
paintCivicGathering=function(g,item,cue){
 if(item.b&&item.gatheringArtLayer!=='static')return;if(!gameOptions.decor||cam.zoom<.4||!['scheduled','active'].includes(cue.status))return;
 g.save();g.translate(item.x,item.y);
 if(cue.status==='scheduled'){box(g,-.29,-.19,.28,.14,1,4,'#a58b62');slab(g,-.30,-.21,.30,.17,6,'#b5ac8a');const p=point(.27,-.26,0);segment(g,p,[p[0],p[1]-15],'#78846c',1.5);g.fillStyle='#d7c08b';g.fillRect(p[0]-5,p[1]-16,10,6);g.fillStyle='#5c796b';g.fillRect(p[0]-3,p[1]-14,6,1);}
 else{
  // Covered public tables, with no displayed inventories or invented sales.
  for(const [u,v,color] of [[-.32,-.12,'#b47c5d'],[.08,-.29,'#6c8d83']]){box(g,u,v,.25,.20,1,6,'#a5916d');for(const [x,y] of [[u,v],[u+.25,v],[u,v+.20],[u+.25,v+.20]])segment(g,point(x,y,1),point(x,y,18),'#7e8068',1);slab(g,u-.035,v-.025,.32,.25,19,color);segment(g,point(u-.035,v+.225,18),point(u+.285,v+.225,18),'#d7c69e',2);for(let j=0;j<3;j++)segment(g,point(u+j*.10,v-.02,19),point(u+j*.10,v+.21,19),'#decda4',1);}
  const a=point(-.38,-.32,26),b=point(.38,-.32,26);segment(g,[a[0],a[1]+16],a,'#6c7a63',1);segment(g,[b[0],b[1]+16],b,'#6c7a63',1);segment(g,a,b,'#687a64',1);for(let i=1;i<7;i++){const t=i/7,x=a[0]+(b[0]-a[0])*t,y=a[1]+(b[1]-a[1])*t;polygon(g,[[x,y],[x+4,y+2],[x+1,y+6]],i%2?'#cfad67':'#a86d5a');}
  for(const [x,y] of [[a[0],a[1]+11],[b[0],b[1]+11]]){g.fillStyle=nightMode?'#ffdd8d':'#c5b78f';g.fillRect(x-1,y-3,3,4);}
 }
 g.restore();if(item.gatheringArtLayer!=='static')for(const a of gatheringArtResidents(item,cue))vehiclePaint(g,a.v,a,0);
};
const gatheringArtSpriteBase=spriteFor;spriteFor=function(item){
 const base=gatheringArtSpriteBase(item),cue=item.b?.kind==='square'&&gatheringArtIndex.get(item.b.id);if(!cue||!['scheduled','active'].includes(cue.status)||!gameOptions.decor||cam.zoom<.4)return base;
 const key=cue.status+':'+nightMode,entry=gatheringArtSprites.get(base);if(entry?.key===key)return entry.canvas;
 const c=document.createElement('canvas');c.width=base.width;c.height=base.height;c.anchorX=base.anchorX;c.anchorY=base.anchorY;c.lightSources=(base.lightSources||[]).slice();const g=c.getContext('2d');g.drawImage(base,0,0);g.translate(c.anchorX,c.anchorY);paintCivicGathering(g,{...item,x:0,y:0,gatheringArtLayer:'static'},cue);
 if(nightMode&&cue.status==='active')for(const u of [-.38,.38]){const p=point(u,-.32,15);c.lightSources.push([p[0]-1,p[1],3,0,4]);}
 if(entry){gatheringArtBytes-=entry.canvas.width*entry.canvas.height*4;gatheringArtSprites.delete(base);}gatheringArtSprites.set(base,{key,canvas:c});gatheringArtBytes+=c.width*c.height*4;while(gatheringArtSprites.size>32||gatheringArtBytes>4*1024*1024){const first=gatheringArtSprites.keys().next().value,old=gatheringArtSprites.get(first);gatheringArtBytes-=old.canvas.width*old.canvas.height*4;gatheringArtSprites.delete(first);}return c;
};
const gatheringArtActivityBase=buildingActivity;buildingActivity=function(items){const actors=gatheringArtActivityBase(items);if(!visualDetailBudget().people||!gameOptions.traffic)return actors;for(const item of items){if(item.b?.kind!=='square')continue;const cue=gatheringArtIndex.get(item.b.id);if(cue)actors.push(...gatheringArtResidents(item,cue));}return actors;};
