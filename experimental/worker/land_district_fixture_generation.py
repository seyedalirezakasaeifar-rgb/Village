"""Reproduce ordinary funded fixture prefixes using untouched current-source tests.
Only stop/write checkpoints are added; no model values or financial helpers added.
"""
from pathlib import Path
import argparse,subprocess,tempfile,sys,os
ap=argparse.ArgumentParser();ap.add_argument('--model-root',required=True);a=ap.parse_args();root=Path(a.model_root).resolve();target=Path(tempfile.mkdtemp(prefix='land-fixtures-'))
for source,name,marker,stop in [
 ('test_urban_growth_journey.py','farm',"    Path('/tmp/townledger-growth-farm-review.json').write_text(fence_archive)","    print('FARM_FIXTURE_READY',flush=True)\n    browser.close()\n    raise SystemExit(0)"),
 ('test_brownfield_player_path.py','brownfield'," amenity_before=p.evaluate("," __import__('pathlib').Path('/tmp/land-brownfield-ready.json').write_text(p.evaluate('__townTest.save()'))\n print('BROWNFIELD_FIXTURE_READY',flush=True)\n b.close()\n raise SystemExit(0)\n")]:
 text=(root/'tests'/source).read_text()
 if text.count(marker)!=1:raise RuntimeError('Source prefix checkpoint changed: '+source)
 if name=='farm':text=text.replace(marker,marker+'\n'+stop)
 else:pos=text.index(marker);text=text[:pos]+stop+text[pos:]
 script=target/(name+'.py');script.write_text(text);env={**os.environ,'PYTHONPATH':str(root/'tests')};subprocess.run([sys.executable,'-u',str(script)],cwd=root,env=env,check=True)
print('Completed original test prefixes; archives in /tmp/townledger-growth-farm-review.json and /tmp/land-brownfield-ready.json')
