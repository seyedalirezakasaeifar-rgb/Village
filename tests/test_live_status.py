"""Fast batches and pause must publish current care/school/firm figures."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest();probe='''window.__expectedMarket=()=>{const m=marketSignal(),care=G.serviceProvision?.health?.coverage,school=G.serviceProvision?.school?.coverage;return {title:m.title,detail:Number.isFinite(care)&&Number.isFinite(school)?Math.round(care*100)+'% care · '+Math.round(school*100)+'% school · '+m.m.open+' firms':m.m.open+' firms · '+m.m.projects+' projects · '+G.stats.hardship+'% hardship'}};window.__repeatHeader=()=>{const original=marketSignal;let calls=0;marketSignal=()=>{calls++;return original()};try{for(let i=0;i<20;i++)updateHeader();return calls}finally{marketSignal=original}};''';script=source.decode().replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("settlement",42)');rows=[]
 for days in [4,9,181,7]:
  p.evaluate('n=>__townTest.step(n)',days);expected=p.evaluate('__expectedMarket()');actual={'title':p.locator('#marketHeadline').inner_text(),'detail':p.locator('#marketDetail').inner_text()};assert actual==expected,{'day':p.evaluate('__townTest.get().day'),'actual':actual,'expected':expected};rows.append({'day':p.evaluate('__townTest.get().day'),**actual});assert p.evaluate('__repeatHeader()')==0
 b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-visual-acceptance';out.mkdir(parents=True,exist_ok=True);(out/'live-status.json').write_text(json.dumps({'source_sha256':sha,'pausedBatches':rows,'unchangedHeaderUpdates':20,'extraMarketScans':0},indent=2)+'\n');print('PASS current status after skipped-day batches and pause, without repeated paused market scans')
