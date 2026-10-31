"""Identical-game-frame review of integrated institutions, rural sectors and night."""
from pathlib import Path
import ast,sys,json,subprocess,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
out=ROOT/'reports/provider-world';out.mkdir(parents=True,exist_ok=True)
fixture=next(ast.literal_eval(n.value) for n in ast.parse((ROOT/'tests/test_private_services.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='probe' for x in n.targets))
probe="""window.__providerCamera=(kind)=>{const b=G.buildings.find(b=>b.kind===kind),p=iso(b.x,b.y);cam={x:p[0],y:p[1]+10,zoom:1.6};dirty=true;draw();return{id:b.id,firm:b.firm};};"""
rows=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for label,source in [('before',subprocess.check_output(['git','show','cae1bf4:assets/game.js'],cwd=ROOT).decode()),('after',(ROOT/'assets/game.js').read_text())]:
  p=browser.new_page(viewport={'width':844,'height':520});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click()
  p.evaluate("__townTest.reset('settlement',42)");p.evaluate('__townTest.step(5)')
  for kind in ['farm','forestry','quarry','wharf','fishery','school','fire']:
   p.evaluate('__providerCamera',kind);p.locator('#view').screenshot(path=str(out/(label+'-'+kind+'.png')))
  p.evaluate('__providerCamera','school');p.evaluate('__townTest.capture({night:true})');p.locator('#view').screenshot(path=str(out/(label+'-night.png')));p.evaluate('__townTest.capture({night:false})')
  for kind in ['school','fire']:
   f=p.evaluate('k=>__privateFixture(k,100)',kind);p.evaluate('__townTest.step(1)');p.evaluate('__providerCamera',kind);p.locator('#view').screenshot(path=str(out/(label+'-independent-'+kind+'.png')))
   p.evaluate('__townTest.capture({night:true})');p.locator('#view').screenshot(path=str(out/(label+'-independent-'+kind+'-night.png')));p.evaluate('__townTest.capture({night:false})')
  p.set_viewport_size({'width':844,'height':390});p.wait_for_timeout(100);p.evaluate("__townTest.reset('settlement',42)");p.evaluate('__townTest.step(5)');p.evaluate('__townTest.capture({zoom:.85,night:true})');p.locator('#view').screenshot(path=str(out/(label+'-night-mobile.png')))
  assert not errors,errors;rows.append({'stage':label,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'errors':errors});p.close()
 browser.close()
(out/'comparison.json').write_text(json.dumps({'captures':rows,'privateScenes':'Controlled matched fee-provider fixture with qualified staff and real paid clients; not a claim of organic entry.','publicScenes':'Fixed-seed settlement after5 economic days.'},indent=2)+'\n');print(rows)
