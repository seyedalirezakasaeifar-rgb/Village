"""Host next-render latency through actual wheel control; not device certification."""
from pathlib import Path
import subprocess,json,statistics
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'docs/previews/webgl-economy-8';s=subprocess.Popen(['python','-m','http.server','8811','--bind','127.0.0.1'],cwd=R/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1280,'height':720});p.goto('http://127.0.0.1:8811/index.html?cityArt=webgl&cityQuality=economy');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.wait_for_function('window.__webglTaste&&__webglTaste.samples.length>=3');p.evaluate('__webglTaste.focus(26,26,1.8)');p.wait_for_timeout(500);before=p.evaluate('__townTest.save()');r=p.locator('#webglTaste').bounding_box();p.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2);samples=[]
  for i in range(8):
   f=p.evaluate('__webglTaste.frameId');start=p.evaluate('performance.now()');p.mouse.wheel(0,-30 if i%2==0 else 30);p.wait_for_function('(n)=>__webglTaste.frameId>n',arg=f);samples.append(p.evaluate('performance.now()')-start)
  assert p.evaluate('__townTest.save()')==before;a=sorted(samples);(O/'input.json').write_text(json.dumps({'hostOnly':True,'source':'actual wheel to next rendered frame; includes automation overhead','samplesMs':samples,'medianMs':statistics.median(a),'p95Ms':a[int((len(a)-1)*.95)],'archiveInvariant':True},indent=2));print({'wheelNextFrameMedianMs':statistics.median(a),'p95Ms':a[int((len(a)-1)*.95)]});b.close()
finally:s.terminate()
