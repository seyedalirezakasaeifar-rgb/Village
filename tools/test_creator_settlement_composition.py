"""Independent synchronous creator-settlement checks; no worker readiness asserted."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__settlementComposition=()=>{
 __townTest.reset('settlement',42);__townTest.step(30);const small=archivePayload();
 // Existing bounded estates are synthetic retained history, never deleted to free a slot.
 const existingCommitments=G.projects.filter(p=>p.kind==='firm'||p.kind==='airport').length;while(G.firms.length<2998-existingCommitments)G.firms.push({id:G.firms.length,building:-1,kind:'grocer',name:'Synthetic retained estate',closed:true,demolished:true,cash:0,stock:{},jobs:0,workers:[],wage:30,price:5,owner:-1,deposits:{},history:[],age:100,debt:0,revenue:0,expenses:0,profit:0,tax:0});
 const locate=()=>{for(let y=2;y<T-2;y++)for(let x=2;x<T-2;x++)if(canPlace(x,y,true,'grocer'))return {x,y};throw Error('No available site');};
 const a=startDevelopmentProject('firm',locate(),100,1,{firmKind:'grocer',capital:100}),b=startDevelopmentProject('firm',locate(),100,1,{firmKind:'grocer',capital:100});if(!a||!b)throw Error('Two actual projects not admitted');
 if(!creatorCapacityReason(0,0,1,true))throw Error('Reservation allowed third commitment');
 // Imported old overbooking: both commitments survive, only one actual firm slot remains.
 while(G.firms.length<2999)G.firms.push({id:G.firms.length,building:-1,kind:'grocer',name:'Synthetic retained estate',closed:true,demolished:true,cash:0,stock:{},jobs:0,workers:[],wage:30,price:5,owner:-1,deposits:{},history:[],age:100,debt:0,revenue:0,expenses:0,profit:0,tax:0});
 if(!hydrateSave(archivePayload()))throw Error('Old overbooked state not importable');const work=constructionWork;let calls=[];constructionWork=p=>{if(p.id!==a.id&&p.id!==b.id)return false;calls.push(p.id);return true;};const total=totalMoney();try{completeDevelopmentProjects();}finally{constructionWork=work;}
 const stalled=G.projects.find(p=>p.id===a.id),opened=readBuild(b.id);if(G.firms.length!==3000||calls.length!==1||calls[0]!==b.id||!stalled||stalled.remaining!==1||!stalled.reason.includes('capacity')||opened.firm<0||Math.abs(totalMoney()-total)>.0001)throw Error('Last-slot competition '+JSON.stringify({firms:G.firms.length,calls,a:a.id,b:b.id,stalled,openedFirm:opened?.firm,moneyDelta:totalMoney()-total}));
 const before=JSON.stringify([G.firms,G.people,G.households,G.treasury,G.region,G.nextId,G.projects]),rng=rngState;calls=[];constructionWork=p=>{if(p.id!==a.id&&p.id!==b.id)return false;calls.push(p.id);throw Error('Refused work must not be invoked');};try{completeDevelopmentProjects();}finally{constructionWork=work;}if(calls.length||before!==JSON.stringify([G.firms,G.people,G.households,G.treasury,G.region,G.nextId,G.projects])||rng!==rngState)throw Error('Retry spent/mutated or invoked work');
 if(!hydrateSave(archivePayload())||!G.projects.some(p=>p.id===a.id))throw Error('Stalled commitment not durable');
 // Supported recovery is restoring a valid lower-history archive, not erasing estates.
 if(!hydrateSave(small)||creatorCapacityReason(0,0,1,true))throw Error('Lower-history recovery left stale capacity refusal');const n=G.firms.length,place=locate(),f=createFirm('grocer',place.x,place.y);if(!f||G.firms.length!==n+1)throw Error('Creation did not resume after restore');
 return {twoCommitmentsReserved:true,oneLastSlotExactlyOneCompletion:true,blockedProjectPreserved:true,secondAttemptZeroWorkMoneyIdsRngChanges:true,stalledCommitmentColdReload:true,lowerHistoryArchiveRecoveryResumesCreation:true,noHistoricalIdentityPrunedForCapacity:true,controlledConstructionReadiness:true,workerOrPaidOwnerReadinessClaimed:false,totalBytesNodesProtected:false};
};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__settlementComposition()');b.close()
r['source_sha256']=hashlib.sha256(source.encode()).hexdigest();dest=ROOT/'reports/creator-settlement-composition.json';dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
