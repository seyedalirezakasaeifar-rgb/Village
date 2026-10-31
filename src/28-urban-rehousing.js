// Replacement housing is actual municipal property, commissioned before clearing
// tenants' homes. No household is spawned to occupy this reserved dwelling.
function urbanRehousingQuote(){
 const reserved=G.buildings.filter(b=>b.relocationReserve).length+(G.projects||[]).filter(p=>p.municipalRehousing).length;
 if(reserved>=8)return {ok:false,reason:'Eight replacement homes are already reserved or under construction. Use the existing reserve before commissioning more.'};
 const places=buildableCandidates('housing').filter(p=>canPlace(p.x,p.y,true,'home')).sort((a,b)=>urbanSiteSuitability(b.x,b.y,'home')-urbanSiteSuitability(a.x,a.y,'home')||a.x-b.x||a.y-b.y);
 if(!places.length)return {ok:false,reason:'Connect and zone a vacant residential lot before commissioning replacement housing.'};
 const place=places[0];return {ok:true,x:place.x,y:place.y,cost:buildCost.home,days:24,reason:'Commission a vacant municipal home with road access. It remains reserved for actual displaced residents, rather than creating a new household.'};
}
function commissionUrbanRehousing(quote){
 const reserved=G.buildings.filter(b=>b.relocationReserve).length+(G.projects||[]).filter(p=>p.municipalRehousing).length;
 if(reserved>=8||!quote||quote.cost!==buildCost.home||!Number.isInteger(quote.x)||!Number.isInteger(quote.y)||!canPlace(quote.x,quote.y,true,'home')||G.treasury<buildCost.home)return {ok:false,reason:'The housing site or budget changed. Review the current quote.'};
 const q={x:quote.x,y:quote.y,cost:buildCost.home,days:24};
 const site=startDevelopmentProject('home',q,48000,q.days,{value:48000,municipalRehousing:true});if(!site)return {ok:false,reason:'The quoted site is no longer vacant.'};
 G.treasury-=q.cost;G.region+=q.cost;G.cumulative.spending+=q.cost;G.cumulative.rehousingCapital=(G.cumulative.rehousingCapital||0)+q.cost;
 book('Municipal housing capital','Regional construction contract',q.cost,'Vacant replacement dwelling',site.id);story('A municipal replacement home is under construction. Its tenancy is reserved for people displaced by a later paid land assembly.','neutral',site.id);save();dirty=true;return {ok:true,reason:'Replacement housing commissioned; existing residents retain their homes during construction.',building:site.id};
}
function urbanHousingRent(h,home,base){return home?.municipalRehousing?Math.min(base,Math.max(0,((h.income||0)-(h.tax||0))*.25)):base;}
function urbanMunicipalHousingDay(){
 for(const b of G.buildings){if(!b.municipalRehousing||b.kind!=='home')continue;
  const cost=Math.min(Math.max(0,G.treasury),1);G.treasury-=cost;G.region+=cost;G.cumulative.spending+=cost;G.cumulative.housingMaintenance=(G.cumulative.housingMaintenance||0)+cost;b.condition=clamp(b.condition+(cost>=1?.025:-.04),0,100);
 }
}
function validateUrbanRehousing(data){
 return (data.projects||[]).every(p=>p.municipalRehousing==null||p.municipalRehousing===true&&p.kind==='home'&&p.value===48000&&!p.privateService&&!p.retailCentre)&&data.buildings.every(b=>{
  if(b.municipalRehousing==null&&b.relocationReserve==null)return true;
  return b.kind==='home'&&b.municipalRehousing===true&&typeof b.relocationReserve==='boolean'&&b.owner===-1&&b.title?.kind==='municipal'&&(!b.relocationReserve||!data.households.some(h=>h.home===b.id&&h.people.length));
 });
}

function urbanRelocationFields(x,y,count){
 const footprint=new Set(footprintFor(x,y,'farm')),plots=[];
 for(let radius=1;radius<=8&&plots.length<count;radius++)for(let dy=-radius;dy<=radius;dy++)for(let dx=-radius;dx<=radius;dx++){
  if(Math.abs(dx)+Math.abs(dy)!==radius||plots.length>=count)continue;const px=x+dx,py=y+dy,id=roadId(px,py);
  if(px<3||py<3||px>=T-3||py>=T-3||!charterOwns(px,py)||footprint.has(id)||G.tiles[id]!==0||G.landUse?.[id]||buildingAt(px,py)||!urbanDescriptor(px,py).agricultural||urbanPlacementReason(px,py,'farm'))continue;
  plots.push({id,x:px,y:py});
 }return plots;
}

function urbanRelocationAffordable(h,dest,origin){
 if(dest.municipalRehousing||dest.owner===h.id)return true;
 const base=h.people.length*(3.1+G.policy.zoningRestriction*.035)*(G.housingMarket?.rentIndex||1)*urbanRentMultiplier(dest);
 const wages=h.people.reduce((n,id)=>{const p=G.people[id];if(!p||p.deceased||p.movedAway)return n;if(p.age>70)return n+(G.policy.pensionDaily||0);const f=p.job>=0&&G.firms[p.job];return n+(f&&!f.closed&&!p.commuteBlocked?Math.max(G.policy.minWage,f.wage)*(1-G.policy.incomeTax/100):0);},0);
 const net=Math.max(0,(h.income||0)-(h.tax||0),wages),ownerPremium=urbanTitleAccount(origin)===h?Math.max(0,origin.value*1.1):0;
 const reserve=Math.max(0,householdLiquidity(h)+ownerPremium+2000-h.people.length*200);
 return base<=net*.35+reserve/720;
}
