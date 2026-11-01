from pathlib import Path
import sys,json,hashlib,subprocess,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__creatorCapTest=()=>{
 const rows=[];const reset=()=>{__townTest.reset('settlement',42);__townTest.step(30);};
 const unchanged=(name,fn)=>{const before=archivePayload(),rng=rngState;fn();if(before!==archivePayload()||rng!==rngState)throw Error(name+' mutated model/RNG');rows.push({name,exactModelAndRng:true});};
 reset();while(G.firms.length<3000)G.firms.push({id:G.firms.length,building:-1,kind:'grocer',name:'Synthetic estate',closed:true,demolished:true,cash:0,stock:{},jobs:0,workers:[],wage:30,price:5,owner:-1,deposits:{},history:[],age:100,debt:0,revenue:0,expenses:0,profit:0,tax:0});
 if(!hydrateSave(archivePayload()))throw Error('Cap archive rejected');let lot;for(let y=2;y<T-2&&!lot;y++)for(let x=2;x<T-2;x++)if(canPlace(x,y,true,'grocer')){lot={x,y};break;}if(!lot)throw Error('No parcel');
 unchanged('paid construction at 3000',()=>construct('grocer',lot.x,lot.y));unchanged('leaf firm at 3000',()=>{if(createFirm('grocer',lot.x,lot.y)!==null)throw Error('admitted');});unchanged('private investor at 3000',()=>privatelyBuiltFirm({}));unchanged('retail at 3000',()=>urbanRetailProposal());unchanged('airfield at 3000',()=>airfieldInvestment({}));unchanged('project at 3000',()=>{if(startDevelopmentProject('firm',lot,100,10,{firmKind:'grocer'}))throw Error('admitted');});
 while(G.firms.length+(G.projects||[]).filter(p=>p.kind==='firm'||p.kind==='airport').length>2999)G.firms.pop();const site=startDevelopmentProject('firm',lot,100,10,{firmKind:'grocer'});if(!site||!creatorCapacityReason(0,0,1,true))throw Error('Reservation not counted');unchanged('paid construction respects last reserved slot',()=>construct('grocer',lot.x,lot.y));
 const project=G.projects.find(p=>p.id===site.id);while(G.firms.length<3000)G.firms.push({id:G.firms.length,closed:true});project.remaining=1;const before=JSON.stringify([G.treasury,G.region,G.nextId,G.firms.length,project.remaining]),rng=rngState;completeDevelopmentProjects();if(before!==JSON.stringify([G.treasury,G.region,G.nextId,G.firms.length,project.remaining])||rng!==rngState||!G.projects.includes(project)||!project.reason.includes('capacity'))throw Error('Committed site lost funds/work');rows.push({name:'oversubscribed old project deferred',fundsIdsRemainingAndRngPreserved:true});
 reset();while(G.people.length<8000)G.people.push({id:G.people.length,name:'Synthetic history',age:90,health:0,hh:0,job:-1,deceased:true,last:[]});G.day=90;unchanged('birth cap',birthsAndGenerations);unchanged('family arrival cap',migrationFamilyArrivalDay);const home=G.buildings.find(b=>b.kind==='home');unchanged('household arrival person cap',()=>{if(addHouseholdAt(home))throw Error('admitted');});
 reset();while(G.households.length<3000)G.households.push({id:G.households.length,name:'Synthetic estate',people:[],cash:0,deposits:{},home:-1});G.day=90;unchanged('formation household cap',householdFormation);unchanged('arrival household cap',()=>{if(addHouseholdAt(G.buildings.find(b=>b.kind==='home')))throw Error('admitted');});
 reset();while(G.people.length<7999)G.people.push({id:G.people.length,name:'Synthetic history',age:90,health:0,hh:0,job:-1,deceased:true,last:[]});const family=G.households.find(h=>h.people.length===2);family.stress=0;family.cash=100000;family.lastBirth=-720;for(const id of family.people){G.people[id].age=25;G.people[id].job=0;}G.day=90;const draw=random;random=()=>0;try{birthsAndGenerations();}finally{random=draw;}if(G.people.length!==8000)throw Error('Final birth slot not usable');unchanged('birth remains capped after final slot',birthsAndGenerations);rows.push({name:'actual birth creator 7999 to 8000',controlledEligibilityAndDraw:true});
 reset();while(G.firms.length<2999)G.firms.push({id:G.firms.length,building:-1,kind:'grocer',name:'Synthetic estate',closed:true,demolished:true,cash:0,stock:{},jobs:0,workers:[],wage:30,price:5,owner:-1,deposits:{},history:[],age:100,debt:0,revenue:0,expenses:0,profit:0,tax:0});let finalLot;for(let y=2;y<T-2&&!finalLot;y++)for(let x=2;x<T-2;x++)if(canPlace(x,y,true,'grocer')){finalLot={x,y};break;}const finalFirm=createFirm('grocer',finalLot.x,finalLot.y);if(!finalFirm||finalFirm.id!==2999||G.firms.length!==3000||!hydrateSave(archivePayload()))throw Error('Last firm slot not importable');rows.push({name:'actual firm creator 2999 to 3000',selfImportable:true});
 const start=performance.now();for(let n=0;n<10000;n++)creatorCapacityReason(0,1);return {rows,checks10000Ms:performance.now()-start,totalByteNodeProtection:false,codecsEnabled:false};
};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__creatorCapTest()');p.close()
 archives=[]
 for variant in ['previous','guarded']:
  base=os.environ.get('CREATOR_PREFLIGHT_BASE','669c908706af997375680674390e46fd132a970a');files=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'src/'],cwd=ROOT,text=True).splitlines()
  code=source if variant=='guarded' else '\n'.join('// SOURCE: '+Path(name).name+'\n'+subprocess.check_output(['git','show',base+':'+name],cwd=ROOT,text=True) for name in sorted(files) if name.endswith('.js'))
  q=b.new_page();q.set_content(html);q.add_script_tag(content=code);q.locator('#newTown').click();q.locator('#pause').click();archives.append(q.evaluate("()=>{__townTest.reset('settlement',42);__townTest.step(90);return __townTest.save();}"));q.close()
 if archives[0]!=archives[1]:raise AssertionError('Ordinary 90-day replay changed')
 r['ordinary_reference_commit']=base;r['ordinary90DayReplayExact']=True;r['ordinaryArchiveSha256']=hashlib.sha256(archives[0].encode()).hexdigest();b.close()
r['source_sha256']=hashlib.sha256(source.encode()).hexdigest();dest=ROOT/'reports/creator-capacity-preflight.json';dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
