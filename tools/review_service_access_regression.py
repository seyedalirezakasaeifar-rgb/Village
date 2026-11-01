"""Reproduce public-pass / district-fail / isolated-fix-pass using immutable source refs."""
import contextlib,hashlib,io,json,re,subprocess,tarfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
BASE='848bf1bfb8fdddc3155ba5a7773348d28073ade4';DISTRICT='ff837b3eabb921ced2b5266d8a009cea8bbfdeb2';FIX='ff9f0d067aef13978b8a07c11ef91f4b2c673d68'
def blob(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT,text=True)
with tarfile.open(fileobj=io.BytesIO(subprocess.check_output(['git','archive',BASE,'src'],cwd=ROOT)))as bundle:modules={Path(m.name).name:bundle.extractfile(m).read().decode()for m in bundle.getmembers()if m.isfile()and m.name.endswith('.js')}
retail=modules['27-urban-evolution.js'];retail=retail[retail.index('function urbanRetailProposal('):retail.index('function urbanEvolutionDay(')]
for name in ['10-finance.js','27-urban-evolution.js','30-economy.js','50-clock.js','98-urban-ui.js']:modules[name]=blob(DISTRICT,'src/'+name)
s=modules['27-urban-evolution.js'];modules['27-urban-evolution.js']=s[:s.index('function urbanRetailProposal(')]+retail+s[s.index('function urbanEvolutionDay('):]
def assemble():
 output='\n'.join('// SOURCE: '+name+'\n'+modules[name]for name in sorted(modules));metadata=json.loads(blob(BASE,'release.json'));return re.sub(r'const RELEASE=Object.freeze\(\{[^\n]+\}\);','const RELEASE=Object.freeze('+json.dumps(metadata,separators=(',',':'))+');',output,count=1)
unsafe=assemble();assert hashlib.sha256(unsafe.encode()).hexdigest()=='49acb7517a496cb5febc7535af6143fc36e79f58a8b7451cc87d4929af87d69e'
modules['12-service-access.js']=blob(FIX,'src/12-service-access.js');fixed=assemble();assert hashlib.sha256(fixed.encode()).hexdigest()=='3af2f8355807bfa3c23482b25816f657ae618970dfeb4e38dc6c34aa3140115c'
def changes(a,b,path=''):
 if type(a)!=type(b):return [{'path':path,'before':a,'after':b}]
 if isinstance(a,dict):return sum((changes(a.get(k),b.get(k),path+'.'+k)for k in a.keys()|b.keys()),[])
 if isinstance(a,list):return [{'path':path,'beforeLength':len(a),'afterLength':len(b)}]if len(a)!=len(b)else sum((changes(x,y,path+'.'+str(i))for i,(x,y)in enumerate(zip(a,b))),[])
 return []if a==b else[{'path':path,'before':a,'after':b}]
code=blob(BASE,'tests/test_retail_proposal_review.py').replace("source=(ROOT/'assets/game.js').read_text()",'source=SOURCE_OVERRIDE').replace("assert page.evaluate('__townTest.save()')==continuation","replayed=page.evaluate('__townTest.save()');REPLAY_DIFFS=changes(json.loads(continuation),json.loads(replayed));assert replayed==continuation")
result={'base':BASE,'district':DISTRICT,'isolatedServiceFix':FIX,'growthRuntimeIncluded':False,'cases':[]}
for label,source in [('acceptedPublic',blob(BASE,'assets/game.js')),('districtBeforeFix',unsafe),('fixedComposition',fixed)]:
 namespace={'SOURCE_OVERRIDE':source,'changes':changes};status='passed'
 try:
  with contextlib.redirect_stdout(io.StringIO()):exec(compile(code,'immutable-retail-review','exec'),namespace)
 except AssertionError:status='assertionFailed'
 result['cases'].append({'label':label,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'status':status,'allReplayDifferences':namespace.get('REPLAY_DIFFS')})
assert [c['status']for c in result['cases']]==['passed','assertionFailed','passed'],result
assert len(result['cases'][1]['allReplayDifferences'])==9 and result['cases'][0]['allReplayDifferences']==result['cases'][2]['allReplayDifferences']==[],result
print(json.dumps(result,indent=2))
