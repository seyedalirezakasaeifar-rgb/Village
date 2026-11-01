"""Full-model/RNG parity for transit mutations with one exact derived correction."""
from pathlib import Path
import sys,json,ast,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
base=subprocess.check_output(['git','show','01eeda3:assets/game.js'],cwd=ROOT,text=True);fixed=(ROOT/'assets/game.js').read_text();tree=ast.parse((ROOT/'tests/test_transit_network.py').read_text());probe=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
extra=r'''
window.__freshnessParity=()=>{__townTest.reset('settlement',42);const setup=__transitProbe.setup();if(!setup.route)throw Error('No actual route');const id=setup.route.id,rows=[];const capture=stage=>rows.push({stage,archive:JSON.parse(archivePayload()),rng:rngState,total:totalMoney(),expected:G.treasury+(G.publicReserve||0)-G.debt});capture('build');if(!setTransitLevel(id,1))throw Error('Resize refused');capture('resize');if(!deleteTransitRoute(id))throw Error('Retire refused');capture('retire');if(!removeTransitFacility(setup.depot.id))throw Error('Remove site refused');capture('remove-site');return rows;};
'''
results=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for code in [base,fixed]:
  p=b.new_page();p.set_content(html);p.evaluate('window.requestAnimationFrame=()=>0');p.add_script_tag(content=code.replace('// SOURCE: 99-instrumentation.js',probe+'\n'+extra+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();results.append(p.evaluate('__freshnessParity()'));p.close()
 b.close()
rows=[]
for old,new in zip(*results):
 assert old['stage']==new['stage'] and old['rng']==new['rng'] and old['total']==new['total'] and old['expected']==new['expected'];assert new['archive']['stats']['townBalance']==new['expected']
 previous=old['archive']['stats']['townBalance'];old['archive']['stats']['townBalance']=old['expected'];assert old['archive']==new['archive'],'Other model field changed at '+new['stage'];rows.append({'stage':new['stage'],'entireModelEqualAfterExactDerivedFormulaCorrection':True,'rngEqual':True,'totalMoneyEqual':True,'baselineBalanceWasStale':previous!=old['expected'],'fixedBalanceMatchesAccounts':True})
out={'baseSourceSha256':hashlib.sha256(base.encode()).hexdigest(),'fixedSourceSha256':hashlib.sha256(fixed.encode()).hexdigest(),'setup':'Existing transit test conserves region/treasury cash and reassigns existing residents; no new people or money','actualUiClaim':False,'excludedFields':[],'assertedDerivedFormula':'stats.townBalance = treasury + publicReserve - debt','rows':rows};(ROOT/'reports/player-freshness-model-parity.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
