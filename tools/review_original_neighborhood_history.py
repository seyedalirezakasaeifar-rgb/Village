"""Reproduce the held history candidate cadence/schema defects on an immutable base."""
from pathlib import Path
import subprocess,tempfile,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
BASE='0a6d217933eb0eac0c42787483ae96c624d23ef5';CANDIDATE='9650b62c7dad3fb8088e908d69ea7355526bd8a0'
def show(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT,text=True)
base=show(BASE,'assets/game.js');candidate=base
with tempfile.TemporaryDirectory()as tmp:
 for name in ['27-urban-evolution.js','98-urban-ui.js']:
  path=Path(tmp)/'src'/name;path.parent.mkdir(exist_ok=True);path.write_text(show(BASE,'src/'+name))
 diff=subprocess.check_output(['git','diff',CANDIDATE+'^',CANDIDATE,'--','src'],cwd=ROOT)
 subprocess.run(['patch','-p1','-d',tmp],input=diff,check=True,stdout=subprocess.PIPE)
 for name in ['27-urban-evolution.js','98-urban-ui.js']:candidate=candidate.replace(show(BASE,'src/'+name),(Path(tmp)/'src'/name).read_text(),1)
probe=r'''window.__historyReview={cadence:()=>{const farms=[],retail=[];urbanHousingMobility=()=>0;urbanDistrictReview=()=>0;if(typeof urbanRecordActivity==='function')urbanRecordActivity=()=>0;urbanFarmRenewal=()=>{farms.push(G.day);return false};urbanRetailProposal=()=>{retail.push(G.day);return false};for(const day of [30,60,90]){G.day=day;urbanEvolutionDay()}return{farms,retail}},schema:()=>{__townTest.reset('settlement',42);__townTest.step(180);const good=archivePayload(),rows=[];for(const kind of ['longAliasKey','extraSnapshotField','extraRowField']){hydrateSave(good);const data=JSON.parse(good),sample=data.urban.activity[0],key=Object.keys(sample.blocks)[0];if(kind==='longAliasKey'){sample.blocks['0'.repeat(128)+key]=sample.blocks[key];delete sample.blocks[key]}else if(kind==='extraSnapshotField')sample.extra='x'.repeat(8192);else sample.blocks[key].extra='x'.repeat(8192);rows.push({kind,accepted:hydrateSave(data)})}return rows}};'''
rows={}
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for label,source in [('base',base),('originalCandidate',candidate)]:
  for case in (['cadence']if label=='base'else['cadence','schema']):
   p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();rows.setdefault(label,{})[case]=p.evaluate('c=>__historyReview[c]()',case);p.close()
 b.close()
assert rows['base']['cadence']['farms']==[30,60,90]and rows['originalCandidate']['cadence']['farms']==[90],rows
assert all(r['accepted']for r in rows['originalCandidate']['schema']),rows
print(json.dumps({'base':BASE,'candidate':CANDIDATE,'base_source_sha256':hashlib.sha256(base.encode()).hexdigest(),'held_candidate_source_sha256':hashlib.sha256(candidate.encode()).hexdigest(),'reproducedHold':rows},indent=2))
