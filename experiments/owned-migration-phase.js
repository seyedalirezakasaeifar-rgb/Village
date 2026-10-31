// Not shipped. Explicit ownership for one reviewed monthly phase, not a day engine.
function createOwnedMigrationStore(initial,initialContext,expectedSource){
 if(outwardMigration.toString()!==expectedSource)throw Error('Migration source changed; review write set before running');
 const audited=createPhaseCowStore(initial),freezeNew=value=>{if(!value||typeof value!=='object'||Object.isFrozen(value))return value;for(const key of Object.keys(value))freezeNew(value[key]);return Object.freeze(value);};
 let root=audited.current,context=freezeNew(initialContext),active=false,exportText=null;
 function captureGlobals(){return {G,rng:rngState,owner:migrationReportOwner,recent:migrationRecent,observed:migrationObservedDay,counts:migrationSessionCounts};}
 function restoreGlobals(saved){G=saved.G;rngState=saved.rng;migrationReportOwner=saved.owner;migrationRecent=saved.recent;migrationObservedDay=saved.observed;migrationSessionCounts=saved.counts;roadNetwork=null;roadGraphOwner=null;cacheBuildingsFor=null;transitTopologyCache=null;transitDailyCache=null;}
 function run(day,{faultAt=null,observe=null}={}){
  if(active)throw Error('Phase already active');if(outwardMigration.toString()!==expectedSource)throw Error('Migration source changed');active=true;
  const saved=captureGlobals(),published=root,oldContext=context,metrics={prepareMs:0,planMs:0,applyMs:0,commitMs:0,ownedPeople:0,ownedHouseholds:0,ownedFirms:0,ownedBuildings:0};let work={...published,day},nextContext,selected=null;
  const boundary=name=>{observe?.(name,published,oldContext);if(name===faultAt)throw Error('Injected owned fault: '+name);};
  try{
   G=work;rngState=context.rng;let started=performance.now();
   if(day%30===0){const choices=G.households.filter(h=>h.people.length&&h.home>=0&&((h.stress||0)>42||(h.worklessness||0)>20)&&migrationSpendable(h).spendable<90*Math.max(1,expectedHouseholdEssentials(h)+migrationDebtDue(h))).map(h=>({h,assessment:migrationEmigrationAssessment(h)})).filter(x=>x.assessment.eligible).sort((a,b)=>a.assessment.runwayDays-b.assessment.runwayDays||a.h.id-b.h.id);
    for(const item of choices){if(random()>=item.assessment.probability)continue;selected={id:item.h.id,home:item.h.home,departures:item.h.people.slice(),assessment:item.assessment};break;}}
   metrics.planMs=performance.now()-started;nextContext={...context,rng:rngState,recent:context.recent.slice(),counts:{...context.counts}};boundary('planned');
   started=performance.now();
   if(selected){const ids=new Set(selected.departures);work.people=published.people.slice();for(const id of selected.departures)if(published.people[id]){work.people[id]={...published.people[id]};metrics.ownedPeople++;}work.households=published.households.slice();work.households[selected.id]={...published.households[selected.id]};metrics.ownedHouseholds=1;work.firms=published.firms.slice();for(const f of published.firms)if(f.workers.some(id=>ids.has(id))){work.firms[f.id]={...f};metrics.ownedFirms++;}work.buildings=published.buildings.slice();const homeIndex=published.buildings.findIndex(b=>b.id===selected.home);if(homeIndex>=0){work.buildings[homeIndex]={...published.buildings[homeIndex]};metrics.ownedBuildings=1;}work.events=published.events.slice();}
   cacheBuildingsFor=null;metrics.prepareMs=performance.now()-started;boundary('owned');G=work;
   if(context.owned){migrationReportOwner=work;migrationRecent=nextContext.recent;migrationObservedDay=context.observed;migrationSessionCounts=nextContext.counts;}else{migrationReportOwner=null;migrationRecent=nextContext.recent;migrationObservedDay=context.observed;migrationSessionCounts=nextContext.counts;}
   started=performance.now();
   if(selected){const h=G.households[selected.id],home=readBuild(h.home),departures=selected.departures;
    for(const id of departures){const p=G.people[id];if(!p)continue;p.movedAway=true;p.job=-1;boundary('person');for(const f of G.firms)if(f.workers.includes(id))f.workers=f.workers.filter(n=>n!==id);boundary('workers');}
    h.people=[];G.region+=Math.max(0,h.cash);h.cash=0;boundary('cash');migrationReleaseTenancy(h);boundary('tenancy');migrationRecord('departure',{household:h.id,people:departures.length,assessment:selected.assessment});boundary('report');story('The '+h.name+' family left after a persistent budget shortfall and a better outside reference. Their financial claims and property titles remain recorded.','bad',home?.id||0);boundary('story');recompute();boundary('recompute');
   }
   metrics.applyMs=performance.now()-started;nextContext={rng:rngState,owned:migrationReportOwner===work,recent:migrationRecent.slice(),observed:migrationObservedDay,counts:{...migrationSessionCounts}};
   boundary('before-commit');started=performance.now();freezeNew(work);freezeNew(nextContext);metrics.commitMs=performance.now()-started;root=work;context=nextContext;exportText=null;return {departures:selected?.departures.length||0,metrics};
  }finally{restoreGlobals(saved);active=false;}
 }
 return {run,get current(){return root;},get context(){return context;},auditMs:audited.auditMs,exportCommitted:()=>exportText??(exportText=JSON.stringify({...root,rngState:context.rng}))};
}
