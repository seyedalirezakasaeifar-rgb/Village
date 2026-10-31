#!/usr/bin/env python3
"""Source-bound matched macro experiments; no production tuning or authored grants.

Run: python tools/balance_lab.py --years 30 --seeds 42,101,909
A month is 30 days and a game year is 360 days. Results are model evidence,
not human playtesting or real-world policy estimates. Negative outcomes persist.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, time
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from test_mobile_rendering import html

PROBE = r'''
window.__balanceLab = (()=>{
 let start, original, basePeople, totals, actions;
 const sum=(xs,f)=>xs.reduce((n,x)=>n+(Number(f(x))||0),0);
 const quantile=(xs,q)=>xs.length?xs.slice().sort((a,b)=>a-b)[Math.floor((xs.length-1)*q)]:0;
 const alive=p=>!p.deceased&&!p.movedAway;
 function sample(){
  const people=G.people.filter(alive),households=G.households.filter(h=>h.people.length),firms=G.firms.filter(f=>!f.closed),liquid=households.map(h=>householdLiquidity(h)/h.people.length),loans=G.loans.filter(l=>l.status==='active'),balances=goodsBalance(),trade=ensureRegionalTrade();
  return {day:G.day,elapsedYears:(G.day-start)/360,population:people.length,jobs:sum(firms,f=>f.jobs),employed:people.filter(p=>p.job>=0||p.publicWork).length,employment:G.stats.employment,hardship:G.stats.hardship,unmetFood:G.market.unmetFood,blockedCommutes:G.market.blockedCommutes,foodDisconnected:G.market.foodDisconnected,wages:sum(households,h=>h.wages),liquidityPerResident:{p10:quantile(liquid,.1),median:quantile(liquid,.5),p90:quantile(liquid,.9)},highStressHouseholds:households.filter(h=>h.stress>50).length,adultSkill:sum(people.filter(p=>p.age>=18),p=>p.skill)/Math.max(1,people.filter(p=>p.age>=18).length),education:G.education,health:G.health,publicLearning:G.civicTrainingCompletions||0,privateLearning:G.privateTrainingCompletions||0,schoolCoverage:G.serviceProvision?.school?.coverage||0,privatePupils:G.privateServiceProvision?.pupils||0,vouchers:G.privateServiceProvision?.vouchers||0,transit:JSON.parse(JSON.stringify(ensureTransit())),privateProviders:firms.filter(f=>f.privateService).map(f=>({id:f.id,kind:f.privateService,cash:f.cash,clients:f.clientsToday||0,profit:f.netProfit||0,staff:workingStaff(f).length})),births:totals.births,inMigration:totals.arrivals,outMigration:G.people.filter(p=>p.movedAway).length,deaths:G.people.filter(p=>p.deceased).length,businesses:firms.length,closedFirms:G.firms.filter(f=>f.closed).length,firmCash:sum(G.firms,f=>f.cash),firmNetProfit:sum(firms,f=>f.netProfit),treasury:G.treasury,municipalDebt:G.debt,regionCash:G.region,banks:G.banks.map(b=>({id:b.id,closed:b.closed,cash:b.cash,regionCredit:b.regionCredit||0,depositClaims:bankDeposits(b.id),equity:bankEquity(b),interestEarned:b.interestEarned,interestPaid:b.interestPaid,loanAPY:b.loanAPY,depositAPY:b.depositAPY})),activeLoanPrincipal:sum(loans,l=>l.balance),loanArrears:loans.filter(l=>l.arrears>0).length,defaults:{household:G.finance.householdDefaults||0,firm:G.finance.businessDefaults||0},prices:{...G.goodsPrices,cpi:G.market.cpi},goods:balances,cumulative:{...G.cumulative},foodProject:G.civicProjects?.active.food||null,contracts:trade.contracts.map(c=>({id:c.id,good:c.good,status:c.status,quantity:c.quantity,delivered:c.delivered})),shipments:trade.shipments.length,lateShipments:trade.shipments.filter(o=>o.due<G.day).length,cashDrift:totalMoney()-totals.money,goodsError:Math.max(0,...balances.map(r=>Math.abs(r.error))),valid:validateTown(),policy:{...G.policy},totals:{...totals}};
 }
 function policy(changes,label){Object.assign(G.policy,changes);recompute();actions.push({day:G.day,label,changes});}
 function invite(){for(const kind of ['school','fire'])actions.push({day:G.day,label:'Invite '+kind,result:seekPrivateServiceInvestment(kind)});}
 function foodProject(local){
  const shop=civicProjectGrocer();if(!shop){actions.push({day:G.day,label:'No trading grocer for food project'});return;}
  if(!civicProjectStart('food',local?'local':'bridge',shop.id))throw Error('Food project rejected');
  const before={treasury:G.treasury,region:G.region,firmCash:shop.cash};
  if(local)civicProjectReviewBuild('bakery','food');else civicProjectReviewFood();
  const choice=$('eventChoices').querySelector('button');if(pendingEvent&&choice)choice.click();
  actions.push({day:G.day,label:local?'Commission surveyed local bakery':'Place paid shop import bridge',before,after:{treasury:G.treasury,region:G.region,firmCash:shop.cash},project:JSON.parse(JSON.stringify(G.civicProjects.active.food))});
 }
 function bus(){
  const lot=buildableCandidates('business').find(c=>canPlace(c.x,c.y,true,'transit_depot'));
  const depot=lot&&buildTransitFacility('transit_depot',lot.x,lot.y);
  if(!depot){actions.push({day:G.day,label:'Bus depot unavailable at normal funding/placement constraints'});return;}
  const spec={mode:'bus',depot:depot.id,stops:[roadId(15,27),roadId(21,27),roadId(27,27),roadId(35,27),roadId(43,27)],level:1},quote=transitQuote(spec),route=buildTransitRoute(spec,quote);
  actions.push({day:G.day,label:'Buy one normally funded cross-town bus and depot; recruit only ordinary eligible staff',depot:depot.id,quote,route:route&&route.id});
 }
 function agreement(foodOnly){
  // Same actual DOM controls and forecast-sized choice as the exchange. No
  // injected stock, preferred producer or fabricated contract object.
  renderPanel('economy');const btn=$('panelBody').querySelector(foodOnly?'[data-trade-offer][data-trade-good=food]:not([disabled])':'[data-trade-offer]:not([disabled])');
  if(!btn){totals.noContractOffers++;return;}btn.click();
  const choice=$('eventChoices').querySelector('button');if(!pendingEvent||!choice)throw Error('Contract preview missing');
  const title=choice.textContent;choice.click();actions.push({day:G.day,label:'Exchange commitment',choice:title});
 }
 return {
 begin:(o)=>{if(!hydrateSave(o.saved))throw Error('Matched save rejected');paused=true;start=G.day;original={...G.policy};basePeople=G.people.length;actions=[];totals={money:totalMoney(),births:0,arrivals:0,unmetFood:0,hardshipResidentDays:0,blockedCommutes:0,firmClosures:0,treasuryEmptyDays:0,providerClosures:0,noContractOffers:0};
  const policies={baseline:{},'import-led':{imports:true,importTariff:0},'local-protected':{imports:true,importTariff:40},'credit-tight':{policyRate:18,lendingRules:90},'credit-recovery':{policyRate:18,lendingRules:90},'credit-late-recovery':{policyRate:18,lendingRules:90},'public-services':{privateServices:0,educationBudget:250,defenseBudget:250,serviceVoucherBudget:0},'private-services':{privateServices:1,educationBudget:0,defenseBudget:0,serviceVoucherBudget:0},'voucher-services':{privateServices:1,educationBudget:0,defenseBudget:0,serviceVoucherBudget:150},'education-investment':{educationBudget:250},'food-contracts':{},'wage-subsidy':{employmentSubsidy:15},'bus-investment':{},'import-bridge':{},'local-producer':{},'supplier-contracts':{}};
  if(!policies[o.mode])throw Error('Unknown mode');policy(policies[o.mode],o.mode);if(o.mode==='bus-investment')bus();if(o.mode==='local-producer'||o.mode==='import-bridge')foodProject(o.mode==='local-producer');if(o.mode.includes('private-services')||o.mode==='voucher-services')invite();return sample();},
 advance:(o)=>{for(let d=0;d<o.days;d++){
  if(pendingEvent)throw Error('Unexpected modal '+pendingEvent.title+' at day '+G.day);
  const elapsed=G.day-start;if((o.mode==='credit-recovery'&&elapsed===720)||(o.mode==='credit-late-recovery'&&elapsed===9000))policy({policyRate:original.policyRate,lendingRules:original.lendingRules},'Restore founding credit settings after '+(elapsed/360)+' years');
  if(elapsed%90===0&&elapsed>0&&(o.mode==='private-services'||o.mode==='voucher-services'))invite();
  if((o.mode==='food-contracts'||o.mode==='supplier-contracts')&&elapsed%30===0)agreement(o.mode==='food-contracts');
  const oldCount=G.people.length,closed=new Set(G.firms.filter(f=>f.closed).map(f=>f.id));tick();
  if(G.day===start+elapsed)throw Error('Clock did not advance');
  for(let i=oldCount;i<G.people.length;i++){if(G.people[i].age===0)totals.births++;else totals.arrivals++;}
  totals.unmetFood+=G.market.unmetFood||0;totals.hardshipResidentDays+=(G.stats.hardship||0)/100*G.stats.population;totals.blockedCommutes+=G.market.blockedCommutes||0;
  totals.treasuryEmptyDays+=Number(G.treasury<1);for(const f of G.firms)if(f.closed&&!closed.has(f.id)){totals.firmClosures++;if(f.privateService)totals.providerClosures++;}
 }return sample();},actions:()=>actions
 };
})();
'''
MODES = ['baseline','local-protected','credit-tight','credit-recovery','credit-late-recovery','public-services','private-services','voucher-services','education-investment','food-contracts','wage-subsidy','bus-investment','import-bridge','local-producer','supplier-contracts']

def write_json(path, value):
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,indent=2)+'\n')
    temporary.replace(path)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--years',type=int,default=30)
    parser.add_argument('--seeds',default='42,101,909')
    parser.add_argument('--modes',default=','.join(MODES))
    parser.add_argument('--warmup',type=int,default=360)
    parser.add_argument('--out',default='reports/balance-lab')
    parser.add_argument('--resume',action='store_true',help='Skip complete compatible histories and retain interrupted attempts')
    args=parser.parse_args()
    if args.years<1 or args.warmup<0:parser.error('years must be positive and warmup nonnegative')
    unknown=set(args.modes.split(','))-set(MODES)-{'import-led'}
    if unknown:parser.error('Unknown modes: '+', '.join(sorted(unknown)))
    source=(ROOT/'assets/game.js').read_bytes();digest=hashlib.sha256(source).hexdigest()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True)
    metadata={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':digest,'args':vars(args),'method':'Matched normal settlement after warmup. Policies are simulation-level legal counterfactuals, provider invitations use normal viability function, contracts use actual exchange controls. No grants, forced staff, injected goods or annexations. Bus and food-investment arms make normal paid construction/order purchases. Autonomous development remains enabled. Existing private incumbents and previously commissioned projects are preserved when new licensing stops. 360-day game years. Initial people retain ordinary skills/wealth. Random streams diverge after intervention; paths are model comparisons, not isolated real-world causal estimates.','limits':['Imports arm retains ordinary local sourcing; protected-local arm uses maximum legal tariff and does not guarantee self-sufficiency.','No authored transit network: commuter support alone is not evidence of paid bus/rail effects. Separate transit-owner fixture required.','No auto-approved council choices: a surprise modal stops and retains the negative outcome.','Death and outward-migration sample counts include warmup; births and arrivals count only intervention period.', 'Daily derived service reports clear on archive restore; use day-30 onward coverage rather than initial zero reports.','No score or fun assertion; evidence concerns constraints, trajectories and decision consequences.']}
    write_json(out/'manifest.json',metadata)
    rows=[]
    if args.resume and (out/'runs.json').exists():
        prior=json.loads((out/'runs.json').read_text())
        if prior['metadata']['source_sha256']!=digest or prior['metadata']['args']['warmup']!=args.warmup:
            raise RuntimeError('Cannot resume a different production source or warmup')
        rows=prior['rows']
        for row in rows:
            if row['status']=='running':row['status']='interrupted';row['failure']='Run intentionally stopped to distribute independent seeds across three processes; partial samples retained.'
    started=time.monotonic()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page();page.set_default_timeout(120000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html);page.add_script_tag(content=source.decode().replace('// SOURCE: 99-instrumentation.js',PROBE+'\n// SOURCE: 99-instrumentation.js'));page.locator('#newTown').click();page.locator('#pause').click()
        for seed in map(int,args.seeds.split(',')):
            page.evaluate('o=>{__townTest.reset("settlement",o.seed);__townTest.step(o.days)}',{'seed':seed,'days':args.warmup})
            saved=page.evaluate('__townTest.save()');state_hash=hashlib.sha256(saved.encode()).hexdigest()
            for mode in args.modes.split(','):
                if any(r['seed']==seed and r['mode']==mode and r['status']=='complete' and r['samples'][-1]['elapsedYears']>=args.years for r in rows):continue
                row={'seed':seed,'mode':mode,'matched_save_sha256':state_hash,'samples':[],'status':'running'};rows.append(row);begin=time.monotonic()
                try:
                    row['initial']=page.evaluate('o=>__balanceLab.begin(o)',{'mode':mode,'saved':saved})
                    elapsed=0
                    intervals=[30]*12+[360]*(args.years-1)
                    for days in intervals:
                        # Yield to the browser between chunks; inference is idle during tick work.
                        elapsed+=days;year=elapsed/360
                        sample=page.evaluate('o=>__balanceLab.advance(o)',{'mode':mode,'days':days})
                        row['samples'].append(sample)
                        if not sample['valid']['ok'] or abs(sample['cashDrift'])>.1 or sample['goodsError']>.01:
                            raise RuntimeError('Invariant failure: '+json.dumps({k:sample[k] for k in ['valid','cashDrift','goodsError']}))
                        if hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()!=digest:raise RuntimeError('Production bundle changed during experiment')
                        write_json(out/'runs.json',{'metadata':metadata,'rows':rows,'pageErrors':errors})
                        if year in [1,3,10,20,30]:print(seed,mode,'year',year,'population',sample['population'],'employment',sample['employment'],'hardship',sample['hardship'],'treasury',round(sample['treasury']),'debt',round(sample['municipalDebt']),flush=True)
                    row['status']='complete'
                except Exception as error:
                    row['status']='failed';row['failure']=str(error);print('RETAINED FAILURE',seed,mode,str(error)[:400],flush=True)
                row['actions']=page.evaluate('__balanceLab.actions()');row['seconds']=time.monotonic()-begin
                write_json(out/'runs.json',{'metadata':metadata,'rows':rows,'pageErrors':errors})
        browser.close()
    print('Finished',len(rows),'histories in',round(time.monotonic()-started,1),'seconds;',sum(r['status']=='failed' for r in rows),'retained failures',flush=True)
if __name__=='__main__':main()
