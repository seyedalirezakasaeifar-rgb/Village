"""Paid natural shoreline detour is eight edges; six-edge crossing saves two."""
import ast,hashlib,json,subprocess
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
BASE='60ab7fe6cfc958f69a084a538c946672ff51eb8a';source=(ROOT/'assets/game.js').read_text();old=subprocess.check_output(['git','show',BASE+':assets/game.js'],cwd=ROOT,text=True);tree=ast.parse((ROOT/'tests/test_road_bridge.py').read_text());fixture=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='probe'for t in n.targets))
probe=r'''window.__stepQuote={setup:()=>{const start=__bridgeTest.setup(),total=totalMoney(),cash=G.treasury;for(let x=63;x<=69;x++)construct('road',x,14,true);flushRoadBatch();invalidateRoads();const q=bridgeCandidateFromBank(start.bank),path=routeBetween(q.banks[0],q.banks[1]);return {q,path,oldSteps:path.length-1,newSteps:q.cells.length+1,totalBefore:total,totalAfter:totalMoney(),paidDetour:cash-G.treasury}},review:bank=>reviewRoadBridge(bank),commit:q=>commitRoadBridge(q.bank,q.key),save:()=>__townTest.save()};'''
rows=[];archives=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for label,js in [('base',old),('candidate',source)]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=js.replace('// SOURCE: 99-instrumentation.js',fixture+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__stepQuote.setup()');assert r['q']['ok'] and r['oldSteps']==8 and r['newSteps']==6 and r['paidDetour']==1050 and r['totalBefore']==r['totalAfter'],r
  if label=='candidate':
   assert r['q']['gain']==2 and r['q']['existingSteps']==8 and r['q']['crossingSteps']==6
   p.evaluate('q=>__stepQuote.review(q.bank)',r['q']);text=p.locator('#eventText').inner_text();assert 'current route takes 8 road steps' in text and 'crossing takes 6' in text and 'saves 2 road steps' in text,text;p.locator('[data-event-choice="1"]').click();r['visibleReview']=text
  else:assert r['q']['gain']==3
  # Direct authorization oracle compares paid economic outcomes without UI audit differences.
  if label=='candidate':fresh=p.evaluate('__stepQuote.setup()')
  else:fresh=r
  result=p.evaluate('q=>__stepQuote.commit(q)',fresh['q']);assert result['ok'],result;archives.append(json.loads(p.evaluate('__stepQuote.save()')));rows.append({'label':label,**r});p.close()
 b.close()
assert archives[0]==archives[1], 'Disclosure changed paid bridge outcome'
print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'base':BASE,'cases':rows,'completePaidBridgeOutcomeIdentical':True,'equalLengthTopologyManufactured':False},indent=2))
