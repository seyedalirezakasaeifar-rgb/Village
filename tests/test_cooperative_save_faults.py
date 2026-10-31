"""Independent exhaustive persistence/native attacks; production scheduler unchanged."""
from test_mobile_rendering import ROOT
import ast,json,hashlib,threading,http.server,functools
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();tree=ast.parse((ROOT/'tests/test_cooperative_barriers.py').read_text());probe=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe+=r'''
window.__saveAttack={replacement:()=>{chosenScenario='settlement';seed(101);paused=true;return archivePayload();},
 run:async(index,action,raw,replacement)=>{
  if(cooperativeDayBusy())finishCooperativeDaySync('test cleanup');if(!hydrateSave(raw))throw Error('Fixture load');paused=true;
  const completed=archivePayload();if(!__coopBarrier.startAt(index))throw Error('Missing boundary');const token=cooperativeJob.token;
  let result,declined=false;
  if(action==='save'){let settled=false;const promise=save().then(v=>{settled=true;return v});await Promise.resolve();if(settled)throw Error('Save acknowledged partial day');finishCooperativeDaySync('save attack');if(!await promise)throw Error('Save failed');result=archivePayload();}
  if(action==='export')result=__townArchive.export();
  if(action==='suspend'){await __townArchive.suspend();result=archivePayload();__townArchive.resume();paused=true;}
  if(action==='back'){__townArchive.back();result=archivePayload();}
  if(action==='invalid'){if(__townArchive.restore('{bad'))throw Error('Invalid import accepted');result=archivePayload();}
  if(action==='import'){if(!__townArchive.restore(replacement))throw Error('Replacement rejected');result=archivePayload();}
  if(action==='newtown'){chosenScenario='settlement';seed(101);paused=true;result=archivePayload();}
  if(action==='command'){let calls=0;const promise=__cooperativeSimulation.command('cash transfer',()=>{calls++;G.treasury+=7;G.region-=7;return calls});await Promise.resolve();if(calls)throw Error('Command ran on partial state');finishCooperativeDaySync('command attack');if(await promise!==1||calls!==1)throw Error('Command not exactly once');result=archivePayload();}
  if(action==='fault'){const saving=save().catch(()=>{declined=true;return false});const command=__cooperativeSimulation.command('faulted input',()=>{throw Error('Faulted input executed')}).catch(()=>false);__coopBarrier.poison();finishCooperativeDaySync('injected failure');await saving;await command;if(!declined)throw Error('Fault did not reject deferred save');result=archivePayload();}
  if(cooperativeDayBusy())throw Error('Partial day escaped barrier');const before=archivePayload();cooperativeChannel.port1.onmessage({data:token});if(archivePayload()!==before)throw Error('Old token mutated completed town');
  return {archive:result,prior:completed,valid:validateTown(),tokenInert:true};
 }
};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
def canonical(raw):
 g=json.loads(raw) if isinstance(raw,str) else dict(raw)
 for k in ['trafficState','visualState']:g.pop(k,None)
 return g
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'httpOrigin':True,'cases':[],'failures':[]}
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.route('**/game.js',lambda r:r.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'),content_type='application/javascript'));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();raw=p.evaluate('__coopBarrier.prepare()');p.evaluate('s=>__townTest.load(s)',raw);expected=canonical(p.evaluate('__coopBarrier.oracle()'));p.evaluate('s=>__townTest.load(s)',raw);stages=p.evaluate('__coopBarrier.stages()');replacement=p.evaluate('__saveAttack.replacement()')
  for index,stage in enumerate(stages,1):
   for action in ['save','export','suspend','back','invalid','import','newtown','command','fault']:
    row={'index':index,'stage':stage,'action':action}
    try:
     actual=p.evaluate('x=>__saveAttack.run(x.index,x.action,x.raw,x.replacement)',dict(row,raw=raw,replacement=replacement));target=canonical(actual['prior']) if action=='fault' else canonical(replacement) if action in ['import','newtown'] else json.loads(json.dumps(expected))
     if action=='command':target['treasury']+=7;target['region']-=7
     got=canonical(actual['archive']);different=[k for k in set(target)|set(got) if target.get(k)!=got.get(k)];assert not different,{'different':different};assert actual['valid']['ok'],actual['valid'];row['passed']=True
    except Exception as e:row['passed']=False;row['error']=str(e);out['failures'].append(row.copy())
    out['cases'].append(row)
   print(index,len(stages),stage,'failures',len(out['failures']),flush=True)
  b.close()
finally:server.shutdown();server.server_close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==out['source_sha256']
path=ROOT/'reports/cooperative-save-faults.json';path.write_text(json.dumps(out,indent=2)+'\n');print('RESULT',len(out['cases']),'cases',len(out['failures']),'failures');assert not out['failures'],out['failures'][:3]
