"""Sustained scenario chapters, no duplicate awards, migration and real policy loop."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
script=source.decode().replace('// SOURCE: 99-instrumentation.js','''
window.__programmeProbe=()=>{const original=G,originalMetrics=programmeMetrics;try{
 const rows=[];for(const scenario of Object.keys(SCENARIO_PROGRAMMES)){G=JSON.parse(JSON.stringify(original));G.scenario=scenario;G.day=1;initializeScenarioProgramme();let metrics={employment:100,hardship:0,food:100,medical:100,school:100,buffers:100,reserve:999,banks:3,blocked:0,training:100,treasury:100000,debt:0};programmeMetrics=()=>metrics;
 G.day=2;updateScenarioProgramme();const held=G.scenarioProgramme.held;updateScenarioProgramme();if(G.scenarioProgramme.held!==held)throw Error('Duplicate day counted');G.day=3;metrics.food=0;metrics.medical=0;updateScenarioProgramme();if(G.scenarioProgramme.held!==0)throw Error('Missing condition did not reset count');metrics.food=metrics.medical=100;
 const funds=totalMoney();for(let day=4;day<230;day++){G.day=day;updateScenarioProgramme();}const p=G.scenarioProgramme;if(p.stage!==3||p.completed.length!==3||p.held!==0)throw Error('Programme did not complete');if(totalMoney()!==funds)throw Error('Programme created money');const count=p.completed.length;updateScenarioProgramme();if(p.completed.length!==count)throw Error('Duplicate completion');rows.push({scenario,completed:p.completed});}
 return rows;
 }finally{G=original;programmeMetrics=originalMetrics;}};
window.__transientProbe=()=>{toast('Message from a different town');showCustomEvent('TEST','Old decision','Do not apply to the next town',[{title:'Continue',apply:()=>{}}]);};
// SOURCE: 99-instrumentation.js''')
# This originless programme fixture uses successful in-memory local storage;
# denied-store warning behavior is covered by test_save_chronology.py.
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content="const fixtureStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>fixtureStore.get(k)??null,setItem:(k,v)=>fixtureStore.set(k,String(v)),removeItem:k=>fixtureStore.delete(k)}})");p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();rows=p.evaluate('__programmeProbe()');assert len(rows)==5
 p.evaluate('__transientProbe();__townTest.reset("settlement",42)');assert not p.locator('#toast').is_visible() and not p.locator('#eventDialog').is_visible();p.evaluate('__townTest.step(90)');passive=json.loads(p.evaluate('__townTest.save()'))['scenarioProgramme'];assert passive['stage']==1,passive
 p.locator('[data-panel=agenda]').click();p.locator('[data-panel=overview]').click();p.locator('.mayor-report > summary').click();button=p.locator('[data-programme-panel=community]').first;button.scroll_into_view_if_needed();assert button.bounding_box()['y']+button.bounding_box()['height']<=p.locator('#panel').bounding_box()['y']+p.locator('#panel').bounding_box()['height'];button.click();assert 'local care and learning' in p.locator('#panelBody').inner_text().lower()
 p.locator('[data-panel=policies]').click()
 for key,value in [('healthBudget','220'),('educationBudget','420'),('roadBudget','80')]:
  f=p.locator(f'[data-policy={key}]');f.evaluate('e=>e.closest("details").open=true');f.fill(value)
 p.locator('#enactPolicy').click();p.evaluate('__townTest.step(180)');after=json.loads(p.evaluate('__townTest.save()'));assert after['scenarioProgramme']['stage']>=2,after['scenarioProgramme']
 saved=p.evaluate('__townTest.save()');p.evaluate('__townTest.step(60)');expected=p.evaluate('__townTest.save()');assert p.evaluate('s=>__townTest.load(s)',saved);p.evaluate('__townTest.step(60)');actual=p.evaluate('__townTest.save()');assert json.loads(expected)['scenarioProgramme']==json.loads(actual)['scenarioProgramme']
 for change in ['g.scenario="constructor";delete g.scenarioProgramme','g.scenario="__proto__";delete g.scenarioProgramme','g.scenarioProgramme.stage=99','g.scenarioProgramme.held=9999','g.scenarioProgramme.lastDay=g.day+1','g.scenarioProgramme.baseline=[]','g.civicTrainingCompletions=-1']:
  assert p.evaluate('''code=>{const raw=__townTest.save(),g=JSON.parse(raw);new Function('g',code)(g);return !__townTest.load(g)&&__townTest.save()===raw;}''',change),change
 assert p.evaluate('''()=>{const g=JSON.parse(__townTest.save());delete g.scenarioProgramme;return __townTest.load(g)&&JSON.parse(__townTest.save()).scenarioProgramme.started===g.day;}''')
 p.locator('[data-panel=agenda]').click();assert p.locator('.programme-chart').count()==1;assert 'observed outcomes' in p.locator('#panelBody').inner_text().lower();assert not errors,errors;b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-player-loop';out.mkdir(parents=True,exist_ok=True);(out/'programme.json').write_text(json.dumps({'source_sha256':sha,'logic':rows,'passive':passive,'afterFundedPolicy':after['scenarioProgramme'],'errors':errors},indent=2)+'\n');print('PASS five scenario programmes, consecutive-day resets, no duplicate day/grant, passive constraint, actual policy enactment/progression, continuation, legacy migration and atomic rejection')
