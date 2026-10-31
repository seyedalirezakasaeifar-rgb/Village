"""Pure atlas/transit adapter; optional worker ref supports pre-integration testing."""
import os,subprocess,json,hashlib
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text();worker_ref=os.environ.get('TOWNLEDGER_TRANSIT_TEST_REF');helper=''
if 'function remapTransitState(' not in source:
 if not worker_ref:
  print('SKIP: transit engine is not integrated; set TOWNLEDGER_TRANSIT_TEST_REF to exercise its exact helper.');raise SystemExit(0)
 worker=subprocess.check_output(['git','show',worker_ref+':src/46-transit-network.js'],cwd=ROOT,text=True)
 helper=worker[worker.index('function remapTransitState('):worker.index('function remapTransitTiles(')]
probe=helper+'''\nwindow.__urbanMigration=normalizeRegionArchive;\n'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click()
 result=p.evaluate('''()=>{const live=__townTest.save(),current=JSON.parse(live),input={gridSize:80,tiles:new Array(6400).fill(0),worldSeed:42,people:[{transitTrip:{day:1,fare:.65,routes:[1],settled:true}}],buildings:[],transit:{version:1,revision:3,tracks:[80*27+49,80*27+50],fares:23,routes:[{id:1,mode:'bus',depot:34,path:[80*27+49,80*27+50],stops:[80*27+49,80*27+50],offsets:[0,1]},{id:2,mode:'elevated',depot:35,path:[80*27+49,80*27+50],stops:[17,18],offsets:[0,1]}]}};const original=JSON.stringify(input),mapped=__urbanMigration(input),s=mapped.transit,expected=[128*27+49,128*27+50];if(JSON.stringify(s.tracks)!==JSON.stringify(expected)||JSON.stringify(s.routes[0].stops)!==JSON.stringify(expected)||s.routes[1].stops.join(',')!=='17,18'||s.routes[0].depot!==34||s.routes[1].depot!==35||s.routes[0].offsets.join(',')!=='0,1'||s.fares!==23||!mapped.people[0].transitTrip.settled)throw Error('Transit identifiers/tickets changed');s.routes[0].path[0]=0;if(JSON.stringify(input)!==original||__townTest.save()!==live)throw Error('Candidate alias or live mutation');const invalid=JSON.parse(original);invalid.transit.tracks=[-1];if(__townTest.load(invalid)||__townTest.save()!==live)throw Error('Malformed transit import was not atomic');return {gridFrom:80,gridTo:128,tracksAndBusStopsRemapped:true,institutionIdsAndOffsetsPreserved:true,settledFarePreserved:true,inputIndependent:true,liveTownUnchanged:true,malformedImportAtomic:true};}''');b.close()
out=ROOT/'docs/previews/urban8/pure-transit-migration.json';out.write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'workerRef':worker_ref,'exactWorkerHelperInjected':bool(helper),'helper_sha256':hashlib.sha256(helper.encode()).hexdigest() if helper else None,'result':result},indent=2)+'\n');print(json.dumps(result,indent=2))
