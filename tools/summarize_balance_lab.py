#!/usr/bin/env python3
"""Summarize completed and failed balance histories without selecting only wins."""
from pathlib import Path
import argparse, gzip, hashlib, json, statistics
ROOT=Path(__file__).resolve().parents[1]
FIELDS=['population','employment','hardship','treasury','municipalDebt','adultSkill','firmCash','activeLoanPrincipal','businesses','privatePupils','schoolCoverage']
PAIRS=[('local-protected','baseline'),('credit-tight','baseline'),('credit-recovery','credit-tight'),('public-services','baseline'),('private-services','public-services'),('voucher-services','private-services'),('education-investment','baseline'),('food-contracts','baseline'),('wage-subsidy','baseline')]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('inputs',nargs='+');p.add_argument('--out',default='reports/balance-lab-summary');args=p.parse_args()
 inputs=[ROOT/x for x in args.inputs];out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True)
 sources=[json.loads(x.read_text()) for x in inputs]
 assert len({s['metadata']['source_sha256'] for s in sources})==1,'Cannot compare different production sources'
 rows=[r for s in sources for r in s['rows']];complete=[r for r in rows if r['status']=='complete'];failed=[r for r in rows if r['status']!='complete']
 keys=[(r['seed'],r['mode']) for r in complete];assert len(keys)==len(set(keys)),'Duplicate complete histories'
 aggregate=[];contrasts=[]
 for year in [1/12,1/3,1,3,10,30]:
  for mode in sorted({r['mode'] for r in complete}):
   selected=[(r,next((s for s in r['samples'] if abs(s['elapsedYears']-year)<1e-6),None)) for r in complete if r['mode']==mode];selected=[(r,s) for r,s in selected if s]
   if not selected:continue
   aggregate.append({'years':year,'mode':mode,'seeds':[r['seed'] for r,s in selected],'mean':{k:statistics.mean(s[k] for r,s in selected) for k in FIELDS},'range':{k:[min(s[k] for r,s in selected),max(s[k] for r,s in selected)] for k in FIELDS},'maximumCashDrift':max(abs(s['cashDrift']) for r,s in selected),'maximumGoodsError':max(s['goodsError'] for r,s in selected)})
  for treatment,control in PAIRS:
   pairs=[]
   for seed in sorted({r['seed'] for r in complete}):
    a=next((r for r in complete if r['seed']==seed and r['mode']==treatment),None);b=next((r for r in complete if r['seed']==seed and r['mode']==control),None)
    if not a or not b:continue
    sa=next((s for s in a['samples'] if abs(s['elapsedYears']-year)<1e-6),None);sb=next((s for s in b['samples'] if abs(s['elapsedYears']-year)<1e-6),None)
    if sa and sb:pairs.append({'seed':seed,'matchedSource':a['matched_save_sha256']==b['matched_save_sha256'],'delta':{k:sa[k]-sb[k] for k in FIELDS}})
   if pairs:contrasts.append({'years':year,'treatment':treatment,'control':control,'paired':pairs,'meanDelta':{k:statistics.mean(r['delta'][k] for r in pairs) for k in FIELDS}})
 summary={'production_sha256':sources[0]['metadata']['source_sha256'],'production_commit':sources[0]['metadata']['source_commit'],'completeHistories':len(complete),'otherOutcomes':[{'seed':r['seed'],'mode':r['mode'],'status':r['status'],'failure':r.get('failure'),'lastYears':r['samples'][-1]['elapsedYears'] if r['samples'] else 0} for r in failed],'aggregate':aggregate,'pairedContrasts':contrasts,'inputs':[{'path':str(x.relative_to(ROOT)),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in inputs]}
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 with gzip.GzipFile(filename=str(out/'full-evidence.json.gz'),mode='wb',mtime=0) as f:f.write(json.dumps(sources,separators=(',',':')).encode())
 lines=['# Balance laboratory observations','',f"Production commit `{summary['production_commit']}`; game SHA-256 `{summary['production_sha256']}`.",'',f"{len(complete)} completed histories. {len(failed)} other outcomes are retained in the evidence. No production coefficients changed.",'','Normal settlement, three requested seeds, matched one-year warmup; 360-day years. Legal policy interventions and normal viability-based provider invitations. Food agreements use actual exchange buttons and their first forecast-sized choice. No financial grants, injected goods, forced workers, mandatory annexations or fabricated network. Autonomous investment remains enabled. Counterfactual random paths diverge after interventions. These are model outcomes, not human playtesting or calibrated policy effects.','', '| Years | Policy | Seeds | Population | Employment % | Hardship % | Treasury | Debt |', '|---:|---|---:|---:|---:|---:|---:|---:|']
 for a in aggregate:
  if a['years'] not in [10,30]:continue
  m=a['mean'];lines.append(f"| {a['years']} | {a['mode']} | {len(a['seeds'])} | {m['population']:.1f} | {m['employment']:.1f} | {m['hardship']:.1f} | {m['treasury']:,.0f} | {m['municipalDebt']:,.0f} |")
 lines+=['','## Retained limits','','These interventions do not author a new local-production/export district or paid transport network. Tariff protection is a sourcing incentive, not proof of a fully local supply chain. Contracts are normal food supplier opportunities, not all commodity agreements. Separate urban and transit owners cover placement, relocation and passenger routing/capacity; those effects cannot be inferred from the legacy commuter budget.','','Private and public school coverage use different resident/learner denominators. Compare paid learners, learning completions and household distribution alongside either index. Initial service reports are cleared during matched archive restore; use day-30 onward snapshots. Births and inward arrivals are detected from actual new resident identities; deaths/outward migration include the warmup and should be differenced against initial counts. External commodity flows are cumulative ledger quantities. Regional cash changes are net external financial flows, not gross trade-dollar turnover.','','Full annual/monthly samples retain conservation, defaults, household liquidity quantiles, births/deaths/migration, prices, firms and public/private provision. No test result certifies fun, physical Android FPS or a real-world economic claim.']
 (out/'OBSERVATIONS.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:summary[k] for k in ['production_commit','production_sha256','completeHistories','otherOutcomes']},indent=2))
if __name__=='__main__':main()
