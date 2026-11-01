// Keep the synchronous Canvas fallback free of the optional 3D dependency.
if(new URLSearchParams(location.search).get('cityArt')==='webgl'){
 import('./webgl-taste.js').catch(error=>{window.__webglTasteFailure=String(error);console.warn('WebGL preview could not load; Canvas remains active.',error);});
}
