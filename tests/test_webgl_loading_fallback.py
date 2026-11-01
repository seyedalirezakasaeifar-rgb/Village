from pathlib import Path
import subprocess,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];server=subprocess.Popen(['python','-m','http.server','8776','--bind','127.0.0.1'],cwd=ROOT/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);result=[]
  for fail in [False,True]:
   page=b.new_page(viewport={'width':844,'height':390});requests=[];errors=[];page.on('request',lambda r:requests.append(r.url));page.on('pageerror',lambda e:errors.append(str(e)))
   if fail:page.route('**/webgl-taste.js',lambda r:r.abort('failed'))
   page.goto('http://127.0.0.1:8776/index.html'+('?cityArt=webgl' if fail else ''),wait_until='networkidle');page.locator('#newTown').click();page.locator('#pause').click();page.locator('#panelClose').click()
   if fail:page.wait_for_function('!!window.__webglTasteFailure')
   else:assert not any('three-' in u or 'webgl-taste.js' in u or 'newfoundland-kit.js' in u for u in requests),requests
   assert page.locator('#webglTaste').count()==0 and page.locator('canvas').first.is_visible();assert page.evaluate('__cityVisualSave()');assert not errors,errors;result.append({'failedWebGLImport':fail,'canvasVisible':True,'saveOK':True,'noHeavyDefaultImports':not fail,'errors':errors});page.close()
  b.close();out=ROOT/'docs/previews/webgl-quality-8';out.mkdir(parents=True,exist_ok=True);(out/'fallback.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
finally:server.terminate()
