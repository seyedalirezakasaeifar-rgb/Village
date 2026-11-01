"""Canonical-byte guard regressions; runs disabled codec only in fresh test pages."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__canonicalBudgetReview=()=>{
 __townTest.reset('settlement',42);__inactivePersonCodec.enable(true);
 const wire=JSON.parse(archivePayload()),stable=archiveLogicalPayload(),rng=rngState,clock=JSON.stringify([saveEpoch,saveOrder,saveRevision,saveTown]),results=[];
 const exact=v=>{const measured=inactiveCodecBudget(v),actual=new Blob([JSON.stringify(v)]).size;if(measured!==actual)throw Error('Byte mismatch '+measured+' != '+actual);return actual;};
 const strings=['','plain','"\\\b\t\n\f\r\u0000\u001f','éࠀ😀','\ud800','\udfff','\ud800x\udfff','\u2028\u2029'];
 for(const s of strings)exact({[s]:[s,true,false,null,-0,1e20,1e21,1e-7,1e-6,Number.MIN_VALUE,Number.MAX_VALUE]});
 let n=12345;for(let j=0;j<100;j++){let s='';for(let i=0;i<80;i++){n=(Math.imul(n,1664525)+1013904223)>>>0;s+=String.fromCharCode(n&65535);}exact({[s]:s});}
 const limit=INACTIVE_CODEC_LIMITS.logicalBytes;
 exact({x:'a'.repeat(limit-8)});let over=false;try{inactiveCodecBudget({x:'a'.repeat(limit-7)});}catch(e){over=e.message.includes('expansion budget');}if(!over)throw Error('Canonical boundary accepted');
 const version=v=>{const w=JSON.parse(JSON.stringify(wire));if(v===1){const decoded=parseArchiveWithInactiveCodec(JSON.stringify(w)).data;w.version=1;delete w.entities;w.payload.households=decoded.households;w.payload.firms=decoded.firms;}return w;};
 const reject=(name,w)=>{const text=JSON.stringify(w).replace(/100000000000000000000/g,'1e20');if(new Blob([text]).size>=INACTIVE_CODEC_LIMITS.bytes)throw Error('Attack exceeds wire cap');let error='';try{parseArchiveWithInactiveCodec(text);}catch(e){error=e.message;}if(!error.includes('expansion budget'))throw Error('Not budget-rejected '+name+': '+error);if(hydrateSave(text)||archiveLogicalPayload()!==stable||rngState!==rng||JSON.stringify([saveEpoch,saveOrder,saveRevision,saveTown])!==clock)throw Error('Atomicity failed '+name);results.push({name,inputBytes:new Blob([text]).size,error});};
 for(const v of [1,2]){
  let w=version(v);w.payload.reviewNumbers=Array(800000).fill(1e20);reject('v'+v+'-flat-numeric',w);
  w=version(v);w.payload.reviewNumbers=Array.from({length:800},()=>({nested:[Array(1000).fill(1e20)]}));reject('v'+v+'-nested-numeric',w);
  w=version(v);w.payload.reviewNumbers=Array(400000).fill(1e20);w.payload.people[0].reviewNumbers=Array(400000).fill(1e20);reject('v'+v+'-mixed-record-numeric',w);
  if(v===2){w=version(v);w.payload.reviewNumbers=Array(300000).fill(1e20);w.payload.households[0].reviewNumbers=Array(250000).fill(1e20);w.payload.firms[0].reviewNumbers=Array(250000).fill(1e20);reject('v2-mixed-estates-firms-numeric',w);}
  // A real historical person value shares the same budget as the payload.
  w=version(v);const p=w.payload.people.pop();p.deceased=true;const fields=Object.keys(p).filter(k=>k!=='id').concat('reviewNumbers').sort();w.inactive={total:wire.inactive.total,fields,rows:[[p.id,fields.map((_,i)=>i),fields.map(k=>k==='reviewNumbers'?Array(400000).fill(1e20):p[k])]]};w.payload.reviewNumbers=Array(400000).fill(1e20);reject('v'+v+'-packed-record-numeric',w);
  w=version(v);w.payload.reviewNumbers=Array(740000).fill(1e20);const text=JSON.stringify(w).replace(/100000000000000000000/g,'1e20'),decoded=parseArchiveWithInactiveCodec(text).data;if(decoded.reviewNumbers.length!==740000||decoded.reviewNumbers.some(x=>x!==1e20))throw Error('Valid near-boundary values changed');results.push({name:'v'+v+'-valid-near-logical-limit',inputBytes:new Blob([text]).size,logicalBytes:new Blob([JSON.stringify(decoded)]).size});
 }
 return {canonicalStringAndNumberFixtures:strings.length+100,exactLimitAccepted:true,oneByteOverRejected:true,atomicStateAndRng:true,results};
};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__canonicalBudgetReview()');b.close()
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'productionFlagEnabled':False,'result':result};target=ROOT/'reports/codec-canonical-budget.json';target.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
