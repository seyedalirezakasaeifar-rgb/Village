"""Local canonical investigation. Strict complete state, no field exclusions."""
from pathlib import Path
import sys,json,hashlib,gzip,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text()
probe=r'''
const canonicalRoad=v=>Array.isArray(v)?v.map(canonicalRoad):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonicalRoad(v[k])])):v;
function roadFullDiff(a,b,path=''){if(typeof a!==typeof b||a===null||b===null)return Object.is(a,b)?[]:[{path,before:a,after:b}];if(Array.isArray(a)||Array.isArray(b)){if(!Array.isArray(a)||!Array.isArray(b)||a.length!==b.length)return [{path,beforeLength:a?.length,afterLength:b?.length}];return a.flatMap((v,i)=>roadFullDiff(v,b[i],path+'['+i+']'));}if(a&&typeof a==='object')return [...new Set([...Object.keys(a),...Object.keys(b)])].flatMap(k=>roadFullDiff(a[k],b[k],path+'.'+k));return Object.is(a,b)?[]:[{path,before:a,after:b}];}
window.__roadCanonicalProbe=spec=>{
 __townTest.reset(spec.scenario||'settlement',spec.seed||42);if(spec.archive&&!hydrateSave(spec.archive))throw Error('Fixture import failed');__townTest.step(spec.steps||0);paused=true;const raw=archivePayload(),before=JSON.parse(raw),money=totalMoney();
 __townTest.step(1);const uninterrupted=JSON.parse(archivePayload()),rngA=rngState;
 if(!hydrateSave(raw))throw Error('Current checkpoint rejected');const warm=JSON.parse(archivePayload());enterContinuedTown();paused=true;const entered=JSON.parse(archivePayload());__townTest.step(1);const replay=JSON.parse(archivePayload()),rngB=rngState;
 const warmDiff=roadFullDiff(before,warm),enterDiff=roadFullDiff(warm,entered),replayDiff=roadFullDiff(uninterrupted,replay);return {label:spec.label,day:before.day,roadBefore:before.roadMetrics,roadWarm:warm.roadMetrics,roadEntered:entered.roadMetrics,warmDiff,enterDiff,replayDiff,rngEqual:rngA===rngB,moneyDrift:totalMoney()-money,valid:validateTown(),exactBefore:canonicalRoad(before),exactEntered:canonicalRoad(entered)};
};
'''
fixtures=[{'label':'seed42-day'+str(n+1),'seed':42,'steps':n}for n in [0,1,6,9,10,29,30,31,59,60,61,89,90]]
fixtures += [{'label':'regional91-day'+str(n+1),'seed':91,'scenario':'regional','steps':n}for n in [0,1,29,30,31]]
for label,ref,path in [('v60','525e47d','tests/fixtures/v60-distressed-town.json'),('planned894','01eeda3','docs/previews/growth-journey/regional-42-planned.json.gz'),('retained778','833afee','tests/fixtures/generated-late-31987fc/terminal.json.gz')]:
 data=subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT);text=gzip.decompress(data).decode()if path.endswith('.gz')else data.decode();fixtures.append({'label':label,'archive':text})
rows=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.evaluate('window.requestAnimationFrame=()=>0');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'))
 for spec in fixtures:
  r=p.evaluate('s=>__roadCanonicalProbe(s)',spec);a=r.pop('exactBefore');c=r.pop('exactEntered');r['beforeHash']=hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest();r['enteredHash']=hashlib.sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest();rows.append(r);print(r['label'],'warm',r['warmDiff'][:6],'enter',r['enterDiff'][:6],'replay',r['replayDiff'][:6],flush=True)
 b.close()
out={'sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'excludedFields':[],'rows':rows};dest=ROOT/'reports/road-canonical-724';dest.mkdir(exist_ok=True,parents=True);(dest/'matrix.json').write_text(json.dumps(out,indent=2)+'\n')
