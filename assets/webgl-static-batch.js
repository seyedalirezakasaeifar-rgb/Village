// Original static material batching. Model identity is retained per triangle;
// transformed normals use the inverse-transpose matrix, including nonuniform scale.
import * as THREE from './vendor/three-0.160.1.module.js';
export function batchStaticMeshes(scene,chunkSize=Infinity){
 const groups=new Map();scene.updateMatrixWorld(true);
 for(const mesh of [...scene.children]){
  if(!mesh.isMesh||mesh.isInstancedMesh||Array.isArray(mesh.material))continue;
  const m=mesh.material,key=[m.type,m.color?.getHex(),m.roughness,m.metalness,m.side,m.map?.uuid||'',mesh.castShadow,mesh.receiveShadow,Math.floor(mesh.position.x/chunkSize),Math.floor(mesh.position.z/chunkSize)].join(':');
  if(!groups.has(key))groups.set(key,[]);groups.get(key).push(mesh);
 }
 let removed=0;
 for(const meshes of groups.values()){
  if(meshes.length<2)continue;
  const positions=[],normals=[],uvs=[],ids=[],tiles=[];let allUV=true;
  for(const mesh of meshes){
   const geo=mesh.geometry.index?mesh.geometry.toNonIndexed():mesh.geometry.clone();geo.applyMatrix4(mesh.matrixWorld);
   const p=geo.getAttribute('position'),n=geo.getAttribute('normal'),uv=geo.getAttribute('uv');allUV=allUV&&!!uv;
   for(let i=0;i<p.count;i++){positions.push(p.getX(i),p.getY(i),p.getZ(i));normals.push(n.getX(i),n.getY(i),n.getZ(i));if(uv)uvs.push(uv.getX(i),uv.getY(i));else uvs.push(0,0);if(i%3===0){ids.push(mesh.userData.buildingId);tiles.push(mesh.userData.gridTileId);}}
   geo.dispose();scene.remove(mesh);mesh.geometry.dispose();removed++;
  }
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));if(allUV)g.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));g.computeBoundingSphere();
  const merged=new THREE.Mesh(g,meshes[0].material);merged.castShadow=meshes[0].castShadow;merged.receiveShadow=meshes[0].receiveShadow;merged.userData.faceBuildingIds=ids;merged.userData.faceGridTileIds=tiles;scene.add(merged);
  for(const mesh of meshes.slice(1))if(mesh.material!==meshes[0].material)mesh.material.dispose();
 }
 return {removed,groups:groups.size};
}
