"""Catchment allocation, recruitment delay, training time and atomic migrations."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text().replace('// SOURCE: 99-instrumentation.js','''
window.__catchmentProbe=()=>{const oldTown=G,oldGraph=graph;try{
 const neighbors=new Map(),edge=(a,b)=>{if(!neighbors.has(a))neighbors.set(a,[]);if(!neighbors.has(b))neighbors.set(b,[]);neighbors.get(a).push(b);neighbors.get(b).push(a);};edge(0,1);let at=0;for(let i=2;i<=61;i++){edge(at,i);at=i;}const regional=at;at=1;for(let i=62;i<=121;i++){edge(at,i);at=i;}
 const net={neighbors,portals:new Map([[10,1],[11,regional],[20,0],[21,at]])};graph=()=>net;
 G={stats:{population:700},buildings:[{id:10,kind:'clinic'},{id:11,kind:'clinic'}],people:Array.from({length:700},(_,id)=>({id})),households:[{id:0,home:20,people:Array.from({length:400},(_,i)=>i)},{id:1,home:21,people:Array.from({length:300},(_,i)=>400+i)}]};
 const normal=serviceAccess('health');G.households.reverse();const reordered=serviceAccess('health');net.portals.delete(11);serviceAccessCaches.clear();const isolated=serviceAccess('health');return {normal:normal.served,reordered:reordered.served,isolated:isolated.served,shares:isolated.households.map(h=>({id:h.id,served:h.served}))};
 }finally{G=oldTown;graph=oldGraph;serviceAccessCaches.clear();}};
window.__staffTrainingProbe=()=>{const old=G;try{
 G=JSON.parse(JSON.stringify(G));G.people.forEach(p=>{p.skill=0;p.job=-1;p.publicIncome=0;p.previousPublicRole='';});G.civicStaffing={};G.day=1;
 const access={coverage:1,households:G.households.map(h=>({id:h.id,distance:0}))};civicStaffCapacity('school',0,access);const initial=civicStaffCapacity('school',1000,access);G.day=30;const waiting=civicStaffCapacity('school',1000,access);G.day=31;const ready=civicStaffCapacity('school',1000,access);
 const p=G.people.find(p=>p.age>=18&&p.age<=60);p.skill=.54;G.civicTraining=[{person:p.id,days:0,started:1}];G.civicTrainingLastDay=null;G.serviceProvision={school:{paid:100,coverage:1}};
 for(let day=1;day<=119;day++){G.day=day;civicTrainingDay(1);}const before=p.skill;G.day=120;civicTrainingDay(1);const completed=p.skill;civicTrainingDay(1);const repeated=p.skill;
 return {initial:initial.regional,waiting:waiting.regional,ready:ready.regional,before,completed,repeated};
 }finally{G=old;}};
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=source);p.locator('#newTown').click();p.locator('#pause').click()
 geo=p.evaluate('__catchmentProbe()');assert all(abs(geo[k]-v)<.00001 for k,v in {'normal':700,'reordered':700,'isolated':350}.items()),geo
 assert all(abs(h['served']-({0:200,1:150}[h['id']]))<.00001 for h in geo['shares']),geo
 staff=p.evaluate('__staffTrainingProbe()');assert staff['initial']==staff['waiting']==0 and staff['ready']>0,staff
 assert staff['before']==.54 and abs(staff['completed']-.64)<.00001 and staff['completed']==staff['repeated'],staff
 p.evaluate('__townTest.step(180)');assert p.evaluate('__townTest.validate().ok')
 bad=p.evaluate('''()=>{const original=__townTest.save(),g=JSON.parse(original);g.civicStaffing={health:{ready:-1,pending:null}};const reject=!__townTest.load(g);return reject&&__townTest.save()===original;}''');assert bad
 p.locator('[data-panel=community]').click();p.locator('.service-provision details summary').first.click();assert 'Qualified staff' in p.locator('#panelBody').inner_text() or 'qualified local staff' in p.locator('#panelBody').inner_text()
 p.locator('[data-service-policy=health]').click();assert p.locator('[data-policy=healthBudget]').evaluate('(e)=>e===document.activeElement')
 p.locator('[data-panel=community]').click();p.locator('[data-service-access=health]').click();assert not p.locator('#panel').is_visible();assert not errors,errors
 b.close();print('PASS shared catchment allocation/reordering/disconnection, 30-day recruitment, 120-day training, no double same-day credit, save rejection and access UI')
