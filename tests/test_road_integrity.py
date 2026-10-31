"""Repeat road invariants and economic accounting across twenty distinct town seeds."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import time
root=Path(__file__).resolve().parents[1];assets=root/'assets'
h= (assets/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(assets/'style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':900,'height':520})
 failures=[];page.on('pageerror',lambda e:failures.append(str(e)))
 page.set_content(h);page.add_script_tag(content=(assets/'game.js').read_text());page.locator('#newTown').click();page.locator('#panelClose').click()
 t=time.monotonic()
 for i in range(20):
  result=page.evaluate('''(scenario)=>{
    __townTest.reset(scenario);
    const g=JSON.parse(__townTest.save()),M=__townTest.road(),money0=__townTest.get().total;
    if(M.connectedFirms!==M.totalFirms||M.connectedHomes!==M.totalHomes)throw Error('Unconnected founding parcels '+JSON.stringify(M));
    for(let j=0;j<220;j++){
      __townTest.advanceTraffic(.16);
      for(const v of __townTest.traffic()){
        if(v.route.length<2)throw Error('Degenerate route');
        for(let k=0;k<v.route.length;k++){
          let at=v.route[k];if(g.tiles[at]!==1)throw Error('Vehicle entered non-road');
          if(k){let previous=v.route[k-1],dx=Math.abs(previous%56-at%56),dy=Math.abs(Math.floor(previous/56)-Math.floor(at/56));if(dx+dy!==1)throw Error('Nonadjacent road segment');}
        }
        if(v.fraction<0||v.fraction>1)throw Error('Bad position interpolation');
      }
    }
    const num=__townTest.traffic().length;
    __townTest.step(90);let after=__townTest.get();
    if(Math.abs(money0-after.total)>0.015)throw Error('Money leaked: '+(money0-after.total));
    if(after.population<1||!Number.isFinite(after.treasury))throw Error('Bad town state');
    return {traffic:num,road:M.roadTiles,people:after.population,buildings:g.buildings.length,day:after.day,financeError:Math.abs(money0-after.total)};
  }''', ['settlement','hardtimes','frontier','industrial'][i%4])
  print(i+1,result)
 print('20 town simulations passed in',round(time.monotonic()-t,1),'s; errors:',failures)
 assert not failures
 page.screenshot(path=str(root/'highroads-test-view.png'))
 print('render ms/frame on host',page.evaluate('__townTest.renderBench(140)'))
 b.close()
