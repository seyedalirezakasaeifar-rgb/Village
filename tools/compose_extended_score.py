"""Seven original longer arrangements for TownLedger; deterministic offline synthesis.
No samples or quoted melodies. Degrees, harmonic plans and section forms are authored here.
"""
from pathlib import Path
import hashlib,json,subprocess,tempfile,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
RATE=32000
SCORES=[
 dict(name='orchard-footpaths',title='Orchard Footpaths',bpm=72,key=65,mode=[0,2,4,6,7,9,11],beats=3,bars=112,tags=['home','quiet'],roots=[0,3,1,4,0,5,3,4],motifs=[[0,2,4,5,4,2,1,0],[2,3,5,4,2,1,2,-1],[4,6,5,3,2,4,1,0]],voice='wood',seed=103),
 dict(name='rails-to-greyhaven',title='Rails to Greyhaven',bpm=94,key=62,mode=[0,2,4,5,7,9,11],beats=4,bars=112,tags=['trade','work'],roots=[0,4,5,3,1,4,3,0],motifs=[[0,4,2,5,4,1,2,0],[2,4,6,5,3,2,1,-1],[4,5,7,6,4,2,3,1]],voice='piano',seed=211),
 dict(name='waterline-work',title='Work at the Waterline',bpm=84,key=67,mode=[0,2,3,5,7,9,10],beats=3,bars=128,tags=['water','trade'],roots=[0,3,0,4,5,3,1,4],motifs=[[0,2,3,5,4,3,1,0],[4,2,5,6,4,3,2,-1],[2,4,3,1,0,2,1,0]],voice='wood',seed=317),
 dict(name='market-day',title='The Long Market Day',bpm=88,key=58,mode=[0,2,4,5,7,9,11],beats=4,bars=112,tags=['market','home'],roots=[0,5,1,4,3,0,1,4],motifs=[[2,4,5,4,2,3,1,0],[4,7,6,5,4,2,1,-1],[0,1,3,4,2,5,3,2]],voice='piano',seed=419),
 dict(name='after-the-rain',title='Rooms after the Rain',bpm=66,key=60,mode=[0,2,3,5,7,9,10],beats=4,bars=104,tags=['evening','quiet'],roots=[0,5,3,1,0,4,3,0],motifs=[[4,3,2,-1,1,0,2,0],[2,5,4,3,1,2,0,-1],[0,2,4,3,5,4,2,1]],voice='wind',seed=523),
 dict(name='a-borough-grows',title='A Borough Grows',bpm=76,key=67,mode=[0,2,4,5,7,9,11],beats=4,bars=112,tags=['growth','home'],roots=[0,3,5,4,1,3,4,0],motifs=[[0,2,4,7,6,4,3,2],[4,5,6,4,2,1,3,2],[2,4,5,7,5,3,2,0]],voice='wind',seed=631),
 dict(name='quiet-river-reprise',title='The Quiet River',bpm=64,key=65,mode=[0,2,4,5,7,9,11],beats=3,bars=128,tags=['water','evening','quiet'],roots=[0,3,1,5,3,0,4,0],motifs=[[0,-1,2,4,3,2,0,-1],[2,4,5,-1,4,2,1,0],[4,2,3,1,2,0,-1,0]],voice='wood',seed=739),
]

