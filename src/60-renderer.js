function headerText(id,value){const el=$(id),text=String(value);if(el&&el.textContent!==text)el.textContent=text;}
function headerMoney(value){return Math.abs(value)>=1000000?(value<0?'−':'')+'$'+(Math.abs(value)/1000000).toLocaleString('en-CA',{maximumFractionDigits:1})+'m':money(value);}
let liveStatusTown=null,liveStatusDay=-1,liveStatusPaused=null,liveStatusKey='';
function updateLiveStatus(){
 if(!$('liveEconomy'))return;
 const care=G.serviceProvision?.health?.coverage,school=G.serviceProvision?.school?.coverage;
 const key=[G.day,care,school,G.stats.businesses,G.stats.population,G.stats.employment,G.stats.hardship,G.stats.marketConfidence,G.market?.foodDisconnected,G.market?.unmetFood,G.journal?.length,G.finance?.creditIssued].join('|');
 const due=liveStatusTown!==G||liveStatusPaused!==paused||G.day<liveStatusDay||G.day-liveStatusDay>=5||((paused||G.day<5)&&key!==liveStatusKey);
 if(!due)return;
 const m=marketSignal();headerText('marketHeadline',m.title);headerText('marketDetail',Number.isFinite(care)&&Number.isFinite(school)?Math.round(care*100)+'% care · '+Math.round(school*100)+'% school · '+m.m.open+' firms':m.m.open+' firms · '+m.m.projects+' projects · '+G.stats.hardship+'% hardship');
 liveStatusTown=G;liveStatusDay=G.day;liveStatusPaused=paused;liveStatusKey=key;
}
function updateHeader(){
 if(!G)return;headerText('pop',fmt(G.stats.population));headerText('funds',headerMoney(G.treasury));if($('funds').title!==money(G.treasury))$('funds').title=money(G.treasury);headerText('jobs',G.stats.employment+'%');headerText('safety',G.stats.safety+'/100');headerText('approval',Math.round(G.council.approval)+'%');headerText('date','YEAR '+G.year+' · MONTH '+G.month+' · DAY '+G.day);
 headerText('season',(seasonsEnabled()?['SPRING IN THE VALE','SUMMER IN THE VALE','AUTUMN IN THE VALE','WINTER IN THE VALE'][Math.floor((G.month-1)/3)]:'THE WORKING CITY')+(weatherEnabled()&&G.weather&&G.weather!=='clear'?' · '+G.weather.toUpperCase():''));
 const pause=$('pause');if(pause.dataset.iconState!==String(paused)){pause.innerHTML=paused?'<svg width=18 height=18 viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 4L21 12L7 20Z"/></svg>':'<svg width=18 height=18 viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6 4H10V20H6ZM14 4H18V20H14Z"/></svg>';pause.dataset.iconState=String(paused);}const label=paused?'Resume simulation':'Pause simulation',title=paused?'Resume':'Pause';if(pause.getAttribute('aria-label')!==label)pause.setAttribute('aria-label',label);if(pause.title!==title)pause.title=title;
 updateLiveStatus();
 headerText('speed',speed+'×');headerText('effectiveSpeed',!paused&&speed>=8?'Actual '+perfStats.effective.toFixed(0)+'×':'');const range=$('speedRange'),value=String(SPEED_PRESETS.indexOf(speed)>=0?SPEED_PRESETS.indexOf(speed):0);if(range&&range.value!==value)range.value=value;$('pauseBanner').style.display=paused?'block':'none';updateObjectiveMini();
}
// ----- Town map renderer. Geometry is cached; only vehicles need a dynamic redraw.
function iso(x,y){return [(x-y)*TW/2+RW/2,(x+y)*TH/2+32]}
function diamond(g,x,y,fill,stroke){let p=iso(x,y);g.beginPath();g.moveTo(p[0],p[1]);g.lineTo(p[0]+TW/2,p[1]+TH/2);g.lineTo(p[0],p[1]+TH);g.lineTo(p[0]-TW/2,p[1]+TH/2);g.closePath();g.fillStyle=fill;g.fill();g.strokeStyle=fill;g.lineWidth=.7;g.stroke();if(stroke){g.strokeStyle=stroke;g.lineWidth=.6;g.stroke()}}
let roadNetwork=null,roadsVersion=0,roadVersionBuilt=-1,roadGraphOwner=null,roadBuildingVersion=-1,traffic=[],trafficClock=0,frameClock=0,renderSprites=[],spritesVersion=-1,vehicleSerial=0;
const roadOffsets=[[-1,0],[1,0],[0,-1],[0,1]];
function ensureRoadWear(){if(!G.roadWear||!Array.isArray(G.roadWear)||G.roadWear.length!==T*T){G.roadWear=new Array(T*T).fill(100)}}
function maintainRoads(){
 ensureRoadWear();
 const net=graph(),privateSet=new Set(G.privateRoads||[]);
 const publicCount=Math.max(1,charterRoadCount());
 const publicBudget=clamp(G.policy.roadBudget,0,250)*(G.actualServiceFunding?.roads??1);
 const publicRepair=publicBudget/publicCount*.23;
 // Private lanes are maintained by locally subscribed user charges, not the
 // municipal road grant. If shops cannot pay, pavement gradually deteriorates.
 const commercial=G.firms.filter(f=>!f.closed&&f.cash>2&&net.portals.has(f.building));
 let privateFees=0;
 if(privateSet.size&&commercial.length){
  const due=Math.min(.22,privateSet.size*.13/commercial.length);
  for(const f of commercial){const paid=Math.min(f.cash,due);f.cash-=paid;f.expenses+=paid;G.region+=paid;privateFees+=paid}
 }
 if(G.development)G.development.privateRoadTolls=(G.development.privateRoadTolls||0)+privateFees;
 const privateRepair=privateFees/Math.max(1,privateSet.size)*.85;
 let total=0,n=0;
 for(const id of net.neighbors.keys()){
  const old=G.roadWear[id];
  const repair=privateSet.has(id)?privateRepair:charterOwns(id%T,id/T|0)?publicRepair:.045;
  G.roadWear[id]=clamp(old-.045-(G.weather==='storm'?.065:0)+repair,25,100);
  total+=G.roadWear[id];n++;
 }
 G.stats.roadCondition=Math.round(total/Math.max(1,n));
 // Keep the scalar quality cache current without rebuilding network routes.
 if(G.roadMetrics)G.roadMetrics.quality=G.stats.roadCondition;
 // Road wear is an economic measure, not a reason to repaint the terrain.
}
const roadId=(x,y)=>y*T+x;
function invalidateRoads(resetTraffic=true){roadsVersion++;roadNetwork=null;if(resetTraffic){traffic.length=0;trafficClock=0;intersectionGates.clear()}if(G)G.roadMetrics=null;dirty=true;}
function flushRoadBatch(){if(!roadBatchDirty)return;roadBatchDirty=false;invalidateRoads();staticDirty=true;if(G){recompute();updateHeader();save()}}
function graph(){
 if(roadNetwork&&roadVersionBuilt===roadsVersion&&roadGraphOwner===G&&roadBuildingVersion===G.buildings.length)return roadNetwork;
 const neighbors=new Map(),parts=new Int32Array(T*T).fill(-1),portals=new Map(),connected=[];
 for(let i=0;i<G.tiles.length;i++)if(G.tiles[i]===1){
  const x=i%T,y=i/T|0,ns=[];
  for(const [dx,dy] of roadOffsets){const xx=x+dx,yy=y+dy;if(xx>=0&&xx<T&&yy>=0&&yy<T&&G.tiles[roadId(xx,yy)]===1)ns.push(roadId(xx,yy))}
  neighbors.set(i,ns);
 }
 let part=0,maxSize=0,mainPart=-1;
 for(const id of neighbors.keys())if(parts[id]===-1){
  const q=[id];parts[id]=part;for(let k=0;k<q.length;k++)for(const n of neighbors.get(q[k]))if(parts[n]===-1){parts[n]=part;q.push(n)}
  if(q.length>maxSize){maxSize=q.length;mainPart=part}part++;
 }
 const anchor=G.buildings.find(b=>b.kind==='townhall');
 if(anchor){for(const [dx,dy] of roadOffsets){let x=anchor.x+dx,y=anchor.y+dy;if(x>=0&&x<T&&y>=0&&y<T&&parts[roadId(x,y)]>=0){mainPart=parts[roadId(x,y)];break}}}
 for(const b of G.buildings){
  const choices=[];for(const id of footprintOf(b)){const xx=id%T,yy=id/T|0;for(const [dx,dy] of roadOffsets){const ax=xx+dx,ay=yy+dy;if(ax>=0&&ax<T&&ay>=0&&ay<T&&G.tiles[roadId(ax,ay)]===1)choices.push(roadId(ax,ay))}}
  if(choices.length){let entry=choices.find(id=>parts[id]===mainPart)??choices[0];portals.set(b.id,entry);if(parts[entry]===mainPart)connected.push(b)}
 }
 roadNetwork={neighbors,parts,portals,connected,mainPart,partsCount:part,maxSize};roadVersionBuilt=roadsVersion;roadGraphOwner=G;roadBuildingVersion=G.buildings.length;return roadNetwork;
}
function routeBetween(a,b){
 const net=graph(),start=typeof a==='number'?a:net.portals.get(a?.id),finish=typeof b==='number'?b:net.portals.get(b?.id);
 if(start==null||finish==null||net.parts[start]!==net.parts[finish])return [];
 if(start===finish)return [start];
 net.routeTrees=net.routeTrees||new Map();let prev=net.routeTrees.get(start);
 if(!prev){prev=new Int32Array(T*T).fill(-1);const queue=[start];prev[start]=start;
  for(let i=0;i<queue.length;i++)for(const n of net.neighbors.get(queue[i])||[]){if(prev[n]!==-1)continue;prev[n]=queue[i];queue.push(n);}
  // 96 route trees at the bounded 128² grid use at most 6 MiB.
  if(net.routeTrees.size>=96)net.routeTrees.delete(net.routeTrees.keys().next().value);net.routeTrees.set(start,prev);
 }
 if(prev[finish]===-1)return [];const path=[finish];let at=finish;
 while(at!==start){at=prev[at];path.push(at);}return path.reverse();
}

