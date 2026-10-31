const pointer={down:false,startX:0,startY:0,px:0,py:0,moved:false,pinch:0,buildTrail:0,hover:null};
function toWorld(x,y){const wx=(x-cw/2)/cam.zoom+cam.x,wy=(y-ch/2)/cam.zoom+cam.y;
 let r=(wx-RW/2)/(TW/2),s=(wy-32-TH/2)/(TH/2);return [Math.floor((s+r)/2+.5),Math.floor((s-r)/2+.5)]}
function onTap(sx,sy){if(!G)return;const r=cv.getBoundingClientRect();const [x,y]=toWorld(sx-r.left,sy-r.top);if(!buildMode&&overlay==='charter'&&charterSurveyTap(sx-r.left,sy-r.top,x,y))return;if(x<0||x>=T||y<0||y>=T)return;
 if(buildMode){construct(buildMode,x,y);return}
 const mx=(sx-r.left-cw/2)/cam.zoom+cam.x,my=(sy-r.top-ch/2)/cam.zoom+cam.y;
 if(inspectWaterTripAt(mx,my)||inspectTripAt(mx,my))return;
 let b=buildingAt(x,y);if(!b){const hit=G.buildings.filter(v=>{const pos=iso(v.x,v.y);return Math.abs(mx-pos[0])<20&&my>=pos[1]-38&&my<=pos[1]+33}).sort((a,b)=>iso(b.x,b.y)[1]-iso(a.x,a.y)[1]);b=hit[0]}
 if(b){selected={id:b.id};openPanel('inspect')}else if(!charterOwns(x,y)&&parcelForTile(x,y)){parcelFocus=parcelForTile(x,y).id;openPanel('construction');revealCharterOffice();document.querySelector('[data-parcel-card="'+parcelFocus+'"]')?.scrollIntoView({block:'start'});}else{selected=null;toast('Unoccupied land. Private investors assess access, demand and expected returns.')}
 dirty=true;
}
cv.addEventListener('pointerdown',e=>{if(pointer.down){pointer.moved=true;return;}pointer.activeId=e.pointerId;roadPainted.clear();pointer.lastRoad=buildMode==='road'?toWorld(e.clientX-cv.getBoundingClientRect().left,e.clientY-cv.getBoundingClientRect().top):null;pointer.down=true;pointer.startX=pointer.px=e.clientX;pointer.startY=pointer.py=e.clientY;pointer.moved=false;try{cv.setPointerCapture(e.pointerId)}catch(err){} });
cv.addEventListener('pointermove',e=>{if(!pointer.down){if(buildMode){const r=cv.getBoundingClientRect(),p=toWorld(e.clientX-r.left,e.clientY-r.top);pointer.hover={x:p[0],y:p[1]};dirty=true;}return;}if(pointer.activeId!==e.pointerId||touches.size>1)return;let dx=e.clientX-pointer.px,dy=e.clientY-pointer.py;if(Math.abs(e.clientX-pointer.startX)>7||Math.abs(e.clientY-pointer.startY)>7)pointer.moved=true;
 if(buildMode==='road'){let br=cv.getBoundingClientRect(),pt=toWorld(e.clientX-br.left,e.clientY-br.top);let prev=pointer.lastRoad||pt;let dxg=pt[0]-prev[0],dyg=pt[1]-prev[1],steps=Math.max(Math.abs(dxg),Math.abs(dyg),1);for(let k=0;k<=steps;k++){let ax=Math.round(prev[0]+dxg*k/steps),ay=Math.round(prev[1]+dyg*k/steps),key=ax+'/'+ay;if(!roadPainted.has(key)){roadPainted.add(key);construct('road',ax,ay,true)}}pointer.lastRoad=pt}else{cam.x-=dx/cam.zoom;cam.y-=dy/cam.zoom;cam.x=clamp(cam.x,0,RW);cam.y=clamp(cam.y,0,RH)}pointer.px=e.clientX;pointer.py=e.clientY;let rect=cv.getBoundingClientRect(),tile=toWorld(e.clientX-rect.left,e.clientY-rect.top);pointer.hover={x:tile[0],y:tile[1]};dirty=true});
