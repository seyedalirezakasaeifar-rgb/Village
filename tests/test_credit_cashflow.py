"""Matched borrower, payment-phase, risk-pricing and commissioned-capacity probes."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js','''
window.__creditProbe=()=>{const originalTown=G,originalPayments=loanPayments;try{
 const clone=()=>{G=JSON.parse(JSON.stringify(originalTown));};clone();const applicant={people:[],cash:0,deposits:{},netIncomeTrend:50,incomeVariance:0,essentialDueTrend:35};
 const negative=bankLoan('household',0,-100,360),negativeSafe=!G.households[0].creditDecision;const low=assessCredit('household',applicant,5000,720,.05),high=assessCredit('household',applicant,5000,720,.20),volatile=assessCredit('household',{...applicant,incomeVariance:400},5000,720,.05);
 clone();const h=G.households[0],bank=G.banks[0];h.cash+=1000;bank.cash-=1000;h.normalDisposable=100000;
 const l={id:1,bankId:0,ownerType:'household',ownerId:0,original:1000,balance:1000,rate:.1,spread:.07,fixedRate:true,term:360,created:G.day,arrears:0,status:'active',paid:0};G.loans=[l];const total=totalMoney(),phases=[];
 loanPayments=function(loans=G.loans){if(loans.includes(l))phases.push({optional:h.discretionary,servicesFunded:G.serviceProvision?.health?.day===G.day});return originalPayments(loans);};tick();const payment={phases,paid:l.paid,drift:totalMoney()-total};originalPayments([l]);payment.repeatPaid=l.paid;loanPayments=originalPayments;
 clone();const f=G.firms[0];G.banks[0].cash-=1000;G.region+=1000+f.cash;f.cash=0;f.debt=1000;f.expenses=0;const overdue={...l,ownerType:'firm',balance:1000,original:1000,paid:0,lastPaymentDay:null,status:'active',arrears:0};G.loans=[overdue];const before=totalMoney();loanPayments();const accrual={expense:f.expenses,balance:overdue.balance,paid:overdue.paid,drift:totalMoney()-before};
 const quote=arrears=>{clone();G.day=15;G.loans=[{...l,ownerType:'firm',balance:10000,arrears,status:'active'}];G.banks[0].loanAPY=.08;bankCompetition();return G.banks[0].loanAPY;};const safeQuote=quote(0),riskyQuote=quote(90);
 clone();G.day=14;const company=G.firms.find(f=>f.kind==='farm');G.region-=2000000-company.cash;company.cash=2000000;company.age=100;company.scale=1;company.marginTrend=.3;company.revenueTrend=1000;company.salesTrend=1000;company.ratedOutput=1000;const funds=totalMoney();planEnterprise(company);const order=company.pendingEquipment,orderedScale=company.scale;G.day=order.ready-1;completeEquipmentOrders();const earlyScale=company.scale;G.day=order.ready;completeEquipmentOrders();const commissionedScale=company.scale;completeEquipmentOrders();const equipment={orderedScale,earlyScale,commissionedScale,repeatScale:company.scale,drift:totalMoney()-funds};
 clone();G.day=14;const idle=G.firms.find(f=>f.kind==='farm');G.region-=2000000-idle.cash;idle.cash=2000000;idle.age=100;idle.marginTrend=.3;idle.revenueTrend=1000;idle.salesTrend=1;idle.ratedOutput=1000;planEnterprise(idle);equipment.idleOrder=!!idle.pendingEquipment;
 return {negative,negativeSafe,low,high,volatile,payment,accrual,safeQuote,riskyQuote,equipment};
 }finally{G=originalTown;loanPayments=originalPayments;}};
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__creditProbe()')
 assert r['negative'] is None and r['negativeSafe'];assert r['low']['approved'] and not r['high']['approved'] and not r['volatile']['approved'],r
 assert r['payment']['paid']>0 and r['payment']['paid']==r['payment']['repeatPaid']
 assert r['payment']['phases']==[{'optional':0,'servicesFunded':True}],r['payment']
 assert abs(r['payment']['drift'])<.001 and abs(r['accrual']['drift'])<.001
 assert r['accrual']['paid']==0 and abs(r['accrual']['expense']-1000*.1/360)<.00001 and r['accrual']['balance']>1000
 assert r['riskyQuote']>r['safeQuote']
 e=r['equipment'];assert e['orderedScale']==e['earlyScale']==1 and e['commissionedScale']==e['repeatScale']>1 and abs(e['drift'])<.001 and not e['idleOrder'],e
 b.close();print('PASS stressed affordability, debt-before-optional-spending, public income timing, once/day repayment, accrued interest, impaired-portfolio pricing and delayed productive investment')
