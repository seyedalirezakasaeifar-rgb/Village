"""Adversarial regression checks discovered during source audit."""
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
html=(root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':844,'height':390},has_touch=True,is_mobile=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html);page.add_script_tag(content=(root/'assets/game.js').read_text());page.locator('#newTown').click();page.locator('#panelClose').click()
 # 1: No funding should not preserve phantom police/fire effectiveness.
 funding=page.evaluate('''()=>{
  let g=JSON.parse(__townTest.save());let total=__townTest.get().total;
  g.region+=g.treasury;g.treasury=0;
  for(let k of ['incomeTax','profitTax','propertyTax','commercialRate','foodTax','utilityTax'])g.policy[k]=0;
  __townTest.load(g);__townTest.step(1);
  const x=JSON.parse(__townTest.save());return {police:x.actualServiceFunding.police,fire:x.actualServiceFunding.fire,road:x.actualServiceFunding.roads,preparedness:x.stats.preparedness,safety:x.stats.safety,total:__townTest.get().total-originalTotal};
 }'''.replace('originalTotal','total'))
 print('Zero-funding service response:',funding)
 assert funding['police']==0 and funding['fire']==0 and funding['road']==0
 assert funding['preparedness']<=5 and abs(funding['total'])<.05
 # 2: Old saves, bad saves and restored road network.
 fresh=page.evaluate('''()=>{
  __townTest.reset();let g=JSON.parse(__townTest.save());
  let saved=JSON.stringify(g);let broken={...g,tiles:g.tiles.slice()};broken.tiles[500]=99;
  if(__townTest.load(broken))throw Error('Accepted corrupt tile');
  if(!__townTest.load(saved))throw Error('Could not restore normal save');
  return __townTest.road();
 }''')
 print('Import validation and network restore:',fresh)
 # 3: Cars stay on passable tiles, no malformed route steps under traffic load.
 traffic=page.evaluate('''()=>{
  for(let i=0;i<600;i++){
   __townTest.advanceTraffic(.04);
   const g=JSON.parse(__townTest.save());
   for(const v of __townTest.traffic()){
    if(v.fraction<0||v.fraction>1)throw Error('Bad traffic interpolation');
    if(v.route.some(n=>g.tiles[n]!==1))throw Error('Traffic left road graph');
    for(let j=1;j<v.route.length;j++)if(Math.abs(v.route[j]%56-v.route[j-1]%56)+Math.abs(Math.floor(v.route[j]/56)-Math.floor(v.route[j-1]/56))!==1)throw Error('Traffic corner shortcut');
   }
  }
  return __townTest.traffic().length;
 }''')
 print('Traffic actors after 600 frames:',traffic)
 # 4: 12 simulated years cannot duplicate household memberships or lose money.
 initial=page.evaluate('__townTest.get().total')
 annual=page.evaluate('''()=>{
  let first=__townTest.get().total;
  __townTest.step(4320);
  let g=JSON.parse(__townTest.save());let ids=new Set(),duplicate=0,bad=0;
  for(let h of g.households)for(let id of h.people){if(ids.has(id))duplicate++;ids.add(id);if(g.people[id].hh!==h.id||g.people[id].deceased)bad++}
  for(let p of g.people.filter(p=>!p.deceased&&!p.movedAway))if(!ids.has(p.id))bad++;
  return {day:g.day,people:g.stats.population,totalError:__townTest.get().total-first,duplicate,bad};
 }''')
 print('Twelve-year population and finance:',annual)
 assert annual['day']==4321 and annual['duplicate']==0 and annual['bad']==0 and abs(annual['totalError'])<2
 # 5: Restart must use a native-game dialogue, not browser confirm.
 page.locator('button[data-panel=settings]').click()
 page.locator('#restart').click()
 assert page.locator('#eventDialog').is_visible() and page.locator('#eventTitle').inner_text()=='Found another town?'
 before=page.evaluate('__townTest.get().day');page.locator('[data-event-choice="0"]').click();assert page.evaluate('__townTest.get().day')==before
 page.locator('#restart').click();page.locator('[data-event-choice="1"]').click();assert page.evaluate('__townTest.get().day')==1
 print('Restart dialog and cancellation preserved save.')
 # 6: Policy proposals survive navigation until explicitly enacted or discarded.
 page.locator('button[data-panel=policies]').click()
 page.locator('input[data-policy=incomeTax]').fill('5')
 page.locator('button[data-panel=treasury]').click()
 page.locator('button[data-panel=policies]').click()
 assert page.locator('input[data-policy=incomeTax]').input_value()=='5'
 assert page.locator('#enactPolicy').is_enabled()
 page.locator('#enactPolicy').click()
 assert page.evaluate('__townTest.get().policy.incomeTax')==5
 print('Staged policy survives tab navigation and enacts at requested rate.')
 assert not errors,errors
 b.close()
 print('PASS: audited regressions')
