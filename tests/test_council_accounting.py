"""Exercise every authored choice through the actual Council dialog settlement."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import hashlib,json
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
script=source.decode().replace('// SOURCE: 99-instrumentation.js','''
window.__councilList=()=>COUNCIL_EVENTS.map(e=>({title:e.title,count:e.choices.length}));
window.__councilOpen=(i)=>{const e=COUNCIL_EVENTS[i];showCustomEvent(e.type,e.title,e.text,e.choices);};
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();saved=p.evaluate('__townTest.save()');events=p.evaluate('__councilList()');count=0
 for i,event in enumerate(events):
  for j in range(event['count']):
   assert p.evaluate('s=>__townTest.load(s)',saved);before=p.evaluate('__townTest.get().total');p.evaluate('i=>__councilOpen(i)',i);p.locator(f'[data-event-choice="{j}"]').click();v=p.evaluate('__townTest.validate()');assert v['ok'],(event,j,v);assert abs(p.evaluate('__townTest.get().total')-before)<.001,(event,j);assert p.evaluate('s=>__townTest.load(s)',p.evaluate('__townTest.save()')),(event,j,'restore');count+=1
 assert not errors,errors;assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha;b.close();print('PASS',count,'Council choices: cash, goods, structure, save/restore and no exceptions')
