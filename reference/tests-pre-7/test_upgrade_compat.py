"""Load supplied 5.6 saves in the current build, verify historic geometry remains valid."""
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
old=(root/'reference/v5.6/assets/game.js').read_text()
new=(root/'assets/game.js').read_text()
html=(root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>','')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True, executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox'])
 o=b.new_page();o.set_content(html);o.add_script_tag(content=old);o.evaluate('__townTest.reset()');o.evaluate('__townTest.step(30)');raw=o.evaluate('__townTest.save()');balance=o.evaluate('__townTest.get().total')
 n=b.new_page();n.set_content(html);n.add_script_tag(content=new)
 assert n.evaluate('(json)=>__townTest.load(json)',raw),'5.6 game cannot be upgraded'
 assert abs(n.evaluate('__townTest.get().total')-balance)<0.1
 n.evaluate('__townTest.step(50)')
 assert not n.evaluate('''()=>{const s=JSON.parse(__townTest.save());return s.buildings.some(b=>s.tiles[b.y*56+b.x]===1)}''')
 print('PASS 5.6 -> current compatible save, maintained financial balance and 50 more days')
 b.close()
