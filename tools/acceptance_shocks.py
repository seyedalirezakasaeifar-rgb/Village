"""Bounded synthetic shocks, real operating rules and paid recovery."""
import sys,json,hashlib,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from soak_migration_causality import PROBE
SETUP="""G.policy.educationBudget=0;G.policy.defenseBudget=0;G.policy.serviceVoucherBudget=100;seekPrivateServiceInvestment('school');__townTest.step(120);seekPrivateServiceInvestment('fire');__townTest.step(120);"""
EXTRA=r'''
window.__shock=(()=>{let start,old,roads=[],bank,trace=[];const remember=logisticsRemember;logisticsRemember=function(o,status){trace.push({day:G.day,id:o.id,firm:o.firm,mode:o.mode||'road',status,qty:o.qty});return remember(o,status)};
function funded(){const p=G.stats.population,w=Math.max(24,G.policy.minWage);Object.assign(G.policy,{educationBudget:Math.ceil(p*10/260*w/.65),healthBudget:Math.ceil(p*5/350*w/.65),defenseBudget:140,policeBudget:180,roadBudget:25,serviceVoucherBudget:100});}
function sample(){return {finance:{...G.finance},banks:G.banks.map(b=>({id:b.id,closed:b.closed,cash:b.cash,claims:bankDeposits(b.id)})),loans:G.loans,providers:G.firms.filter(f=>f.privateService).map(f=>({id:f.id,kind:f.kind,cash:f.cash,closed:!!f.closed,clients:f.clientsToday})),cargo:G.regionalTrade.shipments.length,claims:G.regionalTrade.claims,deliveries:G.regionalTrade.delivered,migration:migrationDiagnostics(),negativeWallets:G.households.filter(h=>h.cash<-.001).length};}
return {begin:o=>{const initial=__migrationLedger.begin(o);start=G.day;old={...G.policy};trace=[];roads=[];bank=null;return {initial,detail:sample()};},advance:o=>{const elapsed=G.day-start;if(elapsed===0){funded();if(o.mode==='bank'){G.policy.policyRate=20;G.policy.lendingRules=100;bank=G.banks.filter(b=>!b.closed).sort((a,b)=>bankDeposits(b.id)-bankDeposits(a.id))[0];liquidateBank(bank,'Controlled receivership; not an inferred natural insolvency');}if(o.mode==='road'){const s=ensureRegionalTrade(),m=OUTSIDE_MARKETS.find(m=>m.id==='port'),f=G.firms.find(f=>f.kind==='grocer'),w=G.firms.find(f=>f.kind==='wharf'&&!f.closed);for(const depot of [w?.id,-1]){const q=regionalQuote(f,m,'food','import',depot);if(q)dispatchRegional(f,'food',60,'import',q);}for(let y=0;y<T;y++){const id=y*T+8;if(G.tiles[id]===1){roads.push({x:8,y});G.tiles[id]=0;}}invalidateRoads(false);}}
if(o.mode==='services'&&elapsed<180)Object.assign(G.policy,{educationBudget:0,healthBudget:0,defenseBudget:0,policeBudget:0,serviceVoucherBudget:0,roadBudget:0});else if(elapsed%30===0)funded();
if(o.mode==='bank'&&elapsed===180){G.policy.policyRate=old.policyRate;G.policy.lendingRules=old.lendingRules;}
if(o.mode==='road'&&elapsed===60){for(const r of roads)construct('road',r.x,r.y,true);flushRoadBatch();}
const state=__migrationLedger.advance({days:30,strategy:'passive'});return {...state,detail:sample()};},finish:()=>({trace,roads,ledger:__migrationLedger.finish(),roundTrip:hydrateSave(archivePayload())})};})();
'''
def main():
 out=ROOT/'reports/shocks';out.mkdir(parents=True,exist_ok=True);source=(ROOT/'assets/game.js').read_bytes();report={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'source_sha256':hashlib.sha256(source).hexdigest(),'rows':[]}
 probe=PROBE.replace('__townTest.step(360);paused=true;',SETUP+'paused=true;').replace('const birthBase=',"construct=moneyWrap('capital:paid-road-recovery',construct);liquidateBank=moneyWrap('finance:controlled-receivership',liquidateBank);const birthBase=")
 with sync_playwright()as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_default_timeout(180000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.decode().replace('// SOURCE: 99-instrumentation.js',probe+EXTRA+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
  for seed in [42,101]:
   for mode in ['baseline','bank','services','road']:
    row={'seed':seed,'mode':mode,'samples':[]};report['rows'].append(row)
    try:
     row['opening']=p.evaluate('o=>__shock.begin(o)',{'seed':seed})
     for month in range(18):
      x=p.evaluate('o=>__shock.advance(o)',{'mode':mode});row['samples'].append(x)
      assert x['valid']['ok']and abs(x['cashDrift'])<.1 and x['goodsError']<.01
      assert not any(x['counts'][k]for k in ['invalidHomeDays','unregisteredHouseholdDays','overCapacityBuildingDays'])
      (out/'results.json').write_text(json.dumps(report,indent=2))
     row['finish']=p.evaluate('__shock.finish()');assert row['finish']['roundTrip'];row['status']='complete'
    except Exception as e:row['status']='failed';row['failure']=str(e)
    print(seed,mode,row['status'],flush=True);(out/'results.json').write_text(json.dumps(report,indent=2))
  report['errors']=errors;b.close()
 (out/'results.json').write_text(json.dumps(report,indent=2));assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==report['source_sha256']
if __name__=='__main__':main()
