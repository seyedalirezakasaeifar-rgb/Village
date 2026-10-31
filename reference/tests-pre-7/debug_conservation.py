from playwright.sync_api import sync_playwright
from pathlib import Path
root=Path(__file__).resolve().parent.parent
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox'])
 page=b.new_page();page.set_content((root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','').replace('<script src="game.js"></script>',''));page.add_script_tag(content=(root/'assets/game.js').read_text());page.evaluate('()=>__townTest.reset("frontier")')
 out=page.evaluate('''()=>{let prev=__townTest.get();for(let i=0;i<430;i++){__townTest.step(1);let current=__townTest.get(),diff=current.total-prev.total;if(Math.abs(diff)>1)return {day:current.day,diff,prev,current}}return {status:'conserved'}}''')
 print(out)
 b.close()
