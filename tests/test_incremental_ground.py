"""Retained atlas terrain stays within measured Canvas raster tolerance of a complete repaint after localized world edits."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
probe=r'''
window.__groundCheck=()=>{const original=G,fastBase=fastRenderEnabled;try{G=JSON.parse(JSON.stringify(G));const funds=Math.min(G.region,6000000);G.region-=funds;G.treasury+=funds;while(G.charter.owned.length<ANNEX_PARCELS.length){const p=ANNEX_PARCELS.find(p=>!G.charter.owned.includes(p.id)&&parcelAdjacent(p));if(!p||!purchaseParcel(p.id,parcelSurvey(p).price))throw Error('No deed');}const rows=[];
 for(const fast of [false,true]){fastRenderEnabled=()=>fast;groundBaseTown=null;drawGround();const p=roadId(95,63),road=graph().neighbors.keys().next().value;G.landUse[p]=G.landUse[p]===1?0:1;G.tiles[road]=G.tiles[road]===1?0:1;G.roadClasses[roadId(27,27)]='arterial';invalidateRoads(false);const t=performance.now();drawGround();const ms=performance.now()-t,a=bg.getImageData(0,0,bitmap.width,bitmap.height).data;groundBaseTown=null;drawGround();const b=bg.getImageData(0,0,bitmap.width,bitmap.height).data;groundBaseTown=null;drawGround();const c=bg.getImageData(0,0,bitmap.width,bitmap.height).data;let selfDiff=0;for(let i=0;i<c.length;i++)if(Math.abs(c[i]-b[i])>2)selfDiff++;let differing=0,max=0,minX=1e9,minY=1e9,maxX=0,maxY=0,samples=[];for(let i=0;i<a.length;i++){const d=Math.abs(a[i]-b[i]);if(d>2){differing++;const px=(i/4|0)%bitmap.width,py=(i/4/bitmap.width|0);minX=Math.min(minX,px);minY=Math.min(minY,py);maxX=Math.max(maxX,px);maxY=Math.max(maxY,py);if(samples.length<12)samples.push([px,py,a[i],b[i]]);}max=Math.max(max,d);}rows.push({fast,bitmapPixels:a.length/4,localizedMs:ms,differingChannels:differing,maxChannelDelta:max,selfDiff,bounds:[minX,minY,maxX,maxY],samples});}
 return rows;}finally{G=original;fastRenderEnabled=fastBase;groundBaseTown=null;groundTileState=null;invalidateRoads(false);staticDirty=true;}};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-accelerated-2d-canvas']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__groundCheck()');b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
(ROOT/'reports/development-8.0/incremental-ground.json').write_text(json.dumps({'source_sha256':sha,'controlledTerrainEdits':True,'rows':r},indent=2)+'\n');# Full repaint versus itself also varies in Chromium edge rasterization.
# Bound both the spatial extent and channel magnitude; missing geometry fails.
assert all(row['differingChannels']/ (row['bitmapPixels']*4)<.0005 and row['maxChannelDelta']<=12 for row in r),r
print('PASS localized all-owned terrain repaint within bounded Canvas edge tolerance of full bitmap after crop/street/class changes at normal and fast quality',r)
