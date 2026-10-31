"""Repeated founding, private-build, development and plot integrity random test."""
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
src=(root/'assets/game.js').read_text()
src=src[:-6]+'''window.__landmarkDebug={
 issues:()=>getFootprintIssues(),
 count:()=>Object.fromEntries(['farm','factory','warehouse','tower','airport','metro_station'].map(kind=>[kind,G.buildings.filter(b=>b.kind===kind&&footprintOf(b).length>1).length])),
 verify:()=>{const occupied=new Set();for(const b of G.buildings)for(const id of footprintOf(b)){
  if(occupied.has(id))throw Error('overlap');occupied.add(id);
  if(G.tiles[id]===1||G.tiles[id]===2||G.landUse?.[id])throw Error('occupied land lost to construction '+id);
 }return occupied.size},
};
})();'''
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True, executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':900,'height':540});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 html=(root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
 page.set_content(html);page.add_script_tag(content=src);page.locator('#newTown').click()
 sample=[]
 for i in range(40):
  sample.append(page.evaluate('''(iteration)=>{
   __townTest.reset(['settlement','hardtimes','frontier','industrial'][iteration%4],iteration*7919+17);
   const plots=__landmarkDebug.verify(),counts=__landmarkDebug.count();
   __townTest.step(90);__landmarkDebug.verify();
   const state=__townTest.save(),total=__townTest.get().total;
   if(!__townTest.load(state))throw Error('Unable to reload a town with large land sites');
   if(Math.abs(__townTest.get().total-total)>.001)throw Error('Money transfer on save/load');
   return {plots,counts,buildingCount:JSON.parse(state).buildings.length};
  }''',i))
 print('40 randomized towns + 90 day development: passed')
 print('Sample:',sample[:3]);print('Total large farms',sum(x['counts']['farm'] for x in sample))
 assert sum(x['counts']['farm'] for x in sample)>20, 'Few multi-square farms in founding scenarios'
 assert not errors,errors
 browser.close()
print('PASS 40 town layout, road overlap, economic/save integrity cases')
