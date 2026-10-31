"""Bounded gesture queue and distinct-command overflow delivery."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,json
m=ast.parse((ROOT/'tests/test_cooperative_barriers.py').read_text());probe=next(ast.literal_eval(n.value) for n in m.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
extra="""window.__queueStress={count:0,run:async()=>{const promises=[];for(let i=0;i<300;i++)promises.push(__cooperativeSimulation.command('distinct transfer '+i,()=>{G.treasury-=1;G.region+=1;__queueStress.count++;}));await Promise.all(promises);return {count:__queueStress.count,status:__cooperativeSimulation.status(),barriers:__cooperativeSimulation.samples().barriers};}};"""
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_content(html);p.add_script_tag(content=(ROOT/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js',probe+'\n'+extra+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();p.evaluate('__coopBarrier.hold()');p.mouse.move(400,170);p.mouse.down()
 for i in range(300):p.mouse.move(400+i%80,170+i%20)
 p.mouse.up();pan=p.evaluate('__cooperativeSimulation.status()');assert pan['queued']<10,pan;p.evaluate('__coopBarrier.release()');p.evaluate('__coopBarrier.hold()');result=p.evaluate('__queueStress.run()');assert result['count']==300 and not result['status']['busy'] and result['status']['queued']==0,result;print(json.dumps({'panQueued':pan['queued'],'distinctCommands':result['count'],'barriers':result['barriers']},indent=2));b.close()
print('PASS sustained trusted pan coalesces; all300 distinct economic transfers settle with bounded overflow')
