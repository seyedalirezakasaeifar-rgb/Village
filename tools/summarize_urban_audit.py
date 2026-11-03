"""Summarize fixed-income cohorts, actual relocation, retail and district events."""
from pathlib import Path
import json,gzip,statistics,sys
folder=Path(sys.argv[1]);data=json.loads((folder/'audit.json').read_text());summary={'source_sha256':data['source_sha256'],'scenario':data['scenario'],'years':data['years'],'runs':[]}
def median(a):return statistics.median(a) if a else 0
def cohorts(samples):
 first=sorted(samples[0]['households'],key=lambda h:(h['income']/h['people'],h['id']));n=max(1,len(first)//4);groups={'initialLowerIncome':{h['id'] for h in first[:n]},'initialHigherIncome':{h['id'] for h in first[-n:]}}
 result={}
 for name,ids in groups.items():
  rows=[]
  for s in samples:
   hs=[h for h in s['households'] if h['id'] in ids];people=sum(h['people'] for h in hs)
   rows.append({'day':s['day'],'survivingHouseholds':len(hs),'people':people,'afterTaxIncomePerPerson':sum(h['income'] for h in hs)/max(1,people),'medianLiquidPerPerson':median([h['liquid']/h['people'] for h in hs]),'medianRentBurden':median([h['rent']/max(1,h['income']) for h in hs]),'schoolCoverage':sum(h['school']*h['people'] for h in hs)/max(1,people),'medianStress':median([h['stress'] for h in hs]),'movedHouseholds':sum(bool(h['relocated']) for h in hs)})
  result[name]={'householdIds':sorted(ids),'first':rows[0],'last':rows[-1],'annual':[s for i,s in enumerate(rows) if i%4==3]}
 return result
for run in data['runs']:
 samples=run['samples'];first,last=samples[0],samples[-1];previous={};moves=0;characters={};changes=[];minGap=None;farms={};farmMoves=[]
 for s in samples:
  for h in s['households']:
   if h['id'] in previous and previous[h['id']]!=h['home']:moves+=1
   previous[h['id']]=h['home']
  for key,d in s['districts'].items():
   if key in characters and characters[key]['character']!=d['character']:
    old=characters[key];gap=d['changed']-old['changed'];minGap=gap if minGap is None else min(minGap,gap);changes.append({'key':key,'day':d['changed'],'from':old['character'],'to':d['character'],'gapFromPriorCharacter':gap})
   characters[key]=d
  for f in s['farms']:
   if f['id'] in farms and (f['x'],f['y'])!=(farms[f['id']]['x'],farms[f['id']]['y']):farmMoves.append({'id':f['id'],'recorded':f['relocated'],'sampled':s['day'],'priorFields':farms[f['id']]['fields'],'fields':f['fields'],'densityBefore':farms[f['id']]['density'],'densityAfter':f['density']})
   farms[f['id']]=f
 rawfile=folder/f"{data['scenario']}-{run['seed']}-{run['arm']}.json.gz";g=json.loads(gzip.decompress(rawfile.read_bytes())) if rawfile.exists() else None
 sources={}
 if g:
  byid={h['id']:h for h in g['households']}
  for key,cohort in cohorts(samples).items():
   hs=[byid[i] for i in cohort['householdIds'] if i in byid and byid[i]['people']];sources[key]={field:sum(h.get(field,0) or 0 for h in hs) for field in ['wages','pension','rentalIncome','dividends','aid','rent','privateServiceFees']}
 entry={'seed':run['seed'],'arm':run['arm'],'quarters':len(samples),'firstDay':first['day'],'finalDay':last['day'],'population':last['population'],'treasury':last['treasury'],'debt':last['debt'],'employment':last['employment'],'hardship':last['hardship'],'school':last['school'],'health':last['health'],'annexed':last['owned'],'deedSpend':last['landPurchases'],'actions':run['actions'],'malls':[],'smallRetail':{'initialOpen':sum(not f['closed'] for f in first['retail'] if not f['mall']),'finalOpen':sum(not f['closed'] for f in last['retail'] if not f['mall']),'closedRecords':sum(f['closed'] for f in last['retail'] if not f['mall'])},'observedHouseholdMoves':moves,'districtCharacterChanges':changes,'minimumObservedCharacterGapDays':minGap,'farmRelocations':farmMoves,'cohorts':cohorts(samples),'finalIncomeSources':sources,'moneyError':last['valid']['total']-first['valid']['total'],'parcels':last.get('parcels',[])}
 mallids=sorted({f['id'] for s in samples for f in s['retail'] if f['mall']})
 for id in mallids:
  history=[{'day':s['day'],**next(f for f in s['retail'] if f['id']==id)} for s in samples if any(f['id']==id for f in s['retail'])];entry['malls'].append({'id':id,'observedQuarters':len(history),'zeroStaffQuarters':sum(not h['staff'] for h in history),'closed':history[-1]['closed'],'last':history[-1],'negativeProfitQuarters':sum((h['net'] or 0)<0 for h in history)})
 summary['runs'].append(entry)
(folder/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for r in summary['runs']:
 print(r['seed'],r['arm'],'day',r['finalDay'],'pop',r['population'],'malls',len(r['malls']),'emptyMallQuarters',sum(m['zeroStaffQuarters'] for m in r['malls']),'smallRetail',r['smallRetail'],'moves',r['observedHouseholdMoves'],'farmMoves',len(r['farmRelocations']),'districtChanges',len(r['districtCharacterChanges']),'deeds',len(r['annexed']),'school',round(r['school'],3),'health',round(r['health'],3))
