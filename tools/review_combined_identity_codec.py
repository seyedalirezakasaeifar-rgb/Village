"""Independent v2 codec field/reference/replay and shared-budget review witness."""
from pathlib import Path
import sys,ast,json,hashlib,os,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();optimized=os.environ.get('CODEC_REVIEW_OPTIMIZED')=='1'
if optimized:
 old=(ROOT/'src/89-inactive-person-codec.js').read_text();new=subprocess.check_output(['git','show','d1f963a:src/89-inactive-person-codec.js'],cwd=ROOT,text=True);assert old in source;source=source.replace(old,new,1)
m=ast.parse((ROOT/'tests/test_estate_firm_codec.py').read_text());owner=next(ast.literal_eval(n.value) for n in m.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets));prefix=owner[owner.index(" __townTest.reset"):owner.index(' __inactivePersonCodec.enable(true);const start=')]
probe=r'''
const independentCanon=v=>Array.isArray(v)?v.map(independentCanon):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,independentCanon(v[k])])):v;
window.__combinedReview={prepare:()=>{PREFIX
 G.households[2999].reviewRefs={person:G.people.length-1,activeHousehold:3000,activeFirm:3000};G.firms[2999].constructor={estate:2999,person:G.people.length-1};G.firms[2999].explicitNull=null;
 __inactivePersonCodec.enable(true);const reviewLogical=archiveLogicalPayload(),wire=JSON.parse(archivePayload());wire.payload.people.reverse();for(const kind of ['households','firms']){wire.payload[kind].reverse();wire.entities[kind].rows.reverse();}wire.inactive.rows.reverse();const decoded=parseArchiveWithInactiveCodec(wire).data;if(JSON.stringify(independentCanon(decoded))!==JSON.stringify(independentCanon(JSON.parse(reviewLogical))))throw Error('Complete logical/reference mismatch');if(!hydrateSave(wire))throw Error('Reordered combined directories rejected');if(Object.prototype.notPollution||!Object.hasOwn(G.firms[2999],'__proto__')||G.households[2999].reviewRefs.activeFirm!==3000)throw Error('Lost special fields/references');return {people:G.people.length,households:G.households.length,firms:G.firms.length,wireBytes:new Blob([JSON.stringify(wire)]).size};},
 run:decodedAgain=>{if(decodedAgain){const w=archivePayload();if(!hydrateSave(w))throw Error('Canonical second decode rejected');}__townTest.step(45);const g=JSON.parse(archiveLogicalPayload());delete g.trafficState;delete g.visualState;return {g:independentCanon(g),rng:rngState};},
 attacks:()=>{const wire=archivePayload(),stable=archiveLogicalPayload(),head=JSON.stringify([saveEpoch,saveOrder,saveRevision,saveTown]),rng=rngState,results=[];
 const mutations={personEstate:v=>v.payload.people[0].hh=99999,loanCreditor:v=>v.payload.loans[0].bankId=-2,loanOwner:v=>v.payload.loans[0].ownerId=99999,summaryOwner:v=>v.payload.settledLoanHistory.households['99999']={count:1,original:1,paid:1},firmId:v=>v.payload.firms[0].id=8999,entityVersionSpoof:v=>{v.version=1;v.entitiesExtended=true;},utf8SharedExpansion:v=>{for(const kind of ['households','firms']){const d=v.entities[kind];d.fields=[...(kind==='households'?['people']:['closed','demolished']),...Array.from({length:10},(_,i)=>'ࠀ'.repeat(120)+String(i).padStart(3,'0'))].sort();d.rows=d.rows.map(r=>[r[0],d.fields.map((_,i)=>i),d.fields.map(k=>k==='people'?[]:k==='closed'||k==='demolished'?true:null)]);}}};
 for(const [name,mutate]of Object.entries(mutations)){const v=JSON.parse(wire);mutate(v);const input=JSON.stringify(v);if(name==='utf8SharedExpansion'){let error='';try{parseArchiveWithInactiveCodec(input)}catch(e){error=e.message;}if(!error.includes('expansion budget'))throw Error('UTF8 shared expansion not rejected by budget: '+error);}if(hydrateSave(v)||archiveLogicalPayload()!==stable||rngState!==rng||JSON.stringify([saveEpoch,saveOrder,saveRevision,saveTown])!==head||JSON.stringify(v)!==input)throw Error('Atomic/domain rejection failed '+name);results.push(name);}return results;
}};
'''.replace('PREFIX',prefix)
results=[];out={'candidate':subprocess.check_output(['git','rev-parse','d1f963a' if optimized else 'aecf8e3'],cwd=ROOT,text=True).strip(),'optimizedVariant':optimized,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'fixturePreparation':'Owner boundary generator, independent assertions; synthetic historical records with real creator boundary actions'}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for decoded_again in [False,True]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();out['boundary']=p.evaluate('__combinedReview.prepare()');
  if not decoded_again:out['additionalAtomicRejected']=p.evaluate('__combinedReview.attacks()')
  results.append(p.evaluate('x=>__combinedReview.run(x)',decoded_again));p.close()
 assert results[0]==results[1],'Canonical logical vs second-decoded45day continuation differs';b.close()
out.update({'fullLogicalFieldAndReferenceEquality':True,'allDirectoriesReorderedWithoutReindexing':True,'canonicalOriginalVsDecodedReplayDays':45,'regionalCreditorAndHighEstateReferencesPreserved':True,'ownPrototypeAndConstructorFieldsPreserved':True});(ROOT/'reports/combined-codec-independent-review.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
