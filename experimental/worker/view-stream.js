// Complete canonical JSON views. Deltas retain every field; no projection/schema truncation.
let workerViewBase=null,workerViewSeq=0;
function workerJsonEqual(a,b){
 const stack=[[a,b]];while(stack.length){const [x,y]=stack.pop();if(x===y)continue;if(x===null||y===null||typeof x!=='object'||typeof y!=='object'||Array.isArray(x)!==Array.isArray(y))return false;if(Array.isArray(x)){if(x.length!==y.length)return false;for(let i=0;i<y.length;i++){if(x[i]===y[i])continue;if(x[i]===null||y[i]===null||typeof x[i]!=='object'||typeof y[i]!=='object')return false;stack.push([x[i],y[i]]);}}else{const keys=Object.keys(y);if(Object.keys(x).length!==keys.length)return false;for(const key of keys){if(!Object.prototype.hasOwnProperty.call(x,key))return false;if(x[key]===y[key])continue;if(x[key]===null||y[key]===null||typeof x[key]!=='object'||typeof y[key]!=='object')return false;stack.push([x[key],y[key]]);}}}return true;
}
function workerJsonDelta(before,after){
 const patches=[],stack=[{a:before,b:after,path:[]}];
 while(stack.length){const {a,b,path}=stack.pop();if(a===b)continue;
  if(a===null||b===null||typeof a!=='object'||typeof b!=='object'||Array.isArray(a)!==Array.isArray(b)){patches.push({path,value:b});continue;}
  // Changed record rows travel intact: leaf paths duplicated tens of thousands
  // of times are larger and substantially slower to stage than complete rows.
  if(path.length>=2&&typeof path[path.length-1]==='number'&&!Array.isArray(b)){if(!workerJsonEqual(a,b))patches.push({path,value:b});continue;}
  if(Array.isArray(b)&&b.every(x=>x===null||typeof x!=='object')&&a.length===b.length){const changed=[];for(let i=0;i<b.length;i++)if(a[i]!==b[i])changed.push(i);if(changed.length>16)patches.push({path,value:b});else for(const i of changed)patches.push({path:path.concat(i),value:b[i]});continue;}
  if(Array.isArray(b)){if(a.length!==b.length)patches.push({path,length:b.length});for(let i=b.length-1;i>=0;i--)if(i>=a.length)patches.push({path:path.concat(i),value:b[i]});else stack.push({a:a[i],b:b[i],path:path.concat(i)});}
  else{for(const key of Object.keys(a))if(!Object.prototype.hasOwnProperty.call(b,key))patches.push({path:path.concat(key),remove:true});for(const key of Object.keys(b)){if(!Object.prototype.hasOwnProperty.call(a,key))patches.push({path:path.concat(key),value:b[key]});else stack.push({a:a[key],b:b[key],path:path.concat(key)});}}
 }return patches;
}
function workerCompleteView(m,projection=false,deliverEffects=true){
 const snapshot=workerSnapshot(projection,deliverEffects);if(!m.publishView||projection)return snapshot;
 const previous=workerViewBase,seq=++workerViewSeq;workerViewBase={epoch:workerEpoch,seq,model:snapshot.model};
 if(m.viewMode==='delta'&&previous?.epoch===workerEpoch&&m.baseViewSeq===previous.seq){const patches=workerJsonDelta(previous.model,snapshot.model);delete snapshot.model;return {...snapshot,view:{format:'json-delta-v1',seq,base:previous.seq,patches}};}
 return {...snapshot,view:{format:'json-full-v1',seq}};
}
