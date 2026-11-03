"""A schema-8 older app may retain optional history without updating it."""
import json,hashlib,subprocess
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text();old=subprocess.check_output(['git','show','0a6d217933eb0eac0c42787483ae96c624d23ef5:assets/game.js'],cwd=ROOT,text=True)
probe="window.__historyGap={state:()=>({day:G.day,activity:G.urban?.activity||[],valid:validateUrban(G)}),record:()=>urbanRecordActivity(),html:key=>urbanNeighborhoodLifeHtml(key),delta:key=>urbanActivityDelta(key)};"
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for js in [source,old]:
  p=b.new_page();p.set_content(html);p.add_script_tag(content=js.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();pages.append(p)
 current,legacy=pages;current.evaluate("__townTest.reset('settlement',42);__townTest.step(180)");initial=current.evaluate('__townTest.save()');assert legacy.evaluate('a=>__townTest.load(a)',initial);legacy.evaluate('__townTest.step(90)');stale=legacy.evaluate('__townTest.save()');assert current.evaluate('a=>__townTest.load(a)',stale);before=current.evaluate('__historyGap.state()');current.evaluate('__townTest.step(90)');first=current.evaluate('__historyGap.state()');print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'olderAppRoundTrip':{'before':before['day'],'oldObservationDays':[s['day']for s in before['activity']],'after':first['day'],'newObservationDays':[s['day']for s in first['activity']],'selfArchiveValid':first['valid']}},indent=2),flush=True)
 assert first['valid']and len(first['activity'])==1,first
 message=current.evaluate('k=>__historyGap.html(k)',next(iter(first['activity'][0]['blocks'])))
 assert f"Latest activity sample: day {first['activity'][0]['day']}" in message,message
 checkpoint=current.evaluate('__townTest.save()');assert current.evaluate('a=>__townTest.load(a)',checkpoint);assert json.loads(checkpoint)==json.loads(current.evaluate('__townTest.save()'))
 current.evaluate('__townTest.step(90)');second=current.evaluate('__historyGap.state()');assert second['valid']and len(second['activity'])==2 and second['activity'][1]['day']-second['activity'][0]['day']==90,second
 b.close()
print('PASS older-app stale optional history resets its comparison without damaging saves')
