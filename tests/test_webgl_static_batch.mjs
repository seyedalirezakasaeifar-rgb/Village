import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import {pathToFileURL} from 'node:url';
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'city-batch-'));try{
fs.copyFileSync('assets/vendor/three-0.160.1.module.js',dir+'/three.mjs');fs.writeFileSync(dir+'/batch.mjs',fs.readFileSync('assets/webgl-static-batch.js','utf8').replace('./vendor/three-0.160.1.module.js','./three.mjs'));
const T=await import(pathToFileURL(dir+'/three.mjs')),{batchStaticMeshes}=await import(pathToFileURL(dir+'/batch.mjs'));const scene=new T.Scene(),expected=[];
for(let i=0;i<3;i++){const m=new T.Mesh(new T.BoxGeometry(1,1,1),new T.MeshStandardMaterial({color:0xaabbcc}));m.position.set(i*3,0,0);m.rotation.y=.2*i;m.scale.set(1+i,.5,1);m.userData.buildingId=40+i;m.castShadow=true;scene.add(m);m.updateMatrixWorld();const g=m.geometry.toNonIndexed();g.applyMatrix4(m.matrixWorld);expected.push(...g.attributes.position.array);g.dispose();}
const r=batchStaticMeshes(scene);if(r.removed!==3||scene.children.length!==1)throw Error('not batched');const m=scene.children[0],p=m.geometry.attributes.position.array;if(p.length!==expected.length||p.some((v,i)=>Math.abs(v-expected[i])>1e-6))throw Error('position changed');
for(let i=0;i<m.geometry.attributes.normal.count;i++){const n=new T.Vector3().fromBufferAttribute(m.geometry.attributes.normal,i);if(Math.abs(n.length()-1)>1e-6)throw Error('normal not unit');}
scene.updateMatrixWorld();for(let i=0;i<3;i++){const ray=new T.Raycaster(new T.Vector3(i*3,3,0),new T.Vector3(0,-1,0)),h=ray.intersectObjects(scene.children)[0];if(!h||h.object.userData.faceBuildingIds[h.faceIndex]!==40+i)throw Error('lost picking identity');}
console.log('PASS batching preserves transformed positions, normal matrices and ray identities');
}finally{fs.rmSync(dir,{recursive:true,force:true});}
