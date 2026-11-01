// Read-only QA observations and map projection only. No simulation/financial work.
window.__playerJourney={
 day:()=>G.day,
 title:tab=>names[tab],
 state:()=>{const text=JSON.stringify(G),rng=rngState,valid=validateTown(),total=totalMoney(),goods=goodsBalance();if(text!==JSON.stringify(G)||rng!==rngState)throw Error('Observer changed authority');return{day:G.day,paused,speed,total,treasury:G.treasury,region:G.region,construction:G.construction,owned:G.charter.owned.slice(),programmes:JSON.parse(JSON.stringify(G.districtProgrammes||{})),routes:JSON.parse(JSON.stringify(G.transit?.routes||[])),transitCapital:G.transit?.capital||0,contracts:JSON.parse(JSON.stringify(G.regionalTrade?.contracts||[])),cargo:G.regionalTrade?.shipments.length||0,priority:G.regionalTrade?.priority,reliefUntil:G.regionalTrade?.reliefUntil,buildings:G.buildings.length,projects:G.projects.length,population:G.stats.population,valid,goodsMax:Math.max(0,...goods.map(g=>Math.abs(g.error))),active,buildMode,toast:$('toast').textContent};},
 site:(kind,near=null)=>{const text=JSON.stringify(G),rng=rngState,net=graph();let result=null;for(let y=3;y<T-3&&!result;y++)for(let x=3;x<T-3;x++){const distance=near?Math.abs(x-near.x)+Math.abs(y-near.y):0;if(near&&(distance<10||distance>20))continue;if(canPlace(x,y,true,kind)&&roadOffsets.some(([dx,dy])=>net.parts[roadId(x+dx,y+dy)]===net.mainPart)){result={x,y,kind};break;}}if(text!==JSON.stringify(G)||rng!==rngState)throw Error('Site observation changed authority');return result;},
 parcel:()=>ANNEX_PARCELS.filter(p=>!G.charter.owned.includes(p.id)&&parcelAdjacent(p)).map(p=>({id:p.id,price:parcelSurvey(p).price})).find(p=>G.treasury>p.price+100000),
 farm:()=>{const text=JSON.stringify(G),rng=rngState;const rows=G.firms.filter(f=>f.kind==='farm'&&!f.closed).map(f=>{const b=readBuild(f.building);return{id:f.id,building:b.id,x:b.x,y:b.y,density:urbanDescriptor(b.x,b.y).density};}).sort((a,b)=>b.density-a.density||a.id-b.id);if(text!==JSON.stringify(G)||rng!==rngState)throw Error('Farm observation changed authority');return rows[0]||null;},
 at:(x,y)=>{const b=buildingAt(x,y);return b?{id:b.id,kind:b.kind,x:b.x,y:b.y}:null;},
 world:(x,y)=>{const p=iso(x,y);return{x:p[0],y:p[1]+TH/2,zoom:.8};},
 point:(x,y)=>{const p=iso(x,y),r=cv.getBoundingClientRect(),sx=cw/2+(p[0]-cam.x)*cam.zoom,sy=ch/2+(p[1]+TH/2-cam.y)*cam.zoom;return{x:r.left+sx,y:r.top+sy,decoded:toWorld(sx,sy)};},
 cargo:id=>({active:!!G.regionalTrade?.shipments.some(o=>o.id===id),recent:!!G.regionalTrade?.recent.some(o=>o.id===id)}),
 bytes:()=>JSON.stringify(G).length,
 waitSaves:async()=>{await saveStorePromise;await saveWrites;}
};
