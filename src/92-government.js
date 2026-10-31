function observedChart(key,color='#7f9968'){
 const a=G.observations.slice(-72);if(a.length<2)return tip('Observations accumulate every ten days.');
 const values=a.map(x=>Number(x[key])||0),lo=Math.min(...values),hi=Math.max(...values),span=Math.max(.0001,hi-lo);
 const p=values.map((v,i)=>`${(i/(values.length-1)*330).toFixed(2)},${(100-(v-lo)/span*85).toFixed(2)}`).join(' ');
 return `<svg class="chart-lines" viewBox="0 0 330 115" aria-label="${esc(key)} over time"><path d="M0 100H330M0 57H330M0 15H330" stroke="#bac4a3" fill="none"/><polyline points="${p}" fill="none" stroke="${color}" stroke-width="2"/></svg><div class="miniNote">Day ${a[0].day}–${fromEnd(a).day} · ${fmt(lo)}–${fmt(hi)}</div>`;
}
function policyImpactCard(){
 const e=fromEnd(G.policyExperiments);if(!e)return tip('Enact a policy package to begin a measured before-and-after record. Town readings are sampled every ten simulated days.');
 let later=e.after||null;for(const o of G.observations||[])if(Number(o.day)>Number(e.day)&&(!later||Number(o.day)>Number(later.day)))later=o;
 const before=e.before||{},changes=(e.changes||[]).map(c=>{
  const name=defs.find(d=>d[0]===c.key)?.[1]||c.key;
  return `${esc(name)}: ${esc(fmt(c.from))} → ${esc(fmt(c.to))}`;
 });
 const title=(e.changes||[]).map(c=>defs.find(d=>d[0]===c.key)?.[1]||c.key).join(', ')||'Policy package';
 const keys=new Set((e.changes||[]).map(c=>c.key));
 let metrics=['population','employment','hardship','treasury'];
 if([...keys].some(k=>['healthBudget','educationBudget','aidBudget','energyAidBudget','outreachBudget','roadBudget','transitBudget'].includes(k)))metrics=['medicalCoverage','schoolCoverage','hardship','treasury'];
 else if([...keys].some(k=>['policyRate','bankReserve','lendingRules','depositGuarantee','treasuryInvestment'].includes(k)))metrics=['bankLiquidity','debt','employment','treasury'];
 else if([...keys].some(k=>['importTariff','imports','foodTax'].includes(k)))metrics=['unmetFood','businesses','employment','treasury'];
 else if([...keys].some(k=>['propertyTax','commercialRate','zoningRestriction'].includes(k)))metrics=['vacancy','rentIndex','privateSpend','employment'];
 const specs={population:['Residents','number'],employment:['Employment','percent'],hardship:['Hardship','percent'],treasury:['Municipal cash','money'],medicalCoverage:['Health coverage','fraction'],schoolCoverage:['School funding used','fraction'],bankLiquidity:['Bank liquidity','money'],debt:['Outstanding debt','money'],unmetFood:['Unmet food demand','number'],businesses:['Operating businesses','number'],vacancy:['Unoccupied homes','number'],rentIndex:['Rent index','decimal'],privateSpend:['Private construction spending','money']};
 const value=(key,v)=>{if(v==null||!Number.isFinite(Number(v)))return '—';const type=specs[key][1];return type==='money'?money(v):type==='percent'?fmt(v)+'%':type==='fraction'?fmt(Number(v)*100)+'%':type==='decimal'?fmt(v):fmt(v);};
 let body;
 if(!later){body=`<p class="desc">No post-change reading yet. Town indicators are sampled every ten simulated days; wait for the next reading to compare.</p>`;}
 else {
  const elapsed=Math.max(0,Number(later.day)-Number(e.day));
  const beforeLabel=Number.isFinite(Number(before.day))?(Number(before.day)===Number(e.day)?'before: day '+before.day:'last pre-change reading: day '+before.day):'enactment snapshot';
  body=`<small>${beforeLabel} · AFTER: day ${later.day} (${elapsed} simulated days after enactment)</small>`+
   metrics.map(k=>{const label=specs[k][0],a=Number(before[k]),b=Number(later[k]),valid=before[k]!=null&&later[k]!=null&&Number.isFinite(a)&&Number.isFinite(b);return strip(label,`${value(k,a)} → ${value(k,b)}${valid?' · Δ '+(b-a>0?'+':'')+value(k,b-a):''}`)}).join('')+
   `<p class="desc">These are observed town changes after the package, not proof it caused them. Other events and delayed effects also influence the readings.</p>`;
 }
 return `<div class="council-card"><small>RECENT POLICY · ENACTED DAY ${e.day}</small><h3>${esc(title)}</h3>${changes.map(x=>`<div class="line"><span>${x}</span></div>`).join('')}${body}</div>`;
}
function renderEconomicAtlas(){
 ensureSystems();const m=G.housingMarket,active=G.firms.filter(f=>!f.closed);
 return head('Property & capital')+`<div class="statgrid">${stat('Median home valuation',money(m.medianValue||0))}${stat('Rent index (founding = 1)',fmt(m.rentIndex))}${stat('Unoccupied dwellings',m.vacancy??0)}${stat('Paid construction contracts',money(G.investors[0].spending))}</div>`+
 tip('Valuations respond gradually to rents, access, condition and location. Investors compare operating yields with funding costs. Regional capital is finite; land and construction have recorded counterparties.')+
 head('Housing rents over time')+observedChart('rentIndex')+
 head('A government decision, followed through')+policyImpactCard()+
 head('Freight in the real supply chain')+strip('Cargo currently travelling',(G.freight||[]).length+' consignments')+strip('Cargo and sampled trips completed',fmt(G.transport.arrived))+strip('Blocked cargo-days',fmt(G.transport.delayed))+
 (G.freight||[]).slice(0,8).map(s=>`<div class="entry"><strong>${fmt(s.qty)} ${esc(s.good)}</strong><small>${esc(G.firms[s.from]?.name)} → ${esc(G.firms[s.to]?.name)}<br>${s.delayed?'Delayed by access interruption':s.remaining+' day(s) remaining'} · goods remain owned in transit</small></div>`).join('')+
 head('Physical goods & clearing prices')+`<table class="report-table"><tr><td>Commodity</td><td>Inventory incl. cargo</td><td>Unit price</td></tr>${goodsBalance().map(a=>`<tr><td>${esc(a.good)}</td><td>${fmt(a.stock)}</td><td>${money(a.price)}</td></tr>`).join('')}</table>`+tip('Production, transformation, household use, imports, exports and cargo are counted separately. Wholesale prices adjust gradually to inventory coverage and regional demand.')+head('Recent investment accounts')+G.transactions.slice(-18).reverse().map(t=>`<div class="entry"><strong>${money(t.amount)} · ${esc(t.reason)}</strong><small>Day ${t.day} · ${esc(t.from)} → ${esc(t.to)}</small></div>`).join('');
}
const economyOriginal=renderEconomy;
renderEconomy=function(){return economyOriginal()+renderEconomicAtlas();};
const inspectOriginal=renderInspectFull;
renderInspectFull=function(){
 let html=inspectOriginal(),b=selected?.id?readBuild(selected.id):null;if(!b)return html;
 const owner=b.owner>=0?'The '+(G.households[b.owner]?.name||'unknown')+' household':b.owner===-2?G.investors[0].name:'Regional owner / public authority';
 html+=head('Parcel title & investment')+strip('Recorded owner',owner)+strip('Property valuation',money(b.value))+strip('Legal land footprint',footprintOf(b).length+' tiles')+strip('Physical condition',Math.round(b.condition)+' / 100');
 if(b.kind==='worksite'||b.redevelopment){const p=G.projects.find(p=>p.id===b.id);if(p)html+=head('Construction progress')+strip('Responsible builder',p.builder||'Crew assignment pending')+strip('Work days remaining',p.remaining)+strip('Days stalled',p.stalledDays||0)+tip(p.reason||'Construction financed; crew and materials are allocated daily.');}
 if(b.investment){const q=b.investment;html+=strip('Investment approved','Day '+q.day)+strip('Expected operating yield',(q.yield*100).toFixed(1)+'%')+strip('Funding hurdle',(q.hurdle*100).toFixed(1)+'%')+strip('Construction budget',money(q.cost))+strip('Land consideration',money(q.land))+tip('Expected returns are the developer’s estimate at approval; realized returns can differ.');}
 html+=G.transactions.filter(t=>t.entity===b.id).slice(-5).reverse().map(t=>`<div class="entry"><strong>${esc(t.reason)}</strong><small>Day ${t.day} · ${money(t.amount)} · ${esc(t.from)} → ${esc(t.to)}</small></div>`).join('');
 return html;
};
const settingsOriginal=renderSettingsFull;
renderSettingsFull=function(){
 const p=perfStats;
 return `<div class="btnrow"><button id="recoverAutosave">Recover previous autosave</button></div>`+head('Views of the Vale')+`<div class="maptool-row"><button id="nightView">${nightMode?'Morning light':'Evening light'}</button><button data-district="all">Whole borough</button><button data-district="main">Market district</button><button data-district="farms">Farm belt</button><button data-view="land">Land values</button><button data-view="roads">Road access</button></div>`+
 head('Session diagnostics')+strip('Draw CPU median / p95',percentile(p.frames,.5).toFixed(2)+' / '+percentile(p.frames,.95).toFixed(2)+' ms')+strip('Daily simulation median / p95',percentile(p.ticks,.5).toFixed(2)+' / '+percentile(p.ticks,.95).toFixed(2)+' ms')+strip('Requested / measured speed',speed+'× / '+p.effective.toFixed(1)+'×')+strip('Queued simulation',p.backlog.toFixed(1)+' days')+strip('Largest cash ledger drift',money(G.accounts?.maxError||0))+tip('CPU timings in this session are not device FPS or a thermal measurement. Measured speed counts completed simulation days. CPU work and queued wall time are bounded to keep controls responsive.')+
 settingsOriginal();
};
function navigateDistrict(which){
 const list=which==='farms'?G.buildings.filter(b=>b.kind==='farm'):which==='main'?G.buildings.filter(b=>b.firm>=0&&!['farm','forestry','quarry'].includes(b.kind)):G.buildings;
 if(!list.length)return;const x=list.reduce((n,b)=>n+b.x,0)/list.length,y=list.reduce((n,b)=>n+b.y,0)/list.length,p=iso(x,y);
 cam.x=p[0];cam.y=p[1]+18;cam.zoom=which==='all'?.59:1.35;closePanel();dirty=true;
}
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b||!G)return;
 if(b.id==='recoverAutosave'){try{const e=readSaveEnvelope(localStorage.getItem('townledger-v6-backup'));if(e&&hydrateSave(e.payload)){toast('Previous autosave recovered. Export it to keep a separate copy.');renderPanel('settings');}else toast('No valid earlier autosave is available.');}catch(_){toast('No valid earlier autosave is available.');}}
 if(b.id==='nightView'){nightMode=!nightMode;clearAtlas();dirty=true;renderPanel('settings');}
 if(b.dataset.district)navigateDistrict(b.dataset.district);
 if(b.dataset.view){overlay=b.dataset.view;closePanel();dirty=true;toast(overlay==='land'?'Land values: green low · gold middle · copper high':'Road access: green connected · copper disconnected');}
});
// Android uses the system document picker; desktop retains the text archive workflow.
window.__townArchive={
 suspend:()=>{hostSuspended=true;acc=0;last=performance.now();stopGameAudio();return save();},
 prepareExit:()=>G?window.__townArchive.suspend():Promise.resolve(true),
 resume:()=>{hostSuspended=false;acc=0;last=performance.now();refreshAmbience();},
 export:()=>archivePayload(),
 restore:text=>{const ok=hydrateSave(text);if(ok){save();$('welcome').style.display='none';dirty=true;staticDirty=true;if(active){renderPanel(active);$('panelClose').focus();}toast('Town restored with its property, bank, cargo and resident records.');}else toast(archiveRestoreError(text));return ok;},
 back:()=>{if($('helpDialog').style.display!=='none'){hideHelpDialog();return true;}if(pendingEvent){closeCouncilDialog(true);return true;}if(active){closePanel();return true;}if(buildMode){closeBuildTool();return true;}return false;}
};
const originalExport=exportSave,originalImport=importSave;
exportSave=function(){if(window.AndroidArchive)window.AndroidArchive.writeBackup(archivePayload());else originalExport();};
importSave=function(){if(window.AndroidArchive)window.AndroidArchive.openBackup();else originalImport();};

if($('townSeed')){try{$('townSeed').value=String(crypto.getRandomValues(new Uint32Array(1))[0]||42);}catch(_){$('townSeed').value=String(Date.now()%4294967295||42);}}
