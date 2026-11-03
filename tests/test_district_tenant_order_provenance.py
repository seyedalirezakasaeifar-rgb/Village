"""Paired natural 20-year archives expose every cold difference and its public provenance."""
import json,hashlib,subprocess,re
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
BASE='848bf1bfb8fdddc3155ba5a7773348d28073ade4';base=subprocess.check_output(['git','show',BASE+':assets/game.js'],cwd=ROOT,text=True);current=(ROOT/'assets/game.js').read_text()
def changes(a,b,path=''):
 if type(a)!=type(b):return [{'path':path,'before':a,'after':b}]
 if isinstance(a,dict):
  result=[]
  for key in a.keys()|b.keys():
   if key not in a or key not in b:result.append({'path':path+'.'+key,'before':a.get(key),'after':b.get(key)})
   else:result+=changes(a[key],b[key],path+'.'+key)
  return result
 if isinstance(a,list):
  if len(a)!=len(b):return [{'path':path,'beforeLength':len(a),'afterLength':len(b)}]
  return sum((changes(x,y,path+'.'+str(i))for i,(x,y)in enumerate(zip(a,b))),[])
 return []if a==b else[{'path':path,'before':a,'after':b}]
result={'base':BASE,'base_sha256':hashlib.sha256(base.encode()).hexdigest(),'source_sha256':hashlib.sha256(current.encode()).hexdigest(),'cases':[]};pages=[]
with sync_playwright()as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for label,source in [('base',base),('candidate',current)]:
  p=browser.new_page();p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42);__townTest.step(7200)");raw=p.evaluate('__townTest.save()');before=json.loads(raw);assert p.evaluate('x=>__townTest.load(x)',raw);canonical=p.evaluate('__townTest.save()');after=json.loads(canonical);assert p.evaluate('x=>__townTest.load(x)',canonical);assert json.loads(p.evaluate('__townTest.save()'))==after;diff=changes(before,after);row={'label':label,'day':before['day'],'population':before['stats']['population'],'before_sha256':hashlib.sha256(raw.encode()).hexdigest(),'canonical_sha256':hashlib.sha256(canonical.encode()).hexdigest(),'all_initial_cold_differences':diff,'moneyBefore':sum(before[k]for k in ['treasury','region']),'normalizationIdempotent':True,'financialArraysUnchanged':all(before[k]==after[k]for k in ['households','people','firms','banks','investors','loans','freight','regionalTrade','accounts','transactions']),'rngUnchanged':before['rngState']==after['rngState']};print(json.dumps(row),flush=True)
  p.evaluate('__townTest.step(30)');first=json.loads(p.evaluate('__townTest.save()'));assert p.evaluate('x=>__townTest.load(x)',canonical);p.evaluate('__townTest.step(30)');second=json.loads(p.evaluate('__townTest.save()'));row['all_replay_differences']=changes(first,second);row['exactReplayFromCanonicalStart']=first==second;result['cases'].append(row);pages.append((p,raw,canonical))
 # The accepted public loader must interpret the candidate's exact same wire identically.
 p=pages[0][0];assert p.evaluate('x=>__townTest.load(x)',pages[1][1]);result['same_candidate_archive_public_vs_candidate_loader_differences']=changes(json.loads(p.evaluate('__townTest.save()')),json.loads(pages[1][2]));p=pages[1][0];assert p.evaluate('x=>__townTest.load(x)',pages[0][1]);result['same_base_archive_public_vs_candidate_loader_differences']=changes(json.loads(p.evaluate('__townTest.save()')),json.loads(pages[0][2]));browser.close()
for case in result['cases']:
 assert case['financialArraysUnchanged']and case['rngUnchanged']and case['exactReplayFromCanonicalStart']and case['all_replay_differences']==[],case
 assert all(re.fullmatch(r'\.buildings\.\d+\.units\.\d+',d['path'])for d in case['all_initial_cold_differences']),case
 groups={}
 for d in case['all_initial_cold_differences']:groups.setdefault(d['path'].rsplit('.',1)[0],[]).append(d)
 for path,rows in groups.items():assert sorted(d['before']for d in rows)==sorted(d['after']for d in rows),(path,rows)
 case['changed_tenant_lists_preserve_each_membership']=True
assert result['same_candidate_archive_public_vs_candidate_loader_differences']==[]and result['same_base_archive_public_vs_candidate_loader_differences']==[]
for file in ['src/90-archive-panels.js','src/44-migration.js']:
 original=subprocess.check_output(['git','show',BASE+':'+file],cwd=ROOT);currentFile=(ROOT/file).read_bytes();assert original==currentFile,file;result[file+'_identical_to_public_base_sha256']=hashlib.sha256(original).hexdigest()
result['comparisonPolicy']='All differences enumerated. Only established tenant-list ordering normalization allowed before replay; no fields excluded from replay or shared-input loader comparisons.'
print(json.dumps(result,indent=2));(ROOT/'reports/commercial-district-integration/tenant-provenance.json').write_text(json.dumps(result,indent=2)+'\n')