function roadMetrics(){
 const net=graph(),firms=G.firms.filter(f=>!f.closed),reachable=firms.filter(f=>{let node=net.portals.get(f.building);return node!=null&&net.parts[node]===net.mainPart}).length;
 const eligible=G.households.filter(h=>{let node=net.portals.get(h.home);return node!=null&&net.parts[node]===net.mainPart}).length;
 let routes=0,length=0;for(let i=0;i<Math.min(10,net.connected.length-1);i++){
  const a=net.connected[i],b=net.connected[(i*7+19)%net.connected.length];if(a===b)continue;let path=routeBetween(a,b);if(path.length>1){routes++;length+=path.length-1}
 }
 return {connectedFirms:reachable,totalFirms:firms.length,connectedHomes:eligible,totalHomes:G.households.length,roadTiles:net.neighbors.size,roadClusters:net.partsCount,averageJourney:routes?Math.round(length/routes):0,quality:Math.round(G.stats.roadCondition??75)};
}
function roadCenter(id){const pos=iso(id%T,id/T|0);return [pos[0],pos[1]+TH/2]}
// Distance-only BFS rows use road-node indices rather than the entire atlas.
// Keep at most 4 MiB of rows, plus the existing 32 tile-indexed compatibility
// rows. This lets the working set grow with actual road density, not map area.
const ROAD_DISTANCE_ROW_BYTES=4*1024*1024;
function roadDistanceRows(net){
 if(net.distanceRows)return net.distanceRows;
 const nodes=[...net.neighbors.keys()],index=new Int32Array(G.tiles.length).fill(-1);
 nodes.forEach((id,i)=>index[id]=i);
 const adjacency=nodes.map(id=>(net.neighbors.get(id)||[]).map(next=>index[next]));
 return net.distanceRows={nodes,index,adjacency,queue:new Int32Array(nodes.length),rows:new Map(),bytes:0,stats:{queries:0,hits:0,builds:0,evictions:0,maxBytes:0}};
}
function roadDistanceRow(start,net){
 const cache=roadDistanceRows(net),stats=cache.stats;stats.queries++;
 let row=cache.rows.get(start);
 if(row){stats.hits++;cache.rows.delete(start);cache.rows.set(start,row);return row;}
 const DistanceArray=cache.nodes.length<32768?Int16Array:Int32Array;
 row=new DistanceArray(cache.nodes.length).fill(-1);const origin=cache.index[start];
 // Invalid/non-road roots preserve an all-minus-one result without retaining keys.
 if(origin==null||origin<0)return row;
 if(origin>=0){let head=0,tail=1;cache.queue[0]=origin;row[origin]=0;
  while(head<tail){const at=cache.queue[head++],distance=row[at]+1;for(const next of cache.adjacency[at])if(row[next]===-1){row[next]=distance;cache.queue[tail++]=next;}}
 }
 stats.builds++;
 while(cache.rows.size&&cache.bytes+row.byteLength>ROAD_DISTANCE_ROW_BYTES){const oldest=cache.rows.keys().next().value;cache.bytes-=cache.rows.get(oldest).byteLength;cache.rows.delete(oldest);stats.evictions++;}
 if(row.byteLength<=ROAD_DISTANCE_ROW_BYTES){cache.rows.set(start,row);cache.bytes+=row.byteLength;stats.maxBytes=Math.max(stats.maxBytes,cache.bytes);}
 return row;
}
function roadDistancesFrom(start,net=graph()){
 if(!net.distanceTrees)net.distanceTrees=new Map();let distance=net.distanceTrees.get(start);
 if(distance){net.distanceTrees.delete(start);net.distanceTrees.set(start,distance);return distance;}
 const cache=roadDistanceRows(net),row=roadDistanceRow(start,net),DistanceArray=cache.nodes.length<32768?Int16Array:Int32Array;
 distance=new DistanceArray(G.tiles.length).fill(-1);for(let i=0;i<cache.nodes.length;i++)distance[cache.nodes[i]]=row[i];
 if(net.distanceTrees.size>=32)net.distanceTrees.delete(net.distanceTrees.keys().next().value);net.distanceTrees.set(start,distance);return distance;
}
function roadDistance(a,b){
 if(a==null||b==null)return Infinity;if(a===b)return 0;
 const net=graph();if(net.parts[a]!==net.parts[b])return Infinity;
 // Preserve the legacy non-road sentinel; normal consumers use graph portals.
 if(!net.neighbors.has(a)||!net.neighbors.has(b))return -1;
 const cache=roadDistanceRows(net),cachedA=cache.rows.has(a),cachedB=cache.rows.has(b),anchor=cachedA?a:cachedB?b:net.distanceLastA===a?a:b;
 net.distanceLastA=a;return roadDistanceRow(anchor,net)[cache.index[anchor===a?b:a]];
}
function beginVehicle(source=null,target=null,emergency=false){
 const net=graph();if(net.connected.length<2)return null;
 let from=source||visualPick(net.connected.filter(b=>b.firm>=0&&G.firms[b.firm]&&!G.firms[b.firm].closed));
 if(!from)return null;
 const src=net.portals.get(from.id);if(src==null)return null;if(traffic.some(v=>v.path[v.segment]===src&&v.fraction<.8))return null;
 let destinations=net.connected.filter(b=>b.id!==from.id&&net.parts[net.portals.get(b.id)]===net.parts[src]);
 if(!destinations.length)return null;
 // Goods vehicles favour another business, while smaller cars visit homes and civic premises.
 const commercial=destinations.filter(b=>b.firm>=0),residential=destinations.filter(b=>b.kind==='home');
 let pool=visualRandom()<.58?commercial:residential;
 let to=target||visualPick(pool.length?pool:destinations);
 if(target&&(!net.portals.has(target.id)||net.parts[net.portals.get(target.id)]!==net.parts[src]))return null;
 if(!to||net.parts[net.portals.get(to.id)]!==net.parts[src])to=visualPick(destinations);
 let path=routeBetween(from,to);if(path.length<2)return null;
 const n=traffic.length,color=emergency?'#c24c3e':['#b98051','#e4c58b','#536e7c','#7b8b71','#9b5f54','#c6bd9e'][((from.id*7+n*3)%6)];
 let style=emergency?'emergency':from.kind==='farm'?'tractor':visualRandom()<.28?'pedestrian':visualRandom()<.48?'truck':'car';let v={id:++vehicleSerial,path,segment:0,fraction:0,speed:emergency?4.3:style==='pedestrian'?.53:style==='tractor'?.68:1+visualRandom()*.4,style,color,emergency,wait:0,age:0,from:from.id,to:to.id};traffic.push(v);return v;
}
function roadServiceDistance(site,station){if(!site||!station)return Infinity;const net=graph(),a=net.portals.get(site.id),b=net.portals.get(station.id);if(a==null||b==null||net.parts[a]!==net.parts[b])return Infinity;return roadDistance(a,b);}
function closestRoadBuilding(x,y,kind){const net=graph(),site=buildingAt(x,y);if(!site)return null;let best=null,d=Infinity;for(const b of net.connected){if(kind&&b.kind!==kind)continue;if(b.firm>=0&&G.firms[b.firm]?.privateService&&(G.firms[b.firm].closed||!(G.firms[b.firm].serviceCapacity>0)))continue;const distance=roadServiceDistance(site,b);if(distance<d){best=b;d=distance}}return best}
function emergencyDispatch(site,kind){if(!site)return;const service=closestRoadBuilding(site.x,site.y,kind);if(service){const v=beginVehicle(service,site,true);if(v){v.speed=5.5;return}}}
let trafficElapsed=0,intersectionGates=new Map();
function trafficUpdate(dt){
 if(paused||pendingEvent||!G||!visualDetailBudget().traffic)return;
 const target=Math.min(42,Math.round(5+Math.sqrt(G.stats.population)*1.25));
 trafficElapsed+=dt;trafficClock+=dt;
 let tries=0;
 while(trafficClock>.72&&traffic.length<target&&tries++<3){trafficClock-=.72;spawnPurposeTrip()}
 if(traffic.length>=target)trafficClock=Math.min(.72,trafficClock);
 const quality=clamp(.52+(G.stats.roadCondition??75)/130,.45,1.25);
 // Reserve occupied DIRECTED ROAD SEGMENTS rather than whole intersections.
 // A vehicle crossing a junction never blocks everyone who is merely
 // travelling on a different segment through that same road tile.
 const edges=new Map();
 for(const v of traffic){let a=v.path[v.segment],b=v.path[v.segment+1];if(b!=null)edges.set(a+'>'+b,v)}
 const ready=[],approved=new Set(),gateTaken=new Set(),network=graph();
 for(const v of traffic){
   v.age=(v.age||0)+dt;
   const step=Math.min(.34,dt*v.speed*quality);
   v.plannedStep=step;
   if(v.path[v.segment+1]==null){v.finished=true;continue}
   if(v.fraction+step<1){const leader=traffic.filter(c=>c!==v&&c.path[c.segment]===v.path[v.segment]&&c.path[c.segment+1]===v.path[v.segment+1]&&c.fraction>v.fraction).sort((a,b)=>a.fraction-b.fraction)[0];const next=leader?Math.min(v.fraction+step,Math.max(v.fraction,leader.fraction-.26)):v.fraction+step;if(next<=v.fraction+.00001)v.wait=(v.wait||0)+dt;else v.wait=0;v.fraction=next;continue;}
   ready.push(v);
 }
 ready.sort((a,b)=>(b.wait-a.wait)||Number(b.emergency)-Number(a.emergency)||(a.id-b.id));
 for(const v of ready){
   const junction=v.path[v.segment+1],after=v.path[v.segment+2];
   const valence=network.neighbors.get(junction)?.length||0;
   const leader=after==null?null:edges.get(junction+'>'+after);
   const entryBlocked=leader&&leader!==v&&leader.fraction<.45;
   const crossing=valence>=3;
   const last=intersectionGates.get(junction)||-99;
   const signalBlocked=crossing&&(trafficElapsed-last<.16||gateTaken.has(junction));
   if(entryBlocked||signalBlocked){v.fraction=Math.min(.96,v.fraction);v.wait=(v.wait||0)+dt;continue}
   approved.add(v.id);
   if(crossing){gateTaken.add(junction);intersectionGates.set(junction,trafficElapsed)}
 }
 for(const v of ready){
  if(!approved.has(v.id))continue;
  v.segment++;
  v.fraction=clamp(v.fraction+v.plannedStep-1,0,.34);
  v.wait=0;
 }
 // Max-duration safeguard protects against malformed saved routes, not
 // normal congestion. Ordinary traffic should make forward progress.
 for(let i=traffic.length-1;i>=0;i--){const v=traffic[i];if(v.finished||v.segment>=v.path.length-1){
    // A sampled commuter is not an economically delivered consignment.
    traffic.splice(i,1);
  }}
 for(const v of traffic)if(v.wait>4&&v.fraction<.001)detour(v);
 if(intersectionGates.size>450){for(const [k,t] of intersectionGates)if(trafficElapsed-t>3)intersectionGates.delete(k)}
 if(G.transit?.routes.some(r=>r.stats?.operating)&&cam.zoom>=.38)dirty=true;
 if(traffic.length||G.airport?.operating||G.metro?.operating||G.buildings.some(b=>b.kind==='factory'||b.kind==='mill'||b.kind==='worksite')||overlay==='metro')dirty=true;
}

