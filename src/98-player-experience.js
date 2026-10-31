// Mayor's desk: observed choices and earned milestones, never a second economy.
function mayorUnitMoney(value){return '$'+Number(value||0).toLocaleString('en-CA',{minimumFractionDigits:2,maximumFractionDigits:2});}
const TOWN_DIRECTIONS={
 exchange:{title:'The regional crossroads',promise:'Build a dependable trading town',tradeoff:'Imports can relieve shortages quickly, but tie up enterprise cash in transit and compete with local suppliers. Export agreements reserve stock before payment arrives.',steps:[
  ['A road to the wider world','Complete a regional delivery.','delivery','economy'],
  ['A promise kept','Fulfil a supplier agreement with real deliveries.','agreement','economy'],
  ['Room for enterprise','Establish a productive trade-park district.','industry','construction'],
  ['Trade that supports a town','Maintain 75% employment, 95% food supplied and 30 authorized spending days in reserve for 30 days.','resilient','treasury']]},
 river:{title:'The working river',promise:'Make scarce shore land earn its place',tradeoff:'Fishing supplies food within a shared catch limit. Freight needs a river outlet, attending workers and competitive orders; the inland lake cannot ship regional cargo.',steps:[
  ['Crews on the water','Operate a staffed fishery.','fishery','construction'],
  ['Cargo as well as catch','Operate a staffed cargo wharf on a regional river outlet.','wharf','construction'],
  ['A lasting waterfront','Establish a working-waterfront district.','waterfront','construction'],
  ['A river town for families','Maintain 95% food supplied, at most 15% hardship and 30 authorized spending days in reserve for 30 days.','riverLife','community']]},
 community:{title:'The complete neighbourhood',promise:'Grow a place where families can stay',tradeoff:'New land without reachable work, care and teaching creates a burden. Public provision spends municipal funds; private provision needs paying customers and access. Compare actual coverage before choosing either.',steps:[
  ['Daily essentials','Supply 95% of food need with at most 15% household hardship.','essentials','economy'],
  ['Care within reach','Achieve at least 65% funded medical access and 60% funded school access.','services','community'],
  ['Growth with a purpose','Establish a mixed-neighbourhood district.','neighbourhood','construction'],
  ['A secure next generation','Maintain 75% employment, 65% medical access, 60% school access and 30 authorized spending days in reserve for 30 days.','familyLife','community']]}
};
function blankMayorJourney(){return {version:1,direction:'',started:G.day,stage:0,held:0,lastDay:G.day,completed:[],guide:true,visited:[],review:null};}
function ensureMayorJourney(){if(!G.mayorJourney)G.mayorJourney=blankMayorJourney();return G.mayorJourney;}
function mayorJourneyView(){return G.mayorJourney||blankMayorJourney();}
function mayorMetrics(){
 const m=programmeMetrics(),trade=G.regionalTrade||{},plans=Object.values(G.districtProgrammes||{}),staffed=G.firms.filter(f=>!f.closed&&workingStaff(f).length>0);
 return {...m,delivery:(trade.delivered||0)>0,agreement:(trade.contracts||[]).some(c=>c.status==='fulfilled'),industry:plans.some(p=>p.focus==='industry'&&p.completed),waterfront:plans.some(p=>p.focus==='waterfront'&&p.completed),neighbourhood:plans.some(p=>p.focus==='neighbourhood'&&p.completed),fishery:staffed.some(f=>f.kind==='fishery'),wharf:staffed.some(f=>{const b=readBuild(f.building);return f.kind==='wharf'&&b&&waterfrontSite(b.x,b.y,'wharf')})};
}
function mayorStepMet(key,m){
 if(['delivery','agreement','industry','waterfront','neighbourhood','fishery','wharf'].includes(key))return !!m[key];
 if(key==='essentials')return m.food>=95&&m.hardship<=15;
 if(key==='services')return m.medical>=65&&m.school>=60;
 if(key==='resilient')return m.employment>=75&&m.food>=95&&m.reserve>=30;
 if(key==='riverLife')return m.food>=95&&m.hardship<=15&&m.reserve>=30;
 if(key==='familyLife')return m.employment>=75&&m.medical>=65&&m.school>=60&&m.reserve>=30;
 return false;
}
function mayorJourneyDay(){
 const p=ensureMayorJourney();if(p.lastDay===G.day)return;p.lastDay=G.day;
 const d=TOWN_DIRECTIONS[p.direction],s=d&&d.steps[p.stage];if(!s)return;
 const met=mayorStepMet(s[2],mayorMetrics());p.held=met?p.held+1:0;
 if(!met||p.held<(p.stage===3?30:1))return;
 p.completed.push({stage:p.stage,day:G.day});p.stage++;p.held=0;
 story('Town direction: '+s[0]+' achieved. '+(p.stage===4?'The '+d.title.toLowerCase()+' record is complete. Keep governing or try another direction.':'Next: '+d.steps[p.stage][0]+'.'),'good');
}
function validateMayorJourney(data){
 const p=data.mayorJourney;if(p==null)return true;
 if(p.version!==1||!(p.direction===''||owns(TOWN_DIRECTIONS,p.direction))||!Number.isInteger(p.started)||p.started<1||p.started>data.day||!Number.isInteger(p.lastDay)||p.lastDay<p.started||p.lastDay>data.day||!Number.isInteger(p.stage)||p.stage<0||p.stage>4||(!p.direction&&p.stage!==0)||!Number.isInteger(p.held)||p.held<0||p.held>=30||typeof p.guide!=='boolean'||!Array.isArray(p.completed)||p.completed.length!==p.stage||!Array.isArray(p.visited)||p.visited.length>12||p.visited.some(k=>!['economy','businesses','community','construction','treasury','policies','journal','citizens','banking','agenda','overview','settings'].includes(k))||new Set(p.visited).size!==p.visited.length)return false;
 if(p.completed.some((c,i)=>!c||c.stage!==i||!Number.isInteger(c.day)||c.day<p.started||c.day>data.day||(i>0&&c.day<p.completed[i-1].day)))return false;
 if(p.review!=null){const v=p.review;if(!Number.isInteger(v.day)||v.day<1||v.day>data.day||!v.metrics||!['employment','food','hardship','medical','school','reserve'].every(k=>Number.isFinite(v.metrics[k])&&v.metrics[k]>=0&&v.metrics[k]<=1000))return false;}
 return true;
}
function recentTradeSetbacks(){
 const contracts=G.regionalTrade?.contracts||[];return contracts.filter(c=>c.status==='missed'&&G.day>=c.deadline&&G.day-c.deadline<=90&&!contracts.some(next=>next.status==='fulfilled'&&next.market===c.market&&next.id>c.id&&next.deadline>=c.deadline)).sort((a,b)=>b.deadline-a.deadline);
}
function mayorPressureCards(){
 const m=mayorMetrics(),s=G.regionalTrade||{shipments:[],contracts:[]},issues=[];
 const add=(score,title,evidence,cause,panel,label)=>issues.push({score,title,evidence,cause,panel,label});
 if(G.day>1&&m.food<95)add(100,'Put food on the shelves',fmt(m.food)+'% of observed food need supplied','Compare shop stocks, purchasing power and inbound arrival dates. Imports buy a buffer; a local food chain needs workers and inputs.','economy','Compare food routes');
 if(m.reserve<30)add(95,'Protect the next month',fmt(m.reserve)+' days of authorized spending in cash','Review actual receipts, pensions and debt before adding recurring commitments. Borrowing buys time and adds interest.','treasury','Review the cash runway');
 if(m.blocked>0)add(90,'Reconnect paid work',fmt(m.blocked)+' interrupted work journeys','A missing connection can strand existing jobs. Repair access before paying for additional capacity.','construction','Review roads');
 if(m.hardship>15)add(85,'A pay packet is not enough',fmt(m.hardship)+'% of households in hardship','Inspect a family’s wages, rent, essentials and savings before choosing tax relief or targeted support.','citizens','Follow household accounts');
 if(G.day>1&&(m.medical<65||m.school<60))add(75,'Places need people and access','Care '+fmt(m.medical)+'% · learning '+fmt(m.school)+'%','More funding cannot instantly create a qualified worker or a road. Compare public capacity and available private providers before building.','community','Compare provision');
 const transit=G.transit?.daily;if(transit?.denied>0)add(82,'The passenger network is leaving riders behind',fmt(transit.denied)+' peak passengers without a place · '+fmt(transit.rides)+' actual journeys today','Compare the corridor’s actual driver attendance, peak capacity and operating bill. A larger fleet uses municipal capital and qualified workers who may also be needed by schools or businesses.','construction','Review the actual transit corridors');
 const delayed=(s.shipments||[]).filter(o=>o.due<G.day);if(delayed.length)add(92,'Cargo is taking longer',delayed.length+' consignments past expected arrival','Expected arrival is a plan. Review access, loading and buyer liquidity before promising another agreement.','economy','Trace the delay');
 const missed=recentTradeSetbacks();if(missed.length){const c=missed[0],market=OUTSIDE_MARKETS.find(m=>m.id===c.market);add(70,'Review a recent missed window',(market?.name||c.name)+' · '+fmt(c.delivered)+' / '+fmt(c.quantity)+' recorded arrivals; window ended day '+c.deadline,'The past window remains in history. Review uncommitted stock and handling before another promise. This is recent delivery evidence, not a hidden reputation score.','economy','Review the actual agreement');}
 if(G.day===1)add(40,'Take the first council session','Awaiting the first daily settlement','Trace food stocks and enterprise cash now. Let one simulated day finish before judging food and funded service coverage.','economy','Trace the supply chain');
 if(!issues.length)add(30,'Choose what growth is for',fmt(m.employment)+'% employment · '+fmt(m.reserve)+' reserve days','Compare a trade park, a mixed neighbourhood and river frontage. Land choice changes eligible activities and operating needs.','construction','Compare district commitments');
 return issues.sort((a,b)=>b.score-a.score).slice(0,3);
}
function mayorDesk(){
 const p=mayorJourneyView(),d=TOWN_DIRECTIONS[p.direction],s=d&&d.steps[p.stage];
 return `<section class="mayor-desk" aria-label="Mayor’s desk"><div class="mayor-heading"><small>YOUR MAYOR’S DESK · DAY ${G.day}</small><button data-mayor-agenda>Town direction →</button></div><h3>${esc(s?s[0]:d?'A direction earned':'What needs your decision?')}</h3>${s?`<p class="desc">${esc(s[1])} ${p.stage===3?p.held+' / 30 consecutive qualifying days.':''}</p>`:''}<div class="mayor-pressure-grid">${mayorPressureCards().map(i=>`<article><strong>${esc(i.title)}</strong><b>${esc(i.evidence)}</b><button data-mayor-panel="${i.panel}">${esc(i.label)}</button><details><summary>Why this matters</summary><p class="desc">${esc(i.cause)}</p></details></article>`).join('')}</div>${p.guide?mayorGuide(p):`<button class="small" data-mayor-guide="show">Show the optional first council session</button>`}</section>`;
}
const MAYOR_GUIDE=[['economy','Trace one shortage','Compare available food, inbound cargo and the landed price. Return to Town Hall to review an inbound delivery when a suitable shop needs stock.'],['businesses','Meet the supplier','Open a firm and compare sales, payroll, inventory purchases and cash. A profitable quote can still need cash before the truck returns.'],['treasury','Price the commitment','Compare cash with recurring authorization before choosing a new service or district.'],['agenda','Choose a town direction','Pick a route that interests you. Earn progress through actual deliveries, services and connected district activity.']];
function mayorGuide(p){const next=MAYOR_GUIDE.find(x=>!p.visited.includes(x[0]));return `<details class="mayor-guide" ${next?'open':''}><summary>Optional first council session · ${MAYOR_GUIDE.filter(x=>p.visited.includes(x[0])).length} / 4 reports explored</summary>${next?`<strong>${esc(next[1])}</strong><p class="desc">${esc(next[2])}</p><button data-mayor-panel="${next[0]}">Open ${esc(next[1].toLowerCase())}</button>`:'<p class="desc">You have explored the decision loop. Keep a small promise, follow the delivery, then choose where to grow.</p>'}<button class="small" data-mayor-guide="hide">Hide guide</button></details>`;}
function mayorDirectionPanel(){
 const p=mayorJourneyView(),d=TOWN_DIRECTIONS[p.direction],m=mayorMetrics();
 return `<section class="mayor-desk"><small>A TOWN WITH A PURPOSE</small><h3>${esc(d?d.title:'Choose your town’s next story')}</h3><p class="desc">A direction is an optional plan, not a policy preset. It spends no money, changes no rules and gives no cash reward. Build through the real economy. Completed stages stay on this record when conditions later worsen; the final stage needs a sustained healthy town.</p>${d?d.steps.map((s,i)=>`<div class="mayor-stage ${i<p.stage?'earned':''}"><span>${i<p.stage?'ACHIEVED DAY '+p.completed[i].day:i===p.stage?'CURRENT':'LATER'}</span><strong>${i+1}. ${esc(s[0])}</strong><p class="desc">${esc(s[1])}</p>${i===p.stage?`<b>${mayorStepMet(s[2],m)?p.stage===3?p.held+' / 30 qualifying days':'Conditions met; recorded at next day close':'Conditions still need work'}</b><button data-mayor-panel="${s[3]}">Work on this stage</button>`:''}</div>`).join(''):''}<details ${d?'':'open'}><summary>${d?'Compare another direction':'Three different ways to grow'}</summary>${Object.entries(TOWN_DIRECTIONS).map(([id,a])=>`<article class="mayor-direction"><h3>${esc(a.title)}</h3><strong>${esc(a.promise)}</strong><p class="desc">${esc(a.tradeoff)}</p><button data-mayor-direction="${id}" ${id===p.direction?'disabled':''}>Review this direction</button></article>`).join('')}</details></section>`;
}
function mayorReviewPanel(){
 const p=mayorJourneyView(),m=mayorMetrics(),r=p.review,labels={employment:'Employment (%)',food:'Food need supplied (%)',hardship:'Household hardship (%)',medical:'Funded medical access (%)',school:'Funded school access (%)',reserve:'Authorized spending reserve (days)'};
 return `<section class="council-card"><h3>Did the decision help?</h3><p class="desc">Save a comparison before a decision, then return after deliveries or staffing have had time to change. This records observations; other events also affect outcomes.</p>${r?`<p class="desc">Day ${r.day} → ${G.day} · ${G.day-r.day} simulated days observed</p><table class="report-table"><thead><tr><th>Observed measure</th><th>Before</th><th>Now</th></tr></thead><tbody>${Object.entries(labels).map(([k,v])=>`<tr><td>${v}</td><td>${fmt(r.metrics[k])}</td><td>${fmt(m[k])}</td></tr>`).join('')}</tbody></table>`:''}<button data-mayor-baseline>${r?'Review replacing comparison':'Record a comparison'}</button></section>`;
}
function mayorFieldNotes(){
 const delivery=G.regionalTrade?.recent?.[0],household=G.households.filter(h=>h.people.length&&readBuild(h.home)).sort((a,b)=>householdLiquidity(a)/a.people.length-householdLiquidity(b)/b.people.length)[0];
 let html='<section class="council-card"><h3>Field notes from the borough</h3><p class="desc">Accounts and observed access, rather than a random opinion poll. These snapshots can change with tomorrow’s settlement.</p>';
 if(delivery){const f=G.firms[delivery.firm];html+=`<article class="mayor-field-note"><strong>A truck reached its destination</strong><p class="desc">Day ${delivery.arrived}: ${fmt(delivery.qty)} ${esc(delivery.good)} ${delivery.direction==='import'?'arrived for':'was delivered by'} ${esc(f?.name||'a local enterprise')}. ${delivery.direction==='import'?'The purchase used enterprise cash before arrival; the goods are now available inventory.':'The outside buyer paid on arrival; receipts belong to the supplying enterprise.'}</p>${f?`<button data-firm="${f.id}">Follow the enterprise account</button>`:''}</article>`;}
 if(household){const h=household;html+=`<article class="mayor-field-note"><strong>A family with the thinnest liquid cushion</strong><p class="desc">The ${esc(h.name)} household has ${h.people.length} residents and ${money(householdLiquidity(h)/h.people.length)} cash and deposits per resident. Recorded daily income ${money(h.income||0)}, food ${money(h.food||0)}, rent ${money(h.rent||0)} and aid ${money(h.aid||0)}. Inspect other expenses before attributing the result to one policy.</p><button data-house="${h.id}">Visit the household account</button></article>`;}
 for(const id of (G.charter?.owned||[]).slice(0,2)){const district=ANNEX_PARCELS.find(a=>a.id===id),m=districtMetrics(id);html+=`<article class="mayor-field-note"><strong>${esc(district.name)} after the deed</strong><p class="desc">${m.pop} residents, ${m.staffed} staffed firms, ${m.connected} connected properties. Observed resident care ${fmt(m.care*100)}%, school access ${fmt(m.school*100)}%. Land ownership alone supplies none of these.</p><button data-district-review="${id}">Visit the district prospectus</button></article>`;}
 return html+'</section>';
}
const mayorOverviewBase=tradingOverviewBase;renderOverviewFull=function(){return mayorDesk()+tradingTownNextDecision()+`<details class="mayor-report"><summary>Full borough report, programme & trading decisions</summary>`+mayorOverviewBase()+'</details>';};
const mayorAgendaBase=renderAgenda;renderAgenda=function(){return mayorDirectionPanel()+mayorReviewPanel()+mayorFieldNotes()+mayorAgendaBase();};
document.addEventListener('click',e=>{
 if(!G)return;const b=e.target.closest('button');if(!b)return;
 const tab=b.dataset.panel||b.dataset.mayorPanel;if(tab&&owns(names,tab)){const p=ensureMayorJourney();if(!p.visited.includes(tab)){p.visited.push(tab);save();}}
 if(b.hasAttribute('data-mayor-agenda')){openPanel('agenda');$('panelBody').scrollTop=0;}
 if(b.dataset.mayorPanel){openPanel(b.dataset.mayorPanel);$('panelBody').scrollTop=0;}
 if(b.dataset.mayorGuide){ensureMayorJourney().guide=b.dataset.mayorGuide==='show';save();renderPanel('overview');}
 if(b.dataset.mayorDirection){const id=b.dataset.mayorDirection,d=TOWN_DIRECTIONS[id];if(!d)return;showCustomEvent('TOWN DIRECTION',d.title,d.tradeoff+' Choosing this direction starts a new four-stage record. Existing buildings, policies, land and money remain as they are.',[{title:'Choose this town direction',cost:0,apply:()=>{const p=ensureMayorJourney();Object.assign(p,{direction:id,started:G.day,stage:0,held:0,lastDay:G.day,completed:[]});save();renderPanel('agenda');}}]);}
 if(b.hasAttribute('data-mayor-baseline')){const record=()=>{const m=mayorMetrics();ensureMayorJourney().review={day:G.day,metrics:Object.fromEntries(['employment','food','hardship','medical','school','reserve'].map(k=>[k,m[k]]))};save();renderPanel('agenda');};if(mayorJourneyView().review)showCustomEvent('OBSERVED OUTCOMES','Replace the comparison?', 'The earlier comparison will be replaced by today’s observed measures. This does not change the economy.',[{title:'Replace with today',cost:0,apply:record}]);else record();}
});
