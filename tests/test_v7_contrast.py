from pathlib import Path
from playwright.sync_api import sync_playwright
import json
R=Path(__file__).resolve().parents[1]
scan='''()=>{const rgb=s=>{const a=s.match(/[\\d.]+/g);return a?[+a[0],+a[1],+a[2],a[3]==null?1:+a[3]]:[0,0,0,0]},blend=(a,b)=>[0,1,2].map(i=>a[i]*a[3]+b[i]*(1-a[3])),lum=a=>a.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);const bad=[];for(const el of document.querySelectorAll('body *')){if(![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))continue;const r=el.getBoundingClientRect(),cs=getComputedStyle(el);if(r.width<1||r.height<1||r.bottom<0||r.top>innerHeight||r.left>innerWidth||r.right<0||cs.visibility==='hidden'||cs.display==='none')continue;if(el.closest('#welcome')&&getComputedStyle(document.querySelector('#welcome')).display==='none')continue;let node=el,chain=[];while(node){chain.unshift(rgb(getComputedStyle(node).backgroundColor));node=node.parentElement}let bg=[255,255,255];for(const a of chain)bg=blend(a,bg);const fg=blend(rgb(cs.color),bg),a=lum(fg),b=lum(bg),contrast=(Math.max(a,b)+.05)/(Math.min(a,b)+.05),large=parseFloat(cs.fontSize)>=24||(parseFloat(cs.fontSize)>=18.66&&+cs.fontWeight>=700);if(contrast<(large?3:4.5))bad.push({text:el.textContent.trim().slice(0,70),tag:el.tagName,cls:el.className,fg:cs.color,bg,ratio:+contrast.toFixed(2)});}return bad;}'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.goto((R/'assets/index.html').as_uri());result={'menu':p.evaluate(scan)};p.locator('#townSeed').fill('42');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.step(120)')
 for tab in ['overview','economy','agenda','policies','treasury','banking','community','businesses','citizens','construction','journal','settings']:
  if not p.locator(f'[data-panel={tab}]').evaluate('e=>e.classList.contains("active")'):p.locator(f'[data-panel={tab}]').click()
  p.wait_for_timeout(100);assert p.locator('#panelBody').evaluate('e=>e.clientHeight')>30
  if tab=='policies':p.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)');p.locator('[data-policy=policyRate]').scroll_into_view_if_needed()
  rows=[]
  for step in range(min(100,int(p.locator('#panelBody').evaluate('e=>Math.ceil(e.scrollHeight/Math.max(1,e.clientHeight))+1')))):
   rows+=p.evaluate(scan);p.locator('#panelBody').evaluate('(e,step)=>e.scrollTop=step*e.clientHeight',step)
  result[tab]=rows
 # Exercise a real council choice modal too.
 p.locator('[data-panel=agenda]').click()
 if p.locator('[data-inbox]').count():
  p.locator('[data-inbox]').first.click();result['council-modal']=p.evaluate(scan)
 (R/'reports/v7.0/contrast.json').write_text(json.dumps(result,indent=2));print({k:len(v) for k,v in result.items()});assert not any(result.values()),'Contrast below required ratio';p.screenshot(path=str(R/'reports/v7.0/settings-phone.png'));b.close()
