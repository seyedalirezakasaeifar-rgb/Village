"""Actual software capability fallback; explicit preferences retry and remain saved."""
from pathlib import Path
import subprocess,json
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'docs/previews/webgl-economy-8';O.mkdir(parents=True,exist_ok=True);s=subprocess.Popen(['python','-m','http.server','8808','--bind','127.0.0.1'],cwd=R/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:8808/index.html?cityArt=webgl&cityBadge=1');p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.wait_for_function('window.__cityRendererFallback');fallback=p.evaluate('__cityRendererFallback');assert 'SwiftShader' in fallback['backend'];assert p.locator('#webglTaste').count()==0;p.locator('[data-panel=settings]').click();p.locator('#panelClose').click();before=p.evaluate('__townTest.save()')
  def pref(value):
   p.locator('[data-panel=settings]').click();p.locator('[data-preference=quality]').select_option(value);p.locator('#panelClose').click()
  pref('low');p.wait_for_function('window.__webglTaste&&__webglTaste.quality==="economy"');assert p.evaluate('__cityVisualSnapshot().options.quality')=='low';p.evaluate('__webglTaste.focus(30,30,2)');p.wait_for_timeout(300);pref('balanced');p.wait_for_function('!window.__webglTaste&&window.__cityRendererFallback');assert p.evaluate('__townTest.save()')==before
  pref('high');p.wait_for_function('window.__webglTaste&&__webglTaste.quality==="reference"&&__webglTaste.samples.length>=3',timeout=90000);assert p.evaluate('!__webglTaste.qualityPolicy.automatic&&__cityVisualSnapshot().options.quality==="high"');assert p.evaluate('JSON.parse(localStorage.getItem("townledger-options")).quality')=='high';view=p.evaluate('__webglTaste.cameraInfo().target');assert view=={'x':30,'z':30},view;assert p.evaluate('__townTest.save()')==before;assert p.evaluate('__cityVisualSave()');assert not errors,errors;(O/'quality-recovery.json').write_text(json.dumps({'capabilityFallback':fallback,'explicitPerformanceRetry':True,'explicitRichRetryAndSaved':True,'cameraRetained':view,'archiveInvariant':True,'save':True,'errors':errors},indent=2));print('PASS actual software fallback, Performance/Rich retries, saved choices/camera/state');b.close()
finally:s.terminate()
