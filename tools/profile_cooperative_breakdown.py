"""Source-bound host trusted input/RAF comparison; no Android performance claim."""
from pathlib import Path
import ast,json,hashlib,functools,http.server,threading,time,gzip,subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def assignment(file,name):
 return next(ast.literal_eval(n.value) for n in ast.parse((ROOT/file).read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
late=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'],cwd=ROOT)).decode()
fixture=assignment('tests/test_transit_live_performance.py','probe');probe=assignment('tools/profile_session.py','probe')
measure=r'''
const causalPending=[],causalResponses=[];window.addEventListener('click',e=>{if(e.isTrusted&&e.target.closest('#mapStatusToggle')&&e.timeStamp>=cooperativeTrustedEpoch)causalPending.push(e.timeStamp);},{capture:true});
const cooperativeTrusted=[];let cooperativeTrustedEpoch=Infinity;window.addEventListener('pointerdown',e=>{if(!e.isTrusted||e.timeStamp<cooperativeTrustedEpoch)return;const sent=e.timeStamp,handler=performance.now()-sent;requestAnimationFrame(()=>cooperativeTrusted.push({at:sent,handlerMs:handler,nextRafMs:performance.now()-sent}));},{capture:true});
'''
extra=r'''
const breakdown={};for(const name of ['beginCooperativeDay','cooperativePump','cooperativeCommit','cooperativeFlushCommands','occupyVacantHousing','seekPrivateServiceInvestment','urbanRetailProposal','dailyEconomy']){const original=eval(name);eval(name+'=function(...args){const t=performance.now();try{return original(...args)}finally{(breakdown["'+name+'"]||(breakdown["'+name+'"]=[])).push(performance.now()-t);}}');}
new MutationObserver(records=>{for(const record of records){if(!causalPending.length)continue;const sent=causalPending.shift(),mutated=performance.now();requestAnimationFrame(()=>requestAnimationFrame(()=>causalResponses.push({sent,mutationMs:mutated-sent,paintOpportunityMs:performance.now()-sent})));}}).observe($('mapStatusToggle'),{attributes:true,attributeFilter:['aria-expanded']});

const lateDraws=[];const lateOriginalDraw=draw;draw=function(...args){if(!cooperativeDayBusy())lateDraws.push({at:performance.now(),day:G.day});return lateOriginalDraw(...args);};
window.__cooperativeProfile={
 run:()=>new Promise(resolve=>{const raf=[],timers=[],start=performance.now(),day=G.day,total=totalMoney();cooperativeTrustedEpoch=start;cooperativeTrusted.length=0;lateDraws.length=0;let lastRaf=0,lastTimer=start;const timer=setInterval(()=>{const now=performance.now();timers.push(now-lastTimer);lastTimer=now;},16);function sample(now){if(lastRaf)raf.push(now-lastRaf);lastRaf=now;if(now-start<12000)requestAnimationFrame(sample);else{clearInterval(timer);paused=true;afterCommittedDay(()=>resolve({elapsedMs:performance.now()-start,days:G.day-day,raf,timers,breakdown,causalResponses,causalMissing:causalPending.length,draws:lateDraws,trusted:cooperativeTrusted,slices:cooperativeSamples.slices,stagedDays:cooperativeSamples.days,ticks:perfStats.ticks,valid:validateTown(),moneyDrift:totalMoney()-total,uiDay:$('date').textContent,completedDay:G.day,queue:cooperativeCommands.length,errors:cooperativeSamples.errors}));}}requestAnimationFrame(sample);})
};
'''
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
source=(ROOT/'assets/game.js').read_text();out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'hostChromium':True,'physicalAndroid':False,'retainedTerminalFixture':True,'fixtureSha256':hashlib.sha256(late.encode()).hexdigest(),'rows':[]}
def summary(values):
 values=sorted(values);return {'n':len(values),'p95Ms':values[min(len(values)-1,int(len(values)*.95))] if values else 0,'p99Ms':values[min(len(values)-1,int(len(values)*.99))] if values else 0,'maxMs':max(values) if values else 0}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for enabled in [False,True]:
  p=b.new_page(viewport={'width':844,'height':390},has_touch=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda route:route.fulfill(content_type='application/javascript',body=source.replace('// SOURCE: 05-systems.js',measure+'\n// SOURCE: 05-systems.js').replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+probe+'\n'+extra+'\n// SOURCE: 99-instrumentation.js')));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();assert p.evaluate('s=>__townTest.load(s)',late);p.evaluate('()=>{paused=true;hostSuspended=false;}');p.evaluate('(on)=>__cooperativeSimulation.enable(on)',enabled);p.locator('#panelClose').click();p.locator('#speedRange').fill('6');p.locator('#pause').click();p.evaluate('()=>{window.__cooperativeProfileRun=__cooperativeProfile.run();}')
  for i in range(16):
   p.wait_for_timeout(550);p.locator('#mapStatusToggle').tap()
  r=p.evaluate('window.__cooperativeProfileRun');row={'enabled':enabled,'days':r['days'],'actualSpeed':r['days']*1650/r['elapsedMs'],'raf':summary(r['raf']),'timerDelivery':summary(r['timers']),'trustedHandler':summary([x['handlerMs'] for x in r['trusted']]),'trustedNextRaf':summary([x['nextRafMs'] for x in r['trusted']]),'breakdown':{k:{**summary(v),'totalMs':sum(v)} for k,v in r['breakdown'].items()},'causalMutation':summary([x['mutationMs'] for x in r['causalResponses']]),'causalPaintOpportunity':summary([x['paintOpportunityMs'] for x in r['causalResponses']]),'causalMissing':r['causalMissing'],'dayWait':summary([max(0,x['elapsedMs']-x['cpuMs']) for x in r['stagedDays']]),'completedDraws':len(r['draws']),'maxDrawGapMs':max([r['draws'][i]['at']-r['draws'][i-1]['at'] for i in range(1,len(r['draws']))] or [0]),'inputToNextDraw':summary([next((d['at']-x['at'] for d in r['draws'] if d['at']>=x['at']),0) for x in r['trusted']]),'slices':summary([x['ms'] for x in r['slices']]),'tickCpu':summary(r['ticks']),'valid':r['valid'],'moneyDrift':r['moneyDrift'],'queue':r['queue'],'errors':errors+r['errors'],'completedDay':r['completedDay'],'uiDay':r['uiDay']};assert row['valid']['ok'] and abs(row['moneyDrift'])<.1 and not row['errors'] and not row['queue'],row;out['rows'].append(row);print(json.dumps(row),flush=True);p.close()
 b.close()
server.shutdown();(ROOT/'reports/cooperative-breakdown-8.json').write_text(json.dumps(out,indent=2));print('PASS source-bound trusted touch, timer/RAF, operations/conservation and cleared queues; results are observations, not Android acceptance')
