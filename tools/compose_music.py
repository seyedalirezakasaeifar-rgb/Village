"""Original TownLedger chamber score. Offline synthesis; no samples or borrowed tunes.
Requires numpy and ffmpeg. Deterministic score/arrangement; emits Vorbis assets.
"""
from pathlib import Path
import numpy as np, wave, subprocess, tempfile, json, hashlib
ROOT=Path(__file__).resolve().parents[1];RATE=32000
# Four-bar melodic phrases written for this project; numbers are scale degrees,
# -1 rests. Eight beats per phrase, varied orchestration over64bars.
PHRASES=[[0,2,4,3,2,1,2,4],[4,5,4,2,1,0,-1,2],[2,3,5,4,2,1,0,-1],[0,4,2,1,3,2,1,0],
 [4,2,5,4,3,1,2,-1],[5,4,2,3,1,0,1,-1],[2,4,6,5,4,2,3,1],[3,2,1,2,0,-1,0,-1]]
SCORES=[('morning-ledger',78,60,[0,5,3,4,0,3,1,4],[0,1,2,3]),('river-and-road',92,62,[0,3,5,4,1,3,0,4],[4,0,6,3]),('lamplit-windows',70,57,[5,3,0,4,5,1,3,4],[5,2,7,3])]
SCALE=[0,2,4,5,7,9,11]
def compose(name,bpm,key,progression,phrases):
 beat=60/bpm;length=64*4*beat+5;mix=np.zeros((int(length*RATE),2),np.float32)
 def note(midi,start,duration,gain,pan,voice):
  n=int(duration*RATE);t=np.arange(n,dtype=np.float32)/RATE;f=440*2**((midi-69)/12)
  if voice=='pluck':
   tone=sum(np.sin(2*np.pi*f*h*t)*np.exp(-t*(1.8+h*.7))/(h*h) for h in range(1,6));env=np.minimum(t/.012,1)*np.minimum((duration-t)/.14,1)
  elif voice=='wind':
   phase=2*np.pi*f*(t+.0004*np.sin(2*np.pi*4.2*t));tone=np.sin(phase)+.12*np.sin(phase*2)+.035*np.sin(phase*3);env=np.minimum(t/.12,1)*np.minimum((duration-t)/.3,1)
  else:
   tone=sum(np.sin(2*np.pi*f*h*t+.12*np.sin(2*np.pi*(3+h*.1)*t))/(h*h) for h in range(1,5));env=np.minimum(t/.8,1)*np.minimum((duration-t)/.9,1)
  tone=(tone*np.maximum(env,0)*gain).astype(np.float32);start=int(start*RATE);end=min(len(mix),start+n);tone=tone[:end-start];mix[start:end,0]+=tone*np.sqrt((1-pan)/2);mix[start:end,1]+=tone*np.sqrt((1+pan)/2)
  # Quiet stereo room reflections, not a separate runtime reverb dependency.
  for delay,amount in [(.13,.13),(.29,.08),(.47,.04)]:
   a=start+int(delay*RATE);b=min(len(mix),a+len(tone));mix[a:b,0]+=tone[:b-a]*amount*np.sqrt((1+pan)/2);mix[a:b,1]+=tone[:b-a]*amount*np.sqrt((1-pan)/2)
 def degree(n):return key+SCALE[n%7]+12*(n//7)
 for bar in range(64):
  root=progression[(bar//2)%8];section=bar//16;at=bar*4*beat
  # Sparse alternating chamber voicings leave room for melody and game sounds.
  for j,d in enumerate([root,root+2,root+4]):note(degree(d)-12,at+.04*j,4.5*beat,.035 if section!=2 else .045,[-.55,.3,.55][j],'pad')
  note(degree(root)-24,at,2.8*beat,.07,-.15,'pluck')
  for k in range(4):
   if section==0 and bar%4==3:continue
   d=[root,root+4,root+2,root+4][k];note(degree(d),at+(k+.5)*beat,1.6*beat,.038,-.5 if bar%2 else .45,'pluck')
  # Two-beat notes form breathing16-bar phrases, with section-specific answers.
  phrase=PHRASES[phrases[(bar//4)%4]]
  for k in range(2):
   d=phrase[(bar%4)*2+k]
   if d<0 or section==0 and bar<4:continue
   register=12 if section in (1,2) else 0;note(degree(d)+register,at+k*2*beat,1.65*beat,.055 if section!=2 else .065,.18,'wind')
  if section==2 and bar%2==0:note(degree(root+2)+12,at+3*beat,2*beat,.025,-.3,'wind')
 # Gentle master fades; bounded soft peak normalization avoids clipping.
 ramp=min(int(3*RATE),len(mix)//2);mix[:ramp]*=np.linspace(0,1,ramp)[:,None];mix[-ramp:]*=np.linspace(1,0,ramp)[:,None]
 peak=float(np.max(np.abs(mix)));mix*=.72/max(.72,peak);pcm=(mix*32767).astype('<i2');out=ROOT/'assets/music'/f'{name}.ogg'
 with tempfile.TemporaryDirectory() as td:
  wav=Path(td)/'score.wav'
  with wave.open(str(wav),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','3',str(out)],check=True)
 return {'file':out.name,'title':name.replace('-',' ').title(),'bpm':bpm,'seconds':length,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'rms':float(np.sqrt(np.mean(mix**2))),'peak':float(np.max(np.abs(mix)))}
if __name__=='__main__':
 from compose_extended_score import SCORES as EXTENDED,compose as compose_extended
 (ROOT/'assets/music').mkdir(exist_ok=True)
 rows=[compose(*s) for s in SCORES]+[compose_extended(spec) for spec in EXTENDED]
 (ROOT/'assets/music/score.json').write_text(json.dumps({'original':True,'license':'CC0-1.0','sampleRate':RATE,'tracks':rows},indent=2)+'\n')
 print(rows)
