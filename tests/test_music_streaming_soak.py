"""Real streaming resource churn and foreground playback; no listening claim.

Run with AUDIO_SOAK_SECONDS=180 AUDIO_SOAK_HANDOFFS=100 (the defaults).
Only the fade clock is accelerated during handoffs; HTML media playback/decoder,
network, seeks, controls, promises and foreground dwell use the real browser.
This is resource-turnover evidence, not hours of continuous playback or Android QA.
"""
from test_mobile_rendering import ROOT
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import hashlib, json, os, threading, time

class Handler(SimpleHTTPRequestHandler):
 def log_message(self, *args): pass

source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
music=(ROOT/'src/95-music.js').read_text()
instrumented=music.replace('const started=performance.now()', 'const started=window.__scoreNow()').replace('(performance.now()-started)', '(window.__scoreNow()-started)')
assert instrumented!=music
source=source.replace(music,instrumented).replace('// SOURCE: 99-instrumentation.js', 'window.__scoreEval=s=>eval(s);\n// SOURCE: 99-instrumentation.js')
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'assets')))
threading.Thread(target=server.serve_forever,daemon=True).start()
handoffs=int(os.environ.get('AUDIO_SOAK_HANDOFFS','100'));dwell=int(os.environ.get('AUDIO_SOAK_SECONDS','180'))
rows=[];errors=[];metadata=[];sequence=[];started=time.monotonic()
with sync_playwright() as pw:
 before={p.name for p in Path('/proc').iterdir() if p.name.isdigit()}
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 roots=[]
 for proc in Path('/proc').iterdir():
  if proc.name.isdigit() and proc.name not in before:
   try:
    command=(proc/'cmdline').read_bytes()
    if b'--remote-debugging-pipe' in command and b'--type=' not in command:roots.append(int(proc.name))
   except (PermissionError,FileNotFoundError,ProcessLookupError):pass
 assert len(roots)==1,roots
 page=browser.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
 page.add_init_script('window.__scoreOffset=0;window.__scoreNow=()=>performance.now()+window.__scoreOffset')
 page.route('**/game.js',lambda route:route.fulfill(body=source,content_type='application/javascript'))
 page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
 def ev(s): return page.evaluate('(s)=>__scoreEval(s)',s)
 cdp=page.context.new_cdp_session(page);cdp.send('Performance.enable')
 def snapshot(label):
  cdp.send('HeapProfiler.collectGarbage')
  prototype=cdp.send('Runtime.evaluate',{'expression':'HTMLAudioElement.prototype','objectGroup':'audio-soak'})['result']['objectId']
  objects=cdp.send('Runtime.queryObjects',{'prototypeObjectId':prototype,'objectGroup':'audio-soak'})['objects']['objectId']
  media=cdp.send('Runtime.callFunctionOn',{'objectId':objects,'functionDeclaration':"function(){return Array.from(this).map(a=>({src:a.getAttribute('src'),paused:a.paused,time:a.currentTime}));}",'returnByValue':True})['result']['value']
  cdp.send('Runtime.releaseObjectGroup',{'objectGroup':'audio-soak'})
  metrics={m['name']:m['value'] for m in cdp.send('Performance.getMetrics')['metrics']}
  pss=0;processes=0
  parents={}
  for proc in Path('/proc').iterdir():
   if proc.name.isdigit():
    try:parents[int(proc.name)]=int((proc/'stat').read_text().rsplit(')',1)[1].split()[1])
    except (PermissionError,FileNotFoundError,ProcessLookupError):pass
  family=set(roots)
  while True:
   expanded=family|{pid for pid,parent in parents.items() if parent in family}
   if expanded==family:break
   family=expanded
  for pid in family:
   proc=Path('/proc')/str(pid)
   if proc.exists():
    try:
     if 'chrom' not in (proc/'comm').read_text():continue
     values=(proc/'smaps_rollup').read_text().splitlines()
     pss+=next(int(line.split()[1])*1024 for line in values if line.startswith('Pss:'));processes+=1
    except (PermissionError,FileNotFoundError,ProcessLookupError):pass
  row={'label':label,'seconds':round(time.monotonic()-started,2),'heapBytes':metrics['JSHeapUsedSize'],'processPssBytes':pss,'chromiumProcesses':processes,'media':media,'referencedDecks':ev('musicDecks.length'),'history':ev('musicHistory.slice()')};rows.append(row)
  print(label, 'media:',len(media),'heap:',int(row['heapBytes']),'process PSS:',pss,flush=True)
  assert len([a for a in media if a['src'] and a['src'].startswith('music/')])<=2,row
  assert row['referencedDecks']<=2,row
 page.locator('#newTown').click();page.locator('#pause').click();page.locator('#panelClose').click()
 page.wait_for_function('__scoreEval("musicDecks.some(d=>!d.audio.paused&&d.audio.currentTime>0)")')
 page.locator('[data-panel=settings]').click()
 def finish_fade():
  page.wait_for_function('__scoreEval("!!musicFade")')
  page.evaluate('window.__scoreOffset+=9000')
  page.wait_for_function('__scoreEval("!musicFade&&musicDecks.length===1&&musicDecks[0].gain===1")')
 finish_fade();snapshot('initial')
 for i in range(handoffs):
  page.locator('#musicNext').click()
  page.wait_for_function('__scoreEval("musicDecks.some(d=>d.index===musicTrack&&!d.audio.paused&&d.audio.currentTime>0)")')
  current=ev('({index:musicTrack,history:musicHistory.slice(),duration:musicDecks[musicDecks.length-1].audio.duration,expected:MUSIC_TRACKS[musicTrack].seconds})')
  assert current['index'] not in sequence[-6:],(sequence[-6:],current)
  metadata.append(current);sequence.append(current['index'])
  # Interrupted handoffs exercise native pause/resume on actual media elements.
  if i%9==0:
   ev('__townArchive.suspend()');assert ev('musicDecks.every(d=>d.audio.paused)&&!musicFade&&musicDecks.length===1')
   ev('__townArchive.resume()')
   page.wait_for_function('__scoreEval("musicDecks.some(d=>!d.audio.paused&&d.audio.currentTime>0)")')
  else:finish_fade()
  assert not ev('musicError')
  if i%20==19:snapshot('handoff-'+str(i+1))
 # Genuine trusted clicks with no decoder/fade waits between them.
 for _ in range(12):page.locator('#musicNext').click()
 page.wait_for_function('__scoreEval("!!musicFade")');finish_fade();snapshot('rapid-next-burst')
 # Real foreground dwell after resource turnover; no fade acceleration here.
 deadline=time.monotonic()+dwell
 while time.monotonic()<deadline:
  page.wait_for_timeout(min(30000,max(1,(deadline-time.monotonic())*1000)))
  assert not ev('musicError')
 snapshot('foreground-dwell')
 assert ev('musicDecks.some(d=>!d.audio.paused&&d.audio.currentTime>0)')
 # Mute/zero/hidden suppress playback; returning never restarts from zero.
 page.locator('#musicVolume').fill('0');assert ev('musicDecks.every(d=>d.audio.paused)')
 resume_position=ev('({index:musicTrack,time:musicDecks[0].audio.currentTime})')
 page.locator('#musicVolume').fill('45')
 page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'))")
 assert ev('musicDecks.every(d=>d.audio.paused)')
 page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:false});document.dispatchEvent(new Event('visibilitychange'))")
 page.wait_for_function('__scoreEval("musicDecks.some(d=>!d.audio.paused)")');snapshot('final-resume')
 assert ev('musicTrack')==resume_position['index']
 assert ev('musicDecks[0].audio.currentTime')>=resume_position['time']-.05
 assert not errors,errors
 browser.close()
server.shutdown();server.server_close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/audio-experience';out.mkdir(exist_ok=True)
report={'source_sha256':sha,'realMedia':True,'acceleratedFadeClockOnly':True,'manualHandoffs':handoffs,'foregroundDwellSeconds':dwell,'elapsedSeconds':round(time.monotonic()-started,2),'metadata':metadata,'snapshots':rows,'errors':errors,'subjectiveListening':False,'physicalAndroid':False}
(out/'streaming-soak.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS real streaming handoffs, native interruptions, foreground dwell, zero volume and hidden resume;',handoffs,'handoffs;',dwell,'seconds dwell;',len(rows),'resource snapshots')
