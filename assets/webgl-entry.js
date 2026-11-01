// Normal release has no diagnostic badge. Explicit QA identification changes no tier/state.
const cityEntryParams=new URLSearchParams(location.search);
if(cityEntryParams.get('cityBadge')==='1'){
 const b=document.createElement('div');b.id='cityRendererIdentity';b.textContent='QA · Canvas mode · awaiting 3D';Object.assign(b.style,{position:'fixed',left:'8px',top:'72px',zIndex:10000,pointerEvents:'none',font:'12px monospace',padding:'6px',color:'#fff',background:'#263b42'});document.body.append(b);window.__cityRendererStatus=text=>{b.textContent='QA · '+text;};
}
if(cityEntryParams.get('cityArt')==='webgl'){
 window.__cityRendererStatus?.('loading WebGL module');import('./webgl-taste.js').catch(error=>{window.__webglTasteFailure=String(error);window.__cityRendererStatus?.('Canvas fallback · module failed');console.warn('WebGL preview could not load; Canvas remains active.',error);});
}

// An explicit preference change can retry 3D after automatic/context fallback.
document.addEventListener('change',e=>{if(cityEntryParams.get('cityArt')==='webgl'&&e.target.dataset.preference==='quality'&&!window.__webglTaste)setTimeout(()=>window.__cityRetry3D?.(),0);});
