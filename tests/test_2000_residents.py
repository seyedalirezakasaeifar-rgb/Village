"""Synthetic large-town stress: ~2,000 resident accounts and ~670 homes.
This tests upper-bound model scale, not 2,000 naturally grown residents.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import time
R=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':844,'height':390},device_scale_factor=1)
 page.set_content((R/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(R/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>',''))
 page.add_script_tag(content=(R/'assets/game.js').read_text())
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 result=page.evaluate('''()=>{__townTest.reset('settlement');let g=JSON.parse(__townTest.save()),busy=new Set(g.buildings.flatMap(b=>(b.footprint||[b.y*g.gridSize+b.x])));
 let free=[];for(let y=3;y<53;y++)for(let x=3;x<53;x++)if(g.tiles[y*g.gridSize+x]===0&&!busy.has(y*g.gridSize+x)&&!g.landUse?.[y*g.gridSize+x])free.push([x,y]);
 let n=0;while(g.people.length<2000&&n<700){let xy=free[n],i=g.households.length,h={id:i,name:'Newcomer'+n,cash:500,home:g.nextId,owner:i,people:[],income:0,rent:0,food:0,tax:0,aid:0,crimeLoss:0,stress:25,security:80,last:[],worklessness:0};let bb={id:g.nextId++,kind:'home',x:xy[0],y:xy[1],value:25000,condition:100,owner:i,firm:-1,hh:i};g.buildings.push(bb);g.homes.push(bb.id);g.households.push(h);g.region-=500;for(let a=0;a<3&&g.people.length<2000;a++){let id=g.people.length;g.people.push({id,name:'Resident '+id,age:26+a*3,skill:.5,health:80,hh:i,job:-1,life:70,last:[]});h.people.push(id)}n++}if(!__townTest.load(g))throw Error('Synthetic town was rejected by footprint validator');return {pop:__townTest.get().population,homes:g.homes.length,blocks:g.buildings.length,sourceSize:JSON.stringify(g).length,baseline:__townTest.get().total}}''')
 print('Synthetic population',result,flush=True)
 assert result['pop']==2000
 now=time.perf_counter();page.evaluate('__townTest.step(120)');elapsed=time.perf_counter()-now
 state=page.evaluate('''()=>{let x=__townTest.get();return{day:x.day,pop:x.population,businesses:x.businesses,cases:x.cases,total:x.total}}''')
 print('120 simulated days',round(elapsed,3),'s',round(elapsed/120*1000,2),'ms/day',state,flush=True)
 assert abs(state['total']-result['baseline'])<5
 assert 1980<=state['pop']<=2000 and state['day']==121 and not errors,errors
 print('PASS: synthetic 2,000-resident economy remains valid',flush=True)
 b.close()
