"""Header/save backport: complete archive/RNG/accounting and restore replay."""
from pathlib import Path
import sys,subprocess,gzip,json,hashlib
sys.path.insert(0,'tests')
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];base=subprocess.check_output(['git','show','87811c5:assets/game.js'],text=True);fixed=(R/'assets/game.js').read_text();dense=gzip.decompress(subprocess.check_output(['git','show','833afee:tests/fixtures/generated-late-31987fc/terminal.json.gz'])).decode();out=R/'reports/sync-header-save';out.mkdir(exist_ok=True,parents=True)
hook=r'''window.syncParity={setup:spec=>{chosenScenario=spec.scenario||'settlement';seed(spec.seed||42);paused=true;if(spec.archive&&!hydrateSave(spec.archive))throw Error('Fixture refused');pendingEvent=null;return {archive:archivePayload(),money:totalMoney(),population:G.stats.population};},step:n=>{__townTest.step(n);return {archive:archivePayload(),valid:validateTown(),money:totalMoney(),goods:Math.max(...goodsBalance().map(x=>Math.abs(x.error))),rng:rngState};},load:a=>{if(!hydrateSave(a))throw Error('Replay load refused');pendingEvent=null;}};'''
rows=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pages=[]
 for code in [base,fixed]:
  p=b.new_page();p.set_content(html);p.evaluate('window.requestAnimationFrame=()=>0');p.add_script_tag(content=code.replace('// SOURCE: 99-instrumentation.js',hook+'// SOURCE: 99-instrumentation.js'));pages.append(p)
 for fixture in [{'seed':42},{'seed':91,'scenario':'regional'},{'seed':909,'scenario':'regional'},{'archive':dense}]:
  initial=[p.evaluate('s=>syncParity.setup(s)',fixture) for p in pages];assert json.loads(initial[0]['archive'])==json.loads(initial[1]['archive'])
  final=[p.evaluate('syncParity.step(180)') for p in pages];a,bstate=[json.loads(v['archive']) for v in final];assert a==bstate,'Complete archive mismatch';assert final[0]['rng']==final[1]['rng']
  for start,end in zip(initial,final):assert end['valid']['ok'] and abs(end['money']-start['money'])<.001 and end['goods']<.001
  pages[1].evaluate('a=>syncParity.load(a)',initial[1]['archive']);replay=pages[1].evaluate('syncParity.step(180)');assert json.loads(replay['archive'])==bstate,'Replay mismatch'
  row={'fixture':'retained778' if 'archive' in fixture else fixture,'initialPopulation':initial[0]['population'],'days':180,'fullArchiveRngExact':True,'candidateReplayExact':True,'excludedFields':[],'cashDrift':final[1]['money']-initial[1]['money'],'goodsError':final[1]['goods'],'terminalModelSHA256':hashlib.sha256(json.dumps(bstate,sort_keys=True,separators=(',',':')).encode()).hexdigest()};rows.append(row);print('PASS',row,flush=True)
 b.close()
(out/'replay.json').write_text(json.dumps({'baseSHA256':hashlib.sha256(base.encode()).hexdigest(),'fixedSHA256':hashlib.sha256(fixed.encode()).hexdigest(),'rows':rows},indent=2)+'\n')
