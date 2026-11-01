"""Bounded exact-town quality comparison; reports real RAF, not submission CPU as FPS."""
from pathlib import Path
import subprocess,json,statistics,hashlib,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews/webgl-chunked-8';OUT.mkdir(parents=True,exist_ok=True)
server=subprocess.Popen(['python','-m','http.server','8775','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def stats(a):
 a=sorted(a);return {'n':len(a),'medianMs':statistics.median(a),'p95Ms':a[int((len(a)-1)*.95)],'maxMs':max(a)}
results=[];canonical=None
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for tier in ['off','on','chunks8']:
   context=browser.new_context(viewport={'width':1000,'height':700},device_scale_factor=1);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));started=time.monotonic();page.goto('http://127.0.0.1:8775/index.html?cityArt=webgl&cityInstanceColors='+('off' if tier=='off' else 'on')+'&cityChunks='+('8' if tier=='chunks8' else '0'),wait_until='networkidle');page.locator('#newTown').click();page.locator('#pause').click();page.locator('#panelClose').click();canonical=canonical or page.evaluate('__townTest.save()');assert page.evaluate('(s)=>__townTest.load(s)',canonical);page.wait_for_function('window.__webglTaste&&__webglTaste.sceneRevision===__cityVisualRevision()&&__webglTaste.samples.length>=36',timeout=90000)
   r=page.evaluate('()=>({quality:__webglTaste.quality,backingSize:__webglTaste.backingSize,shadowSize:__webglTaste.shadowSize,shadowPasses:__webglTaste.shadowPasses,cpu:__webglTaste.samples,raf:__webglTaste.rafSamples,backend:__webglTaste.renderer,calls:__webglTaste.drawCalls,triangles:__webglTaste.triangles,memory:__webglTaste.memory(),batching:__webglTaste.batching,programs:__webglTaste.programs,materials:__webglTaste.materialCount,state:__cityVisualSnapshot(),before:__webglTaste.stateBefore})');state=r.pop('state');assert state['rng']==r['before']['rng'] and state['day']==r['before']['day'] and state['total']==r['before']['total'];model={k:state[k] for k in ['day','population','total','rng','size','tiles','buildings','bridges']};digest=hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest();r.update({'batchMode':tier,'modelDigest':digest,'cpu':stats(r['cpu'][8:]),'raf':stats(r['raf'][8:]),'elapsedSeconds':time.monotonic()-started,'stateInvariant':True,'saveOK':page.evaluate('__cityVisualSave()'),'errors':errors});assert not errors;results.append(r);(OUT/'tiers.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(r),flush=True);page.screenshot(path=str(OUT/('scene-'+tier+'.png')));page.evaluate('__webglTaste.dispose()');context.close()
  browser.close()
 assert len({r['modelDigest'] for r in results})==1,'town state differs between tiers'
finally:server.terminate()
