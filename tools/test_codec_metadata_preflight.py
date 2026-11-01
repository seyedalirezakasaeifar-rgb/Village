"""Directory-header failures must precede value traversal and reconstruction."""
from pathlib import Path
import sys,ast,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text()
m=ast.parse((ROOT/'tests/test_estate_firm_codec.py').read_text());owner=next(ast.literal_eval(n.value) for n in m.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets));prefix=owner[owner.index(" __townTest.reset"):owner.index(' __inactivePersonCodec.enable(true);const start=')]
probe=r'''
window.__metadataPreflight=()=>{PREFIX
 __inactivePersonCodec.enable(true);const wire=JSON.parse(archivePayload()),stable=archiveLogicalPayload(),rng=rngState,clock=JSON.stringify([saveEpoch,saveOrder,saveRevision,saveTown]),results=[];
 const cases={personTotal:w=>w.inactive.total++,missingEntities:w=>delete w.entities,extraEntities:w=>w.entities.extra={},unexpectedV1Entities:w=>w.version=1};
 for(const kind of ['households','firms']){
  cases[kind+'Total']=w=>w.entities[kind].total++;
  cases[kind+'OverTotal']=w=>w.entities[kind].total=9001;
  cases[kind+'Missing']=w=>delete w.entities[kind];
  cases[kind+'Rows']=w=>w.entities[kind].rows={};
  cases[kind+'Active']=w=>w.payload[kind]=Array(3001).fill(w.payload[kind][0]);
  cases[kind+'FieldId']=w=>w.entities[kind].fields=['id'];
  cases[kind+'FieldOrder']=w=>w.entities[kind].fields=['z','a'];
 }
 for(const [name,mutate]of Object.entries(cases)){
  const w=JSON.parse(JSON.stringify(wire));mutate(w);const input=JSON.stringify(w);let budgetCalls=0,reconstructions=0,rejected=false;
  const budget=inactiveCodecBudget,decode=decodeHistoricalEntity;
  try{inactiveCodecBudget=function(v){budgetCalls++;return budget(v);};decodeHistoricalEntity=function(...args){reconstructions++;return decode(...args);};rejected=!hydrateSave(w);}finally{inactiveCodecBudget=budget;decodeHistoricalEntity=decode;}
  if(!rejected||budgetCalls||reconstructions||JSON.stringify(w)!==input||archiveLogicalPayload()!==stable||rngState!==rng||JSON.stringify([saveEpoch,saveOrder,saveRevision,saveTown])!==clock)throw Error('Early/atomic rejection failed '+name);
  results.push({name,budgetCalls,reconstructions,atomic:true});
 }
 let budgetCalls=0,reconstructions=0;const budget=inactiveCodecBudget,decode=decodeHistoricalEntity;
 try{inactiveCodecBudget=function(v){budgetCalls++;return budget(v);};decodeHistoricalEntity=function(...args){reconstructions++;return decode(...args);};const decoded=parseArchiveWithInactiveCodec(JSON.stringify(wire));if(decoded.data.households.length!==3001||decoded.data.firms.length!==3001)throw Error('Valid metadata rejected');}finally{inactiveCodecBudget=budget;decodeHistoricalEntity=decode;}
 if(budgetCalls!==1||reconstructions!==2)throw Error('Valid path not traversed exactly once');
 return {wireBytes:new Blob([JSON.stringify(wire)]).size,fixture:'Owner synthetic historical generator with actual constructor boundary actions',malformed:results,validBudgetCalls:budgetCalls,validReconstructions:reconstructions};
};
'''.replace('PREFIX',prefix)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__metadataPreflight()');b.close()
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'productionDefaultEnabled':False,'result':result};(ROOT/'reports/codec-metadata-preflight.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
