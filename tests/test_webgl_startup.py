"""The selected renderer must start from New Town without requiring Pause."""
from pathlib import Path
import subprocess,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews/webgl-night-overlays-8';OUT.mkdir(parents=True,exist_ok=True)
server=subprocess.Popen(['python','-m','http.server','8794','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright()as w:
  b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':520});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:8794/index.html?cityArt=webgl&cityQuality=low');p.locator('#newTown').click();p.wait_for_function('window.__webglTaste',timeout=60000);first=p.evaluate('__cityVisualMotionState()');p.wait_for_timeout(400);later=p.evaluate('__cityVisualMotionState()');assert first['paused']or later['clock']>first['clock'];
  if not later['paused']:p.locator('#pause').click()
  assert p.evaluate('__cityVisualSave()');assert not errors;(OUT/'startup.json').write_text(json.dumps({'startsWithoutPauseAction':True,'initialPaused':first['paused'],'normalClockAdvanced':later['clock']>first['clock'],'save':True,'errors':errors},indent=2)+'\n');print('PASS startswithoutPauseaction,normalclock/save');b.close()
finally:server.terminate()
