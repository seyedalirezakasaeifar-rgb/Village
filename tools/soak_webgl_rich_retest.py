"""Sequential, timed real-clock city soaks; frozen29dd12a, no performance certification."""
from pathlib import Path
import subprocess,time,json,hashlib,traceback,os,datetime,argparse
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'docs/previews/webgl-rich-retest-8';O.mkdir(parents=True,exist_ok=True)
A=argparse.ArgumentParser();A.add_argument('--seconds',type=int,default=1800);A.add_argument('--phases',default='economy,reference');args=A.parse_args()
sha=lambda s:hashlib.sha256(s.encode()if isinstance(s,str)else s).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
source=(R/'assets/game.js').read_text();probe='''window.__runningSoak={status:()=>({day:G.day,population:G.stats.population,cash:G.treasury,buildings:G.buildings.length,paused,clock:frameClock,rng:rngState,active:(G.regionalTrade?.shipments||[]).filter(o=>o.mode==='river').map(o=>({id:o.id,stage:o.stage,qty:o.qty})),recent:(G.regionalTrade?.recent||[]).slice(0,12).map(o=>({id:o.id,status:o.status})),boats:portCargoPoses().map(o=>o.id)}),actorMatch:()=>{const v=__webglTaste,e=__cityVisualActors(v.lod,v.selected).slice(0,64).filter(a=>(a.opacity??1)>0),a=v.actorStats.poses;return {ok:e.length===a.length&&e.every((x,i)=>x.id===a[i].id&&Math.abs(x.x-a[i].x)<1e-6&&Math.abs(x.z-a[i].z)<1e-6),expected:e.map(x=>x.id),actual:a.map(x=>x.id)};}};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
files=[R/'assets/game.js',*sorted((R/'assets').glob('webgl*.js')),*sorted((R/'assets').glob('newfoundland*.js'))];hashes={str(p.relative_to(R)):sha(p.read_bytes())for p in files};manifest={'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'sourceModules':hashes,'routedProbeSHA256':sha(script),'startUTC':now(),'processPID':os.getpid(),'harnessSHA256':sha(Path(__file__).read_bytes()),'secondsPerPhase':args.seconds,'sequential':True,'phases':[]}
def save(): (O/'manifest.json').write_text(json.dumps(manifest,indent=2))
save();server=subprocess.Popen(['python','-m','http.server','8813','--bind','127.0.0.1'],cwd=R/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def closed(p):
 if p.locator('#panel').is_visible():p.locator('#panelClose').click()
def paused(p,want):
 if p.evaluate('__cityVisualMotionState().paused')!=want:p.locator('#pause').click()
def events(p,log):
 for _ in range(5):
  buttons=p.locator('[data-event-choice]');eligible=[buttons.nth(i)for i in range(buttons.count())if buttons.nth(i).is_visible()and buttons.nth(i).is_enabled()]
  if not eligible:return
  text=eligible[0].inner_text();eligible[0].click();log.append({'kind':'ordinary-event-choice','text':text,'utc':now()})
def ready(p):p.wait_for_function('window.__webglTaste&&__webglTaste.sceneRevision===__cityVisualRevision()&&__webglTaste.samples.length>=3',timeout=45000)
def park(p,log):
 paused(p,True);events(p,log);paused(p,True);closed(p);p.keyboard.press('Escape');p.evaluate('__townTest.capture({overlay:"none"})');s=p.evaluate('__cityVisualSnapshot()');b=next((b for b in s['buildings']if b['kind']in ['square','park']),None)
 if not b or s['treasury']<6000:log.append({'kind':'clear-rebuild-skipped','reason':'no facility or affordable treasury'});return
 p.evaluate('(b)=>{__webglTaste.focus(b.x,b.y,3.5);__cityVisualInspectBuilding(b.id)}',b);q=p.locator('[data-urban-clear="'+str(b['id'])+'"]')
 if not q.count():closed(p);return
 q.click();yes=p.locator('[data-event-choice="0"]')
 if not yes.is_enabled():events(p,log);closed(p);return
 yes.click();p.wait_for_function('(id)=>!__cityVisualSnapshot().buildings.some(b=>b.id===id)',arg=b['id']);p.locator('[data-panel=construction]').click();p.locator('[data-build=park]').scroll_into_view_if_needed();p.locator('[data-build=park]').click();point=p.evaluate('(b)=>__webglTaste.project(b.x,b.y)',b);p.mouse.click(point['x'],point['y']);ready(p);s2=p.evaluate('__cityVisualSnapshot()');n=next(a for a in s2['buildings']if a['kind']=='park'and a['x']==b['x']and a['y']==b['y']);assert n['id']!=b['id'] and b['id']not in p.evaluate('__webglTaste.loadedBuildings');log.append({'kind':'actual-reviewed-clearance-paid-park','old':b['id'],'new':n['id'],'day':s2['day'],'cashBefore':s['treasury'],'cashAfter':s2['treasury']});closed(p)
def plan(p,log):
 paused(p,True);events(p,log);paused(p,True);closed(p);p.keyboard.press('Escape');p.evaluate('__townTest.capture({overlay:"none"})');s=p.evaluate('__cityVisualSnapshot()');b=next((b for b in s['buildings']if b['kind']=='home'),None)
 if not b or s['treasury']<1800:log.append({'kind':'plan-skipped','reason':'no affordable survey'});return
 p.evaluate('(id)=>__cityVisualInspectBuilding(id)',b['id']);q=p.locator('[data-urban-plan=residential][data-urban-building="'+str(b['id'])+'"]')
 if q.count()and q.is_enabled():
  q.evaluate('e=>e.closest("details").open=true');q.click();yes=p.locator('[data-event-choice="0"]')
  if yes.is_enabled():yes.click();log.append({'kind':'actual-paid-residential-plan','day':s['day'],'cashBefore':s['treasury'],'cashAfter':p.evaluate('__cityVisualSnapshot().treasury')})
  else:events(p,log)
 closed(p)
def trade(p,log):
 paused(p,True);events(p,log);paused(p,True);closed(p);p.locator('[data-panel=economy]').click();office=p.locator('#portFreightOffice')
 if office.count():
  office.evaluate('e=>e.open=true');q=p.locator('[data-port-direction=import]:not([disabled])').first
  if q.count():
   q.click();yes=p.locator('[data-event-choice="0"]')
   if yes.is_enabled():yes.click();log.append({'kind':'actual-reviewed-paid-river-order','status':p.evaluate('__runningSoak.status()')})
   else:events(p,log)
  else:log.append({'kind':'river-order-skipped','reason':'no affordable staffed route'})
 closed(p)
def inspect_static(p,folder,name):
 paused(p,True);ready(p);p.wait_for_function('__runningSoak.actorMatch().ok',timeout=8000);before=p.evaluate('__townTest.save()');a=p.locator('#webglTaste').screenshot();p.wait_for_timeout(220);b=p.locator('#webglTaste').screenshot();after=p.evaluate('__townTest.save()');assert before==after,'paused render changed full archive/RNG';assert a==b,'paused raw canvas pixels changed';assert p.locator('#webglMapOverlay').count()==1;v=p.evaluate('({lod:__webglTaste.lod,revision:__webglTaste.sceneRevision,loaded:__webglTaste.loadedBuildings.length,memory:__webglTaste.memory(),calls:__webglTaste.drawCalls,triangles:__webglTaste.triangles,backend:__webglTaste.renderer,actors:__webglTaste.actorStats.actors,work:__webglTaste.actorWork})');v['fullArchiveSHA256']=sha(before);v['pausedPixelSHA256']=sha(a);v['pausedInvariant']=True;return v
try:
 with sync_playwright()as w:
  # Preview pair is captured before paid actions, same actual archive/camera.
  pair=[]
  for phase in args.phases.split(','):
   pref='low'if phase=='economy'else'high';folder=O/phase;folder.mkdir(exist_ok=True);row={'phase':phase,'actions':[],'samples':[],'checks':[],'errors':[],'knownFindings':[],'shippingChanges':[]};manifest['phases'].append(row);save()
   browser=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=browser.new_context(viewport={'width':1000,'height':577},device_scale_factor=1);p=context.new_page();p.set_default_timeout(45000);p.on('pageerror',lambda e:row['errors'].append(str(e)));p.add_init_script("localStorage.setItem('townledger-options',JSON.stringify({quality:'"+pref+"',fps:20}))");p.route('**/game.js',lambda r:r.fulfill(body=script,content_type='application/javascript'))
   try:
    p.goto('http://127.0.0.1:8813/index.html?cityArt=webgl&cityQuality='+phase);p.locator('#newTown').click();paused(p,True);closed(p);assert p.evaluate('(s)=>__townTest.load(s)',(R/'docs/previews/webgl-economy-8/town.json').read_text());p.evaluate('__townTest.capture()');ready(p);p.locator('[data-panel=settings]').click();closed(p);p.evaluate('__webglTaste.focus(27,27,1.8)');ready(p);p.screenshot(path=str(O/(phase+'-representative.png')));pair.append({'phase':phase,'archive':sha(p.evaluate('__townTest.save()'))});(O/'pair.json').write_text(json.dumps(pair,indent=2))
    if len(pair)==2:assert pair[0]['archive']==pair[1]['archive'],'representative pair archive mismatch'
    park(p,row['actions']);plan(p,row['actions']);trade(p,row['actions']);closed(p);row['initial']=inspect_static(p,folder,'initial');row['startUTC']=now();start=time.monotonic();deadline=start+args.seconds;row['deadlineUTC']=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=args.seconds)).isoformat();row['browserPIDNote']='Playwright-managed Chromium, sequential phase';paused(p,False);next_camera=30;next_sample=300;iteration=0;last_shipping=None;loss_done=False;options_done=False;save();print(json.dumps({'phase':phase,'startUTC':row['startUTC'],'deadlineUTC':row['deadlineUTC'],'pid':os.getpid()}),flush=True)
    while time.monotonic()<deadline:
     events(p,row['actions']);st=p.evaluate('__runningSoak.status()');shipping=json.dumps([st['active'],st['recent'],st['boats']],sort_keys=True)
     if shipping!=last_shipping:row['shippingChanges'].append({'elapsed':round(time.monotonic()-start,2),**st});last_shipping=shipping
     elapsed=time.monotonic()-start
     if elapsed>=next_camera:
      paused(p,True);events(p,row['actions']);paused(p,True);closed(p);iteration+=1;view=[(26,26,1.8),(32,29,3.5),(4,26,3.5),(105,90,.5)][iteration%4];p.evaluate('(v)=>__webglTaste.focus(...v)',view);p.evaluate('(v)=>__townTest.capture({overlay:v})',['none','roads','neighbourhoods','transit','charter'][iteration%5]);ready(p)
      if iteration%6==0:p.set_viewport_size({'width':390 if iteration%12==0 else 844,'height':844 if iteration%12==0 else 390});ready(p)
      v=inspect_static(p,folder,str(iteration));v.update({'elapsed':round(elapsed,2),'day':p.evaluate('__runningSoak.status().day')});row['checks'].append(v)
      if not options_done and elapsed>60:
       p.evaluate('__webglTaste.focus(26,26,3.5)');ready(p);before=p.evaluate('__webglTaste.actorStats.actors');p.locator('[data-panel=settings]').click();p.locator('[data-option=traffic]').click();closed(p);p.wait_for_timeout(600);m=p.evaluate('__runningSoak.actorMatch()')
       if not m['ok']:row['knownFindings'].append({'kind':'paused-traffic-option-stale-actors','actual':m,'elapsed':round(elapsed,2)});p.screenshot(path=str(folder/'paused-traffic-option-finding.png'))
       p.locator('[data-panel=settings]').click();p.locator('[data-option=traffic]').click();closed(p);options_done=True;row['actions'].append({'kind':'real-traffic-option-roundtrip','initialActors':before,'matchAfterOff':m});ready(p)
      if not loss_done and elapsed>600:
       baseline=p.evaluate('__townTest.save()');p.evaluate('__webglLose=(()=>{const c=document.querySelector("#webglTaste");return(c.getContext("webgl2")||c.getContext("webgl")).getExtension("WEBGL_lose_context")})()');p.evaluate('__webglLose.loseContext()');p.wait_for_function('!window.__webglTaste');assert p.evaluate('__townTest.save()')==baseline;p.locator('[data-panel=settings]').click();q=p.locator('[data-preference=quality]');q.select_option('high'if pref=='low'else'low');q=p.locator('[data-preference=quality]');q.select_option(pref);closed(p);ready(p);assert p.evaluate('JSON.parse(localStorage.getItem("townledger-options")).quality')==pref;assert p.evaluate('__townTest.save()')==baseline;row['actions'].append({'kind':'actual-context-loss-quality-retry','saveUnchanged':True,'savedPreference':pref,'elapsed':round(elapsed,2)});loss_done=True
      if elapsed>=next_sample:
       session=context.new_cdp_session(p);session.send('HeapProfiler.collectGarbage');heap=session.send('Runtime.getHeapUsage');session.detach();sample={**v,'heap':heap,'dom':p.locator('*').count(),'canvases':p.locator('#webglTaste').count(),'overlay':p.locator('#webglMapOverlay').count(),'status':p.evaluate('__runningSoak.status()')};row['samples'].append(sample);p.screenshot(path=str(folder/('sample-'+str(int(next_sample))+'.png')));next_sample+=300
       if elapsed<1500:trade(p,row['actions'])
       if elapsed>850 and elapsed<1300:park(p,row['actions']);plan(p,row['actions'])
      assert not row['errors'],row['errors'];paused(p,False);next_camera=elapsed+30;save()
     p.wait_for_timeout(1000)
    paused(p,True);events(p,row['actions']);paused(p,True);closed(p);row['final']=inspect_static(p,folder,'final');row['finalStatus']=p.evaluate('__runningSoak.status()');row['endUTC']=now();row['elapsedSeconds']=time.monotonic()-start;assert row['elapsedSeconds']>=args.seconds;assert p.evaluate('__cityVisualSave()');assert not row['errors'];row['result']='completed_with_findings'if row['knownFindings']else'completed';save();print(json.dumps({'phase':phase,'result':row['result'],'elapsed':row['elapsedSeconds'],'checks':len(row['checks']),'samples':len(row['samples']),'finalDay':row['finalStatus']['day']}),flush=True)
   except Exception as e:
    row['result']='failed';row['failureUTC']=now();row['failure']=traceback.format_exc();
    try:p.screenshot(path=str(folder/'failure.png'));(folder/'failure-state.json').write_text(p.evaluate('__townTest.save()'))
    except Exception as capture:row['captureFailure']=str(capture)
    save();print(row['failure'],flush=True)
   finally:context.close();browser.close()
 manifest['endUTC']=now();manifest['sourceStillImmutable']=hashes=={str(p.relative_to(R)):sha(p.read_bytes())for p in files};assert manifest['sourceStillImmutable'];save();print('TERMINAL '+json.dumps({'phases':[(p['phase'],p['result'])for p in manifest['phases']],'immutable':True}),flush=True)
finally:server.terminate()
