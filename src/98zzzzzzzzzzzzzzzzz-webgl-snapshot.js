// Read-only adapter for an opt-in renderer experiment. No simulation clock writes.
window.__cityVisualSnapshot=()=>{if(!G)return null;const hall=G.buildings.find(b=>b.kind==='townhall')||{x:28,y:28};return {paused,day:G.day,population:G.stats.population,treasury:G.treasury,total:totalMoney(),rng:rngState,size:T,center:{x:hall.x,y:hall.y},tiles:G.tiles.slice(),buildings:G.buildings.map(b=>({id:b.id,x:b.x,y:b.y,kind:b.kind,condition:b.condition,footprint:footprintOf(b).slice()})),bridges:typeof bridgeRenderSnapshot==='function'?bridgeRenderSnapshot():[]};};

window.__cityVisualSave=()=>save();
