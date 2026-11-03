// Stable visual states follow property condition, occupation and funded capex.
function propertyAppearance(b){
 const f=G.firms[b.firm],empty=b.kind==='home'&&!G.households[b.hh]?.people.some(id=>!G.people[id]?.deceased&&!G.people[id]?.movedAway);
 return {condition:b.condition<45?'distressed':b.condition<75?'weathered':'maintained',status:f?(f.closed?'closed':'trading'):empty?'vacant':'occupied',invested:!!f&&f.scale>=1.4};
}
function appearanceKey(b){const a=propertyAppearance(b);return a.condition+':'+a.status+':'+a.invested;}
function architecturalIdentity(g,b,w,d){
 if(!gameOptions.decor||gameOptions.quality==='low'||b.kind==='worksite'||b.redevelopment)return;
 const a=propertyAppearance(b),u=-w*.365,v=d*.35,H=b.kind==='tower'?132:b.kind==='apartment'?48:b.kind==='office'?60:['home','farm','forestry','quarry'].includes(b.kind)?0:30;
 const civic=['school','college','townhall','courthouse','bank','clinic'].includes(b.kind),shop=['grocer','bakery','tavern'].includes(b.kind),industrial=['factory','warehouse','sawmill','mill'].includes(b.kind);
 if(civic){
  for(const z of [3,17,30]){slab(g,u-.025,v-.015,w*.78,.055,z,'#d7ceb0');segment(g,point(u,v+.05,z-1),point(u+w*.76,v+.05,z-1),'#8d8d78');}
  // Alternating dressed corner stones and a broad civic entrance stair.
  for(let z=2;z<30;z+=5)box(g,u-.01,v,.07,.05,z,3,'#d9d1b5');
  for(let j=0;j<3;j++)slab(g,-.15-j*.025,v+.05+j*.055,.30+j*.05,.06,3-j,'#c6bda1');
 }
 if(shop){
  // Glazed shopfront and timber-framed display, distinct from civic windows.
  box(g,u+.05,v+.015,w*.21,.025,3,9,a.status==='closed'?'#827e6b':'#6f9690');
  box(g,u+w*.50,v+.015,w*.20,.025,3,9,a.status==='closed'?'#827e6b':'#739e9a');
  for(const x of [u+.05,u+w*.26,u+w*.50,u+w*.70])segment(g,point(x,v+.045,2),point(x,v+.045,13),'#d6c39a',1);
  if(b.kind==='bakery'){const q=point(u+.12,v+.06,7);g.fillStyle='#e4c788';for(let j=0;j<3;j++)g.fillRect(q[0]+j*3,q[1]+j,3,2);}
 }
 if(industrial){
  // Clerestory glazing and riveted cladding retain the warehouse silhouette.
  for(let j=0;j<6;j++){const x=u+.04+j*w*.105;segment(g,point(x,v+.02,1),point(x,v+.02,27),'#8d8d7a');}
  for(let j=0;j<3;j++){const q=point(u+.08+j*w*.20,-d*.05,36);polygon(g,[[q[0]-5,q[1]],[q[0]+3,q[1]-4],[q[0]+9,q[1]-1],[q[0]+1,q[1]+3]],a.status==='closed'?'#78837b':'#8fbbb1');}
 }
 if(b.kind==='home'){
  const q=point(-w*.30,d*.36,0);
  // Three parcel treatments: stone-edged beds, paved courts, kitchen plots.
  if(b.id%3===0){for(let j=0;j<5;j++){const t=point(-.34+j*.13,.39,1);g.fillStyle='#b6b79b';g.fillRect(t[0]-2,t[1]-1,4,2);}}
  else if(b.id%3===1){for(let j=0;j<4;j++)slab(g,-.34+j*.11,.36,.075,.08,1,'#c9bd9a');}
  else {for(let j=0;j<3;j++)slab(g,-.37,.17+j*.08,.25,.035,1,j%2?'#89915b':'#aa9364');}
  if(a.status==='vacant'){segment(g,[q[0],q[1]-5],[q[0],q[1]-15],'#6c7157');g.fillStyle='#d6c49e';g.fillRect(q[0]-5,q[1]-15,11,5);}
 }
 if(a.invested&&industrial){box(g,.12,-.12,.20,.20,37,8,'#81998d');slab(g,.10,-.14,.24,.24,46,'#acb9a4');segment(g,point(.21,-.02,37),point(.21,-.02,28),'#687c72',2);}
 if(a.condition!=='maintained'&&H){for(let j=0;j<3;j++){const q=point(u+.08+j*w*.2,v+.05,8+j*5);segment(g,q,[q[0]+2,q[1]+6],'#737a6755');segment(g,[q[0]+2,q[1]+6],[q[0]-1,q[1]+9],'#737a6755');}}
 if(a.status==='closed'&&H){const q=point(0,v+.07,7);g.fillStyle='#a48f6a';g.fillRect(q[0]-6,q[1]-2,12,5);segment(g,[q[0]-5,q[1]-1],[q[0]+5,q[1]+2],'#736d55');}
}
