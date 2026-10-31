"""Real media playback, decoded score signal and bounded contextual selection.
No subjective listening or physical speaker claim is made.
"""
from test_mobile_rendering import ROOT
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,hashlib

class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'assets')))
threading.Thread(target=server.serve_forever,daemon=True).start()
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest();errors=[]
probe=r'''
window.__musicEval=s=>eval(s);
window.__musicSelectionCheck=()=>{
 const previous={history:musicHistory.slice(),track:musicTrack,mood:musicMood,random:musicRandomState},economic=rngState,saved=archivePayload(),sequence=[];
 try{musicHistory=[];musicTrack=-1;musicRandomState=12345;
  for(let i=0;i<100;i++){const recent=musicHistory.slice(),index=chooseMusicTrack();if(recent.includes(MUSIC_TRACKS[index].file)||index===musicTrack)throw Error('Repeated recent piece');musicTrack=index;recordMusicPlayback(index);sequence.push(index);}
  if(new Set(sequence).size!==MUSIC_TRACKS.length)throw Error('Playlist omitted pieces');
  const count=mood=>{musicMood=mood;musicRandomState=121212;musicHistory=[];musicTrack=-1;let quiet=0;for(let i=0;i<400;i++){const t=MUSIC_TRACKS[chooseMusicTrack()];quiet+=t.tags.some(tag=>['quiet','evening'].includes(tag));}return quiet;};
  const quiet=count('quiet'),lively=count('lively');if(quiet<=lively)throw Error('Character preference ignored');if(rngState!==economic||archivePayload()!==saved)throw Error('Score selection mutated economy');
  return {pieces:MUSIC_TRACKS.length,seconds:MUSIC_TRACKS.reduce((n,t)=>n+t.seconds,0),selections:sequence.length,unique:new Set(sequence).size,noRepeatWindow:MUSIC_RECENT_LIMIT,quietSelections:quiet,livelyQuietSelections:lively,economicStateUnchanged:true};
 }finally{musicHistory=previous.history;musicTrack=previous.track;musicMood=previous.mood;musicRandomState=previous.random;rememberMusic();}
};
'''
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
 page.route('**/game.js',lambda route:route.fulfill(body=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'),content_type='application/javascript'))
 page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
 def ev(expression):return page.evaluate('(s)=>{const v=__musicEval(s);return typeof v==="function"?v():v}',expression)
 assert ev('musicDecks.length')==0
 page.locator('#newTown').click();page.locator('#pause').click();page.locator('#panelClose').click()
 page.wait_for_function('__musicEval("musicDecks.some(d=>!d.audio.paused&&d.audio.currentTime>0)")')
 selection=ev('__musicSelectionCheck()');assert selection['seconds']>2700 and selection['pieces']==10
 page.locator('[data-panel=settings]').click();page.locator('#soundToggle').click();assert ev('musicDecks.some(d=>!d.audio.paused)')
 page.locator('#musicVolume').fill('25');assert ev('musicVolume')==.25
 page.locator('#musicMood').select_option('quiet');assert ev('musicMood')=='quiet'
 page.locator('#musicToggle').click();assert ev('musicDecks.every(d=>d.audio.paused)')
 page.locator('#musicToggle').click();page.wait_for_function('__musicEval("musicDecks.some(d=>!d.audio.paused)")')
 ev('__townArchive.suspend()');assert ev('musicDecks.every(d=>d.audio.paused)')
 ev('__townArchive.resume()');page.wait_for_function('__musicEval("musicDecks.some(d=>!d.audio.paused)")')
 page.locator('#musicNext').click();page.wait_for_function('__musicEval("!musicFade && musicDecks.length===1 && musicDecks[0].gain===1")')
 old=ev('musicTrack')
 ev('()=>{const a=musicDecks[0].audio;Object.defineProperty(a,"currentTime",{configurable:true,value:MUSIC_TRACKS[musicTrack].seconds-3});a.dispatchEvent(new Event("timeupdate"))}')
 page.wait_for_function('__musicEval("musicTrack")!=='+str(old));assert ev('musicDecks.length')<=2
 page.wait_for_function('__musicEval("musicDecks.some(d=>d.index===musicTrack&&!d.audio.paused&&d.audio.currentTime>0)")')
 assert ev('musicError')==''
 # Release each large decoded buffer between browser jobs; production streams
 # through HTML media and never keeps a decoded-buffer playlist.
 tracks=ev('MUSIC_TRACKS');decoded=[];cdp=page.context.new_cdp_session(page)
 for i in range(len(tracks)):
  decoded.append(ev('''async()=>{const t=MUSIC_TRACKS['''+str(i)+'''],ctx=new AudioContext();try{const a=await ctx.decodeAudioData(await(await fetch('music/'+t.file+'.ogg')).arrayBuffer()),v=a.getChannelData(0);let energy=0,peak=0;for(let j=0;j<v.length;j+=32){energy+=v[j]*v[j];peak=Math.max(peak,Math.abs(v[j]));}return{file:t.file,seconds:a.duration,channels:a.numberOfChannels,rms:Math.sqrt(energy/Math.ceil(v.length/32)),peak};}finally{await ctx.close();}}'''))
  cdp.send('HeapProfiler.collectGarbage')
 assert all(abs(a['seconds']-b['seconds'])<.05 for a,b in zip(decoded,tracks)),decoded
 assert all(t['seconds']>170 and t['channels']==2 and .005<t['rms']<.3 and t['peak']<.99 for t in decoded),decoded
 page.reload();assert ev('musicVolume')==.25 and ev('musicMood')=='quiet';assert ev('musicDecks.length')==0
 assert not errors,errors;browser.close()
server.shutdown();server.server_close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-8.0';out.mkdir(exist_ok=True)
(out/'music.json').write_text(json.dumps({'source_sha256':sha,'selection':selection,'decoded':decoded,'realMediaPlayback':True,'subjectiveListening':False,'errors':errors},indent=2)+'\n')
print('PASS ten original pieces decode with nonzero signal, real gesture playback, contextual/no-repeat selection, independent controls, host pause/resume, natural handoff and preference persistence',selection)
