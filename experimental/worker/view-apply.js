// Stages a full immutable successor. The old complete view remains visible until adoption.
async function applyCanonicalDelta(base,patches,yieldTask){
 if(!base||!Object.isFrozen(base)||!Array.isArray(patches))throw Error('Invalid canonical delta base');
 const copies=new Map();let root=base,deadline=performance.now()+3;
 const copy=value=>{if(value===null||typeof value!=='object')throw Error('Delta parent is not a container');if(copies.has(value))return copies.get(value);const result=Array.isArray(value)?value.slice():{...value};copies.set(value,result);copies.set(result,result);return result;};
 for(const patch of patches){if(!Array.isArray(patch.path)||patch.path.length>80)throw Error('Invalid delta path');if(!patch.path.length){if(patch.remove||patch.length!==undefined)throw Error('Invalid delta root');root=patch.value;continue;}
  root=copy(root);let at=root;
  for(let i=0;i<patch.path.length-1;i++){const key=patch.path[i];if(typeof key!=='string'&&(!Number.isSafeInteger(key)||key<0))throw Error('Invalid delta key');if(!Object.prototype.hasOwnProperty.call(at,key))throw Error('Missing delta parent');const child=copy(at[key]);Object.defineProperty(at,key,{value:child,writable:true,enumerable:true,configurable:true});at=child;}
  const key=patch.path[patch.path.length-1];if(patch.length!==undefined){if(!Number.isSafeInteger(patch.length)||patch.length<0)throw Error('Invalid delta array length');const target=copy(at[key]);if(!Array.isArray(target))throw Error('Delta length target is not an array');target.length=patch.length;Object.defineProperty(at,key,{value:target,writable:true,enumerable:true,configurable:true});}
  else if(patch.remove)delete at[key];else Object.defineProperty(at,key,{value:patch.value,writable:true,enumerable:true,configurable:true});
  if(performance.now()>deadline){await yieldTask();deadline=performance.now()+3;}
 }
 // Freeze only newly copied/received objects; unchanged immutable subtrees are shared.
 const stack=[root];while(stack.length){const value=stack.pop();if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.freeze(value);for(const child of Object.values(value))stack.push(child);}if(performance.now()>deadline){await yieldTask();deadline=performance.now()+3;}}
 return root;
}
