"""Sequential saved actual-trip actor option, warm-cache and disposal checks for both tiers."""
from pathlib import Path
import subprocess,json,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'docs/previews/webgl-tier-actor-resources-8';O.mkdir(parents=True,exist_ok=True)
files=[R/'assets/game.js',*sorted((R/'assets').glob('webgl*.js')),*sorted((R/'assets').glob('newfoundland*.js'))]
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
server=subprocess.Popen(['python','-m','http.server','8816','--bind','127.0.0.1'],cwd=R/'assets',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
rows=[]
def ready(p):p.wait_for_function('window.__webglTaste&&__webglTaste.sceneRevision===__cityVisualRevision()&&__webglTaste.samples.length>=3',timeout=90000)
try:
 with sync_playwright()as w:
  for tier in ['economy','reference']:
   b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});p.set_default_timeout(90000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   p.goto('http://127.0.0.1:8816/index.html?cityArt=webgl&cityQuality='+tier);p.locator('#newTown').click();p.locator('#pause').click();p.locator('#panelClose').click();assert p.evaluate('(s)=>__townTest.load(s)',(R/'docs/previews/webgl-actor-options-8/lod-fixture.json').read_text());ready(p);p.evaluate('__webglTaste.focus(4,26,3.5)');p.wait_for_function('__webglTaste.actorStats.actors>0',timeout=60000);p.locator('[data-panel=settings]').click();before=p.evaluate('__townTest.save()');p.locator('#panelClose').click();ready(p);row={'tier':tier,'options':[],'cache':[],'backend':p.evaluate('__webglTaste.renderer')}
   for option in ['traffic','effects']:
    initial=p.evaluate('__webglTaste.actorStats.actors');assert initial>0
    p.locator('[data-panel=settings]').click();p.locator('[data-option='+option+']').click();p.locator('#panelClose').click();p.wait_for_function('()=>{const v=__webglTaste,e=__cityVisualActors(v.lod,v.selected).filter(a=>(a.opacity??1)>0);return JSON.stringify(e.map(a=>a.id))===JSON.stringify(v.actorStats.poses.map(a=>a.id));}');off=p.evaluate('__webglTaste.actorStats.actors');assert option!="traffic" or off==0;assert p.evaluate('__townTest.save()')==before
    p.locator('[data-panel=settings]').click();p.locator('[data-option='+option+']').click();p.locator('#panelClose').click();p.wait_for_function('__webglTaste.actorStats.actors>0');assert p.evaluate('__townTest.save()')==before;row['options'].append({'option':option,'realActorsBefore':initial,'off':off,'restored':p.evaluate('__webglTaste.actorStats.actors')})
   for view in [(26,26,1.8),(45,26,.9),(80,80,.25),(26,26,1.8)]*2:
    previous=p.evaluate('__webglTaste.frameId');p.evaluate('(v)=>__webglTaste.focus(...v)',view);p.wait_for_function('(f)=>__webglTaste.frameId>f',arg=previous);ready(p);p.wait_for_timeout(300);row['cache'].append(p.evaluate('({lod:__webglTaste.lod,memory:__webglTaste.memory()})'))
   print(tier,json.dumps(row['cache']),flush=True);assert row['cache'][3]['memory']==row['cache'][7]['memory'],row['cache'];frame=p.evaluate('__webglTaste.frameId');p.wait_for_timeout(1000);assert p.evaluate('__webglTaste.frameId')==frame;assert p.evaluate('__townTest.save()')==before;assert p.evaluate('__cityVisualSave()');p.screenshot(path=str(O/(tier+'.png')))
   p.evaluate('window.__retiredRenderer=__webglTaste;__webglTaste.dispose()');row['disposed']=p.evaluate('__retiredRenderer.memory()');assert row['disposed']['geometries']==row['disposed']['textures']==0;assert p.locator('#view').is_visible();assert p.locator('#webglTaste').count()==p.locator('#webglMapOverlay').count()==0;assert p.evaluate('__townTest.save()')==before;assert not errors,errors;row.update({'errors':errors,'fullArchiveRNGInvariant':True,'pausedNoExtraDraws':True,'save':True});rows.append(row);b.close()
 assert hashes=={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
 (O/'checks.json').write_text(json.dumps({'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'sourceModules':hashes,'sequential':True,'rows':rows},indent=2));print('PASS Economy/Rich actual actors, paused traffic/effects, bounded caches, idle, save and zero GPU resources after disposal')
finally:server.terminate()
