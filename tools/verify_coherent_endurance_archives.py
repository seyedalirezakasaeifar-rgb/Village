"""Exact terminal cold state, inherited tenancy projection, replay and native UTF-8 transport."""
from pathlib import Path
import sys,subprocess,json,hashlib,copy,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
BASE='0a6d217933eb0eac0c42787483ae96c624d23ef5';source=(ROOT/'assets/game.js').read_text();base=subprocess.check_output(['git','show',BASE+':assets/game.js'],cwd=ROOT,text=True);folder=ROOT/'reports/coherent-composition/endurance';files=sorted(folder.glob('*-endurance-town.json'));assert len(files)==5,files

def canonical_tenancy(data):
 result=copy.deepcopy(data)
 for b in result['buildings']:
  capacity={'home':1,'apartment':4,'tower':9}.get(b['kind'],0)
  if not capacity:continue
  ids=sorted(h['id']for h in result['households']if h['home']==b['id']and h['people']);b['hh']=ids[0]if ids else -1
  if b['kind']!='home':b['units']=ids
  if isinstance(b.get('legacySharedTenants'),list):
   if len(ids)<=capacity:b.pop('legacySharedTenants')
   else:b['legacySharedTenants']=sorted(i for i in b['legacySharedTenants']if i in ids)
 return result

def differences(a,b,path=''):
 if type(a)!=type(b):return [{'path':path,'before':a,'after':b}]
 if isinstance(a,dict):return sum([differences(a.get(k),b.get(k),path+'.'+k)for k in a.keys()|b.keys()],[])
 if isinstance(a,list):return sum([differences(x,y,path+'.'+str(i))for i,(x,y)in enumerate(zip(a,b))],[])if len(a)==len(b)else[{'path':path,'before':a,'after':b}]
 return []if a==b else [{'path':path,'before':a,'after':b}]

rows=[]
with sync_playwright()as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for js in [base,source]:
  p=browser.new_page();p.set_content(html);p.add_script_tag(content=js);p.locator('#newTown').click();p.locator('#pause').click();pages.append(p)
 for file in files:
  raw=file.read_text();original=json.loads(raw);outputs=[]
  for page in pages:
   assert page.evaluate('a=>__townTest.load(a)',raw),file.name;outputs.append(json.loads(page.evaluate('__townTest.save()')))
  expected=canonical_tenancy(original)
  if outputs[0]!=expected or outputs[1]!=expected:
   print(json.dumps({'terminal':file.name,'unexpectedBase':differences(expected,outputs[0])[:30],'unexpectedCurrent':differences(expected,outputs[1])[:30]},indent=2),flush=True)
  assert outputs[0]==outputs[1]==expected,file.name
  canonical=json.dumps(outputs[1],separators=(',',':'));page=pages[1];assert page.evaluate('a=>__townTest.load(a)',canonical);assert json.loads(page.evaluate('__townTest.save()'))==expected
  page.evaluate('__townTest.step(30)');warm_checkpoint=json.loads(page.evaluate('__townTest.save()'));page.evaluate('__townTest.step(30)');warm_future=json.loads(page.evaluate('__townTest.save()'))
  assert page.evaluate('a=>__townTest.load(a)',json.dumps(warm_checkpoint,separators=(',',':')))
  loaded_checkpoint=json.loads(page.evaluate('__townTest.save()'));assert loaded_checkpoint==canonical_tenancy(warm_checkpoint),(file.name,'warm checkpoint cold drift',differences(canonical_tenancy(warm_checkpoint),loaded_checkpoint)[:20])
  page.evaluate('__townTest.step(30)');replayed_future=json.loads(page.evaluate('__townTest.save()'));assert canonical_tenancy(replayed_future)==canonical_tenancy(warm_future),(file.name,'warm/cold future differs',differences(canonical_tenancy(warm_future),canonical_tenancy(replayed_future))[:20])
  normalizations=differences(original,expected);rows.append({'terminal':file.name,'raw_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'rawUtf8Bytes':len(file.read_bytes()),'day':original['day'],'personRecords':len(original['people']),'householdRecords':len(original['households']),'firmRecords':len(original['firms']),'optionalHistoryUtf8Bytes':len(json.dumps(original['urban'].get('activity',[]),separators=(',',':')).encode()),'pairedBaseAndCurrentColdStateExact':True,'idempotentColdAndWarm30DayReplayExact':True,'warmCheckpointInheritedTenancyProjection':differences(warm_checkpoint,canonical_tenancy(warm_checkpoint)),'explicitInheritedTenancyProjection':normalizations})
 browser.close()
transport=r'''package org.townledger.vale;import java.nio.file.*;import java.io.*;import java.util.Arrays;public final class EnduranceArchiveTransportTest{public static void main(String[]args)throws Exception{for(String path:args){byte[] raw=Files.readAllBytes(Paths.get(path));byte[] read=ArchiveIO.read(new ByteArrayInputStream(raw));String text=ArchiveIO.decode(read);byte[] encoded=ArchiveIO.encode(text);ByteArrayOutputStream out=new ByteArrayOutputStream();ArchiveIO.write(out,encoded);if(!Arrays.equals(raw,out.toByteArray()))throw new AssertionError(path);}System.out.println("PASS actual bounded ArchiveIO UTF-8 read/decode/encode/write on all five generated terminal archives");}}'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'EnduranceArchiveTransportTest.java';p.write_text(transport);subprocess.run(['java','com.sun.tools.javac.Main','-d',tmp,str(ROOT/'android/app/src/main/java/org/townledger/vale/ArchiveIO.java'),str(p)],check=True);subprocess.run(['java','-Xmx512m','-cp',tmp,'org.townledger.vale.EnduranceArchiveTransportTest',*[str(p)for p in files]],check=True)
result={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'base':BASE,'base_archive_module_sha256':hashlib.sha256(subprocess.check_output(['git','show',BASE+':src/90-archive-panels.js'],cwd=ROOT)).hexdigest(),'archive_module_sha256':hashlib.sha256((ROOT/'src/90-archive-panels.js').read_bytes()).hexdigest(),'excludedFields':[],'nativeArchiveIOFiveTerminalRoundtripsExact':True,'cases':rows,'scope':'All full states compared against the explicitly reconstructed existing tenancy projection, paired against the pre-history loader. No financial, identity, road, cargo, service receipt, RNG or visual fields omitted.'}
assert result['base_archive_module_sha256']==result['archive_module_sha256']
print(json.dumps(result,indent=2));(folder/'terminal-cold-transport.json').write_text(json.dumps(result,indent=2)+'\n')