cv.addEventListener('pointerup',e=>{$('gameRoot').classList.add('map-used');if(pointer.activeId!==e.pointerId)return;if(pointer.down&&!pointer.moved)onTap(e.clientX,e.clientY);flushRoadBatch();pointer.down=false;pointer.activeId=null;pointer.lastRoad=null;roadPainted.clear()});
window.addEventListener('keydown',e=>{
 if(e.key!=='Escape')return;
 if(pendingEvent||$('helpDialog').style.display!=='none'){if(window.__townArchive?.back?.())e.preventDefault();return;}
 if(active){if(window.__townArchive?.back?.())e.preventDefault();return;}
 if(buildMode){closeBuildTool();e.preventDefault();return;}
 // Match Android Back: dismiss the top navigation layer rather than leaving
 // keyboard users stranded behind an open drawer or transient help/archive form.
 if(window.__townArchive?.back?.())e.preventDefault();
});cv.addEventListener('pointercancel',()=>{flushRoadBatch();pointer.down=false;pointer.activeId=null;pointer.lastRoad=null;roadPainted.clear()});cv.addEventListener('pointerleave',()=>{pointer.hover=null;dirty=true});
cv.addEventListener('wheel',e=>{e.preventDefault();cam.zoom=clamp(cam.zoom*(e.deltaY<0?1.12:.89),.025,1.7);dirty=true},{passive:false});
let touches=new Map();cv.addEventListener('touchstart',e=>{touches=new Map([...e.touches].map(t=>[t.identifier,{x:t.clientX,y:t.clientY}]));if(touches.size===2){pointer.moved=true;const a=[...touches.values()];pointer.pinch=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y)}},{passive:true});
cv.addEventListener('touchmove',e=>{touches=new Map([...e.touches].map(t=>[t.identifier,{x:t.clientX,y:t.clientY}]));if(touches.size===2){const a=[...touches.values()],d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);if(pointer.pinch>0){cam.zoom=clamp(cam.zoom*d/pointer.pinch,.025,1.7);dirty=true}pointer.pinch=d}},{passive:true});
cv.addEventListener('touchend',e=>{touches=new Map([...e.touches].map(t=>[t.identifier,{x:t.clientX,y:t.clientY}]));pointer.pinch=0});
cv.addEventListener('touchcancel',()=>{touches.clear();pointer.pinch=0;pointer.down=false;pointer.activeId=null;pointer.lastRoad=null;roadPainted.clear();flushRoadBatch();});
function closeBuildTool(){flushRoadBatch();buildMode='';pointer.hover=null;pointer.down=false;pointer.activeId=null;pointer.lastRoad=null;roadPainted.clear();dirty=true;$('placementHint').style.display='none';$('hint').textContent='DRAG TO PAN · TAP TO INSPECT';toast('Construction tool closed');}
function construct(kind,x,y,quiet=false){
 if(kind!=='inspect'&&!charterOwns(x,y)){if(!quiet)toast('Regional land: purchase the district in Public Works before developing it.');return;}
 if(kind==='inspect'){buildMode='';const target=buildingAt(x,y);if(target){selected={id:target.id};openPanel('inspect')}else toast('No building is present at this lot.');dirty=true;return}
 if(kind==='repair'){if(x<0||x>=T||y<0||y>=T||cityCell(x,y)!==1){if(!quiet)toast('Select an existing road tile to resurface.');return}ensureRoadWear();if(G.roadWear[roadId(x,y)]>96){if(!quiet)toast('This street is already in excellent condition.');return}if(G.treasury<buildCost.repair){if(!quiet)toast('Insufficient town funds.');return}G.treasury-=buildCost.repair;G.region+=buildCost.repair;G.roadWear[roadId(x,y)]=100;G.construction++;staticDirty=true;dirty=true;updateHeader();if(!quiet)toast('Street resurfaced.');return}
 if(kind==='road'){
   if(x<0||x>=T||y<0||y>=T)return;
   if(![0,3].includes(cityCell(x,y))||G.landUse?.[roadId(x,y)]||buildingAt(x,y)){if(!quiet)toast('Road requires vacant, unreserved land.');return}
   if(G.treasury<buildCost.road){if(!quiet)toast('Insufficient town funds for this road.');return}
   G.treasury-=buildCost.road;G.region+=buildCost.road;G.tiles[y*T+x]=1;ensureRoadWear();G.roadWear[roadId(x,y)]=100;G.construction++;dirty=true;
   if(quiet){roadBatchDirty=true;return;}invalidateRoads();staticDirty=true;recompute();updateHeader();save();return;
 }
 if(!canPlace(x,y,true,kind)){toast(['fishery','wharf'].includes(kind)?waterfrontSitingReason(x,y,kind):'This project requires a fully vacant footprint with road access.');return}
 if(kind==='forestry'&&!Array.from({length:25},(_,i)=>[x+(i%5)-2,y+Math.floor(i/5)-2]).some(([a,b])=>cityCell(a,b)===3)){toast('Forestry operations require nearby woodland.');return}
 const cost=buildCost[kind];if(G.treasury<cost){toast('Town treasury cannot afford '+types[kind].n+' ('+money(cost)+').');return}
 G.treasury-=cost;G.region+=cost;
 if(['grocer','bakery','mill','farm','forestry','sawmill','quarry','contractor','tavern','fishery','wharf','factory','warehouse','office','college'].includes(kind)){
   if(G.region<15000){toast('Regional investment capital is exhausted.');G.treasury+=cost;G.region-=cost;return}
   G.region-=12000+G.policy.permitFee;const newFirm=createFirm(kind,x,y);newFirm.cash=12000;transferTreasury(G.policy.permitFee,'permits');assignJobs();story('New local enterprise: '+types[kind].n+' opens on a developed lot.','good');
 }else if(kind==='home'){
   const b={id:G.nextId++,kind,x,y,value:48000,condition:100,owner:-1,firm:-1,hh:-1};G.buildings.push(b);let family={id:G.households.length,name:pick(surnames),cash:rn(900,3000),home:b.id,owner:-1,people:[],income:0,rent:0,food:0,tax:0,aid:0,crimeLoss:0,stress:25,security:85,last:[],worklessness:0};
   G.households.push(family);G.region-=family.cash;G.homes.push(b.id);b.hh=family.id;b.owner=family.id;
   for(let n=0;n<2;n++){let p={id:G.people.length,name:pick(first)+' '+family.name,age:Math.round(rn(19,60)),skill:rn(.3,1),health:rn(65,100),hh:family.id,job:-1,life:65,last:[]};G.people.push(p);family.people.push(p.id)}
   assignJobs();story('A new household settled in the village.','good',b.id,family.id);
 }else G.buildings.push({id:G.nextId++,kind,x,y,value:cost*10,condition:100,owner:-1,firm:-1,hh:-1,footprint:footprintFor(x,y,kind)});
 G.construction++;invalidateRoads();recompute();updateHeader();staticDirty=true;dirty=true;save();toast(types[kind].n+' constructed.');if(active==='construction')renderPanel('construction');
}
function stat(label,value,cls=''){return `<div class="stat"><small>${esc(label)}</small><b class="${cls}">${esc(value)}</b></div>`}
function line(label,value,cls=''){return `<div class="line"><span>${esc(label)}</span><span class="${cls}">${esc(value)}</span></div>`}
function head(s){return `<div class="section">${esc(s)}</div>`}
function chart(field,bad=false){const ar=G.history.slice(-65);if(!ar.length)return '';let vals=ar.map(x=>x[field]),mn=Math.min(...vals),mx=Math.max(...vals),range=Math.max(1,mx-mn);return `<div class="history">${ar.map(x=>`<i class="${bad?'bad':''}" style="height:${Math.max(4,10+90*(x[field]-mn)/range)}%" title="Day ${x.day}: ${fmt(x[field])}"></i>`).join('')}</div><div class="desc">Observations, last ${ar.length} days · range ${fmt(mn)}–${fmt(mx)}.</div>`}
function renderOverview(){const s=G.stats;
 return head('This morning in town')+`<div class="statgrid">${stat('Population',fmt(s.population))}${stat('Employment',s.employment+'%')}${stat('Business doors open',s.businesses+' / '+G.firms.length)}${stat('Households in hardship',s.hardship+'%',s.hardship>30?'negative':'')}</div>`+
 head('Public ledger')+line('Municipal cash',money(G.treasury))+line('Debt',money(G.debt))+line('Outstanding household savings',money(s.cash))+line('Private business capital',money(s.businessCash))+
 head('A village of consequences')+`<p class="desc">Tax and wage decisions affect real household balances. Goods move among farms, mills, bakeries and grocers. Businesses can close, police respond to crime, and the town can face fires. Select any property on the map to inspect its inhabitants or finances.</p>`+
 chart('employment')+head('Latest entries')+G.events.slice(0,8).map(eventHtml).join('');
}
function eventHtml(e){return `<div class="event"><strong>Day ${e.day}</strong> · ${esc(e.text)} ${e.bid>0?`<button class="small" data-inspect="${e.bid}">View</button>`:''}</div>`}
function renderCommunity(){const s=G.stats;
 return head('Community condition')+`<div class="statgrid">${stat('Safety index',s.safety+'/100')}${stat('Crime / last 30 days',fmt(s.dailyCrime))}${stat('Emergency readiness',s.preparedness+'%')}${stat('Households in hardship',s.hardship+'%')}</div>`+
 `<p class="desc">Funding and stations affect response capacity. Hardship, job loss and isolation affect risks. Theft removes real money from victims and transfers it to another local household; incidents are attached to locations.</p>`+
 head('Community expenditure')+line('Policing / day',money(G.policy.policeBudget))+line('Fire & defence / day',money(G.policy.defenseBudget))+line('Housing assistance / day',money(G.policy.aidBudget))+line('Outreach / day',money(G.policy.outreachBudget))+
 head('Local incident register')+(G.cases.length?G.cases.slice(0,15).map(eventHtml).join(''):'<p class="desc">No criminal incidents recorded yet.</p>')+
 head('Safety trend')+chart('safety');
}
function slider(d){let [k,name,lo,hi,step,unit,help]=d,v=G.policy[k];return `<div class="range"><label><b>${esc(name)}</b><span id="show-${k}">${unit==='$'?'$'+fmt(v):fmt(v)+unit}</span></label><input aria-label="${esc(name)}" type="range" min="${lo}" max="${hi}" step="${step}" value="${v}" data-policy="${k}"><div class="desc">${esc(help)}</div></div>`}
function renderPolicies(){return head('A government economics experiment')+`<p class="desc">Move a policy control to enact it immediately. Entries are logged with baseline employment, safety, hardship, cash and business counts. Comparisons are observations, not proof of causation.</p>`+
 defs.map(slider).join('')+head('Trade & exchange')+
 `<div class="line"><span>Allow regional imports</span><button id="tradeToggle" class="small ${G.policy.imports?'on':''}">${G.policy.imports?'ALLOWED':'RESTRICTED'}</button></div><p class="desc">A closed border can interrupt the village supply chain. Tariffs transfer money to the treasury but increase import costs.</p>`;
}
function renderTreasury(){let c=G.cumulative,p=G.policy;
 return head('Municipal accounts')+`<div class="statgrid">${stat('Cash on hand',money(G.treasury),G.treasury<5000?'negative':'')}${stat('Municipal borrowing',money(G.debt))}${stat('Income taxes collected',money(c.incomeTax))}${stat('Business profit taxes',money(c.profitTax))}</div>`+
 head('Receipts since founding')+line('Income tax',money(c.incomeTax))+line('Profit tax',money(c.profitTax))+line('Land and property',money(c.propertyTax))+line('Food sales tax',money(c.foodTax))+line('Business permits',money(c.permits))+line('Import tariffs',money(c.tariffs))+
 head('Expenditure since founding')+line('Public services and subsidies',money(c.spending))+line('Direct housing aid',money(c.welfare))+line('Unpaid principal',money(G.debt))+
 `<div class="btnrow"><button id="borrow">Borrow $5,000</button><button id="repay">Repay $5,000</button></div><p class="desc">Borrowing increases both cash and outstanding debt. Interest accrues each month and is paid to the regional lender. Unfunded public budgets reduce service capacity.</p>`+
 head('Treasury history')+chart('treasury');
}
function renderCitizens(){return head('Village families')+`<p class="desc">Select a household to inspect each resident's name, age, job, savings, food expenses, taxes and hardship.</p>`+
 G.households.filter(h=>h.people.length>0).map(h=>{let b=readBuild(h.home),people=h.people.map(id=>G.people[id]).filter(p=>p&&!p.deceased&&p.movedAway!==true),workers=people.filter(p=>(p.job>=0&&!p.commuteBlocked)||p.publicWork).length;return `<div class="entry" data-house="${h.id}"><strong>The ${esc(h.name)} household</strong><br><small>${people.length} people · ${workers} employed · Savings ${money(h.cash)} · Stress ${Math.round(h.stress)}/100 · Lot ${b?`${b.x},${b.y}`:'?'}</small></div>`}).join('');
}
function renderBusinesses(){let total=G.firms.filter(f=>!f.closed).length;
 return head('Private enterprises')+`<p class="desc">${total} businesses operate. Wages, input prices, permit fees, sales taxes, production and crime influence their balances. Tap one to inspect.</p>`+
 G.firms.map(f=>`<div class="entry" data-firm="${f.id}"><strong>${esc(f.name)}</strong> <span class="pill">${f.closed?'CLOSED':'OPEN'}</span><br><small>${esc(types[f.kind].n)} · ${f.workers.length}/${f.jobs} staff · ${money(f.cash)} cash · Last profit ${money(f.profit)}</small></div>`).join('');
}
function renderConstruction(){return head('Village planning and private development')+
 '<p class="desc">Choose a building type, then tap a clear roadside plot on the map. Road tiles can be extended over open land. Costs are paid from town funds and recorded as construction purchases. Private enterprises also require regional investment capital.</p>'+
 `<div class="btnrow"><button data-build="" class="${buildMode===''?'on':''}">Inspect</button>${Object.entries(buildCost).map(([key,cost])=>`<button data-build="${key}" class="${buildMode===key?'on':''}">${buildIcons[key]} ${esc(types[key]?types[key].n:'Road')} · ${money(cost)}</button>`).join('')}</div>`+
 head('Physical services')+line('Police stations',G.buildings.filter(b=>b.kind==='police').length)+line('Fire brigades',G.buildings.filter(b=>b.kind==='fire').length)+line('Houses',G.homes.length)+line('Developed lots',G.buildings.length);
}
function renderJournal(){const j=G.journal;
 return head('The policy journal')+`<p class="desc">Every change captures the village's state when enacted. The differences below compare the current village with that baseline. They may reflect other events, time and policy changes.</p>`+
 j.slice().reverse().map(p=>{
 const base=p.baseline||{};const diff=(key,suff='',sign=false)=>{let d=(key==='treasury'?G.treasury:G.stats[key])-(base[key]||0);return (d>=0?'+':'')+fmt(d)+suff};
 return `<div class="entry"><strong>Day ${p.day}: ${esc(p.name)}</strong><p class="desc">${esc(p.message||'')}</p><div class="compact">Since change: employment ${diff('employment',' pts')} · hardship ${diff('hardship',' pts')} · safety ${diff('safety',' pts')} · businesses ${diff('businesses')} · treasury ${diff('treasury')}</div></div>`}).join('');
}
function renderSettings(){return head('Local save and diagnostics')+
 line('App version',RELEASE.version+' · Android adaptation')+line('Engine','Hardware-accelerated WebView Canvas 2D')+line('Residents',G.people.length)+line('Active businesses',G.stats.businesses)+line('Rendered scenery','Retained offscreen map image')+line('Autosave schedule',gameOptions.autoSave+' seconds, pause and app exit')+
 '<p class="desc">This is an offline Android adaptation, not a port of the original Godot/C++ project. Save data resides locally in app storage.</p><div class="btnrow"><button id="saveNow">Save game</button><button id="restart" class="red">Start a new village</button></div>'+
 head('Model limitations')+'<p class="desc">This is an illustrative agent-based economy. Policy outcomes use explicit behavioural rules, not statistically estimated causal effects. A single simulated town cannot establish what real-world policy will do.</p>';
}
function renderInspect(){const b=selected&&readBuild(selected.id);if(!b)return '<p>No property selected.</p>';const loc=`Lot ${b.x}, ${b.y}`;
 let html=head(types[b.kind].n+' · '+loc)+`<div class="statgrid">${stat('Estimated property value',money(b.value))}${stat('Condition',fmt(b.condition)+'/100')}</div>`;
 if(b.kind==='home'){
   const h=G.households[b.hh];if(!h)return html;
   html+=head('The '+h.name+' household')+`<div class="statgrid">${stat('Liquid savings',money(h.cash),h.cash<150?'negative':'')}${stat('Stress',fmt(h.stress)+'/100',h.stress>60?'negative':'')}${stat('Food yesterday',money(h.food))}${stat('Income yesterday',money(h.income))}</div>`+
   line('Rent yesterday',money(h.rent))+line('Income taxes yesterday',money(h.incomeTax??h.tax))+line('Housing assistance yesterday',money(h.aid))+line('Lifetime theft losses',money(h.crimeLoss))+line('Perceived security',fmt(h.security)+'/100')+
   head('People living here')+h.people.map(id=>{const p=G.people[id];if(!p)return '';const f=G.firms[p.job];return `<div class="entry"><strong>${esc(p.name)}</strong><br><small>Age ${p.age} · ${f?esc(f.name):'Not employed'} · Health ${Math.round(p.health)}/100</small></div>`}).join('');
 }else if(b.firm>=0){const f=G.firms[b.firm];if(f){html+=head(f.name)+`<div class="statgrid">${stat('Enterprise cash',money(f.cash))}${stat('Workers',f.workers.length+'/'+f.jobs)}${stat('Revenue yesterday',money(f.revenue))}${stat('Net profit yesterday',money(f.profit),f.profit<0?'negative':'')}</div>`+
 line('Minimum payable wage',money(workerIncome(f))+'/day')+line('Cash stolen since opening',money(f.theft))+line('Business taxes yesterday',money(f.tax))+
 head('Warehouse')+Object.keys(goods).map(k=>line(k,fmt(f.stock[k]||0))).join('')+
 head('Employees')+f.workers.slice(0,20).map(id=>{const p=G.people[id];return p?`<div class="line"><span>${esc(p.name)}</span><span>${esc(G.households[p.hh]?.name||'')}</span></div>`:''}).join('');
 }}else html+='<p class="desc">Public facility. Its physical presence improves village services only when the municipality funds the corresponding budget.</p>';
 html+=`<p class="desc">Ownership and all financial amounts are modelled local accounts, not decorative scores.</p>`;return html;
}
let panelOpener=null;
function openPanel(tab,opener=null){panelOpener=opener||document.activeElement;active=tab;$('gameRoot').classList.add('drawer-open');$('panel').classList.add('show');$('panelBody').scrollTop=0;$('tabs').querySelectorAll('button').forEach(b=>b.classList.toggle('active',b.dataset.panel===tab));renderPanel(tab)}
function closePanel(){const previous=active;active='';$('gameRoot').classList.remove('drawer-open');$('panel').classList.remove('show');$('tabs').querySelectorAll('button').forEach(b=>b.classList.remove('active'));const returnTarget=panelOpener?.isConnected&&panelOpener!==document.body&&panelOpener.getClientRects().length?panelOpener:$('tabs').querySelector(`button[data-panel="${previous}"]`);if(returnTarget)returnTarget.focus();panelOpener=null}
function economySnapshot(){
 const demand=cityDemand(),activeFirms=G.firms.filter(f=>!f.closed),families=G.households.filter(h=>h.people.some(id=>G.people[id]&&!G.people[id].deceased&&!G.people[id].movedAway));
 const byType={},kindSections={farm:'Agriculture',fishery:'Agriculture',wharf:'Logistics',forestry:'Resource extraction',quarry:'Resource extraction',mill:'Manufacturing',sawmill:'Manufacturing',factory:'Manufacturing',bakery:'Food & retail',grocer:'Food & retail',tavern:'Food & retail',warehouse:'Logistics',contractor:'Construction',office:'Services',college:'Services'};
 for(const f of G.firms){const sector=kindSections[f.kind]||'Other services',entry=byType[sector]||(byType[sector]={sector,open:0,closed:0,workers:0,jobs:0,profit:0,sales:0,capital:0,atRisk:0});
  if(f.closed)entry.closed++;else {entry.open++;entry.workers+=f.workers.length;entry.jobs+=f.jobs;entry.profit+=f.profit||0;entry.sales+=f.revenue||0;entry.capital+=f.cash||0;if(f.profit<0&&f.cash<Math.max(2500,f.wage*f.jobs*12))entry.atRisk++;}
 }
 const values=families.map(h=>h.cash/Math.max(1,h.people.length)).sort((a,b)=>a-b),median=values.length?values[Math.floor(values.length/2)]:0;
 const banks=G.banks.filter(b=>!b.closed),deposits=banks.reduce((sum,b)=>sum+bankDeposits(b.id),0),reserves=banks.reduce((sum,b)=>sum+b.cash,0),loans=G.loans.filter(l=>l.status==='active').reduce((sum,l)=>sum+l.balance,0);
 const marketJobs=activeFirms.reduce((sum,f)=>sum+f.jobs,0),working=activeFirms.reduce((sum,f)=>sum+f.workers.length,0);
 const vacantHomes=G.homes.filter(id=>{const b=readBuild(id);return b&&(!G.households[b.hh]||!G.households[b.hh].people.some(pid=>G.people[pid]&&!G.people[pid].movedAway&&!G.people[pid].deceased))}).length;
 return {demand,sectors:Object.values(byType).filter(x=>x.open||x.closed).sort((a,b)=>b.workers-a.workers),families:families.length,median,open:activeFirms.length,closed:G.firms.length-activeFirms.length,atRisk:activeFirms.filter(f=>f.profit<0&&f.cash<Math.max(2500,f.wage*f.jobs*12)).length,banks:banks.length,deposits,reserves,loans,marketJobs,working,vacantHomes,projects:(G.projects||[]).length};
}
function marketSignal(){const m=economySnapshot(),s=G.stats;let title,description,kind;
 if((G.market?.foodDisconnected||0)>0){title='Groceries out of reach';description=fmt(G.market.foodDisconnected)+' residents lack an operating grocer on their road network. Restore access or develop a reachable shop.';kind='danger';}
 else if((G.market?.unmetFood||0)>G.stats.population*.08){title='Essential food is going unfilled';description='Inspect shop stock, retail staff, delivered prices and household purchasing power.';kind='danger';}
 else if(s.hardship>35){title='Households under pressure';description='High hardship threatens local demand. Consider relief, jobs and essential living costs.';kind='danger';}
 else if(s.employment<65){title='A weak labour market';description='Jobs are scarce. Check business cash flow and the cost of hiring.';kind='danger';}
 else if(m.demand.housingPressure>75){title='Housing market tightening';description='Land values and household crowding favour new homes, if zoning and finance allow.';kind='warn';}
 else if(m.atRisk>=3){title='Firms at risk';description=m.atRisk+' active businesses have losses and thin cash buffers.';kind='warn';}
 else if(G.serviceProvision&&((G.serviceProvision.health?.coverage??1)<.65||(G.serviceProvision.school?.coverage??1)<.60)){title='Care and learning need attention';description='Strong jobs alone do not purchase public services. Compare access, qualified staffing and operating funds in Services.';kind='warn';}
 else if(s.employment>85&&s.hardship<14){title='Strong work and household reserves';description='Employment is high and few households currently show low liquidity or severe stress. Continue monitoring access, services and public commitments.';kind='good';}
 else {title='The economy is adjusting';description='Follow private construction, credit, employment and household purchasing power.';kind='normal';}
 return {title,description,kind,m};
}
function renderEconomy(){let signal=marketSignal(),m=signal.m,d=m.demand,active=G.firms.filter(f=>!f.closed),jobs=active.reduce((s,f)=>s+f.jobs,0),filled=active.reduce((s,f)=>s+f.workers.length,0);
 const cell=(name,value,detail,cls='')=>`<div class="market-cell ${cls}"><small>${esc(name)}</small><strong>${esc(value)}</strong><span>${esc(detail)}</span></div>`;
 return `<div class="market-status ${signal.kind}"><small>LIVE BOROUGH ECONOMY</small><h3>${esc(signal.title)}</h3><p>${esc(signal.description)}</p></div>`+
 `<div class="market-cells">${cell('Employment',G.stats.employment+'%',G.stats.employed+' residents working')}${cell('Median savings',money(m.median),'per household member')}${cell('Housing pressure',d.housingPressure+'/100',m.vacantHomes+' vacant cottages')}${cell('Private work sites',String(m.projects),'projects underway')}${cell('Businesses',String(m.open),m.closed+' historical closures')}${cell('Banks & credit',String(m.banks),money(m.loans)+' loans outstanding')}</div>`+
 head('Where people earn their living')+`<p class="desc">Actual operating enterprises, employees, sales and daily operating profit. A negative profit reflects losses, not an abstract score.</p>`+
 `<table class="market-table"><thead><tr><th>Industry</th><th>Firms</th><th>Jobs</th><th>Daily profit</th></tr></thead><tbody>`+m.sectors.map(x=>`<tr><td>${esc(x.sector)}${x.atRisk?` <small class="risk-mark">${x.atRisk} at risk</small>`:''}</td><td>${x.open}</td><td>${x.workers}/${x.jobs}</td><td class="${x.profit<0?'negative':'positive'}">${money(x.profit)}</td></tr>`).join('')+'</tbody></table>'+
 head('Private investment, not player placement')+meter('Demand for homes',d.homeDemand,d.homeDemand>65?'#e6a37a':'#9dce9c')+meter('Demand for commerce',d.businessDemand,'#adc7a9')+strip('Job openings',d.jobVacancy)+strip('Residential capacity',d.homes+' housing units')+strip('Next private sites',m.projects+' projects in construction')+strip('Regional exports & investment',money(G.region))+
 head('Banks, loans and savings')+strip('Household and company deposits',money(m.deposits))+strip('Cash reserves at local banks',money(m.reserves))+strip('Loans still being repaid',money(m.loans))+strip('Banks in operation',m.banks)+
 head('What should the government do?')+`<div class="council-card"><p class="desc">You do not control private developers, firms or banks. Adjust a few policy rates, funding priorities or municipal borrowing and let the market respond. Watch outcomes over months and years, not just individual days.</p><div class="btnrow"><button id="marketPolicy">Review policy rates</button><button id="marketFamilies">Inspect households</button><button id="marketCompanies">Inspect firms</button></div></div>`+
 head('Employment history')+miniChart('employment')+head('Private enterprise count')+miniChart('businesses')+head('Households under pressure')+miniChart('hardship')+head('Recent economic developments')+headlineList(8);
}
const names={economy:'The Living Economy',banking:'Banks & Credit',overview:'Town Hall',agenda:'Council Agenda',community:'Civic Services',policies:'Economic Policy',treasury:'The Public Purse',citizens:'Our Residents',businesses:'Local Enterprise',construction:'Works & Planning',journal:'Public Record',settings:'Game Options',inspect:'Property Inspector',trip:'Journey Inspector'};
function renderPanel(tab){if(!G)return;const sc=$('panelBody');const y=sc.scrollTop;let contents='';
 try{contents=({overview:renderOverviewFull,economy:renderEconomy,agenda:renderAgenda,community:renderCommunityFull,policies:renderPoliciesFull,treasury:renderTreasuryFull,banking:financePanel,citizens:renderCitizensFull,businesses:renderBusinessesFull,construction:renderConstructionFull,journal:renderJournalFull,settings:renderSettingsFull,inspect:renderInspectFull,trip:renderTripInspector}[tab]||renderOverview)()}
 catch(e){contents='<div class="event">Panel error: '+esc(e.message)+'</div>';console.error(e)}
 $('panelTitle').textContent=names[tab]||'TownLedger';sc.innerHTML=contents;sc.scrollTop=y;
}
function journalPolicy(k,old,nv){const base={...G.stats,treasury:G.treasury};G.journal.push({day:G.day,name:defs.find(d=>d[0]===k)?.[1]||k,message:`Policy revised from ${fmt(old)} to ${fmt(nv)}.`,baseline:base});if(G.journal.length>100)G.journal.shift();story('Council revised '+(defs.find(d=>d[0]===k)?.[1]||k)+'.','neutral')}
$('tabs').addEventListener('click',e=>{const b=e.target.closest('button[data-panel]');if(!b)return;const p=b.dataset.panel;if(p===active)closePanel();else openPanel(p)});
$('panelClose').onclick=closePanel;$('topNotice').onclick=()=>openPanel('journal',$('topNotice'));$('liveEconomy').onclick=()=>openPanel('economy',$('liveEconomy'));
$('panelBody').addEventListener('input',e=>{if(e.target.id==='searchPeople'){citizenQuery=e.target.value;return;}const input=e.target.closest('[data-policy]');if(!input)return;let k=input.dataset.policy,value=+input.value;const d=defs.find(d=>d[0]===k);draftPolicy[k]=value;const el=$('show-'+k);if(el)el.textContent=d[5]==='$'?money(value):policyNumber(value)+d[5];const button=$('enactPolicy');if(button)button.disabled=false;const summ=$('draftSummary');if(summ)summ.textContent=Object.keys(draftPolicy).filter(k=>draftPolicy[k]!==G.policy[k]).map(k=>k==='imports'?'Regional inventory imports: '+(G.policy.imports?'OPEN':'RESTRICTED')+' → '+(draftPolicy.imports?'OPEN':'RESTRICTED'):defs.find(d=>d[0]===k)?.[1]+': '+policyNumber(G.policy[k])+' → '+policyNumber(draftPolicy[k])).join(' · ')});
$('panelBody').addEventListener('change',e=>{if(e.target.id==='searchPeople'){renderPanel('citizens');return;}const input=e.target.closest('[data-policy]');if(!input)return;draftPolicy[input.dataset.policy]=+input.value;const b=$('enactPolicy');if(b)b.disabled=false});
$('panelBody').addEventListener('click',e=>{const b=e.target.closest('button,[data-house],[data-firm],[data-inspect],[data-ambition]');if(!b)return;
 if(b.dataset.build!==undefined){flushRoadBatch();buildMode=b.dataset.build;if(overlay==='charter'){overlay='none';parcelFocus=null;}dirty=true;$('hint').textContent=buildMode?'TAP A CLEAR ROADSIDE PLOT · '+(buildMode==='road'?'DRAG TO PAINT ROADS':'DRAG TO PAN'):'DRAG TO PAN · TAP TO INSPECT';$('placementHint').style.display=buildMode?'block':'none';$('placementHint').textContent=buildMode?'PLACING '+(types[buildMode]?.n||'ROADS').toUpperCase()+' · COST '+money(buildCost[buildMode])+(['fishery','wharf'].includes(buildMode)?' · SHORE + ROAD'+(buildMode==='wharf'?' + RIVER OUTLET':''):''):'';closePanel();toast(buildMode?'Tap the map to build '+(types[buildMode]?.n||'road')+'.':'Inspection mode enabled');return}
 if(b.dataset.house!==undefined){const h=G.households[+b.dataset.house];if(h){const house=readBuild(h.home);if(!house){toast('This household no longer has an address in town.');return}selected={id:h.home};openPanel('inspect');const p=iso(house.x,house.y);cam.x=p[0];cam.y=p[1];dirty=true}return}
 if(b.dataset.firm!==undefined){const f=G.firms[+b.dataset.firm];if(f){const house=readBuild(f.building);if(!house){toast('This company no longer has premises in town.');return}selected={id:f.building};openPanel('inspect');const p=iso(house.x,house.y);cam.x=p[0];cam.y=p[1];dirty=true}return}
 if(b.dataset.inspect!==undefined){selected={id:+b.dataset.inspect};openPanel('inspect');const house=readBuild(selected.id);if(house){const p=iso(house.x,house.y);cam.x=p[0];cam.y=p[1];dirty=true}return}
 if(b.id==='enactPolicy'){enactPolicyPackage();return}
 if(b.id==='resetPolicy'){draftPolicy={};renderPanel('policies');return}
 if(b.dataset.cabinet){const packageRates={
 enterprise:{incomeTax:10,profitTax:7,permitFee:0,zoningRestriction:10,businessRegulation:20},
 housing:{zoningRestriction:0,propertyTax:1,transitBudget:90,permitFee:35},
 services:{incomeTax:19,profitTax:22,healthBudget:190,educationBudget:200,aidBudget:160,roadBudget:140},
 austerity:{incomeTax:14,profitTax:14,healthBudget:75,educationBudget:75,policeBudget:110,defenseBudget:80,aidBudget:55,roadBudget:80}
 };const rates=packageRates[b.dataset.cabinet];if(rates){for(const [k,v] of Object.entries(rates)){const d=defs.find(d=>d[0]===k);if(d)draftPolicy[k]=clamp(v,d[2],d[3]);}renderPanel('policies');toast('Policy proposal drafted. Review and enact it to apply.');}return}
 if(b.id==='marketPolicy'){openPanel('policies');return}
 if(b.id==='marketFamilies'){openPanel('citizens');return}
 if(b.id==='marketCompanies'){openPanel('businesses');return}
 if(b.id==='jumpAgenda'){openPanel('agenda');return}
 if(b.id==='jumpJournal'){openPanel('journal');return}
 if(b.id==='closeInspect'){closePanel();return}
 if(b.id==='convene'){if(G.day-G.lastEventDay>=12){offerCouncilEvent(true)}return}
 if(b.dataset.inbox!==undefined){reviewCouncilInbox(+b.dataset.inbox);return}
 if(b.dataset.ambition){G.ambition=b.dataset.ambition;updateHeader();renderPanel('agenda');save();return}
 if(b.dataset.filterPeople){filterPeople=b.dataset.filterPeople;renderPanel('citizens');return}
 if(b.dataset.filterFirms){filterFirms=b.dataset.filterFirms;renderPanel('businesses');return}
 if(b.dataset.buildCategory){constructionCategory=b.dataset.buildCategory;renderPanel('construction');return}
 if(b.id==='focusBad'){const poor=G.households.filter(h=>h.people.length>0&&readBuild(h.home)).sort((a,b)=>a.cash/Math.max(1,a.people.length)-b.cash/Math.max(1,b.people.length))[0];if(poor&&readBuild(poor.home)){selected={id:poor.home};openPanel('inspect')}return}
 if(b.id==='saveNow'){const epoch=saveEpoch,label=b.textContent;b.disabled=true;b.textContent='SAVING…';b.setAttribute('aria-busy','true');save().then(ok=>{if(b.isConnected){b.disabled=false;b.textContent=label;b.removeAttribute('aria-busy')}if(epoch===saveEpoch)toast(ok?'Village saved on this device.':'Saving failed; export a backup before leaving.')})}
 if(b.id==='restart'){showCustomEvent('TOWN ARCHIVE','Found another town?','Starting a new village will overwrite your most recent local autosave. Export a backup before proceeding.',[
  {title:'Keep the present village',desc:'Return to your existing town.',apply:()=>{}},
  {title:'Start a fresh village',desc:'Discard the current local save and return to the founding menu.',apply:()=>{start(true);closePanel();toast('A new village has been founded.')}}
 ]);return}
 if(b.id==='backupSave'){exportSave();return}
 if(b.id==='importSave'){importSave();return}
 if(b.dataset.servicePolicy){openPanel('policies');const input=$('panelBody').querySelector('[data-policy="'+(b.dataset.servicePolicy==='health'?'healthBudget':'educationBudget')+'"]');if(input){input.closest('details').open=true;input.scrollIntoView({block:'center'});input.focus();}return}
 if(b.dataset.serviceAccess){overlay=b.dataset.serviceAccess==='health'?'healthAccess':'schoolAccess';closePanel();dirty=true;toast('Service access: green available · gold partial · copper unserved. Road distance and shared facility places determine reach.');return}
 if(b.dataset.openPanel){openPanel(b.dataset.openPanel);return}
 if(b.id==='tutorial'){openTutorialDialog(b);return}
 if(b.id==='toggleDevelopment'){G.autoBuild=!G.autoBuild;save();renderPanel(active);toast(G.autoBuild?'Private investment resumed.':'New private construction paused.');return;}
 if(b.id==='overlayMetro'){overlay=overlay==='metro'?'none':'metro';dirty=true;renderPanel(active);return;}
 if(b.id==='overlayR'){overlay=overlay==='roads'?'none':'roads';dirty=true;renderPanel(active);return}
 if(b.id==='overlayC'){overlay=overlay==='crime'?'none':'crime';dirty=true;renderPanel(active);return}
 if(b.id==='overlayH'){overlay=overlay==='hardship'?'none':'hardship';dirty=true;renderPanel(active);return}
 if(b.id==='overlayB'){overlay=overlay==='business'?'none':'business';dirty=true;renderPanel(active);return}
 if(b.id==='tradeToggle'){draftPolicy.imports=!(draftPolicy.imports??G.policy.imports);renderPanel('policies');return}
 if(b.id==='soundToggle'){soundEnabled=!soundEnabled;try{localStorage.setItem('townledger-audio',soundEnabled?'on':'off')}catch(e){};refreshAmbience();renderPanel('settings');return}
 if(b.id==='borrow'){let limit=Math.max(25000,G.stats.population*350);if(G.debt+5000>limit||G.region<5000){toast('Regional lender declined: the credit limit or available funds have been reached.');return;}G.debt+=5000;G.treasury+=5000;G.region-=5000;story('Council borrowed $5,000 from the regional lender.');recompute();updateHeader();save();renderPanel(active)}
 if(b.id==='repay'){let v=Math.min(5000,G.debt,G.treasury);G.debt-=v;G.treasury-=v;G.region+=v;recompute();updateHeader();save();renderPanel(active)}
});
$('zoomIn').onclick=()=>{cam.zoom=clamp(cam.zoom*1.22,.025,1.7);dirty=true};$('zoomOut').onclick=()=>{cam.zoom=clamp(cam.zoom/1.22,.025,1.7);dirty=true};$('center').onclick=()=>{if(overlay==='charter'){overlay='none';parcelFocus=null;}centerTownCamera();};$('overlayToggle').onclick=()=>{overlay=overlay==='none'?'roads':overlay==='roads'?'metro':overlay==='metro'?'hardship':overlay==='hardship'?'crime':overlay==='crime'?'business':'none';dirty=true;toast('Map overlay: '+overlay)};
 $('pause').onclick=()=>{paused=!paused;fit();updateHeader();if(paused){draw();save()}};const SPEED_PRESETS=[1,2,4,8,16,32,64];
 $('speed').onclick=()=>{const index=SPEED_PRESETS.indexOf(speed);speed=SPEED_PRESETS[(index+1)%SPEED_PRESETS.length];acc=0;sampleDays=0;sampleSeconds=0;G.speed=speed;fit();updateHeader()};
 $('speedRange').addEventListener('input',e=>{speed=SPEED_PRESETS[+e.target.value]||1;acc=0;sampleDays=0;sampleSeconds=0;if(G)G.speed=speed;fit();updateHeader();});
