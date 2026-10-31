function dailyEconomy(){
 ensureMarketModel();recruitPrivateServiceStaff();marketOpen=true;const P=G.policy,live=G.firms.filter(f=>!f.closed),counts={};
 for(const f of live)counts[f.kind]=(counts[f.kind]||0)+1;
 for(const f of G.firms){f.revenue=f.pendingRevenue||0;f.pendingRevenue=0;f.expenses=f.pendingFreightExpense||0;f.pendingFreightExpense=0;f.debtDue=0;f.cogs=f.pendingCogs||0;f.pendingCogs=0;f.purchases=0;f.payroll=0;f.nonSalesIncome=0;f.recoveries=0;f.salesQty=f.pendingSalesQty||0;f.pendingSalesQty=0;f.production=0;f.profit=0;f.tax=0;f.age++;}
 for(const p of G.people){p.previousPublicRole=p.publicWork?(p.publicRole||''):'';p.publicRole='';p.publicWork=false;p.publicIncome=0;p.commuteBlocked=false;}
 for(const h of G.households){h.income=0;h.crimeLossToday=0;h.recoveredLosses=0;h.serviceReceipts=0;h.wages=0;h.pension=0;h.rentalIncome=0;h.dividends=0;h.debtService=0;h.debtDue=0;h.propertyPaid=0;h.propertyMaintenance=0;h.rent=0;h.food=0;h.tax=0;h.incomeTax=0;h.energyTax=0;h.aid=0;h.utilities=0;h.energyRebate=0;h.travel=0;h.travelDue=0;h.shoppingTravel=0;h.discretionary=0;h.last=[];}
 G.market.unmetFood=0;G.market.consumedFood=0;G.market.externalSales=0;G.market.imports=0;G.market.foodDisconnected=0;G.market.blockedCommutes=0;
 transitOperatingDay();
 for(const f of live){planEnterprise(f);f.attendingWorkers=f.workers.filter(id=>workerCanCommute(G.people[id],f));const attending=new Set(f.attendingWorkers);if(!attending.size)f.ratedOutput=0;
  const wage=workerIncome(f);for(const id of f.workers.slice()){const person=G.people[id],h=G.households[person?.hh];if(!h)continue;if(!attending.has(id)){person.commuteBlocked=true;person.commuteBlockedDays=(person.commuteBlockedDays||0)+1;G.market.blockedCommutes++;if(person.commuteBlockedDays>=30){person.job=-1;person.commuteBlockedDays=0;person.searchAfter=G.day+1;f.workers=f.workers.filter(p=>p!==id);}continue;}person.commuteBlockedDays=0;
   const gross=Math.min(wage,f.cash),tax=gross*P.incomeTax/100;f.cash-=gross;f.expenses+=gross;f.payroll+=gross;h.cash+=gross-tax;h.income+=gross;h.wages+=gross;h.incomeTax+=tax;h.tax+=tax;transferTreasury(tax,'incomeTax');if(gross<wage*.9){f.strain++;person.unpaidDays=(person.unpaidDays||0)+1;}else person.unpaidDays=0;if(person.unpaidDays>=7){person.job=-1;person.searchAfter=G.day+7;f.workers=f.workers.filter(v=>v!==id);}}
  const subsidy=Math.min(G.treasury,workingStaff(f).length*P.employmentSubsidy);G.treasury-=subsidy;f.cash+=subsidy;f.revenue+=subsidy;f.nonSalesIncome+=subsidy;G.cumulative.spending+=subsidy;
  const site=readBuild(f.building),due=(site?.value||0)*(P.commercialRate||0)/100/360,rate=Math.min(f.cash,due);f.cash-=rate;f.expenses+=rate;transferTreasury(rate,'commercialRate');
  const overhead=Math.min(f.cash,2+f.workers.length*(.6+P.businessRegulation*.035));f.cash-=overhead;f.expenses+=overhead;G.region+=overhead;
 }
 prepareWaterfrontDay(live);
 if(G.day%7===0)assignJobs();
 const exportPool={grain:250+G.stats.population*.45,flour:70+G.stats.population*.18,food:100+G.stats.population*.30,logs:100+G.stats.population*.20,timber:65+G.stats.population*.18,stone:70+G.stats.population*.12,manufactures:35+G.stats.population*.15};
 const producerCounts={};if(G.scenario==='regional')exportPool.manufactures*=6;else if(G.scenario==='industrial')exportPool.manufactures*=2.5;
 for(const f of live){const out=formulas[f.kind]?.out;if(out)producerCounts[out]=(producerCounts[out]||0)+1;}
 // Production is bounded by employed labour, anticipated sales and inventories.
 for(const kind of ['farm','fishery','forestry','quarry','mill','sawmill','bakery','factory'])for(const f of live){
  if(f.kind!==kind||!workingStaff(f).length)continue;const recipe=formulas[kind],base=SECTOR_WORKERS[kind];
  const skill=workingStaff(f).reduce((a,id)=>a+(G.people[id]?.skill||.5),0)/workingStaff(f).length;
  let capacity=recipe.qty*workingStaff(f).length/base*(.82+skill*.25+G.education*.0015)*(1+(f.scale-1)*.25);
  if(kind==='farm'){capacity*=1+Math.min(.9,(G.fieldCount?.[f.id]||0)*.035);if(seasonsEnabled())capacity*=[.85,1.15,1.35,.65][Math.floor((G.month-1)/3)];if(G.weather==='drought')capacity*=.72;}
  if(kind==='fishery')capacity=Math.min(capacity,f.fishingAllowance||0);
  f.ratedOutput=capacity;
  const expectedOrders=Math.max(1,f.salesTrend,(exportPool[recipe.out]||0)/Math.max(1,producerCounts[recipe.out])*(G.regionalDemand||1)*.8),target=expectedOrders*4.5,inventory=f.stock[recipe.out]||0;
  let quantity=Math.max(0,Math.min(capacity,target-inventory));
  if(recipe.inp){const ratio=recipe.amount/recipe.qty,need=quantity*ratio;
   if((f.stock[recipe.inp]||0)+pendingGoods(f,recipe.inp)<need*3)trade(f,recipe.inp,need*4-(f.stock[recipe.inp]||0));
   quantity=Math.min(quantity,(f.stock[recipe.inp]||0)/ratio);}
  quantity=Math.floor(quantity);if(quantity<=0)continue;
  let inputCost=0;if(recipe.inp){const used=quantity*recipe.amount/recipe.qty;inputCost=takeInventory(f,recipe.inp,used);goodsEntry(recipe.inp,'consumed',used);}
  const old=f.stock[recipe.out]||0;f.unitCost[recipe.out]=((f.unitCost[recipe.out]||0)*old+inputCost)/Math.max(1,old+quantity);
  f.stock[recipe.out]=old+quantity;f.production=quantity;goodsEntry(recipe.out,'produced',quantity);
 }
 // The external market has finite sector orders and a downward-sloping demand curve.

 const exportOffset=live.length?G.day%live.length:0;for(const f of live.slice(exportOffset).concat(live.slice(0,exportOffset))){const out=formulas[f.kind]?.out;if(out&&workingStaff(f).length){
  const ask=marketOutputPrice(f,out),relative=ask/Math.max(.1,marketPrice(out));
  const orders=exportPool[out]/producerCounts[out]*Math.pow(clamp(1/relative,.25,1.7),1.7);
  const keep=Math.max(10,f.salesTrend*.8);regionBuy(f,out,Math.max(0,Math.min(orders,(f.stock[out]||0)-keep)),ask);
 }}
 // Externally traded services require staff and share a finite pool of contracts.
 const servicePools={office:480+G.stats.population*2.4,warehouse:240+G.stats.population*.9,contractor:170+G.stats.population*.65,tavern:100+G.stats.population*.45,college:100+G.stats.population*.20};
 if(G.scenario==='regional'){servicePools.office*=1.8;servicePools.warehouse*=2;servicePools.tavern*=2.5;}
 for(const f of live){if(servicePools[f.kind]&&workingStaff(f).length){const capacity=clamp(workingStaff(f).length/(SECTOR_WORKERS[f.kind]||3),0,1.8);serviceSales(f,servicePools[f.kind]/counts[f.kind]*Math.min(1.4,capacity)*(G.regionalDemand||1));}}
 // Retailers order inventory to cover a few days of expected household demand.
 const grocers=live.filter(f=>f.kind==='grocer');
 for(const f of grocers){const daily=Math.max(15,reachableRetailDemand(f),f.salesTrend),target=daily*5;
  if((f.stock.food||0)+pendingGoods(f,'food')<daily*3)trade(f,'food',Math.max(0,target-(f.stock.food||0)));
  f.retailCapacity=workingStaff(f).length*80;}
 // A public employee cannot be counted six times across six service budgets.
 G.actualServiceFunding={police:fundedPublicPayroll(P.policeBudget),fire:fundedPublicPayroll(P.defenseBudget),outreach:fundedPublicPayroll(P.outreachBudget),transit:G.transit?.routes.length?0:fundedPublicPayroll(P.transitBudget||0)};
 const retirees=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.age>70),pensionDue=retirees.length*(P.pensionDaily||0),pensionPaid=Math.min(G.treasury,pensionDue);G.treasury-=pensionPaid;G.cumulative.spending+=pensionPaid;G.cumulative.pensions=(G.cumulative.pensions||0)+pensionPaid;for(const p of retirees){const h=G.households[p.hh],amount=pensionPaid/Math.max(1,retirees.length);h.cash+=amount;h.income+=amount;h.pension+=amount;}G.market.pensionFunding=pensionDue>0?pensionPaid/pensionDue:1;
 fundCivicServices();
 const householdLoans=new Map();for(const l of G.loans)if(l.status==='active'&&l.ownerType==='household'){if(!householdLoans.has(l.ownerId))householdLoans.set(l.ownerId,[]);householdLoans.get(l.ownerId).push(l);}
 const propertyDue=new Map();for(const b of G.buildings)if(['home','apartment','tower'].includes(b.kind)&&b.owner>=0)propertyDue.set(b.owner,(propertyDue.get(b.owner)||0)+b.value*P.propertyTax/100/360);
 const living=G.households.filter(h=>h.people.length),consumerSuppliers=live.filter(f=>['tavern','office','contractor','factory','college'].includes(f.kind)&&workingStaff(f).length>0);
 for(const h of living){
  // Withdraw only existing deposits; cash scarcity does not manufacture credit.
  const target=h.people.length*25;if(h.cash<target)for(const [id,amount] of Object.entries(h.deposits||{})){withdrawal(h,G.banks[+id],Math.min(amount,target-h.cash));if(h.cash>=target)break;}
  const home=readBuild(h.home),owner=home?.owner;
  const rent=(h.temporaryHousing||owner===h.id)?0:h.people.length*(3.1+P.zoningRestriction*.035)*(G.housingMarket?.rentIndex||1);
  const paid=Math.min(h.cash,rent);h.cash-=paid;h.rent=paid;h.rentDue=rent;
  if(owner===-2)propertyInvestor().cash+=paid;else if(G.households[owner]){const landlord=G.households[owner];landlord.cash+=paid;landlord.income+=paid;landlord.rentalIncome+=paid;}else G.region+=paid;
 }
 const shoppingOffset=living.length?hash(G.day+G.worldSeed)%living.length:0,shoppingOrder=living.slice(shoppingOffset).concat(living.slice(0,shoppingOffset)),retailReference=foodPriceEstimate();
 for(const h of shoppingOrder){
  const home=readBuild(h.home);
  let need=h.people.length*1.6,remaining=need;
  const reachable=groceryChoices(h,home,grocers),shops=reachable.filter(o=>o.f.stock.food>0&&o.f.retailCapacity>0);if(!reachable.length)G.market.foodDisconnected+=h.people.length;
  for(let {f,travel,metro,transit,distance} of shops){const unit=f.price*(1+P.foodTax/100);let q=Math.min(remaining,f.stock.food,f.retailCapacity,Math.max(0,h.cash-travel)/unit);if(q<=0)continue;
   if(transit&&!transitReserve(transit,2)){transit=null;metro=false;travel=distance*.035*2;q=Math.min(remaining,f.stock.food,f.retailCapacity,Math.max(0,h.cash-travel)/unit);if(q<=0)continue;}
   if(transit){transitDemand(transit,false,2);transitCollectFare(h,transit,2);h.shoppingTravel+=travel;}else{
   h.cash-=travel;h.travel+=travel;h.travelDue+=travel;h.shoppingTravel+=travel;if(metro){G.metro.cash+=travel;G.metro.dailyRides+=2;G.metro.rides+=2;G.metro.revenue+=travel;}else G.region+=travel;}
   const net=q*f.price,tax=net*P.foodTax/100;h.cash-=net+tax;h.food+=net+tax;f.cash+=net;f.revenue+=net;takeInventory(f,'food',q,true);f.retailCapacity-=q;goodsEntry('food','consumed',q);transferTreasury(tax,'foodTax');remaining-=q;if(remaining<.001)break;}

  G.market.consumedFood+=need-remaining;G.market.unmetFood+=remaining;
  h.stress=clamp(h.stress+(remaining>.1?remaining*.30:-.20),0,100);
  const cold=seasonsEnabled()&&(G.month>=10||G.month<=2),bill=h.people.length*(2.25+(cold?1.8:0))*(1+P.utilityTax/100),energy=regionalUtilityAccess(home)?Math.min(h.cash,bill):0,levy=energy-energy/(1+P.utilityTax/100);
  h.utilityConnected=regionalUtilityAccess(home);h.utilityDue=bill;h.cash-=energy;h.utilities=energy;h.energyTax=levy;G.region+=energy-levy;transferTreasury(levy,'utilityTax');if(energy<bill*.8)h.stress=clamp(h.stress+.35,0,100);
  for(const id of h.people){const person=G.people[id];if(person.job<0||person.commuteBlocked)continue;const firm=G.firms[person.job],work=firm&&readBuild(firm.building);if(!work||!home)continue;if(person.transitTrip?.day===G.day){transitCollectFare(h,person.transitTrip);continue;}const dist=Math.abs(home.x-work.x)+Math.abs(home.y-work.y),metro=hasMetroCommute(home,work)&&G.metro?.operating;
   const fareDue=metro?G.metro.fare:dist*.035*(1-clamp(P.transitBudget*(G.actualServiceFunding?.transit||0)/280,0,.65)),fare=Math.min(h.cash,fareDue);h.travelDue+=fareDue;h.cash-=fare;h.travel+=fare;if(metro){G.metro.cash+=fare;G.metro.dailyRides++;G.metro.rides++;G.metro.revenue+=fare;}else G.region+=fare;}
  loanPayments(householdLoans.get(h.id)||[]);
  const propertyReserve=propertyDue.get(h.id)||0;h.essentialDue=(h.rentDue||0)+need*(reachable[0]?.f.price||retailReference)*(1+P.foodTax/100)+bill+h.travelDue+propertyReserve;
  const disposable=Math.max(0,h.income-h.incomeTax-h.food-h.rent-h.utilities-h.travel-h.debtService-propertyReserve),wealth=h.cash+Object.values(h.deposits||{}).reduce((a,v)=>a+v,0);
  h.normalDisposable=(h.normalDisposable??disposable)*.96+disposable*.04;
  // Lower rates modestly reduce desired cash saving; income remains the main budget.
  let budget=Math.min(Math.max(0,h.cash-propertyReserve),Math.max(0,h.normalDisposable*.55+(wealth-h.people.length*500)*.0006)*clamp(1.08-(P.policyRate||0)*.018,.65,1.1));
  const suppliers=consumerSuppliers.filter(f=>sharesRoadNetwork(home,readBuild(f.building)));
  for(let j=0;j<Math.min(3,suppliers.length)&&budget>.01;j++){const f=suppliers[(h.id*7+G.day+j*11)%suppliers.length],amount=budget/(3-j);let actual=amount;
   if(f.kind==='factory'){const q=Math.min(f.stock.manufactures||0,amount/(marketPrice('manufactures')*1.25));actual=q*marketPrice('manufactures')*1.25;takeInventory(f,'manufactures',q,true);goodsEntry('manufactures','consumed',q);}
   h.cash-=actual;h.discretionary+=actual;f.cash+=actual;f.revenue+=actual;budget-=actual;}
 }
 if(P.propertyTax>0)for(const b of G.buildings.filter(b=>['home','apartment','tower'].includes(b.kind))){const owner=b.owner===-2?propertyInvestor():G.households[b.owner];if(!owner)continue;const pay=Math.min(owner.cash,b.value*P.propertyTax/100/360);owner.cash-=pay;owner.propertyPaid=(owner.propertyPaid||0)+pay;transferTreasury(pay,'propertyTax');}
 const poor=living.slice().sort((a,b)=>a.cash/a.people.length-b.cash/b.people.length);
 for(const [budgetKey,limit] of [['aidBudget',30],['energyAidBudget',8]]){let left=Math.min(P[budgetKey]||0,G.treasury);for(const h of poor){if(left<.01||h.cash/h.people.length>300)break;const amount=Math.min(left,limit);h.cash+=amount;h.aid+=amount;G.treasury-=amount;left-=amount;G.cumulative.welfare+=amount;G.cumulative.spending+=amount;}}
 privateServiceDay();
 for(const h of living){const workers=h.people.some(id=>(G.people[id]?.job>=0&&!G.people[id]?.commuteBlocked)||G.people[id]?.publicWork);h.worklessness=workers?0:(h.worklessness||0)+1;h.stress=clamp(h.stress+(h.cash<h.people.length*50?.12:workers?-.06:.02),0,100);}
 const foodPrice=grocers.length?grocers.reduce((a,f)=>a+f.price,0)/grocers.length:G.market.baseFoodPrice,previous=G.market.cpi;
 G.market.cpi=100*(.55*foodPrice/G.market.baseFoodPrice+.25*(G.housingMarket?.rentIndex||1)+.20);G.market.inflation=(G.market.cpi/Math.max(1,previous)-1)*360*100;
 restartViableEnterprise();
}
function finalizeMarketBooks(){
 for(const f of G.firms){if(f.closed)continue;f.profit=f.revenue-(f.cogs||0)-f.expenses;f.tax=Math.min(f.cash,Math.max(0,f.profit)*G.policy.profitTax/100);f.cash-=f.tax;transferTreasury(f.tax,'profitTax');f.netProfit=f.profit-f.tax;
  f.salesTrend=f.salesTrend*.965+(f.salesQty||0)*.035;f.revenueTrend=f.revenueTrend*.965+Math.max(0,f.revenue-f.recoveries)*.035;f.marginTrend=f.marginTrend*.965+clamp(f.netProfit/Math.max(1,f.revenue,f.revenueTrend),-1,1)*.035;
  f.operating={sales:Math.max(0,f.revenue-f.nonSalesIncome),otherIncome:f.nonSalesIncome,costOfGoods:f.cogs||0,payroll:f.payroll||0,otherCosts:Math.max(0,f.expenses-(f.payroll||0)),profitTax:f.tax,netProfit:f.netProfit,purchases:f.purchases||0,inventoryValue:Object.entries(f.stock).reduce((n,[k,q])=>n+q*(f.unitCost[k]??marketPrice(k)),0)};
  if(f.cash<Math.max(100,workerIncome(f)*f.jobs*2))f.strain++;else f.strain=Math.max(0,f.strain-2);
  if((f.netProfit<0||f.revenue<1)&&f.cash<1000)f.lossDays++;else f.lossDays=Math.max(0,f.lossDays-1);
  if(f.lossDays>75&&f.cash<workerIncome(f)*Math.max(1,f.workers.length)*3)liquidateFirm(f,'persistent operating losses after capacity adjustments');
  const owner=G.households[f.owner];if(owner&&f.netProfit>0&&f.cash>workerIncome(f)*f.jobs*60){const dividend=Math.min(f.cash*.002,f.netProfit*.20);f.cash-=dividend;owner.cash+=dividend;owner.income+=dividend;owner.dividends=(owner.dividends||0)+dividend;}
  f.history.push(f.cash);if(f.history.length>45)f.history.shift();
 }
 updateCreditObservations();marketOpen=false;
}
function policePower(){const b=G.buildings.filter(b=>b.kind==='police').length,court=G.buildings.filter(b=>b.kind==='courthouse').length;const funded=G.actualServiceFunding?.police??1;return clamp(.035+funded*((G.policy.policeBudget/(G.stats.population*.7+1))*.48 + b*.10+court*.05),.035,.95)}
function defensePower(){const b=G.buildings.filter(b=>b.kind==='fire'&&isPublicFacility(b)).length;const funded=G.actualServiceFunding?.fire??1;return clamp(.025+funded*((G.policy.defenseBudget/(G.stats.population*.65+1))*.50+b*.1),.025,.96)}
function incidents(){
 const unemployment=1-G.people.filter(p=>!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=70&&((p.job>=0&&!p.commuteBlocked)||p.publicWork)).length/Math.max(1,G.people.filter(p=>!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=70).length);
 const residentHouseholds=G.households.filter(h=>h.people.length>0);
 const hardship=residentHouseholds.filter(h=>h.stress>60||householdLiquidity(h)<150).length/Math.max(1,residentHouseholds.length);
 const danger=(.075+unemployment*.11+hardship*.07)*G.stats.population/300*(1-policePower()*.7)*(1-Math.min(.4,G.policy.outreachBudget*(G.actualServiceFunding?.outreach??1)/400)*.24);
 if(random()<danger){let b=pick(G.buildings.filter(b=>['home','grocer','bakery','mill','farm','sawmill','quarry','contractor'].includes(b.kind)));
    if(b){let loss=0,hid=-1;const police=closestRoadBuilding(b.x,b.y,'police');const distance=police?roadServiceDistance(b,police):80;const localCoverage=clamp(1-distance/60,0,1)*policePower();
      if(b.kind==='home'){const h=G.households[b.hh];if(!h?.people.length)return;if(h){hid=h.id;loss=Math.min(h.cash,rn(45,340)*(1-localCoverage*.38));h.cash-=loss;h.crimeLoss+=loss;h.crimeLossToday=(h.crimeLossToday||0)+loss;h.security=clamp(h.security-rn(5,14),0,100);h.stress=clamp(h.stress+2,0,100);}}
      else{const f=G.firms[b.firm];if(f){loss=Math.min(f.cash,rn(130,600)*(1-localCoverage*.38));f.cash-=loss;f.theft+=loss;f.expenses=(f.expenses||0)+loss}}
      // stolen cash is redistributed among agents; cannot disappear without a counterparty
      const suspects=G.households.filter(h=>h.id!==hid&&h.people.length);
      const offender=suspects.length?pick(suspects):null;if(offender)offender.cash+=loss;else G.region+=loss;
      let item={day:G.day,offender:offender?.id??-1,loss,resolved:false,text:(b.kind==='home'?'Burglary at '+G.households[b.hh].name+' cottage':'Theft at '+G.firms[b.firm].name)+'; reported loss '+money(loss)+'.',type:'bad',bid:b.id,hid};
      G.cases.unshift(item);G.cases.length=Math.min(G.cases.length,100);emergencyDispatch(b,'police');G.cumulative.crime+=1;story(item.text,'bad',b.id,hid);
    }
 }
 if(random()<.025*G.stats.population/300){const b=pick(G.buildings.filter(b=>b.kind!=='road'));if(b){const localResponse=Math.max(publicFireResponse(b),privateFireResponse(b));let damage=rn(1,16)*(1-localResponse*.78);emergencyDispatch(b,'fire');
     b.condition=clamp(b.condition-damage,0,100);G.cumulative.fires++;
     const recovery=Math.max(0,damage)*b.value/2500;let owner=b.kind==='home'?G.households[b.owner]:G.firms[b.firm];
     if(owner&&owner.cash){let paid=Math.min(owner.cash,recovery);owner.cash-=paid;if(b.kind==='home')owner.propertyMaintenance=(owner.propertyMaintenance||0)+paid;else owner.expenses=(owner.expenses||0)+paid;G.region+=paid;b.condition=clamp(b.condition+paid*2500/b.value,0,100)}
     story('A fire damaged '+(types[b.kind]?types[b.kind].n:'property')+'; estimated '+fmt(damage)+' condition points lost.','bad',b.id)
 }}
}
function recompute(){
 let people=G.people.filter(p=>!p.deceased&&p.movedAway!==true).length,working=G.people.filter(p=>!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=70),employed=working.filter(p=>(p.job>=0&&!p.commuteBlocked)||p.publicWork).length,poor=G.households.filter(h=>h.people.length>0&&(householdLiquidity(h)/Math.max(1,h.people.length)<150||h.stress>65)).length;
 const safety=clamp(Math.round(60+policePower()*34+G.policy.outreachBudget*(G.actualServiceFunding?.outreach??1)/30-poor/Math.max(1,G.households.filter(h=>h.people.length>0).length)*28),0,100);
 const businessCount=G.firms.filter(f=>!f.closed).length;
 const oldStats=G.stats||{};
 G.stats={population:people,employed,workforce:working.length,employment:working.length?Math.round(employed/working.length*100):100,unemployment:working.length?Math.round((working.length-employed)/working.length*100):0,
   hardship:Math.round(poor/Math.max(1,G.households.filter(h=>h.people.length>0).length)*100),safety,preparedness:Math.round(defensePower()*100),businesses:businessCount,
   cash:G.households.reduce((s,h)=>s+h.cash,0),businessCash:G.firms.reduce((s,f)=>s+f.cash,0),dailyCrime:G.cases.filter(c=>c.day>G.day-30).length,
   income:G.households.reduce((s,h)=>s+h.income,0),townBalance:G.treasury+(G.publicReserve||0)-G.debt};
 for(let k of ['health','education','wellbeing','marketConfidence','roadCondition','roadService','militia','realWages','prosperity','avgCash','compliance','propertyCosts','airPollution'])if(oldStats[k]!=null&&Number.isFinite(oldStats[k]))G.stats[k]=oldStats[k];
 G.stats.health=Math.round(G.health??74);G.stats.education=Math.round(G.education??46);if(G.day%10===1||!G.roadMetrics)G.roadMetrics=roadMetrics();G.stats.roadAccess=G.roadMetrics.totalFirms?Math.round(G.roadMetrics.connectedFirms/G.roadMetrics.totalFirms*100):100;
 if(G.stats.wellbeing==null)G.stats.wellbeing=72;if(G.stats.marketConfidence==null)G.stats.marketConfidence=60;
}
// === MARKET CITY: ENDOGENOUS PRIVATE URBAN DEVELOPMENT ===
// Municipal policy affects the expected returns. Construction itself is paid
// by investors or existing firms, not awarded to the player for free.
