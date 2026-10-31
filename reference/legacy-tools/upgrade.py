from pathlib import Path
root=Path(__file__).resolve().parent.parent
js=root/'assets/game.js'
s=js.read_text()
# 16 authored cottages plus varied commercial frontage; old data URIs retained for all non-redrawn types.
s=s.replace("`tree-${season}-${item.id%8}`:","`tree-${season}-${item.id%8}`:")
# Sprite drawing now uses all variants but preserves the original fallback.
s=s.replace("let lo=0,hi=displayItems.length;", "let lo=0,hi=displayItems.length;")
s=s.replace("const mixed=decor.concat(moving).sort((a,b)=>a.y-b.y);", "const mixed=decor.concat(moving,streetLife(sx,sy,ww,hh)).sort((a,b)=>a.y-b.y);")
s=s.replace("if(item.kind==='vehicle'){vehiclePaint(ctx,item.v,item,frameClock);continue}","if(item.kind==='vehicle'){vehiclePaint(ctx,item.v,item,frameClock);continue}if(item.kind==='pedestrian'){paintPedestrian(ctx,item);continue}")
s=s.replace("diamond(bg,x,y,base,t===1?'#8c8a75':'#294b361b');", "diamond(bg,x,y,base,t===1?'#8c8a75':null);")
s=s.replace("if(t===0&&G.landUse?.[id]!==1&&!site){", "if(t===0&&G.landUse?.[id]!==1&&!site){")
s=s.replace("function draw(){if(!G||!dirty)return;", """
// Ambient residents walk along the ACTUAL connected road network. Purely visual:
// no fake commuters enter the economic accounts. Deterministic and capped.
let streetLifeVersion=-1,streetSegments=[];
function streetLife(sx,sy,ww,hh){
 if(cam.zoom<.50||!G||paused)return [];
 const net=graph();
 if(streetLifeVersion!==roadsVersion){
  streetLifeVersion=roadsVersion;streetSegments=[];
  for(const [id,links] of net.neighbors){if(net.parts[id]!==net.mainPart)continue;
   for(const n of links){if(id>=n)continue;const a=roadCenter(id),b=roadCenter(n);
    streetSegments.push([a,b,id,n]);}
  }
 }
 if(!streetSegments.length)return [];
 const n=Math.min(24,Math.max(4,Math.floor((G.stats?.population||0)/11)));
 const out=[],clock=frameClock*.11;
 for(let k=0;k<n;k++){
  const index=((k*7919+Math.floor(clock*.07)*31)>>>0)%streetSegments.length;
  const [a,b,id]=streetSegments[index],phase=(clock*(.55+k%3*.14)+k*.241)%1;
  const x=a[0]+(b[0]-a[0])*phase,y=a[1]+(b[1]-a[1])*phase;
  if(x<sx-10||x>sx+ww+10||y<sy-10||y>sy+hh+10)continue;
  out.push({kind:'pedestrian',x:x-4,y:y-2,id:k,phase});
 }
 return out;
}
function paintPedestrian(g,item){
 const x=Math.round(item.x),y=Math.round(item.y),step=(Math.floor(frameClock*5+item.id)%2),coat=['#946444','#c9a47c','#537d70','#657db0','#b85d64','#6d586a'][item.id%6];
 g.fillStyle='#162e2c88';g.fillRect(x-2,y+3,7,2);
 g.fillStyle=item.id%4===0?'#4d3c33':'#e4bb96';g.fillRect(x,y-7,3,4);
 g.fillStyle=coat;g.fillRect(x-1,y-3,5,5);
 g.fillStyle='#334a4b';g.fillRect(x+(step?2:-1),y+2,2,3);g.fillRect(x+(step?-1:2),y+2,2,3);
 if(item.id%5===0){g.fillStyle='#685b4a';g.fillRect(x-2,y-8,7,2);}
}
function draw(){if(!G||!dirty)return;""")
# New economy and macro dashboard; all numbers refer to real saved economic state.
needle='const names={banking:'
assert needle in s
s=s.replace(needle,'''function economySnapshot(){
 const demand=cityDemand(),activeFirms=G.firms.filter(f=>!f.closed),families=G.households.filter(h=>h.people.some(id=>G.people[id]&&!G.people[id].deceased&&!G.people[id].movedAway));
 const byType={},kindSections={farm:'Agriculture',fishery:'Agriculture',forestry:'Resource extraction',quarry:'Resource extraction',mill:'Manufacturing',sawmill:'Manufacturing',factory:'Manufacturing',bakery:'Food & retail',grocer:'Food & retail',tavern:'Food & retail',warehouse:'Logistics',contractor:'Construction',office:'Services',college:'Services'};
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
 if(s.hardship>35){title='Households under pressure';description='High hardship threatens local demand. Consider relief, jobs and essential living costs.';kind='danger';}
 else if(s.employment<65){title='A weak labour market';description='Jobs are scarce. Check business cash flow and the cost of hiring.';kind='danger';}
 else if(m.demand.housingPressure>75){title='Housing market tightening';description='Land values and household crowding favour new homes, if zoning and finance allow.';kind='warn';}
 else if(m.atRisk>=3){title='Firms at risk';description=m.atRisk+' active businesses have losses and thin cash buffers.';kind='warn';}
 else if(s.employment>85&&s.hardship<14){title='Broad-based prosperity';description='Employment is high and most households are meeting their expenses.';kind='good';}
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
const names={economy:'The Living Economy',banking:''')
s=s.replace('overview:renderOverviewFull,agenda:renderAgenda','overview:renderOverviewFull,economy:renderEconomy,agenda:renderAgenda')
# Display one-line indicators below map ticker.
s=s.replace('function updateHeader(){if(!G)return;', 'function updateHeader(){if(!G)return;')
s=s.replace("$('pause').textContent=paused?'▶':'Ⅱ';", "$('pause').textContent=paused?'▶':'Ⅱ';if($('liveEconomy')&&(G.day%5===1||G.day<5)){const m=marketSignal();$('liveEconomy').innerHTML=`<b>${esc(m.title)}</b><span>${G.stats.employment}% employed · ${m.m.open} firms · ${m.m.projects} building · ${G.stats.hardship}% hardship</span>`;}")
s=s.replace(" if(b.id==='jumpAgenda'){", " if(b.id==='marketPolicy'){openPanel('policies');return}\n if(b.id==='marketFamilies'){openPanel('citizens');return}\n if(b.id==='marketCompanies'){openPanel('businesses');return}\n if(b.id==='jumpAgenda'){")
# 30-day economic pulse changes, not arbitrary random popups.
s=s.replace("if(G.day%30===0)monthlyReview();", "if(G.day%60===0){let before=G.lastEconomicSignal||'',now=marketSignal();if(now.kind!=='normal'&&now.title!==before){story(now.title+'. '+now.description,now.kind==='good'?'good':'bad');G.lastEconomicSignal=now.title;}}if(G.day%30===0)monthlyReview();")
# Fix version display.
s=s.replace("line('App version','0.2.0 · Android adaptation')", "line('App version','5.6.0 · Android adaptation')")
js.write_text(s)
# HTML tweaks keep compatibility with prior button ids.
html=root/'assets'/'index.html';s=html.read_text()
s=s.replace('TOWNLEDGER — HARVEST & HEARTH','TOWNLEDGER — THE LIVING BOROUGH').replace('Harvest & Hearth','The Living Borough').replace('HARVEST & HEARTH','THE LIVING BOROUGH')
s=s.replace('Every family has a future. Every decision has a cost.','A living economy. Your decisions ripple through it.')
s=s.replace('<div class="mapbuttons">', '<div id="liveEconomy" class="live-economy" aria-live="off"><b>A growing town</b><span>The market moves on its own.</span></div><div class="mapbuttons">')
s=s.replace('<button data-panel="agenda"><span class="tabico">▣</span><span>Agenda</span></button>', '<button data-panel="economy"><span class="tabico">◫</span><span>Economy</span></button><button data-panel="agenda"><span class="tabico">▣</span><span>Agenda</span></button>')
s=s.replace('<span>Build</span>', '<span>Public Works</span>')
html.write_text(s)
