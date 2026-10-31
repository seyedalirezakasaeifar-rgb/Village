"""Cross-system save faults with actual route fares, cargo, provider and mall escrow."""
import ast,hashlib,json
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
def fixture(path):
 tree=ast.parse((ROOT/'tests'/path).read_text())
 return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
probe=fixture('test_transit_network.py')+'\n'+fixture('test_save_adversarial.py')+r'''
window.__saveComposite=()=>{
 G.autoBuild=false;G.policy.privateServices=1;G.policy.educationBudget=0;G.policy.defenseBudget=0;G.policy.serviceVoucherBudget=100;G.policy.privateTuitionCap=4;G.policy.privateFireFeeCap=1;
 for(const p of G.people)if(p.age>=18&&p.age<=60)p.skill=.6;
 __transitProbe.setup();__transitProbe.rail();__townTest.step(1);
 const provider=seekPrivateServiceInvestment('school');if(!G.projects.some(p=>p.privateService))throw Error('Provider fixture failed: '+provider);
 // Controlled catchment growth preserves existing resident IDs and every wallet.
 for(const h of G.households)for(let j=0;j<18;j++){const p={id:G.people.length,name:'Save QA catchment resident',age:29,skill:.7,health:90,hh:h.id,job:-1,life:70,last:[]};G.people.push(p);h.people.push(p.id);}
 invalidateUrban();invalidateBuildingIndex();invalidateRoads(false);recompute();G.stats.marketConfidence=75;
 const mall=urbanRetailProposal(true);if(!mall.ok)throw Error('Mall fixture failed: '+mall.reason);
 const f=G.firms.find(f=>f.kind==='grocer');for(const m of OUTSIDE_MARKETS)if(dispatchRegional(f,'food',10,'import',regionalQuote(f,m,'food','import'))>0)break;
 if(!G.regionalTrade.shipments.length)throw Error('Missing paid cargo');
 // Add one controlled paid ride using the real reservation/settlement APIs;
 // catchment setup invalidates old trip caches, so require a new receipt.
 const route=G.transit.routes.find(r=>r.mode==='bus'&&r.stats.operating),rider=G.people.find(p=>p.job>=0),ticket=route&&{routes:[route.id],time:20,fare:.65,transfers:0,day:G.day};
 if(!ticket||!transitReserve(ticket))throw Error('No passenger capacity for paid receipt');transitCollectFare(G.households[rider.hh],ticket);rider.transitTrip=ticket;
 if(!ticket.settled)throw Error('Missing paid passenger receipt');
 const total=totalMoney(),before=archivePayload(),g=JSON.parse(before),receipt=JSON.stringify(g.people.map(p=>p.transitTrip)),payloads=JSON.stringify({cargo:g.regionalTrade.shipments,transit:g.transit,projects:g.projects});
 if(!hydrateSave(before)||Math.abs(totalMoney()-total)>.001)throw Error('Composite restore lost money');
 if(JSON.stringify(G.people.map(p=>p.transitTrip))!==receipt||JSON.stringify({cargo:G.regionalTrade.shipments,transit:G.transit,projects:G.projects})!==payloads)throw Error('Composite restore changed authoritative receipts/escrow/cargo');
 if(!validateTown().ok)throw Error('Composite restored invalid');
 return {grid:T,people:G.people.length,routes:G.transit.routes.length,settledTickets:G.people.filter(p=>p.transitTrip).length,fares:G.transit.fares,cargo:G.regionalTrade.shipments.length,providerEscrow:G.projects.filter(p=>p.privateService).reduce((n,p)=>n+p.serviceEscrow,0),mallEscrow:G.projects.filter(p=>p.retailCentre).reduce((n,p)=>n+p.urbanEscrow,0),cashConserved:true,receiptsPreserved:true};
};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__saveComposite()');r['faults']=p.evaluate('__saveQA()');b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-save-qa';out.mkdir(exist_ok=True);(out/'composite.json').write_text(json.dumps({'source_sha256':sha,'controlledCatchment':True,'result':r},indent=2)+'\n');print('PASS composite records and atomic faults',r)
