"""Earlier public-only project counters retain their meaning after private integration."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_text()
probe='''
window.__projectCounterMigration=()=>{const original=G,metricBase=programmeMetrics,coverageBase=localCivicCoverage;try{
 G=JSON.parse(JSON.stringify(original));delete G.civicProjects;G.civicTrainingCompletions=0;G.privateTrainingCompletions=100;const h=G.households.find(h=>h.people.length);civicProjectStart('skills','network',h.id);const p=G.civicProjects.active.skills;
 delete p.trainingScope;p.trainingBaseline=0;programmeMetrics=()=>({...metricBase(),reserve:100});localCivicCoverage=()=>1;
 const legacy=civicProjectObservation(p);if(legacy.met||!legacy.evidence.includes('0 new'))throw Error('Old public-only baseline consumed historical private terms');
 p.trainingScope='all';p.trainingBaseline=100;G.privateTrainingCompletions=101;const combined=civicProjectObservation(p);if(!combined.met||!combined.evidence.includes('1 new'))throw Error('New combined scope ignored real additional private learning');
 if(!validateCivicProjects(G))throw Error('Combined scope archive rejected');delete p.trainingScope;if(!validateCivicProjects(G))throw Error('Legacy scope archive rejected');p.trainingScope='unknown';if(validateCivicProjects(G))throw Error('Unknown counter scope accepted');
 return{legacyObservation:legacy.evidence,combinedObservation:combined.evidence};
}finally{G=original;programmeMetrics=metricBase;localCivicCoverage=coverageBase;}};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__projectCounterMigration()');b.close()
out=ROOT/'reports/civic-projects';out.mkdir(parents=True,exist_ok=True);(out/'legacy-counters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledCounterFixture':True,**result},indent=2)+'\n')
print('PASS legacy public-only term baseline, new combined public/private scope, valid old/new archives and unknown-scope rejection')
