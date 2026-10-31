// --- Founder's Edition: long-form borough strategy systems and reporting. ---
const AMBITIONS=[
 {id:'resilient_banks',title:'A resilient banking centre',description:'Keep three solvent banks operating, fewer than two business loan defaults, and 75% employment for 50 days.',days:50,goal:g=>g.banks?.filter(b=>!b.closed&&bankEquity(b)>0).length>=3&&g.finance.businessDefaults<2&&g.stats.employment>=75,progress:g=>Math.min(1,(g.banks?.filter(b=>!b.closed).length||0)/3*.6+g.stats.employment/75*.4),reward:6500},
 {id:'balanced',title:'Keep the books',description:'Maintain $60,000 in municipal cash, no debt, and 65% employment for 25 days.',days:25,goal:g=>g.treasury>=60000&&g.debt===0&&g.stats.employment>=65,progress:g=>Math.min(1,(g.treasury/60000)*.65+(g.stats.employment/65)*.35),reward:3500},
 {id:'safe',title:'A safe place to live',description:'Maintain a safety index of 88, with no more than two crimes in 30 days, for 20 days.',days:20,goal:g=>g.stats.safety>=88&&g.stats.dailyCrime<=2,progress:g=>Math.min(1,g.stats.safety/88),reward:3200},
 {id:'market',title:'A thriving market town',description:'Support at least 25 trading businesses and employment above 80% for 25 days.',days:25,goal:g=>g.stats.businesses>=25&&g.stats.employment>=80,progress:g=>Math.min(1,g.stats.businesses/25),reward:5000},
 {id:'families',title:'A town for families',description:'Reduce household hardship under 9% while retaining at least 70 homes for 20 days.',days:20,goal:g=>g.stats.hardship<=9&&g.homes.length>=70,progress:g=>Math.min(1,.5*(1-g.stats.hardship/100)+.5*g.homes.length/70),reward:4800},
 {id:'education',title:'A learned community',description:'Raise schooling to 70 and public health to 80, then sustain both for 20 days.',days:20,goal:g=>g.education>=70&&g.health>=80,progress:g=>Math.min(1,(g.education/70+g.health/80)/2),reward:4200},
 {id:'liberty',title:'A leaner tax regime',description:'Maintain income tax at 5% or less, employment at 75%+, and a $25,000 reserve for 25 days.',days:25,goal:g=>g.policy.incomeTax<=5&&g.stats.employment>=75&&g.treasury>=25000,progress:g=>Math.min(1,.5*g.stats.employment/75+.5*g.treasury/25000),reward:4000},
 {id:'resilience',title:'Ready for hard times',description:'Raise emergency readiness to 80+, fund a second fire brigade, and sustain it 20 days.',days:20,goal:g=>g.stats.preparedness>=80&&g.buildings.filter(b=>b.kind==='fire').length>=2,progress:g=>Math.min(1,g.stats.preparedness/80),reward:4000},
 {id:'boom',title:'An ambitious borough',description:'Bring 300 residents into the town without losing employment below 70% for 25 days.',days:25,goal:g=>g.people.length>=300&&g.stats.employment>=70,progress:g=>Math.min(1,g.people.length/300),reward:6500},
 {id:'reputation',title:'An enduring mandate',description:'Earn 78% council approval, with a safety index of 75, for 30 days.',days:30,goal:g=>g.council.approval>=78&&g.stats.safety>=75,progress:g=>Math.min(1,g.council.approval/78),reward:5000}
];
const COUNCIL_EVENTS=[
 {title:'A petition from the shopkeepers',type:'COMMERCE & TRADE',text:'Local merchants say rising delivery expenses are eating their margins. They ask for temporary help, while residents want prices kept down.',choices:[
  {title:'Finance a local delivery cooperative',desc:'Pay $2,200. Deliver working capital to nearby firms.',cost:2200,apply:()=>{let list=G.firms.filter(f=>!f.closed);let n=Math.min(8,list.length);for(let f of list.slice(0,n))f.cash+=2200/n;G.council.factions.merchants+=4;}},
  {title:'Simplify commercial licences',desc:'Reduce the permit fee by $200; sacrifice possible permit revenue.',apply:()=>{G.policy.permitFee=Math.max(0,G.policy.permitFee-200);G.council.factions.merchants+=3}},
  {title:'Leave prices and freight to the market',desc:'No expenditure. Merchants remain responsible for their costs.',apply:()=>{G.council.factions.merchants-=2}}
 ]},
 {title:'The bridge needs repairs',type:'PUBLIC WORKS',text:'The stone bridge carrying traffic to the northern quarter has begun to crack. Engineers advise action before winter.',choices:[
  {title:'Repair it properly',desc:'Pay $3,000. Better trade access and road reliability.',cost:3000,apply:()=>{G.policy.roadBudget=Math.min(250,G.policy.roadBudget+10);G.council.factions.public+=3}},
  {title:'Authorize urgent patchwork',desc:'Pay $900. A partial, temporary improvement.',cost:900,apply:()=>{G.council.factions.public+=1}},
  {title:'Postpone repairs',desc:'No cost now. Residents question council priorities.',apply:()=>{G.council.factions.public-=5;G.unrest+=2}}
 ]},
 {title:'Families facing eviction',type:'HOUSING & WELFARE',text:'A local charity reports several working households have fallen behind on rent. It asks the council to contribute to an emergency relief fund.',choices:[
  {title:'Fund a relief programme',desc:'Transfer $2,400 directly to the poorest households.',cost:2400,apply:()=>{let h=G.households.slice().sort((a,b)=>a.cash-b.cash).slice(0,12);for(let p of h){p.cash+=200;p.stress=Math.max(0,p.stress-5);}G.council.factions.workers+=4}},
  {title:'Make relief conditional on training',desc:'Spend $1,300 on work placement and training.',cost:1300,apply:()=>{G.education+=2;G.council.factions.workers+=2}},
  {title:'Refer households to private charity',desc:'No budget impact. Increased dissatisfaction among poorer households.',apply:()=>{G.council.factions.workers-=4}}
 ]},
 {title:'A merchant wants to expand',type:'PRIVATE INVESTMENT',text:'A local trader has identified a vacant premises. They can open another shop if planning permission and capital are secured.',choices:[
  {title:'Offer a development grant',desc:'Pay $2,000 in startup capital and promote private entry.',cost:2000,apply:()=>{let f=G.firms.filter(f=>f.closed)[0];if(f){f.closed=false;f.cash+=5500;f.strain=0;assignJobs();}else{let f=pick(G.firms);if(f)f.cash+=2000;}G.council.factions.merchants+=3}},
  {title:'Waive the entry fee for a year',desc:'Reduce new-entry permit charges to $0.',apply:()=>{G.policy.permitFee=0;G.council.factions.merchants+=3}},
  {title:'Decline special favours',desc:'The standard planning and licensing system remains in force.',apply:()=>{G.council.factions.merchants-=1}}
 ]},
 {title:'Illness spreads at the school',type:'PUBLIC HEALTH',text:'A seasonal respiratory illness is circulating. The clinic says it can reduce disruption if a temporary programme is funded.',choices:[
  {title:'Provide treatment and preventive supplies',desc:'Spend $1,800. Improves town health and reduces household stress.',cost:1800,apply:()=>{G.health=Math.min(100,G.health+5);for(const h of G.households)h.stress=Math.max(0,h.stress-.6)}},
  {title:'Ask employers to adopt voluntary precautions',desc:'No direct cost. Modest public health gains.',apply:()=>{G.health=Math.min(100,G.health+1)}},
  {title:'Take no action',desc:'The illness is allowed to run its course.',apply:()=>{G.health=Math.max(20,G.health-3);G.council.factions.public-=2}}
 ]},
 {title:'The industrial safety dispute',type:'WORKING CONDITIONS',text:'Workers at the sawmill say basic precautions have been neglected. Employers warn that more inspection rules will raise costs.',choices:[
  {title:'Increase workplace inspections',desc:'Raise business regulation by 15 points.',apply:()=>{G.policy.businessRegulation=Math.min(100,G.policy.businessRegulation+15);G.council.factions.workers+=3;G.council.factions.merchants-=2}},
  {title:'Co-finance safety improvements',desc:'Spend $1,500 on protective equipment for firms.',cost:1500,apply:()=>{G.health+=2;G.council.factions.workers+=2;G.council.factions.merchants+=2}},
  {title:'Leave the matter to individual employers',desc:'No spending or new regulatory obligations.',apply:()=>{G.council.factions.workers-=3;G.council.factions.merchants+=2}}
 ]},
 {title:'A dry summer threatens the farms',type:'AGRICULTURE',text:'Farmers report that irrigation ditches are running low. Crop yields and exports may decline unless the borough acts.',choices:[
  {title:'Build emergency irrigation channels',desc:'Spend $2,800; support farm production capacity.',cost:2800,apply:()=>{G.firms.filter(f=>f.kind==='farm'&&!f.closed).forEach(f=>{f.stock.grain+=80;f.cash+=150;});G.council.factions.merchants+=2}},
  {title:'Provide a small farmer loan',desc:'Advance $1,000 to local farms.',cost:1000,apply:()=>{G.firms.filter(f=>f.kind==='farm'&&!f.closed).slice(0,5).forEach(f=>f.cash+=200)}},
  {title:'Allow farms to adapt privately',desc:'No expense, but traders face reduced near-term output.',apply:()=>{G.firms.filter(f=>f.kind==='farm'&&!f.closed).forEach(f=>f.stock.grain=Math.max(0,f.stock.grain-50))}}
 ]},
 {title:'The night watch requests support',type:'CRIME & SECURITY',text:'The constabulary reports a rise in burglary attempts in outlying lanes. Officers request more staff and lighting.',choices:[
  {title:'Raise daily patrol funding',desc:'Increase constabulary expenditure by $40 per day.',apply:()=>{G.policy.policeBudget=Math.min(800,G.policy.policeBudget+40);G.council.factions.public+=2}},
  {title:'Fund a one-time neighbourhood programme',desc:'Spend $1,300; support vulnerable households.',cost:1300,apply:()=>{G.households.filter(h=>h.security<65).forEach(h=>h.security+=8);G.council.factions.public+=2}},
  {title:'Maintain the existing patrols',desc:'No new expense.',apply:()=>{G.council.factions.public-=1}}
 ]},
 {title:'A new regional trade agreement',type:'COMMERCE & TRADE',text:'Regional merchants offer stable supplies of grain and timber. In return, they request lower import charges.',choices:[
  {title:'Sign a free-trade agreement',desc:'Remove import tariffs and allow unrestricted regional trade.',apply:()=>{G.policy.importTariff=0;G.policy.imports=true;G.council.factions.merchants+=4}},
  {title:'Negotiate a lower tariff',desc:'Cut the current tariff rate in half.',apply:()=>{G.policy.importTariff=Math.floor(G.policy.importTariff/2);G.council.factions.merchants+=2}},
  {title:'Keep the present trading arrangements',desc:'No immediate policy change.',apply:()=>{}}
 ]},
 {title:'Flooding on the low road',type:'CIVIL DEFENCE',text:'Heavy rain has washed out culverts on the east side. Some properties face water damage if repairs are delayed.',choices:[
  {title:'Mobilize the fire brigade and volunteers',desc:'Spend $2,700. Protect homes and restore access.',cost:2700,apply:()=>{G.crisesHandled++;G.council.factions.public+=3}},
  {title:'Organize local volunteer crews',desc:'Spend $650. Partial protection.',cost:650,apply:()=>{G.crisesHandled++;G.health=Math.max(0,G.health-1)}},
  {title:'Leave residents to arrange private repairs',desc:'No municipal expense; some households suffer damage.',apply:()=>{G.households.slice(0,8).forEach(h=>{let p=Math.min(h.cash,170);h.cash-=p;G.region+=p;h.stress+=3;});G.council.factions.public-=3}}
 ]},
 {title:'The apprentices ask for a school',type:'EDUCATION & EMPLOYMENT',text:'Young workers say the town needs formal training if local firms are to compete with regional employers.',choices:[
  {title:'Establish an apprenticeship fund',desc:'Spend $1,600, increasing vocational skill.',cost:1600,apply:()=>{G.education=Math.min(100,G.education+5);G.council.factions.workers+=3}},
  {title:'Ask businesses to organize training',desc:'No municipal expenditure. Small productivity improvement.',apply:()=>{G.education=Math.min(100,G.education+1);G.council.factions.merchants+=2}},
  {title:'Maintain current schooling',desc:'No change.',apply:()=>{G.council.factions.workers-=1}}
 ]},
 {title:'Council must address the deficit',type:'THE PUBLIC PURSE',text:'The treasurer warns that current services may become unaffordable if reserves continue to decline.',choices:[
  {title:'Reduce non-essential daily programmes',desc:'Cut administrative, outreach and road spending.',apply:()=>{G.policy.outreachBudget=Math.max(0,G.policy.outreachBudget-20);G.policy.roadBudget=Math.max(0,G.policy.roadBudget-10);G.policy.educationBudget=Math.max(0,G.policy.educationBudget-20);G.council.factions.public-=3}},
  {title:'Increase the income-tax rate',desc:'Raise income tax by 3 percentage points.',apply:()=>{G.policy.incomeTax=Math.min(40,G.policy.incomeTax+3);G.council.factions.workers-=3}},
  {title:'Raise an emergency municipal loan',desc:'Borrow $7,000 with interest due.',apply:()=>{G.debt+=7000;G.treasury+=7000;G.region-=7000}}
 ]}
];
// Additional town stories: each decision affects actual funds, people, local firms or policy rules.
COUNCIL_EVENTS.push(
 {title:'The bakers face a flour shortage',type:'FOOD SUPPLY',text:'The local bakery guild cannot obtain sufficient flour at current prices. Families are already paying more for basic bread.',choices:[
  {title:'Buy emergency supplies',desc:'Pay $1,800 to restock bakeries and reduce immediate shortages.',cost:1800,apply:()=>{G.firms.filter(f=>f.kind==='bakery'&&!f.closed).slice(0,4).forEach(f=>{f.stock.flour=(f.stock.flour||0)+120;f.cash+=150;});G.council.factions.workers+=2}},
  {title:'Ease grain import duties',desc:'Remove import tariffs to lower suppliers’ input costs.',apply:()=>{G.policy.importTariff=0;G.policy.imports=true;G.council.factions.merchants+=2}},
  {title:'Keep the market free of intervention',desc:'No public expense; food prices may remain elevated.',apply:()=>{G.council.factions.workers-=2}}
 ]},
 {title:'Petition for fair wages',type:'WORK & INCOME',text:'A group of poorly paid employees wants the council to mandate higher wages. Shopkeepers say their margins are already thin.',choices:[
  {title:'Raise the daily wage floor by $5',desc:'Employers must meet a higher payroll; workers may gain more income.',apply:()=>{G.policy.minWage=Math.min(90,G.policy.minWage+5);G.council.factions.workers+=3;G.council.factions.merchants-=2}},
  {title:'Subsidize employment instead',desc:'Pay employers an extra $2 per working resident each day.',apply:()=>{G.policy.employmentSubsidy=Math.min(15,G.policy.employmentSubsidy+2);G.council.factions.merchants+=2;G.council.factions.workers+=2}},
  {title:'Keep wages privately negotiated',desc:'Make no new employment rule.',apply:()=>{G.council.factions.workers-=2}}
 ]},
 {title:'The housing shortage petition',type:'HOUSING & PLANNING',text:'Young households say they cannot find affordable houses near the square. Established property owners oppose building on the village outskirts.',choices:[
  {title:'Open new residential land',desc:'Reduce zoning restrictions by 20 points to allow private housebuilding.',apply:()=>{G.policy.zoningRestriction=Math.max(0,G.policy.zoningRestriction-20);G.council.factions.homeowners-=2;G.council.factions.workers+=3}},
  {title:'Finance new municipal cottages',desc:'Pay $3,000 into a housing programme for families in hardship.',cost:3000,apply:()=>{G.households.slice().sort((a,b)=>a.cash-b.cash).slice(0,10).forEach(h=>{h.cash+=300;h.stress=clamp(h.stress-5,0,100)});G.council.factions.workers+=3}},
  {title:'Preserve the current neighbourhood plans',desc:'Leave building restrictions in place.',apply:()=>{G.council.factions.homeowners+=2;G.council.factions.workers-=2}}
 ]},
 {title:'A theft at the market square',type:'LAW & ORDER',text:'Several stallholders report stolen cash, and residents accuse the watch of ignoring repeated warnings.',choices:[
  {title:'Fund a targeted investigation',desc:'Spend $1,400 on detectives and restitution for the affected traders.',cost:1400,apply:()=>{G.firms.filter(f=>!f.closed).slice(0,7).forEach(f=>f.cash+=200);G.council.factions.public+=3}},
  {title:'Build a stronger night watch',desc:'Raise ongoing police funding by $30 per day.',apply:()=>{G.policy.policeBudget=Math.min(800,G.policy.policeBudget+30);G.council.factions.public+=2}},
  {title:'Ask stallholders to hire their own guards',desc:'No public expense; private traders bear the burden.',apply:()=>{G.council.factions.merchants-=2}}
 ]},
 {title:'Refugees from the flooded valley',type:'MIGRATION & COMMUNITY',text:'Families displaced by a flood in a neighbouring district are asking to settle in the town. The school and grocers expect extra demand.',choices:[
  {title:'Open a municipal resettlement fund',desc:'Spend $2,000 supporting the lowest-cash families and social integration.',cost:2000,apply:()=>{G.households.slice().sort((a,b)=>a.cash-b.cash).slice(0,10).forEach(h=>{h.cash+=200;h.stress=clamp(h.stress-2,0,100)});G.council.factions.public+=3}},
  {title:'Allow private sponsors to assist arrivals',desc:'No municipal funding; remove some housing restrictions.',apply:()=>{G.policy.zoningRestriction=Math.max(0,G.policy.zoningRestriction-10);G.council.factions.merchants+=2}},
  {title:'Defer new settlement until homes are built',desc:'No immediate housing pressure or public spending.',apply:()=>{G.council.factions.public-=2}}
 ]},
 {title:'An old mine could reopen',type:'JOBS & NATURAL RESOURCES',text:'A regional operator wants to restart an abandoned quarry. It could create jobs, but nearby residents worry about dust and road wear.',choices:[
  {title:'Offer a conditional investment grant',desc:'Pay $1,600 to boost the quarry’s capital and maintain safety standards.',cost:1600,apply:()=>{const f=G.firms.find(f=>f.kind==='quarry');if(f){f.cash+=1600;f.strain=Math.max(0,f.strain-10);if(f.closed){f.closed=false;assignJobs()}}G.council.factions.merchants+=2}},
  {title:'Permit reopening under stricter safeguards',desc:'Raise inspection standards by 10 points.',apply:()=>{G.policy.businessRegulation=Math.min(100,G.policy.businessRegulation+10);G.council.factions.homeowners+=3}},
  {title:'Do not subsidize a private enterprise',desc:'No public expenditure or special permission.',apply:()=>{G.council.factions.merchants-=1}}
 ]},
 {title:'The volunteer brigade wants equipment',type:'CIVIL DEFENCE',text:'The local volunteer corps warns that the next major storm could overwhelm the existing fire brigade.',choices:[
  {title:'Buy new equipment',desc:'Spend $2,100 on storm preparedness and local protective supplies.',cost:2100,apply:()=>{G.policy.defenseBudget=Math.min(800,G.policy.defenseBudget+20);G.crisesHandled++;G.council.factions.public+=3}},
  {title:'Expand volunteer training',desc:'Increase volunteer funding by $35 per day.',apply:()=>{G.policy.militiaBudget=Math.min(400,G.policy.militiaBudget+35);G.council.factions.public+=2}},
  {title:'Rely on mutual aid from neighbouring towns',desc:'No extra town spending; coverage remains uncertain.',apply:()=>{G.council.factions.public-=2}}
 ]},
 {title:'The grocers dispute inspection fees',type:'SMALL BUSINESS',text:'Several family-owned shops are paying more for paperwork and inspections than expected. Residents also want food safety enforced.',choices:[
  {title:'Simplify the inspection rules',desc:'Lower business regulation by 15 points, reducing operating compliance costs.',apply:()=>{G.policy.businessRegulation=Math.max(0,G.policy.businessRegulation-15);G.council.factions.merchants+=4}},
  {title:'Help small shops modernize',desc:'Spend $1,800 on better storage equipment and food safety.',cost:1800,apply:()=>{G.firms.filter(f=>f.kind==='grocer'&&!f.closed).slice(0,6).forEach(f=>{f.cash+=300;f.stock.food=(f.stock.food||0)+20});G.council.factions.public+=2}},
  {title:'Keep current safeguards and fees',desc:'No change to local regulatory standards.',apply:()=>{G.council.factions.public+=1;G.council.factions.merchants-=2}}
 ]}
);


