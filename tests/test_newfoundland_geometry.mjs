import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import {pathToFileURL} from 'node:url';
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'newfoundland-geometry-'));fs.copyFileSync(new URL('../assets/vendor/three-0.160.1.module.js',import.meta.url),path.join(tmp,'three.mjs'));fs.writeFileSync(path.join(tmp,'kit.mjs'),fs.readFileSync(new URL('../assets/newfoundland-kit.js',import.meta.url),'utf8').replace('./vendor/three-0.160.1.module.js','./three.mjs'));
const THREE=await import(pathToFileURL(path.join(tmp,'three.mjs'))),{newfoundlandBuilding}=await import(pathToFileURL(path.join(tmp,'kit.mjs')));
let cases=0;
for(const kind of ['home','apartment','grocer','bakery','tavern'])for(let front=0;front<4;front++)for(const attached of [false,true]){
 const T=16,id=5*T+5,b={id:7,x:5,y:5,kind,footprint:[id]},state={size:T,tiles:Array(T*T).fill(0),buildings:[b]};const [dx,dz]=[[0,1],[1,0],[0,-1],[-1,0]][front];state.tiles[(5+dz)*T+5+dx]=1;
 if(attached)state.buildings.push({id:8,x:5+dz,y:5-dx,kind:'home',footprint:[(5-dx)*T+5+dz]});
 const before=JSON.stringify(state),scene=new THREE.Scene(),bounds=[];const box=(x,y,z,w,h,d)=>bounds.push([x-w/2,z-d/2,x+w/2,z+d/2]);
 if(!newfoundlandBuilding(b,{state,scene,box}))throw Error('kit missing');scene.updateMatrixWorld(true);scene.traverse(o=>{if(o.isMesh){o.geometry.computeBoundingBox();const q=o.geometry.boundingBox.clone().applyMatrix4(o.matrixWorld);bounds.push([q.min.x,q.min.z,q.max.x,q.max.z]);}});
 for(const q of bounds)if(q[0]<4.5-1e-6||q[1]<4.5-1e-6||q[2]>5.5+1e-6||q[3]>5.5+1e-6)throw Error(JSON.stringify({kind,front,attached,bounds:q}));
 if(JSON.stringify(state)!==before)throw Error('model mutation');scene.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});cases++;
}
console.log('PASS',cases,'kind/orientation/attachment envelopes, original state unchanged');

fs.rmSync(tmp,{recursive:true});