$('speedRange').addEventListener('change',()=>{if(G)save();});
function start(newVillage){if(newVillage){seed(Number($('townSeed')?.value)||42)}else if(!load())seed();centerTownCamera();invalidateRoads();buildMode='';selected=null;overlay='none';paused=false;speed=SPEED_PRESETS.includes(G.speed)?G.speed:1;acc=0;fit();$('welcome').style.display='none';dirty=true;staticDirty=true;updateHeader();openPanel('overview');}
$('newTown').onclick=()=>{start(true);refreshAmbience()};$('continue').onclick=()=>{start(false);refreshAmbience()};
try{if(localStorage.getItem('townledger-v6')||localStorage.getItem('townledger-v6-backup')||localStorage.getItem('townledger-village-founder-3')||localStorage.getItem('townledger-village-civic-2'))$('continue').style.display='block'}catch(e){}
window.addEventListener('resize',fit);fit();
let last=performance.now(),acc=0,lastMapDraw=0,lastHeader=0,lastPanel=0,lastAutosave=performance.now(),speedSample=0,sampleDays=0,sampleSeconds=0;
function frame(now){
 const raw=Math.max(0,(now-last)/1000);last=now;
 if(G&&!paused&&!hostSuspended&&!pendingEvent&&!document.hidden){
  // Admit requested wall time, then do a bounded amount of real simulation work.
  // A bounded queue avoids a multi-minute catchup after an interrupted phone frame.
  const dt=Math.min(raw,.25);acc=Math.min(acc+dt*speed,1.65*8);
  const budget=speed>=16?10:6,end=performance.now()+budget;let completed=0;
  while(acc>=1.65&&(!completed||performance.now()<end)&&!pendingEvent){const t=performance.now();tick();perfStats.ticks.push(performance.now()-t);if(perfStats.ticks.length>180)perfStats.ticks.shift();acc-=1.65;completed++;}
  perfStats.days+=completed;perfStats.elapsed+=dt;perfStats.backlog=acc/1.65;
  sampleDays+=completed;sampleSeconds+=raw;
  if(sampleSeconds>=1){perfStats.effective=sampleDays*1.65/sampleSeconds;sampleDays=0;sampleSeconds=0;}
  if(!gameOptions.reducedMotion){frameClock+=dt;if(gameOptions.traffic)trafficUpdate(dt);}dirty=true;
 }else{sampleDays=0;sampleSeconds=0;if(document.hidden)acc=0;}
 if(G&&!document.hidden){
  if(now-lastHeader>=250){updateHeader();lastHeader=now;}
  if(active&&!paused&&now-lastPanel>=1500&&!['policies','citizens','settings','construction'].includes(active)&&!$('panelBody').contains(document.activeElement)){renderPanel(active);lastPanel=now;}
  if(!paused&&now-lastAutosave>=gameOptions.autoSave*1000){save();lastAutosave=now;}
  const fps=speed>=32?Math.min(20,gameOptions.fps):gameOptions.fps;
  if(dirty&&now-lastMapDraw>=1000/fps){const t=performance.now();draw();perfStats.frames.push(performance.now()-t);if(perfStats.frames.length>600)perfStats.frames.shift();lastMapDraw=now;}
 }
 requestAnimationFrame(frame);
}requestAnimationFrame(frame);
window.addEventListener('beforeunload',()=>save());document.addEventListener('visibilitychange',()=>{last=performance.now();acc=0;if(document.hidden){save();stopGameAudio()}else refreshAmbience()});
window.addEventListener('error',e=>{console.error(e.error||e.message);toast('Runtime issue: '+(e.message||'Unknown'))});
