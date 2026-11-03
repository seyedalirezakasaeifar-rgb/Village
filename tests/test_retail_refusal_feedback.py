"""Guard-only refusal reasons disclose real limits; no workers, money or sites granted."""
import hashlib,json,subprocess
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
BASE='60ab7fe6cfc958f69a084a538c946672ff51eb8a';source=(ROOT/'assets/game.js').read_text();old=subprocess.check_output(['git','show',BASE+':assets/game.js'],cwd=ROOT,text=True)
probe=r'''window.__refusals=()=>{const saved=G,demandFn=cityDemand,candidates=buildableCandidates;const cases=[{name:'residents',residents:319},{name:'confidence',confidence:41.9},{name:'project',project:true},{name:'competition',opened:640},{name:'combined',residents:200,confidence:20,project:true,opened:900},{name:'automaticPaused',automatic:true},{name:'exactThresholds'},{name:'closedCompetitor',closed:true,opened:999},{name:'expiredWindow',opened:640,day:1000}];try{return cases.map(c=>{G=JSON.parse(JSON.stringify(saved));G.day=c.day||999;G.autoBuild=false;G.projects=c.project?[{retailCentre:true}]:[];G.firms=c.opened?[{retailCentre:true,closed:!!c.closed,openedDay:c.opened}]:[];cityDemand=()=>({residents:c.residents??320,confidence:c.confidence??42});buildableCandidates=()=>{throw Error('Reached site screening')};const before=JSON.stringify(G),rng=rngState;let result;try{result=urbanRetailProposal(c.automatic?false:'preview')}catch(e){if(e.message!=='Reached site screening')throw e;result={screenPassed:true}}if(before!==JSON.stringify(G)||rng!==rngState)throw Error('Read changed model or RNG');return {name:c.name,...result}})}finally{G=saved;cityDemand=demandFn;buildableCandidates=candidates}};'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);rows=[]
 for js in [old,source]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=js.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();rows.append(p.evaluate('__refusals()'));p.close()
 b.close()
a,z=rows
assert [r.get('screenPassed',False)for r in a]==[r.get('screenPassed',False)for r in z]
by={r['name']:r for r in z}
for name,text in [('residents','319 residents'),('confidence','confidence is 41'),('project','already under construction'),('competition','at least 1 simulated day'),('automaticPaused','development is paused')]:assert text in by[name]['reason'],by[name]
assert len(by['combined']['blockers'])==4
for name in ['exactThresholds','closedCompetitor','expiredWindow']:assert by[name]['screenPassed'],by[name]
print(json.dumps({'base':BASE,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':z,'baselineAdmissionIdentical':True,'readOnlyModelAndRNG':True,'scope':'Isolated eligibility guard; reaching site screen is not a viable site or available-worker claim'},indent=2))
