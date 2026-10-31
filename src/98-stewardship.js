// Dated achievements remain history; current district services still deserve attention.
let civicWatchCache=null;
function civicStewardship(force=false){
 if(!G)return [];const projects=Object.values(G.civicProjects?.active||{}).filter(p=>p.kind==='district'&&p.status==='complete');if(!projects.length)return [];
 const net=graph(),key=[G.day,G.buildings.length,G.finance?.insolvencies||0,projects.map(p=>p.id+':'+p.target+':'+G.districtProgrammes?.[p.target]?.focus).join('|')].join('/');
 if(!force&&civicWatchCache?.town===G&&civicWatchCache.net===net&&civicWatchCache.key===key)return civicWatchCache.issues;
 const issues=[];
 for(const project of projects){
  const parcel=ANNEX_PARCELS.find(p=>p.id===project.target),focus=G.districtProgrammes?.[project.target]?.focus;if(!parcel||focus!==project.branch)continue;
  const companies=G.firms.filter(f=>{const b=readBuild(f.building);return b&&civicBlueprintInside(parcel,b.x,b.y);}),metrics=districtMetrics(parcel.id);
  const add=(title,detail,firm,kind,severity='watch')=>issues.push({project:project.id,parcel:parcel.id,title:parcel.name+': '+title,detail,firm:firm?.id??null,building:firm?.building??null,kind,severity,closedDay:firm?.closedDay??null});
  const role=(kind,label)=>{
   const active=companies.filter(f=>f.kind===kind&&!f.closed),attending=active.find(f=>workingStaff(f).length>0);
   if(attending){if(attending.netProfit<0&&attending.cash<Math.max(1,-attending.netProfit)*30)add(label+' has a thin cash cushion','Latest operating loss '+money(-attending.netProfit)+'; cash '+money(attending.cash)+'. Compare paid traffic with payroll. This is a recent observation, not a forecast.',attending,kind);return;}
   const closed=companies.filter(f=>f.kind===kind&&f.closed).sort((a,b)=>(b.closedDay||0)-(a.closedDay||0))[0];
   if(!active.length&&closed)add(label+' closed',closed.name+' is closed; its operating account shows '+money(closed.cash)+'. The delivered project record stays intact; inspect the account, replace the missing activity, or review a different future charter.',closed,kind,'urgent');
   else if(active.length)add(label+' has no attending crew','The structure exists, but no workers currently attend. Inspect jobs and road access before buying another building.',active[0],kind);
   else add(label+' is no longer present','The district’s earlier record includes this activity. Review current structures and a complete recovery blueprint.',null,kind,'urgent');
  };
  if(project.branch==='waterfront'){role('fishery','Fishery');role('wharf','Cargo wharf');}
  else if(metrics.staffed<2){const closed=companies.filter(f=>f.closed).sort((a,b)=>(b.closedDay||0)-(a.closedDay||0))[0];add('local workplaces need attention',metrics.staffed+' firms currently have attending staff. The district’s earlier delivery record does not guarantee continuing operation.',closed,null,closed?'urgent':'watch');}
  else if(project.branch==='neighbourhood'&&metrics.pop>=8&&(metrics.care<.4||metrics.school<.4))add('local care or teaching has slipped','Current resident access: care '+fmt(metrics.care*100)+'%, teaching '+fmt(metrics.school*100)+'%. Compare local public places, qualified staff and purchased private teaching.',null,'school');
 }
 issues.sort((a,b)=>Number(b.severity==='urgent')-Number(a.severity==='urgent')||(b.closedDay||0)-(a.closedDay||0));civicWatchCache={town:G,net,key,issues};return issues;
}
function civicWatchForProject(project){return civicStewardship().filter(i=>i.project===project.id);}
function civicReviewRecharter(parcelId){
 const p=G.civicProjects?.active.district,plan=G.districtProgrammes?.[parcelId];if(!p||p.target!==parcelId||!plan)return;
 showCustomEvent('CIVIC PROJECT','A different future for '+ANNEX_PARCELS.find(a=>a.id===parcelId).name,'Revising this charter costs $1,200 and requires 30 days since its prior designation. Existing private titles, buildings, cargo and debts remain. New permissions do not convert or demolish an old business. A new district project will record the chosen purpose; the earlier certificate remains in history.',Object.entries(DISTRICT_FOCI).filter(([key])=>key!==plan.focus&&!(key==='waterfront'&&parcelId!=='river-reach')).map(([focus,definition])=>({title:'Recharter as '+definition.name,desc:definition.description,cost:1200,apply:()=>{if(!chooseDistrictFocus(parcelId,focus)){toast('The revision interval or funds do not permit this charter yet.');return;}civicProjectStart('district',focus,parcelId);openCivicProjects('district');}})));
}
const civicWatchCardBase=civicProjectCard;civicProjectCard=function(project){
 let html=civicWatchCardBase(project);const issues=civicWatchForProject(project);if(!issues.length)return html;
 const content=`<section class="civic-watch-line" aria-label="Current district stewardship"><strong>Current operating check</strong>${issues.map(i=>`<p class="desc"><b>${esc(i.title)}</b><br>${esc(i.detail)}</p>${i.building?`<button data-inspect="${i.building}">Inspect the actual business</button>`:''}`).join('')}<div class="btnrow"><button data-civic-project-road>Review a recovery blueprint</button>${[...new Set(issues.map(i=>i.kind).filter(k=>CIVIC_BLUEPRINT_KINDS[project.branch].includes(k)))].map(kind=>`<button data-civic-project-build="${kind}" data-civic-project-kind="district">Survey replacement ${esc(types[kind].n.toLowerCase())}</button>`).join('')}<button data-civic-recharter="${project.target}">Compare a different future charter</button><button data-mayor-panel="community">Review local service provision</button></div></section>`;
 return html.replace('<div class="btnrow">',content+'<div class="btnrow">');
};
const civicWatchStatusBase=updateMapStatusDeck;const civicWatchSignal=document.createElement('div');civicWatchSignal.id='civicWatchSignal';civicWatchSignal.hidden=true;$('mapStatusDetails').prepend(civicWatchSignal);
updateMapStatusDeck=function(){
 civicWatchStatusBase();if(!G)return;const issue=civicStewardship()[0],caption=$('mapStatusToggle').querySelector('.map-status-caption'),label=issue?.severity==='urgent'?'TOWN SIGNALS · OPERATING ALERT':'TOWN SIGNALS';if(caption.textContent!==label)caption.textContent=label;
 if(issue){headerText('mapStatusHeadline',issue.title);const text=issue.title+' — '+issue.detail;if(civicWatchSignal.dataset.issue!==text){civicWatchSignal.dataset.issue=text;civicWatchSignal.innerHTML=`<p>${esc(issue.detail)}</p><button data-civic-watch-project="${issue.project}">Review ${esc(ANNEX_PARCELS.find(p=>p.id===issue.parcel).name)}</button>`;}civicWatchSignal.hidden=false;}
 else{civicWatchSignal.hidden=true;}
 const urgent=issue?.severity==='urgent';if($('mapStatusToggle').classList.contains('operating-alert')!==!!urgent)$('mapStatusToggle').classList.toggle('operating-alert',!!urgent);
};
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b||!G)return;if(b.dataset.civicRecharter)civicReviewRecharter(b.dataset.civicRecharter);if(b.dataset.civicWatchProject)openCivicProjects('district');});

const civicWatchResetBase=resetTownTransientUI;resetTownTransientUI=function(){civicWatchCache=null;civicBlueprintCacheTown=null;civicBlueprintCache.clear();civicWatchResetBase();};
