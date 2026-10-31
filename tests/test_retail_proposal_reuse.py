"""Proposal-local worker scan reuse: mutation oracle and paired full-model CPU."""
from pathlib import Path
import functools,gzip,hashlib,http.server,json,subprocess,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];source=(ROOT/'assets/game.js').read_text();baseline=source
for file in ['27-urban-evolution.js','29-retail-labour.js']:
 current=(ROOT/'src'/file).read_text();old=subprocess.check_output(['git','show','5c50301:src/'+file],cwd=ROOT,text=True);assert current in baseline;baseline=baseline.replace(current,old)
old=subprocess.check_output(['git','show','5c50301:src/29-retail-labour.js'],cwd=ROOT,text=True);reference=old[old.index('function urbanRetailLabour('):old.index('function urbanRetailPlan(')].replace('function urbanRetailLabour(', 'function referenceRetailLabour(')
archive=gzip.decompress(subprocess.check_output(['git','show','833afee35aa714919a38e420e74cee1f719315db:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)).decode()
probe=reference+r'''
window.__retailReuse={
 oracle:()=>{const sites=buildableCandidates('business').slice(0,60),before=JSON.stringify(G),rng=rngState,cases=[];const check=label=>{const context=urbanRetailLabourCandidates();for(const site of sites)for(const offer of [null,25,50]){const a=JSON.stringify(referenceRetailLabour(site,offer)),b=JSON.stringify(urbanRetailLabour(site,offer)),c=JSON.stringify(urbanRetailLabour(site,offer,context));if(a!==b||b!==c)throw Error('Bid mismatch '+label);}cases.push(label);};check('late town');
 const person=G.people.find(p=>!p.deceased&&!p.movedAway&&p.age>=18&&p.age<=60),firm=G.firms.find(f=>!f.closed),home=G.households[person.hh],other=G.households.find(h=>h.people.length&&h.home!==home.home);
 const changes=[[firm,'wage',firm.wage+7],[firm,'closed',true],[person,'publicWork','test-duty'],[person,'searchAfter',G.day+30],[G.policy,'minWage',G.policy.minWage+5],[home,'home',other.home],[G,'day',G.day+31]];
 for(const [object,key,value]of changes){const had=Object.prototype.hasOwnProperty.call(object,key),old=object[key];object[key]=value;check(key);if(had)object[key]=old;else delete object[key];}
 if(before!==JSON.stringify(G)||rng!==rngState)throw Error('Oracle changed model/RNG');return {sites:sites.length,offers:3,cases,unchanged:true};},
 step:n=>{const start=performance.now();__townTest.step(n);return {ms:performance.now()-start,day:G.day,valid:validateTown(),money:totalMoney(),goodsError:Math.max(...goodsBalance().map(v=>Math.abs(v.error)))};},
 model:()=>{const g=JSON.parse(archivePayload());delete g.trafficState;delete g.visualState;return g;}
};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();result={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'baseline_sha256':hashlib.sha256(baseline.encode()).hexdigest(),'checkpoint_sha256':hashlib.sha256(archive.encode()).hexdigest(),'pairs':[],'errors':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for repeat in range(6):
  rows={};models={}
  for name in (['baseline','candidate'] if repeat%2==0 else ['candidate','baseline']):
   payload=(baseline if name=='baseline' else source).replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js');p=b.new_page();p.set_default_timeout(120000);p.on('pageerror',lambda e:result['errors'].append(str(e)));p.route('**/game.js',(lambda body:lambda r:r.fulfill(content_type='application/javascript',body=body))(payload));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townArchive.restore(s)',archive);p.keyboard.press('Escape');p.evaluate('__townTest.step(180)');assert p.evaluate('s=>__townArchive.restore(s)',archive);p.keyboard.press('Escape')
   if repeat==0 and name=='candidate':result['oracle']=p.evaluate('__retailReuse.oracle()')
   assert p.evaluate('s=>__townArchive.restore(s)',archive);p.keyboard.press('Escape')
   rows[name]=p.evaluate('__retailReuse.step(180)');models[name]=p.evaluate('__retailReuse.model()');p.close()
  assert models['baseline']==models['candidate'],[k for k in models['baseline'] if models['baseline'][k]!=models['candidate'].get(k)];result['pairs'].append(rows);print('PASS exact 180-day model/RNG pair',repeat,rows,flush=True)
 b.close()
server.shutdown();assert not result['errors'];out=ROOT/'reports/integration/retail-proposal-reuse-8';out.mkdir(parents=True,exist_ok=True);(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
