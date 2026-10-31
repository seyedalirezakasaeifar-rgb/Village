'use strict';
// TownLedger: offline small-town economic policy laboratory. Separate Android WebView adaptation.
(function(){
// Negative indexing without requiring a recent Android WebView Array.at.
function fromEnd(values,offset=1){return values[values.length-offset];}
function owns(object,key){return Object.prototype.hasOwnProperty.call(object,key);}
const ART_DATA={};
const $=id=>document.getElementById(id), clamp=(x,a,b)=>Math.max(a,Math.min(b,x)),money=x=>(x<0?'−':'')+'$'+Math.round(Math.abs(x)).toLocaleString('en-CA');
const fmt=x=>Number(x||0).toLocaleString('en-CA',{maximumFractionDigits:1});
const esc=x=>String(x==null?'':x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const rn=(a,b)=>a+random()*(b-a),pick=a=>a[random()*a.length|0];
const first=['Arthur','Alice','Thomas','Eleanor','Henry','Margaret','Jack','Edith','Charles','Emily','George','Rose','William','Florence','James','Clara','Robert','Agnes','Daniel','Ivy','Samuel','Hannah','Oliver','Mabel','Edward','Beatrice','Frederick','Ada','Joseph','Grace','Peter','Julia','Benjamin','Isabel'];
const surnames=['Bennett','Parker','Sutton','Miller','Hughes','Clarke','Foster','Wright','Carter','Howard','Taylor','Moore','Campbell','Ward','Russell','Harris','Reed','Turner','Hill','Smith','Brooks','Davies','Morgan','Baker','Wilson','Grant'];
const T=128, TW=72, TH=36, RW=T*TW+140,RH=T*TH+120;
const types={
 bank:{n:'Bank Branch',cost:0,col:'#a3b0a6',jobs:0},
 worksite:{n:'Private Construction Site',cost:0,col:'#c0a076',jobs:0},
 apartment:{n:'Apartment House',cost:0,col:'#b7ab91',jobs:0},
 tower:{n:'High-rise Residences',cost:0,col:'#a0afb1',jobs:0},
 factory:{n:'Manufacturing Works',cost:9800,col:'#879398',jobs:14,build:'Factory'},
 warehouse:{n:'Freight Depot',cost:12000,col:'#927b65',jobs:10,build:'Freight Depot'},
 office:{n:'Commercial Offices',cost:14200,col:'#a5a69b',jobs:13,build:'Office'},
 college:{n:'Private College',cost:18000,col:'#a9a088',jobs:8,build:'College'},
 airport:{n:'Regional Airfield',cost:0,col:'#879c9e',jobs:18},
 metro_station:{n:'Underground Station',cost:18000,col:'#496a7a',jobs:0,build:'Private Underground'},
 repair:{n:'Resurface road',cost:135,col:'#a0a28b',jobs:0,build:'Repair'},
 home:{n:'Cottage',cost:20000,col:'#cbaf75',jobs:0,build:'Home'},
 grocer:{n:'Grocer',cost:4300,col:'#a96d49',jobs:7,build:'Grocer'},
 bakery:{n:'Bakery',cost:3600,col:'#b77b56',jobs:7,build:'Bakery'},
 mill:{n:'Flour Mill',cost:4800,col:'#869888',jobs:8,build:'Flour Mill'},
 farm:{n:'Farm',cost:3100,col:'#ad9d54',jobs:9,build:'Farm'},
 forestry:{n:'Forestry',cost:3000,col:'#6c8d65',jobs:8,build:'Forestry'},
 sawmill:{n:'Sawmill',cost:4100,col:'#ac865e',jobs:8,build:'Sawmill'},
 quarry:{n:'Quarry',cost:3900,col:'#92928d',jobs:8,build:'Quarry'},
 contractor:{n:'Construction Co.',cost:4400,col:'#b2a38e',jobs:8,build:'Contractor'},
 townhall:{n:'Town Hall',cost:0,col:'#d6c6a4',jobs:0},
 police:{n:'Constabulary',cost:7600,col:'#6588a7',jobs:5,build:'Police Station'},
 fire:{n:'Fire Brigade',cost:6900,col:'#bb745b',jobs:5,build:'Fire Brigade'},
 clinic:{n:'Clinic',cost:8000,col:'#bdb7a3',jobs:6,build:'Clinic'},
 park:{n:'Public Green',cost:550,col:'#6c987a',jobs:0,build:'Park'},
 school:{n:'Village School',cost:6900,col:'#ac9372',jobs:0,build:'School'},
 courthouse:{n:'Magistrates Court',cost:8400,col:'#9a9887',jobs:0,build:'Court'},
 watchtower:{n:'Watchtower',cost:4900,col:'#879089',jobs:0,build:'Watchtower'},
 square:{n:'Market Square',cost:2500,col:'#aca486',jobs:0,build:'Market Square'},
 wharf:{n:'River Cargo Wharf',cost:7600,col:'#819b98',jobs:2,build:'Cargo wharf'},
 fishery:{n:'River Fishery',cost:3500,col:'#75a5a2',jobs:7,build:'Fishery'},
 tavern:{n:'Village Tavern',cost:3200,col:'#b28c56',jobs:6,build:'Tavern'},
};
const goods={grain:2,flour:3,food:3.3,logs:2,timber:4,stone:3,manufactures:8.5};
const formulas={farm:{out:'grain',qty:140,inp:null,amount:0},mill:{out:'flour',qty:175,inp:'grain',amount:105},bakery:{out:'food',qty:200,inp:'flour',amount:105},grocer:{out:null,qty:0,inp:'food',amount:0},forestry:{out:'logs',qty:170},sawmill:{out:'timber',qty:130,inp:'logs',amount:100},quarry:{out:'stone',qty:125},fishery:{out:'food',qty:130},factory:{out:'manufactures',qty:85,inp:'timber',amount:58}};
const buildIcons={metro_station:'Ⓜ',repair:'↻',road:'═',home:'⌂',grocer:'▣',bakery:'♨',mill:'◈',farm:'❖',forestry:'♣',sawmill:'▥',quarry:'◆',contractor:'⚒',police:'♜',fire:'♨',clinic:'✚',park:'♣',school:'✎',courthouse:'⚖',watchtower:'♜',square:'◉',wharf:'⚓',fishery:'≈',tavern:'♨',factory:'⚙',warehouse:'▤',office:'▦',college:'♜'};
const buildCost={metro_station:18000,road:150,repair:135,home:20000,grocer:4300,bakery:3600,mill:4800,farm:3100,forestry:3000,sawmill:4100,quarry:3900,contractor:4400,police:7600,fire:6900,clinic:8000,park:550,school:6900,courthouse:8400,watchtower:4900,square:2500,wharf:7600,fishery:3500,tavern:3200,factory:9800,warehouse:12000,office:14200,college:18000};
const defs=[
 ['privateServices','License new private schools and brigades',0,1,1,'','One permits entrepreneurial entry; zero stops new licenses without confiscating existing providers.'],
 ['privateTuitionCap','Private tuition ceiling / learner / day',0,8,.25,'$','Maximum fee per equivalent learner-day. A low ceiling improves prices only if an operator can still cover qualified teaching and premises costs.'],
 ['privateFireFeeCap','Private brigade membership ceiling / resident / day',0,2,.05,'$','Voluntary inspection, prevention and priority membership. Nonmembers still receive nearby emergency spillover; rescue is never sold at the burning doorstep.'],
 ['serviceVoucherBudget','Targeted private-service vouchers / day',0,400,5,'$','Purchase otherwise unaffordable private teaching or brigade memberships for low-liquid-wealth families. Actual purchases only; unused authorization stays in the treasury.'],
 ['pensionDaily','Retirement pension / person / day',0,40,1,'$','Treasury-funded income for residents over 70. Benefits are shared proportionally if funds fall short; an ageing population raises the fiscal cost.'],
 ['policyRate','Policy interest rate (annual)',0,20,.25,'%','Benchmark set by the monetary authority. Bank funding, new and variable-rate credit, savings and investment hurdles adjust with a lag. Higher rates restrain borrowing and demand; lower rates do not make insolvent projects viable.'],
 ['incomeTax','Income tax',0,40,1,'%','Share of earnings paid by working residents to the town.'],
 ['profitTax','Business profit tax',0,45,1,'%','Tax on positive net operating profit of private businesses.'],
 ['propertyTax','Property tax (annual)',0,5,.1,'%','Tax on property values, charged to owners daily in annualized instalments.'],
 ['foodTax','Food sales tax',0,30,1,'%','Collected from purchases at local grocers; reduces food affordability.'],
 ['utilityTax','Domestic energy levy',0,30,1,'%','Levied on actual household heating and electricity bills. Raises funds, increases living costs.'],
 ['commercialRate','Business property rate (annual)',0,8,.25,'%','Annual tax on privately operating premises, payable even in years with weak profits.'],
 ['minWage','Minimum daily wage',10,90,1,'$','Raises pay but also raises labour costs for small firms.'],
 ['permitFee','Business entry permit',0,3000,25,'$','Fee charged when an investor opens a new enterprise.'],
 ['policeBudget','Constabulary budget / day',0,800,10,'$','Fund patrols, investigators and public safety. Stations improve coverage.'],
 ['defenseBudget','Fire and civil defence / day',0,800,10,'$','Maintains emergency preparedness. Stations improve response.'],
 ['aidBudget','Housing assistance / day',0,600,10,'$','Direct household transfers, prioritized by hardship and low savings.'],
 ['energyAidBudget','Heating assistance / day',0,400,10,'$','Pays energy bills for low-cash households, especially in winter.'],
 ['transitBudget','Commuter transit / day',0,250,10,'$','Supports journeys to work and improves access to jobs across the borough.'],
 ['outreachBudget','Community outreach / day',0,300,10,'$','Local support services that reduce isolation and some risk factors.'],
 ['employmentSubsidy','Wage subsidy / worker / day',0,15,1,'$','Town reimburses employers per filled job, subject to available funds.'],
 ['importTariff','Import tariff',0,40,1,'%','Adds costs to imported food and industrial materials, producing revenue.'],
 ['healthBudget','Clinic & public health / day',0,500,10,'$','Fund preventive treatment, clinic equipment and household health.'],
 ['educationBudget','School & training / day',0,500,10,'$','Raises worker skill and increases business productivity gradually.'],
 ['roadBudget','Road maintenance / day',0,250,10,'$','Upkeep for roads and local access; poor service lowers trade efficiency.'],
 ['zoningRestriction','Building restrictions',0,100,5,'%','Higher restrictions slow private homebuilding, reducing housing supply.'],
 ['businessRegulation','Business compliance rules',0,100,5,'%','Safeguards can lower workplace incidents but add costs to local firms.'],
 ['militiaBudget','Civil defence volunteers / day',0,400,10,'$','Reserve volunteers who help manage exceptional floods and regional emergencies.'],
 ['bankReserve','Bank minimum reserve',5,35,1,'%','Bank cash reserves against deposits. Higher levels lower lending capacity and help meet withdrawals.'],
 ['lendingRules','Credit underwriting standards',0,100,5,'%','Strict standards constrain risky borrowing but reduce investment and consumption credit.'],
 ['depositGuarantee','Deposit insurance coverage',0,100,5,'%','When a bank fails, cover this share of otherwise lost deposits using available municipal funds.'],
 ['treasuryInvestment','Regional reserve investment share',0,100,5,'%','Share of surplus municipal cash available to buy outside-region securities when trade liquidity is low.']
];
const defaults={privateServices:1,privateTuitionCap:4,privateFireFeeCap:1,serviceVoucherBudget:0,policyRate:3,pensionDaily:16,incomeTax:12,profitTax:12,propertyTax:1.1,foodTax:4,utilityTax:2,commercialRate:.6,energyAidBudget:35,transitBudget:35,minWage:28,permitFee:250,policeBudget:180,defenseBudget:140,aidBudget:100,outreachBudget:40,employmentSubsidy:0,importTariff:0,healthBudget:70,educationBudget:90,roadBudget:25,zoningRestriction:25,businessRegulation:25,militiaBudget:25,bankReserve:12,lendingRules:35,depositGuarantee:0,treasuryInvestment:60,imports:true};
let hostSuspended=false;
let G=null,active='',buildMode='',selected=null,paused=false,speed=1,toastTimeout=0,chosenScenario='settlement',draftPolicy={},overlay='none',pendingEvent=null,previousDailyCash=0,autoSaveOK=true,filterPeople='all',filterFirms='all',citizenQuery='',constructionCategory='all',showTutorial=true,roadPainted=new Set(),roadBatchDirty=false;
let bitmap=document.createElement('canvas');bitmap.width=RW;bitmap.height=RH;let bg=bitmap.getContext('2d',{alpha:false,willReadFrequently:false});
const cv=$('view'),ctx=cv.getContext('2d',{alpha:false});let cw=1000,ch=600,dpr=1,cam={x:RW/2,y:RH/2,zoom:.68};let dirty=true,staticDirty=true;let vehicles=[];
// FINANCIAL ECONOMY: banks are separate cash-holding agents. Deposits are
// liabilities, NOT additional currency in the conservation check. Loans move
// actual reserves to borrowers and return principal + interest on repayment.
const FIN_BANK_NAMES=['Vale Mutual Savings','Mercantile & County Bank','First Borough Credit'];
