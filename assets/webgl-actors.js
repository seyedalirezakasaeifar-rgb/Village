import * as THREE from './vendor/three-0.160.1.module.js';
import {bridgeHeightAt} from './webgl-bridges.js';
// Bounded original actor geometry. All pose/status inputs come from the model
// adapter; this module neither dispatches trips nor settles cargo.
export function actorLayer(scene,size,bridges){
 const cube=new THREE.BoxGeometry(1,1,1),mesh=new THREE.InstancedMesh(cube,new THREE.MeshStandardMaterial({color:'#ffffff',roughness:.8}),1024),heads=new THREE.InstancedMesh(new THREE.SphereGeometry(1,6,4),new THREE.MeshStandardMaterial({color:'#ffffff',roughness:1}),64),dummy=new THREE.Object3D();mesh.count=0;heads.count=0;mesh.frustumCulled=false;heads.frustumCulled=false;mesh.setColorAt(0,new THREE.Color('#ffffff'));heads.setColorAt(0,new THREE.Color('#ffffff'));scene.add(mesh,heads);
 const fadeMeshes=Array.from({length:10},()=>{const m=new THREE.InstancedMesh(cube,new THREE.MeshStandardMaterial({color:'#ffffff',roughness:.8,transparent:true,opacity:0,depthWrite:false}),5);m.count=0;m.frustumCulled=false;m.setColorAt(0,new THREE.Color('#ffffff'));scene.add(m);return m;});let last=[];
 function update(actors){let n=0,hn=0,fadeIndex=0;last=[];for(const m of fadeMeshes){m.count=0;m.userData.instanceActorIds=[];}mesh.userData.instanceActorIds=[];heads.userData.instanceActorIds=[];
  for(const a of actors.slice(0,64)){
   const fade=a.kind==='boat'&&(a.opacity??1)<.999?fadeMeshes[fadeIndex++]:null;if((a.opacity??1)<=0)continue;if(fade){fade.material.opacity=a.opacity;fade.renderOrder=Math.round((a.x+a.z)*100);}
   const heading=Math.atan2(a.dx,a.dz),c=Math.cos(heading),s=Math.sin(heading),base=a.kind==='boat'?-.005:a.kind==='train'?1.22:bridgeHeightAt(a.x,a.z,bridges,size),color=a.color||'#b98959';
   function part(u,y,v,w,h,d,col){if(n>=1024||fade&&fade.count>=5)return;dummy.position.set(a.x+c*u+s*v,base+y,a.z-s*u+c*v);dummy.rotation.set(0,heading,0);dummy.scale.set(w,h,d);dummy.updateMatrix();if(fade){const i=fade.count++;fade.setMatrixAt(i,dummy.matrix);fade.setColorAt(i,new THREE.Color(col));fade.userData.instanceActorIds[i]=a.id;}else{mesh.setMatrixAt(n,dummy.matrix);mesh.setColorAt(n,new THREE.Color(col));mesh.userData.instanceActorIds[n]=a.id;n++;}}
   if(a.kind==='pedestrian'){
    part(0,.13,0,.055,.13,.055,color);for(const u of [-.017,.017])part(u,.045,0,.018,.09,.022,'#414e4e');if(hn<64){dummy.position.set(a.x,base+.23,a.z);dummy.rotation.set(0,0,0);dummy.scale.setScalar(.034);dummy.updateMatrix();heads.setMatrixAt(hn,dummy.matrix);heads.setColorAt(hn,new THREE.Color('#c99a75'));heads.userData.instanceActorIds[hn]=a.id;hn++;}
   }else if(a.kind==='boat'){
    part(0,.055,0,.21,.10,.58,'#526c70');part(0,.11,0,.18,.035,.49,'#baa276');part(0,.16,-.16,.14,.09,.15,'#e1d9bd');part(0,.13,.08,.15,.06,.24,color);part(0,.17,-.245,.06,.025,.018,'#4a7181');
   }else{
    const large=['truck','bus','train'].includes(a.kind),length=a.kind==='train'?.82:a.kind==='bus'?.65:large?.59:.39,width=large?.23:.19;
    part(0,large?.15:.10,0,width,large?.21:.12,length,color);if(a.kind==='truck'){part(0,.23,.19,width*.92,.14,.17,'#d2c9ac');part(0,.25,.285,width*.77,.07,.014,'#466978');}else{part(0,large?.25:.18,0,width*.89,large?.07:.08,length*.66,'#527383');part(0,large?.30:.225,0,width*.97,.025,length*.70,color);}
    for(const u of [-width*.52,width*.52])for(const v of [-length*.30,length*.30])part(u,.045,v,.035,.09,.075,'#354744');
   }
   last.push({id:a.id,kind:a.kind,x:a.x,z:a.z,base});
  }
  mesh.count=n;heads.count=hn;mesh.boundingSphere=null;heads.boundingSphere=null;mesh.instanceMatrix.needsUpdate=true;mesh.instanceColor.needsUpdate=true;heads.instanceMatrix.needsUpdate=true;heads.instanceColor.needsUpdate=true;for(const m of fadeMeshes){m.boundingSphere=null;if(m.count){m.instanceMatrix.needsUpdate=true;m.instanceColor.needsUpdate=true;}}return {actors:last.length,parts:n+hn+fadeMeshes.reduce((sum,m)=>sum+m.count,0),poses:last};
 }
 return {update};
}
