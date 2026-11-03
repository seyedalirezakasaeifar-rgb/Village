"""Read-only complete authored seed-state comparison with the accepted bridge base."""
import hashlib,json,subprocess
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
BASE='ecbc945c4aeeb99d27d0cf7b7cd8ee63651af785';baseline=subprocess.check_output(['git','show',BASE+':assets/game.js'],cwd=ROOT,text=True);current=(ROOT/'assets/game.js').read_text();cases=[(scenario,seed) for scenario in ['settlement','regional','hardtimes','industrial'] for seed in [42,101,909]]
def collect(browser,source):
 p=browser.new_page();p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();rows=[p.evaluate("a=>{__townTest.reset(...a);return JSON.parse(__townTest.save())}",list(case)) for case in cases];p.close();return rows
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);before=collect(b,baseline);after=collect(b,current);b.close()
def changes(a,b,path=''):
 if type(a)!=type(b):return [{'path':path,'before':a,'after':b}]
 if isinstance(a,dict):
  result=[]
  for k in a.keys()|b.keys():
   if k not in a or k not in b:result.append({'path':path+'.'+k,'before':a.get(k),'after':b.get(k)})
   else:result.extend(changes(a[k],b[k],path+'.'+k))
  return result
 if isinstance(a,list):
  if len(a)!=len(b):return [{'path':path,'beforeLength':len(a),'afterLength':len(b)}]
  return sum((changes(x,y,path+'.'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
 return [] if a==b else [{'path':path,'before':a,'after':b}]
rows=[]
for case,a,z in zip(cases,before,after):
 differences=changes(a,z);rows.append({'scenario':case[0],'seed':case[1],'differences':differences})
print(json.dumps({'base':BASE,'base_source_sha256':hashlib.sha256(baseline.encode()).hexdigest(),'source_sha256':hashlib.sha256(current.encode()).hexdigest(),'cases':rows},indent=2),flush=True)
for row in rows:
 assert all(d['path'] in {'.journal.0.baseline.safety','.journal.1.baseline.approval'} and d.get('before') is None and isinstance(d.get('after'),(int,float)) and 0<=d['after']<=100 for d in row['differences']),row
print('PASS 12 accepted authored starts retain financial/identity/road/cargo/RNG state; explicit founding-journal census corrections only')