function setupScenario(){
 if(chosenScenario==='hardtimes'){
   G.region+=G.treasury-16000;G.treasury=16000;G.debt=9000;G.treasury+=9000;G.region-=9000;for(const f of G.firms.filter(f=>f.kind==='farm'||f.kind==='sawmill')){let old=f.cash;f.cash*=.22;G.region+=old-f.cash;f.strain=34;}for(const h of G.households.slice(0,26)){let old=h.cash;h.cash*=.15;G.region+=old-h.cash;h.stress+=25}G.policy.incomeTax=19;G.policy.profitTax=26;G.policy.zoningRestriction=55;G.regionalDemand=.55;G.council.approval=41;G.council.factions.workers=39;G.scenario='hardtimes';story('The borough faces layoffs, debt and a strained treasury.','bad');
 }else if(chosenScenario==='frontier'){
   G.region+=G.treasury-43000;G.treasury=43000;G.policy.incomeTax=6;G.policy.profitTax=7;G.policy.policeBudget=90;G.policy.defenseBudget=60;G.policy.educationBudget=40;G.policy.healthBudget=35;G.policy.aidBudget=40;G.scenario='frontier';
   for(const f of G.firms.slice(10)){f.closed=true;for(let id of f.workers)if(G.people[id])G.people[id].job=-1;f.workers=[];}G.council.approval=69;story('A small frontier council inherits open land and a lean budget.','neutral');
 }else if(chosenScenario==='industrial'){
   G.region+=G.treasury-68000;G.treasury=68000;G.policy.profitTax=5;G.policy.incomeTax=15;G.policy.permitFee=0;G.policy.businessRegulation=40;G.policy.minWage=34;G.policy.educationBudget=130;G.scenario='industrial';
   for(const f of G.firms){f.cash+=2500;G.region-=2500}G.council.approval=58;story('Industrial investment is rising, but employers and workers disagree over wages and regulation.','neutral');
 }else{G.scenario='settlement';story('The council inherits a promising community and a difficult balancing act.','good');}
 recompute();
}
function fundLocalService(amount){return fundedPublicPayroll(amount);}
function fundCivicServices(){const P=G.policy;
 const healthRatio=purchaseCivicService('health',P.healthBudget||0),schoolRatio=purchaseCivicService('school',P.educationBudget||0),roadRatio=fundLocalService(P.roadBudget||0),militiaRatio=fundLocalService(P.militiaBudget||0),transitRatio=G.actualServiceFunding?.transit||0;
 G.actualServiceFunding=Object.assign(G.actualServiceFunding||{},{roads:roadRatio,health:healthRatio,school:schoolRatio,militia:militiaRatio,transit:transitRatio});
}
function extendedCivicDay(){
 let P=G.policy;
 let clinic=G.buildings.filter(b=>b.kind==='clinic').length,parks=G.buildings.filter(b=>b.kind==='park'||b.kind==='square').length,schools=G.buildings.filter(b=>b.kind==='school').length,watch=G.buildings.filter(b=>b.kind==='watchtower').length;
 const healthRatio=G.actualServiceFunding?.health||0,schoolRatio=G.actualServiceFunding?.school||0,roadRatio=G.actualServiceFunding?.roads||0,militiaRatio=G.actualServiceFunding?.militia||0,transitRatio=G.actualServiceFunding?.transit||0;
 G.health=clamp(G.health+(.063*healthRatio-.037- (G.stats.hardship||0)*.0002),25,99);
 G.education=clamp(G.education+.048*schoolRatio-.009,15,99);
 civicTrainingDay(schoolRatio);
 G.stats.health=Math.round(G.health);G.stats.education=Math.round(G.education);
 if(G.day%3===0&&schoolRatio>0){let p=pick(G.people.filter(p=>!p.deceased&&p.movedAway!==true));if(p){p.skill=clamp(p.skill+.018*localCivicCoverage('school',p.hh),0,1.3)}}
 if(G.day%6===0){let p=pick(G.people.filter(p=>!p.deceased&&p.movedAway!==true));if(p){p.health=clamp(p.health+(-.3+1.6*localCivicCoverage('health',p.hh))+rn(-.5,.5),10,100);if(p.health<25){const h=G.households[p.hh];if(h)h.stress=clamp(h.stress+1,0,100)}}}
 if(G.day%8===0&&parks>0){let h=pick(G.households);if(h)h.stress=clamp(h.stress-1.5,0,100)}
 const warmth=G.weather==='storm'?-.4:0;
 G.stats.wellbeing=Math.round(clamp(82-G.households.reduce((s,h)=>s+h.stress,0)/Math.max(1,G.households.length)*.46+parks*.5+G.health*.08+warmth,0,100));
 G.stats.avgCash=G.stats.cash/Math.max(1,G.households.length);
 G.stats.compliance=P.businessRegulation;
 G.stats.marketConfidence=Math.round(clamp(77-G.stats.unemployment*.5-G.stats.hardship*.48-P.profitTax*.23-P.permitFee*.005+Math.max(0,15-P.importTariff)*.12+parks*.3+(G.regionalDemand-1)*20,5,99));
 G.stats.propertyCosts=(2.15+P.zoningRestriction*.035);
 G.stats.realWages=Math.round(G.households.reduce((s,h)=>s+h.income-h.tax-h.rent-h.food,0)/Math.max(1,G.stats.population)*10)/10;
 G.stats.prosperity=Math.round(clamp(G.stats.employment*.5+G.stats.marketConfidence*.3+G.stats.wellbeing*.2,0,100));
 G.stats.roadService=Math.round(clamp((G.stats.roadCondition??75)*.65+clamp((P.roadBudget||0)*roadRatio/Math.max(1,(graph().neighbors.size-(G.privateRoads||[]).length)*.045/.23),0,1)*23+clamp((P.transitBudget||0)*transitRatio/280,0,1)*12,0,100));
 G.stats.militia=Math.round(clamp(25+militiaRatio*(P.militiaBudget||0)/30+watch*12,0,100));
}
function updateCouncilAndMissions(){
 const C=G.council,P=G.policy,s=G.stats;
 if(G.day%4===0){
  const worker=clamp(20+s.employment*.45-s.hardship*.75+Math.min(P.aidBudget,250)*.024-P.foodTax*.60-P.incomeTax*.30+s.wellbeing*.06,5,98);
  const merchant=clamp(36+s.marketConfidence*.22+s.employment*.20-P.profitTax*.40-P.businessRegulation*.12-P.permitFee*.008,5,98);
  const homeowner=clamp(38+s.safety*.30+s.employment*.10-P.propertyTax*6-P.zoningRestriction*.12+Math.min(16,s.wellbeing*.08),5,98);
  const publicv=clamp(17+s.safety*.40+s.wellbeing*.30+s.health*.1-Math.min(25,Math.max(0,G.debt-G.treasury)/4500),5,98);
  for(const [k,v] of Object.entries({workers:worker,merchants:merchant,homeowners:homeowner,public:publicv}))C.factions[k]=clamp(C.factions[k]*.88+v*.12,0,100);
  const avg=.31*C.factions.workers+.25*C.factions.merchants+.2*C.factions.homeowners+.24*C.factions.public;
  C.approval=clamp(C.approval*.85+avg*.15,5,97);
 }
 G.stats.approval=Math.round(C.approval);
 for(const m of AMBITIONS){if(G.achievements.includes(m.id))continue;let n=G.ambitionDays[m.id]||0;G.ambitionDays[m.id]=m.goal(G)?n+1:0;
  if(G.ambitionDays[m.id]>=m.days){G.achievements.push(m.id);let bonus=Math.min(m.reward,G.region*.5);G.treasury+=bonus;G.region-=bonus;G.council.approval=clamp(G.council.approval+3,0,100);story('AMBITION ACHIEVED: '+m.title+'. Regional development grant '+money(bonus)+'.','good');if(speed<=8)toast('Ambition complete: '+m.title+'!');save();}}
}
function privateInvestmentAndHousing(){assignJobs();}
function monthlyReview(){
 // External demand periodically contracts. Recovery is gradual; policy affects resilience through firm cash, taxes and trade.
 G.regionalDemand=clamp((G.regionalDemand||1)*.90+0.10+rn(-.035,.035),.42,1.22);
 if(G.day%180===0&&random()<.33){G.regionalDemand=clamp(G.regionalDemand-rn(.17,.34),.42,1.22);story('Regional buyers cut orders. Local mills, farms and shops brace for a trade slowdown.','bad');}
 const seasonal=G.month>=10||G.month<=2?['clear','clear','rain','storm']:G.month>=6&&G.month<=8?['clear','clear','clear','drought','rain']:['clear','clear','rain','rain','storm'];
 G.weather=weatherEnabled()?pick(seasonal):'clear';refreshAmbience();if(G.weather==='storm')story('Heavy rain and high winds are expected; fire and civil defence are on alert.','neutral');if(G.weather==='drought')story('A dry spell threatens harvest yields and local food output.','bad');
 if(random()<.22*(1-G.stats.militia/115)){let f=pick(G.firms.filter(f=>!f.closed&&f.cash>100));if(f){let stolen=Math.min(f.cash,rn(100,650));f.cash-=stolen;f.theft+=stolen;G.region+=stolen;G.council.factions.public=clamp(G.council.factions.public-2,0,100);story('A bandit raid targeted '+f.name+'; '+money(stolen)+' was stolen.','bad',f.building);}}
 let r={...G.stats,day:G.day,cash:G.treasury};G.lastMonth=r;
 if(G.treasury<5000){story('Treasurer warns: the council has less than $5,000 of uncommitted funds.','bad');}
 else if(G.stats.unemployment>30){story('Joblessness is above 30%; families are requesting employment assistance.','bad');}
 else if(G.stats.hardship<6&&G.stats.employment>75){story('The borough records a month of relatively steady work and low hardship.','good');}
 if(G.month===12)story('Year-end statements have been filed at the town hall.','neutral');
}
function electionReview(){
 G.council.elections++;let approved=G.council.approval>=50;const stamp='Year '+G.year+' election: '+(approved?'Council retains public confidence':'Council loses majority support')+' ('+Math.round(G.council.approval)+'% approval).';story(stamp,approved?'good':'bad');G.journal.push({day:G.day,name:'Municipal election',message:stamp,baseline:{...G.stats,treasury:G.treasury}});
 // Elections enter the permanent journal without interrupting unattended simulation.
 if(active==='agenda'||active==='journal')renderPanel(active);
}
function offerCouncilEvent(interrupt=false){
 // Ordinary correspondence belongs in the agenda, not in a blocking modal.
 // It is deliberately safe at 64×: the simulation never waits for a reply.
 let recent=G.recentCouncilEvents||[],pool=COUNCIL_EVENTS.filter(e=>!recent.includes(e.title));
 if(!pool.length)pool=COUNCIL_EVENTS;
 let event=pick(pool);G.recentCouncilEvents=recent.concat(event.title).slice(-6);G.lastEventDay=G.day;
 if(interrupt){showCustomEvent(event.type,event.title,event.text,event.choices);return;}
 G.councilInbox=Array.isArray(G.councilInbox)?G.councilInbox:[];
 G.councilInbox.unshift({title:event.title,day:G.day});
 G.councilInbox=G.councilInbox.slice(0,7);
 story('A council petition is waiting: '+event.title+'. Review it in the Agenda when convenient.','neutral');
}
function reviewCouncilInbox(index){
 const inbox=G.councilInbox||[],entry=inbox[index];if(!entry)return;
 const found=COUNCIL_EVENTS.find(e=>e.title===entry.title);
 if(!found)inbox.splice(index,1);
 if(found)showCustomEvent(found.type,found.title,found.text,found.choices);
 else story('An archived council petition is no longer actionable.','neutral');
 save();if(active==='agenda')renderPanel('agenda');
}

