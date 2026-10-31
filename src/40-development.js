function cityDemand(){
 const residents=G.people.reduce((n,p)=>n+Number(!p.deceased&&p.movedAway!==true),0);
 const open=G.firms.filter(f=>!f.closed);
 const jobs=open.reduce((n,f)=>n+f.jobs,0);
 const employed=G.people.reduce((n,p)=>n+Number(!p.deceased&&p.movedAway!==true&&p.job>=0),0);
 const jobVacancy=Math.max(0,jobs-employed);
 const homes=G.buildings.reduce((n,b)=>n+(b.kind==='home'?1:b.kind==='apartment'?4:b.kind==='tower'?9:0),0)+(G.projects||[]).filter(p=>p.kind==='home').length;
 const residentHouseholds=G.households.filter(h=>h.people.length>0);
 const viable=residentHouseholds.filter(h=>householdLiquidity(h)>Math.max(180,h.people.length*125)).length;
 const incomes=residentHouseholds.length?viable/residentHouseholds.length:0;
 const hardship=G.stats.hardship||0;
 const demandJobs=clamp(jobVacancy/Math.max(1,jobs),0,1);
 const regulation=G.policy.zoningRestriction/100;
 const confidence=G.stats.marketConfidence||50;
 const targetPop=residents+clamp(jobVacancy*.42,0,45)+Math.max(0,residents*.018);
 const targetHomes=Math.ceil(targetPop/2.2);
 const housingPressure=clamp((targetHomes-homes)/Math.max(1,homes)*100+50+(incomes-.7)*15,0,100);
 const housingDemand=clamp((targetHomes-homes)*6+jobVacancy*.7+(confidence-50)*.32-hardship*.45-regulation*16,0,100);
 const kinds={};
 for(const f of open)kinds[f.kind]=(kinds[f.kind]||0)+1;
 const ratio=(kind,ideal)=>Math.max(0,Math.min(100,(residents/ideal/(kinds[kind]||.55)-1)*75));
 let applicants={
  grocer:ratio('grocer',45),bakery:ratio('bakery',76),farm:ratio('farm',90),
  mill:ratio('mill',130),forestry:ratio('forestry',170),sawmill:ratio('sawmill',190),
  contractor:ratio('contractor',105),quarry:ratio('quarry',135),tavern:ratio('tavern',145),
  fishery:ratio('fishery',245),wharf:waterfrontDemand(),factory:residents>=190?ratio('factory',280):0,warehouse:residents>=220?ratio('warehouse',290):0,office:residents>=240?ratio('office',310):0,college:residents>=320?ratio('college',600):0
 };
 const foodShort=G.firms.filter(f=>!f.closed&&f.kind==='grocer').some(f=>(f.stock.food||0)<35);
 if(foodShort){applicants.farm+=12;applicants.bakery+=10;applicants.grocer+=5}
 const businessDemand=Math.round(clamp(Math.max(...Object.values(applicants))*.75+(confidence-50)*.25-hardship*.17-G.policy.permitFee*.007-G.policy.businessRegulation*.11,0,100));
 const freeLots=G.buildings.length<T*T?countBuildableLots(15):0;
 return {residents,homes,jobs,jobVacancy,homeDemand:Math.round(housingDemand),housingPressure:Math.round(housingPressure),businessDemand,applicants,freeLots,confidence,hardship,auto:G.autoBuild!==false};
}
function countBuildableLots(radius){
 let n=0;for(let y=5;y<T-5;y++)for(let x=5;x<T-5;x++)if(Math.abs(x-27)+Math.abs(y-27)<radius&&canPlace(x,y))n++;
 return n;
}
function buildableCandidates(focus='housing',projection=null){
 // A proposal can share geometry within its synchronous review, but every scan
 // must retain the original random draws and fresh ranking (including ties).
 if(projection?.sites)return projection.sites.map(p=>({x:p.x,y:p.y,score:p.baseScore+random()*1.7})).sort((a,b)=>b.score-a.score);
 if(projection)projection.sites=[];
 const net=graph(),places=[];
 for(let y=3;y<T-3;y++)for(let x=3;x<T-3;x++){
  if(!canPlace(x,y,true,focus==='business'?'plot':'home'))continue;
  const adjacent=roadOffsets.map(([dx,dy])=>roadId(x+dx,y+dy)).filter(id=>net.parts[id]===net.mainPart);
  if(!adjacent.length)continue;
  let houses=0,work=0,competition=0;
  for(const b of G.buildings){const d=Math.abs(b.x-x)+Math.abs(b.y-y);
   if(d>10)continue;
   if(b.kind==='home')houses+=1/(1+d*.3);
   if(b.firm>=0&&!G.firms[b.firm]?.closed)work+=1/(1+d*.3);
   if(focus==='business'&&b.kind==='grocer')competition+=1/(1+d*.35);
  }
  const edge=Math.abs(x-27)+Math.abs(y-27);
  const baseScore=(focus==='housing'?work*2.2+houses*.65:houses*2.4+work*.75-competition*.15)-edge*.05;
  if(projection)projection.sites.push({x,y,baseScore});
  const score=baseScore+random()*1.7;
  places.push({x,y,score});
 }
 places.sort((a,b)=>b.score-a.score);
 return places;
}
function privateContract(cost){return financeConstruction(cost);}
function privatelyBuiltRoads(demand){
 if(G.region<40000||G.policy.zoningRestriction>=90||demand.residents<145||demand.freeLots>75||(demand.homeDemand<20&&demand.businessDemand<25))return false;
 const net=graph(),plans=[];
 for(const [id,links] of net.neighbors){if(net.parts[id]!==net.mainPart)continue;const x=id%T,y=id/T|0;
  for(const [dx,dy] of roadOffsets){if(links.includes(roadId(x+dx,y+dy)))continue;
   const cells=[];let connects=false,valid=true;
   for(let k=1;k<=8;k++){const xx=x+dx*k,yy=y+dy*k,n=roadId(xx,yy);
    if(xx<5||xx>T-6||yy<5||yy>T-6){valid=false;break;}
    if(G.tiles[n]===1){connects=k>=5;break;}
    if(!charterOwns(xx,yy)||![0,3].includes(G.tiles[n])||G.landUse?.[n]||buildingAt(xx,yy)){valid=false;break;}
    // No one-lot parallel strips; leave space for real blocks and legal plots.
    if(k>2&&roadOffsets.some(([ax,ay])=>(ax*dx+ay*dy===0)&&cityCell(xx+ax,yy+ay)===1)){valid=false;break;}
    cells.push(n);
   }
   if(!valid||cells.length<5)continue;
   const end=fromEnd(cells),score=(connects?10:0)+cells.length+Math.min(8,Math.abs(end%T-27)+Math.abs((end/T|0)-27))*.12;
   plans.push({cells,score});
  }
 }
 plans.sort((a,b)=>b.score-a.score);const plan=plans[0];if(!plan)return false;
 const cost=plan.cells.length*buildCost.road;if(!privateContract(cost))return false;
 G.roadClasses=G.roadClasses||{};G.streetNames=G.streetNames||{};const name=['Elm','Westgate','Cedar','Victoria','Meadow','Foundry'][(G.development.roads||0)%6]+' Street';
 for(const id of plan.cells){G.tiles[id]=1;G.privateRoads.push(id);G.roadClasses[id]='local';G.streetNames[id]=name;ensureRoadWear();G.roadWear[id]=100;}
 G.development.roads+=plan.cells.length;G.development.privateSpend=(G.development.privateSpend||0)+cost;G.construction+=plan.cells.length;invalidateRoads(false);staticDirty=true;dirty=true;
 story('A funded '+name+' extension opened a connected block for development.','good');return true;
}
function startDevelopmentProject(kind,place,value,days,extra={}){
 const target=kind==='firm'?extra.firmKind:kind;
 if(!canPlace(place.x,place.y,true,target))return null;
 const b={id:G.nextId++,kind:'worksite',x:place.x,y:place.y,value,condition:100,owner:-1,firm:-1,hh:-1,developer:true,footprint:footprintFor(place.x,place.y,target)};
 for(const id of b.footprint)if(G.tiles[id]===3)G.tiles[id]=0;
 G.buildings.push(b);
 G.projects.push({id:b.id,kind,remaining:days,duration:days,start:G.day,...extra});
 staticDirty=true;dirty=true;
 G.development.started=(G.development.started||0)+1;
 return b;
}
function completeDevelopmentProjects(){
 if(!G.projects?.length)return;
 let changed=false;
 for(let i=G.projects.length-1;i>=0;i--){
  const p=G.projects[i];if(!constructionWork(p))continue;p.remaining--;
  if(p.remaining>0)continue;
  if(p.kind==='fields'){G.projects.splice(i,1);completeFarmFields(p);changed=true;continue;}
  const b=readBuild(p.id);
  G.projects.splice(i,1);
  if(!b)continue;
  if(p.kind==='public'){b.kind=p.publicKind;b.title={kind:'municipal',id:0};b.owner=-1;story(types[b.kind].n+' opened after publicly financed construction.','good',b.id);
  }else if(p.kind==='home'){
   b.kind='home';b.value=p.value;b.baseValue=p.value;b.developer=true;b.owner=-2;b.title={kind:'investor',id:0};
   if(p.municipalRehousing){b.owner=-1;b.title={kind:'municipal',id:0};b.developer=false;b.municipalRehousing=true;b.relocationReserve=true;}
   b.hh=-1;if(!G.homes.includes(b.id))G.homes.push(b.id);G.development.homes++;
   story(p.municipalRehousing?'Municipal replacement housing finished. The vacant home remains reserved for existing tenants displaced by approved land assembly.':'Cottage construction finished. The home is available to local households and workers with job prospects.','good',b.id);
  }else if(p.kind==='redevelop'){
   completeRedevelopment(b,p);
  }else if(p.kind==='airport'){
   completeAirfield(b,p);
  }else if(p.kind==='firm'){
   b.kind=p.firmKind;b.value=types[b.kind].cost*10;
   const escrowed=p.privateService||p.retailCentre;
   const capital=p.privateService?Math.max(0,p.serviceEscrow||0):p.retailCentre?Math.max(0,p.urbanEscrow||0):Math.min(p.capital,Math.max(0,G.region-1000));
   const fee=Math.min(G.policy.permitFee,Math.max(0,G.region-(escrowed?0:capital)));
   G.region-=(escrowed?0:capital)+fee;
   const f=createFirm(b.kind,b.x,b.y,true,()=>b);
   f.cash=capital;if(p.privateService){f.privateService=p.privateService;f.owner=-1;f.serviceFee=p.serviceFee;f.jobs=p.serviceStaff||(p.privateService==='school'?1:2);f.wage=p.serviceWage??Math.max(G.policy.minWage,36);f.name=p.privateService==='school'?'Independent Learning House '+f.id:'Mutual Fire Brigade '+f.id;b.title={kind:'firm',id:f.id};b.owner=f.owner;}transferTreasury(fee,'permits');
   if(G.policy.lendingRules<70&&(G.stats.marketConfidence||50)>48&&G.day%3===0){const loan=bankLoan('firm',f.id,Math.round(Math.min(2400,capital*.17)),480);if(loan)f.jobs=Math.min(18,f.jobs+1)}
   if(p.retailCentre){b.retailCentre=true;b.owner=-1;b.title={kind:'firm',id:f.id};f.owner=-1;f.retailCentre=true;f.openedDay=G.day;f.name='Vale Shopping Centre '+f.id;f.jobs=p.retailStaff||8;f.wage=p.retailWage||f.wage;f.scale=2;f.retailCatchment=p.retailCatchment;f.retailExpectedNet=p.retailExpectedNet;recruitUrbanRetailStaff(f);b.value=220000;}
   G.development.firms++;
   story('New private enterprise completed: '+f.name+' opened its doors.','good',b.id);
  }
  G.construction++;changed=true;
 }
 if(changed){invalidateRoads(false);recompute();assignJobs();staticDirty=true;dirty=true}
}
function privatelyBuiltHome(demand){
 if(demand.homeDemand<9||demand.hardship>57||demand.confidence<22||G.region<35000||demand.residents>=2000||G.policy.zoningRestriction>=94)return false;
 const approval=clamp(1-G.policy.zoningRestriction/125-G.policy.propertyTax/18,0,1);
 if(random()>approval)return false;
 const lots=buildableCandidates('housing');if(!lots.length)return false;
 const place=lots[0],quote=developmentQuote(place,'home',demand),cost=quote.cost;
 if(quote.expected<=0){G.development.lastRejected={day:G.day,reason:'Expected housing yield below funding hurdle',...quote};return false;}
 const savings=clamp(Math.round(rn(1250,3900)),500,4500);
 if(G.region<cost+savings+10000)return false;
 const value=Math.round(38000+demand.housingPressure*240);
 const site=startDevelopmentProject('home',place,value,18+Math.round(rn(0,14)),{value,savings});
 if(!site)return false;privateContract(cost);explainDevelopment(site,quote,'housing');
 G.development.privateSpend=(G.development.privateSpend||0)+cost;
 story('A housing developer broke ground for a privately financed cottage.','good',site.id);
 return true;
}
function privatelyBuiltFirm(demand){
 if(demand.businessDemand<17||demand.hardship>70||G.region<120000||G.policy.permitFee>2800||G.policy.zoningRestriction>=90)return false;
 const capacity=G.people.filter(p=>!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=70&&p.job<0).length;
 if(capacity<3&&!(demand.confidence>48&&demand.homeDemand>15&&G.region>250000))return false;
 const ranked=Object.entries(demand.applicants).sort((a,b)=>b[1]-a[1]);
 const approval=clamp(.65+(demand.confidence-50)/160-G.policy.businessRegulation/180-G.policy.profitTax/130,0.07,.95);
 if(random()>approval)return false;
 const candidates=buildableCandidates('business');
 let kind=null,place=null;
 for(const [choice,score] of ranked){
  if(score<13)break;
  const competitors=G.firms.filter(f=>f.kind===choice&&!f.closed&&f.age>45);
  if(competitors.length>=2&&competitors.filter(f=>f.netProfit< -75).length>competitors.length*.55)continue;
  const spot=candidates.slice().sort((a,b)=>(b.score+urbanSiteSuitability(b.x,b.y,choice))-(a.score+urbanSiteSuitability(a.x,a.y,choice))).find(v=>canPlace(v.x,v.y,true,choice));
  if(spot){kind=choice;place=spot;break}
 }
 if(!kind||!place)return false;
 const quote=developmentQuote(place,kind,demand);if(quote.expected<=0){G.development.lastRejected={day:G.day,reason:'Expected enterprise yield below funding hurdle',...quote};return false;}
 const capital=11500+Math.round(rn(0,7000));
 const fee=G.policy.permitFee,buildingCost=types[kind].cost;
 if(G.region<capital+fee+buildingCost+25000)return false;
 const site=startDevelopmentProject('firm',place,types[kind].cost*10,24+Math.round(rn(0,20)),{firmKind:kind,capital});
 if(!site)return false;privateContract(buildingCost);explainDevelopment(site,quote,kind);
 G.development.privateSpend=(G.development.privateSpend||0)+buildingCost+capital;
 story('Private investors started building a '+types[kind].n.toLowerCase()+' after evaluating market demand.','good',site.id);
 return true;
}
function stationHubs(){
 const candidates=buildableCandidates('business').filter(c=>canPlace(c.x,c.y,true,'metro_station'));
 return candidates.map(c=>{let residents=0,workplaces=0;
  for(const b of G.buildings){const d=Math.abs(b.x-c.x)+Math.abs(b.y-c.y);if(d<=7){if(b.kind==='home')residents+=8-d;if(b.firm>=0&&!G.firms[b.firm]?.closed)workplaces+=10-d;}}
  return {...c,demand:residents+workplaces*1.35};
 }).sort((a,b)=>b.demand-a.demand);
}
function stationBuilding(place){
 if(!canPlace(place.x,place.y,true,'metro_station'))return null;
 const b={id:G.nextId++,kind:'metro_station',x:place.x,y:place.y,value:180000,condition:100,owner:-1,firm:-1,hh:-1,private:true,footprint:footprintFor(place.x,place.y,'metro_station')};
 G.buildings.push(b);G.metro.stations.push(b.id);G.development.stations++;return b;
}
function connectMetro(a,b,newStations=0){
 const len=Math.abs(a.x-b.x)+Math.abs(a.y-b.y);
 const price=buildCost.metro_station*newStations+len*1100;
 // The two station buildings have already been created before this function is called.
 if(G.metro.cash<price)return false;
 G.metro.cash-=price;
 const share=price*.24;
 const constructors=G.firms.filter(f=>f.kind==='contractor'&&!f.closed);
 if(constructors.length){const c=constructors[G.day%constructors.length];c.cash+=share;c.revenue+=share;G.region+=price-share;}
 else G.region+=price;
 G.metro.lines.push({from:a.id,to:b.id,length:len,built:G.day,readyDay:G.day+85,color:['#e4ba67','#7cb5ba','#b78cb9','#cf887d'][G.metro.lines.length%4]});
 G.metro.invested+=price;G.development.privateSpend=(G.development.privateSpend||0)+price;
 return true;
}
function metroExpansion(demand){
 if(!G.metro||G.policy.zoningRestriction>=92||demand.residents<350||G.region<160000)return false;
 if(demand.confidence<40||demand.hardship>45)return false;
 const hubs=stationHubs();if(hubs.length<2)return false;
 const metro=G.metro;
 // Private shareholders subscribe equity; the franchise pays its construction bills.
 if(!metro.stations.length){
  const a=hubs[0],b=hubs.find(p=>Math.abs(p.x-a.x)+Math.abs(p.y-a.y)>=11&&p.demand>10);
  if(!b)return false;
  const route=Math.abs(a.x-b.x)+Math.abs(a.y-b.y),cost=2*buildCost.metro_station+route*1100;
  if(G.region<cost+100000)return false;
  const shares=cost+36000;
  G.region-=shares;metro.cash+=shares;
  const aa=stationBuilding(a),bb=stationBuilding(b);
  if(!aa||!bb)throw Error('Metro land reservation failed');
  if(!connectMetro(aa,bb,2))throw Error('Underground capital budget mismatch');
  metro.operating=false;G.construction+=2;staticDirty=true;dirty=true;
  story('Private investors opened the Vale Underground: a two-station railway financed from subscribed shares and fares. Inspect the rail network in the map overlays.','good',aa.id);
  return true;
 }
 // Extensions need an observed passenger market and sufficient retained earnings.
 if(demand.residents<540+metro.stations.length*90||metro.cash<70000||metro.stations.length>=8||metro.rides<250)return false;
 const existing=metro.stations.map(id=>readBuild(id)).filter(Boolean);
 const outer=hubs.find(c=>existing.every(s=>Math.abs(s.x-c.x)+Math.abs(s.y-c.y)>=9)&&c.demand>18);
 if(!outer)return false;
 const near=existing.slice().sort((a,b)=>Math.abs(a.x-outer.x)+Math.abs(a.y-outer.y)-Math.abs(b.x-outer.x)-Math.abs(b.y-outer.y))[0];
 const cost=buildCost.metro_station+(Math.abs(near.x-outer.x)+Math.abs(near.y-outer.y))*1100;
 if(metro.cash<cost+18000)return false;
 const station=stationBuilding(outer);
 if(!station)return false;
 if(!connectMetro(near,station,1))throw Error('Underground extension budget mismatch');
 G.construction++;staticDirty=true;dirty=true;
 story('The privately owned Vale Underground extended its railway to a new neighbourhood.','good',station.id);
 return true;
}
function hasMetroCommute(home,work){
 const metro=G?.metro;
 if(!home||!work||!metro?.operating||!metro.lines?.length)return false;
 if(Math.abs(home.x-work.x)+Math.abs(home.y-work.y)<7)return false;
 // Stops within walking distance of the origin and destination, plus connected lines.
 const start=metro.stations.filter(id=>{const b=readBuild(id);return b&&Math.abs(b.x-home.x)+Math.abs(b.y-home.y)<=6;});
 const goal=new Set(metro.stations.filter(id=>{const b=readBuild(id);return b&&Math.abs(b.x-work.x)+Math.abs(b.y-work.y)<=6;}));
 if(!start.length||!goal.size)return false;
 const visited=new Set(start),queue=start.slice();
 for(let i=0;i<queue.length;i++){
  const at=queue[i];if(goal.has(at))return true;
  for(const line of metro.lines){if(line.readyDay>G.day)continue;const next=line.from===at?line.to:line.to===at?line.from:null;
   if(next!=null&&!visited.has(next)){visited.add(next);queue.push(next)}
  }
 }
 return false;
}
function metroOperatingDay(){
 const metro=G?.metro;if(!metro?.stations?.length)return;
 const openLines=metro.lines.filter(line=>!line.readyDay||line.readyDay<=G.day);if(!openLines.length){metro.operating=false;return;}
 const cost=5+metro.stations.length*3+metro.lines.length*5+metro.dailyRides*.025;
 const paid=Math.min(metro.cash,cost);
 metro.cash-=paid;G.region+=paid;metro.expenses+=paid;
 metro.operating=metro.cash>=cost;
 if(metro.revenue-paid<0)metro.daysInDeficit++;
 else metro.daysInDeficit=Math.max(0,metro.daysInDeficit-1);
 if(!metro.operating&&G.day%30===0)story('The private underground suspended trains after its operating reserve ran out.','bad');
 metro.dailyRides=0;
}
function drawMetroOverlay(g,subdued=false){
 if(!G.metro?.lines?.length)return;
 g.save();g.lineWidth=5;g.globalAlpha=subdued?.28:.90;
 for(let i=0;i<G.metro.lines.length;i++){
  const line=G.metro.lines[i],a=readBuild(line.from),b=readBuild(line.to);
  if(!a||!b)continue;
  const p=iso(a.x,a.y),q=iso(b.x,b.y);
  g.strokeStyle='#17232c';g.lineWidth=9;g.beginPath();g.moveTo(p[0],p[1]);g.lineTo(q[0],q[1]);g.stroke();
  g.strokeStyle=line.color;g.lineWidth=4;g.setLineDash([10,5]);g.beginPath();g.moveTo(p[0],p[1]);g.lineTo(q[0],q[1]);g.stroke();g.setLineDash([]);
  if(G.metro.operating&&(!line.readyDay||line.readyDay<=G.day)){
   const phase=(frameClock*.115+i*.21)%2,t=phase<=1?phase:2-phase;
   const xx=p[0]+(q[0]-p[0])*t,yy=p[1]+(q[1]-p[1])*t;
   g.save();g.translate(xx,yy);g.rotate(Math.atan2(q[1]-p[1],q[0]-p[0]));
   g.fillStyle='#f2e8c7';g.strokeStyle='#182c32';g.lineWidth=1.3;
   for(let wagon=-1;wagon<=1;wagon++){g.fillRect(wagon*12-5,-4,10,8);g.strokeRect(wagon*12-5,-4,10,8);
    g.fillStyle=line.color;g.fillRect(wagon*12-3,-3,6,3);g.fillStyle='#f2e8c7';}
   g.restore();
  }
 }
 if(!subdued)for(const id of G.metro.stations){const s=readBuild(id);if(!s)continue;let [x,y]=iso(s.x,s.y);
  g.fillStyle='#17232c';g.beginPath();g.arc(x,y,14,0,Math.PI*2);g.fill();g.fillStyle='#f6d17c';g.beginPath();g.arc(x,y,10,0,Math.PI*2);g.fill();g.fillStyle='#203035';g.font='bold 13px sans-serif';g.textAlign='center';g.fillText('M',x,y+4);
 }
 g.restore();
}
// Regional economy. Decisions are derived from physical land, capital and
// observable demand. The city player sets rules; agents invest their own funds.
function regionalIndustryDay(){
 if(!G)return;
 let factories=0,depots=0;
 for(const f of G.firms){
  if(f.closed)continue;
  if(f.kind==='factory')factories++;
  if(f.kind==='warehouse'){
   depots++;
   const freight=Math.min(G.region,290+Math.min(300,G.firms.filter(v=>!v.closed).length*3));
   G.region-=freight;f.cash+=freight;f.revenue+=freight;
  }else if(f.kind==='office'){
   const services=Math.min(G.region,390+Math.max(0,G.stats.marketConfidence-40)*3);
   G.region-=services;f.cash+=services;f.revenue+=services;
  }else if(f.kind==='college'){
   const students=G.households.filter(h=>h.cash>900&&h.people.some(id=>{const p=G.people[id];return p&&!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=28})).slice(0,36);
   for(const h of students){const fee=Math.min(h.cash,8.5);h.cash-=fee;h.educationExpense=(h.educationExpense||0)+fee;f.cash+=fee;f.revenue+=fee;const candidate=h.people.map(id=>G.people[id]).find(p=>p&&!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=28);
    if(candidate)candidate.skill=clamp(candidate.skill+.00007,0,1.1);
   }
   const research=Math.min(G.region,200);G.region-=research;f.cash+=research;f.revenue+=research;
   G.education=clamp(G.education+.002,0,100);
  }
 }
 G.stats.airPollution=clamp(factories*6+depots*1.5+(G.airport?.operating?4:0)-G.buildings.filter(b=>b.kind==='park').length*.6,0,100);
 // Pollution affects specific nearby families rather than a free-floating score.
 if(factories&&G.day%10===0){const plants=G.firms.filter(f=>f.kind==='factory'&&!f.closed).map(f=>readBuild(f.building)).filter(Boolean);
  for(const h of G.households){const home=readBuild(h.home);if(!home)continue;
   if(plants.some(b=>Math.abs(b.x-home.x)+Math.abs(b.y-home.y)<=4))h.stress=clamp(h.stress+.18,0,100);
  }
 }
}
function fieldLotsNear(farm,limit=6){
 const site=readBuild(farm.building);if(!site)return [];
 const result=[];
 for(let radius=1;radius<=6;radius++)for(let dy=-radius;dy<=radius;dy++)for(let dx=-radius;dx<=radius;dx++){
  if(Math.abs(dx)+Math.abs(dy)!==radius)continue;
  const x=site.x+dx,y=site.y+dy,id=roadId(x,y);
  if(!charterOwns(x,y)||x<3||y<3||x>=T-3||y>=T-3||G.tiles[id]!==0||G.landUse?.[id]||buildingAt(x,y))continue;
  // Grow a continuous farm belt, not isolated strips inside the central square.
  const civicDistance=Math.abs(x-27)+Math.abs(y-27);
  if(civicDistance<8||!urbanDescriptor(x,y).agricultural||urbanPlacementReason(x,y,'farm'))continue;
  result.push({id,x,y,score:(civicDistance>17?4:0)+(Math.abs(dx)+Math.abs(dy))*-.22+(G.tiles[roadId(x-1,y)]===3?.3:0)});
 }
 result.sort((a,b)=>b.score-a.score);
 return result.slice(0,limit);
}
function farmDistrictExpansion(demand){
 if(demand.residents<115||G.policy.zoningRestriction>=95||G.region<25000)return false;
 const farms=G.firms.filter(f=>f.kind==='farm'&&!f.closed&&f.cash>300);
 if(!farms.length)return false;
 const shortages=G.firms.filter(f=>f.kind==='mill'&&!f.closed).some(f=>(f.stock.grain||0)<70);
 let chosen=null,lots=[];
 for(const f of farms.sort((a,b)=>(G.fieldCount?.[a.id]||0)-(G.fieldCount?.[b.id]||0))){
  if((G.fieldCount?.[f.id]||0)>=15)continue;
  if(G.projects.some(p=>p.kind==='fields'&&p.firmId===f.id))continue;
  const possible=fieldLotsNear(f,4+Math.round(demand.residents/500));
  if(possible.length>=2){chosen=f;lots=possible;break}
 }
 if(!chosen)return false;
 if(!shortages&&(G.development.fields||0)>demand.residents*.14&&random()<.65)return false;
 const investment=lots.length*480;
 if(G.region<investment+10000)return false;
 G.landUse=G.landUse||{};G.fieldOwner=G.fieldOwner||{};G.projects=G.projects||[];
 for(const item of lots){G.landUse[item.id]=2;G.fieldOwner[item.id]=chosen.id;}
 const id=G.nextId++;
 G.projects.push({id,kind:'fields',firmId:chosen.id,plots:lots.map(v=>v.id),remaining:16+Math.ceil(lots.length/2),start:G.day});
 privateContract(investment);
 G.development.privateSpend=(G.development.privateSpend||0)+investment;
 staticDirty=true;dirty=true;
 story('A farmers’ cooperative cleared and planted '+lots.length+' plots of cropland outside town.','good',chosen.building);
 return true;
}
function completeFarmFields(project){
 G.fieldCount=G.fieldCount||{};
 let planted=0;
 for(const id of project.plots||[]){
  if(G.landUse?.[id]!==2||G.fieldOwner?.[id]!==project.firmId)continue;
  G.landUse[id]=1;planted++;
 }
 G.fieldCount[project.firmId]=(G.fieldCount[project.firmId]||0)+planted;
 G.development.fields=(G.development.fields||0)+planted;
 G.construction+=planted;
 story('Harvest fields established: '+planted+' new plots are producing crops.','good',G.firms[project.firmId]?.building||-1);
 staticDirty=true;dirty=true;
}
function ownerCompensation(building){
 if(building.owner===-2)return 0;
 const seller=G.households[building.owner],price=building.value*1.05,investor=propertyInvestor();
 if(G.region<price)return 0;
 G.region-=price;investor.cash+=price;investor.invested+=price;book('Regional capital',investor.name,price,'Equity subscription for property acquisition',building.id);
 investor.cash-=price;if(seller)seller.cash+=price;else G.region+=price;
 book(investor.name,seller?seller.name+' household':'Regional landowner',price,'Property acquisition with protected tenancy',building.id);
 building.owner=-2;building.title={kind:'investor',id:0};return price;
}
function urbanRedevelopment(demand){
 if(demand.residents<290||demand.confidence<33||demand.hardship>65||G.policy.zoningRestriction>=78)return false;
 if(G.projects.some(p=>p.kind==='redevelop'))return false;
 const taller=demand.residents>=620&&G.policy.zoningRestriction<=53&&demand.housingPressure>=37;
 const target=taller?'tower':'apartment',maxUnits=taller?9:4;
 if(demand.homeDemand<12&&demand.housingPressure<58)return false;
 let candidates=G.buildings.filter(b=>b.kind==='home'||(taller&&b.kind==='apartment'));
 candidates=candidates.filter(b=>!b.municipalRehousing&&b.title?.kind!=='municipal'&&!b.redevelopment&&nearRoad(b.x,b.y)&&Math.abs(b.x-27)+Math.abs(b.y-27)<(taller?22:27)&&
  (footprintOf(b).length>=4||canPlace(b.x,b.y,true,target,b)));
 candidates.sort((a,b)=>{
  const av=(Math.abs(a.x-27)+Math.abs(a.y-27))*1.4+(a.kind==='apartment'?2:0)+(a.units?.length||1)*2;
  const bv=(Math.abs(b.x-27)+Math.abs(b.y-27))*1.4+(b.kind==='apartment'?2:0)+(b.units?.length||1)*2;
  return av-bv;
 });
 const b=candidates[0];if(!b)return false;
 const cost=target==='tower'?155000:39000;
 if(G.region<cost+b.value*1.05+80000)return false;
 ownerCompensation(b);
 b.redevelopment={kind:target,started:G.day,remaining:target==='tower'?75:38};
 const occupants=b.units||[b.hh];for(const id of occupants){const h=G.households[id];if(h?.people.length)h.temporaryHousing={project:b.id,since:G.day,provider:'Prepaid regional relocation contract'};}
 if(footprintOf(b).length<4)reserveFootprint(b,target);
 G.projects.push({id:b.id,kind:'redevelop',target,remaining:b.redevelopment.remaining,duration:b.redevelopment.remaining,start:G.day,formerValue:b.value,priorKind:b.kind,units:maxUnits});
 privateContract(cost);
 G.development.privateSpend=(G.development.privateSpend||0)+cost;
 staticDirty=true;dirty=true;
 story('A private developer acquired planning approval to replace '+(b.kind==='apartment'?'an older apartment house':'a cottage')+' with a '+(taller?'residential tower':'four-unit apartment block')+'.','neutral',b.id,b.hh);
 return true;
}
function addHouseholdAt(building,capital=1700){
 const housing=migrationHousingStatus(building);if(!housing.capacity||housing.available<1||housing.reserved||housing.underConstruction)return null;
 const occupants=Math.min(2,2000-G.people.filter(p=>!p.deceased&&!p.movedAway).length);if(occupants<1)return null;
 const cash=Math.min(Math.max(0,G.region),capital);if(cash<500)return null;
 const profiles=migrationNewProfiles(occupants),assessment=G.day>1?migrationAssessment(building,profiles,cash):null;
 if(assessment&&!assessment.eligible){migrationRecord('arrival-deferred',{home:building.id,assessment});return null;}
 if(assessment&&random()>=assessment.pullProbability){migrationRecord('outside-option-preferred',{home:building.id,assessment});return null;}
 G.region-=cash;const h={id:G.households.length,name:pick(surnames),cash,home:building.id,owner:-1,people:[],income:0,rent:0,food:0,tax:0,incomeTax:0,energyTax:0,utilities:0,travel:0,aid:0,crimeLoss:0,stress:27,security:86,last:[],worklessness:0};G.households.push(h);
 for(const profile of profiles){const p={id:G.people.length,name:pick(first)+' '+h.name,...profile,hh:h.id,job:-1,last:[]};G.people.push(p);h.people.push(p.id);}
 migrationRegisterTenancy(h,building);migrationAcceptOffers(h.people.map(id=>G.people[id]),assessment);
 if(G.day>1){assignJobs();recompute();migrationRecord('household-arrival',{household:h.id,people:profiles.length,capital:cash,assessment});}return h;
}

