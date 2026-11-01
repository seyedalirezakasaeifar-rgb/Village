from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_mobile_rendering import html
from playwright.sync_api import sync_playwright
source=(ROOT/'assets/game.js').read_text();api=(ROOT/'experiments/root-capacity-api.js').read_text();adapter=(ROOT/'experiments/automatic-day-admission.js').read_text()
probe=r'''
window.__profileAdmission=()=>{
 const a=__automaticDayAdmission;let on=false;
 function setup(enabled){if(on)a.disable();__townTest.reset('settlement',42);__townTest.step(30);__inactivePersonCodec.enable(true);if(enabled&&!a.enable())throw Error('Activation failed');on=enabled;}
 function sample(n){const out=[];for(let i=0;i<n;i++){const t=performance.now();tick();out.push(performance.now()-t);}return out;}
 setup(false);const baseline=sample(12);setup(true);const enabled=sample(12);
 const bound=a.visualReserve(),logical=JSON.parse(archiveLogicalPayload()),roads=G.tiles.map((v,i)=>v===1?i:-1).filter(i=>i>=0),numeric=-.0000010000000000000002;
 const actor={};for(const k of ['id','segment','fraction','speed','wait','age','from','to','person','shipment','rerouted','plannedStep'])actor[k]=numeric;
 Object.assign(actor,{path:roads,style:'pedestrian',color:'#ffffff',emergency:false,finished:false,reason:'x'.repeat(bound.reasonBytes)});
 const visual={vehicles:Array.from({length:80},()=>actor),clock:numeric,elapsed:numeric,gates:roads.map(i=>[i,numeric]),serial:numeric};
 const actualBytes=new Blob([JSON.stringify(visual)]).size;
 let actualNodes=0;const stack=[visual];while(stack.length){const v=stack.pop();actualNodes++;if(v&&typeof v==='object')for(const k of Object.keys(v))stack.push(v[k]);}
 if(actualBytes>bound.bytes||actualNodes>bound.nodes)throw Error('Worst visual projection exceeded bound');
 G.capacityProfilePadding='';const cert=a.certificate();G.capacityProfilePadding='x'.repeat(INACTIVE_CODEC_LIMITS.bytes-cert.bytes-cert.reserveBytes-200000);const certificateTime=performance.now();if(!a.retry().ok)throw Error('Near-limit state not admissible');const nearCertificateMs=performance.now()-certificateTime,near=sample(3);
 const before=archiveLogicalPayload();G.capacityProfilePadding+='x'.repeat(300000);const denied=archiveLogicalPayload(),t=performance.now();tick();const refusalMs=performance.now()-t;if(a.status().last.ok||archiveLogicalPayload()!==denied)throw Error('Near-limit refusal not atomic');
 return {baselineTickMs:baseline,enabledTickMs:enabled,nearLimitTickMs:near,nearCertificateMs,refusalMs,visualBound:{...bound,actualBytes,actualNodes},hostChromiumOnly:true,syntheticPadding:true,productionAssembled:false};
};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',api+'\n'+adapter+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__profileAdmission()');b.close()
out={'base_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'adapter_sha256':hashlib.sha256(adapter.encode()).hexdigest(),'result':r};target=ROOT/'reports/automatic-day-admission';target.mkdir(exist_ok=True);(target/'profile-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
