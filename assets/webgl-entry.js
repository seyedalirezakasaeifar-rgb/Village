// QA probe is explicit and absent from the normal release interface.
const cityEntryParams=new URLSearchParams(location.search),cityProbe=cityEntryParams.get('cityProbe')==='1';
const cityLoad3D=()=>import('./webgl-taste.js').catch(error=>{window.__webglTasteFailure=String(error);window.__cityProbeStatus?.('Canvas fallback: module failed');console.warn('WebGL preview could not load; Canvas remains active.',error);});
if(cityProbe){
 const badge=document.createElement('button');badge.id='cityRendererProbe';badge.textContent='QA · Canvas · Start paused 3D';Object.assign(badge.style,{position:'fixed',left:'8px',top:'72px',zIndex:10000,font:'12px monospace',padding:'8px',color:'#fff',background:'#263b42',border:'2px solid #ddbf65'});document.body.append(badge);
 window.__cityProbeStatus=text=>{badge.textContent='QA · '+text;};
 badge.onclick=()=>{const s=window.__cityVisualSnapshot?.();if(!s){window.__cityProbeStatus('Canvas · create/continue town first');return;}if(!s.paused)document.getElementById('pause').click();badge.onclick=null;window.__cityProbeStatus('paused · loading 3D modules');cityLoad3D();};
}else if(cityEntryParams.get('cityArt')==='webgl')cityLoad3D();
