// Experimental wire-only codec. No saved preference; production remains disabled.
const INACTIVE_CODEC_LIMITS=Object.freeze({bytes:8*1024*1024,logicalBytes:16*1024*1024,active:8000,inactive:16000,total:24000,entityActive:3000,entityInactive:6000,entityTotal:9000,fields:64,entityFields:128,cells:500000,nodes:1000000,depth:24});
let inactivePersonCodecEnabled=false;
function inactiveCodecCooperative(){return typeof cooperativeDayBusy==='function';}
function inactiveCodecBudget(value){let nodes=0;function visit(v,depth){if(++nodes>INACTIVE_CODEC_LIMITS.nodes||depth>INACTIVE_CODEC_LIMITS.depth)throw Error('Inactive identity expansion budget exceeded');if(typeof v==='number'&&!Number.isFinite(v))throw Error('Nonfinite identity value');if(v&&typeof v==='object')for(const key in v)if(owns(v,key))visit(v[key],depth+1);}visit(value,0);}
function historicalEntity(kind,row){return kind==='households'?Array.isArray(row?.people)&&row.people.length===0:row?.closed===true&&row.demolished===true;}
function encodeHistoricalEntity(kind,all){
 const lim=INACTIVE_CODEC_LIMITS;if(!Array.isArray(all)||all.length>lim.entityTotal||all.some((r,i)=>!r||r.id!==i))throw Error('Entity directory capacity exceeded');
 const history=all.filter(r=>historicalEntity(kind,r)),active=all.filter(r=>!historicalEntity(kind,r)),fields=[...new Set(history.flatMap(r=>Object.keys(r).filter(k=>k!=='id')))].sort();
 return {active,packed:{total:all.length,fields,rows:history.map(r=>{const indices=fields.map((k,i)=>owns(r,k)?i:-1).filter(i=>i>=0);return [r.id,indices,indices.map(i=>r[fields[i]])];})}};
}
function decodeHistoricalEntity(kind,active,packed,shared){
 const lim=INACTIVE_CODEC_LIMITS;
 if(!packed||!Number.isSafeInteger(packed.total)||packed.total<0||packed.total>lim.entityTotal||!Array.isArray(active)||active.length>lim.entityActive||!Array.isArray(packed.rows)||packed.rows.length>lim.entityInactive||active.length+packed.rows.length!==packed.total||!Array.isArray(packed.fields)||packed.fields.length>lim.entityFields||new Set(packed.fields).size!==packed.fields.length||packed.fields.some((k,i)=>typeof k!=='string'||k.length>128||k==='id'||i&&k<=packed.fields[i-1]))throw Error('Malformed historical '+kind+' directory');
 shared.expansion+=packed.total*16;if(shared.expansion>lim.logicalBytes)throw Error('Decoded archive expansion budget exceeded');
 const records=new Array(packed.total),seen=new Set(),keyBytes=packed.fields.map(k=>new Blob([JSON.stringify(k)]).size),put=r=>{if(!r||!Number.isSafeInteger(r.id)||r.id<0||r.id>=packed.total||seen.has(r.id))throw Error('Duplicate historical entity ID');seen.add(r.id);records[r.id]=r;};
 for(const r of active){if(historicalEntity(kind,r))throw Error('Historical entity in active section');put(r);}
 for(const row of packed.rows){if(!Array.isArray(row)||row.length!==3||!Array.isArray(row[1])||!Array.isArray(row[2])||row[1].length!==row[2].length||(shared.cells+=row[1].length)>lim.cells)throw Error('Malformed historical entity row');const r={id:row[0]};for(let i=0;i<row[1].length;i++){const at=row[1][i];if(!Number.isSafeInteger(at)||at<0||at>=packed.fields.length||i&&at<=row[1][i-1])throw Error('Invalid historical entity field index');shared.expansion+=keyBytes[at]+3;if(shared.expansion>lim.logicalBytes)throw Error('Decoded archive expansion budget exceeded');Object.defineProperty(r,packed.fields[at],{value:row[2][i],writable:true,enumerable:true,configurable:true});}if(!historicalEntity(kind,r))throw Error('Active entity hidden in history');put(r);}
 if(seen.size!==packed.total)throw Error('Historical entity directory has holes');return records;
}
function decodeInactiveEnvelope(wire,encodedBytes){
 const lim=INACTIVE_CODEC_LIMITS;
 if(!inactivePersonCodecEnabled)throw Error('Experimental inactive identity codec is disabled');
 if(!wire||wire.format!=='TownLedgerInactivePeople'||![1,2].includes(wire.version)||wire.schema!==9||wire.logicalSchema!==8||!wire.payload||wire.payload.schema!==9)throw Error('Unsupported inactive identity format');
 const packed=wire.inactive,data=wire.payload;
 if(!packed||!Number.isSafeInteger(packed.total)||packed.total<1||packed.total>lim.total||!Array.isArray(packed.fields)||packed.fields.length>lim.fields||new Set(packed.fields).size!==packed.fields.length||packed.fields.some((k,i)=>typeof k!=='string'||k.length>128||k==='id'||i&&k<=packed.fields[i-1])||!Array.isArray(packed.rows)||packed.rows.length>lim.inactive||!Array.isArray(data.people)||data.people.length>lim.active||data.people.length+packed.rows.length!==packed.total)throw Error('Malformed inactive identity directory');
 inactiveCodecBudget(wire);
 const shared={cells:0,expansion:(encodedBytes??new Blob([JSON.stringify(wire)]).size)+packed.total*16};
 if(wire.version===2){if(!wire.entities||Object.keys(wire.entities).sort().join(',')!=='firms,households')throw Error('Malformed estate directory');for(const kind of ['households','firms'])data[kind]=decodeHistoricalEntity(kind,data[kind],wire.entities[kind],shared);}else if(wire.entities!=null)throw Error('Unexpected estate directory');
 const keyBytes=packed.fields.map(k=>new Blob([JSON.stringify(k)]).size),people=new Array(packed.total),seen=new Set();let cells=shared.cells,expansion=shared.expansion;if(expansion>lim.logicalBytes)throw Error('Decoded archive expansion budget exceeded');
 const put=p=>{if(!p||!Number.isSafeInteger(p.id)||p.id<0||p.id>=packed.total||seen.has(p.id))throw Error('Duplicate or invalid person ID');seen.add(p.id);people[p.id]=p;};
 for(const p of data.people){if(p.deceased===true||p.movedAway===true)throw Error('Inactive person in active section');put(p);}
 for(const row of packed.rows){if(!Array.isArray(row)||row.length!==3||!Array.isArray(row[1])||!Array.isArray(row[2])||row[1].length!==row[2].length||(cells+=row[1].length)>lim.cells)throw Error('Malformed identity row');const p={id:row[0]};for(let i=0;i<row[1].length;i++){const at=row[1][i];if(!Number.isSafeInteger(at)||at<0||at>=packed.fields.length||i&&at<=row[1][i-1])throw Error('Invalid identity field index');expansion+=keyBytes[at]+3;if(expansion>lim.logicalBytes)throw Error('Decoded archive expansion budget exceeded');Object.defineProperty(p,packed.fields[at],{value:row[2][i],writable:true,enumerable:true,configurable:true});}if(p.deceased!==true&&p.movedAway!==true)throw Error('Active person hidden in history');put(p);}
 if(seen.size!==packed.total)throw Error('Identity directory has holes');
 for(const p of people)if(!Number.isInteger(p.hh)||!data.households?.[p.hh]||!Number.isFinite(p.age))throw Error('Invalid identity/estate reference');
 data.people=people;data.schema=wire.logicalSchema;return data;
}
function parseArchiveWithInactiveCodec(raw){
 const text=typeof raw==='string'?raw:JSON.stringify(raw);
 if(inactivePersonCodecEnabled&&(text.length>INACTIVE_CODEC_LIMITS.bytes||new Blob([text]).size>INACTIVE_CODEC_LIMITS.bytes))throw Error('Archive exceeds encoded byte budget');
 const value=JSON.parse(text);if(value?.format!=='TownLedgerInactivePeople')return {data:value,extended:false};
 return {data:decodeInactiveEnvelope(value,new Blob([text]).size),extended:true,entitiesExtended:value.version===2};
}
const archiveLogicalPayload=archivePayload;
archivePayload=function(){
 const text=archiveLogicalPayload();if(!inactivePersonCodecEnabled)return text;
 if(inactiveCodecCooperative())throw Error('Inactive identity codec requires cooperative snapshot integration');
 const data=JSON.parse(text),all=data.people;if(!Array.isArray(all)||all.length>INACTIVE_CODEC_LIMITS.total||all.some((p,i)=>!p||p.id!==i))throw Error('Identity directory capacity exceeded');
 const inactive=all.filter(p=>p.deceased===true||p.movedAway===true),active=all.filter(p=>p.deceased!==true&&p.movedAway!==true),fields=[...new Set(inactive.flatMap(p=>Object.keys(p).filter(k=>k!=='id')))].sort();
 data.people=active;const logicalSchema=data.schema;data.schema=9;
 const wire={format:'TownLedgerInactivePeople',version:2,schema:9,logicalSchema,payload:data,inactive:{total:all.length,fields,rows:inactive.map(p=>{const indices=fields.map((k,i)=>owns(p,k)?i:-1).filter(i=>i>=0);return [p.id,indices,indices.map(i=>p[fields[i]])];})}};
 wire.entities={};for(const kind of ['households','firms']){const directory=encodeHistoricalEntity(kind,data[kind]);wire.entities[kind]=directory.packed;data[kind]=directory.active;}
 // The wire is detached from live state by the original logical JSON parse.
 // Validate this private candidate directly, avoiding a second full wire parse.
 // Independent serialization round-trip equivalence is covered by codec gates.
 const encoded=JSON.stringify(wire),encodedBytes=new Blob([encoded]).size;if(encoded.length>INACTIVE_CODEC_LIMITS.bytes||encodedBytes>INACTIVE_CODEC_LIMITS.bytes)throw Error('Archive exceeds encoded byte budget');decodeInactiveEnvelope(wire,encodedBytes);return encoded;
};
window.__inactivePersonCodec={enable:enabled=>{if(enabled===true&&inactiveCodecCooperative())throw Error('Cooperative snapshot contract is not integrated');if(enabled!==true&&inactivePersonCodecEnabled&&G&&(G.people.length>8000||G.households.length>3000||G.firms.length>3000))throw Error('Load a legacy-sized town or found another before disabling its required identity codec');inactivePersonCodecEnabled=enabled===true;return inactivePersonCodecEnabled;},status:()=>({enabled:inactivePersonCodecEnabled,limits:INACTIVE_CODEC_LIMITS,wireSchema:9,wireVersion:2})};
