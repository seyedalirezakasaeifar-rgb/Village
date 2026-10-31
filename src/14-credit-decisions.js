function foodPriceEstimate(){const shops=G.firms.filter(f=>!f.closed&&f.kind==='grocer'&&f.price>0);return shops.length?shops.reduce((n,f)=>n+f.price,0)/shops.length:(G.market?.baseFoodPrice||5.2);}
function openingHouseholdIncome(h){return h.people.reduce((sum,id)=>{const p=G.people[id];if(!p||p.deceased||p.movedAway)return sum;if(p.age>70)return sum+(G.policy.pensionDaily||0);const f=G.firms[p.job];return sum+(f&&!f.closed&&!p.commuteBlocked?workerIncome(f)*(1-G.policy.incomeTax/100):0);},0);}
function expectedHouseholdEssentials(h){
 if(Number.isFinite(h.essentialDueTrend))return h.essentialDueTrend;
 const home=readBuild(h.home),rent=home?.owner===h.id||h.temporaryHousing?0:h.people.length*(3.1+G.policy.zoningRestriction*.035)*(G.housingMarket?.rentIndex||1);
 const property=G.buildings.filter(b=>b.owner===h.id&&['home','apartment','tower'].includes(b.kind)).reduce((n,b)=>n+b.value*G.policy.propertyTax/100/360,0);
 return rent+property+h.people.length*(1.6*foodPriceEstimate()*(1+G.policy.foodTax/100)+2.25*(1+G.policy.utilityTax/100));
}
function assessCredit(kind,owner,amount,term,rate){
 const strict=clamp((G.policy.lendingRules||0)/100,0,1),stressRate=rate+.02,scheduled=amount/term+amount*rate/360,stressed=amount/term+amount*stressRate/360;
 let recurring,essential,buffer;
 if(kind==='household'){
  recurring=Number.isFinite(owner.netIncomeTrend)?Math.max(0,owner.netIncomeTrend-Math.sqrt(owner.incomeVariance||0)):openingHouseholdIncome(owner);
  essential=expectedHouseholdEssentials(owner);buffer=Math.max(0,householdLiquidity(owner)-essential*90)/term;
 }else{recurring=Math.max(0,(owner.revenueTrend||0)*Math.max(0,owner.marginTrend||0));essential=0;buffer=Math.max(0,owner.cash-workerIncome(owner)*Math.max(1,owner.jobs)*45)/term;}
 const capacity=Math.max(0,recurring-essential)/(1.25+strict)+buffer;
 return {approved:stressed<=capacity,reason:stressed<=capacity?'Payment fits observed surplus and reserves':'Stressed payment exceeds income surplus and usable reserves',scheduled,stressed,capacity,recurring,essential};
}
function updateCreditObservations(){
 for(const h of G.households){if(!h.people.length)continue;const income=Math.max(0,h.income-h.incomeTax),old=h.netIncomeTrend??income;h.netIncomeTrend=old*.95+income*.05;h.incomeVariance=(h.incomeVariance||0)*.95+(income-old)*(income-old)*.05;h.essentialDueTrend=(h.essentialDueTrend??h.essentialDue??0)*.95+(h.essentialDue||0)*.05;}
}
function completeEquipmentOrders(){for(const f of G.firms){const order=f.pendingEquipment;if(!order||G.day<order.ready)continue;f.scale=Math.min(2.2,(f.scale||1)+order.gain);f.equipmentCommissioned=(f.equipmentCommissioned||0)+order.cost;f.pendingEquipment=null;dirty=true;}}
function validateCreditState(data){
 for(const p of data.people){if(p.commuteBlocked!=null&&typeof p.commuteBlocked!=='boolean')return false;if(p.commuteBlockedDays!=null&&(!Number.isInteger(p.commuteBlockedDays)||p.commuteBlockedDays<0||p.commuteBlockedDays>30))return false;}
 for(const f of data.firms)if(f.attendingWorkers!=null&&(!Array.isArray(f.attendingWorkers)||new Set(f.attendingWorkers).size!==f.attendingWorkers.length||f.attendingWorkers.some(id=>!Number.isInteger(id)||!data.people[id])))return false;
 for(const owner of [...data.households,...data.firms])if(owner.creditDecision){const c=owner.creditDecision;if(typeof c.approved!=='boolean'||!Number.isInteger(c.day)||c.day<1||c.day>data.day||!Number.isFinite(c.requested)||c.requested<0||typeof c.reason!=='string'||c.reason.length>500)return false;for(const key of ['scheduled','stressed','capacity','recurring','essential'])if(c[key]!=null&&(!Number.isFinite(c[key])||c[key]<0))return false;}

 const fields=['netIncomeTrend','incomeVariance','essentialDueTrend','essentialDue','travelDue'];
 for(const h of data.households)for(const key of fields)if(h[key]!=null&&(!Number.isFinite(h[key])||h[key]<0))return false;
 for(const f of data.firms)if(f.pendingEquipment){const o=f.pendingEquipment;if(!Number.isFinite(o.cost)||o.cost<=0||!Number.isFinite(o.gain)||o.gain<=0||o.gain>1.2||!Number.isInteger(o.ordered)||o.ordered<1||o.ordered>data.day||o.ready!==o.ordered+30)return false;}
 for(const l of data.loans||[])for(const key of ['lastPaymentDay','defaultedDay'])if(l[key]!=null&&(!Number.isInteger(l[key])||l[key]<1||l[key]>data.day))return false;
 return true;
}
function creditDecisionReport(owner){
 const c=owner.creditDecision;if(!c)return tip('A new credit application will be assessed against observed income, essential costs, working capital and a stressed repayment. Low interest alone does not make an unaffordable loan viable.');
 return `<div class="credit-decision"><strong>Latest credit review · day ${fmt(c.day)} · ${c.approved?'APPROVED':'NOT APPROVED'}</strong><p class="desc">${esc(c.reason)}</p>${Number.isFinite(c.capacity)?strip('Stressed payment / day',money(c.stressed))+strip('Assessed payment capacity / day',money(c.capacity)):''}</div>`;
}
const creditEconomyBase=renderEconomy;
renderEconomy=function(){const active=G.loans.filter(l=>l.status==='active'),orders=G.firms.filter(f=>f.pendingEquipment);return head('Credit and investment pipeline')+strip('Active household / enterprise loans',active.filter(l=>l.ownerType==='household').length+' / '+active.filter(l=>l.ownerType==='firm').length)+strip('Loans with missed payments',active.filter(l=>l.arrears>0).length)+strip('Funded equipment orders',orders.length)+tip('Debt service reduces spendable household income. Banks price impaired portfolios and assess a rate-stressed repayment. Equipment is paid for at order and becomes productive after commissioning; credit cannot replace demand or missing inputs.')+creditEconomyBase();};
