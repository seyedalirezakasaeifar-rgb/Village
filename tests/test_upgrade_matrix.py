"""Generate old engine exports in memory; publish hashes/counts only."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import subprocess,json,hashlib
source=(ROOT/'assets/game.js').read_text();rows=[]
probe='''window.__upgrade={fault:()=>{const raw=archivePayload(),rng=rngState,original=ensureScenarioProgramme;try{ensureScenarioProgramme=()=>{throw Error('Injected import interruption')};if(hydrateSave(raw))throw Error('Interrupted import accepted')}finally{ensureScenarioProgramme=original}if(archivePayload()!==raw||rngState!==rng)throw Error('Interrupted import lost live state');return true;},found:()=>{chosenScenario='settlement';seed(42);paused=true;return typeof archivePayload==='function'?archivePayload():JSON.stringify(G)},pause:()=>{paused=true;hostSuspended=true},large:()=>{while(G.people.length<8000)G.people.push({id:G.people.length,name:'Historical synthetic resident',age:90,hh:0,job:-1,health:0,skill:.5,life:0,last:[],deceased:true});return archivePayload()}};'''
def injected(s):
 pos=s.rfind('})();');return s[:pos]+probe+s[pos:]
def total(g):return sum(g.get(k,0) for k in ['treasury','region'])+sum(a.get('cash',0) for k in ['households','firms','banks','investors'] for a in g.get(k,[]))+g.get('metro',{}).get('cash',0)+sum(p.get('serviceEscrow',0)+p.get('urbanEscrow',0) for p in g.get('projects',[]))
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=injected(source));current=p.evaluate('__upgrade.found()')
 cases=[('authentic-v60-distressed',(ROOT/'tests/fixtures/v60-distressed-town.json').read_text()),('authentic-corporate-liquidity',(ROOT/'tests/fixtures/corporate-liquidity-trap.json').read_text()),('current-fresh',current),('current-8000-history',p.evaluate('__upgrade.large()'))]
 engines=[('supplied5.6',None,'reference/v5.6/assets'),('supplied6.0',None,'reference/v6.0/assets'),('7.0.0','1c7fd61','assets'),('7.1.1','ac76281','assets'),('8-schema7','29174c1','assets'),('8-schema8','441a713','assets')]
 for label,ref,path in engines:
  try:
   oldsource=subprocess.check_output(['git','show',ref+':'+path+'/game.js'],cwd=ROOT,text=True) if ref else (ROOT/path/'game.js').read_text();oldhtml=subprocess.check_output(['git','show',ref+':'+path+'/index.html'],cwd=ROOT,text=True) if ref else (ROOT/path/'index.html').read_text();q=b.new_page();q.set_content(oldhtml.replace('<script src="game.js"></script>',''));q.add_script_tag(content=injected(oldsource));raw=q.evaluate('__upgrade.found()');q.close();cases.append((label,raw))
  except Exception as e:rows.append({'case':label,'status':'generation-error','error':str(e)[:800]})
 for label,raw in cases:
  row={'case':label,'archive_sha256':hashlib.sha256(raw.encode()).hexdigest(),'utf8Bytes':len(raw.encode())}
  try:
   old=json.loads(raw);row.update(schema=old.get('schema'),release=old.get('release'),grid=len(old['tiles'])**.5,people=len(old['people']));live=p.evaluate('__townTest.save()');accepted=p.evaluate('r=>__townArchive.restore(r)',raw);row['accepted']=accepted
   if not accepted:assert p.evaluate('__townTest.save()')==live;row['atomicRejection']=True
   else:
    new=json.loads(p.evaluate('__townTest.save()'));assert abs(total(old)-total(new))<.01;assert [(a['id'],a['name'],a['hh'],a['age']) for a in old['people']]==[(a['id'],a['name'],a['hh'],a['age']) for a in new['people']];assert [(a['id'],a['kind'],a['owner'],a['x'],a['y']) for a in old['buildings']]==[(a['id'],a['kind'],a['owner'],a['x'],a['y']) for a in new['buildings']];assert p.evaluate('__townTest.validate().ok');row['cashDrift']=total(new)-total(old);row['identitiesAndPropertyPreserved']=True
   row['status']='pass'
  except Exception as e:row.update(status='failure',error=str(e)[:800])
  rows.append(row)
 p.evaluate('r=>__townTest.load(r)',current)
 for mutation in ['g.schema=999','g.schema=-1','g.people[0].hh=999999']:
  result=p.evaluate('code=>{const before=__townTest.save(),g=JSON.parse(before);new Function("g",code)(g);return {rejected:!__townArchive.restore(JSON.stringify(g)),unchanged:__townTest.save()===before}}',mutation);assert result=={'rejected':True,'unchanged':True};rows.append({'case':mutation,'status':'pass',**result})
 assert p.evaluate('__townArchive.restore("{truncated")') is False
 future=p.evaluate('()=>{const g=JSON.parse(__townTest.save());g.schema=999;__townArchive.restore(JSON.stringify(g));return document.querySelector("#toast").textContent}');assert 'newer save schema 999' in future and 'unchanged' in future
 assert p.evaluate('__upgrade.fault()');rows.append({'case':'interrupted adoption rollback','status':'pass','archiveAndRNGUnchanged':True});exported=json.loads(p.evaluate('__townArchive.export()'));assert exported['release'] and exported['schema'];b.close()
out=ROOT/'reports/upgrade-matrix';out.mkdir(exist_ok=True);result={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'rows':rows,'currentExportIdentity':{k:exported.get(k) for k in ['version','schema','release','gridSize']},'payloadsRetained':False};(out/'matrix.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert not any(r['status'] in ['failure','generation-error'] for r in rows)