let councilOpener=null;
function closeCouncilDialog(defer=false){
 const event=pendingEvent;pendingEvent=null;$('eventDialog').style.display='none';
 if(defer&&event&&event.type!=='TOWN ARCHIVE'&&COUNCIL_EVENTS.some(e=>e.title===event.title)){G.councilInbox=G.councilInbox||[];if(!G.councilInbox.some(e=>e.title===event.title))G.councilInbox.unshift({title:event.title,day:G.day});}
 if(active==='agenda')renderPanel(active);save();
 const target=councilOpener?.isConnected?councilOpener:$('tabs').querySelector('[data-panel="agenda"]');target?.focus();councilOpener=null;
}
function directTransactionDialog(type){return ['REGIONAL EXCHANGE','REGIONAL ROADS','DISTRICT PLANNING','FIRST DELIVERY','TOWN DIRECTION','OBSERVED OUTCOMES'].includes(type)}
function showCustomEvent(type,title,text,choices){councilOpener=document.activeElement;pendingEvent={type,title,text,choices};
 $('eventEyebrow').textContent=type;$('eventTitle').textContent=title;$('eventText').textContent=text;
 $('eventChoices').innerHTML=choices.map((c,i)=>`<button data-event-choice="${i}" ${c.cost>0?'data-sound="coin"':''} ${c.cost&&G.treasury<c.cost?'disabled':''}><strong>${esc(c.title)}</strong><small>${esc(c.desc||'')}${c.cost?' · Cost: '+money(c.cost):''}</small></button>`).join('');
 if(type!=='TOWN ARCHIVE'&&COUNCIL_EVENTS.some(e=>e.title===title)){G.councilInbox=G.councilInbox||[];if(!G.councilInbox.some(e=>e.title===title))G.councilInbox.unshift({title,day:G.day});save();}
 $('eventDialog').style.display='flex';$('eventDefer').textContent=(type==='TOWN ARCHIVE'||type==='LAND PURCHASE'||directTransactionDialog(type))?'CANCEL':'DECIDE LATER';$('eventChoices').querySelector('button:not([disabled])')?.focus();
}
$('eventChoices').addEventListener('click',e=>{
 const b=e.target.closest('button[data-event-choice]');if(!b||!pendingEvent)return;
 const evt=pendingEvent,c=evt.choices[+b.dataset.eventChoice];if(!c)return;
 if(evt.type==='TOWN ARCHIVE'||evt.type==='LAND PURCHASE'){if(c.cost&&G.treasury<c.cost)return;closeCouncilDialog();c.apply();return;}
 if(directTransactionDialog(evt.type)){closeCouncilDialog();c.apply();recompute();updateHeader();save();dirty=true;return;}
 const goodsBefore=stockTotals();const fundsBefore=totalMoney();if(c.cost){if(G.treasury<c.cost)return;G.treasury-=c.cost;G.region+=c.cost;G.cumulative.spending+=c.cost;}
 try{c.apply()}catch(ex){console.error('Council decision',ex)}
 const goodsAfter=stockTotals();for(const k of Object.keys(goods)){const delta=goodsAfter[k]-goodsBefore[k];goodsEntry(k,delta>=0?'imports':'consumed',Math.abs(delta));}
 const regionalFunding=totalMoney()-fundsBefore;G.region-=regionalFunding;if(Math.abs(regionalFunding)>.001)book(regionalFunding>0?'Regional capital':'Council settlement',regionalFunding>0?'Council decision beneficiaries':'Regional capital',Math.abs(regionalFunding),'Explicit council programme settlement');
 G.journal.push({day:G.day,name:evt.title,message:c.title+'. '+(c.desc||''),baseline:{...G.stats,treasury:G.treasury}});
 story('COUNCIL DECISION: '+c.title+' — '+evt.title,'neutral');G.councilInbox=(G.councilInbox||[]).filter(e=>e.title!==evt.title);closeCouncilDialog();recompute();updateHeader();if(active)renderPanel(active);save();dirty=true;
});
function totalMoney(){return (G.projects||[]).reduce((n,p)=>n+(p.serviceEscrow||0),0)+G.treasury+G.region+(G.investors||[]).reduce((n,a)=>n+a.cash,0)+(G.metro?.cash||0)+(G.banks||[]).reduce((n,b)=>n+b.cash,0)+G.households.reduce((n,h)=>n+h.cash,0)+G.firms.reduce((n,f)=>n+f.cash,0)}
function investigateCases(){if(G.day%5!==0)return;const power=policePower();for(const item of G.cases.slice(0,30)){if(item.resolved||item.offender==null||item.loss<=0||G.day-item.day<3)continue;let age=G.day-item.day;if(age>50){item.resolved='cold';continue;}if(random()<(.025+power*.14)){let offender=G.households[item.offender];let victim=item.hid>=0?G.households[item.hid]:(G.firms[readBuild(item.bid)?.firm]);if(offender&&victim){let recovered=Math.min(offender.cash,item.loss*(.30+power*.45));if(recovered>0){offender.cash-=recovered;victim.cash+=recovered;if(item.hid<0){victim.revenue+=recovered;victim.nonSalesIncome=(victim.nonSalesIncome||0)+recovered;victim.recoveries=(victim.recoveries||0)+recovered;}else victim.recoveredLosses=(victim.recoveredLosses||0)+recovered;}item.recovered=Math.round(recovered);item.resolved=true;story('Constabulary concluded an investigation; '+money(recovered)+' was recovered for the victim.','good',item.bid,item.hid);}}}}
function yearlyDemographics(){
 let deaths=0;
 for(const p of G.people){
  if(p.deceased||p.movedAway)continue;p.age++;if(p.age>70&&p.job>=0){const f=G.firms[p.job];if(f)f.workers=f.workers.filter(id=>id!==p.id);p.job=-1;p.retired=true;p.publicWork=false;}
  if(p.age>85&&(p.age>95||random()<.17)){
   p.deceased=true;p.job=-1;
   const h=G.households[p.hh];if(h)h.people=h.people.filter(id=>id!==p.id);
   for(const f of G.firms)f.workers=f.workers.filter(id=>id!==p.id);
   deaths++;
  }
 }
 if(deaths)story(deaths+' elderly residents passed away this year. Their families will remember them.','neutral');
 // Vacant homes can receive a new household from outside town. Do not clone
 // an existing resident into two household rosters, and keep external cash balanced.
 for(const h of G.households){
  if(h.people.length||!readBuild(h.home)||G.stats.population>=2000||G.region<1000||cityDemand().housingPressure<48)continue;
  const building=readBuild(h.home),newHousehold=addHouseholdAt(building,900);
  if(newHousehold){if(building.hh===h.id)building.hh=newHousehold.id;if(Array.isArray(building.units))building.units=building.units.map(id=>id===h.id?newHousehold.id:id);h.home=-1;story('A newcomer household rented an empty home; the former estate retains its balances and title.','neutral',building.id,newHousehold.id);}

 }
 assignJobs();
}

function updateObjectiveMini(){if(!G)return;let m=AMBITIONS.find(m=>m.id===G.ambition)||AMBITIONS[0],days=G.ambitionDays[m.id]||0,p=m.progress(G);
 if(G.achievements.includes(m.id))p=1;else if(m.goal(G))p=Math.min(1,days/m.days);
 headerText('objectiveName',m.title);$('objectiveProgress').style.width=(100*clamp(p,0,1))+'%';
 const h=G.events[0];if(h){headerText('headline',h.text);}
 if(G.roadMetrics&&G.roadMetrics.connectedFirms<G.roadMetrics.totalFirms){headerText('headline','Road access warning: '+(G.roadMetrics.totalFirms-G.roadMetrics.connectedFirms)+' local businesses are cut off from town freight.');}
}

$('eventDefer').onclick=()=>closeCouncilDialog(true);
$('eventDialog').addEventListener('keydown',e=>{
 if(e.key!=='Tab')return;const controls=[...$('eventDialog').querySelectorAll('button:not([disabled])')];const first=controls[0],last=fromEnd(controls);
 if(e.shiftKey&&document.activeElement===first){last.focus();e.preventDefault();}else if(!e.shiftKey&&document.activeElement===last){first.focus();e.preventDefault();}
});
