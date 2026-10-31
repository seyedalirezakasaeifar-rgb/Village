"""A natural three-year town exposes phantom available retail workers."""
from pathlib import Path
import gzip,json,hashlib,subprocess
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text();archive=gzip.decompress((ROOT/'tests/fixtures/urban-retail-unfunded-labour.json.gz').read_bytes()).decode()
probe=r'''
window.__retailLabourAudit=()=>({day:G.day,total:totalMoney(),public:G.people.filter(p=>p.publicWork||p.previousPublicRole||p.publicRole).map(p=>p.id),legacyFree:G.people.filter(p=>!p.deceased&&!p.movedAway&&p.age>=16&&p.age<=70&&p.job<0).length,unemployed:G.people.filter(p=>!p.deceased&&!p.movedAway&&p.age>=16&&p.age<=70&&p.job<0&&!p.publicWork&&!p.publicRole&&!p.previousPublicRole&&(p.searchAfter||0)<=G.day).length,malls:G.firms.filter(f=>f.retailCentre).map(f=>({id:f.id,staff:f.workers.slice(),jobs:f.jobs,wage:f.wage,cash:f.cash,net:f.netProfit,payroll:f.payroll,price:f.price})),jobs:G.people.map(p=>({id:p.id,job:p.job,changed:p.privateJobChange||null})),valid:validateTown()});
'''
results={}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for label,js in [('before',subprocess.check_output(['git','show','525e47dd3967741fb59d2fd06921c1647a29a24a:assets/game.js'],cwd=ROOT,text=True)),('after',source)]:
  p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=js.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('a=>__townTest.load(a)',archive);start=p.evaluate('__retailLabourAudit()');p.evaluate('__townTest.step()');end=p.evaluate('__retailLabourAudit()');assert end['valid']['ok'] and abs(end['total']-start['total'])<.05 and not errors
  target=next(f for f in start['malls'] if not f['staff']);later=next(f for f in end['malls'] if f['id']==target['id']);results[label]={'initialLegacyFree':start['legacyFree'],'initialGenuineJobseekers':start['unemployed'],'initial':target,'nextDay':later,'cashError':end['total']-start['total'],'valid':end['valid']}
  if label=='before':assert not later['staff'],'Fixture no longer exposes original unstaffed centre'
  else:
   assert later['staff'] and not(set(later['staff'])&set(start['public'])),'Funded public employees were double-counted or no real hire occurred'
   assert later['payroll']>0 and later['wage']>target['wage'],'Hiring was not backed by a real wage offer'
   p.evaluate('__townTest.step(89)');long=p.evaluate('__retailLabourAudit()');assert long['valid']['ok'] and abs(long['total']-start['total'])<.1;results[label]['day90']=next(f for f in long['malls'] if f['id']==target['id']);save=p.evaluate('__townTest.save()');bad=json.loads(save);bad['firms'][target['id']]['retailHiringReview']=bad['day']+1;assert not p.evaluate('a=>__townTest.load(a)',bad);assert p.evaluate('a=>__townTest.load(a)',save)
  p.close()
 b.close()
out=ROOT/'docs/previews/urban8/retail-labour-viability.json';out.write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'fixture':'Natural regional seed42 day1081 from 525e47d, no injected agents/cash/stocks.','results':results},indent=2)+'\n');print(json.dumps(results,indent=2))
