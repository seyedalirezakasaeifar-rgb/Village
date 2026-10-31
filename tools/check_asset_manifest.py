#!/usr/bin/env python3
"""Verify local audio/image references consumed by offline Android asset packaging."""
from pathlib import Path
import hashlib,json,re,sys,urllib.parse
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'assets'

def refs():
 rows=[]
 music=(ROOT/'src/95-music.js').read_text()
 match=re.search(r'const MUSIC_TRACKS=(\[.*?\]);',music)
 if not match:raise ValueError('MUSIC_TRACKS literal not found')
 for t in json.loads(match.group(1)):rows.append(('assets/music/'+t['file']+'.ogg','music manifest'))
 audio=(ROOT/'src/95-audio.js').read_text()
 for name in sorted(set(re.findall(r"playSfx\('([^']+)'\)",audio))|{'rain','village'}):rows.append(('assets/sound/'+name+'.wav','effects controller'))
 for p in [*ROOT.glob('assets/*.css'),ROOT/'assets/index.html']:
  text=p.read_text()
  for u in re.findall(r'url\([\'"]?([^\)\'"]+)',text):
   u=u.strip()
   if u.startswith(('data:','#')):continue
   rows.append((urllib.parse.urlparse(u).path,'reference in '+p.relative_to(ROOT).as_posix()))
 for ext in ('*.png','*.jpg','*.jpeg','*.webp','*.svg','*.gif'):
  for p in ASSETS.rglob(ext):
   if p.name!='LICENSE.txt' and p.name not in ['townledger.xml']:
    rows.append((p.relative_to(ROOT).as_posix(),'shipped image file'))
 return sorted(set(rows))

def main():
 manifest=[];errors=[];external=[]
 for rel,origin in refs():
  if re.match(r'^(?:[a-z]+:|//|/)',rel):external.append({'reference':rel,'origin':origin});continue
  p=ROOT/rel
  if not p.is_file():errors.append({'missing':rel,'origin':origin});continue
  n=p.stat().st_size
  if n<=0:errors.append({'empty':rel,'origin':origin});continue
  manifest.append({'path':rel,'origin':origin,'bytes':n,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 report={'schema':1,'offlineAndroidAssetRoot':'assets/','references':manifest,'externalOrAbsoluteMediaReferences':external,'errors':errors,'status':'passed' if not errors and not external else 'failed'}
 out=ROOT/'reports/asset-manifest-8.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':report['status'],'references':len(manifest),'errors':errors,'external':external,'report':out.relative_to(ROOT).as_posix()}))
 if errors or external:sys.exit(1)
if __name__=='__main__':main()
