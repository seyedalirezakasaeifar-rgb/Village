"""Physical grocery access, delivered prices, work interruption and recovery."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js','''
window.__marketProbe=()=>{const original=G,originalGraph=graph;try{
 const clone=()=>{G=JSON.parse(JSON.stringify(original));rngState=G.rngState;householdMarketCache=null;serviceAccessCaches.clear();};
 clone();const h=G.households.find(h=>h.people.some(id=>G.people[id].job>=0)),id=h.id,person=h.people.find(id=>G.people[id].job>=0),firm=G.people[person].job;const before=totalMoney();tick();const base={food:G.households[id].food,wages:G.households[id].wages,drift:totalMoney()-before};
 clone();const net=originalGraph(),portals=new Map(net.portals);portals.delete(G.households[id].home);const cut={...net,portals};graph=()=>cut;const cash=totalMoney();tick();const blocked={food:G.households[id].food,privateWages:G.households[id].wages-G.people.filter(p=>p.hh===id).reduce((n,p)=>n+(p.publicIncome||0),0),work:G.people[person].commuteBlocked,job:G.people[person].job,travel:G.households[id].travel,disconnected:G.market.foodDisconnected,drift:totalMoney()-cash};graph=originalGraph;tick();const repaired={food:G.households[id].food,work:G.people[person].commuteBlocked,job:G.people[person].job};
 clone();const home=readBuild(G.households[id].home),shops=G.firms.filter(f=>f.kind==='grocer'&&!f.closed);G.actualServiceFunding={transit:0};const choices=groceryChoices(G.households[id],home,shops),price=choices.every(o=>Math.abs(o.score-(o.f.price*(1+G.policy.foodTax/100)+o.travel/(G.households[id].people.length*1.6)))<.000001)&&choices.some(o=>o.travel>0);
 return {base,blocked,repaired,firm,price};
 }finally{G=original;rngState=G.rngState;graph=originalGraph;householdMarketCache=null;serviceAccessCaches.clear();}};
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42)");r=p.evaluate('__marketProbe()')
 assert r['base']['food']>0 and r['base']['wages']>0,r
 assert r['blocked']['food']==r['blocked']['privateWages']==r['blocked']['travel']==0 and r['blocked']['work'] and r['blocked']['disconnected']>0,r
 assert r['blocked']['job']==r['repaired']['job']==r['firm'] and not r['repaired']['work'] and r['repaired']['food']>0,r
 assert all(abs(r[k]['drift'])<.001 for k in ['base','blocked']) and r['price'],r
 p.evaluate('__townTest.step(180)');assert p.evaluate('__townTest.validate().ok')
 for mutation in ['g.firms[0].pendingEquipment={gain:.06,cost:2000,ordered:g.day,ready:g.day+1}','g.loans=[{id:999,bankId:0,ownerType:"firm",ownerId:0,original:1000,balance:1000,rate:.1,term:360,status:"active",lastPaymentDay:g.day+1}]','g.people[0].commuteBlockedDays=-1']:
  assert p.evaluate('''mutation=>{const raw=__townTest.save(),g=JSON.parse(raw);new Function('g',mutation)(g);return !__townTest.load(g)&&__townTest.save()===raw;}''',mutation),mutation
 assert not errors,errors;b.close();print('PASS disconnected grocery/work markets, delivered prices, repair recovery, currency conservation and atomic financial metadata rejection')
