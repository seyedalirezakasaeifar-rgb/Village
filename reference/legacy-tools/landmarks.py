"""Original multi-tile town landmarks (transparent PNGs)."""
from PIL import Image,ImageDraw
from pathlib import Path
import random,math
ROOT=Path(__file__).resolve().parent.parent/'assets'/'art'
INK='#33413c'
def P(d,p,c,outline=INK,w=3):
 d.polygon(p,fill=c);d.line(p+[p[0]],fill=outline,width=w,joint='curve')
def R(d,r,c,o=None,w=2):d.rectangle(r,fill=c,outline=o,width=w)
def L(d,p,c,w=2):d.line(p,fill=c,width=w)
def make(k,seed=0):
 W=224;H=240;im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
 d.ellipse((23,177,206,213),fill='#29413963')
 # Dark woodland garden and stone walk occupying 2x2 parcels
 P(d,[(19,164),(109,117),(205,160),(112,207)],'#b6b38a','#78816b',2)
 for j in range(11):
  x=(j*19+seed*11)%180+19;y=174+(j*7)%30
  R(d,(x,y,x+3,y+2),'#708e61')
 if k=='farm':
  # Red barn and hayloft, ladder, fencing and independent grain silo
  R(d,(48,106,145,183),'#ad5f4e',INK,3);R(d,(51,109,58,180),'#7e453b');R(d,(137,109,143,178),'#7e453b')
  P(d,[(37,110),(95,57),(157,108),(95,126)],'#b75949')
  P(d,[(37,110),(95,57),(157,108),(95,126)],None,'#53392f',3)
  for y in (83,97):L(d,[(55,y+13),(94,y-21),(141,y+12)],'#db8d68',2)
  R(d,(79,138,117,184),'#584c40','#e9cd9b',3)
  L(d,[(79,138),(117,184)],'#e1b388',3);L(d,[(117,138),(79,184)],'#e1b388',3)
  P(d,[(85,117),(95,103),(105,117)],'#ead5a6');R(d,(90,117,102,128),'#4e696e','#f2d79d',2)
  R(d,(159,74,186,180),'#bbb79e','#5f655a',3);d.ellipse((159,63,187,83),fill='#d4cba9',outline=INK,width=3)
  R(d,(162,105,183,108),'#8b8d7e');R(d,(163,135,183,139),'#8b8d7e');R(d,(165,175,182,181),'#657b5c')
  for x,y in ((31,180),(40,184),(160,191),(179,190)):
   R(d,(x,y,x+19,y+9),'#d2b76d','#8c824f',2)
   for xx in (x+4,x+10,x+16):L(d,[(xx,y+1),(xx+2,y+8)],'#e9cf86',1)
  for x in range(36,81,11):R(d,(x,194,x+3,205),'#f2e3bd',INK,1)
  L(d,[(37,200),(80,200)],'#eee1be',3)
  # A pair of chickens roaming the yard
  for x,y in ((121,193),(132,200)):
   d.ellipse((x,y,x+8,y+6),fill='#f1ece0',outline='#7e725d',width=1);R(d,(x+8,y+1,x+11,y+3),'#d59c52')
 elif k in ('tower','apartment'):
  floors=10 if k=='tower' else 5;top=19 if k=='tower' else 80
  color='#9bbec2' if k=='tower' else '#d3ac90';edge='#5d838b' if k=='tower' else '#a57565'
  P(d,[(50,top+20),(113,top-8),(174,top+20),(111,top+47)],'#4b6e7b' if k=='tower' else '#765b57')
  P(d,[(50,top+20),(111,top+47),(111,177),(50,151)],edge)
  P(d,[(111,top+47),(174,top+20),(174,150),(111,177)],color)
  for i in range(floors):
   y=top+36+i*(120/floors)
   for x in (63,81,100):
    R(d,(x,int(y),x+10,int(y+6)),('#f6dd9b' if (i+x//10)%4==0 else '#badbd7'),'#355664',1)
   for x in (123,145,161):
    R(d,(x,int(y-8),x+10,int(y-2)),('#fff1bd' if (i+x//7)%4==0 else '#b5d3d5'),'#5b797b',1)
   if i%2==0:
    L(d,[(51,int(y+10)),(111,int(y+35))],'#d2d5ce',2)
    L(d,[(111,int(y+35)),(173,int(y+9))],'#f4eee0',2)
  R(d,(98,163,115,185),'#354e53','#c1c4ad',2)
  if k=='tower':R(d,(110,top-26,115,top-6),'#94b5b9');R(d,(95,top-26,132,top-23),'#dfe6d8')
 elif k=='factory':
  R(d,(32,105,177,185),'#89989e',INK,3)
  for j in range(4):
   x=32+j*37;P(d,[(x,107),(x+18,83),(x+37,107)],'#c7c8bb');L(d,[(x,107),(x+36,107)],'#50656c',3)
  for x in range(43,175,20):R(d,(x,125,x+13,147),'#a2c7bd',INK,2)
  R(d,(78,163,112,185),'#4b676e',INK,2)
  for x,y in ((144,26),(167,38)):
   R(d,(x,y,x+17,116),'#646f72',INK,3);R(d,(x-3,y-5,x+19,y+1),'#e1c8a4',INK,2)
  for x in range(35,78,14):R(d,(x,191,x+11,199),'#cba46b',INK,1)
 elif k=='warehouse':
  P(d,[(26,109),(102,62),(192,103),(119,148)],'#a2a496')
  P(d,[(27,112),(119,151),(119,187),(27,147)],'#a99f8b')
  P(d,[(119,151),(191,108),(191,151),(119,187)],'#c6b89a')
  for y in (78,91,105):L(d,[(49,y+20),(105,y-13),(175,y+16)],'#798786',3)
  for x in (126,150,174):R(d,(x,145,x+18,173),'#5b6c6c',INK,2)
  for x in (40,68,94):R(d,(x,163,x+19,186),'#5b6261','#decbb2',2)
  R(d,(123,186,158,200),'#ba965f',INK,1)
 elif k=='metro_station':
  R(d,(33,104,188,179),'#73958d',INK,3)
  P(d,[(26,108),(107,65),(196,102),(111,149)],'#396d76')
  P(d,[(26,108),(107,65),(196,102),(111,149)],None,'#e1e6cb',3)
  for x in range(45,174,23):
   R(d,(x,123,x+16,154),'#a8d4cf',INK,2)
   L(d,[(x+7,125),(x+7,150)],'#eaf5dc',2)
  R(d,(84,155,127,184),'#2d444a',INK,3)
  for x,y in ((92,177),(94,182),(96,187),(98,192)):L(d,[(x,y),(132-x+92,y)],'#acb9b0',3)
  d.ellipse((101,24,153,76),fill='#d2dcad',outline=INK,width=4)
  R(d,(119,30,130,65),'#436d6c');R(d,(108,41,142,51),'#436d6c')
 elif k=='airport':
  R(d,(25,110,191,174),'#adbeb8',INK,3)
  P(d,[(20,109),(102,67),(198,104),(116,145)],'#d6d9ce')
  for x in range(38,184,22):R(d,(x,126,x+17,153),'#6c9faa',INK,2)
  R(d,(107,152,142,186),'#657f80',INK,2)
  R(d,(153,37,175,121),'#788f8d',INK,3)
  R(d,(147,33,181,55),'#cbd9d1',INK,3)
  for x in (151,160,169):R(d,(x,39,x+7,47),'#4e7786')
  L(d,[(170,34),(170,16)],'#6c7374',3)
 elif k in ('school','college'):
  R(d,(27,90,185,179),'#c0b39b',INK,3)
  P(d,[(19,95),(107,45),(197,94),(109,142)],'#a5765f')
  for x in range(43,179,24):
   R(d,(x,118,x+16,148),'#8da8a4',INK,2)
   L(d,[(x+8,121),(x+8,145)],'#fff4d1',2)
  R(d,(100,154,124,183),'#596455',INK,2)
  R(d,(103,39,123,69),'#ded4b4',INK,2)
  d.ellipse((108,39,122,54),fill='#d6c97c',outline=INK,width=1)
 else:raise ValueError(k)
 return im
if __name__=='__main__':
 for kind in ('farm','tower','apartment','factory','warehouse','metro_station','airport','school','college'):
  im=make(kind);im.save(ROOT/(kind+'-0.png'),optimize=True)
 print('Wrote 9 original multi-tile landmark sprites')
