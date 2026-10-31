"""Art silhouettes, condition/closure, envelopes, LOD and economic independence."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
out=ROOT/'reports/art-direction';out.mkdir(parents=True,exist_ok=True)
source=(ROOT/'assets/game.js').read_text()
probe=r'''window.__dioramaProbe=()=>{
 const before=JSON.stringify(G),oldNight=nightMode,oldDecor=gameOptions.decor,oldQuality=gameOptions.quality;
 const digest=c=>{const a=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let hash=2166136261,count=0,minX=c.width,minY=c.height,maxX=0,maxY=0;for(let i=0;i<a.length;i+=4){if(a[i+3]){count++;const x=i/4%c.width,y=Math.floor(i/4/c.width);minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}for(let k=0;k<4;k++)hash=Math.imul(hash^a[i+k],16777619);}return {hash:hash>>>0,count,bounds:[minX,minY,maxX,maxY],size:[c.width,c.height]};};
 const specimen=(kind,id=0,condition=100)=>{const b={kind,id,x:20,y:20,hh:kind==='home'?0:-1,firm:-1,condition,value:10000};return digest(spriteFor({kind:'building',id,b,x:0,y:0,w:kind==='factory'?2:1,d:kind==='factory'?2:1}));};
 const ground=(kind,x,y)=>{const c=document.createElement('canvas');c.width=240;c.height=150;const g=c.getContext('2d');g.translate(120,40);dioramaFoundation(g,{kind,x,y,retailCentre:false},1,1);return digest(c).hash;};
 gameOptions.decor=true;gameOptions.quality='balanced';nightMode=false;clearAtlas();
 const ids=Array.from({length:120},(_,i)=>i),homeIds=Array.from({length:6},(_,style)=>ids.find(id=>houseStyleId(id)===style)),homes=homeIds.map(id=>specimen('home',id));
 const sectors=Array.from(DIORAMA_KINDS,kind=>({kind,...specimen(kind)}));
 const conditions=[100,65,30].map(c=>specimen('home',1,c));
 nightMode=true;const night=specimen('home',1);nightMode=false;const day=specimen('home',1);
 gameOptions.decor=false;clearAtlas();const plain=specimen('factory');gameOptions.decor=true;clearAtlas();const detailed=specimen('factory');
 const shadows=document.createElement('canvas');shadows.width=300;shadows.height=300;paintCastShadows(shadows.getContext('2d'),[{kind:'building',b:{kind:'factory',id:2},x:80,y:80,w:2,d:2}]);
 const groundTypes=['home','apartment','grocer','factory'].map(kind=>ground(kind,20,20)),parcels=ANNEX_PARCELS.slice(0,5).map(p=>ground('home',p.x,p.y));
 nightMode=oldNight;gameOptions.decor=oldDecor;gameOptions.quality=oldQuality;clearAtlas();staticDirty=true;dirty=true;draw();
 return {homes,sectors,conditions,night,day,plain,detailed,groundTypes,parcels,unchanged:before===JSON.stringify(G)};
};'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__dioramaProbe()')
 assert r['unchanged'] and len({h['hash'] for h in r['homes']})==6,r
 assert len({h['hash'] for h in r['conditions']})==3,r['conditions']
 assert len(set(r['groundTypes']))==4 and len(set(r['parcels']))>=4,r['groundTypes']
 assert r['night']['hash']!=r['day']['hash'] and r['plain']['hash']!=r['detailed']['hash']
 for item in r['sectors']+r['homes']:
  x,y,xx,yy=item['bounds'];w,h=item['size'];assert item['count']>100 and x>0 and y>0 and xx<w-1 and yy<h-1,item
 assert not errors,errors;b.close()
 r.update(source_sha256=hashlib.sha256(source.encode()).hexdigest(),errors=errors)
 (out/'architecture-checks.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS six house silhouettes,'+str(len(r['sectors']))+' sector models,condition/night/detail distinctions,unclipped envelopes,type- and district-specific parcel grounds,no economic writes')
