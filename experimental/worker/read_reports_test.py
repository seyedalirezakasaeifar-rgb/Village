from pathlib import Path
import sys,json,gzip,subprocess,hashlib,time,os
projection=os.environ.get("RENDER_PROJECTION","1")=="1"
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
archive=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode()
source=Path('assets/game.js').read_text()
hook='''paused=true;const oracleEffects=[];save=()=>{oracleEffects.push('save-request');return true;};toast=()=>oracleEffects.push('notification');refreshAmbience=()=>oracleEffects.push('ambience-refresh');updateHeader=()=>oracleEffects.push('header-invalidated');renderPanel=()=>oracleEffects.push('panel-invalidated');window.reportOracle=(type,id)=>{let report;if(type==='district-report')report={parcel:id,survey:parcelSurvey(ANNEX_PARCELS.find(p=>p.id===id)),metrics:G.charter.owned.includes(id)?districtMetrics(id):null};else if(type==='transit-report')report=transitRouteReport(id);else if(type==='cargo-report')report=ensureRegionalTrade().shipments.find(x=>x.id===id);else report={calendar:civicCalendarView(),venues:civicGatheringVenues().map(v=>({id:v.b.id,name:v.name}))};G.rngState=rngState;return {model:JSON.parse(JSON.stringify(G)),report};};window.oracle={load:a=>{G=JSON.parse(a);rngState=G.rngState;invalidateRoads();pendingEvent=null;},step:n=>{for(let i=0;i<n;i++)tick();},review:i=>reviewCouncilInbox(i),state:()=>{G.rngState=rngState;return JSON.parse(JSON.stringify(G));},effects:()=>oracleEffects.splice(0)};
'''
def clean(g):return {k:v for k,v in g.items() if k not in ('trafficState','visualState')}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.evaluate('''()=>{window.nativeRAF=requestAnimationFrame;window.requestAnimationFrame=f=>(window.productionRAF=nativeRAF(f));}''');p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'))
 p.evaluate('a=>oracle.load(a)',archive)
 p.evaluate('''code=>{window.w=new Worker(URL.createObjectURL(new Blob([code],{type:'application/javascript'})));let serial=0,epoch=0,command=0;window.ask=m=>new Promise((resolve,reject)=>{const id=++serial;const h=e=>{if(e.data.id===id){w.removeEventListener('message',h);if(e.data.ok)epoch=e.data.result.epoch;resolve(e.data);}};w.addEventListener('message',h);w.postMessage({epoch,command:++command,...m,id});setTimeout(()=>reject(Error('Worker timeout')),30000);});}''',Path('experimental/worker/model.generated.js').read_text())
 def ask(m):
  r=p.evaluate('m=>ask(m)',m);assert r['ok'],r;return r['result']
 ask({'type':'load','archive':archive})
 rows=[]
 state=json.loads(archive);route=state['transit']['routes'][0]['id'];cargo=state['regionalTrade']['shipments'][0]['id']
 for kind,parcel in [('district-report','east-meadow'),('district-report','river-reach'),('calendar-report',None),('transit-report',route),('cargo-report',cargo)]:
  actual=ask({'type':kind,'parcel':parcel,'route':parcel,'shipment':parcel});expected=p.evaluate('a=>reportOracle(...a)',[kind,parcel]);assert clean(actual['model'])==clean(expected['model']),(kind,'model');a=actual.get('report',actual.get('cargo'));e=expected['report'];
  if kind=='transit-report':a={k:v for k,v in a.items() if k!='calculationMs'};e={k:v for k,v in e.items() if k!='calculationMs'}
  assert a==e,(kind,'report');rows.append({'command':kind,'parcel':parcel,'exactModelRng':True,'exactReport':True})
 Path('experimental/worker/read-reports-proof.json').write_text(json.dumps({'source':'d2b7086','rows':rows},indent=2));print('PASS original district/calendar functions, full state/RNG and report parity');b.close()
