"""Original, deterministic pixel-art sprites for the TownLedger isometric renderer.
All assets made with Pillow primitives; no external game artwork and no copyrighted sprites.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import random, math
ROOT=Path(__file__).resolve().parent.parent/'assets'/'art'
ROOT.mkdir(parents=True,exist_ok=True)
INK='#293b35'
COLORS=[('#edb4a1','#a33f47','#faf0d4'),('#edca90','#b95b39','#f4dfba'),('#a8cabd','#547c83','#f4e7c8'),('#c8b6df','#7d5b96','#fbedd9'),('#edc2a7','#aa7861','#f3dfc2'),('#b0cde4','#457a9d','#f5f0d9'),('#f2cf85','#af6338','#f9e5bb'),('#b5d0a6','#507b58','#f9f1d4'),('#daa7af','#854b71','#fff0d4'),('#e3c79d','#84715f','#fff1d1'),('#a7cbcd','#54738b','#ecf5e2'),('#edb0a2','#8f4e68','#f7e9cf'),('#b9bfe2','#5d688a','#fae8df'),('#d8deb2','#77874c','#fff1d2'),('#ebccae','#ab6048','#e9ded2'),('#aeb7cc','#4c668b','#fff2df')]

def rect(d,xy,fill,outline=None,w=1):d.rectangle(tuple(map(int,xy)),fill=fill,outline=outline,width=w)
def poly(d,xy,fill,outline=INK,w=2):d.polygon([(int(x),int(y)) for x,y in xy],fill=fill);d.line([(int(x),int(y)) for x,y in xy]+[(int(xy[0][0]),int(xy[0][1]))],fill=outline,width=w,joint='curve')
def line(d,xy,fill=INK,w=2):d.line(xy,fill=fill,width=w)
def dot(d,x,y,c,n=2):rect(d,(x,y,x+n,y+n),c)
def brighten(c,amount=1.2):
 h=c.lstrip('#');t=[int(h[i:i+2],16) for i in (0,2,4)];return '#'+''.join(f'{min(255,int(v*amount)):02x}' for v in t)
def darken(c,amt=.7):
 h=c.lstrip('#');return '#'+''.join(f'{max(0,int(int(h[i:i+2],16)*amt)):02x}' for i in (0,2,4))
def shadow(d):d.ellipse((15,108,117,131),fill='#273e3558')
def garden(d,seed):
 r=random.Random(seed)
 # Border of flowers around a compact front garden
 for i in range(12):
  x=r.randint(20,109);y=r.randint(110,131)
  if r.random()<.5:continue
  dot(d,x,y,r.choice(['#366b50','#4c985a','#83a447']),2)
  if r.random()>.35:dot(d,x+1,y-2,r.choice(['#f5e8a4','#ff9fb1','#f8a76f','#dba4e8']),2)
 for x in range(19,110,10):
  if seed%4==0: rect(d,(x,117,x+4,119),'#efe5c3',INK,1)

def home(seed):
 r=random.Random(seed*201+934)
 wall,roof,trim=COLORS[seed%len(COLORS)]
 image=Image.new('RGBA',(128,144));d=ImageDraw.Draw(image)
 shadow(d);garden(d,seed)
 # Foundation and warm stone pathway
 poly(d,[(21,97),(62,119),(111,95),(68,75)],'#8a775c',None,0)
 poly(d,[(24,90),(64,112),(105,91),(65,67)],'#dbc39a',None,0)
 for k in range(4):rect(d,(57+k*2,117+k*3,67+k*3,119+k*3),'#baad84')
 # Deep side walls with crisp vertical face separation
 poly(d,[(23,57),(65,80),(65,114),(23,92)],darken(wall,.78))
 poly(d,[(65,80),(106,57),(106,96),(65,114)],wall)
 # Timber beams or stone siding pattern
 if seed%4==0:
  for z in (72,94):line(d,[(24,z),(65,z+22)],darken(wall,.67),2)
 elif seed%4==1:
  for z in (83,99):line(d,[(66,z),(104,z-21)],brighten(wall,1.07),1)
 elif seed%4==2:
  for z in (81,100):
   for x in (77,91):rect(d,(x,z-3,x+6,z),darken(wall,.91))
 # Upper steep sloped asymmetrical roof
 roofhighlight=brighten(roof,1.19)
 poly(d,[(12,60),(54,25),(79,29),(66,78)],roofhighlight)
 poly(d,[(66,78),(79,29),(119,57),(105,68)],roof)
 poly(d,[(12,60),(66,78),(105,68),(119,57),(106,62),(66,84),(12,65)],darken(roof,.66),None,0)
 # Roof tiles, alternating colored rows
 for j in range(5):
  yy=37+j*8
  for k in range(6):
   xx=29+k*6-j*2
   if 20<xx<65 and yy<64:
    d.line([(xx,yy),(xx+4,yy+2)],fill=darken(roof,.78),width=1)
 for j in range(5):
  x=81+j*7
  for y in range(43,57,5):d.line([(x,y),(x+3,y+1)],fill=darken(roof,.68),width=1)
 # Chimney, irregular brickwork
 if seed%5!=2:
  cx=74 if seed%2 else 42;cy=27 if cx==42 else 20
  rect(d,(cx,cy-14,cx+10,cy+12),'#b68e77',INK,2);rect(d,(cx-2,cy-16,cx+12,cy-12),'#f8debd',INK,1)
  for y in (cy-7,cy+1,cy+7):line(d,[(cx+1,y),(cx+9,y)],'#765b4f',1)
 # Roof dormer on alternate homes
 if seed%3==2:
  poly(d,[(43,44),(54,31),(65,43)],'#e6cead')
  rect(d,(50,44,59,55),'#3f6a6b','#e9d4ad',2)
 # Lit windows and shutters; face-specific perspective
 for xx,yy in [(35,75),(83,77)]:
  rect(d,(xx-3,yy-3,xx+13,yy+16),darken(roof,.76),INK,2)
  rect(d,(xx,yy,xx+10,yy+12),r.choice(['#d0e5d5','#a6cfd2','#fbe0a1']), '#fff5d7',1)
  line(d,[(xx+5,yy),(xx+5,yy+12)],'#fdf2d6',2)
  line(d,[(xx,yy+6),(xx+10,yy+6)],'#fff4d4',1)
  rect(d,(xx-4,yy,xx-2,yy+13),darken(roof,.8));rect(d,(xx+12,yy,xx+14,yy+13),darken(roof,.8))
  rect(d,(xx-1,yy+13,xx+12,yy+15),'#9d7959')
 # Hand-worked wood door and stone threshold
 poly(d,[(64,94),(77,88),(77,106),(64,114)],'#735b49')
 line(d,[(65,97),(76,91)],'#caa779',1);dot(d,72,102,'#f0cc72',2)
 poly(d,[(61,113),(77,105),(83,109),(64,119)],'#c2ad84')
 # Decor: flowering pots, steps, fencing
 if seed%3==0:
  rect(d,(99,107,110,113),'#a9684b',INK,1)
  for x in (102,106,109):line(d,[(x,107),(x,99)],'#448c54',1);dot(d,x-1,98,r.choice(['#f9d2ac','#e89397','#ffedb0']),3)
 if seed%5==1:
  for x in range(13,50,9):
   rect(d,(x,114,x+2,126),'#eee4c1',INK,1)
  line(d,[(14,118),(47,118)],'#f9e9ca',2)
 if seed%4==3:
  poly(d,[(80,106),(107,93),(116,99),(89,114)],'#8e9f67')
  for i in range(6):dot(d,85+i*4,104-i//2*2,'#f6c9a2',2)
 return image

def commerce(kind,variant=0):
 seed=sum(map(ord,kind))*19+variant*73;r=random.Random(seed)
 color={'grocer':'#79a19a','bakery':'#edc49a','tavern':'#a88978','bank':'#c1ae93','office':'#a8c6b5','clinic':'#e7d5b7','school':'#e1c49c','police':'#a4bdcc','fire':'#d39c8e','courthouse':'#d0cbb7','college':'#b9b3ce','townhall':'#d8c39f','contractor':'#cfb08e','fishery':'#98bbb6','mill':'#c9b897','forestry':'#9fbd86','sawmill':'#b6a28c','quarry':'#a5a4a0','watchtower':'#bfc5ae','worksite':'#d4be90','park':'#8ac087','square':'#d2c79f','metro_station':'#a1c1b8','warehouse':'#bfb5a0','factory':'#a3aeb6','tower':'#a1b8c5','apartment':'#e5c0a5','airport':'#c6c5b8'}.get(kind,'#c7b4a1')
 roof={'grocer':'#538d86','bakery':'#b85e4c','tavern':'#6e574b','bank':'#576c80','clinic':'#ae7966','townhall':'#6c8475','school':'#b77650','sawmill':'#a55e4a','forestry':'#437059','factory':'#667e87','warehouse':'#626f71','fire':'#b14840','police':'#52708e'}.get(kind,'#716e73')
 image=Image.new('RGBA',(128,144));d=ImageDraw.Draw(image);shadow(d)
 garden(d,seed)
 # Different commercial footprints / architectural eras
 if kind in ('tower','apartment'):
  floors=8 if kind=='tower' else 4
  poly(d,[(37,108),(100,102),(100,115),(37,120)],'#52656c')
  poly(d,[(37,105-floors*10),(73,98-floors*10),(73,111),(37,119)],darken(color,.70))
  poly(d,[(73,98-floors*10),(99,83-floors*10),(99,101),(73,111)],color)
  poly(d,[(34,104-floors*10),(77,96-floors*10),(102,81-floors*10),(61,89-floors*10)],roof)
  for yy in range(floors):
   y=112-floors*10+yy*10
   for xx in (45,58):rect(d,(xx,y+1,xx+7,y+6),r.choice(['#fbe3a2','#91bece','#b2d5d3']),INK,1)
   for xx in (79,88):rect(d,(xx,y-9,xx+6,y-3),'#b7d2d1',INK,1)
  rect(d,(60,104,71,117),'#4c575d',INK,1)
  return image
 if kind in ('park','square'):
  d.ellipse((18,85,108,134),fill='#64965a',outline=INK,width=2)
  d.ellipse((32,87,94,120),fill='#a3c280')
  rect(d,(54,91,67,119),'#e3c68f',INK,1)
  for xx in (37,82):
   rect(d,(xx,107,xx+6,116),'#805f46');d.ellipse((xx-10,76,xx+17,103),fill='#548b61',outline=INK,width=2)
  for x,y in ((36,116),(77,117),(89,109)):dot(d,x,y,'#efb8ba',3)
  return image
 # Base of building, some complex roofs with floor heights
 h=69 if kind in ('townhall','school','courthouse','college','bank','clinic') else 54
 if kind in ('factory','warehouse','sawmill','mill','quarry'):
  h=48
 poly(d,[(17,109-h),(65,128-h),(111,104-h),(65,80-h)],roof)
 poly(d,[(21,117-h),(65,138-h),(65,115),(21,94)],darken(color,.76))
 poly(d,[(65,138-h),(108,116-h),(108,99),(65,120)],color)
 # Roof fascia and ceramic gables
 poly(d,[(10,110-h),(63,82-h),(117,105-h),(65,140-h)],brighten(roof,1.16))
 poly(d,[(65,140-h),(117,105-h),(111,113-h),(65,147-h)],darken(roof,.65),None,0)
 if kind in ('factory','mill','sawmill','warehouse','quarry'):
  for j in range(5):line(d,[(25+j*8,111-h-j*3),(57+j*8,129-h-j*3)],darken(roof,.79),1)
 # Architectural ornament
 for y in range(118-h,122,20):
  line(d,[(24,y),(62,y+17)],brighten(color,1.22),2)
 if kind in ('townhall','courthouse','bank','college','school'):
  poly(d,[(38,110-h),(63,92-h),(88,110-h)],'#efe5c3')
  line(d,[(38,110-h),(88,110-h)],'#a78e73',3)
  for xx in (49,60,72,83):rect(d,(xx,97,xx+4,115),'#dfd9bd',INK,1)
  rect(d,(59,105,71,119),'#4d685e',INK,1)
 # Windows, awnings and storefronts
 if kind in ('grocer','bakery','tavern','fishery','office','bank','clinic','contractor','metro_station'):
  rect(d,(32,82,57,104),'#44696a',INK,2);rect(d,(34,84,55,99),'#a0cbd0',None)
  for j in range(3):rect(d,(33+j*8,73,38+j*8,82),r.choice(['#e8d1a2','#b85d65','#f9e4b7','#688e80']))
  rect(d,(76,79,94,103),'#4b6966',INK,2);rect(d,(79,82,92,98),'#a4c2bf')
 else:
  for xx,yy in ((35,79),(82,77)):
   rect(d,(xx,yy,xx+14,yy+17),'#3b6a78',INK,2)
   line(d,[(xx+7,yy+2),(xx+7,yy+14)],'#f1efd8',2)
 # Shop signs, individual icon instead of text
 icon={'grocer':'#e6d257','bakery':'#f5a378','tavern':'#cf9c57','fishery':'#73bcb6','clinic':'#f9f2e8','bank':'#d1bf77','office':'#c9d9e6','metro_station':'#e7d7a3','sawmill':'#b17d54','forestry':'#76b183','quarry':'#929da4'}.get(kind,'#e8d9bb')
 if kind in ('grocer','bakery','tavern','fishery','clinic','bank','office','metro_station'):
  rect(d,(44,55,79,71),darken(roof,.75),INK,2)
  rect(d,(49,58,74,67),icon)
  if kind=='clinic':line(d,[(61,58),(61,68)],'#b15357',3);line(d,[(57,63),(66,63)],'#b15357',3)
  elif kind=='grocer':d.ellipse((57,58,66,67),fill='#db6859');dot(d,61,57,'#668c4a')
  elif kind=='bakery':d.ellipse((55,59,68,66),fill='#ae6a40');line(d,[(59,58),(63,65)],'#f2d098',1)
  elif kind=='metro_station':rect(d,(59,59,64,66),'#426c84')
 # Shopfront door
 rect(d,(62,105,73,119),darken(roof,.66),INK,2);dot(d,70,112,'#e8c67b',2)
 # Distinct chimney stacks and industrial features
 if kind in ('factory','mill','sawmill','quarry'):
  for i in range(2 if kind=='factory' else 1):
   xx=85+i*12;rect(d,(xx,17-i*9,xx+9,79),'#a4a19a',INK,2)
   rect(d,(xx-2,15-i*9,xx+11,22-i*9),'#e7c8a6',INK,2)
  rect(d,(25,100,52,117),'#4c6058',INK,2)
 elif kind=='tavern':
  rect(d,(26,39,36,64),'#877360',INK,1)
 elif kind=='school':
  rect(d,(94,65,100,97),'#b97a64',INK,1)
 elif kind=='worksite':
  for xx in (30,50,83):line(d,[(xx,91),(xx,47)],'#bfa269',4)
  for y in (60,76,94):line(d,[(26,y),(100,y)],'#e4b974',3)
 return image

def tree(seed,season):
 r=random.Random(seed*17+season*997);image=Image.new('RGBA',(128,144));d=ImageDraw.Draw(image)
 # Slightly more realistic hand-worked canopies; transparent bounding canvas.
 d.ellipse((46,114,87,123),fill='#1b382f53');rect(d,(62,72,70,115),'#5d5140',INK,1)
 for i in range(5):
  x=56+r.randint(-20,23);y=55+i*8+r.randint(-10,8)
  if season==2: c=r.choice(['#71857a','#7a918b','#b8c6ba'])
  elif season==1:c=r.choice(['#dc9b56','#b75d4c','#d4b562','#8a9353'])
  else:c=r.choice(['#468d5c','#5a9d5b','#7bb16a','#3f7a62'])
  d.ellipse((x-20,y-19,x+24,y+16),fill=c,outline=darken(c,.72),width=2)
  for j in range(7):
   xx=x+r.randint(-15,17);yy=y+r.randint(-12,13)
   dot(d,xx,yy,brighten(c,1.18),r.randint(2,4))
 return image

if __name__=='__main__':
 for i in range(16):home(i).save(ROOT/f'home-{i}.png',optimize=True)
 types=['grocer','bakery','tavern','bank','office','clinic','school','police','fire','courthouse','college','townhall','contractor','fishery','mill','forestry','sawmill','quarry','watchtower','worksite','park','square','metro_station','warehouse','factory','tower','apartment','airport']
 for kind in types:
  for i in range(3 if kind in ('grocer','bakery','tavern','office','farm','factory','warehouse','apartment') else 1):commerce(kind,i).save(ROOT/f'{kind}-{i}.png',optimize=True)
 for season in range(3):
  for i in range(8):tree(i,season).save(ROOT/f'tree-{season}-{i}.png',optimize=True)
 print('generated',len(list(ROOT.glob('*.png'))),'sprites')
