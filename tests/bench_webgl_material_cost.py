"""Same archive/camera, old renderer versus clean street/specialized hooks.
Common current architectural assets are deliberately shared by both variants."""
from pathlib import Path
import subprocess,json,statistics,hashlib,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews/webgl-material-cost-8';OUT.mkdir(parents=True,exist_ok=True);old=(ROOT/'assets/webgl-taste.js').read_text();lambert=re.sub(r',roughness:[^,}]+','',old.replace('THREE.MeshStandardMaterial','THREE.MeshLambertMaterial'))
server=subprocess.Popen(['python','-m','http.server','8797','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def stats(a):
 a=sorted(a);return {'n':len(a),'medianMs':statistics.median(a),'p95Ms':a[int((len(a)-1)*.95)],'maxMs':max(a)}
try:
 results=[];canonical=None
 with sync_playwright()as w:
  browser=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for mode in ['standard','lambert']:
   c=browser.new_context(viewport={'width':1280,'height':720});p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   if mode=='lambert':p.route('**/webgl-taste.js',lambda r:r.fulfill(body=lambert,content_type='application/javascript'))
   p.goto('http://127.0.0.1:8797/index.html?cityArt=webgl&cityQuality=low&cityBenchmark=1');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();canonical=canonical or p.evaluate('__townTest.save()');assert p.evaluate('(s)=>__townTest.load(s)',canonical);p.wait_for_function('window.__webglTaste&&__webglTaste.sceneRevision===__cityVisualRevision()');p.evaluate('__webglTaste.focus(27,27,1.8)');p.wait_for_function('__webglTaste.lod==="near"&&__webglTaste.samples.length>=28',timeout=120000);before=p.evaluate('__townTest.save()');r=p.evaluate('()=>({calls:__webglTaste.drawCalls,triangles:__webglTaste.triangles,materials:__webglTaste.materialCount,programs:__webglTaste.programs,memory:__webglTaste.memory(),buildMs:__webglTaste.buildMs,cpu:__webglTaste.samples,raf:__webglTaste.rafSamples,backend:__webglTaste.renderer})');r['cpu']=stats(r['cpu'][8:]);r['raf']=stats(r['raf'][8:]);r['mode']=mode;r['sourceModuleHashes']={str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in [ROOT/'assets/game.js',*sorted((ROOT/'assets').glob('webgl*.js')),*sorted((ROOT/'assets').glob('newfoundland*.js'))]};r['baselineRendererHash']=hashlib.sha256(old.encode()).hexdigest();r['archiveDigest']=hashlib.sha256(before.encode()).hexdigest();p.screenshot(path=str(OUT/(mode+'.png')));assert p.evaluate('__townTest.save()')==before;assert p.evaluate('__cityVisualSave()');assert not errors;r['errors']=errors;results.append(r);(OUT/'paired.json').write_text(json.dumps(results,indent=2)+'\n');print({k:r[k]for k in ['mode','calls','triangles','materials','programs','buildMs','raf']},flush=True);c.close()
  browser.close()
 assert results[0]['archiveDigest']==results[1]['archiveDigest']
finally:server.terminate()
