from pathlib import Path
import sys,json,hashlib,subprocess,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
PAID='455a12f1d01943bc9a8846b437146612e5f9bfd2'
def published(path):return subprocess.check_output(['git','show',PAID+':'+path],cwd=ROOT,text=True)
source=(ROOT/'assets/game.js').read_text()
for name in ['70-interaction.js','80-civic.js','98-project-opportunities.js']:
 source=re.sub(r'// SOURCE: '+re.escape(name)+r'\n.*?(?=// SOURCE: |\Z)',lambda m:'// SOURCE: '+name+'\n'+published('src/'+name)+'\n',source,flags=re.S)
bootstrap=(ROOT/'experiments/root-capacity-api.js').read_text()+'\n'+(ROOT/'experiments/automatic-day-admission.js').read_text()+'\n'+published('experiments/paid-command-root.js')+"\nsave=()=>Promise.resolve(true);__automaticDayAdmission.install();__installPaidCommandLayer(__automaticDayAdmission);\n"
probe=r'''
window.__composed=async()=>{
 const a=__automaticDayAdmission;if(__rootAdmission.shared!==a.shared)throw Error('Multiple controllers');
 async function sequence(enabled){a.disable();__townTest.reset('settlement',42);__inactivePersonCodec.enable(true);if(enabled&&!a.enable())throw Error('Initial capacity refused');__townTest.step(30);
  let site;for(let y=2;y<T-2&&!site;y++)for(let x=2;x<T-2;x++)if(canPlace(x,y,true,'grocer')){site={x,y};break;}
  construct('grocer',site.x,site.y);const e=COUNCIL_EVENTS[0];showCustomEvent(e.type,e.title,e.text,e.choices);$('eventChoices').querySelector('button').click();await Promise.resolve();await Promise.resolve();
  if(pendingEvent)throw Error('Actual paid council choice failed '+JSON.stringify(__rootAdmission.status()));__townTest.step(30);return {archive:archiveLogicalPayload(),rng:rngState,money:totalMoney()};
 }
 const oracle=await sequence(false),guarded=await sequence(true);if(oracle.archive!==guarded.archive||oracle.rng!==guarded.rng||oracle.money!==guarded.money)throw Error('Composed day/paid sequence diverged');
 const wire=archivePayload();a.disable();if(!hydrateSave(wire))throw Error('Committed composed archive cannot self-import');
 return {oneSharedController:true,realConstructionAndCouncilChoice:true,dayCount:60,exactArchiveRngMoney:true,committedArchiveSelfImports:true,productionAssembled:false};
};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',bootstrap+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__composed()');b.close()
out={'composed_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'automatic_adapter_sha256':hashlib.sha256((ROOT/'experiments/automatic-day-admission.js').read_bytes()).hexdigest(),'paid_dependency':PAID,'result':r};target=ROOT/'reports/automatic-day-admission';target.mkdir(exist_ok=True);(target/'composed-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
