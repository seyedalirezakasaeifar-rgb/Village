// Original procedural material art. No photographs, external assets or RNG calls.
import * as THREE from './vendor/three-0.160.1.module.js';
const maps=new Map();
const noise=(x,y)=>{const q=Math.sin(x*127.1+y*311.7)*43758.5453;return q-Math.floor(q);};
export function materialMap(kind){
 if(maps.has(kind))return maps.get(kind);const c=document.createElement('canvas');c.width=c.height=128;const g=c.getContext('2d');
 if(kind==='contact'){
  const r=g.createRadialGradient(64,64,12,64,64,64);r.addColorStop(0,'rgba(17,30,31,.42)');r.addColorStop(.60,'rgba(17,30,31,.24)');r.addColorStop(1,'rgba(17,30,31,0)');g.fillStyle=r;g.fillRect(0,0,128,128);
 }else{
  const a=g.createImageData(128,128);for(let y=0;y<128;y++)for(let x=0;x<128;x++){
   let v=248;
   if(kind==='road')v=228+noise(x,y)*22;
   if(kind==='ground')v=218+17*Math.sin(x*.043)*Math.cos(y*.054)+9*Math.sin(x*.13+y*.09)+noise(x,y)*5;
   if(kind==='brick'){const mortar=y%16<2||(x+(Math.floor(y/16)%2)*16)%32<2;v=mortar?213:238+noise(Math.floor(x/32),Math.floor(y/16))*17;}
   if(kind==='stone'){const mortar=y%24<2||(x+(Math.floor(y/24)%2)*23)%46<2;v=mortar?203:231+noise(Math.floor(x/46),Math.floor(y/24))*24;}
   if(kind==='roof'){const seam=x%32<2,course=y%32<1;v=seam?205:course?224:244+noise(Math.floor(x/32),Math.floor(y/32))*10;}
   const i=(y*128+x)*4;a.data[i]=v;a.data[i+1]=v;a.data[i+2]=v;a.data[i+3]=255;
  }g.putImageData(a,0,0);
 }
 const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;if(kind!=='contact')t.wrapS=t.wrapT=THREE.RepeatWrapping;if(kind==='ground')t.repeat.set(4,4);t.anisotropy=1;maps.set(kind,t);return t;
}
export function roofUV(geometry){
 const p=geometry.getAttribute('position'),n=geometry.getAttribute('normal'),uv=[];for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i);if(Math.abs(n.getX(i))>.7)uv.push(z*2,y*2);else uv.push(x*2,z*2+y*2);}geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
}
export function contactGrounding(scene,state,buildings){
 const ids=new Set(buildings),poses=[];for(const b of state.buildings)if(ids.has(b.id)&&!['park','square','worksite','quarry','forestry'].includes(b.kind)&&!b.stage?.redevelopment)for(const id of b.footprint)poses.push([id%state.size,Math.floor(id/state.size)]);
 if(!poses.length)return;const m=new THREE.InstancedMesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({map:materialMap('contact'),transparent:true,depthWrite:false,toneMapped:false}),poses.length),d=new THREE.Object3D();
 poses.forEach(([x,z],i)=>{d.position.set(x,.0405,z);d.rotation.x=-Math.PI/2;d.scale.set(.98,.98,1);d.updateMatrix();m.setMatrixAt(i,d.matrix);});m.raycast=()=>{};scene.add(m);
}
export function releaseMaterialMaps(){for(const t of maps.values())t.dispose();maps.clear();}