function completeRedevelopment(b,p){
 const existing=b.kind==='apartment'?(b.units||[]).slice():(b.hh>=0?[b.hh]:[]);
 for(const id of existing){if(G.households[id])delete G.households[id].temporaryHousing;}
 b.replacedKind=p.priorKind||b.kind;b.kind=p.target;b.owner=-2;b.title={kind:'investor',id:0};b.redevelopment=null;b.lastRedeveloped=G.day;
 b.value=p.target==='tower'?560000:175000;
 b.units=existing;
 for(let k=b.units.length;k<p.units;k++){
  const h=addHouseholdAt(b,1800+Math.round(rn(0,2500)));
  if(!h)break;migrationRegisterTenancy(h,b);
 }
 if(b.units.length)b.hh=b.units[0];
 G.development.redevelopments=(G.development.redevelopments||0)+1;
 if(p.target==='tower')G.development.towers=(G.development.towers||0)+1;
 story('A '+(p.target==='tower'?'high-rise':'mid-rise apartment block')+' opened where older housing once stood. Existing residents retained homes; vacant units are offered subject to local demand.','good',b.id,b.hh);
}
function airfieldCandidate(){
 const net=graph();const options=[];
 const vectors=[[1,0],[0,1]];
 for(let y=7;y<T-7;y++)for(let x=7;x<T-7;x++){
  if(!canPlace(x,y,true,'airport'))continue;
  const adjoining=roadOffsets.map(([dx,dy])=>roadId(x+dx,y+dy)).find(id=>net.parts[id]===net.mainPart);
  if(adjoining==null)continue;
  const distance=Math.abs(x-27)+Math.abs(y-27);
  if(distance<12||distance>36)continue;
  for(const [dx,dy] of vectors){const runway=[];
   for(let i=2;i<=7;i++)for(let w=0;w<2;w++){
    const xx=x+dx*i+(dy?w:0),yy=y+dy*i+(dx?w:0),id=roadId(xx,yy);
    if(!charterOwns(xx,yy)||xx<3||yy<3||xx>=T-3||yy>=T-3||![0,3].includes(cityCell(xx,yy))||G.landUse?.[id]||buildingAt(xx,yy)){runway.length=0;break}
    runway.push(id);
   }
   if(runway.length!==12)continue;
   options.push({x,y,runway,score:distance*.22+random()*1.2});
  }
 }
 options.sort((a,b)=>b.score-a.score);
 return options[0];
}
function airfieldInvestment(demand){
 if(G.airport||demand.residents<520||demand.confidence<38||G.policy.zoningRestriction>=72||G.region<850000)return false;
 const site=airfieldCandidate();if(!site)return false;
 const outlay=225000;
 const terminal=startDevelopmentProject('airport',site,450000,120,{runway:site.runway});
 if(!terminal)return false;
 G.airport={building:terminal.id,firm:null,runway:site.runway,operating:false,passengers:0,freight:0,flights:0,initialCost:outlay,started:G.day};
 G.landUse=G.landUse||{};
 for(const id of site.runway){G.landUse[id]=2;if(G.tiles[id]===3)G.tiles[id]=0;}
 privateContract(outlay);
 G.development.privateSpend=(G.development.privateSpend||0)+outlay;
 staticDirty=true;dirty=true;
 story('A regional aviation company began constructing an airfield and runway with subscribed private capital.','good',terminal.id);
 return true;
}
function completeAirfield(b,p){
 if(!G.airport||G.airport.building!==b.id)return;
 b.kind='airport';b.value=780000;b.private=true;
 for(const id of p.runway||[])if(G.landUse?.[id]===2)G.landUse[id]=3;
 const capital=Math.min(G.region,140000);G.region-=capital;
 const f=createFirm('airport',b.x,b.y,true,()=>b);
 f.cash=capital;f.wage=36;f.jobs=6;f.kind='airport';
 G.airport.firm=f.id;G.airport.operating=true;
 G.development.airfields=(G.development.airfields||0)+1;
 story('The privately financed regional airfield opened. Tickets, freight and visitors now support its operation.','good',b.id);
}
function airfieldOperatingDay(){
 const a=G.airport;if(!a||a.firm==null)return;
 const f=G.firms[a.firm];if(!f||f.closed){a.operating=false;return}
 const residents=G.people.reduce((n,p)=>n+Number(!p.deceased&&p.movedAway!==true),0);
 if(f.workers.length<3){a.operating=false;a.dailyFlights=0;return;}
 const visitors=Math.max(0,Math.min(76,Math.floor((residents*.015+(G.stats.marketConfidence||55)*.05)*(G.regionalDemand||1))));
 const flights=Math.max(1,Math.ceil(visitors/19)),receipts=Math.min(G.region,visitors*42+flights*95);
 G.region-=receipts;f.cash+=receipts;f.revenue+=receipts;if(G.market)G.market.externalSales+=receipts;
 const fuel=Math.min(f.cash,flights*110+45);f.cash-=fuel;f.expenses+=fuel;G.region+=fuel;
 a.passengers+=visitors;a.freight+=flights*.4;a.flights+=flights;a.dailyFlights=flights;a.seats=19;a.loadFactor=visitors/(flights*19);
 a.operating=f.cash>1000;
 if(!a.operating&&G.day%30===0)story('The airfield faces a cash crisis; scheduled flights are suspended.','bad',a.building);
}
function paintDenseBuilding(g,b,x,y){
 const tower=b.kind==='tower',floors=tower?9:4,width=tower?31:27,h=floors*10;
 const by=y+TH/2+8;
 g.fillStyle='#1b2525aa';g.beginPath();g.ellipse(x+6,by+10,width,11,0,0,Math.PI*2);g.fill();
 g.fillStyle=tower?'#758b93':'#ad9c86';g.fillRect(x-width/2,by-h,width,h);
 g.fillStyle=tower?'#536973':'#846f5e';g.beginPath();g.moveTo(x+width/2,by-h);g.lineTo(x+width/2+15,by-h-7);g.lineTo(x+width/2+15,by-7);g.lineTo(x+width/2,by);g.fill();
 g.fillStyle=tower?'#a3bac0':'#dbcead';g.fillRect(x-width/2-2,by-h-6,width+4,6);
 for(let floor=0;floor<floors;floor++){
  for(let col=0;col<3;col++){
   g.fillStyle=((b.id+floor*3+col)%5===0)?'#e5c67b':tower?'#aec8cc':'#d7c19e';
   g.fillRect(x-width/2+4+col*(width-7)/3,by-h+7+floor*10,Math.max(3,(width-13)/3),5);
  }
 }
 g.fillStyle='#303d3d';g.fillRect(x-4,by-14,8,14);
 if(b.redevelopment){g.strokeStyle='#dcb86e';g.lineWidth=1.5;for(let i=-width/2;i<width/2;i+=12){g.beginPath();g.moveTo(x+i,by);g.lineTo(x+i,by-h+3);g.stroke()}}
}
function paintAirfieldTerminal(g,b,x,y){
 const by=y+TH/2+8;
 g.fillStyle='#26383b';g.fillRect(x-33,by-12,66,17);
 g.fillStyle='#afc5c0';g.fillRect(x-31,by-28,62,18);
 g.fillStyle='#506872';for(let i=-25;i<=23;i+=12)g.fillRect(x+i,by-23,8,10);
 g.fillStyle='#ebd49a';g.fillRect(x-34,by-32,68,5);
 g.fillStyle='#f2e5c4';g.font='bold 10px sans-serif';g.fillText('AIR',x-12,by-15);
 g.fillStyle='#dde8e3';g.beginPath();g.moveTo(x-17,by+2);g.lineTo(x+10,by-1);g.lineTo(x+19,by+3);g.lineTo(x+3,by+5);g.lineTo(x,by+10);g.lineTo(x-4,by+5);g.closePath();g.fill();
}

