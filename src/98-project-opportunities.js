// Concrete civic projects orchestrate existing safe actions. They own no money or goods.
const CIVIC_PROJECT_KINDS=['food','district','skills'];
function civicProjectState(){return G.civicProjects||{version:1,serial:0,lastDay:G.day,active:{},history:[],declined:[]};}
function ensureCivicProjects(){if(!G.civicProjects)G.civicProjects=civicProjectState();return G.civicProjects;}
function civicProjectTargetHousehold(privateOnly=false){
 let best=null;for(const h of G.households){if(!h.people.length||!readBuild(h.home)||privateOnly&&!h.people.some(id=>privateEligiblePupil(G.people[id])))continue;const coverage=localCivicCoverage('school',h.id),liquidity=householdLiquidity(h)/h.people.length;
 if(!best||coverage<best.coverage||coverage===best.coverage&&(liquidity<best.liquidity||liquidity===best.liquidity&&h.id<best.h.id))best={h,coverage,liquidity};}
 return best?.h;
}
function civicProjectGrocer(){return G.firms.filter(f=>!f.closed&&f.kind==='grocer'&&readBuild(f.building)).sort((a,b)=>((a.stock.food||0)+pendingGoods(a,'food'))/Math.max(1,reachableRetailDemand(a))-((b.stock.food||0)+pendingGoods(b,'food'))/Math.max(1,reachableRetailDemand(b))||a.id-b.id)[0];}
function civicProjectTitle(p){return p.kind==='food'?'The fresh-food circuit':p.kind==='district'?'A gateway worth building':'The school-to-work promise';}
function civicProjectStart(kind,branch,target){
 if(!CIVIC_PROJECT_KINDS.includes(kind))return false;
 if(kind==='food'&&(!['bridge','local'].includes(branch)||!G.firms[target]||G.firms[target].closed||G.firms[target].kind!=='grocer'))return false;
 if(kind==='district'&&(!owns(DISTRICT_FOCI,branch)||!ANNEX_PARCELS.some(a=>a.id===target)||branch==='waterfront'&&target!=='river-reach'))return false;
 if(kind==='skills'&&(!['network','campus','private'].includes(branch)||!G.households[target]?.people.length))return false;
 const s=ensureCivicProjects(),old=s.active[kind];if(old){s.history.unshift({...old,status:old.status==='complete'?'complete':'replanned',closed:G.day});s.history.length=Math.min(s.history.length,9);}
 s.declined=s.declined.filter(k=>k!==kind);s.active[kind]={id:++s.serial,kind,branch,target,started:G.day,lastDay:G.day,status:'active',orders:[],arrived:0,firm:null,building:null,output:0,sales:0,net:0,trainingScope:kind==='skills'&&branch==='private'?'private':'all',trainingBaseline:kind==='skills'&&branch==='private'?(G.privateTrainingCompletions||0):programmeMetrics().training,learning:0,completed:null,proof:null};
 story('Civic project adopted: '+civicProjectTitle(s.active[kind])+'. '+(kind==='district'?DISTRICT_FOCI[branch].name:kind==='food'?branch==='bridge'?'A paid import bridge for an identified shop.':'A local producer must earn actual sales.':branch==='network'?'Fund and staff existing reachable schools.':branch==='private'?'Invite independently financed teaching and compare actual affordability.':'Investigate an additional reachable school site.'),'neutral');save();return true;
}
function civicProjectObservation(p){
 const m=programmeMetrics();
 if(p.kind==='food'){
  const shop=G.firms[p.target],f=p.firm==null?null:G.firms[p.firm],pending=(G.regionalTrade?.shipments||[]).filter(o=>p.orders.includes(o.id)),late=pending.filter(o=>o.due<G.day);
  const evidence=p.branch==='bridge'?fmt(p.arrived)+' / 180 commissioned food units arrived':fmt(p.output)+' produced · '+fmt(p.sales)+' sold · accumulated operating result '+money(p.net);
  const shopReady=!!shop&&!shop.closed&&workingStaff(shop).length>0,met=shopReady&&(p.branch==='bridge'?p.arrived>=179.999&&m.food>=95:!!f&&!f.closed&&workingStaff(f).length>0&&p.output>=120&&p.sales>=100&&p.net>=0&&m.food>=95);
  const setback=!shop||shop.closed?'The named shop has closed. Replan around a trading shop; paid cargo remains in the normal freight system.':!shopReady?'The named shop needs attending retail staff before this circuit can count as usable. Review its jobs and access.':late.length?'Commissioned cargo is past its expected date. Inspect the route and loading before ordering more.':p.branch==='local'&&f?.closed?'The commissioned producer closed. Inspect losses and consider an import bridge instead.':p.branch==='local'&&f&&p.net<0?'The producer has not paid its way. Check inputs, customers and labour before commissioning another.':'';
  return {met,evidence,detail:'Observed food need supplied '+fmt(m.food)+'%. '+(pending.length?pending.length+' commissioned loads still travelling. ':'')+'Completion needs reliable food supply as well as the project’s deliveries or a viable producer.',setback};
 }
 if(p.kind==='district'){
  const owned=G.charter.owned.includes(p.target),plan=G.districtProgrammes?.[p.target],dm=owned?districtMetrics(p.target):null;
  return {met:!!plan&&plan.focus===p.branch&&plan.completed,evidence:owned?dm.connected+' connected properties · '+dm.staffed+' staffed firms · '+dm.pop+' residents':'Development rights not yet acquired',detail:DISTRICT_FOCI[p.branch].goal+' '+(plan?.focus===p.branch?(plan.completed?'District established.':plan.held+' / 30 actual qualifying days.'):'Record the intended charter after purchase.'),setback:plan&&plan.focus!==p.branch?'The current charter differs from this project. Review rezoning costs and the 30-day revision limit, or replan the project.':''};
 }
 const h=G.households[p.target],coverage=h?.people.length?localCivicCoverage('school',h.id):0,privateShare=G.privateServiceProvision?.school?.[p.target]||0,privateRoute=p.branch==='private',terms=Math.max(0,(privateRoute?(G.privateTrainingCompletions||0):p.trainingScope==='all'?m.training:(G.civicTrainingCompletions||0))-p.trainingBaseline);
 const met=privateRoute?privateShare>0&&(p.learning||0)>=30&&terms>=1&&m.reserve>=20:coverage>=.6&&terms>=1&&m.reserve>=20;
 return {met,evidence:privateRoute?'Target family '+fmt(p.learning||0)+' paid learner-days · '+terms+' fee-funded terms completed':'Target household teaching access '+fmt(coverage*100)+'% · '+terms+' new adult training terms completed',detail:privateRoute?'Purchase 30 quality-adjusted learner-days for the named household, complete one actual fee-funded term in town, and retain 20 authorized spending days. Independent proposals need financing approval and 45 funded construction workdays, then qualified staff and fee-paying learners. A term needs 120 equivalent paid teaching days.':'Deliver at least 60% funded access to the named household, finish one actual adult term, and retain 20 authorized spending days. A term needs 120 equivalent funded teaching days; recruitment takes 30 days.',setback:!h?.people.length?'The target household no longer lives here. Replan for a resident household.':m.reserve<20?'Cash covers less than 20 authorized spending days. Review the recurring promise before increasing it.':''};
}
function civicProjectRecordArrival(order){
 const p=G.civicProjects?.active.food;if(!p||p.status!=='active'||!p.orders.includes(order.id))return;
 p.arrived+=order.qty;p.orders=p.orders.filter(id=>id!==order.id);
}
// Observe the existing settlement boundary, rather than trusting its bounded recent log.
const projectRegionalFreightBase=regionalFreightDay;
regionalFreightDay=function(){
 const town=G,p=G.civicProjects?.active.food,tracked=p?.status==='active'?(G.regionalTrade?.shipments||[]).filter(o=>p.orders.includes(o.id)):[];
 projectRegionalFreightBase();if(G!==town||!tracked.length)return;
 const pending=new Set((G.regionalTrade?.shipments||[]).map(o=>o.id));
 for(const order of tracked)if(!pending.has(order.id))civicProjectRecordArrival(order);
};
function civicProjectsDay(){
 const s=G.civicProjects;if(!s||s.lastDay===G.day)return;s.lastDay=G.day;
 for(const p of Object.values(s.active)){
  if(p.status!=='active'||p.lastDay===G.day)continue;p.lastDay=G.day;
  if(p.kind==='food'){
   for(const o of G.regionalTrade?.recent||[])civicProjectRecordArrival(o);
   const f=p.firm==null?null:G.firms[p.firm];if(f){p.output+=Math.max(0,f.production||0);p.sales+=Math.max(0,f.salesQty||0);p.net+=Number(f.operating?.netProfit)||0;}
  }
  if(p.kind==='skills'&&p.branch==='private'&&G.privateServiceProvision?.day===G.day){const h=G.households[p.target];p.learning=(p.learning||0)+(G.privateServiceProvision.school[p.target]||0)*(h?.people.length||0);}
  const o=civicProjectObservation(p);if(!o.met)continue;p.status='complete';p.completed=G.day;p.proof=o.evidence;
  story('Civic project delivered: '+civicProjectTitle(p)+'. '+o.evidence+'. The achievement records real provision; no cash bonus was created.','good');
 }
}
function civicProjectLot(kind,anchor,parcelId=null){
 const net=graph(),p=parcelId&&ANNEX_PARCELS.find(a=>a.id===parcelId),candidates=[];
 const minX=p?p.x:Math.max(2,anchor.x-14),maxX=p?p.x+p.w-1:Math.min(T-3,anchor.x+14),minY=p?p.y:Math.max(2,anchor.y-14),maxY=p?p.y+p.h-1:Math.min(T-3,anchor.y+14);
 for(let y=minY;y<=maxY;y++)for(let x=minX;x<=maxX;x++)candidates.push({x,y,d:Math.abs(x-anchor.x)+Math.abs(y-anchor.y)});
 candidates.sort((a,b)=>a.d-b.d||a.y-b.y||a.x-b.x);
 return candidates.find(c=>canPlace(c.x,c.y,true,kind)&&footprintFor(c.x,c.y,kind).every(id=>!p||parcelForTile(id%T,id/T|0)?.id===p.id)&&footprintFor(c.x,c.y,kind).some(id=>roadOffsets.some(([dx,dy])=>{const q=roadId(id%T+dx,(id/T|0)+dy);return net.parts[q]===net.mainPart&&net.neighbors.has(q)})))||null;
}
function civicProjectRoadPlan(parcelId){
 const p=ANNEX_PARCELS.find(a=>a.id===parcelId);if(!p)return null;const net=graph(),sources=[...net.neighbors.keys()].filter(id=>net.parts[id]===net.mainPart).sort((a,b)=>a-b),prev=new Int32Array(T*T);prev.fill(-2);const queue=[];
 for(const id of sources){prev[id]=-1;queue.push(id);}
 const center={x:p.x+Math.floor(p.w/2),y:p.y+Math.floor(p.h/2)},eligible=(x,y)=>{if(x<0||y<0||x>=T||y>=T)return false;const id=roadId(x,y);return (charterOwns(x,y)||parcelForTile(x,y)?.id===p.id)&&[0,1,3].includes(G.tiles[id])&&!buildingAt(x,y)&&!G.landUse?.[id];};
 let end=null;for(let n=0;n<queue.length;n++){const id=queue[n],x=id%T,y=id/T|0;if(parcelForTile(x,y)?.id===p.id&&Math.abs(x-center.x)+Math.abs(y-center.y)<=3){end=id;break;}for(const [dx,dy] of [[1,0],[0,1],[-1,0],[0,-1]]){const xx=x+dx,yy=y+dy;if(!eligible(xx,yy))continue;const next=roadId(xx,yy);if(prev[next]!==-2)continue;prev[next]=id;queue.push(next);}}
 if(end==null)return null;const path=[];for(let id=end;id>=0;id=prev[id])path.push(id);path.reverse();const cells=path.filter(id=>G.tiles[id]!==1);return {path,cells,cost:cells.length*buildCost.road,end};
}
function civicProjectPlanSvg(cells,focus){
 const anchor=focus||{x:cells[0]%T,y:cells[0]/T|0},r=5,marks=new Set(cells),x0=clamp(anchor.x-r,0,T-r*2-1),y0=clamp(anchor.y-r,0,T-r*2-1),n=r*2+1;
 let tiles='';for(let y=y0;y<y0+n;y++)for(let x=x0;x<x0+n;x++){const id=roadId(x,y),b=buildingAt(x,y),color=marks.has(id)?'#d8a94f':b?'#876d57':G.tiles[id]===1?'#8a998f':G.tiles[id]===2?'#71a7ad':G.tiles[id]===3?'#63896a':'#d0d9b8';tiles+=`<rect x="${(x-x0)*12}" y="${(y-y0)*12}" width="11" height="11" fill="${color}"/>`;}
 return `<svg class="civic-project-plan" viewBox="0 0 ${n*12} ${n*12}" role="img" aria-label="Survey at grid ${anchor.x}, ${anchor.y}; gold is proposed work, grey existing roads, brown buildings, blue water">${tiles}</svg><p class="desc">Gold: proposed work · grey: road · brown: occupied · blue: water. Grid ${anchor.x}, ${anchor.y}; schematic, north at top.</p>`;
}
let civicProjectSurveyTarget=null;
function civicProjectVisit(x,y,kind='',projectKind=''){
 if(!kind&&buildMode)closeBuildTool();
 if(kind&&projectKind){const project=G.civicProjects?.active[projectKind];civicProjectSurveyTarget=project?{town:G,id:project.id,projectKind,kind,x,y}:null;}
 overlay='none';parcelFocus=null;
 if(kind){buildMode=kind;pointer.hover={x,y};$('placementHint').style.display='block';$('placementHint').textContent='PROJECT SITE · '+types[kind].n.toUpperCase()+' · TAP TO BUILD OR BACK TO CANCEL';}
 const pos=iso(x,y);cam={x:pos[0],y:pos[1]+25,zoom:.85};closePanel();dirty=true;
}
// A surveyed site may be commissioned in the review or built with a real map tap.
const projectConstructBase=construct;
construct=function(kind,x,y,quiet=false){
 const before=G?.nextId;projectConstructBase(kind,x,y,quiet);const target=civicProjectSurveyTarget;
 if(!target||G!==target.town||kind!==target.kind||x!==target.x||y!==target.y)return;
 const p=G.civicProjects?.active[target.projectKind],b=G.buildings.find(b=>b.id>=before&&b.kind===kind&&b.x===x&&b.y===y);
 if(p?.id===target.id&&b){p.building=b.id;if(p.kind==='food')p.firm=b.firm;civicProjectSurveyTarget=null;save();}
};
const projectCloseBuildBase=closeBuildTool;closeBuildTool=function(){civicProjectSurveyTarget=null;projectCloseBuildBase();};
function civicProjectReviewBuild(kind,projectKind){
 const project=G.civicProjects?.active[projectKind];if(!project||project.status!=='active')return;
 const parcel=projectKind==='district'?ANNEX_PARCELS.find(a=>a.id===project.target):null,anchor=parcel?{x:parcel.x+Math.floor(parcel.w/2),y:parcel.y+Math.floor(parcel.h/2)}:projectKind==='skills'?readBuild(G.households[project.target]?.home):readBuild(G.firms[project.target]?.building);
 if(!anchor)return;const lot=civicProjectLot(kind,anchor,parcel?.id);if(!lot){toast('No connected, legally vacant site fits this project. Build a street connection or choose a site manually in Public Works.');return;}
 const cost=buildCost[kind],town=G,pid=project.id;
 showCustomEvent('CIVIC PROJECT',types[kind].n+' at grid '+lot.x+', '+lot.y,'Authorize the existing construction purchase: '+money(cost)+' from municipal cash. Treasury after purchase '+money(G.treasury-cost)+'. '+(kind==='school'?'The school still needs reachable pupils, qualified staff and recurring funding.':'The enterprise still needs workers, inputs and customers. The current workforce includes '+Math.max(0,G.stats.workforce-G.stats.employed)+' residents without a job; this is not a guarantee they can reach or staff this firm. Normal regional startup investment and permit settlement apply; this is not a guarantee of profit.')+' Existing titles and reservations are preserved.',[
  {title:'Commission this exact site',cost:0,apply:()=>{const p=G.civicProjects?.active[projectKind];if(G!==town||p?.id!==pid||!canPlace(lot.x,lot.y,true,kind)||G.treasury<cost){toast('The site or quote changed. Review the project again.');return;}const id=G.nextId;construct(kind,lot.x,lot.y);const b=G.buildings.find(b=>b.id>=id&&b.kind===kind&&b.x===lot.x&&b.y===lot.y);if(b){p.building=b.id;if(projectKind==='food')p.firm=b.firm;save();}openCivicProjects(projectKind);}},
  {title:'Survey the site first',cost:0,apply:()=>civicProjectVisit(lot.x,lot.y,kind,projectKind)}
 ]);
 const cells=footprintFor(lot.x,lot.y,kind);$('eventText').insertAdjacentHTML('afterend','<div class="civic-project-survey">'+civicProjectPlanSvg(cells,lot)+'</div>');
}
function civicProjectReviewRoad(){
 const p=G.civicProjects?.active.district;if(!p||!G.charter.owned.includes(p.target)){toast('Acquire the district deed before commissioning its road.');return;}
 const plan=civicProjectRoadPlan(p.target);if(!plan){toast('Private titles or terrain block this corridor. Draw an alternative connection in Public Works.');return;}if(!plan.cells.length){toast('The district’s surveyed gateway is already connected.');return;}
 const town=G,pid=p.id,signature=plan.cells.join(',');
 showCustomEvent('CIVIC PROJECT','Commission the district gateway',plan.cells.length+' vacant road tiles to the district interior. Cost '+money(plan.cost)+'; municipal cash afterwards '+money(G.treasury-plan.cost)+'. This opens access, not guaranteed investment. Further streets, staffing and operating services remain separate.',[{title:'Build the surveyed connection',cost:0,apply:()=>{const current=G.civicProjects?.active.district,next=civicProjectRoadPlan(p.target);if(G!==town||current?.id!==pid||!next||next.cells.join(',')!==signature||G.treasury<next.cost){toast('The corridor or funds changed. Review the gateway again.');return;}for(const id of next.cells)construct('road',id%T,id/T|0,true);flushRoadBatch();story('Civic gateway commissioned: '+next.cells.length+' paid road tiles into '+ANNEX_PARCELS.find(a=>a.id===p.target).name+'.','good');openCivicProjects('district');}}]);
 $('eventText').insertAdjacentHTML('afterend','<div class="civic-project-survey">'+civicProjectPlanSvg(plan.cells,{x:plan.end%T,y:plan.end/T|0})+'</div>');
}
function civicProjectReviewFood(){
 const p=G.civicProjects?.active.food,f=p&&G.firms[p.target];if(!p||p.branch!=='bridge'||p.status!=='active'||!f||f.closed)return;
 const remaining=Math.max(0,180-p.arrived-(G.regionalTrade?.shipments||[]).filter(o=>p.orders.includes(o.id)).reduce((n,o)=>n+o.qty,0));if(remaining<.001){toast('The commissioned food is already travelling. Track its actual arrival before ordering again.');return;}
 const q=OUTSIDE_MARKETS.map(m=>regionalQuote(f,m,'food','import')).filter(Boolean).sort((a,b)=>(a.price*(1+G.policy.importTariff/100)+a.freight)-(b.price*(1+G.policy.importTariff/100)+b.freight))[0];if(!q){toast('No regional road reaches this shop. Restore the connection first.');return;}
 const amount=Math.min(remaining,180),cost=amount*(q.price*(1+G.policy.importTariff/100)+q.freight),town=G,pid=p.id;
 showCustomEvent('CIVIC PROJECT','A food bridge for '+f.name,fmt(amount)+' food from '+q.m.name+'; estimated '+money(cost)+' paid by this enterprise, approximately '+q.days+' days in transit. Shop cash '+money(f.cash)+'. Tariffs and freight are included. Imported stock can compete with local producers; loading capacity can split the order. The town gets no grant.',[{title:'Place the paid project order',cost:0,apply:()=>{const current=G.civicProjects?.active.food;if(G!==town||current?.id!==pid||!G.policy.imports||f.closed){toast('The project or import policy changed.');return;}const s=ensureRegionalTrade(),before=s.serial,n=dispatchRegional(f,'food',amount,'import',regionalQuote(f,q.m,'food','import'));if(n>0){current.orders.push(...s.shipments.filter(o=>o.id>before&&o.firm===f.id).map(o=>o.id));save();}else toast('Working capital or loading capacity is unavailable; no order was placed.');openCivicProjects('food');}}]);
}
function civicProjectSchoolBudget(){
 const estimate=Math.ceil(G.stats.population*CIVIC_STANDARDS.school.staff/CIVIC_STANDARDS.school.capacity*Math.max(24,G.policy.minWage)/.65/10)*10,target=clamp(Math.max(G.policy.educationBudget,estimate),0,500),increase=target-G.policy.educationBudget;
 showCustomEvent('CIVIC PROJECT','A recurring teaching promise','Prepare education authorization '+money(target)+'/day, '+money(increase)+'/day above the current setting. Over 120 fully purchased days the additional authorization is '+money(increase*120)+'. Actual purchases depend on reachable places and staff. New buildings are not included. This drafts one policy for review; it does not enact it.',[{title:'Draft the teaching allocation',cost:0,apply:()=>{draftPolicy.educationBudget=target;openPanel('policies');const input=document.querySelector('[data-policy="educationBudget"]');if(input){input.closest('details').open=true;input.scrollIntoView({block:'center'});input.focus();}}}]);
}
function civicProjectOffers(){
 const s=civicProjectState(),offers=[];if(CIVIC_PROJECT_KINDS.every(k=>s.active[k]))return offers;const m=programmeMetrics(),grocer=!s.active.food?civicProjectGrocer():null,h=!s.active.skills&&G.day>1?civicProjectTargetHousehold():null;
 if(!s.active.food&&grocer)offers.push({kind:'food',title:'The fresh-food circuit',signal:G.day===1?'A shop can commission a paid buffer before its shelves run low.':fmt(m.food)+'% of observed food need supplied. '+grocer.name+' holds '+fmt(grocer.stock.food||0)+' food.',text:'Bridge the next deliveries with outside stock, or commission a local producer that must find workers and earn its costs. The routes compete for enterprise cash, municipal capital and labour.',target:grocer.id});
 if(!s.active.district&&(G.regionalTrade?.delivered>0||G.day>=30))offers.push({kind:'district',title:'A gateway worth building',signal:'The town has '+G.charter.owned.length+' acquired outer districts and '+fmt(m.reserve)+' authorized spending days in reserve.',text:'Choose a specific tract and its purpose. Buy its deed, connect its interior, then establish actual activity. A trade park excludes new homes; a neighbourhood excludes heavy industry; a waterfront protects scarce shore lots.'});
 if(!s.active.skills&&h&&G.day>1)offers.push({kind:'skills',title:'The school-to-work promise',signal:fmt(localCivicCoverage('school',h.id)*100)+'% teaching access for the '+h.name+' household.',text:'Fund reachable schools and a full adult training term, or investigate a new campus if places cannot reach this family. Capital and recurring spending compete with the district gateway.',target:h.id});
 return offers;
}
function civicProjectActions(p){
 if(p.status==='complete')return `<button data-civic-project-visit="${p.kind}">Visit the result</button>`+(p.kind==='district'&&ANNEX_PARCELS.some(a=>(G.charter.owned.includes(a.id)||parcelAdjacent(a))&&!G.districtProgrammes?.[a.id]?.completed)?'<button data-civic-project-review="district">Plan the next district</button>':'');
 if(p.kind==='food')return (p.branch==='bridge'?`<button data-civic-project-order ${G.policy.imports?'':'disabled'}>Review the paid food bridge</button>`:p.firm==null?'<button data-civic-project-build="bakery" data-civic-project-kind="food">Survey a local bakery</button>':`<button data-firm="${p.firm}">Inspect the commissioned producer</button>`)+`<button data-civic-project-replan="food">Compare the other food route</button>`;
 if(p.kind==='skills'){if(p.branch==='private')return '<button data-private-invite="school">Invite independently financed school proposals</button><button id="privateServicePolicies">Review licensing, fees & vouchers</button><button data-mayor-panel="community">Inspect actual providers and construction</button>';const access=serviceAccess('school'),b=p.building&&readBuild(p.building);return '<button data-civic-project-budget>Review recurring teaching funds</button>'+(!b&&access.coverage<.95?'<button data-civic-project-build="school" data-civic-project-kind="skills">Survey an additional school</button>':'')+'<button data-mayor-panel="community">Compare staffing, training & providers</button>';}
 const parcel=ANNEX_PARCELS.find(a=>a.id===p.target),owned=G.charter.owned.includes(p.target),focus=G.districtProgrammes?.[p.target]?.focus;
 if(!owned)return `<button data-civic-project-deed>Review the deed · ${money(parcelSurvey(parcel).price)}</button><button data-parcel-preview="${p.target}">Survey the tract</button>`;
 if(focus!==p.branch)return `<button data-civic-project-charter>Review the ${esc(DISTRICT_FOCI[p.branch].name.toLowerCase())} charter</button>`;
 const plan=civicProjectRoadPlan(p.target);if(plan?.cells.length)return `<button data-civic-project-road>Review interior road · ${money(plan.cost)}</button><button data-parcel-preview="${p.target}">Survey the connection</button>`;
 const kinds=p.branch==='industry'?['factory','warehouse']:p.branch==='waterfront'?['fishery','wharf']:['grocer','bakery'];return kinds.map(kind=>{const district=ANNEX_PARCELS.find(a=>a.id===p.target),f=G.firms.find(f=>{const b=readBuild(f.building);return !f.closed&&f.kind===kind&&b&&parcelForTile(b.x,b.y)?.id===district.id;});return f?`<button data-firm="${f.id}">Inspect ${esc(types[kind].n.toLowerCase())} · ${workingStaff(f).length} attending workers</button>`:`<button data-civic-project-build="${kind}" data-civic-project-kind="district">Survey ${esc(types[kind].n.toLowerCase())} · ${money(buildCost[kind])}</button>`;}).join('')+'<button data-civic-project-plan>Plan housing, streets & services</button>';
}
function civicProjectCard(p){
 const o=civicProjectObservation(p),target=p.kind==='district'?ANNEX_PARCELS.find(a=>a.id===p.target).name:p.kind==='food'?G.firms[p.target]?.name:'The '+(G.households[p.target]?.name||'departed')+' household';
 return `<article class="civic-project-card ${p.status==='complete'?'delivered':''}" data-project-card="${p.kind}"><small>${p.status==='complete'?'DELIVERED DAY '+p.completed:'ADOPTED DAY '+p.started} · ${esc(target)}</small><h3>${esc(civicProjectTitle(p))}</h3><b>${esc(p.status==='complete'?(p.proof||o.evidence):o.evidence)}</b>${o.setback&&p.status==='active'?`<p class="civic-project-setback">${esc(o.setback)}</p>`:''}<p class="desc">${esc(p.status==='complete'?'A working result recorded on day '+p.completed+'. Current conditions can still change; the delivered project remains part of the town’s record.':o.detail)}</p><div class="btnrow">${civicProjectActions(p)}</div>${p.status==='active'?`<details><summary>Reconsider this commitment</summary><p class="desc">Replanning or withdrawing changes this project record. Existing deeds, buildings, charter rules, paid cargo and policy commitments remain in force.</p><button data-civic-project-withdraw="${p.kind}">Review withdrawal</button></details>`:''}</article>`;
}
function civicProjectsPanel(){
 const s=civicProjectState(),offers=civicProjectOffers();return `<section id="civicProjects" class="civic-project-board"><small>CONCRETE WORK · COMPETING COMMITMENTS</small><h3>Build something the town can use</h3><p class="desc">Choose what deserves capital, working cash and people. Projects can run together, but draw on the same real economy. They earn a permanent delivery record, not a cash prize.</p>${Object.values(s.active).map(civicProjectCard).join('')}${offers.filter(o=>!s.declined.includes(o.kind)).map(o=>`<article class="civic-project-card"><small>CONDITION-DRIVEN OPPORTUNITY</small><h3>${o.title}</h3><b>${esc(o.signal)}</b><p class="desc">${esc(o.text)}</p><button data-civic-project-review="${o.kind}">Compare the project routes</button><button class="small" data-civic-project-decline="${o.kind}">Pass for now</button></article>`).join('')}${s.declined.length?'<button data-civic-project-restore>Show passed opportunities</button>':''}${s.history.length?'<details><summary>Earlier commitments</summary>'+s.history.map(p=>`<p class="desc">${esc(civicProjectTitle(p))} · ${esc(p.status)} on day ${p.closed}. Existing assets and liabilities continue normally.</p>`).join('')+'</details>':''}</section>`;
}
function openCivicProjects(kind=''){openPanel('agenda');const target=kind?document.querySelector('[data-project-card="'+kind+'"]'):$('civicProjects');target?.scrollIntoView({block:'start'});}
function civicProjectReview(kind,replan=false){
 const old=G.civicProjects?.active[kind],offer=civicProjectOffers().find(o=>o.kind===kind),target=old?.target??offer?.target;
 if(kind==='food'){if(target==null)return;showCustomEvent('CIVIC PROJECT','The fresh-food circuit','Choose a route for '+G.firms[target].name+'. Imports pay a finite food buffer from the shop’s cash and arrive after transit. A local bakery needs a '+money(buildCost.bakery)+' municipal site, regional startup capital, workers, flour and profitable buyers. Either route can disappoint; no artificial reward pays for the decision.',[
  {title:'Adopt the import bridge',desc:'Commission 180 food for the named shop, then verify actual arrivals and food access.',apply:()=>{civicProjectStart('food','bridge',target);openCivicProjects('food');}},
  {title:'Adopt a viable local producer',desc:'Survey and commission a bakery; produce 120, sell 100 and recover operating costs while food need is supplied.',apply:()=>{civicProjectStart('food','local',target);openCivicProjects('food');}}
 ]);return;}
 if(kind==='skills'){if(target==null)return;const access=serviceAccess('school'),privateTarget=civicProjectTargetHousehold(true);showCustomEvent('CIVIC PROJECT','The school-to-work promise','The '+G.households[target].name+' household needs usable teaching. Existing facilities can reach '+fmt(access.coverage*100)+'% of residents before funding and staffing. An adult term requires 120 equivalent funded days. Plan operating funds alongside capital; a private provider also needs viable customers and staff.',[
  {title:'Use the existing school network',desc:'Prioritize funded access and an adult training term; review the recurring allocation before enactment.',apply:()=>{civicProjectStart('skills','network',target);openCivicProjects('skills');}},
  ...(privateTarget?[{title:'Invite independent teaching',desc:'For the '+privateTarget.name+' household: investors assess demand, qualified labour, financing and fees. No municipal site grant; fees and targeted vouchers must fund real teaching.',apply:()=>{civicProjectStart('skills','private',privateTarget.id);openCivicProjects('skills');}}]:[]),
  ...(access.coverage<.95?[{title:'Investigate an additional campus',desc:'Survey a '+money(buildCost.school)+' site; teaching, staffing and maintenance remain recurring commitments.',apply:()=>{civicProjectStart('skills','campus',target);openCivicProjects('skills');}}]:[])
 ]);return;}
 showCustomEvent('CIVIC PROJECT','Choose the district and its purpose','A larger boundary is useful only when it can be reached and supported. Review a tract below; then choose a binding charter. No land is bought in this review.',[{title:'Compare district geography',apply:()=>{openPanel('construction');revealCharterOffice();}}]);
 const candidates=ANNEX_PARCELS.filter(p=>(G.charter.owned.includes(p.id)||parcelAdjacent(p))&&!G.districtProgrammes?.[p.id]?.completed);if(!candidates.length){closeCouncilDialog();toast('Every adjoining district already has an established programme. Review the borough’s completed work.');return;}$('eventText').insertAdjacentHTML('afterend','<div class="civic-project-survey civic-project-choice"><label>Project tract <select id="projectParcel">'+candidates.map(p=>`<option value="${p.id}">${esc(p.name)} · ${G.charter.owned.includes(p.id)?'owned':money(parcelSurvey(p).price)}</option>`).join('')+'</select></label><label>Purpose <select id="projectFocus">'+Object.entries(DISTRICT_FOCI).map(([id,a])=>`<option value="${id}">${esc(a.name)}</option>`).join('')+'</select></label><p class="desc" id="projectDistrictFacts"></p><p class="desc">Trade park: commuters and paid freight. Mixed neighbourhood: homes, local work and care. Working waterfront: scarce shore lots and a real river outlet.</p><button id="projectDistrictAdopt">Adopt this district project</button></div>');
 const surveyFacts=()=>{const parcel=ANNEX_PARCELS.find(p=>p.id===$('projectParcel').value),q=parcelSurvey(parcel),road=civicProjectRoadPlan(parcel.id),option=$('projectFocus').querySelector('option[value="waterfront"]');option.disabled=parcel.id!=='river-reach';if(option.disabled&&$('projectFocus').value==='waterfront')$('projectFocus').value='neighbourhood';$('projectDistrictFacts').textContent=q.land+' land tiles, '+q.water+' water tiles, '+q.forest+' woodland tiles. '+(G.charter.owned.includes(parcel.id)?'Deed already owned.':'Deed '+money(q.price)+'.')+' Surveyed interior connection '+(road?money(road.cost)+' for '+road.cells.length+' new road tiles.':'blocked by terrain or existing titles; an alternative route is needed.')+' '+(parcel.id==='river-reach'?'This is a regional river cargo outlet.':parcel.id==='east-meadow'?'The lake supports fishing, but cannot fulfil a regional cargo-wharf project.':'This inland tract has no regional shipping outlet; choose trade or neighbourhood use.');};
 $('projectParcel').onchange=surveyFacts;surveyFacts();
 $('projectDistrictAdopt').onclick=()=>{const parcel=$('projectParcel').value,focus=$('projectFocus').value;closeCouncilDialog();if(civicProjectStart('district',focus,parcel))openCivicProjects('district');};
}
const projectCloseCouncilBase=closeCouncilDialog;closeCouncilDialog=function(defer=false){
 const opened=[...document.querySelectorAll('[data-project-card] details[open]')].map(d=>d.closest('[data-project-card]').dataset.projectCard);
 document.querySelectorAll('.civic-project-survey').forEach(e=>e.remove());projectCloseCouncilBase(defer);
 for(const kind of opened){const d=document.querySelector('[data-project-card="'+kind+'"] details');if(d)d.open=true;}
};
const projectResetTransientBase=resetTownTransientUI;resetTownTransientUI=function(){civicProjectSurveyTarget=null;document.querySelectorAll('.civic-project-survey').forEach(e=>e.remove());projectResetTransientBase();};
const projectDeskBase=mayorDesk;mayorDesk=function(){const s=civicProjectState(),count=Object.values(s.active).filter(p=>p.status==='active').length;return projectDeskBase().replace('</section>',`<div class="civic-project-shortcut"><button data-civic-projects>Concrete civic projects${count?' · '+count+' underway':''}</button><small>Compare a food circuit, district gateway and school-to-work promise.</small></div></section>`);};
const projectAgendaBase=renderAgenda;renderAgenda=function(){return civicProjectsPanel()+projectAgendaBase();};
document.addEventListener('click',e=>{
 if(!G)return;const b=e.target.closest('button');if(!b)return;
 if(b.hasAttribute('data-civic-projects'))openCivicProjects();
 if(b.dataset.civicProjectReview)civicProjectReview(b.dataset.civicProjectReview);
 if(b.dataset.civicProjectReplan)civicProjectReview(b.dataset.civicProjectReplan,true);
 if(b.dataset.civicProjectDecline){const s=ensureCivicProjects();if(!s.declined.includes(b.dataset.civicProjectDecline))s.declined.push(b.dataset.civicProjectDecline);save();openCivicProjects();}
 if(b.hasAttribute('data-civic-project-restore')){ensureCivicProjects().declined=[];save();openCivicProjects();}
 if(b.dataset.civicProjectWithdraw){const kind=b.dataset.civicProjectWithdraw,p=G.civicProjects?.active[kind];if(p)showCustomEvent('CIVIC PROJECT','Withdraw from '+civicProjectTitle(p)+'?','The record will close. Existing purchased assets, charter rules, policy commitments and cargo remain in the economy. Nothing is refunded or demolished.',[{title:'Withdraw the project record',apply:()=>{const s=ensureCivicProjects();if(s.active[kind]?.id!==p.id)return;s.history.unshift({...p,status:'withdrawn',closed:G.day});s.history.length=Math.min(s.history.length,9);delete s.active[kind];save();openCivicProjects();}}]);}
 if(b.hasAttribute('data-civic-project-deed')){
  const p=G.civicProjects?.active.district;if(!p)return;requestParcelPurchase(p.target);
  if(pendingEvent?.type==='LAND PURCHASE')for(const choice of pendingEvent.choices){const apply=choice.apply;choice.apply=()=>{apply();if(G.civicProjects?.active.district?.id===p.id)openCivicProjects('district');};}
 }
 if(b.hasAttribute('data-civic-project-charter')){
  const p=G.civicProjects?.active.district;if(!p)return;const old=G.districtProgrammes?.[p.target];
  showCustomEvent('CIVIC PROJECT','Record the district’s purpose',DISTRICT_FOCI[p.branch].description+' '+(old?'Revision costs $1,200 and requires 30 days since the prior designation.':'The initial designation has no planning fee.')+' Existing titles remain legal.',[{title:'Record this project charter',apply:()=>{if(!chooseDistrictFocus(p.target,p.branch))toast('The charter could not change. Check the revision interval and available funds.');openCivicProjects('district');}}]);
 }
 if(b.hasAttribute('data-civic-project-order'))civicProjectReviewFood();
 if(b.hasAttribute('data-civic-project-road'))civicProjectReviewRoad();
 if(b.dataset.civicProjectBuild)civicProjectReviewBuild(b.dataset.civicProjectBuild,b.dataset.civicProjectKind);
 if(b.hasAttribute('data-civic-project-budget'))civicProjectSchoolBudget();
 if(b.hasAttribute('data-civic-project-plan')){constructionCategory='housing';openPanel('construction');document.querySelector('.build-grid')?.scrollIntoView({block:'start'});}
 if(b.dataset.civicProjectVisit){const p=G.civicProjects?.active[b.dataset.civicProjectVisit];if(!p)return;if(p.kind==='district')previewParcel(p.target);else{const target=p.building?readBuild(p.building):p.kind==='food'?readBuild(G.firms[p.target]?.building):readBuild(G.households[p.target]?.home);if(target)civicProjectVisit(target.x,target.y);}}
});
function validateCivicProjects(data){
 const s=data.civicProjects;if(s==null)return true;if(s.version!==1||!Number.isSafeInteger(s.serial)||s.serial<0||!Number.isInteger(s.lastDay)||s.lastDay<1||s.lastDay>data.day||!s.active||typeof s.active!=='object'||Array.isArray(s.active)||Object.keys(s.active).length>3||!Array.isArray(s.history)||s.history.length>9||!Array.isArray(s.declined)||s.declined.length>3||new Set(s.declined).size!==s.declined.length||s.declined.some(k=>!CIVIC_PROJECT_KINDS.includes(k)))return false;
 const seen=new Set(),valid=(p,history)=>{if(!p||!CIVIC_PROJECT_KINDS.includes(p.kind)||!Number.isSafeInteger(p.id)||p.id<1||p.id>s.serial||seen.has(p.id)||!Number.isInteger(p.started)||p.started<1||p.started>data.day||!Number.isInteger(p.lastDay)||p.lastDay<p.started||p.lastDay>data.day||!['active','complete','withdrawn','replanned'].includes(p.status)||!Array.isArray(p.orders)||p.orders.length>24||p.orders.some(id=>!Number.isSafeInteger(id)||id<1||(!data.regionalTrade||id>data.regionalTrade.serial))||new Set(p.orders).size!==p.orders.length||!['arrived','output','sales','trainingBaseline'].every(k=>Number.isFinite(p[k])&&p[k]>=0)||!Number.isFinite(p.net)||p.learning!=null&&(!Number.isFinite(p.learning)||p.learning<0)||p.firm!=null&&!data.firms[p.firm]||p.building!=null&&!data.buildings.some(b=>b.id===p.building)||p.trainingScope!=null&&!['all','private'].includes(p.trainingScope)||p.proof!=null&&(typeof p.proof!=='string'||p.proof.length>800)||p.completed!=null&&(!Number.isInteger(p.completed)||p.completed<p.started||p.completed>data.day)||p.status==='complete'&&p.completed==null||history&&(!Number.isInteger(p.closed)||p.closed<p.started||p.closed>data.day)||!history&&!['active','complete'].includes(p.status))return false;
 seen.add(p.id);if(p.kind==='district')return owns(DISTRICT_FOCI,p.branch)&&ANNEX_PARCELS.some(a=>a.id===p.target)&&(p.branch!=='waterfront'||p.target==='river-reach');if(!Number.isInteger(p.target)||p.target<0)return false;return p.kind==='food'?['bridge','local'].includes(p.branch)&&!!data.firms[p.target]&&data.firms[p.target].kind==='grocer':['network','campus','private'].includes(p.branch)&&!!data.households[p.target];};
 return Object.entries(s.active).every(([kind,p])=>p.kind===kind&&valid(p,false))&&s.history.every(p=>valid(p,true));
}

// Keep keyboard navigation in the topmost council/project dialog, including surveys.
$('eventDialog').addEventListener('keydown',e=>{
 if(e.key!=='Tab'||!pendingEvent||$('helpDialog').style.display!=='none')return;
 const items=[...$('eventDialog').querySelectorAll('button:not([disabled]),select:not([disabled]),input:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])')].filter(el=>el.offsetParent!==null);
 if(!items.length)return;const first=items[0],last=fromEnd(items);
 if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
 else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
});
