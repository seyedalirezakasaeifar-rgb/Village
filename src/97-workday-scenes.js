// Original small workday tableaux. They visualize actual operating activity;
// samples never create cargo, income, pupils or production in the simulation.
function workdayScenes(items){
 if(!visualDetailBudget().people||!gameOptions.decor||gameOptions.quality==='low')return [];
 const scenes=[],cap=fastRenderEnabled()?3:gameOptions.quality==='high'?12:7;
 for(let n=items.length-1;n>=0;n--){const item=items[n],b=item.b;if(!b||scenes.length>=cap)continue;const f=G.firms[b.firm];let scene=null;
  if(f&&!f.closed&&workingStaff(f).length&&f.production>0){if(['mill','sawmill','factory'].includes(b.kind))scene='machinery';else if(['farm','fishery','forestry'].includes(b.kind))scene='harvest';}
  if(f&&!f.closed&&b.kind==='wharf'&&workingStaff(f).length&&(f.cargoToday||0)>0)scene='loading';
  if(b.kind==='clinic'&&G.serviceProvision?.health?.paid>0&&G.serviceProvision.health.coverage>0)scene='care';
  if(b.kind==='school'&&G.serviceProvision?.school?.paid>0&&G.serviceProvision.school.coverage>0)scene='teaching';
  if(b.kind==='worksite'||b.redevelopment){const p=G.projects.find(p=>p.id===b.id);if(p&&!p.reason&&p.remaining>0)scene='construction';}
  if(!scene)continue;const front=point(item.w*.10,item.d*.48,0),portal=graph().portals.get(b.id),road=portal==null?null:roadCenter(portal);const x=road&&road[1]>=item.y?item.x*.35+road[0]*.65:item.x+front[0],y=road&&road[1]>=item.y?item.y*.35+road[1]*.65:item.y+front[1];scenes.push({kind:'workday',scene,b,f,x,y,dx:1,dy:.5});
 }
 return scenes;
}
function paintWorkdayScene(g,a,clock){
 const phase=clock+a.b.id*.17,x=Math.round(a.x),y=Math.round(a.y),skin=['#d6b38b','#c79570','#9d7358'][a.b.id%3];
 g.save();g.translate(x,y);g.fillStyle='#304b4530';g.beginPath();g.ellipse(0,2,16,4,.2,0,Math.PI*2);g.fill();
 const person=(px,py,color,scale=1,working=false)=>{g.save();g.translate(Math.round(px),Math.round(py));g.scale(scale,scale);const reach=working?Math.sin(phase*3)*2:0;
  g.fillStyle='#374e43';g.fillRect(-2,-2,2,4);g.fillRect(1,-1,2,3);g.fillStyle=color;g.fillRect(-3,-9,6,8);g.fillStyle=tone(color,.75);g.fillRect(2,-8,2,7);g.fillStyle=skin;g.fillRect(-2,-14,5,5);g.fillRect(-5,-8+reach,2,5);g.fillRect(4,-8-reach,2,5);g.fillStyle='#6a5a41';g.fillRect(-3,-15,7,2);g.restore();};
 if(a.scene==='machinery'){
  // A cast-iron flywheel and a short handling bench share one drive phase.
  polygon(g,[[-16,-4],[-3,-9],[14,-1],[1,5]],'#aa9674');segment(g,[-14,-2],[-14,5],'#6d7160',2);segment(g,[12,0],[12,7],'#6d7160',2);
  g.save();g.translate(-6,-10);g.transform(.85,.42,0,1,0,0);g.strokeStyle='#565f53';g.lineWidth=3;g.beginPath();g.arc(0,0,8,0,Math.PI*2);g.stroke();g.strokeStyle='#b2ad86';g.lineWidth=1;g.beginPath();g.arc(0,0,6,0,Math.PI*2);g.stroke();
  for(let j=0;j<6;j++){const turn=phase*1.8+j*Math.PI/3;segment(g,[0,0],[Math.cos(turn)*6,Math.sin(turn)*6],'#7d856c',1.5);}g.fillStyle='#d0bb83';g.fillRect(-2,-2,4,4);g.restore();
  const drift=(phase*.35)%1;if(a.b.kind==='sawmill'){segment(g,[0+drift*6,-5],[12+drift*6,1],'#b19464',4);segment(g,[1+drift*6,-6],[13+drift*6,0],'#d0b583',1);}else{polygon(g,[[3,-7],[9,-10],[14,-7],[8,-4]],'#c2ad7d');polygon(g,[[3,-7],[8,-4],[8,1],[3,-2]],'#9f895d');polygon(g,[[8,-4],[14,-7],[14,-2],[8,1]],'#ad996c');}
  person(14,8,'#6f8271',.86,true);
 }else if(a.scene==='harvest'){
  person(-5+Math.sin(phase*.6)*3,0,'#9c8054',.93,true);g.fillStyle='#ad8d5d';g.fillRect(5,-4,8,5);g.fillStyle='#d3be87';g.fillRect(5,-5,8,2);
  if(a.b.kind==='fishery'){segment(g,[-5,-9],[5,-21+Math.sin(phase)*1.2],'#b3a37a');segment(g,[5,-21+Math.sin(phase)*1.2],[11,-3],'#ddd7b099');}else for(let j=0;j<3;j++){segment(g,[6+j*2,-5],[6+j*2,-10],'#b8ad65');g.fillStyle='#d2bd72';g.fillRect(5+j*2,-11,3,3);}
 }else if(a.scene==='loading'){
  const step=(phase*.22)%1;person(-12+step*20,step*6,'#718b80',.93,true);g.fillStyle='#c8aa72';g.fillRect(-14+step*20,-5+step*6,7,5);segment(g,[-13+step*20,-4+step*6],[-8+step*20,-2+step*6],'#8d7854');box(g,.12,.12,.13,.11,0,5,'#b69a65');
 }else if(a.scene==='care'){
  person(-7,0,'#d3d8c3',.97,true);g.fillStyle='#477b66';g.fillRect(-9,-8,4,1);person(8,5+Math.sin(phase*.5),'#8b7765',.87);g.fillStyle='#c7b587';g.fillRect(0,-2,5,4);g.fillStyle='#607d6b';g.fillRect(1,-1,3,1);
 }else if(a.scene==='teaching'){
  person(-7,-1,'#687e77',1,true);person(3,5,'#ab8b60',.72);person(12,9,'#84956a',.70);segment(g,[-11,-11],[-1,-7],'#c7b994',2);
 }else{
  person(-5,1,'#9c855b',.93,true);g.fillStyle='#dbc183';g.fillRect(-8,-14,7,3);const angle=Math.sin(phase*3)*.65;segment(g,[-1,-9],[6+angle*4,-16+angle*5],'#7b6f52',2);segment(g,[3+angle*4,-17+angle*5],[9+angle*4,-15+angle*5],'#66776e',3);polygon(g,[[6,2],[13,-1],[18,2],[11,5]],'#b9a27b');
 }
 g.restore();
}
