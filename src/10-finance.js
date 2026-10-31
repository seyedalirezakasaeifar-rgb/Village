function ensureFinance(){
 if(!G)return;
 if(!Array.isArray(G.banks))G.banks=[];
 if(!Array.isArray(G.loans))G.loans=[];
 if(!G.finance)G.finance={failures:0,businessDefaults:0,householdDefaults:0,creditIssued:0,depositLosses:0,insuredPayouts:0,foreclosures:0,downzonings:0,insolvencies:0,bankRuns:0};
 for(const h of G.households){if(!h.deposits||typeof h.deposits!=='object'||Array.isArray(h.deposits))h.deposits={};if(!Number.isFinite(h.creditScore))h.creditScore=.65;}
 for(const f of G.firms){if(!Number.isFinite(f.creditScore))f.creditScore=.68;if(!Number.isFinite(f.lossDays))f.lossDays=0;}
}
function seedBanks(){
 ensureFinance();if(G.banks.length)return;
 const capital=[34000,29000,26000],depositAPY=[.016,.024,.031],loanAPY=[.071,.085,.109];
 for(let i=0;i<3;i++){const equity=Math.min(capital[i],Math.max(0,G.region-50000));G.region-=equity;
  G.banks.push({id:i,name:FIN_BANK_NAMES[i],cash:equity,depositAPY:depositAPY[i],loanAPY:loanAPY[i],closed:false,runDays:0,losses:0,interestEarned:0,interestPaid:0,loansOriginated:0});
 }
 // Voluntary deposits: cash leaves household wallets and enters bank vaults.
 for(const h of G.households){const b=G.banks[h.id%3];const amount=Math.max(0,Math.min(h.cash,Math.round(h.cash*(.08+(h.id%5)*.055))));
  h.cash-=amount;b.cash+=amount;h.deposits[b.id]=amount;
 }
}
function bankDeposits(bankId){let n=0;for(const h of G.households)n+=Math.max(0,h.deposits?.[bankId]||0);for(const f of G.firms)n+=Math.max(0,f.deposits?.[bankId]||0);return n}
function bankLoans(bankId){return G.loans.filter(l=>l.bankId===bankId&&l.status==='active').reduce((n,l)=>n+l.balance,0)}
function bankEquity(b){return b.cash+(b.regionCredit||0)+bankLoans(b.id)-bankDeposits(b.id)}
function availableBank(b){const reserve=Math.max(bankDeposits(b.id)*((G.policy.bankReserve??12)/100),Math.max(0,bankEquity(b))*.30);return Math.max(0,b.cash-reserve)}
function bestBank(loan=false){return G.banks.filter(b=>!b.closed&&availableBank(b)>3500&&bankEquity(b)>1000).sort((a,b)=>loan?a.loanAPY-b.loanAPY:b.depositAPY-a.depositAPY)[0]||null}
function bankLoan(kind,id,amount,term=360){
 ensureFinance();if(!['firm','household'].includes(kind)||!Number.isFinite(amount)||amount<=0||!Number.isInteger(term)||term<30||term>3600)return null;let owner=kind==='firm'?G.firms[id]:G.households[id];if(!owner||owner.closed)return null;const decline=reason=>{owner.creditDecision={day:G.day,requested:amount,approved:false,reason};return null;};
 if(G.loans.some(l=>l.status==='active'&&l.ownerType===kind&&l.ownerId===id))return decline('An active loan already finances this borrower');
 const strict=(G.policy.lendingRules??35)/100;const score=clamp(owner.creditScore??.65,.05,.99);
 const ratio=kind==='firm'?amount/Math.max(1,owner.cash+1500):amount/Math.max(1,owner.cash+(owner.deposits?Object.values(owner.deposits).reduce((a,v)=>a+v,0):0));
 if(amount<100)return decline('Requested advance is below the lending minimum');if(score<.32+strict*.25)return decline('Credit standing does not meet current lending standards');if(ratio>7.8-strict*3.2)return decline('Request exceeds the borrower liquidity limit');
 const b=G.banks.filter(b=>!b.closed&&availableBank(b)>=amount*1.20&&bankEquity(b)>amount*.08).sort((a,b)=>a.loanAPY-b.loanAPY)[0];if(!b)return decline('No bank has sufficient lendable reserves and equity');
 const rate=b.loanAPY+strict*.022+(1-score)*.055;const assessment=assessCredit(kind,owner,amount,term,rate);owner.creditDecision={day:G.day,requested:amount,...assessment};if(!assessment.approved)return null;
 b.cash-=amount;owner.cash+=amount;
 const loan={id:(G.nextLoanId= Math.max(G.nextLoanId||0,G.loans.length)+1),bankId:b.id,ownerType:kind,ownerId:id,original:amount,balance:amount,rate,spread:Math.max(.02,rate-(G.policy.policyRate||0)/100),fixedRate:false,term,created:G.day,arrears:0,status:'active',paid:0};
 G.loans.push(loan);b.loansOriginated++;G.finance.creditIssued+=amount;
 if(kind==='firm')owner.debt=(owner.debt||0)+amount;
 return loan;
}
function loanPayments(loans=G.loans){
 for(const l of loans){if(l.status!=='active'||l.balance<=0||l.lastPaymentDay===G.day)continue;l.lastPaymentDay=G.day;
  const owner=l.ownerType==='firm'?G.firms[l.ownerId]:G.households[l.ownerId];if(!owner){l.status='default';l.defaultedDay=G.day;continue;}
  const lender=l.bankId<0?null:G.banks[l.bankId];
  if(G.day%30===0&&l.fixedRate!==true){const benchmark=(G.policy.policyRate||0)/100,spread=l.spread??Math.max(.025,l.rate-.03);l.spread=spread;l.rate=l.rate*.75+(benchmark+spread)*.25;}
  const interest=l.balance*l.rate/360;
  const minPrincipal=Math.min(l.balance,l.original/Math.max(30,l.term));
  const due=minPrincipal+interest;l.scheduledDue=due;owner.debtDue=(owner.debtDue||0)+due;
  // Borrowers cannot pay more than cash. Failed firms cannot create repayment funds.
  if(l.ownerType==='household'&&owner.cash<due)for(const [id,deposit] of Object.entries(owner.deposits||{})){withdrawal(owner,G.banks[+id],Math.min(deposit,due-owner.cash));if(owner.cash>=due)break;}
  const paid=Math.min(Math.max(0,owner.cash),due);
  const paidInterest=Math.min(paid,interest),paidPrincipal=Math.max(0,paid-paidInterest);
  owner.cash-=paid;if(l.ownerType==='household')owner.debtService=(owner.debtService||0)+paid;if(lender&&!lender.closed){lender.cash+=paid;lender.interestEarned+=paidInterest}else G.region+=paid;
  l.paidToday=paid;
  l.balance=Math.max(0,l.balance-paidPrincipal+(interest-paidInterest));l.paid+=paid;
  if(l.ownerType==='firm'){owner.debt=Math.max(0,(owner.debt||0)-paidPrincipal+(interest-paidInterest));owner.expenses=(owner.expenses||0)+interest;}
  if(paid<due*.8){l.arrears++;owner.creditScore=clamp(owner.creditScore-.004,.08,.99);}else {l.arrears=Math.max(0,l.arrears-1);owner.creditScore=clamp(owner.creditScore+.0004,.08,.99);}
  if(l.balance<.01){l.balance=0;l.status='repaid';if(l.ownerType==='firm')owner.debt=0;}
  else if(l.arrears>=95||owner.closed&&l.arrears>=12){
   l.status='default';l.defaultedDay=G.day;if(l.ownerType==='firm'){owner.debt=Math.max(0,(owner.debt||0)-l.balance);G.finance.businessDefaults++;}
   else G.finance.householdDefaults++;
   if(lender&&!lender.closed)lender.losses+=l.balance;
   owner.creditScore=clamp(owner.creditScore-.22,.05,.99);
   story((l.ownerType==='firm'?owner.name:'The '+owner.name+' household')+' defaulted on a bank loan of '+money(l.balance)+'.','bad',l.ownerType==='firm'?owner.building:owner.home);
  }
 }
}
function depositTransfer(h,b,amount){
 if(!b||b.closed||amount<=0)return 0;amount=Math.max(0,Math.min(h.cash,amount));h.cash-=amount;b.cash+=amount;h.deposits[b.id]=(h.deposits[b.id]||0)+amount;return amount;
}
function withdrawal(h,b,amount){
 if(!b||b.closed||amount<=0)return 0;
 // Redeem the bank's own marketable securities at par before denying cash withdrawals.
 const requested=Math.min(amount,h.deposits?.[b.id]||0),redeem=Math.min(Math.max(0,requested-b.cash),b.regionCredit||0,Math.max(0,G.region));
 if(redeem>0){G.region-=redeem;b.cash+=redeem;b.regionCredit-=redeem;}
 amount=Math.min(requested,b.cash);
 h.deposits[b.id]-=amount;b.cash-=amount;h.cash+=amount;return amount;
}
function liquidateBank(b,reason='Insolvent balance sheet'){
 if(b.closed)return;const claims=bankDeposits(b.id);
 b.closed=true;G.finance.failures++;
 // A failed bank's loan assets are sold to regional creditors for a conservative
 // haircut; the cash price funds the receivership. Region receives loan rights.
 let transferred=0;for(const l of G.loans){if(l.bankId!==b.id||l.status!=='active')continue;
  const purchase=Math.min(G.region,Math.max(0,l.balance*.35));G.region-=purchase;b.cash+=purchase;
  l.bankId=-1;transferred++;
 }
 if((b.regionCredit||0)>0){const value=b.regionCredit;const sale=Math.min(G.region,value*.83);G.region-=sale;b.cash+=sale;b.regionCredit=0;}
 const liquidCash=Math.max(0,b.cash),uninsured=clamp(G.policy.depositGuarantee??0,0,100)/100;
 const recovery=claims>0?Math.min(1,liquidCash/claims):1;
 let losses=0,payout=0;
 for(const entity of [...G.households,...G.firms]){
  if(!entity.deposits)continue;const claim=Math.max(0,entity.deposits[b.id]||0);if(!claim)continue;
  const recovered=claim*recovery,shortfall=claim-recovered;
  entity.cash+=recovered;b.cash-=recovered;payout+=recovered;entity.deposits[b.id]=0;
  // A deposit guarantee pays against a quantified loss from municipal funds,
  // not freshly invented reserves. Insufficient budget leaves uncovered losses.
  const insured=Math.min(shortfall*uninsured,G.treasury);
  G.treasury-=insured;entity.cash+=insured;G.finance.insuredPayouts+=insured;
  losses+=shortfall-insured;
 }
 G.finance.depositLosses+=losses;
 G.region+=Math.max(0,b.cash);b.cash=0;
 story(b.name+' entered receivership: '+reason+'. Depositor losses '+money(losses)+', '+transferred+' loans sold to regional lenders.','bad');
}
function regionalCapitalMarket(){
 // Depositor-backed private investment and municipal savings purchase bonds
 // in the outside trading region. Bonds remain assets on lender balance sheets;
 // cash actually moves to the region to finance demand for local exports.
 if(!G||!G.banks)return;
 G.publicReserve=Number.isFinite(G.publicReserve)?G.publicReserve:0;
 for(const b of G.banks){if(b.closed)continue;
  const due=(b.regionCredit||0)*.037/360;
  const paid=Math.min(due,Math.max(0,G.region));
  G.region-=paid;b.cash+=paid;b.interestEarned+=paid;
  if(paid+1e-6<due)b.regionArrears=(b.regionArrears||0)+(due-paid);
  else b.regionArrears=Math.max(0,(b.regionArrears||0)-paid*.15);
 }
 const publicInterest=Math.min(G.region,G.publicReserve*.024/360);
 G.region-=publicInterest;G.treasury+=publicInterest;
 if(G.day%30!==0)return;
 const targetRegion=3500000;
 // Local savings reach external borrowers only when credit is required.
 if(G.region<targetRegion){
  const fraction=clamp((G.policy.treasuryInvestment??60)/100,0,1);
  const invest=Math.max(0,Math.min(210000,(G.treasury-240000)*.30*fraction,targetRegion-G.region));
  if(invest>200){G.treasury-=invest;G.region+=invest;G.publicReserve+=invest;}
  for(const b of G.banks){if(b.closed)continue;
   const claims=bankDeposits(b.id);
   const minimumCash=Math.max(9000,claims*.42);
   const limit=Math.max(0,claims*.54-(b.regionCredit||0));
   const amount=Math.max(0,Math.min(180000,b.cash-minimumCash,limit,targetRegion-G.region));
   if(amount>1000&&bankEquity(b)>claims*.015){b.cash-=amount;b.regionCredit=(b.regionCredit||0)+amount;G.region+=amount;}
  }
 }else if(G.region>targetRegion+1200000){
  // Bond market repayments are actual transfers, not asset write-offs.
  for(const b of G.banks){if(b.closed||!b.regionCredit)continue;
   const redeem=Math.min(b.regionCredit*.10,G.region-(targetRegion+500000));
   if(redeem>0){b.regionCredit-=redeem;G.region-=redeem;b.cash+=redeem;}
  }
 }
 if(G.treasury<25000&&G.publicReserve>0&&G.region>75000){
  const redeem=Math.min(G.publicReserve,85000,G.region-50000);G.publicReserve-=redeem;G.region-=redeem;G.treasury+=redeem;
 }
}
function bankCompetition(){
 if(G.day%15!==0)return;
 // Rates are quoted independently. Liquidity, credit demand, regulation and
 // default histories affect spreads, allowing depositors and borrowers to shop.
 for(const b of G.banks){if(b.closed)continue;
  const deposits=bankDeposits(b.id),liquid=deposits>0?b.cash/deposits:1;
  const stress=Math.max(0,1.25-liquid);
  const demand=clamp((G.stats.businesses||20)/80,0,.6);
  const risk=clamp((G.policy.lendingRules??35)/100,0,1);
  const exposure=G.loans.filter(l=>l.bankId===b.id),active=exposure.filter(l=>l.status==='active'),arrears=active.reduce((n,l)=>n+l.balance*clamp(l.arrears/95,0,1),0),recentLoss=exposure.filter(l=>l.status==='default'&&l.defaultedDay>=(b.createdDay||0)&&G.day-l.defaultedDay<360).reduce((n,l)=>n+l.balance,0);
  const creditRisk=clamp((arrears+recentLoss)/Math.max(1,active.reduce((n,l)=>n+l.balance,0)+recentLoss),0,1);b.creditRisk=creditRisk;
  const targetLoan=clamp((G.policy.policyRate||0)/100+.022+(b.id%3)*.004+risk*.018+stress*.025+demand*.008+creditRisk*.04,.018,.34);
  b.loanAPY=b.loanAPY*.72+targetLoan*.28;
  const targetDeposit=clamp((G.policy.policyRate||0)/100*.78+.002+(b.id%3)*.001+stress*.004,.001,.18);
  b.depositAPY=b.depositAPY*.75+targetDeposit*.25;
 }
}
function bankMarketEntry(){
 if(G.day%90!==0||G.region<100000)return false;
 const operating=G.banks.filter(b=>!b.closed);
 const population=G.stats.population||0;
 if(operating.length>=3&&(population<700||operating.length>=4))return false;
 if(operating.length>=2&&(G.stats.marketConfidence||50)<36)return false;
 const initial=25000+Math.min(15000,Math.max(0,population-350)*14);
 if(G.region<initial+50000)return false;
 G.region-=initial;
 const retired=G.banks.find(b=>b.closed);const id=retired?retired.id:G.banks.length;
 const names=['Riverside Savings & Loan','County Agricultural Credit','Broadway Commercial Bank','East Bank Mutual','Cooperative Industrial Bank','Western Exchange Bank'];
 const bank={id,name:names[((G.finance.failures||0)+id)%names.length],cash:initial,depositAPY:.027,loanAPY:.081,closed:false,runDays:0,losses:0,interestEarned:0,interestPaid:0,loansOriginated:0,createdDay:G.day};
 if(retired)G.banks[id]=bank;else G.banks.push(bank);
 let branch=G.buildings.find(b=>b.kind==='bank'&&(b.bankId===retired?.id||G.banks[b.bankId]?.closed));
 if(!branch){const candidates=buildableCandidates('business');let place=candidates[0];if(place){branch={id:G.nextId++,kind:'bank',x:place.x,y:place.y,value:75000,condition:100,owner:-1,firm:-1,hh:-1};G.buildings.push(branch);invalidateRoads(false);}}
 if(branch)branch.bankId=id;
 staticDirty=true;dirty=true;
 story(bank.name+' opened after raising '+money(initial)+' in subscribed regional capital. Depositors now have another choice.','good',branch?.id||0);
 return true;
}
function bankDaily(){
 ensureFinance();loanPayments(G.loans.filter(l=>l.ownerType==='firm'||!G.households[l.ownerId]?.people.length));regionalCapitalMarket();bankCompetition();bankMarketEntry();
 // Keep fulfilled and defaulted loan history bounded; active loans are never discarded.
 if(G.loans.length>2500){const past=G.loans.filter(l=>l.status!=='active');const removable=new Set(past.slice(0,Math.max(0,G.loans.length-1800)).map(l=>l.id));if(removable.size)G.loans=G.loans.filter(l=>!removable.has(l.id));}

 // Overnight funds deposited with the regional clearing market earn a floating yield.
 // Every dollar of interest is paid by that counterparty; no currency is minted.
 for(const b of G.banks){if(b.closed)continue;const yieldRate=clamp((G.policy.policyRate||0)/100*.85,.001,.17);const earnings=Math.min(G.region,b.cash*yieldRate/360);G.region-=earnings;b.cash+=earnings;b.interestEarned+=earnings;}
 for(const bank of G.banks){if(bank.closed)continue;const expense=Math.min(bank.cash,4+G.loans.filter(l=>l.bankId===bank.id&&l.status==='active').length*.22);bank.cash-=expense;const beneficiaries=G.households.filter(h=>h.people.length>0);if(beneficiaries.length){let worker=beneficiaries[(G.day+bank.id*17)%beneficiaries.length];worker.cash+=expense*.7;worker.income+=expense*.7;worker.serviceReceipts=(worker.serviceReceipts||0)+expense*.7;G.region+=expense*.3;}else G.region+=expense;}
 for(const b of G.banks){if(b.closed)continue;
  // Interest accrues daily to depositors as a claim on bank assets.
  // It is capped by the bank's non-impaired equity to avoid uncontrolled negative values.
  const claims=bankDeposits(b.id),cap=Math.max(0,bankEquity(b));
  const interest=Math.min(claims*b.depositAPY/360,cap*.012);
  if(interest>0&&claims>0){for(const entity of [...G.households,...G.firms]){const bal=entity.deposits?.[b.id]||0;if(bal>0)entity.deposits[b.id]+=interest*bal/claims;}
   b.interestPaid+=interest;}
 }
 // Withdrawal/deposit decisions are monthly rather than per-frame.
 if(G.day%30===0){
  for(const h of G.households){if(!h.people.length)continue;const deposited=Object.values(h.deposits||{}).reduce((a,v)=>a+v,0);
   const need=Math.max(0,Math.min(deposited,h.people.length*30-h.cash));
   if(need>0){let remaining=need;const balances=Object.entries(h.deposits).sort((a,b)=>b[1]-a[1]);for(const [id] of balances){if(remaining<=.001)break;remaining-=withdrawal(h,G.banks[+id],remaining);}}
   else if(h.cash>Math.max(900,h.people.length*600)){
    const bank=G.banks.filter(b=>!b.closed&&bankEquity(b)>0).sort((a,b)=>b.depositAPY-a.depositAPY)[0];
    if(bank)depositTransfer(h,bank,(h.cash-h.people.length*500)*.18);
   }
  }
  for(const b of G.banks){if(b.closed)continue;
   // Defaults deteriorate solvency. A reserve shortage generates withdrawals
   // only if confidence is already low, making runs endogenous, not arbitrary.
   const claims=bankDeposits(b.id);
   // A solvent institution first sells liquid regional assets, then seeks private equity.
   const redemption=Math.min(Math.max(0,claims*.25-b.cash),b.regionCredit||0,G.region);
   if(redemption>0){b.regionCredit-=redemption;G.region-=redemption;b.cash+=redemption;}
   const capital=bankEquity(b);
   const liquid=claims>0?b.cash/claims:1;
   const requiredEquity=Math.max(2200,claims*.035);
   if(capital>=0&&capital<requiredEquity&&liquid>.25&&G.region>requiredEquity+50000){
    const issue=Math.min(50000,requiredEquity-capital+1500,G.region*.05);
    G.region-=issue;b.cash+=issue;b.equityRaised=(b.equityRaised||0)+issue;
    if(G.day%360===0)story(b.name+' raised '+money(issue)+' in new private equity to strengthen depositor protection.','neutral');
   }
   if(capital<0||liquid<(G.policy.bankReserve??12)/180){b.runDays++;
    const panic=clamp((.16-liquid)*.4+(claims*.03-capital)/Math.max(1,claims)*.5,0,.15);
    if(panic>.005){for(const h of G.households){const d=h.deposits?.[b.id]||0;if(d>0)withdrawal(h,b,d*panic);}
     G.finance.bankRuns++;}
   }else b.runDays=Math.max(0,b.runDays-1);
   if(bankEquity(b)<-100||(b.runDays>=12&&b.cash<claims*.06)||claims>0&&b.cash<1&&b.runDays>=4)liquidateBank(b,capital<0?'Loan losses exceeded capital':'Sustained deposit withdrawals');
  }
 }
 // Struggling companies can apply for a genuinely funded line of credit.
 if(G.day%60===0){
  const candidate=G.households.filter(h=>h.people.length>0&&h.cash<120&&h.creditScore>.6&&h.worklessness<20).sort((a,b)=>a.cash-b.cash).slice(0,2);
  for(const h of candidate)bankLoan('household',h.id,Math.round(400+h.people.length*210),150);
 }
 if(G.day%35===0){const s=G.firms.filter(f=>!f.closed&&f.cash<2800&&f.age>35&&f.lossDays<14&&f.profit> -45&&f.strain<18&&f.creditScore>.56)
   .sort((a,b)=>a.cash-b.cash).slice(0,Math.max(2,Math.ceil(G.firms.length*.08)));
  for(const f of s){const loan=bankLoan('firm',f.id,Math.round(clamp(6800-f.cash,2300,6500)),420);
   if(loan)story(f.name+' received '+money(loan.original)+' of working-capital credit from '+G.banks[loan.bankId].name+'.','neutral',f.building);
  }
 }
}
function liquidateFirm(f,reason){
 // Insolvent companies dispose of stock/equipment, pay secured creditors, and
 // distribute only the residual to shareholders. Assets cannot pay twice.
 if(!f||f.closed)return false;
 const site=readBuild(f.building);
 const stockValue=Object.entries(f.stock||{}).reduce((n,[key,value])=>n+Math.max(0,value)*(goods[key]||1),0);
 const salvage=Math.max(0,Math.min(G.region,stockValue*.18+(site?.value||0)*.015));
 G.region-=salvage;f.cash+=salvage;
 for(const l of G.loans){if(l.ownerType!=='firm'||l.ownerId!==f.id||l.status!=='active')continue;
  const amount=Math.min(Math.max(0,f.cash),Math.max(0,l.balance));
  f.cash-=amount;l.balance=Math.max(0,l.balance-amount);l.paid+=amount;
  const bank=l.bankId>=0?G.banks[l.bankId]:null;
  if(bank&&!bank.closed)bank.cash+=amount;else G.region+=amount;
  if(l.balance<.01){l.balance=0;l.status='repaid';}
  else {l.status='default';l.defaultedDay=G.day;G.finance.businessDefaults++;if(bank&&!bank.closed)bank.losses+=l.balance;f.creditScore=clamp((f.creditScore||.6)-.20,.05,.99);}
 }
 const residual=Math.max(0,f.cash);f.cash=0;f.debt=0;
 const shareholder=G.households[f.owner];if(shareholder)shareholder.cash+=residual;else G.region+=residual;
 for(const [good,qty] of Object.entries(f.stock))goodsEntry(good,'exports',qty);
 f.stock={};f.closed=true;f.closedDay=G.day;G.finance.insolvencies++;
 for(const id of f.workers)if(G.people[id])G.people[id].job=-1;
 f.workers=[];
 story(f.name+' entered liquidation: '+reason+'. Creditors received asset proceeds before shareholders.','bad',f.building);
 return true;
}
function liquidityStress(){
 // Firms go bankrupt after actual negative operating history and persistent
 // inability to satisfy creditors, not from a random destruction roll.
 for(const f of G.firms){if(f.closed)continue;
  if(f.profit<0&&f.cash<3000)f.lossDays++;else f.lossDays=Math.max(0,(f.lossDays||0)-2);
  if(f.lossDays>68&&f.cash<360)liquidateFirm(f,f.lossDays+' consecutive financially weak days');
 }
}
function outwardMigration(){
 if(G.day%30!==0)return 0;
 const hardship=G.stats.hardship||0,unemployment=G.stats.unemployment||0;
 if(hardship<25&&unemployment<26&&(G.regionalDemand||1)>.68)return 0;
 const chance=clamp(.035+Math.max(0,hardship-25)*.004+Math.max(0,unemployment-26)*.003,0,.27);
 if(random()>chance)return 0;
 const choices=G.households.filter(h=>h.home>=0&&h.people.length>0&&h.stress>42&&h.cash<Math.max(550,h.people.length*260))
  .sort((a,b)=>(b.stress-a.stress)+(a.cash-b.cash)*.005);
 if(!choices.length)return 0;
 const h=choices[0],oldHome=readBuild(h.home),departures=h.people.slice();
 for(const id of departures){const p=G.people[id];if(!p)continue;p.movedAway=true;p.job=-1;
  for(const f of G.firms)if(f.workers.includes(id))f.workers=f.workers.filter(n=>n!==id);
 }
 h.people=[];
 // External migrants take cash with them. Their remaining bank deposits are
 // still real liabilities to external depositors, not municipal residents.
 G.region+=Math.max(0,h.cash);h.cash=0;
 story('The '+h.name+' family left town after persistent hardship and weak job prospects, leaving a vacant home.','bad',oldHome?.id||0);
 recompute();return departures.length;
}
function reverseRedevelopment(){
 if(G.day%60!==0||!G.autoBuild)return false;
 const d=cityDemand();
 // Building owners react to actual vacancy and declining values. A tower will
 // not be razed while families still depend on its units.
 if(d.housingPressure>42||d.homeDemand>12)return false;
 const towers=G.buildings.filter(b=>['tower','apartment'].includes(b.kind)&&!b.redevelopment&&
   !G.projects.some(p=>p.id===b.id));
 for(const b of towers){
  const occupied=(b.units||[]).map(id=>G.households[id]).filter(h=>h&&h.home===b.id&&h.people.some(id=>!G.people[id]?.deceased&&G.people[id]?.movedAway!==true));
  if(occupied.length>1)continue;
  if((G.day-(b.lastRedeveloped||0))<480)continue;
  const cost=b.kind==='tower'?48000:19000;
  if(G.region<cost+30000)continue;
  // Owner pays demolition and conversion; no residents disappear.
  privateContract(cost);
  const sole=occupied[0];const formerUnits=(b.units||[]).slice();b.kind='home';b.footprint=[roadId(b.x,b.y)];invalidateBuildingIndex();invalidateRoads(false);b.units=[];b.hh=sole?.id??-1;b.value=Math.max(35000,Math.round(b.value*.28));b.replacedKind='tower';b.lastRedeveloped=G.day;
  for(const hid of formerUnits){const household=G.households[hid];if(household&&household.id!==sole?.id&&household.home===b.id)household.home=-1;}
  if(sole){sole.home=b.id;if(!G.homes.includes(b.id))G.homes.push(b.id)}
  G.finance.downzonings++;G.development.downzonings=(G.development.downzonings||0)+1;
  staticDirty=true;dirty=true;
  story('Vacancy and falling land values led a developer to replace an underused high-rise with a single residence.','neutral',b.id,b.hh);
  return true;
 }
 return false;
}
function financePanel(){
 ensureFinance();const active=G.loans.filter(l=>l.status==='active');
 const deposits=G.banks.reduce((n,b)=>n+bankDeposits(b.id),0),credit=active.reduce((n,l)=>n+l.balance,0);
 return head('Banking and credit markets')+tip('Banks compete for deposits and make loans from actual available cash. Firms can fail after losses and debt defaults; banks can enter receivership following asset losses and withdrawals. Deposits are liabilities, not extra money.')+
 `<div class="statgrid">${stat('Household deposits',money(deposits))}${stat('Outstanding credit',money(credit))}${stat('Operating banks',G.banks.filter(b=>!b.closed).length+' / '+G.banks.length)}${stat('Bank failures',G.finance.failures)}${stat('Business insolvencies',G.finance.insolvencies)}${stat('Loan defaults',G.finance.businessDefaults+G.finance.householdDefaults)}${stat('Depositor losses',money(G.finance.depositLosses))}${stat('Converted towers',G.finance.downzonings)}</div>`+
 head('Competing institutions')+G.banks.map(b=>`<div class="council-card"><h3>${esc(b.name)} · ${b.closed?'IN RECEIVERSHIP':'OPEN'}</h3>${strip('Deposits owed',money(bankDeposits(b.id)))}${strip('Cash reserves',money(b.cash))}${strip('Loan portfolio',money(bankLoans(b.id)))}${strip('Regional securities',money(b.regionCredit||0))}${strip('Equity after impairments',money(bankEquity(b)))}${strip('Savings interest',Math.round(b.depositAPY*10000)/100+'% annual')}${strip('Base lending rate',Math.round(b.loanAPY*10000)/100+'% annual')}</div>`).join('')+
 head('Current debtors')+active.slice(0,24).map(l=>{const owner=l.ownerType==='firm'?G.firms[l.ownerId]:G.households[l.ownerId];return `<div class="entry"><strong>${esc(owner?.name||'Unknown debtor')}</strong><small> ${money(l.balance)} outstanding · ${(100*l.rate).toFixed(1)}% interest · ${esc(G.banks[l.bankId]?.name||'Regional creditor')}</small></div>`}).join('')+
 head('Municipal savings')+strip('Public regional-bond holdings',money(G.publicReserve||0))+strip('Liquid municipal cash',money(G.treasury))+head('Financial history')+miniChart('deposits')+tip('Council policies influence reserve requirements, credit standards and whether public funds insure part of the deposits lost in a bank liquidation. Bank failures are possible without being guaranteed.');
}

