// Normal release has no diagnostic badge. Explicit QA identification changes no tier/state.
const cityEntryParams=new URLSearchParams(location.search);
if(cityEntryParams.get('cityBadge')==='1'){
 const b=document.createElement('div');b.id='cityRendererIdentity';b.textContent='QA · Canvas mode · awaiting 3D';Object.assign(b.style,{position:'fixed',left:'8px',top:'72px',zIndex:10000,pointerEvents:'none',font:'12px monospace',padding:'6px',color:'#fff',background:'#263b42'});document.body.append(b);window.__cityRendererStatus=text=>{b.textContent='QA · '+text;};
}
let rendererPreference='canvas';try{rendererPreference=localStorage.getItem('townledger-renderer')==='webgl'?'webgl':'canvas';}catch(_){}
window.__city3DRequested=cityEntryParams.get('cityArt')==='webgl'||rendererPreference==='webgl';
window.__cityRendererPreference=()=>window.__city3DRequested?'webgl':'canvas';
let moduleLoaded=false,loading=null;
function load3D(){if(moduleLoaded){window.__cityRetry3D?.();return;}if(loading)return;window.__cityRendererStatus?.('loading WebGL module');loading=import('./webgl-taste.js').then(()=>{moduleLoaded=true;}).catch(error=>{window.__webglTasteFailure=String(error);window.__cityRendererStatus?.('Canvas fallback · module failed');console.warn('WebGL preview could not load; Canvas remains active.',error);}).finally(()=>{loading=null;});}
if(window.__city3DRequested)load3D();
document.addEventListener('change',e=>{
 if(e.target.dataset.renderer==='city'){
  window.__city3DRequested=e.target.value==='webgl';try{localStorage.setItem('townledger-renderer',window.__city3DRequested?'webgl':'canvas');}catch(_){}
  if(window.__city3DRequested)load3D();else{window.__webglTaste?.dispose();window.__cityVisualResumeCanvas?.();window.__cityRendererStatus?.('Canvas selected');}
 }
 if(window.__city3DRequested&&e.target.dataset.preference==='quality'&&!window.__webglTaste)setTimeout(()=>window.__cityRetry3D?.(),0);
});
