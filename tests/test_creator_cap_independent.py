"""Eligible-path counterexamples for reservation and paid retail capacity guards."""
import hashlib,json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text()
retail_guard=" const capacityReason=creatorCapacityReason(0,0,1,true);if(capacityReason)return {ok:false,reason:capacityReason};\n"
assert source.count(retail_guard)==1
construct_guard="const capacityReason=createsFirm?creatorCapacityReason(0,0,1,true):'';"
assert source.count(construct_guard)==1
probe=r'''
function capEstate(){const t=G.firms[0];return {...t,id:G.firms.length,building:-1,name:'Synthetic closed history',closed:true,demolished:true,cash:0,stock:Object.fromEntries(Object.keys(t.stock).map(k=>[k,0])),workers:[],attendingWorkers:[],jobs:0,deposits:{},debt:0,owner:-1,history:[]};}
function capFill(n){while(G.firms.length<n)G.firms.push(capEstate());}
function capRetailFixture(){__townTest.reset('settlement',42);for(const h of G.households)for(let j=0;j<18;j++){const p={id:G.people.length,name:'Controlled capacity fixture resident',age:29,skill:.7,health:90,hh:h.id,job:-1,life:70,last:[]};G.people.push(p);h.people.push(p.id);}G.stats.marketConfidence=75;const q=urbanRetailProposal('preview');if(!q.ok)throw Error('Retail counterexample is ineligible: '+q.reason);return q;}
window.__independentCap={
 retail:()=>{capRetailFixture();capFill(3000);const before=archivePayload(),rng=rngState,result=urbanRetailProposal();return {result,modelUnchanged:before===archivePayload(),rngUnchanged:rng===rngState};},
 reserved:()=>{__townTest.reset('settlement',42);capFill(2999);const lots=[];for(let y=2;y<T-2&&lots.length<2;y++)for(let x=2;x<T-2&&lots.length<2;x++)if(canPlace(x,y,true,'grocer')&&lots.every(p=>Math.abs(x-p.x)+Math.abs(y-p.y)>6))lots.push({x,y});if(lots.length<2)throw Error('Two legal lots required');const site=startDevelopmentProject('firm',lots[0],10000,10,{firmKind:'grocer'});if(!site||!canPlace(lots[1].x,lots[1].y,true,'grocer'))throw Error('Reservation control has no separate vacant paid site');const before=archivePayload(),rng=rngState,treasury=G.treasury;construct('grocer',lots[1].x,lots[1].y);return {differentVacantLot:true,modelUnchanged:before===archivePayload(),rngUnchanged:rng===rngState,firmCount:G.firms.length,treasuryDelta:G.treasury-treasury};},
 overbooked:()=>{const q=capRetailFixture(),result=urbanRetailProposal(true,q.reviewKey);if(!result.ok)throw Error(result.reason);capFill(3000);recompute();if(!hydrateSave(archivePayload()))throw Error('Old overbooked project fixture must be a valid archive');const project=G.projects.find(p=>p.retailCentre);project.remaining=1;const money=totalMoney(),rng=rngState,before=JSON.parse(archivePayload()),escrow=project.urbanEscrow;completeDevelopmentProjects();const after=JSON.parse(archivePayload());before.projects.find(p=>p.id===project.id).reason=project.reason;return {validLegacyFixture:true,expectedReasonOnly:JSON.stringify(before)===JSON.stringify(after),remaining:project.remaining,escrowBefore:escrow,escrowAfter:project.urbanEscrow,moneyUnchanged:money===totalMoney(),rngUnchanged:rng===rngState,reason:project.reason};}
};'''
rows={}
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for label,js in [('guarded',source),('missingRetailGuard',source.replace(retail_guard,'',1)),('missingPaidReservationGuard',source.replace(construct_guard,"const capacityReason='';",1))]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=js.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
  rows[label]={}
  for name in (['retail','reserved','overbooked']if label=='guarded'else['retail']if label=='missingRetailGuard'else['reserved']):rows[label][name]=p.evaluate('n=>__independentCap[n]()',name)
  p.close()
 b.close()
g=rows['guarded'];assert g['retail']['modelUnchanged']and g['retail']['rngUnchanged']and 'capacity' in g['retail']['result']['reason']
assert g['reserved']['modelUnchanged']and g['reserved']['rngUnchanged']and g['reserved']['firmCount']==2999
assert not rows['missingRetailGuard']['retail']['rngUnchanged'],rows
assert rows['missingPaidReservationGuard']['reserved']['firmCount']==3000 and rows['missingPaidReservationGuard']['reserved']['treasuryDelta']<0,rows
old=g['overbooked'];assert old['expectedReasonOnly']and old['remaining']==1 and old['escrowBefore']==old['escrowAfter']==28000 and old['moneyUnchanged']and old['rngUnchanged'],old
print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledHistoricalAndRetailFixtures':True,'cases':rows},indent=2))
