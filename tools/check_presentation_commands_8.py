"""Run real command acceptance on both sources and compare complete model/RNG.
Only the two explicit visual transport fields are excluded from final snapshots.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
original=Path.read_text;variants={'base':subprocess.check_output(['git','show','6e8665e:assets/game.js'],cwd=ROOT,text=True),'candidate':original(ROOT/'assets/game.js')};rows=[]
for test in ['test_civic_calendar.py','test_brownfield_renewal.py','test_procurement.py']:
 states={}
 for name,source in variants.items():
  def read(path,*args,**kwargs):return source if path.resolve()==(ROOT/'assets/game.js').resolve() else original(path,*args,**kwargs)
  Path.read_text=read
  path=ROOT/'tests'/test;code=original(path);code=code.replace('b.close()',"__commandSnapshot=json.loads(p.evaluate('__townTest.save()'));b.close()")
  scope={'__file__':str(path),'__name__':'__main__'}
  try:exec(compile(code,str(path),'exec'),scope)
  finally:Path.read_text=original
  model=scope['__commandSnapshot'];model.pop('trafficState',None);model.pop('visualState',None);states[name]=model
 if states['base']!=states['candidate']:
  differences=[k for k in states['base'] if states['base'].get(k)!=states['candidate'].get(k)];raise AssertionError((test,differences))
 rows.append({'test':test,'completeModelAndRngEqual':True,'day':states['base']['day'],'rngState':states['base']['rngState']});print('EXACT',test,flush=True)
out=ROOT/'reports/presentation-repeat';out.mkdir(exist_ok=True);(out/'commands.json').write_text(json.dumps({'sourceHashes':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in variants.items()},'excludedFields':['trafficState','visualState'],'rows':rows},indent=2)+'\n')
