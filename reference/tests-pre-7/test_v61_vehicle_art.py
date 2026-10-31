"""Raster proof that car and truck silhouettes rotate, not only their lights."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os,json
R=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox']);p=b.new_page(viewport={'width':600,'height':440});html=(R/'assets/index.html').read_text().replace('<script src="game.js"></script>','');p.set_content(html)
 script=(R/'assets/game.js').read_text();at=script.rfind('})();');p.add_script_tag(content=script[:at]+'window.__paintVehicle61=vehiclePaint;'+script[at:])
 result=p.evaluate('''()=>{const results=[];for(const style of ['car','truck']){const samples=[];for(const [dx,dy] of [[36,18],[-36,18],[-36,-18],[36,-18]]){const c=document.createElement('canvas');c.width=80;c.height=80;const g=c.getContext('2d');__paintVehicle61(g,{style,color:'#b35f46',id:1},{x:40,y:40,dx,dy},0);const a=g.getImageData(0,0,80,80).data;let hash=0;for(let i=0;i<a.length;i++)hash=(Math.imul(hash,31)+a[i])>>>0;samples.push(hash);}if(new Set(samples).size!==4)throw Error(style+' failed heading-sensitive raster');results.push({style,distinctHeadings:new Set(samples).size});}return results;}''')
 (R/'reports/v6.1/vehicle-orientation.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',result);b.close()
