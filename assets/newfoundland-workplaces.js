// Original generalized Newfoundland working/civic architecture, not replicas.
import * as THREE from './vendor/three-0.160.1.module.js';
export function newfoundlandWorkplace(b,{state,scene,box,richMaterials=true}){
 const civic=['townhall','school','college','courthouse','police','clinic','fire'],commercial=['bank','office'],working=['warehouse','factory','mill','sawmill','contractor','fishery','wharf'],farm=b.kind==='farm';
 if(!civic.includes(b.kind)&&!commercial.includes(b.kind)&&!working.includes(b.kind)&&!farm)return false;
 const xs=b.footprint.map(i=>i%state.size),zs=b.footprint.map(i=>Math.floor(i/state.size)),minX=Math.min(...xs),minZ=Math.min(...zs),w=Math.max(...xs)-minX+1,d=Math.max(...zs)-minZ+1;
 if(w*d!==b.footprint.length)return false; // Never build through a concave title's void.
 const x=minX+(w-1)/2,z=minZ+(d-1)/2,sides=[[0,1],[1,0],[0,-1],[-1,0]],scores=sides.map(([dx,dz])=>{const xx=Math.round(x+dx*(w/2+.5)),zz=Math.round(z+dz*(d/2+.5));return xx>=0&&zz>=0&&xx<state.size&&zz<state.size&&(b.kind==='wharf'||b.kind==='fishery'?[2,4]:[1,4]).includes(state.tiles[zz*state.size+xx])?0:1;}),front=scores.indexOf(Math.min(...scores)),theta=front*Math.PI/2,c=Math.round(Math.cos(theta)),s=Math.round(Math.sin(theta)),W=(front%2?d:w)*.87,D=(front%2?w:d)*.68;
 function part(u,y,v,a,h,depth,color,rough=.86){box(x+c*u+s*v,y,z-s*u+c*v,front%2?depth:a,h,front%2?a:depth,color,rough);}
 const industry=working.includes(b.kind)||farm,fire=b.kind==='fire',clinic=b.kind==='clinic',bank=b.kind==='bank',levels=industry||fire||clinic?1:b.kind==='office'?3:2,H=levels*(industry?.83:.58),stone=richMaterials?({bank:'#aaa393',townhall:'#ad7764',school:'#a9846e',college:'#b99173',courthouse:'#a3a08e',police:'#8f8d7e',clinic:'#b9c8b1',fire:'#9c5b4b',farm:'#a44739',factory:'#8d6c5d',mill:'#9c8870',sawmill:'#8f7663',warehouse:'#667b79',contractor:'#718477',fishery:'#688e93',wharf:'#947c62'}[b.kind]||'#768582'):bank?'#aaa393':civic.includes(b.kind)?'#ad7764':farm?'#a44739':'#768582',trim='#ded8c6',roof='#455b64';
 part(0,.045,0,W+.08,.09,D+.12,'#9b9c8f');part(0,H/2+.12,0,W,H,D,(richMaterials?(['bank','courthouse'].includes(b.kind)?'stone:':civic.includes(b.kind)&&!clinic||['factory','mill'].includes(b.kind)?'brick:':'clap:'):'')+stone);part(0,.16,0,W+.025,.16,D+.035,'#747d79');
 // Roof ridge, eaves and full end gables share one lawful footprint.
 const a=W/2+.035,q=D/2+.035,rise=industry?.23:.31,V=[-a,0,-q,a,0,-q,a,rise,0,-a,0,-q,a,rise,0,-a,rise,0,-a,rise,0,a,rise,0,a,0,q,-a,rise,0,a,0,q,-a,0,q,-a,0,-q,-a,rise,0,-a,0,q,a,0,-q,a,0,q,a,rise,0];
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(V,3));g.computeVertexNormals();const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:roof,roughness:.7,metalness:.12,side:THREE.DoubleSide}));m.position.set(x,H+.13,z);m.rotation.y=theta;m.castShadow=true;m.receiveShadow=true;m.userData.buildingId=b.id;scene.add(m);part(0,H+.12,0,W+.07,.065,D+.07,trim);
 const columns=Math.max(2,Math.floor(W/.31));
 for(let f=0;f<levels;f++)for(let j=0;j<columns;j++){
  const u=-W*.35+j*W*.70/(columns-1),y=.48+f*.58;
  if(f===0&&Math.abs(u)<W*.21&&!industry)continue;
  part(u,y,D/2+.022,.17,.27,.035,trim);part(u,y+.005,D/2+.045,.12,.21,.018,'#456779',.3);part(u,y,D/2+.059,.012,.21,.01,trim);
 }
 // Side/rear institutional and warehouse windows avoid blank colour slabs.
 for(const side of [-1,1])for(let f=0;f<levels;f++)for(const v of [-D*.24,D*.24]){part(side*(W/2+.015),.48+f*.58,v,.035,.25,.18,trim);part(side*(W/2+.036),.48+f*.58,v,.018,.19,.12,'#456779',.3);}
 if(industry||fire){
  const doors=fire?2:1;for(let i=0;i<doors;i++){const u=(i-(doors-1)/2)*W*.42;part(u,.43,D/2+.035,W*(doors===2?.34:.49),.59,.045,trim);part(u,.42,D/2+.063,W*(doors===2?.28:.43),.49,.025,fire?'#8e4239':'#5d6d69');for(const y of [.26,.38,.50,.62])part(u,y,D/2+.081,W*(doors===2?.28:.43),.014,.01,'#a8aaa0');}
 }else{
  part(0,.40,D/2+.03,.25,.52,.055,trim);part(0,.39,D/2+.067,.18,.44,.025,'#3c5555');part(0,.70,D/2+.07,.24,.09,.025,'#739297',.3);part(0,.06,D/2+.08,.39,.12,.14,'#b0afa0');
  if(bank||b.kind==='courthouse'){for(const u of [-W*.36,-W*.18,W*.18,W*.36]){part(u,.63,D/2+.07,.045,1.05,.07,trim);part(u,1.15,D/2+.07,.085,.06,.10,trim);}part(0,.94,D/2+.06,W,.055,.06,trim);}
 }
 if(b.kind==='townhall'){part(0,H+.29,0,.28,.44,.28,stone);part(0,H+.53,0,.33,.045,.33,trim);part(0,H+.34,.15,.13,.13,.018,trim);part(0,H+.34,.162,.012,.05,.012,'#3c5555');}
 // Actual closure is a shutter/barrier cue; no decorative crowds or paid crews.
 if(b.firm?.closed||b.provider?.closed){part(0,.18,D/2+.11,W*.66,.035,.025,'#9b7652');}
 return true;
}
