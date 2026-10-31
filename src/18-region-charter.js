// The original 56×56 town keeps every existing right. Five real outer districts
// extend the region to 80×80; undeveloped regional land requires a mayoral deed.
const CHARTER_BASE=56;
let parcelFocus=null;
const ANNEX_PARCELS=[
 {id:'east-meadow',name:'East Meadow',x:56,y:2,w:22,h:26,description:'A large eastern tract with woodland and lake frontage.'},
 {id:'county-ridge',name:'County Ridge',x:56,y:28,w:22,h:28,description:'Eastern upland for a new connected district.'},
 {id:'river-reach',name:'Lower River Reach',x:2,y:56,w:26,h:22,description:'New southern riverbank, suitable for working waterfronts.'},
 {id:'orchard-downs',name:'Orchard Downs',x:28,y:56,w:28,h:22,description:'A substantial southern tract for homes, farms and civic sites.'},
 {id:'high-common',name:'High Common',x:56,y:56,w:22,h:22,description:'The far southeastern common, reached through an adjoining district.'}
];
function newCharter(){return {version:1,owned:[],deeds:[],revision:0};}
function regionalTerrain(x,y,seedValue){
 if(x<5+Math.sin(y*.2)*1.7||x===5&&y%4===0)return 2;
 if(x>=56&&((x-66)*(x-66)/36+(y-22)*(y-22)/64)<1)return 2;
 return hash((y*T+x)^((seedValue||42)>>>0))%100<31?3:0;
}
function parcelForTile(x,y){return ANNEX_PARCELS.find(p=>x>=p.x&&x<p.x+p.w&&y>=p.y&&y<p.y+p.h)||null;}
function charterOwns(x,y){if(x<0||y<0||x>=T||y>=T)return false;if(x<CHARTER_BASE&&y<CHARTER_BASE)return true;const p=parcelForTile(x,y);return !!p&&!!G.charter?.owned.includes(p.id);}
function charterFootprint(x,y,kind){return footprintFor(x,y,kind).every(id=>charterOwns(id%T,id/T|0));}
function charterRoadCount(){const privateSet=new Set(G.privateRoads||[]);return [...graph().neighbors.keys()].filter(id=>!privateSet.has(id)&&charterOwns(id%T,id/T|0)).length;}
function parcelSurvey(p){let land=0,water=0,forest=0,roads=0;for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++){const cell=G.tiles[roadId(x,y)];if(cell===2)water++;else{land++;if(cell===3)forest++;if(cell===1)roads++;}}return {land,water,forest,roads,area:p.w*p.h,price:12000+land*42+roads*75};}
function parcelAdjacent(p){const owned=G.charter?.owned||[];return p.x===56&&p.y<56||p.y===56&&p.x<56||ANNEX_PARCELS.some(q=>owned.includes(q.id)&&((q.x+q.w===p.x||p.x+p.w===q.x)&&Math.max(q.y,p.y)<Math.min(q.y+q.h,p.y+p.h)||(q.y+q.h===p.y||p.y+p.h===q.y)&&Math.max(q.x,p.x)<Math.min(q.x+q.w,p.x+p.w)));}
function purchaseParcel(id,quotedPrice){
 const p=ANNEX_PARCELS.find(p=>p.id===id);if(!p||!G.charter||G.charter.owned.includes(id)||!parcelAdjacent(p))return false;const quote=parcelSurvey(p);if(!Number.isFinite(quotedPrice)||quotedPrice!==quote.price||G.treasury<quote.price)return false;
 G.treasury-=quote.price;G.region+=quote.price;G.charter.owned.push(id);G.charter.deeds.push({id,price:quote.price,day:G.day});G.charter.revision++;G.cumulative.landPurchases=(G.cumulative.landPurchases||0)+quote.price;
 book('Municipal land budget','Regional land authority',quote.price,'Annexation deed: '+p.name);G.journal.push({day:G.day,name:'District annexed',message:p.name+': '+quote.area+' new regional tiles, '+quote.land+' land tiles. Development rights purchased for '+money(quote.price)+'. Existing private titles are unchanged.',baseline:{...G.stats,treasury:G.treasury}});
 story('The mayor acquired '+p.name+'. Roads and service coverage must still be developed.','good');invalidateRoads(false);staticDirty=true;dirty=true;updateHeader();save();return true;
}
function validateCharter(data){
 const c=data.charter;if(!c||c.version!==1||!Array.isArray(c.owned)||new Set(c.owned).size!==c.owned.length||c.owned.some(id=>!ANNEX_PARCELS.some(p=>p.id===id))||!Array.isArray(c.deeds)||c.deeds.length!==c.owned.length||!Number.isInteger(c.revision)||c.revision!==c.owned.length)return false;
 const seen=new Set();for(const d of c.deeds){if(!d||seen.has(d.id)||!c.owned.includes(d.id)||!Number.isInteger(d.day)||d.day<1||d.day>data.day||!Number.isFinite(d.price)||d.price<12000||d.price>100000)return false;seen.add(d.id);}
 const ownsTile=(id)=>{const x=id%T,y=id/T|0;if(x<CHARTER_BASE&&y<CHARTER_BASE)return true;const p=parcelForTile(x,y);return !!p&&c.owned.includes(p.id);};
 if(data.tiles.some((type,id)=>type===1&&!ownsTile(id)))return false;
 if(data.buildings.some(b=>(b.footprint||[b.y*T+b.x]).some(id=>!ownsTile(id))))return false;
 if(Object.keys(data.landUse||{}).some(id=>!ownsTile(+id))||(data.privateRoads||[]).some(id=>!ownsTile(id)))return false;
 if(c.owned.includes('high-common')&&!c.owned.some(id=>id==='county-ridge'||id==='orchard-downs'))return false;
 return true;
}
function normalizeRegionArchive(input){
 if(!input||!Array.isArray(input.tiles))return input;
 if(input.tiles.length===T*T){if(input.gridSize!==T)return null;return input;}
 if(input.tiles.length!==CHARTER_BASE*CHARTER_BASE||(input.gridSize!=null&&input.gridSize!==CHARTER_BASE))return null;
 const data=JSON.parse(JSON.stringify(input)),oldSize=CHARTER_BASE,count=oldSize*oldSize;
 const tile=id=>{if(!Number.isInteger(+id)||+id<0||+id>=count)throw Error('Invalid legacy regional tile');return (+id/oldSize|0)*T+(+id%oldSize);};
 const list=a=>a.map(tile),map=object=>Object.fromEntries(Object.entries(object||{}).map(([id,v])=>[tile(id),v]));
 const tiles=Array.from({length:T*T},(_,id)=>regionalTerrain(id%T,id/T|0,data.worldSeed||data.scenarioSeed));for(let y=0;y<oldSize;y++)for(let x=0;x<oldSize;x++)tiles[y*T+x]=data.tiles[y*oldSize+x];data.tiles=tiles;
 for(const b of data.buildings||[])if(Array.isArray(b.footprint))b.footprint=list(b.footprint);
 for(const key of ['roadClasses','streetNames','landUse','fieldOwner'])if(data[key])data[key]=map(data[key]);
 if(Array.isArray(data.roadWear)){const wear=new Array(T*T).fill(100);for(let id=0;id<Math.min(count,data.roadWear.length);id++)wear[tile(id)]=data.roadWear[id];data.roadWear=wear;}
 if(Array.isArray(data.privateRoads))data.privateRoads=list(data.privateRoads);
 for(const p of data.projects||[])for(const key of ['plots','runway'])if(Array.isArray(p[key]))p[key]=list(p[key]);
 if(data.airport?.runway)data.airport.runway=list(data.airport.runway);
 for(const s of data.freight||[])if(Array.isArray(s.path))s.path=list(s.path);
 for(const v of data.trafficState?.vehicles||[])if(Array.isArray(v.path))v.path=list(v.path);
 if(data.trafficState)data.trafficState.gates=[];
 data.gridSize=T;data.charter=newCharter();return data;
}
function centerTownCamera(zoom=.95){const hall=G.buildings.find(b=>b.kind==='townhall')||{x:28,y:28};const p=iso(hall.x+1,hall.y+1);cam={x:p[0],y:p[1]+28,zoom};dirty=true;}
