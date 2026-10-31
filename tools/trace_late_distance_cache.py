"""Replay the approved generated late fixture and count real distance-cache work.
No route/model replacement: wrappers observe queries, hits/misses and invalidations.
"""
from pathlib import Path
import gzip,hashlib,json,os
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'tests/fixtures/generated-late-31987fc';manifest=json.loads((folder/'manifest.json').read_text());name=os.environ.get('LATE_FIXTURE','terminal');meta=next(v for v in manifest['fixtures'] if v['name']==name);packed=(folder/meta['file']).read_bytes();assert hashlib.sha256(packed).hexdigest()==meta['compressed_sha256'];raw=gzip.decompress(packed);assert hashlib.sha256(raw).hexdigest()==meta['archive_sha256'];town=json.loads(raw);assert town['day']==meta['day'] and town['gridSize']==128 and town['autoBuild'] and town['policy']['privateServices']==1
checkpoint=Path('/tmp/townledger-generated-'+name+'-31987fc.json');checkpoint.write_bytes(raw)
os.environ.setdefault('LATE_CHECKPOINT',str(checkpoint));os.environ.setdefault('LATE_SOURCE_REF',manifest['source_commit']);os.environ.setdefault('LATE_LABEL',name+'-cache');os.environ.setdefault('LATE_SECONDS','24')
CACHE_PROBE=r'''
let distanceScope='',distanceQuery=null;
const distanceEvidence={queries:0,treeCalls:0,hits:0,misses:0,evictions:0,invalidations:[],newGraphs:[],scopes:{},querySamples:{}};
const distanceNetIds=new WeakMap();let distanceNextNet=0;
function distanceScopeEvidence(){const key=distanceScope||'(other)';if(!distanceEvidence.scopes[key])distanceEvidence.scopes[key]={queries:0,treeCalls:0,hits:0,misses:0,evictions:0,missMs:0,hitMs:0,maxMissMs:0,anchors:new Set(),graphIds:new Set()};return distanceEvidence.scopes[key];}
for(const name of ['dailyEconomy','transitOperatingDay','workerCanCommute','exportRoutes','privateServiceDay','urbanEvolutionDay','assignJobs','trade','seekPrivateServiceInvestment']){const original=eval(name),wrapped=function(...args){if(!lateOn)return original.apply(this,args);const old=distanceScope;distanceScope=old?old+'/'+name:name;try{return original.apply(this,args)}finally{distanceScope=old}};eval(name+'=wrapped');}
const distanceBase=roadDistance;roadDistance=function(a,b){if(!lateOn)return distanceBase(a,b);const old=distanceQuery,q={a,b,day:G.day,scope:distanceScope||'(other)'};distanceQuery=q;distanceEvidence.queries++;distanceScopeEvidence().queries++;try{const value=distanceBase(a,b);q.result=Number.isFinite(value)?value:String(value);const samples=distanceEvidence.querySamples[q.scope]||(distanceEvidence.querySamples[q.scope]=[]);if(samples.length<16)samples.push(q);return value}finally{distanceQuery=old}};
const distanceTreeBase=roadDistancesFrom;roadDistancesFrom=function(start,net=graph()){
 if(!lateOn)return distanceTreeBase(start,net);const hit=!!net.distanceTrees?.has(start),full=!hit&&(net.distanceTrees?.size||0)>=32,scope=distanceScopeEvidence();
 let id=distanceNetIds.get(net);if(!id){id=++distanceNextNet;distanceNetIds.set(net,id);distanceEvidence.newGraphs.push({id,day:G.day,roadsVersion,nodes:net.neighbors.size,buildings:G.buildings.length,treesBefore:net.distanceTrees?.size||0});}
 scope.graphIds.add(id);scope.anchors.add(start);scope.treeCalls++;distanceEvidence.treeCalls++;if(hit){scope.hits++;distanceEvidence.hits++}else{scope.misses++;distanceEvidence.misses++;if(full){scope.evictions++;distanceEvidence.evictions++}}
 if(distanceQuery){distanceQuery.anchor=start;distanceQuery.hit=hit;distanceQuery.graph=id;}
 const t=performance.now();try{return distanceTreeBase(start,net)}finally{const ms=performance.now()-t;if(hit)scope.hitMs+=ms;else{scope.missMs+=ms;scope.maxMissMs=Math.max(scope.maxMissMs,ms);}}
};
const distanceInvalidateBase=invalidateRoads;invalidateRoads=function(...args){if(lateOn)distanceEvidence.invalidations.push({day:G.day,scope:distanceScope||'(other)',roadsVersion,resetTraffic:args[0]!==false});return distanceInvalidateBase(...args)};
const distanceEndBase=__late.end;__late.end=function(){const value=distanceEndBase();const scopes={};for(const [name,s] of Object.entries(distanceEvidence.scopes))scopes[name]={...s,distinctAnchors:s.anchors.size,anchorIds:[...s.anchors].sort((a,b)=>a-b),graphIds:[...s.graphIds]};return {...value,distanceCache:{...distanceEvidence,scopes,finalTrees:graph().distanceTrees?.size||0,graphCount:distanceNextNet,configuredTreeLimit:32}}};
'''
runner=ROOT/'tools/profile_late_session_8.py';code=runner.read_text();assert code.count('def stats(a):')==1;code=code.replace('def stats(a):','probe += CACHE_PROBE\ndef stats(a):',1);needle="raw=p.evaluate('__late.end()');";assert code.count(needle)==1;code=code.replace(needle,needle+"result['distanceCache']=raw['distanceCache'];result['cacheInstrumentationSha256']=hashlib.sha256(CACHE_PROBE.encode()).hexdigest();",1);exec(compile(code,str(runner),'exec'),{'__name__':'__main__','__file__':str(runner),'CACHE_PROBE':CACHE_PROBE})
