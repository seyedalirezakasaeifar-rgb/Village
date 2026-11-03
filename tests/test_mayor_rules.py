"""All three direction state machines: sustained results, once/day, no rewards.
This is a controlled metric fixture, separate from the real economic playthrough.
"""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text()
probe='''
window.__mayorRules=()=>{const original=G,metricsOriginal=mayorMetrics,rows=[];try{
 for(const direction of Object.keys(TOWN_DIRECTIONS)){
  G=JSON.parse(JSON.stringify(original));G.day=1;delete G.mayorJourney;
  const p=ensureMayorJourney();p.direction=direction;
  const metrics={employment:90,hardship:5,food:100,medical:90,school:90,reserve:60,delivery:true,agreement:true,industry:true,waterfront:true,neighbourhood:true,fishery:true,wharf:true};
  mayorMetrics=()=>metrics;const cash=totalMoney();
  G.day=2;mayorJourneyDay();if(p.stage!==1)throw Error('First stage absent');mayorJourneyDay();if(p.stage!==1)throw Error('Duplicate day advanced');
  G.day=3;mayorJourneyDay();G.day=4;mayorJourneyDay();if(p.stage!==3)throw Error('Sequential stage missing');
  G.day=5;mayorJourneyDay();if(p.held!==1)throw Error('Healthy day missing');
  metrics.food=0;metrics.medical=0;G.day=6;mayorJourneyDay();if(p.held!==0)throw Error('Unhealthy day did not reset final sustain');
  metrics.food=100;metrics.medical=90;
  for(let day=7;day<=36;day++){G.day=day;mayorJourneyDay();}
  if(p.stage!==4||p.completed.length!==4||p.held!==0)throw Error('Final sustain failed');
  const count=G.events.length;G.day=37;mayorJourneyDay();if(G.events.length!==count)throw Error('Duplicate completion story');
  if(totalMoney()!==cash)throw Error('Direction invented a reward');if(!validateMayorJourney(G))throw Error('Completed state invalid');
  rows.push({direction,completed:p.completed,moneyDelta:totalMoney()-cash});
 }
 return rows;
}finally{G=original;mayorMetrics=metricsOriginal;}};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390})
 p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'))
 p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click()
 rows=p.evaluate('__mayorRules()');assert len(rows)==3
 b.close()
out=ROOT/'reports/player-experience';out.mkdir(parents=True,exist_ok=True)
(out/'rules.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'controlledMetricFixture':True,'directions':rows},indent=2)+'\n')
print('PASS three direction paths, sequential evidence, once-per-day progression, final 30-day reset and recovery, no repeated completion, no cash reward, valid completed archive')
