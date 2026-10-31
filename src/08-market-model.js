let marketOpen=false;
function policyNumber(value){return Number(value||0).toLocaleString('en-CA',{maximumFractionDigits:2});}
// A stock-flow consistent operating model. Inventory purchases are assets;
// cost of goods becomes expense when sold, rather than when a warehouse fills.
function householdLiquidity(h){return h.cash+Object.values(h.deposits||{}).reduce((n,v)=>n+Math.max(0,v),0);}
const SECTOR_WORKERS={farm:4,fishery:3,mill:3,bakery:3,grocer:2,forestry:3,sawmill:3,quarry:3,contractor:4,tavern:3,factory:7,warehouse:4,office:6,college:5,airport:6};
function ensureMarketModel(){
 if(!G.market)G.market={version:2,cpi:100,inflation:0,baseFoodPrice:5.2,unmetFood:0,consumedFood:0,externalSales:0,imports:0,privateRestartCapital:0};
 G.market.version=2;for(const p of G.people)if(p.age>70&&p.job>=0){p.job=-1;p.retired=true;}
 for(const f of G.firms){
  f.workers=f.workers.filter(id=>G.people[id]?.job===f.id&&!G.people[id]?.deceased&&!G.people[id]?.movedAway);
  f.unitCost=f.unitCost||Object.fromEntries(Object.keys(goods).map(k=>[k,marketPrice(k)]));f.ask=f.ask||{};f.operating=f.operating||{};
  if(!Number.isFinite(f.salesTrend))f.salesTrend=formulas[f.kind]?.qty*.65||30;
  if(!Number.isFinite(f.revenueTrend))f.revenueTrend=Math.max(1,workerIncome(f)*f.workers.length*1.3);
  if(!Number.isFinite(f.marginTrend))f.marginTrend=.12;f.marginTrend=clamp(f.marginTrend,-1,1);
  f.scale=f.scale||1;f.workingCapitalRaised=f.workingCapitalRaised||0;
 }
}
function foodRetailTarget(f){
 const staff=Math.max(1,workingStaff(f).length),volume=Math.max(15,Math.min(reachableRetailDemand(f),staff*80)),cost=f.unitCost?.food||marketPrice('food');
 return (cost+workerIncome(f)*staff/volume+.12)*(1.10+G.policy.businessRegulation*.0004);
}
function recordInventoryPurchase(f,good,qty,total){
 const held=(f.stock[good]||0)+pendingGoods(f,good);f.unitCost=f.unitCost||{};
 f.unitCost[good]=((f.unitCost[good]||marketPrice(good))*held+total)/Math.max(.001,held+qty);
 f.purchases=(f.purchases||0)+total;f.cashFlow=(f.cashFlow||0)-total;
}
function takeInventory(f,good,qty,sold=false){
 qty=Math.min(Math.max(0,qty),f.stock[good]||0);f.stock[good]=(f.stock[good]||0)-qty;
 const cost=qty*(f.unitCost?.[good]??marketPrice(good));
 if(sold){if(marketOpen){f.cogs=(f.cogs||0)+cost;f.salesQty=(f.salesQty||0)+qty;}else{f.pendingCogs=(f.pendingCogs||0)+cost;f.pendingSalesQty=(f.pendingSalesQty||0)+qty;}}
 return cost;
}
function marketOutputPrice(f,good){return f.ask?.[good]||marketPrice(good);}
function planEnterprise(f){
 if(f.closed)return;
 const wage=workerIncome(f),base=SECTOR_WORKERS[f.kind]||4,recipe=formulas[f.kind]?.out?formulas[f.kind]:null;
 if(f.kind==='grocer'){const target=foodRetailTarget(f);f.price=f.age<3?target:f.price*.93+target*.07;}
 if(recipe){
  const unitInputs=recipe.inp?(recipe.amount/recipe.qty)*(f.unitCost[recipe.inp]||marketPrice(recipe.inp)):0;
  const efficiency=recipe.qty/base*(f.kind==='farm'?1+Math.min(.9,(G.fieldCount?.[f.id]||0)*.035):1);
  const breakEven=unitInputs+wage/Math.max(1,efficiency)+.10;
  const target=Math.max(marketPrice(recipe.out)*.94,breakEven*1.16);
  f.ask[recipe.out]=(f.ask[recipe.out]||target)*.96+target*.04;
 }
 if(G.day%14!==0||f.age<28)return;
 // Inventories and realized orders guide labour demand; losses are not a dice roll.
 let desired=f.jobs;
 if(f.kind==='airport')desired=4+Math.ceil((G.airport?.dailyFlights||1)*1.5);
 else if(recipe){const perWorker=recipe.qty/base*(.88+G.education*.0015)*(f.kind==='farm'?1+Math.min(.9,(G.fieldCount?.[f.id]||0)*.035):1);
  desired=Math.ceil(Math.max(1,f.salesTrend)*1.12/Math.max(1,perWorker));
 }else if(f.kind==='grocer')desired=Math.ceil(Math.max(1,f.salesTrend)/65);
 else desired=Math.ceil(Math.max(0,f.revenueTrend-f.cogs*.2)/(wage*1.45));
 desired=clamp(desired,1,Math.ceil(base*f.scale*2));
 if(f.marginTrend<-.18&&f.cash<wage*Math.max(1,f.jobs)*60)desired=Math.min(desired,Math.max(1,f.jobs-1));
 if(desired>f.jobs&&f.cash<wage*(desired-f.jobs)*35+1800)desired=f.jobs;
 if(desired!==f.jobs){f.jobs+=Math.sign(desired-f.jobs);while(f.workers.length>f.jobs){const blocked=f.workers.findIndex(id=>!workerCanCommute(G.people[id],f)),id=f.workers.splice(blocked<0?f.workers.length-1:blocked,1)[0];if(G.people[id])G.people[id].job=-1;}}
 if(f.workers.some(id=>workerCanCommute(G.people[id],f))&&!f.pendingEquipment&&f.marginTrend>.16&&f.cash>wage*f.jobs*100&&f.scale<2.2&&(recipe?f.ratedOutput>0&&f.salesTrend*1.12>=f.ratedOutput&&(!recipe.inp||(f.stock[recipe.inp]||0)+pendingGoods(f,recipe.inp)>=recipe.amount*f.workers.length/base):f.jobs>=Math.ceil(base*f.scale*2)&&f.workers.length>=f.jobs)){const cost=1500+base*130,annualGain=f.revenueTrend*.015*360*(1-G.policy.profitTax/100);if(f.cash>cost+6000&&annualGain>cost*((G.policy.policyRate||0)/100+.08)){f.cash-=cost;G.region+=cost;f.pendingEquipment={gain:.06,cost,ordered:G.day,ready:G.day+30};f.capex=(f.capex||0)+cost;}}
 const unemployment=G.stats.unemployment||0;
 if(f.marginTrend>.18&&unemployment<9)f.wage=Math.min(80,f.wage*1.0015);
 else if(f.marginTrend<0)f.wage=Math.max(G.policy.minWage,f.wage*.998);
}
function enterpriseRevenue(f,amount){f.cash+=amount;if(marketOpen)f.revenue+=amount;else f.pendingRevenue=(f.pendingRevenue||0)+amount;}
function serviceSales(f,amount){
 amount=Math.min(Math.max(0,G.region),Math.max(0,amount));G.region-=amount;f.cash+=amount;f.revenue+=amount;G.market.externalSales+=amount;return amount;
}
function fundedPublicPayroll(amount,share=.65,eligible=null,role=''){
 const paid=Math.max(0,Math.min(G.treasury,amount));G.treasury-=paid;G.cumulative.spending+=paid;
 let payroll=paid*share,spent=0,wage=Math.max(24,G.policy.minWage);
 const available=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.age>=18&&p.age<=70&&p.job<0&&(p.publicIncome||0)<wage&&(eligible?eligible(p):!p.previousPublicRole));
 for(const p of available){if(payroll<.001)break;const h=G.households[p.hh];if(!h?.people.length)continue;const pay=Math.min(payroll,wage-(p.publicIncome||0));const tax=pay*G.policy.incomeTax/100;h.cash+=pay-tax;h.income+=pay;h.wages=(h.wages||0)+pay;h.tax+=tax;h.incomeTax+=tax;transferTreasury(tax,'incomeTax');p.publicIncome=(p.publicIncome||0)+pay;p.publicWork=p.publicIncome>=wage*.5;if(role)p.publicRole=role;payroll-=pay;spent+=pay;}
 G.region+=paid-spent;return amount>0?paid/amount:0;
}
// Explicit operating standards, expressed in the same resident capacities used
// by the existing facilities. Five clinic teams cover 350 residents; ten school
// staff cover 260. The public wage and existing 65% payroll share price the work;
// remaining purchases pay regional staff/suppliers, including when locals work.
const CIVIC_STANDARDS={health:{building:'clinic',capacity:350,staff:5},school:{building:'school',capacity:260,staff:10}};
function purchaseCivicService(kind,authorized){
 const standard=CIVIC_STANDARDS[kind],population=Math.max(0,G.stats.population),facilities=G.buildings.filter(b=>b.kind===standard.building).length;
 const wage=Math.max(24,G.policy.minWage),required=population*standard.staff/standard.capacity*wage/.65;
 const facilityCoverage=population?Math.min(1,facilities*standard.capacity/population):0;
 const access=serviceAccess(kind),staffing=civicStaffCapacity(kind,authorized,access),requested=Math.min(Math.max(0,authorized),required*Math.min(access.coverage,staffing.coverage)),paid=requested*fundedPublicPayroll(requested,.65,p=>qualifiedForService(p,kind)&&civicCandidateSets.get(kind).has(p.id),kind);
 const coverage=required?Math.min(access.coverage,paid/required):0;
 const result={day:G.day,authorized,required,requested,paid,unspent:Math.max(0,authorized-paid),population,facilities,facilityCoverage,accessCoverage:access.coverage,accessLimit:access.limit,accessibleResidents:access.served,staffing,coverage,wage};
 if(!G.serviceProvision)G.serviceProvision={};G.serviceProvision[kind]=result;
 return coverage;
}
function restartViableEnterprise(){
 if(G.day%30!==0||G.region<70000)return;
 const open=G.firms.filter(f=>!f.closed),population=G.stats.population;
 const desired={grocer:Math.ceil(population/100),farm:Math.ceil(population/100),mill:Math.ceil(population/220),bakery:Math.ceil(population/140),office:Math.ceil(population/120),factory:Math.ceil(population/240),contractor:Math.ceil(population/180),tavern:Math.ceil(population/160),forestry:1,sawmill:1,quarry:1,warehouse:Math.ceil(population/300)};
 const counts={};for(const f of open)counts[f.kind]=(counts[f.kind]||0)+1;
 for(const f of G.firms){if(!f.closed||!readBuild(f.building)||G.day-(f.closedDay||0)<120||(counts[f.kind]||0)>=(desired[f.kind]||1))continue;
  // An investment must clear a return hurdle and afford the actual legal payroll.
  const base=SECTOR_WORKERS[f.kind]||3,wage=Math.max(G.policy.minWage,28),recipe=formulas[f.kind]?.out?formulas[f.kind]:null;
  const perWorkerRevenue=recipe?recipe.qty/base*marketPrice(recipe.out)-(recipe.amount||0)/base*marketPrice(recipe.inp):f.kind==='grocer'?65*(foodRetailTarget({...f,jobs:2})-marketPrice('food')):48;
  const expected=perWorkerRevenue-wage*(1+G.policy.businessRegulation*.003);
  const capital=6000+wage*base*45+G.policy.permitFee;
  if(expected*base*360*(1-G.policy.profitTax/100)<=capital*((G.policy.policyRate||0)/100+.08)||G.policy.permitFee>1600)continue;
  if(G.region<capital+50000)continue;
  const owner=G.households[f.owner];if(owner)owner.cash+=f.cash;else G.region+=f.cash;
  G.region-=capital;f.cash=capital-G.policy.permitFee;transferTreasury(G.policy.permitFee,'permits');f.closed=false;f.closedDay=0;f.strain=0;f.lossDays=0;f.jobs=base;f.wage=wage;f.marginTrend=.1;f.reopenedDay=G.day;f.workingCapitalRaised+=capital;G.market.privateRestartCapital+=capital;
  story('Investors reopened '+f.name+' after a demand and operating-margin review.','good',f.building);assignJobs();return;
 }
}
