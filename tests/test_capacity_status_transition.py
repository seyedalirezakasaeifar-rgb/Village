"""Evidence: supported wire states can fail after death without new identities."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json,os
source=(ROOT/'assets/game.js').read_text();probe=r'''
window.__statusCapacity=()=>{const rows={};for(const kind of ['people','households']){__townTest.reset('settlement',42);__townTest.step(30);__inactivePersonCodec.enable(true);G.treasury+=G.region;G.region=0;for(const p of G.people)p.age=20;
 if(kind==='people'){while(G.people.filter(p=>p.deceased||p.movedAway).length<16000)G.people.push({id:G.people.length,name:'Historical identity',age:96,hh:0,job:-1,deceased:true,last:[]});G.people[G.households[0].people[0]].age=96;}
 else{while(G.households.filter(h=>!h.people.length).length<6000)G.households.push({id:G.households.length,name:'Estate',people:[],home:-1,cash:0,deposits:{},last:[]});for(const id of G.households[0].people)G.people[id].age=96;}
 const wire=archivePayload();if(!hydrateSave(wire))throw Error('Initial state invalid');const total=G[kind].length,money=totalMoney();yearlyDemographics();let error='',encoded='';try{encoded=archivePayload()}catch(e){error=String(e)}if(Boolean(error)!==window.expectStatusFailure||G[kind].length!==total||totalMoney()!==money)throw Error('Expected status-only failure not reproduced: '+kind);let legacyRefused=false;if(encoded){const legacy=JSON.parse(encoded);legacy.version=2;legacyRefused=!hydrateSave(legacy);if(!legacyRefused)throw Error('Legacy partition bound bypassed');}rows[kind]={legacyRefused,admittedBytes:new Blob([wire]).size,totalBefore:total,totalAfter:G[kind].length,moneyPreserved:true,historicalAfter:G[kind].filter(r=>kind==='people'?r.deceased||r.movedAway:!r.people.length).length,error};}return rows;};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('(value)=>window.expectStatusFailure=value',bool(os.environ.get('CAPACITY_EXPECT_STATUS_FAILURE')));r=p.evaluate('__statusCapacity()');b.close()
out=ROOT/'reports/capacity-status';out.mkdir(exist_ok=True);(out/('negative.json' if os.environ.get('CAPACITY_EXPECT_STATUS_FAILURE') else 'fixed.json')).write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'statusTransition':r},indent=2)+'\n');print('PASS',r)