def compose(spec):
 beat=60/spec['bpm'];bar_beats=spec['beats'];duration=spec['bars']*bar_beats*beat+1.5
 mix=np.zeros((int(duration*RATE),2),np.float32);rng=np.random.default_rng(spec['seed'])
 def degree(n):return spec['key']+spec['mode'][n%7]+12*(n//7)
 def add(midi,start,length,gain,pan,voice):
  n=max(1,int(length*RATE));t=np.arange(n,dtype=np.float32)/RATE;f=440*2**((midi-69)/12)
  if voice in ['piano','wood']:
   tone=np.zeros(n,np.float32)
   for h in range(1,7):tone+=np.sin(2*np.pi*f*h*(1+.00012*h*h)*t)*np.exp(-t*(1.1+h*.55))/(h**(1.7 if voice=='piano' else 2.2))
   attack=.006 if voice=='piano' else .014
  elif voice=='wind':
   phase=2*np.pi*f*t+.018*np.sin(2*np.pi*4.6*t);tone=np.sin(phase)+.16*np.sin(2*phase)+.035*np.sin(3*phase);attack=.12
  elif voice=='bass':tone=np.sin(2*np.pi*f*t)+.23*np.sin(2*np.pi*f*2*t)*np.exp(-t*2);attack=.035
  else:
   tone=sum(np.sin(2*np.pi*f*h*t+.04*np.sin(2*np.pi*(3.2+h*.11)*t))/(h*h) for h in range(1,5));attack=.65
  env=np.minimum(t/attack,1)*np.minimum((length-t)/min(.6,length*.3),1);tone=(tone*np.maximum(env,0)*gain).astype(np.float32)
  at=int(start*RATE);end=min(len(mix),at+n)
  if at>=len(mix):return
  tone=tone[:end-at];left=np.sqrt((1-pan)/2);right=np.sqrt((1+pan)/2)
  mix[at:end,0]+=tone*left;mix[at:end,1]+=tone*right
  for delay,level in [(.11,.11),(.23,.065),(.37,.035)]:
   a=at+int(delay*RATE);b=min(len(mix),a+len(tone))
   if b>a:mix[a:b,0]+=tone[:b-a]*level*right;mix[a:b,1]+=tone[:b-a]*level*left
 def brush(start,gain):
  n=int(.14*RATE);t=np.arange(n)/RATE;v=rng.normal(0,1,n).astype(np.float32);v=np.diff(v,prepend=v[0])*.4*np.exp(-t*32)*np.minimum(t/.003,1)*gain;a=int(start*RATE);b=min(len(mix),a+n)
  if b>a:mix[a:b,0]+=v[:b-a]*.7;mix[a:b,1]+=v[:b-a]*.6
 # A / response / A' / bridge / open chorus / response / coda. Section-specific
 # register, density and orchestration change together; no runtime random notes.
 form=[0,1,0,2,3,1,4,4]
 for bar in range(spec['bars']):
  section=form[min(len(form)-1,bar//16)];local=bar%16;root=spec['roots'][(bar//2+(2 if section==2 else 0))%8];at=bar*bar_beats*beat
  coda=bar>=spec['bars']-8;energy=.62 if section in [0,4] else .82 if section==2 else 1
  if coda:energy*=max(.35,(spec['bars']-bar)/8)
  voicing=[root,root+2,root+4] if section!=2 else [root,root+4,root+6]
  for j,d in enumerate(voicing):add(degree(d)-12,at+j*.023,bar_beats*beat+.22,.033*energy,[-.5,.1,.5][j],'strings')
  add(degree(root)-24,at,bar_beats*beat*.82,.062*energy,-.12,'bass')
  if not coda or bar%2==0:
   pulses=bar_beats if section in [0,4] else bar_beats*2
   for k in range(pulses):
    if section in [0,4] and (bar+k)%4==3:continue
    d=[root,root+4,root+2,root+6][(k+bar%2)%4];add(degree(d),at+(k+.3)*bar_beats/pulses*beat,1.2*beat,.024*energy,-.48 if k%2 else .4,'wood')
  motif=spec['motifs'][(bar//4+(1 if section==2 else 0))%len(spec['motifs'])]
  for k in range(2):
   d=motif[(bar%4)*2+k]
   if d<0 or section==0 and local<2 or coda and bar%2:continue
   register=12 if section==3 else 0
   add(degree(d)+register,at+k*bar_beats*.5*beat,bar_beats*.43*beat,.060*energy,.16,spec['voice'])
  if section==1 and local%4==3:
   answer=spec['motifs'][1][(local//4)%8]
   if answer>=0:add(degree(answer+2),at+bar_beats*.66*beat,bar_beats*.6*beat,.028,-.27,'wind')
  if section==3 and bar%4==1:add(degree(root+6)+12,at+beat,bar_beats*beat*.7,.022,-.3,'wind')
  if 'work' in spec['tags'] or 'market' in spec['tags']:
   if section in [1,3] and not coda:
    brush(at+beat*.95,.012);brush(at+beat*(bar_beats-.12),.009)
 # Match broad loudness without flattening authored section dynamics.
 rms=float(np.sqrt(np.mean(mix**2)));peak=float(np.max(np.abs(mix)));mix*=min(.065/max(rms,1e-6),.58/max(peak,1e-6))
 for seconds,front in [(.6,True),(1.0,False)]:
  n=int(seconds*RATE);ramp=np.linspace(0,1,n,dtype=np.float32)[:,None]
  if front:mix[:n]*=ramp
  else:mix[-n:]*=ramp[::-1]
 out=ROOT/'assets/music'/(spec['name']+'.ogg')
 with tempfile.TemporaryDirectory() as td:
  wav=Path(td)/'score.wav'
  with wave.open(str(wav),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes((mix*32767).astype('<i2').tobytes())
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','2',str(out)],check=True)
 return {'file':out.name,'title':spec['title'],'bpm':spec['bpm'],'seconds':duration,'tags':spec['tags'],'bars':spec['bars'],'beatsPerBar':bar_beats,'sections':['opening','response','return','bridge','open chorus','response','coda'],'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'rms':float(np.sqrt(np.mean(mix**2))),'peak':float(np.max(np.abs(mix)))}

if __name__=='__main__':
 rows=[]
 for spec in SCORES:
  row=compose(spec);rows.append(row);print(row['file'],round(row['seconds'],1),flush=True)
 legacy=json.loads((ROOT/'assets/music/score.json').read_text())['tracks'];legacy=[r for r in legacy if r['file'] in ['morning-ledger.ogg','river-and-road.ogg','lamplit-windows.ogg']]
 (ROOT/'assets/music/score.json').write_text(json.dumps({'original':True,'license':'CC0-1.0','sampleRate':RATE,'tracks':legacy+rows},indent=2)+'\n')
 print('Original score minutes',round(sum(r['seconds'] for r in legacy+rows)/60,2),flush=True)
