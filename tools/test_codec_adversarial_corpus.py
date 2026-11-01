"""Seeded, bounded codec corpus with deterministic reproduction and work counters."""
from pathlib import Path
import sys,json,hashlib,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__codecCorpus=(keysOnly=false)=>{
 const seed=0x53a91c2d;let state=seed;const random=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state;};
 __townTest.reset('settlement',42);__inactivePersonCodec.enable(true);
 const initial=JSON.parse(archivePayload()),copy=v=>JSON.parse(JSON.stringify(v));
 const pack=rows=>{const fields=[...new Set(rows.flatMap(r=>Object.keys(r).filter(k=>k!=='id')))].sort();return {fields,rows:rows.map(r=>{const at=fields.map((k,i)=>Object.hasOwn(r,k)?i:-1).filter(i=>i>=0);return [r.id,at,at.map(i=>r[fields[i]])];})};};
 const originals={};const base=copy(initial);let history=[];for(let i=0;i<2;i++){const p=base.payload.people.pop();p.deceased=true;history.push(p);}base.inactive={total:initial.inactive.total,...pack(history)};originals.people=copy(history);
 for(const kind of ['households','firms']){const active=base.payload[kind],rows=[];for(let i=0;i<2;i++){const r=copy(active[0]);r.id=active.length+i;if(kind==='households'){r.people=[];r.home=-1;}else{r.closed=true;r.demolished=true;r.building=-1;r.workers=[];}rows.push(r);}base.entities[kind]={total:active.length+rows.length,...pack(rows)};originals[kind]=copy(rows);}
 const logical=parseArchiveWithInactiveCodec(JSON.stringify(base)).data;
 const stable=archiveLogicalPayload(),rng=rngState,clock=JSON.stringify([saveEpoch,saveOrder,saveRevision,saveTown]);
 const stats={seed,randomCanonicalCases:0,validWireCases:0,invalidCases:0,maxWireBytes:0,earlyRejectCases:0,syntaxCases:0,lateWork:{},budgetCases:[]},failures=[];
 const equal=(a,b)=>{if(Object.is(a,b))return true;if(!a||!b||typeof a!=='object'||typeof b!=='object'||Array.isArray(a)!==Array.isArray(b))return false;const ka=Object.keys(a).sort(),kb=Object.keys(b).sort();return ka.length===kb.length&&ka.every((k,i)=>k===kb[i]&&equal(a[k],b[k]));};
 const expectedBase=copy(base.payload);expectedBase.schema=8;for(const kind of ['people','households','firms'])expectedBase[kind]=[...expectedBase[kind],...originals[kind]].sort((a,b)=>a.id-b.id);if(!equal(logical,expectedBase))throw Error('Baseline full-field directory fidelity');
 const measured=text=>{const count={budgetCalls:0,historicalDirectoryCalls:0,propertyDefinitions:0};const budget=inactiveCodecBudget,decode=decodeHistoricalEntity,define=Object.defineProperty;let data,error='';try{inactiveCodecBudget=function(v){count.budgetCalls++;return budget(v);};decodeHistoricalEntity=function(...a){count.historicalDirectoryCalls++;return decode(...a);};Object.defineProperty=function(...a){count.propertyDefinitions++;return define(...a);};data=parseArchiveWithInactiveCodec(text).data;}catch(e){error=e.message;}finally{inactiveCodecBudget=budget;decodeHistoricalEntity=decode;Object.defineProperty=define;}stats.maxWireBytes=Math.max(stats.maxWireBytes,new Blob([text]).size);return {count,data,error};};
 const reject=(name,text,early=false,syntax=false)=>{const r=measured(text);if(!r.error)throw Error('Accepted malformed '+name);if(early&&(r.count.budgetCalls||r.count.historicalDirectoryCalls||r.count.propertyDefinitions))throw Error('Not early '+name);if(hydrateSave(text)||archiveLogicalPayload()!==stable||rngState!==rng||JSON.stringify([saveEpoch,saveOrder,saveRevision,saveTown])!==clock)throw Error('Atomicity '+name);stats.invalidCases++;if(early)stats.earlyRejectCases++;if(syntax)stats.syntaxCases++;stats.lateWork[name]={...r.count,error:r.error};return r;};
 const valid=(name,text,expected)=>{const r=measured(text);if(r.error||!equal(r.data,expected))throw Error('Field fidelity '+name+': '+r.error);stats.validWireCases++;};
 const checkValue=(name,token)=>{const w=copy(base);w.payload.reviewValue='__CORPUS_RAW__';const text=JSON.stringify(w).replace('"__CORPUS_RAW__"',token),expected=copy(logical);expected.reviewValue=JSON.parse(token);valid(name,text,expected);};
 if(!keysOnly){
 const nums=['0','-0','0.0','-0.000e+10','1e20','1E+020','100000000000000000000','1e21','1e-7','1e-6','5e-324','1e-324','-1e-999','1.7976931348623157e308','9007199254740993','1.2300e+2'];for(const n of nums)checkValue('number-'+n,n);
 const texts=['','plain','éࠀ😀','\ud800','\udfff','\ud800x\udfff','"\\\b\t\n\f\r\u0000\u001f','\u2028\u2029'];for(const s of texts)checkValue('string-'+JSON.stringify(s),JSON.stringify(s));checkValue('escaped-ascii','"\\u0061\\u0062"');checkValue('escaped-pair','"\\ud83d\\ude00"');
 const tree=depth=>{const at=random()%6;if(depth===0||at<3){if(at===0)return (random()%2?-1:1)*Number('1e'+(random()%600-300));if(at===1){let s='';for(let i=0,n=random()%20;i<n;i++)s+=String.fromCharCode(random()&65535);return s;}return [null,true,false][random()%3];}if(at===3)return Array.from({length:random()%5},()=>tree(depth-1));const o={};for(let i=0,n=random()%5;i<n;i++){const k=['__proto__','constructor','é😀','\u0000','a'][random()%5]+i;Object.defineProperty(o,k,{value:tree(depth-1),enumerable:true});}return o;};
 for(let i=0;i<2048;i++){const v=tree(4),expected=new Blob([JSON.stringify(v)]).size;if(inactiveCodecBudget(v)!==expected)throw Error('Canonical mismatch seed '+seed+' case '+i);stats.randomCanonicalCases++;if(i<256)checkValue('random-'+i,JSON.stringify(v));if(i<64){const w=copy(base),e=copy(expectedBase);w.payload.people[0].reviewValue=copy(v);e.people[0].reviewValue=copy(v);for(const kind of ['people','households','firms']){const records=copy(originals[kind]);records[0].reviewValue=copy(v);e[kind][records[0].id].reviewValue=copy(v);const packed=kind==='people'?w.inactive:w.entities[kind];Object.assign(packed,pack(records));}valid('random-mixed-directories-'+i,JSON.stringify(w),e);}}
 // JSON duplicate property names have ordinary last-value-wins semantics. Every
 // validator sees that same parsed value; no duplicate-ID array is allowed.
 let text=JSON.stringify(base);valid('duplicate-version-last-valid',text.replace('"version":2','"version":3,"version":2'),logical);reject('duplicate-version-last-invalid',text.replace('"version":2','"version":2,"version":3'),true);
 valid('duplicate-id-key-last-valid',text.replace('"id":0','"id":99999,"id":0'),logical);
 checkValue('prototype-key-object','{"__proto__":{"notPollution":true},"constructor":{"x":1},"__proto__":{"last":2}}');
 const w=copy(base);w.payload.reviewValue=null;const e=copy(logical);e.reviewValue={a:2};valid('duplicate-unknown-key-last-value',JSON.stringify(w).replace('"reviewValue":null','"reviewValue":{"a":1,"a":2}'),e);
 for(const token of ['[1,,2]','[1,]','{"a":}','NaN','Infinity','01','+1','1.','1e','"\\uZZZZ"']){const w=copy(base);w.payload.reviewValue='__BAD__';reject('syntax-'+token,JSON.stringify(w).replace('"__BAD__"',token),true,true);}
 for(const token of ['1e309','-1e999']){const w=copy(base);w.payload.reviewValue='__BAD__';reject('nonfinite-'+token,JSON.stringify(w).replace('"__BAD__"',token));}
 const mutations={
  missingPayload:w=>delete w.payload,missingPersonFields:w=>delete w.inactive.fields,missingPersonRows:w=>delete w.inactive.rows,missingSchema:w=>delete w.schema,missingLogicalSchema:w=>delete w.logicalSchema,
  entitiesArray:w=>w.entities=[],entitiesNull:w=>w.entities=null,unknownDirectory:w=>w.entities.unknown={},personTotalFraction:w=>w.inactive.total+=0.5,personTotalString:w=>w.inactive.total=String(w.inactive.total),
  activeDuplicateId:w=>w.payload.people[1].id=w.payload.people[0].id,activeMissingId:w=>delete w.payload.people[0].id,activeUnsafeId:w=>w.payload.people[0].id=9007199254740992,
  historyDuplicateId:w=>w.inactive.rows[1][0]=w.inactive.rows[0][0],historyIdNull:w=>w.inactive.rows[0][0]=null,historyRowNull:w=>w.inactive.rows[0]=null,historyValuesNull:w=>w.inactive.rows[0][2]=null,historyIndicesObject:w=>w.inactive.rows[0][1]={},historySparseIndex:w=>delete w.inactive.rows[0][1][0],historyIndexString:w=>w.inactive.rows[0][1][0]='0',historyIndexFraction:w=>w.inactive.rows[0][1][0]=0.5,historyIndexNegative:w=>w.inactive.rows[0][1][0]=-1,historyIndexDuplicate:w=>w.inactive.rows[0][1][1]=w.inactive.rows[0][1][0],
  historyAgeMissing:w=>{const r=w.inactive.rows[0],at=r[1].indexOf(w.inactive.fields.indexOf('age'));r[1].splice(at,1);r[2].splice(at,1);},historyHhMissing:w=>{const r=w.inactive.rows[0],at=r[1].indexOf(w.inactive.fields.indexOf('hh'));r[1].splice(at,1);r[2].splice(at,1);},
  householdTotal:w=>w.entities.households.total++,firmTotal:w=>w.entities.firms.total++,firmFieldsDuplicate:w=>w.entities.firms.fields.push(w.entities.firms.fields[0]),householdDuplicateId:w=>w.entities.households.rows[1][0]=w.entities.households.rows[0][0],firmDuplicateId:w=>w.entities.firms.rows[1][0]=w.entities.firms.rows[0][0],firmRowSparse:w=>delete w.entities.firms.rows[0],firmValuesShort:w=>w.entities.firms.rows[0][2].pop()
 };
 const earlyNames=new Set(['missingPayload','missingPersonFields','missingPersonRows','missingSchema','missingLogicalSchema','entitiesArray','entitiesNull','unknownDirectory','personTotalFraction','personTotalString','householdTotal','firmTotal','firmFieldsDuplicate']);
 for(const [name,mutate]of Object.entries(mutations)){const w=copy(base);mutate(w);reject(name,JSON.stringify(w),earlyNames.has(name));}
 // Seeded combinations retain a known invalid header; this verifies no mutation
 // combination sneaks past the early barrier or changes live state.
 const entries=Object.entries(mutations);for(let i=0;i<128;i++){const w=copy(base),[name,mutate]=entries[random()%entries.length];mutate(w);w.inactive.total=-1;reject('seeded-header-'+i+'-'+name,JSON.stringify(w),true);}
 }
 if(!keysOnly){
 // Each estate directory alone fits the shared node budget. Together they do
 // not, and must reject before constructing either directory.
 const large=copy(initial);for(const kind of ['households','firms']){const fields=[...(kind==='households'?['people']:['closed','demolished']),...Array.from({length:43},(_,i)=>'x'+i)].sort(),active=large.payload[kind];large.entities[kind]={total:active.length+6000,fields,rows:Array.from({length:6000},(_,i)=>[active.length+i,fields.map((_,j)=>j),fields.map(k=>k==='people'?[]:k==='closed'||k==='demolished'?true:null)])};}
 for(const kind of ['households','firms']){const single=copy(large),other=kind==='firms'?'households':'firms';single.entities[other]=copy(initial.entities[other]);const r=measured(JSON.stringify(single));if(r.error)throw Error('Individual node budget unexpectedly fails '+kind+': '+r.error);stats.budgetCases.push({name:kind+'-alone',accepted:true,...r.count});}
 const shared=reject('shared-node-combination',JSON.stringify(large));if(shared.count.budgetCalls!==1||shared.count.historicalDirectoryCalls||shared.count.propertyDefinitions)throw Error('Shared node budget reconstructed state');stats.budgetCases.push({name:'combined-node-limit',...shared.count,error:shared.error});
 }
 const expanded=copy(initial);for(const kind of ['households','firms']){const fields=[...(kind==='households'?['people']:['closed','demolished']),...Array.from({length:10},(_,i)=>'ࠀ'.repeat(120)+String(i).padStart(3,'0'))].sort(),active=expanded.payload[kind];expanded.entities[kind]={total:active.length+3000,fields,rows:Array.from({length:3000},(_,i)=>[active.length+i,fields.map((_,j)=>j),fields.map(k=>k==='people'?[]:k==='closed'||k==='demolished'?true:null)])};}
 if(keysOnly!=='reject')for(const kind of ['households','firms']){const single=copy(expanded),other=kind==='firms'?'households':'firms';single.entities[other]=copy(initial.entities[other]);const r=measured(JSON.stringify(single));if(r.error)throw Error('Individual expansion budget unexpectedly fails '+kind+': '+r.error);stats.budgetCases.push({name:kind+'-key-expansion-alone',accepted:true,...r.count});}
 const expandedReject=reject('shared-key-expansion-combination',JSON.stringify(expanded));if(!expandedReject.error.includes('expansion budget')||expandedReject.count.historicalDirectoryCalls||expandedReject.count.propertyDefinitions)throw Error('Shared decoded-byte rejection reconstructed fields');stats.budgetCases.push({name:'combined-key-expansion-limit',...expandedReject.count,error:expandedReject.error});
 if(keysOnly!=='reject'){
 const near=copy(expanded);for(const kind of ['households','firms']){near.entities[kind].rows=near.entities[kind].rows.slice(0,2000);near.entities[kind].total=near.payload[kind].length+2000;}near.payload.reviewPadding='';
 const expectedCharge=w=>{let n=new Blob([JSON.stringify(w)]).size+w.inactive.total*16;for(const kind of ['households','firms'])n+=w.entities[kind].total*16;for(const d of [w.entities.households,w.entities.firms,w.inactive]){const costs=d.fields.map(k=>new Blob([JSON.stringify(k)]).size+3);for(const row of d.rows)for(const at of row[1])n+=costs[at];}return n;};
 const beforePadding=expectedCharge(near),padding=INACTIVE_CODEC_LIMITS.logicalBytes-beforePadding;if(padding<0||padding>4*1024*1024)throw Error('Near-limit fixture no longer bounded');near.payload.reviewPadding='a'.repeat(padding);if(expectedCharge(near)!==INACTIVE_CODEC_LIMITS.logicalBytes)throw Error('Near-limit charge oracle mismatch');
 const nearText=JSON.stringify(near);if(new Blob([nearText]).size>INACTIVE_CODEC_LIMITS.bytes)throw Error('Near-limit fixture exceeds wire cap');const acceptedNear=measured(nearText);if(acceptedNear.error||acceptedNear.data.reviewPadding!==near.payload.reviewPadding||acceptedNear.data.households.length!==near.entities.households.total||acceptedNear.data.firms.length!==near.entities.firms.total)throw Error('Valid exact expansion charge rejected or changed');stats.budgetCases.push({name:'exact-shared-key-expansion-limit',accepted:true,conservativeBytes:expectedCharge(near),...acceptedNear.count});
 near.payload.reviewPadding+='a';const oneOver=reject('shared-key-expansion-one-byte-over',JSON.stringify(near));if(oneOver.count.historicalDirectoryCalls||oneOver.count.propertyDefinitions)throw Error('One-byte-over shared expansion reconstructed fields');stats.budgetCases.push({name:'shared-key-expansion-one-byte-over',...oneOver.count,error:oneOver.error});
 }
 if(!keysOnly){let deep={};for(let i=0;i<30;i++)deep={next:deep};const deepWire=copy(base);deepWire.payload.reviewDeep=deep;const d=reject('depth-combination',JSON.stringify(deepWire));if(d.count.historicalDirectoryCalls)throw Error('Depth failure reconstructed state');}
 if(Object.prototype.notPollution)throw Error('Prototype pollution');
 // Keep the work table bounded and preserve exact case names/seed for replay.
 stats.mode=keysOnly||'full';stats.failureCount=failures.length;stats.negativeZeroPreservedBeforeSerialization=keysOnly?null:true;stats.duplicateKeySemantics=keysOnly?'not tested in focused mode':'JSON.parse last value wins';stats.identityArraysRequireUniqueIds=keysOnly?null:true;return stats;
};
'''
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--js-flags=--max-old-space-size=384']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('mode=>__codecCorpus(mode)',os.environ.get('CODEC_CORPUS_KEYS_ONLY') or False);b.close()
except Exception as error:
 failure={'seed':0x53a91c2d,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'error':str(error),'reproduction':'python tools/assemble.py && python tools/test_codec_adversarial_corpus.py'}
 (ROOT/'reports/codec-adversarial-corpus-failure.json').write_text(json.dumps(failure,indent=2));raise
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'productionDefaultEnabled':False,'browserOldSpaceCapMiB':384,'result':result};(ROOT/('reports/codec-shared-key-focused.json' if os.environ.get('CODEC_CORPUS_KEYS_ONLY') else 'reports/codec-adversarial-corpus.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
