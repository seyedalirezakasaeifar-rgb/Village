// Original modular geometry. Public heritage references inform proportions;
// no photographic textures or concept-image backdrops are used.
import * as THREE from './vendor/three-0.160.1.module.js';
import {newfoundlandFamily,newfoundlandCondition} from './newfoundland-families.js';
const PAINT=['#a84136','#d5a63d','#367a91','#437e67','#805b87','#bd7646','#548fa0'];
export function newfoundlandBuilding(b,{state,scene,box}){
 const family=newfoundlandFamily(b,state);if(family==='construction')return false;
 if(!['home','apartment','grocer','bakery','tavern'].includes(b.kind))return false;
 const xs=b.footprint.map(i=>i%state.size),zs=b.footprint.map(i=>Math.floor(i/state.size)),minX=Math.min(...xs),minZ=Math.min(...zs),worldW=Math.max(...xs)-minX+1,worldD=Math.max(...zs)-minZ+1,x=minX+(worldW-1)/2,z=minZ+(worldD-1)/2;
 const sides=[[0,1],[1,0],[0,-1],[-1,0]],score=sides.map(([dx,dz])=>{let best=99;for(let step=1;step<=3;step++){const xx=Math.round(x+dx*(dx?worldW/2+.5:0)+dx*(step-1)),zz=Math.round(z+dz*(dz?worldD/2+.5:0)+dz*(step-1));if(xx>=0&&zz>=0&&xx<state.size&&zz<state.size&&[1,4].includes(state.tiles[zz*state.size+xx]))best=Math.min(best,step);}return best;});
 const front=score.indexOf(Math.min(...score)),theta=front*Math.PI/2,cos=Math.round(Math.cos(theta)),sin=Math.round(Math.sin(theta)),localW=front%2?worldD:worldW,localD=front%2?worldW:worldD;
 const neighbor=(sign)=>state.buildings.some(o=>o.id!==b.id&&o.kind==='home'&&o.footprint.some(i=>b.footprint.some(j=>(j%state.size+sign*cos>=0&&j%state.size+sign*cos<state.size)&&i===j+sign*cos-sign*sin*state.size)));
 const left=neighbor(-1),right=neighbor(1),W=localW-(left&&right ? .06 : (left||right ? .12 : .18)),D=localD*.64,home=b.kind==='home',floors=b.kind==='apartment'?3:family==='suburban-bungalow'?1:2,H=floors*.55,color=newfoundlandCondition(b)==='distressed'?new THREE.Color(PAINT[b.id%PAINT.length]).lerp(new THREE.Color('#909482'),.20).getStyle():PAINT[b.id%PAINT.length],trim=newfoundlandCondition(b)==='distressed'?'#cbc7b6':'#e8e1cb',slate=['#40545e','#556c70','#6d6260'][b.id%3];
 function local(u,y,v,w,h,d,c,r=.85){box(x+cos*u+sin*v,y,z-sin*u+cos*v,front%2?d:w,h,front%2?w:d,c,r);}
 function meshRoof(u,y,v,w,d,rise,type='mansard'){
  if(type==='saltbox'||type==='gable'){
   const ridge=type==='saltbox'?d*.14:0,V=[-w/2,0,-d/2,w/2,0,-d/2,w/2,rise,ridge,-w/2,0,-d/2,w/2,rise,ridge,-w/2,rise,ridge,-w/2,rise,ridge,w/2,rise,ridge,w/2,0,d/2,-w/2,rise,ridge,w/2,0,d/2,-w/2,0,d/2,-w/2,0,-d/2,-w/2,rise,ridge,-w/2,0,d/2,w/2,0,-d/2,w/2,0,d/2,w/2,rise,ridge];
   const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(V,3));geo.computeVertexNormals();const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:slate,roughness:.67,metalness:.16,side:THREE.DoubleSide}));mesh.rotation.y=theta;mesh.position.set(x+cos*u+sin*v,y,z-sin*u+cos*v);mesh.userData.buildingId=b.id;mesh.castShadow=true;mesh.receiveShadow=true;scene.add(mesh);return;
  }
  if(type==='flat')rise=.07;
  const bottom=[[-w/2,-d/2],[w/2,-d/2],[w/2,d/2],[-w/2,d/2]],top=bottom.map(([a,c])=>[a*(type==='flat'?.98:type==='mansard'?.75:.10),c*.68]);const vertices=[];
  for(let i=0;i<4;i++){const j=(i+1)%4,A=bottom[i],B=bottom[j],C=top[j],E=top[i];vertices.push(A[0],0,A[1],B[0],0,B[1],C[0],rise,C[1],A[0],0,A[1],C[0],rise,C[1],E[0],rise,E[1]);}
  vertices.push(top[0][0],rise,top[0][1],top[2][0],rise,top[2][1],top[1][0],rise,top[1][1],top[0][0],rise,top[0][1],top[3][0],rise,top[3][1],top[2][0],rise,top[2][1]);
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geo.computeVertexNormals();const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:slate,roughness:.67,metalness:.16,side:THREE.DoubleSide}));mesh.rotation.y=theta;mesh.position.set(x+cos*u+sin*v,y,z-sin*u+cos*v);mesh.userData.buildingId=b.id;mesh.castShadow=true;mesh.receiveShadow=true;scene.add(mesh);
 }
 local(0,.045,0,localW*.96,.09,localD*.96,'#a1a293');local(0,.12,0,W+.02,.20,D+.03,'#7a7e74');local(0,H/2+.17,0,W,H,D,'clap:'+color);
 // Clapboard courses use an original shared procedural material, not thousands of shadow-casting strips.
 for(const u of [-W/2+.018,W/2-.018]){local(u,H/2+.17,D/2+.02,.035,H,.03,trim);local(u,H/2+.17,-D/2-.015,.035,H,.03,trim);}
 for(const [side,attached] of [[-1,left],[1,right]])if(attached){const reach=(localW-W)/2;local(side*(localW/2-reach/2),H/2+.17,0,reach,H,D,'clap:'+color);local(side*(localW/2-.025),H+.23,0,.05,.10,D+.08,trim);}
 local(0,H+.19,0,Math.min(W+.08,localW*.99),.075,D+.10,trim);local(0,H+.25,0,Math.min(W+.10,localW*.99),.055,D+.12,'#66716a');meshRoof(0,H+.27,0,Math.min(W+.08,localW*.99),D+.11,.34,family==='coastal-saltbox'?'saltbox':['suburban-cape','compact-timber'].includes(family)?'gable':family==='rural-biscuitbox'?'flat':b.id%3?'mansard':'hip');
 function window(u,y,v,width=.20,height=.29,side=1){local(u,y,v,width+.045,height+.05,.035,trim);local(u,y+.005,v+side*.025,width,height,.025,'#37596c',.26);local(u,y,v+side*.044,.014,height,.012,trim);local(u,y,v+side*.047,width,.014,.012,trim);local(u,y-height/2-.035,v+side*.04,width+.07,.035,.075,trim);local(u,y+height/2+.035,v+side*.025,width+.065,.035,.045,trim);}
 for(let f=0;f<floors;f++)for(const u of [-W*.24,W*.24])if(f||u<0)window(u,.48+f*.55,D/2+.035);
 for(const [side,attached] of [[-1,left],[1,right]])if(!attached)for(let f=0;f<floors;f++)for(const v of [-D*.22,D*.22]){const y=.48+f*.55;local(side*(W/2+.018),y,v,.03,.28,.19,trim);local(side*(W/2+.038),y,v,.02,.22,.13,'#37596c',.26);local(side*(W/2+.054),y,v,.012,.012,.13,trim);}
 for(let f=0;f<floors;f++)for(const u of [-W*.24,W*.24])window(u,.48+f*.55,-D/2-.035,.18,.25,-1);
 // Distinct doorway, transom, stone steps and slender handrails all stay on plot.
 const doorU=W*.24;local(doorU,.40,D/2+.035,.22,.48,.055,trim);local(doorU,.39,D/2+.07,.16,.40,.025,'#394d4b');local(doorU,.65,D/2+.08,.16,.085,.025,'#708b91',.3);local(doorU+.055,.38,D/2+.09,.018,.018,.018,'#c3a464',.45);
 for(let k=0;k<3;k++)local(doorU,.035+k*.04,D/2+.12-k*.035,.28,.07+k*.055,.08,'#aaa99b');
 for(const u of [doorU-.15,doorU+.15]){local(u,.21,D/2+.14,.018,.33,.018,'#4b5e59');local(u,.38,D/2+.09,.018,.025,.15,'#4b5e59');}
 // Dormer is structural original geometry, with a separate framed face.
 if(!['suburban-bungalow','rural-biscuitbox'].includes(family)&&b.id%3!==0){local(0,H+.40,D*.23,.25,.25,.22,color);window(0,H+.42,D*.23+.13,.16,.18);meshRoof(0,H+.54,D*.23,.31,.30,.12,'hip');}
 local(-W*.28,H+.58,-D*.19,.10,.30,.13,'#8d7560');
 if(!home){local(0,.93,D/2+.08,W*.82,.13,.06,'#e5d7b3');local(0,.92,D/2+.12,W*.70,.07,.015,color);local(0,.76,D/2+.08,W*.88,.055,.13,['#6f4d5e','#395e53','#a85a39'][b.id%3]);}
 if(family==='detached-merchant'){for(const u of [-W*.38,0,W*.38])local(u,.42,D/2+.12,.035,.70,.035,trim);local(0,.80,D/2+.10,W*.9,.065,.22,slate);}
 return true;
}
