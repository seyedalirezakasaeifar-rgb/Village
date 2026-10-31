#!/usr/bin/env python3
"""Source-bound matched funding/credit histories; production is never edited."""
from pathlib import Path
import hashlib, json, os, subprocess, sys
from playwright.sync_api import sync_playwright
from soak_migration_causality import PROBE
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html

EXTRA=r'''
window.__matched=(()=>{
 let start=0,credit={};
 const quantile=(xs,q)=>xs.length?xs.slice().sort((a,b)=>a-b)[Math.floor((xs.length-1)*q)]:0;
 function detail(){const hh=G.households.filter(h=>h.people.length),firms=G.firms.filter(f=>!f.closed),alive=G.people.filter(p=>!p.deceased&&!p.movedAway),wealth=hh.map(h=>migrationSpendable(h).spendable),cash=hh.map(h=>h.cash),wages=firms.map(f=>f.wage),homes=G.buildings.filter(b=>housingUnitCapacity(b)>0);return {migration:migrationDiagnostics(),populationIdentity:alive.length,under18:alive.filter(p=>p.age<18).length,over70:alive.filter(p=>p.age>70).length,walletQuartiles:[0,.25,.5,.75,1].map(q=>quantile(cash,q)),spendableQuartiles:[0,.25,.5,.75,1].map(q=>quantile(wealth,q)),lockedDeposits:hh.reduce((n,h)=>n+migrationSpendable(h).locked,0),wageQuartiles:[0,.5,1].map(q=>quantile(wages,q)),householdStressMean:hh.reduce((n,h)=>n+h.stress,0)/Math.max(1,hh.length),firmCash:firms.reduce((n,f)=>n+f.cash,0),insolventFirms:firms.filter(f=>f.cash<0).length,closedFirms:G.firms.filter(f=>f.closed).length,loans:G.loans.map(l=>({ownerType:l.ownerType,principal:l.principal,balance:l.balance,arrears:l.arrears,defaulted:l.defaulted})),availableHousingUnits:homes.reduce((n,b)=>n+migrationHousingStatus(b).available,0),outsideReference:migrationOutsideReference(2,2)};}
 return {begin:o=>{const state=__migrationLedger.begin(o);start=G.day;credit={policyRate:G.policy.policyRate,lendingRules:G.policy.lendingRules};return {...state,detail:detail()};},advance:o=>{const elapsed=G.day-start;if(o.strategy==='credit-recovery')Object.assign(G.policy,elapsed<360?{policyRate:18,lendingRules:90}:credit);const state=__migrationLedger.advance({days:30,strategy:o.strategy==='passive'?'passive':'service-oriented'});return {...state,detail:detail(),creditPhase:o.strategy==='credit-recovery'?(elapsed<360?'tight':'restored'):'unchanged'};}};
})();
'''

def write(path,obj):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,indent=2)+'\n');tmp.replace(path)

def main():
    out=ROOT/'reports/migration-matched';out.mkdir(parents=True,exist_ok=True)
    source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
    probe=PROBE.replace("__townTest.reset('settlement',o.seed)","__townTest.reset(o.scenario,o.seed)")
    result={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':sha,'method':'Two seeds, settlement and regional starts. Identical one-year natural warmup. Three subsequent years: passive; monthly legal service authorizations; same service authorizations with legal 18% rate/90 lending rules for year one, then restored opening credit policy for two years. No grants, workforce edits, bank cash edits, forced events, or production coefficients changed. Source-hook demographic identity and exclusive treasury ledger. Outside alternative is a labelled founding-policy reference, not a simulated foreign city.','rows':[]}
    with sync_playwright()as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage']);page=browser.new_page();page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);page.add_script_tag(content=source.decode().replace('// SOURCE: 99-instrumentation.js',probe+'\n'+EXTRA+'\n// SOURCE: 99-instrumentation.js'));page.locator('#newTown').click();page.locator('#pause').click()
        for scenario in ['settlement','regional']:
            for seed in [42,101]:
                opening_hash=None
                for strategy in ['passive','services','credit-recovery']:
                    row={'scenario':scenario,'seed':seed,'strategy':strategy,'samples':[],'status':'running'};result['rows'].append(row)
                    try:
                        row['initial']=page.evaluate('o=>__matched.begin(o)',{'scenario':scenario,'seed':seed})
                        saved=page.evaluate('__townTest.save()');row['starting_save_sha256']=hashlib.sha256(saved.encode()).hexdigest()
                        if opening_hash is None:opening_hash=row['starting_save_sha256']
                        assert row['starting_save_sha256']==opening_hash,'Mismatched starting archive'
                        for month in range(36):
                            sample=page.evaluate('o=>__matched.advance(o)',{'strategy':strategy});row['samples'].append(sample)
                            assert sample['valid']['ok'],sample['valid']
                            assert abs(sample['cashDrift'])<.1 and sample['goodsError']<.01 and abs(sample['treasuryReconciliation'])<.01,'Financial invariant'
                            assert not any(sample['counts'][k] for k in ['invalidHomeDays','unregisteredHouseholdDays','overCapacityBuildingDays']),'Tenancy invariant'
                            assert sample['population']==sample['detail']['populationIdentity'],'Population recomputation'
                            write(out/'histories.json',result)
                        row['status']='complete'
                    except Exception as e:row['status']='failed';row['failure']=str(e)
                    row['events']=page.evaluate('__migrationLedger.finish()');write(out/'histories.json',result)
                    last=row['samples'][-1]if row['samples']else row['initial'];print(scenario,seed,strategy,row['status'],'pop',last['population'],'treasury',round(last['treasury']),'education',round(last['education'],2),'counts',last['counts'],flush=True)
        result['pageErrors']=errors;write(out/'histories.json',result);browser.close()
    assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha,'Production source changed during experiment'
    assert all(r['status']=='complete'for r in result['rows'])and not result['pageErrors']
    summary={k:result[k]for k in ['source_commit','source_sha256','method']};summary['rows']=[]
    for row in result['rows']:
        a=row['initial'];b=row['samples'][-1]
        observed={k:b['detail']['migration']['sessionCounts'][k]-a['detail']['migration']['sessionCounts'][k]for k in ['births','immigration','deaths','emigration']}
        assert all(observed[k]==b['counts'][k]for k in observed),'UI observer differs from independent source ledger'
        assert b['population']==a['population']+observed['births']+observed['immigration']-observed['deaths']-observed['emigration']
        summary['rows'].append({k:row[k]for k in ['scenario','seed','strategy','starting_save_sha256']}|{'initial':a,'annualSamples':[row['samples'][i]for i in [11,23,35]],'maximumAbsoluteCashDrift':max(abs(y['cashDrift'])for y in row['samples']),'maximumGoodsError':max(y['goodsError']for y in row['samples']),'maximumTreasuryReconciliationError':max(abs(y['treasuryReconciliation'])for y in row['samples']),'observerCountsMatchSourceLedger':True})
    write(out/'summary.json',summary)

if __name__=='__main__':main()
