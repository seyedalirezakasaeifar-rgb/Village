"""Execute the production Activity's exact injected import script in Chromium.

Checks the browser side of the native handshake; does not certify Android dialogs.
"""
from pathlib import Path
import hashlib,json,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
java=(ROOT/'android/app/src/main/java/org/townledger/vale/MainActivity.java').read_text()
match=re.search(r'web\.evaluateJavascript\("(\(function\(\)\{var box=.*?)",null\);',java)
assert match,'Production import script missing'
script=match.group(1).replace('"+quoted+"',json.dumps('fixture archive'))
results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for mode in ['success','rejected','exception']:
  p=browser.new_page();p.set_content('<body>Current town</body>')
  p.evaluate('''mode=>{window.calls=0;window.acks=[];window.observed=null;window.AndroidArchive={restoreResult:ok=>acks.push(ok)};window.__townArchive={restore:raw=>{calls++;observed={busy:document.body.getAttribute('aria-busy'),overlay:!!document.querySelector('[role=alertdialog]'),raw};if(mode==='exception')throw Error('Rejected fixture');return mode==='success';}};}''',mode)
  p.evaluate(script)
  p.wait_for_function('acks.length===1')
  result=p.evaluate('({calls,acks,observed,busy:document.body.hasAttribute("aria-busy"),overlay:!!document.querySelector("[role=alertdialog]")})')
  assert result['calls']==1 and result['acks']==[mode=='success'],result
  assert result['observed']=={'busy':'true','overlay':True,'raw':'fixture archive'},result
  assert not result['busy'] and not result['overlay'],result
  results.append({'mode':mode,**result});p.close()
 browser.close()
print(json.dumps({'activity_sha256':hashlib.sha256(java.encode()).hexdigest(),'cases':results},indent=2))
print('PASS exact production import script: success, rejection, exception acknowledgement and overlay cleanup')
