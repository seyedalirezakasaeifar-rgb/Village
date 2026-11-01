// Committed read projection and existing-action adapter for an opt-in renderer.
window.__cityVisualSnapshot=()=>{if(!G||simulationBusy)return null;const hall=G.buildings.find(b=>b.kind==='townhall')||{x:28,y:28};return {revision:window.__cityVisualRevision(),paused,day:G.day,population:G.stats.population,treasury:G.treasury,total:totalMoney(),rng:rngState,size:T,center:{x:hall.x,y:hall.y},tiles:G.tiles.slice(),buildings:G.buildings.map(b=>({id:b.id,x:b.x,y:b.y,kind:b.kind,condition:b.condition,footprint:footprintOf(b).slice()})),bridges:typeof bridgeRenderSnapshot==='function'?bridgeRenderSnapshot():[]};};

window.__cityVisualSave=()=>save();

window.__cityVisualRevision=()=>G&&!simulationBusy?[G.day,G.construction,roadsVersion,G.bridgeRevision||0].join(':'):'';
window.__cityVisualTap=(x,y)=>{if(!G||simulationBusy||!Number.isInteger(x)||!Number.isInteger(y)||x<0||y<0||x>=T||y>=T)return false;const p=roadCenter(roadId(x,y)),r=cv.getBoundingClientRect();onTap(r.left+cw/2+(p[0]-cam.x)*cam.zoom,r.top+ch/2+(p[1]-cam.y)*cam.zoom);return true;};
