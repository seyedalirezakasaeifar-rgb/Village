from pathlib import Path
exec((Path(__file__).with_name('profile_automatic_day_admission.py')).read_text().split("probe=r'''")[0])
probe=r'''
window.__visualBoundTest=()=>{
 __townTest.reset('settlement',42);const oldTiles=G.tiles,oldTraffic=traffic;traffic=[];const rows=[];
 for(const count of [0,385,G.tiles.length]){
  G.tiles=G.tiles.map((_,i)=>i<count?1:0);const bound=__automaticDayAdmission.visualReserve(),n=-.0000010000000000000002,actor={};
  for(const k of ['id','segment','fraction','speed','wait','age','from','to','person','shipment','rerouted','plannedStep'])actor[k]=n;
  Object.assign(actor,{path:Array.from({length:count},(_,i)=>i),style:'pedestrian',color:'#ffffff',emergency:false,finished:false,reason:'x'.repeat(bound.reasonBytes)});
  const projected={vehicles:Array.from({length:80},()=>actor),clock:n,elapsed:n,gates:Array.from({length:count},(_,i)=>[i,n]),serial:n};
  const bytes=new Blob([JSON.stringify(projected)]).size;let nodes=0;const stack=[projected];while(stack.length){const v=stack.pop();nodes++;if(v&&typeof v==='object')for(const key of Object.keys(v))stack.push(v[key]);}
  if(bytes>bound.bytes||nodes>bound.nodes)throw Error('Visual projection escaped reserve');rows.push({roadCount:count,actualBytes:bytes,reservedBytes:bound.bytes,actualNodes:nodes,reservedNodes:bound.nodes,fullReserveExceedsSupportedNodeBudget:bound.nodes>INACTIVE_CODEC_LIMITS.nodes});
 }
 G.tiles=oldTiles;traffic=[{path:[0,1],wait:'growing-string'}];let invalid=false;try{__automaticDayAdmission.visualReserve();}catch(_){invalid=true;}traffic=oldTraffic;if(!invalid)throw Error('Unbounded string arithmetic accepted');return {rows,nonNumericGrowthRejected:true,syntheticSerializerUpperBounds:true,productionAssembled:false};
};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',api+'\n'+adapter+'\n'+probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();r=p.evaluate('__visualBoundTest()');b.close()
out={'base_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'adapter_sha256':hashlib.sha256(adapter.encode()).hexdigest(),'result':r};target=ROOT/'reports/automatic-day-admission';target.mkdir(exist_ok=True);(target/'visual-bound-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
