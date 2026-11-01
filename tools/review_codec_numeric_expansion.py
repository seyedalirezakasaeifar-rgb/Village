"""Raw numeric token canonicalization versus the claimed logical byte bound."""
from pathlib import Path
import sys,subprocess,json,hashlib,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
person_root=os.environ.get('CODEC_REVIEW_PERSON_ROOT')
if person_root:
 source=(Path(person_root)/'assets/game.js').read_text();candidate='f93a87ca331669c7a7907453799f009eb8adbfa0'
else:
 source=(ROOT/'assets/game.js').read_text();old=(ROOT/'src/89-inactive-person-codec.js').read_text();new=subprocess.check_output(['git','show','d1f963a:src/89-inactive-person-codec.js'],cwd=ROOT,text=True);source=source.replace(old,new,1);candidate='d1f963afc24dc932e91c48bb72253583b3390429'

probe=r'''window.__numericExpansion=()=>{__townTest.reset('settlement',42);__inactivePersonCodec.enable(true);const w=JSON.parse(archivePayload());w.payload.reviewNumericValues=Array(800000).fill(1e20);const text=JSON.stringify(w).replace(/100000000000000000000/g,'1e20'),encodedBytes=new Blob([text]).size;let parseError='',logicalBytes=0;try{const decoded=parseArchiveWithInactiveCodec(text);logicalBytes=new Blob([JSON.stringify(decoded.data)]).size;}catch(e){parseError=e.message;}const accepted=hydrateSave(text);let exportError='';if(accepted)try{archivePayload();}catch(e){exportError=e.message;}return {encodedBytes,encodedLimit:INACTIVE_CODEC_LIMITS.bytes,logicalBytes,logicalLimit:INACTIVE_CODEC_LIMITS.logicalBytes,parseError,accepted,exportError,claimedLogicalBoundExceeded:logicalBytes>INACTIVE_CODEC_LIMITS.logicalBytes};};'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__numericExpansion()');b.close()
out={'candidate':candidate,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'fixture':'Adversarial valid JSON short exponent tokens in permitted unknown payload field','result':result};(ROOT/('reports/codec-numeric-expansion-person-review.json' if person_root else 'reports/codec-numeric-expansion-review.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
