"""Reproduce late-town public service access and operating constraints."""
from pathlib import Path
import hashlib, json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html

FIXTURE = Path('/tmp/townledger-terminal-31987fc.json')
if not FIXTURE.exists():
    raise SystemExit(f'Missing retained archive: {FIXTURE}')
archive = FIXTURE.read_text()
source = (ROOT / 'assets/game.js').read_text()

probe = r'''window.__lateServiceDiagnosis=(saved,years)=>{
 if(!__townTest.load(saved))throw Error('Retained archive rejected');
 let choices=0;const originalOffer=offerCouncilEvent;offerCouncilEvent=function(){choices++;G.lastEventDay=G.day;return false;};
 const initial={day:G.day,population:G.stats.population,treasury:G.treasury,region:G.region,money:totalMoney(),goods:goodsBalance()};
 for(let y=0;y<years;y++)for(let d=0;d<360;d++)__townTest.step(1);
 offerCouncilEvent=originalOffer;
 const access={},facilities={};
 for(const kind of ['school','health']){
  const a=serviceAccess(kind),std=CIVIC_STANDARDS[kind],all=G.buildings.filter(b=>b.kind===std.building),publicSites=all.filter(isPublicFacility),reachable=new Set(a.households.filter(h=>h.distance!==null).map(h=>h.id)),qualified=G.people.filter(p=>qualifiedForService(p,kind));
  access[kind]={coverage:a.coverage,served:a.served,residents:a.population,households:a.households.length,reachableHouseholds:reachable.size,unreachableResidents:a.households.filter(h=>h.distance===null).reduce((n,h)=>n+h.residents,0),maxRoadDistance:Math.max(0,...a.households.map(h=>h.distance).filter(Number.isFinite))};
  facilities[kind]={total:all.length,public:publicSites.length,private:all.length-publicSites.length,publicSites:publicSites.map(b=>({id:b.id,x:b.x,y:b.y,roadPortal:graph().portals.get(b.id),condition:b.condition,owner:b.owner,title:b.title,firm:b.firm})),staffing:G.civicStaffing?.[kind]||null,unemployedQualified:qualified.filter(p=>reachable.has(p.hh)&&p.job<0).length,qualifiedTotal:qualified.length,unemployedReachableAdults:G.people.filter(p=>reachable.has(p.hh)&&!p.deceased&&!p.movedAway&&p.age>=18&&p.age<=70&&p.job<0).length};
 }
 const out={initial,end:{day:G.day,population:G.stats.population,treasury:G.treasury,region:G.region,debt:G.debt,policy:{healthBudget:G.policy.healthBudget,educationBudget:G.policy.educationBudget,aidBudget:G.policy.aidBudget,outreachBudget:G.policy.outreachBudget,roadBudget:G.policy.roadBudget,militiaBudget:G.policy.militiaBudget,transitBudget:G.policy.transitBudget},facilities,access,provision:G.serviceProvision,actualServiceFunding:G.actualServiceFunding,health:G.health,education:G.education,hardship:G.stats.hardship,employment:G.stats.employment,schoolCount:G.buildings.filter(b=>b.kind==='school').length,clinicCount:G.buildings.filter(b=>b.kind==='clinic').length,unpaidWorkerDays:G.people.reduce((n,p)=>n+(p.unpaidDays||0),0),valid:validateTown(),cashDrift:totalMoney()-initial.money,goodsError:Math.max(0,...goodsBalance().map(x=>Math.abs(x.error||0)))},choicesSuppressed:choices,archive:archivePayload()};return out;
};'''

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page()
    page.set_default_timeout(900000)
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.set_content(html)
    page.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js', probe+'\n// SOURCE: 99-instrumentation.js'))
    page.locator('#newTown').click()
    page.locator('#pause').click()
    result = page.evaluate('x=>__lateServiceDiagnosis(x,25)', archive)
    browser.close()

assert not errors, errors
assert result['end']['valid']['ok'], result['end']['valid']
assert abs(result['end']['cashDrift']) < .1, result['end']['cashDrift']
assert result['end']['goodsError'] < .01, result['end']['goodsError']
path = ROOT/'docs/evidence/food-shortage-recovery8/late-town-service-diagnosis.json'
path.write_text(json.dumps({
    'fixture_archive_sha256': hashlib.sha256(archive.encode()).hexdigest(),
    'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
    'source_commit': __import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'years': 25,
    'method': 'Exact retained generated town, current source, one-day deterministic steps, no council policy changes; household/cash/goods provenance remains in the archive validator.',
    'result': result,
}, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='archive'}, indent=2))
