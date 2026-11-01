import * as THREE from './vendor/three-0.160.1.module.js';
if(new URLSearchParams(location.search).get('cityArt')==='webgl'){
 const start=()=>{const state=window.__cityVisualSnapshot?.();if(!state||!state.paused){setTimeout(start,100);return;}build(state);};start();
}
function build(state){
 const base=document.querySelector('canvas'),bounds=base.getBoundingClientRect(),renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
 renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(bounds.width,bounds.height);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
 const canvas=renderer.domElement;canvas.id='webglTaste';Object.assign(canvas.style,{position:'fixed',left:bounds.left+'px',top:bounds.top+'px',width:bounds.width+'px',height:bounds.height+'px',zIndex:'2',pointerEvents:'none'});document.body.append(canvas);
 const scene=new THREE.Scene();scene.background=new THREE.Color('#b8c9c9');scene.fog=new THREE.Fog('#b8c9c9',65,120);
 const cx=state.center.x,cz=state.center.y,extent=10;
 const camera=new THREE.OrthographicCamera(-extent*bounds.width/bounds.height,extent*bounds.width/bounds.height,extent,-extent,.1,150);camera.position.set(cx+26,30,cz+26);camera.lookAt(cx,0,cz);
 scene.add(new THREE.HemisphereLight('#d9edff','#5e684a',1.8));const sun=new THREE.DirectionalLight('#ffe0b0',4);sun.position.set(cx-15,24,cz+6);sun.target.position.set(cx,0,cz);scene.add(sun,sun.target);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-23,right:23,top:23,bottom:-23,near:1,far:65});sun.shadow.normalBias=.025;sun.shadow.bias=-.00015;sun.shadow.radius=4;
 const batches=new Map(),cube=new THREE.BoxGeometry(1,1,1),dummy=new THREE.Object3D();
 function box(x,y,z,w,h,d,color,rough=.85){const key=color+':'+rough;if(!batches.has(key))batches.set(key,{mat:new THREE.MeshStandardMaterial({color,roughness:rough}),poses:[]});batches.get(key).poses.push([x,y,z,w,h,d]);}
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(70,70),new THREE.MeshStandardMaterial({color:'#82966b',roughness:1}));ground.rotation.x=-Math.PI/2;ground.position.set(cx,-.045,cz);ground.receiveShadow=true;scene.add(ground);
 const roofGeo=new THREE.BufferGeometry();const vertices=[-.5,0,-.5,.5,0,-.5,0,.5,-.5,-.5,0,.5,0,.5,.5,.5,0,.5,-.5,0,-.5,0,.5,-.5,0,.5,.5,-.5,0,-.5,0,.5,.5,-.5,0,.5,.5,0,-.5,.5,0,.5,0,.5,.5,.5,0,-.5,0,.5,.5,0,.5,-.5];roofGeo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));roofGeo.computeVertexNormals();
 const roofs=['#596871','#8c4e39','#668579','#464f5b'];const walls=['#e0cfaf','#b98d73','#d5d3bd','#a4b7ad','#c5a77d'];
 function roof(x,y,z,w,d,id){const m=new THREE.Mesh(roofGeo,new THREE.MeshStandardMaterial({color:roofs[id%4],roughness:.82,side:THREE.DoubleSide}));m.position.set(x,y,z);m.scale.set(w,.85,d);m.castShadow=true;m.receiveShadow=true;scene.add(m);box(x,y-.035,z,w,.10,d,'#635e51');
 // Individual standing seams carry a real roof pitch rather than a flat cap.
 for(let k=-.36;k<.4;k+=.18){box(x+k*w,y+.20,z-d*.25,.018,.025,d*.47,roofs[id%4]);}
 }
 const occupied=new Set(state.buildings.flatMap(b=>b.footprint));
 for(let z=cz-17;z<=cz+17;z++)for(let x=cx-17;x<=cx+17;x++){
  if(x<0||z<0||x>=state.size||z>=state.size)continue;const id=z*state.size+x,t=state.tiles[id];
  if(t===1||t===4){box(x,.015,z,1,.05,1,'#bcbba8');box(x,.05,z,.78,.05,.78,'#596769');for(const [dx,dz] of [[1,0],[0,1]]){if(state.tiles[id+dx+dz*state.size]===1){box(x+dx*.5,.05,z+dz*.5,dx?.98:.78,.05,dz?.98:.78,'#596769');}}}
  if(t===2){box(x,-.015,z,1,.04,1,'#528e99',.27);}
  if(t===3&&!occupied.has(id)&&id%3===0){tree(x,z,id);}
 }
 function tree(x,z,id){const trunk=new THREE.Mesh(new THREE.CylinderGeometry(.065,.10,1.2,6),new THREE.MeshStandardMaterial({color:'#75604a'}));trunk.position.set(x,.6,z);trunk.castShadow=true;scene.add(trunk);for(let j=0;j<5;j++){const mat=new THREE.MeshStandardMaterial({color:['#527a48','#648d50','#7b9b5d'][j%3],roughness:1});const crown=new THREE.Mesh(new THREE.IcosahedronGeometry(.5+(j%2)*.13,1),mat);crown.position.set(x+Math.sin(id+j*2)*.32,1.3+j*.13,z+Math.cos(id+j*2)*.32);crown.scale.y=.8;crown.castShadow=true;crown.receiveShadow=true;scene.add(crown);}}
 for(const b of state.buildings){if(Math.abs(b.x-cx)>15||Math.abs(b.y-cz)>15)continue;const xs=b.footprint.map(i=>i%state.size),zs=b.footprint.map(i=>Math.floor(i/state.size)),w=Math.max(...xs)-Math.min(...xs)+1,d=Math.max(...zs)-Math.min(...zs)+1,x=b.x+(w-1)/2,z=b.y+(d-1)/2,home=b.kind==='home',industrial=['factory','mill','sawmill','warehouse'].includes(b.kind),civic=['townhall','school','clinic','police','fire'].includes(b.kind),floors=home?(b.id%4===0?2:1):b.kind==='office'?3:2,h=floors*.72,W=w*.79,D=d*.75,color=walls[b.id%walls.length];
  box(x,.035,z,w*.94,.07,d*.94,'#a3a590');box(x,h/2+.08,z,W,h,D,color);box(x,.14,z,W+.035,.15,D+.035,'#8d8e7a');
  roof(x,h+.08,z,W+.14,D+.17,b.id);box(x+W*.23,h+.47,z-D*.15,.13,.65,.14,'#9b846a');
  for(let f=0;f<floors;f++)for(let j=0;j<Math.max(2,Math.floor(W/.36));j++){const xx=x-W*.34+j*W*.34,yy=.42+f*.72;box(xx,yy,z+D/2+.018,.20,.31,.035,'#e6d9bd');box(xx,yy+.015,z+D/2+.04,.145,.235,.025,'#496b7b',.25);box(xx,yy-.17,z+D/2+.06,.24,.045,.11,'#c4b899');}
  for(let f=0;f<floors;f++)for(let j=0;j<2;j++){const zz=z-D*.25+j*D*.5,yy=.42+f*.72;box(x+W/2+.02,yy,zz,.035,.30,.19,'#e1d5bb');box(x+W/2+.045,yy,zz,.025,.23,.13,'#456776',.25);}
  box(x,.30,z+D/2+.04,.18,.48,.08,'#554e40');box(x,.055,z+D/2+.17,.32,.1,.25,'#bbb29c');
  if(civic){box(x,h+.6,z,.38,1,.38,color);roof(x,h+1.1,z,.49,.49,b.id);}
  if(!home&&!industrial){box(x,.55,z+D/2+.15,W*.8,.08,.30,['#4f766a','#a06543','#6b6374'][b.id%3]);}
  if(home&&b.id%3===0)tree(x-W*.58,z-D*.32,b.id);
 }
 for(const {mat,poses} of batches.values()){const mesh=new THREE.InstancedMesh(cube,mat,poses.length);poses.forEach((p,i)=>{dummy.position.set(p[0],p[1],p[2]);dummy.scale.set(p[3],p[4],p[5]);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);});mesh.castShadow=true;mesh.receiveShadow=true;scene.add(mesh);}
 const samples=[];let count=0;function frame(){const t=performance.now();renderer.render(scene,camera);samples.push(performance.now()-t);if(samples.length>120)samples.shift();window.__webglTaste={source:'three0.160.1',stateBefore:{day:state.day,total:state.total,rng:state.rng},stateNow:()=>window.__cityVisualSnapshot(),samples,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,renderer:renderer.getContext().getParameter(renderer.getContext().RENDERER)};if(++count<180)requestAnimationFrame(frame);}frame();
}
