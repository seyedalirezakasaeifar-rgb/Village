"""Independent phase snapshots, complete-state equivalence and bounded history admission."""
import hashlib,json,subprocess
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
from neighborhood_history_oracle import ORACLE_PROBE
BASE='0a6d217933eb0eac0c42787483ae96c624d23ef5'
source=(ROOT/'assets/game.js').read_text();base=subprocess.check_output(['git','show',BASE+':assets/game.js'],cwd=ROOT,text=True)
probe=ORACLE_PROBE+r'''
let historyBuilds=0,historyCalls=0,historyCPU=0;
if(typeof urbanRecordActivity==='function'){const original=urbanRecordActivity;urbanRecordActivity=function(){const before=urbanCache,start=performance.now();original();const first=JSON.stringify(G.urban.activity);original();if(JSON.stringify(G.urban.activity)!==first)throw Error('Repeated same-day capture changed the history');historyCPU+=performance.now()-start;historyCalls++;if(urbanCache!==before)historyBuilds++;};}
window.__independentHistory={reset:scenario=>{independentlyObserved=[];historyBuilds=0;historyCalls=0;historyCPU=0;__townTest.reset(scenario,42);closePanel();paused=true;},run:days=>{if(days)__townTest.step(days);return {archive:JSON.parse(archivePayload()),expected:independentlyObserved,historyBuilds,historyCalls,historyCPU,valid:validateTown().ok};},
 guards:()=>{const good=archivePayload(),input=JSON.parse(good),cases=[];const sample=input.urban.activity[0],key=Object.keys(sample.blocks)[0];for(const kind of ['longAliasKey','extraSnapshotField','extraRowField','negative','fractional','tooLarge','threeSamples','wrongSpacing','future','arrayBlocks','arrayRow','missingValue']){const data=JSON.parse(good),s=data.urban.activity[0],row=s.blocks[key];if(kind==='longAliasKey'){s.blocks['0'.repeat(128)+key]=row;delete s.blocks[key]}else if(kind==='extraSnapshotField')s.extra='x'.repeat(8192);else if(kind==='extraRowField')row.extra='x'.repeat(8192);else if(kind==='negative')row.residents=-1;else if(kind==='fractional')row.staffedJobs=.5;else if(kind==='tooLarge')row.jobCapacity=10000001;else if(kind==='threeSamples')data.urban.activity.push(data.urban.activity[1]);else if(kind==='wrongSpacing')data.urban.activity[1].day--;else if(kind==='future')data.urban.activity[1].day=data.day+1;else if(kind==='arrayBlocks')s.blocks=[];else if(kind==='arrayRow')s.blocks[key]=[];else delete row.occupiedHomes;const accepted=hydrateSave(data);cases.push({kind,accepted,atomic:good===archivePayload()});}
 const blocks={};for(let y=0;y<T/8;y++)for(let x=0;x<T/8;x++)blocks[x+':'+y]={residents:10000000,occupiedHomes:10000000,staffedJobs:10000000,jobCapacity:10000000};const largest=[{day:90,blocks},{day:180,blocks}],data=JSON.parse(good);data.urban.activity=largest;const accepted=hydrateSave(data),bytes=new TextEncoder().encode(JSON.stringify(largest)).length;const restored=hydrateSave(good);return {cases,maximumShapeAccepted:accepted,maximumLedgerUtf8Bytes:bytes,normalTownRestored:restored};},
 reads:()=>{const person=G.people.find(p=>!p.deceased&&!p.movedAway&&p.job<0&&!p.publicWork&&!p.commuteBlocked&&G.households[p.hh]?.people.includes(p.id));if(!person)throw Error('No real resident for record counterexample');const home=readBuild(G.households[person.hh].home),key=urbanBlockKey(home.x,home.y),before=archivePayload(),saved={age:person.age,publicWork:person.publicWork,publicIncome:person.publicIncome,publicRole:person.publicRole};person.age=16;person.publicWork=false;const young=urbanNeighborhoodPulse(key);person.age=18;const adult=urbanNeighborhoodPulse(key);person.publicWork=true;person.publicIncome=30;person.publicRole='transit';const publicCrew=urbanNeighborhoodPulse(key);for(const[k,v]of Object.entries(saved)){if(v===undefined)delete person[k];else person[k]=v;}const start=performance.now();for(let i=0;i<100;i++)urbanNeighborhoodPulse(key);const elapsed=performance.now()-start;return {youngSearching:young.searching,adultSearching:adult.searching,paidCrewSearching:publicCrew.searching,publicCrewIncrease:publicCrew.publicCrew-adult.publicCrew,completeArchiveAndRngUnchanged:before===archivePayload(),hundredReadsMs:elapsed};}
};'''
rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for code in [base,source]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=code.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();pages.append(p)
 for scenario in ['settlement','regional','industrial']:
  for p in pages:p.evaluate('s=>__independentHistory.reset(s)',scenario)
  for elapsed in [0,90,180,270,360]:
   reference,current=[p.evaluate('n=>__independentHistory.run(n)',0 if elapsed==0 else 90)for p in pages];expected=reference['archive']
   if reference['expected']:expected['urban']['activity']=reference['expected']
   if reference['expected']!=current['expected']or current['archive']!=expected:
    def differences(a,b,path=''):
     if type(a)!=type(b):return [(path,a,b)]
     if isinstance(a,dict):return sum([differences(a.get(k),b.get(k),path+'.'+k)for k in a.keys()|b.keys()],[])
     if isinstance(a,list):return sum([differences(x,y,path+'.'+str(i))for i,(x,y)in enumerate(zip(a,b))],[])if len(a)==len(b)else [(path,'length',len(a),len(b))]
     return []if a==b else [(path,a,b)]
    print(json.dumps({'scenario':scenario,'elapsed':elapsed,'phaseOracleDifferences':differences(reference['expected'],current['expected']),'completeArchiveDifferences':differences(expected,current['archive'])[:30]},indent=2),flush=True)
   assert reference['expected']==current['expected']and current['archive']==expected,(scenario,elapsed)
   assert current['valid']and reference['valid']and current['historyBuilds']==0,(scenario,elapsed)
   rows.append({'scenario':scenario,'elapsedDays':elapsed,'completeStateMatchesIndependentExpectedLedger':True,'historyColdBuilds':current['historyBuilds'],'quarterCalls':current['historyCalls'],'quarterCaptureCPUmsWithDuplicateCapture':current['historyCPU']})
 guards=pages[1].evaluate('__independentHistory.guards()');assert all(not r['accepted']and r['atomic']for r in guards['cases']),guards;assert guards['maximumShapeAccepted']and guards['maximumLedgerUtf8Bytes']<65536 and guards['normalTownRestored'],guards
 reads=pages[1].evaluate('__independentHistory.reads()');assert reads['youngSearching']==reads['adultSearching']and reads['paidCrewSearching']==reads['adultSearching']-1 and reads['publicCrewIncrease']==1 and reads['completeArchiveAndRngUnchanged'],reads
 b.close()
print(json.dumps({'base':BASE,'base_source_sha256':hashlib.sha256(base.encode()).hexdigest(),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'excludedFields':[],'checkpoints':rows,'schema':guards,'observationalRecordCases':reads,'timingLimits':'Host diagnostic timers, including deliberate duplicate capture; not a device/FPS guarantee.'},indent=2))
