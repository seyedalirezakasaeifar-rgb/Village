// Public service authorizations are explicit daily dollars, never percentages or
// automatic population multipliers. Planning reads state; only enactment applies it.
const SERVICE_BUDGET_KEYS={healthBudget:'health',educationBudget:'school'};
let serviceBudgetErrorTown=null,serviceBudgetInputErrors={};
function serviceBudgetMoney(value){const n=Number(value)||0;return '$'+n.toLocaleString('en-CA',{minimumFractionDigits:Math.abs(n-Math.round(n))>1e-8?2:0,maximumFractionDigits:2});}
function isServiceBudgetKey(key){return owns(SERVICE_BUDGET_KEYS,key);}
function parseServiceBudget(value){
 if(typeof value!=='number'&&(typeof value!=='string'||!/^\d+(?:\.\d+)?$/.test(value)))return {ok:false,reason:'Enter a daily dollar amount from $0 to $50,000.'};
 const amount=Number(value);if(!Number.isFinite(amount)||amount<0||amount>PUBLIC_SERVICE_BUDGET_LIMIT)return {ok:false,reason:'Enter a finite daily dollar amount from $0 to $50,000.'};
 return {ok:true,value:Math.round(amount*100)/100};
}
function validateServiceBudgetArchive(data){
 for(const key of Object.keys(SERVICE_BUDGET_KEYS)){if(!owns(data.policy,key))continue;const checked=parseServiceBudget(data.policy[key]);if(!checked.ok)return false;}
 return true;
}
function serviceBudgetErrors(){if(serviceBudgetErrorTown!==G){serviceBudgetErrorTown=G;serviceBudgetInputErrors={};}return serviceBudgetInputErrors;}
function prepareServiceBudgetEnactment(){
 if(Object.keys(serviceBudgetErrors()).length)return {ok:false,reason:'Correct the daily service amount before enacting the policy package.'};
 const values={};for(const key of Object.keys(SERVICE_BUDGET_KEYS))if(owns(draftPolicy,key)){const parsed=parseServiceBudget(draftPolicy[key]);if(!parsed.ok)return parsed;values[key]=parsed.value;}
 for(const [key,value] of Object.entries(values))draftPolicy[key]=value;return {ok:true};
}
function publicServiceBudgetEstimate(kind,policy=G?.policy||defaults){
 const standard=CIVIC_STANDARDS[kind],population=G?G.people.reduce((n,p)=>n+Number(!p.deceased&&!p.movedAway),0):0,wage=Math.max(24,Number(policy.minWage)||24),full=population*standard.staff/standard.capacity*wage/.65;
 const access=G?serviceAccess(kind):{coverage:0,served:0,households:[]},facilities=G?G.buildings.filter(b=>b.kind===standard.building&&isPublicFacility(b)).length:0,provision=G?.serviceProvision?.[kind],publicCoverage=provision?.coverage||0;
 let privateCoverage=0;if(kind==='school'&&G?.privateServiceProvision?.school)for(const h of G.households)privateCoverage+=(G.privateServiceProvision.school[h.id]||0)*h.people.length/Math.max(1,population);
 privateCoverage=clamp(privateCoverage,0,1);const reachable=full*clamp(access.coverage||0,0,1),combinedGap=full*Math.min(clamp(access.coverage||0,0,1),Math.max(0,1-privateCoverage));
 return {kind,population,wage,full,reachable,combinedGap,facilities,observed:!!provision,access:clamp(access.coverage||0,0,1),publicCoverage,privateCoverage,combinedCoverage:clamp(publicCoverage+privateCoverage,0,1),staffing:provision?.staffing||null,pendingDay:G?.civicStaffing?.[kind]?.pending?.day||null};
}
function serviceBudgetRange(key,policy={...(G?.policy||defaults),...draftPolicy}){
 const estimate=publicServiceBudgetEstimate(SERVICE_BUDGET_KEYS[key],policy),current=Number(G?.policy?.[key])||0,proposed=Number(policy[key])||0;
 const desired=Math.max(500,estimate.full*1.25,current,proposed),quantum=desired<=1000?100:desired<=10000?250:1000;
 return {min:0,max:Math.min(PUBLIC_SERVICE_BUDGET_LIMIT,Math.ceil(desired/quantum)*quantum),step:.01,hardMax:PUBLIC_SERVICE_BUDGET_LIMIT};
}
function serviceBudgetOutlook(policy={...(G?.policy||defaults),...draftPolicy}){
 const keys=['policeBudget','defenseBudget','healthBudget','educationBudget','aidBudget','energyAidBudget','outreachBudget','roadBudget','transitBudget','militiaBudget','serviceVoucherBudget'];
 let ceiling=keys.reduce((n,k)=>n+(Number(policy[k])||0),0);
 ceiling+=(G?.stats.employed||0)*(Number(policy.employmentSubsidy)||0);
 ceiling+=(G?G.people.filter(p=>!p.deceased&&!p.movedAway&&p.age>70).length:0)*(Number(policy.pensionDaily)||0);
 ceiling+=(G?.debt||0)*((Number(policy.policyRate)||0)/100+.015)/360;
 ceiling+=G?.regionalTrade?.reliefUntil>=G?.day?108:0;
 ceiling+=G?G.buildings.filter(b=>b.municipalRehousing&&b.kind==='home').length:0;
 if(G?.transit?.routes.length){
  const drivers=G.transit.routes.reduce((n,r)=>n+(TRANSIT_LEVELS[r.level]?.vehicles||0)*(TRANSIT_MODES[r.mode]?.staff||0),0);
  ceiling+=transitOperatingCommitment()+drivers*(Math.max(24,policy.minWage)-Math.max(24,G.policy.minWage))-(Number(policy.transitBudget)||0);
 }
 const estimates={health:publicServiceBudgetEstimate('health',policy),school:publicServiceBudgetEstimate('school',policy)};
 const currentNeed=ceiling-(Number(policy.healthBudget)||0)-(Number(policy.educationBudget)||0)+Math.min(Number(policy.healthBudget)||0,estimates.health.reachable)+Math.min(Number(policy.educationBudget)||0,estimates.school.reachable);
 const taxes=['incomeTax','profitTax','propertyTax','foodTax','utilityTax','commercialRate','tariffs','permits','housingRents'];
 const receipts=taxes.reduce((n,k)=>n+(Number.isFinite(G?.cumulative?.[k])?G.cumulative[k]:0),0)+(G?.transit?.fares||0),dailyReceipts=receipts/Math.max(1,(G?.day||1)-1),cash=Math.max(0,G?.treasury||0),deficit=currentNeed-dailyReceipts;
 return {ceiling,currentNeed,dailyReceipts,cash,deficit,runway:deficit>0?cash/deficit:null,estimates};
}
function serviceBudgetRecommendation(key,policy={...(G?.policy||defaults),...draftPolicy}){
 const outlook=serviceBudgetOutlook(policy),estimate=outlook.estimates[SERVICE_BUDGET_KEYS[key]],other=outlook.currentNeed-Math.min(Number(policy[key])||0,estimate.reachable),cashEnvelope=Math.max(0,outlook.dailyReceipts+outlook.cash/30-other);
 return {amount:Math.max(0,Math.min(PUBLIC_SERVICE_BUDGET_LIMIT,Math.floor(Math.min(estimate.reachable,cashEnvelope)))),cashEnvelope,estimate,outlook};
}