function vehiclePosition(v){
 const i=v.segment,t=clamp(v.fraction,0,1),t2=t*t,t3=t2*t;
 const a=roadCenter(v.path[Math.max(0,i-1)]),p=roadCenter(v.path[i]);
 const q=roadCenter(v.path[Math.min(v.path.length-1,i+1)]),b=roadCenter(v.path[Math.min(v.path.length-1,i+2)]);
 // Catmull–Rom cornering has continuous position and heading at junctions.
 // With one-tile spacing, rounded turns remain within adjoining road tiles.
 const curve=(k)=>.5*(2*p[k]+(-a[k]+q[k])*t+(2*a[k]-5*p[k]+4*q[k]-b[k])*t2+(-a[k]+3*p[k]-3*q[k]+b[k])*t3);
 const tangent=(k)=>.5*((-a[k]+q[k])+2*(2*a[k]-5*p[k]+4*q[k]-b[k])*t+3*(-a[k]+3*p[k]-3*q[k]+b[k])*t2);
 let x=curve(0),y=curve(1),dx=tangent(0),dy=tangent(1);
 const length=Math.hypot(dx,dy)||1,side=v.style==='pedestrian'?(G.roadClasses?.[v.path[i]]==='arterial'?20:G.roadClasses?.[v.path[i]]==='collector'?17:13):4.3;
 return {x:x-dy/length*side,y:y+dx/length*side,dx,dy};
}
