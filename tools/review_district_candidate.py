"""Reproduce held district candidate defects without installing it in production.

Exit zero means the immutable candidate's rejection and proposed one-line review
correction were reproduced; it is not an acceptance pass for that candidate.
"""
from pathlib import Path
import io,tarfile,subprocess,json,hashlib,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from playwright.sync_api import sync_playwright
from test_mobile_rendering import html
BASE='e3fae439e96b33bc3a62340f9a898029af674111';CANDIDATE='b7a6039a799b2ceac38903f85da45933b61d4154'
def blob(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT,text=True)
base=blob(BASE,'assets/game.js')
with tarfile.open(fileobj=io.BytesIO(subprocess.check_output(['git','archive',BASE,'src'],cwd=ROOT)))as bundle:
 modules={Path(m.name).name:bundle.extractfile(m).read().decode()for m in bundle.getmembers()if m.isfile()and m.name.endswith('.js')}
retail=modules['27-urban-evolution.js'];retail=retail[retail.index('function urbanRetailProposal('):retail.index('function urbanEvolutionDay(')]
module=blob(CANDIDATE,'src/27-urban-evolution.js');module=module[:module.index('function urbanRetailProposal(')]+retail+module[module.index('function urbanEvolutionDay('):]
modules['27-urban-evolution.js']=module;modules['98-urban-ui.js']=blob(CANDIDATE,'src/98-urban-ui.js')
source='\n'.join('// SOURCE: '+name+'\n'+modules[name]for name in sorted(modules));metadata=json.loads(blob(BASE,'release.json'));source=re.sub(r'const RELEASE=Object.freeze\(\{[^\n]+\}\);','const RELEASE=Object.freeze('+json.dumps(metadata,separators=(',',':'))+');',source,count=1)
assert hashlib.sha256(source.encode()).hexdigest()=='a6a1339050cbbe572ade5f430e1157fe88f37faf4ca1d1ed244566ee4cb1a9f6'
probe="window.__districtAcceptance={cache:()=>{__townTest.reset('regional',42);__townTest.step(1);const before=JSON.stringify(G),cached=JSON.parse(JSON.stringify((urbanSpatial().profiles||urbanSpatial().blocks)));invalidateUrban();const fresh=urbanSpatial().profiles||urbanSpatial().blocks,changes=[];for(const [key,row]of Object.entries(cached))for(const field of Object.keys(row))if(JSON.stringify(row[field])!==JSON.stringify(fresh[key][field]))changes.push({key,field,cached:row[field],fresh:fresh[key][field]});return {changes,modelUnchanged:before===JSON.stringify(G)};},review:()=>{__townTest.reset('regional',42);__townTest.step(720);invalidateUrban();const c=urbanSpatial(),entry=Object.entries(c.profiles).find(([k,p])=>p.character!==c.blocks[k].character&&c.blocks[k].buildings.length>=3);if(!entry)throw Error('No actual observed/base character difference');const [key,p]=entry,u=ensureUrban(),base=G.day;u.districts[key]={name:'Review control',character:c.blocks[key].character,since:1,changed:1};const stages=[];for(const offset of [0,30,60,90]){G.day=base+offset;u.lastReview=-1;invalidateUrban();urbanDistrictReview();stages.push({day:G.day,observed:urbanSpatial().profiles[key].character,archived:JSON.parse(JSON.stringify(u.districts[key]))})}return {key,stages};}};"
result={'base':BASE,'candidate':CANDIDATE,'base_source_sha256':hashlib.sha256(base.encode()).hexdigest(),'candidate_source_sha256':hashlib.sha256(source.encode()).hexdigest()}
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 fixed=source.replace('old.character=b.character;old.changed=G.day;','old.character=observed;old.changed=G.day;');assert fixed!=source
 for label,js in [('base',base),('candidate',source),('proposedReviewFix',fixed)]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=js.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();row={'cache':p.evaluate('__districtAcceptance.cache()')}
  if label!='base':row['review']=p.evaluate('__districtAcceptance.review()')
  result[label]=row;p.close()
 b.close()
assert all(result[label]['cache']['modelUnchanged']for label in ['base','candidate','proposedReviewFix'])
last=result['candidate']['review']['stages'][-1];fixedLast=result['proposedReviewFix']['review']['stages'][-1]
assert last['archived']['character']!=last['observed'] and 'proposed'not in last['archived']
assert fixedLast['archived']['character']==fixedLast['observed']
assert any(c['field']=='bankDeposits'for c in result['candidate']['cache']['changes'])
result['acceptance']='HOLD: observed-character commit fails; derived current bank/income data stale. One-line review correction verified in memory, cache contract still unresolved.'
print(json.dumps(result,indent=2))
