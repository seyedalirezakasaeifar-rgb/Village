// Experimental wire-only codec. No saved preference; production remains disabled.
const INACTIVE_CODEC_LIMITS=Object.freeze({bytes:8*1024*1024,logicalBytes:16*1024*1024,active:8000,inactive:16000,total:24000,entityActive:3000,entityInactive:6000,entityTotal:9000,fields:64,entityFields:128,cells:500000,nodes:1000000,depth:24});
let inactivePersonCodecEnabled=false;
function inactiveCodecCooperative(){return typeof cooperativeDayBusy==='function';}
// Count canonical JSON bytes before allocating reconstructed directories. Raw JSON
// numbers (for example 1e20) may grow when serialized; raw input size is not an
// upper bound. JSON-derived inputs contain only these types. Do not stringify
// the whole decoded object merely to measure it.
function inactiveCodecBudget(value){
 const lim=INACTIVE_CODEC_LIMITS;let nodes=0,bytes=0;
 const add=n=>{bytes+=n;if(bytes>lim.logicalBytes)throw Error('Decoded archive expansion budget exceeded');};
 function stringBytes(s){
  add(2);for(let i=0;i<s.length;i++){const c=s.charCodeAt(i);
   if(c===34||c===92||c===8||c===9||c===10||c===12||c===13)add(2);
   else if(c<32)add(6);
   else if(c<128)add(1);
   else if(c<2048)add(2);
   else if(c>=0xd800&&c<=0xdbff&&i+1<s.length&&s.charCodeAt(i+1)>=0xdc00&&s.charCodeAt(i+1)<=0xdfff){add(4);i++;}
   else if(c>=0xd800&&c<=0xdfff)add(6);
   else add(3);
  }
 }
 function visit(v,depth){
  if(++nodes>lim.nodes||depth>lim.depth)throw Error('Inactive identity expansion budget exceeded');
  if(v===null){add(4);return;}
  if(typeof v==='number'){if(!Number.isFinite(v))throw Error('Nonfinite identity value');add(String(v).length);return;}
  if(typeof v==='string'){stringBytes(v);return;}
  if(typeof v==='boolean'){add(v?4:5);return;}
  if(!v||typeof v!=='object')throw Error('Unsupported identity value');
  add(2);let count=0;
  if(Array.isArray(v)){for(let i=0;i<v.length;i++){if(count++)add(1);visit(v[i],depth+1);}}
  else for(const key in v)if(owns(v,key)){if(count++)add(1);stringBytes(key);add(1);visit(v[key],depth+1);}
 }
 visit(value,0);return bytes;
}
function historicalEntity(kind,row){return kind==='households'?Array.isArray(row?.people)&&row.people.length===0:row?.closed===true&&row.demolished===true;}
function encodeHistoricalEntity(kind,all){
 const lim=INACTIVE_CODEC_LIMITS;if(!Array.isArray(all)||all.length>lim.entityTotal||all.some((r,i)=>!r||r.id!==i))throw Error('Entity directory capacity exceeded');
 const history=all.filter(r=>historicalEntity(kind,r)),active=all.filter(r=>!historicalEntity(kind,r)),fields=[...new Set(history.flatMap(r=>Object.keys(r).filter(k=>k!=='id')))].sort();
 return {active,packed:{total:all.length,fields,rows:history.map(r=>{const indices=fields.map((k,i)=>owns(r,k)?i:-1).filter(i=>i>=0);return [r.id,indices,indices.map(i=>r[fields[i]])];})}};
}
function validateHistoricalEntityDirectory(kind,active,packed){
 const lim=INACTIVE_CODEC_LIMITS;
 if(!packed||!Number.isSafeInteger(packed.total)||packed.total<0||packed.total>lim.entityTotal||!Array.isArray(active)||active.length>lim.entityActive||!Array.isArray(packed.rows)||packed.rows.length>lim.entityInactive||active.length+packed.rows.length!==packed.total||!Array.isArray(packed.fields)||packed.fields.length>lim.entityFields||new Set(packed.fields).size!==packed.fields.length||packed.fields.some((k,i)=>typeof k!=='string'||k.length>128||k==='id'||i&&k<=packed.fields[i-1]))throw Error('Malformed historical '+kind+' directory');
}
// Validate row metadata and charge every repeated key before constructing any
// records. Use a private counter copy so reconstruction retains its own checks.
function preflightIdentityExpansion(packed,shared,entity){
 const lim=INACTIVE_CODEC_LIMITS,label=entity?'historical entity':'identity';
 if(entity)shared.expansion+=packed.total*16;
 if(shared.expansion>lim.logicalBytes)throw Error('Decoded archive expansion budget exceeded');
 const keyBytes=packed.fields.map(k=>new Blob([JSON.stringify(k)]).size);
 for(const row of packed.rows){
  if(!Array.isArray(row)||row.length!==3||!Array.isArray(row[1])||!Array.isArray(row[2])||row[1].length!==row[2].length||(shared.cells+=row[1].length)>lim.cells)throw Error('Malformed '+label+' row');
  for(let i=0;i<row[1].length;i++){const at=row[1][i];
   if(!Number.isSafeInteger(at)||at<0||at>=packed.fields.length||i&&at<=row[1][i-1])throw Error('Invalid '+label+' field index');
   shared.expansion+=keyBytes[at]+3;if(shared.expansion>lim.logicalBytes)throw Error('Decoded archive expansion budget exceeded');
  }
 }
 return keyBytes;
}
function decodeHistoricalEntity(kind,active,packed,shared,keyBytes){
 const lim=INACTIVE_CODEC_LIMITS;
 shared.expansion+=packed.total*16;if(shared.expansion>lim.logicalBytes)throw Error('Decoded archive expansion budget exceeded');
 const records=new Array(packed.total),seen=new Set(),put=r=>{if(!r||!Number.isSafeInteger(r.id)||r.id<0||r.id>=packed.total||seen.has(r.id))throw Error('Duplicate historical entity ID');seen.add(r.id);records[r.id]=r;};
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
 // Reject every directory header before traversing values or reconstructing any
 // other directory. In particular, invalid firm totals must not decode estates.
 if(wire.version===2){
  if(!wire.entities||typeof wire.entities!=='object'||Array.isArray(wire.entities))throw Error('Malformed estate directory');
  let directories=0;for(const kind in wire.entities)if(owns(wire.entities,kind)){if(kind!=='households'&&kind!=='firms')throw Error('Malformed estate directory');directories++;}
  if(directories!==2)throw Error('Malformed estate directory');
  for(const kind of ['households','firms'])validateHistoricalEntityDirectory(kind,data[kind],wire.entities[kind]);
 }else if(wire.entities!=null)throw Error('Unexpected estate directory');
 const canonicalBytes=inactiveCodecBudget(wire);
 const shared={cells:0,expansion:Math.max(encodedBytes??0,canonicalBytes)+packed.total*16};
 const planned={...shared},entityKeyBytes={};
 if(wire.version===2)for(const kind of ['households','firms'])entityKeyBytes[kind]=preflightIdentityExpansion(wire.entities[kind],planned,true);
 const keyBytes=preflightIdentityExpansion(packed,planned,false);
 if(wire.version===2)for(const kind of ['households','firms'])data[kind]=decodeHistoricalEntity(kind,data[kind],wire.entities[kind],shared,entityKeyBytes[kind]);
 const people=new Array(packed.total),seen=new Set();let cells=shared.cells,expansion=shared.expansion;if(expansion>lim.logicalBytes)throw Error('Decoded archive expansion budget exceeded');
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
 // Validate the independently parsed representation before returning any bytes.
 const encoded=JSON.stringify(wire);if(encoded.length>INACTIVE_CODEC_LIMITS.bytes||new Blob([encoded]).size>INACTIVE_CODEC_LIMITS.bytes)throw Error('Archive exceeds encoded byte budget');decodeInactiveEnvelope(JSON.parse(encoded));return encoded;
};
window.__inactivePersonCodec={enable:enabled=>{if(enabled===true&&inactiveCodecCooperative())throw Error('Cooperative snapshot contract is not integrated');if(enabled!==true&&inactivePersonCodecEnabled&&G&&(G.people.length>8000||G.households.length>3000||G.firms.length>3000))throw Error('Load a legacy-sized town or found another before disabling its required identity codec');inactivePersonCodecEnabled=enabled===true;return inactivePersonCodecEnabled;},status:()=>({enabled:inactivePersonCodecEnabled,limits:INACTIVE_CODEC_LIMITS,wireSchema:9,wireVersion:2})};
