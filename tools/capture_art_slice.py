"""Fixed-seed/camera comparison with the preserved 7.0.3 APK assets."""
from pathlib import Path
import json,hashlib,zipfile,sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'reports/art-slice';out.mkdir(parents=True,exist_ok=True)
rows=[]
with zipfile.ZipFile(ROOT/'android-checkpoints/TownLedger-The-Working-City-7.0.3.apk') as old, sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for name in ['before','after']:
  read=(lambda p:old.read('assets/'+p).decode()) if name=='before' else (lambda p:(ROOT/'assets'/p).read_text())
  html=read('index.html')
  for sheet in ['style.css','vale.css','civic7.css']:html=html.replace('<link rel="stylesheet" href="'+sheet+'">','<style>'+read(sheet)+'</style>')
  html=html.replace('<script src="game.js"></script>','');source=read('game.js');p=b.new_page(viewport={'width':960,'height':600});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42)");p.locator('#panelClose').click()
  g=p.evaluate('JSON.parse(__townTest.save())');water=[i for i,t in enumerate(g['tiles']) if t==2];shore=min(water,key=lambda i:abs(i%56-36)+abs(i//56-26));x,y=shore%56,shore//56
  for scene,opts in [('town',{'zoom':.75}),('river',{'x':(56*72+140)/2+(x-y)*36,'y':32+(x+y)*18,'zoom':1.1})]:
   p.evaluate('(o)=>__townTest.capture(o)',opts);p.locator('#view').screenshot(path=str(out/(name+'-'+scene+'.png')))
  rows.append({'stage':name,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'errors':errors});assert not errors; p.close()
 b.close()
(out/'comparison.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
