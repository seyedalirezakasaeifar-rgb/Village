#!/usr/bin/env python3
"""Assemble ordered source modules into the offline distribution script."""
from pathlib import Path
import subprocess, json, re
ROOT=Path(__file__).resolve().parents[1]
parts=sorted((ROOT/'src').glob('*.js'))
output='\n'.join('// SOURCE: '+p.name+'\n'+p.read_text() for p in parts)
metadata=json.loads((ROOT/'release.json').read_text())
output=re.sub(r'const RELEASE=Object.freeze\(\{[^\n]+\}\);','const RELEASE=Object.freeze('+json.dumps(metadata,separators=(',',':'))+');',output,count=1)
(ROOT/'assets/game.js').write_text(output)
subprocess.run(['node','--check',str(ROOT/'assets/game.js')],check=True)
print('Assembled',len(parts),'modules,',len(output),'characters')
