"""Actual original669 construction and road algorithms through one paid worker root."""
from pathlib import Path
import sys,json,subprocess,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
original=subprocess.check_output(['git','show','669c908:assets/game.js']).decode();source=Path('assets/game.js').read_text();code=Path('experimental/worker/model.generated.js').read_text();bridge=''.join(Path('experimental/worker/'+n).read_text() for n in ['runtime-guard.js','archive-endpoint.js','real-view-bridge.js'])
hook='''paused=true;window.buildProbe={fixture:()=>{seed(42);G.treasury+=100000;G.region-=100000;pendingEvent=null;active='';ensureRoadWear();const id=G.tiles.findIndex(v=>v===1);G.roadWear[id]=25;return archivePayload();},load:a=>{G=JSON.parse(a);rngState=G.rngState;const metrics=G.roadMetrics;invalidateRoads();G.roadMetrics=metrics;pendingEvent=null;active='';},lot:k=>{const before=rngState;try{return buildableCandidates(k).find(p=>canPlace(p.x,p.y,true,k));}finally{rngState=before;}},road:()=>{for(let y=1;y<T-1;y++)for(let x=1;x<T-2;x++)if([x,x+1].every(a=>charterOwns(a,y)&&[0,3].includes(cityCell(a,y))&&!G.landUse?.[roadId(a,y)]&&!buildingAt(a,y)))return [[x,y],[x+1,y]];},repair:()=>{const id=G.roadWear.findIndex((v,i)=>v<96&&G.tiles[i]===1);return {x:id%T,y:Math.floor(id/T)};},apply:m=>{if(m.type==='construction')construct(m.kind,m.x,m.y);else{roadPainted.clear();for(let i=1;i<m.points.length;i++){const prev=m.points[i-1],pt=m.points[i],dx=pt[0]-prev[0],dy=pt[1]-prev[1],steps=Math.max(Math.abs(dx),Math.abs(dy),1);for(let k=0;k<=steps;k++){const x=Math.round(prev[0]+dx*k/steps),y=Math.round(prev[1]+dy*k/steps),key=x+'/'+y;if(!roadPainted.has(key)){roadPainted.add(key);construct('road',x,y,true);}}}flushRoadBatch();roadPainted.clear();}return JSON.parse(archivePayload());}};\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[];errors=[]
 for kind,src in [('oracle',original),('worker',source)]:
  p=b.new_page();p.route('http://build.test/',lambda r:r.fulfill(body=html,content_type='text/html'));p.goto('http://build.test/');p.on('pageerror',lambda e:errors.append(str(e)));p.add_script_tag(content=src.replace('// SOURCE: 99-instrumentation.js',(bridge if kind=='worker' else '')+hook+'// SOURCE: 99-instrumentation.js'));pages.append(p)
 oracle,p=pages;archive=oracle.evaluate('buildProbe.fixture()');oracle.evaluate('a=>buildProbe.load(a)',archive);p.evaluate('''async a=>window.real=await __workerRealView.enable(a.code,a.archive,{initializeAuthority:async ask=>{const r=await ask({type:'initialize-command-owner'});if(!r.ordinaryDayReady)throw Error('Owner unavailable');}})''',{'code':code,'archive':archive});rows=[]
 for kind in ['park','home','grocer','repair','road-stroke']:
  if kind=='road-stroke':m={'type':'road-stroke','points':oracle.evaluate('buildProbe.road()')}
  else:m={'type':'construction','kind':kind,**oracle.evaluate('k=>k==="repair"?buildProbe.repair():buildProbe.lot(k)',kind)}
  expected=oracle.evaluate('m=>buildProbe.apply(m)',m);reply=p.evaluate('m=>real.command(m)',m);actual=reply['model']
  for key in ['visualState','trafficState']:actual.pop(key,None);expected.pop(key,None)
  
  if actual!=expected:
   Path('/tmp/construction-diff.json').write_text(json.dumps({'actual':actual,'expected':expected},indent=2));print({k:[str(actual.get(k))[:300],str(expected.get(k))[:300]] for k in set(actual)|set(expected) if actual.get(k)!=expected.get(k)},flush=True)
  assert actual==expected,kind
  assert reply['paid']['committed'];rows.append(m);p.evaluate('real.settleSaves()')
 before=p.evaluate('real.command({type:"export"})')['archive']
 for m in [{'type':'construction','kind':'park','x':-1,'y':0},{'type':'construction','kind':'__proto__','x':0,'y':0},{'type':'road-stroke','points':[[0,0],[99999,0]]},{'type':'construction','kind':'park',**rows[0]}]:
  result=p.evaluate('m=>real.command(m).then(()=>false,e=>e.message)',m)
  assert result,m
  assert p.evaluate('real.command({type:"export"})')['archive']==before,m
 assert not errors,errors
 Path('experimental/worker/construction-family-proof.json').write_text(json.dumps({'productionEnabled':False,'oracleCommit':'669c908706af997375680674390e46fd132a970a','sourceSha256':hashlib.sha256(source.encode()).hexdigest(),'workerSha256':hashlib.sha256(code.encode()).hexdigest(),'operationsExactFullModelRng':rows,'invalidOrOccupiedRefuseUnchanged':4,'pageErrors':errors},indent=2)+'\n');print('PASS park/home/firm/repair/road-stroke exact original669 model/RNG; four refusals unchanged');b.close()