function autonomousDevelopment(){
 if(!G||!G.development)return;
 const demand=cityDemand();
 G.development.lastReport={day:G.day,homeDemand:demand.homeDemand,businessDemand:demand.businessDemand,freeLots:demand.freeLots,jobVacancy:demand.jobVacancy};
 if(!G.autoBuild)return;
 let built=[];
 if(privatelyBuiltRoads(demand))built.push('roads');
 if(privatelyBuiltHome(demand))built.push('housing');
 if(privatelyBuiltFirm(demand))built.push('business');
 if(metroExpansion(demand))built.push('underground');
 if(farmDistrictExpansion(demand))built.push('fields');
 if(urbanRedevelopment(demand))built.push('redevelopment');
 if(airfieldInvestment(demand))built.push('airfield');
 if(reverseRedevelopment())built.push('downzoning');
 if(built.length){
  G.development.decisions.push({day:G.day,kind:built.join(', '),demand:demand.homeDemand,commercial:demand.businessDemand});
  if(G.development.decisions.length>120)G.development.decisions.shift();
  recompute();assignJobs();
 }
}
function developmentPanel(){
 const d=G.development||{},p=d.lastReport||cityDemand(),m=G.metro||{stations:[],lines:[],cash:0,rides:0};
 const status=G.autoBuild?'Investors respond to demand automatically.':'Private construction paused by player.';
 return `<div class="statgrid">${stat('Housing demand',p.homeDemand+'/100')}${stat('Business demand',p.businessDemand+'/100')}${stat('Private road lots',d.roads||0)}${stat('Projects under construction',G.projects?.length||0)}${stat('Private road tolls',money(d.privateRoadTolls||0))}${stat('Private homes',d.homes||0)}${stat('New enterprises',d.firms||0)}${stat('Underground stations',m.stations.length)}${stat('Subway rides',fmt(m.rides||0))}${stat('Rail operator cash',money(m.cash||0))}${stat('Agricultural district plots',d.fields||0)}${stat('Apartment redevelopments',d.redevelopments||0)}${stat('Residential towers',d.towers||0)}${stat('Private airfields',d.airfields||0)}${stat('Downzoned properties',d.downzonings||0)}${stat('Regional passengers',fmt(G.airport?.passengers||0))}${stat('Industrial employers',G.firms.filter(f=>!f.closed&&['factory','warehouse','office'].includes(f.kind)).length)}</div>`+
 `<p class="desc">${esc(status)} Road developers finance extensions from regional capital; housing developers choose lots near jobs, and merchants enter underserved markets. Underground investors evaluate population and density, then fund stations and tunnels. Farmers acquire field plots and raise grain output; factory owners and freight depots respond to supply and demand; landlords may replace cottages with apartments or towers after assembling a site; and airport investors require a major regional market, a clear runway, and long-term operating capital. The railway pays ongoing costs from fares. Income, profit and property taxes, zoning and business rules influence investment.</p>`+
 `<p class="desc">${m.stations.length?esc('Vale Underground — '+(m.lines?.some(line=>line.readyDay>G.day)?'construction in progress':m.operating?'operating':'service suspended')+' · '+m.lines.length+' line(s) · '+money(m.fare)+' fare · '+money(m.revenue||0)+' lifetime receipts'):'No subway yet. Investors usually require at least 350 residents, sufficient density and financial confidence.'}</p>`;
}

