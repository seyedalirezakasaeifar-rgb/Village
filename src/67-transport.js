function setPurposeStyle(v,style){v.style=style;v.speed=style==='pedestrian'?.53:style==='truck'?.90:1.15;return v;}
function restoreTransport(){
 const state=G.trafficState;visualState=G.visualState||918273;
 traffic=[];trafficClock=0;intersectionGates.clear();
 if(state){traffic=(state.vehicles||[]).filter(v=>Array.isArray(v.path)&&v.path.length>=2&&v.path.every(n=>Number.isInteger(n)&&G.tiles[n]===1)&&Number.isInteger(v.segment)&&v.segment>=0&&v.segment<v.path.length-1&&Number.isFinite(v.fraction)&&v.fraction>=0&&v.fraction<1).slice(0,80).map(v=>({...v,path:v.path.slice()}));frameClock=Number(state.clock)||0;trafficElapsed=Number(state.elapsed)||0;vehicleSerial=Number(state.serial)||0;intersectionGates=new Map((state.gates||[]).filter(a=>Array.isArray(a)&&a.length===2));}
}
function pendingGoods(firm,good){return (G.freight||[]).filter(s=>s.to===firm.id&&s.good===good).reduce((n,s)=>n+s.qty,0);}
function dispatchGoods(seller,buyer,good,qty,path){
 G.freight=G.freight||[];G.nextFreight=(G.nextFreight||0)+1;
 const duration=Math.max(1,Math.ceil((path.length-1)/15));
 G.freight.push({id:G.nextFreight,from:seller.id,to:buyer.id,good,qty,path,remaining:duration,duration,started:G.day,delayed:0});
}
function freightDay(){
 if(!G.freight?.length)return;
 const keep=[];
 for(const s of G.freight){const from=G.firms[s.from],to=G.firms[s.to];if(!from||!to){throw Error('Shipment has an invalid owner');}
  const route=routeBetween(readBuild(from.building),readBuild(to.building));
  if(route.length<1){s.delayed++;keep.push(s);G.transport.delayed++;continue;}
  s.path=route;s.remaining--;
  if(s.remaining>0)keep.push(s);else{to.stock[s.good]=(to.stock[s.good]||0)+s.qty;G.transport.arrived++;}
 }
 G.freight=keep;
}
function spawnPurposeTrip(){
 if(!G)return null;
 // Trips are samples of actual commuter assignments or paid in-flight cargo.
 const freights=G.freight||[];if(freights.length&&vehicleSerial%3===0){const s=freights[vehicleSerial%freights.length],f=G.firms[s.from],t=G.firms[s.to];const v=beginVehicle(readBuild(f.building),readBuild(t.building));if(v){setPurposeStyle(v,'truck');v.reason=s.qty.toFixed(0)+' '+s.good+' → '+t.name;v.shipment=s.id;return v;}}
 const employed=G.people.filter(p=>!p.deceased&&!p.movedAway&&p.job>=0);if(!employed.length)return null;
 const p=employed[hash(vehicleSerial+G.day)%employed.length],h=G.households[p.hh],f=G.firms[p.job];
 if(p.transitTrip?.day===G.day)return null;
 const home=readBuild(h.home),work=readBuild(f.building);if(!home||!work||f.closed)return null;
 const returning=vehicleSerial%2===1;const v=beginVehicle(returning?work:home,returning?home:work);if(v){setPurposeStyle(v,(p.id%3===0)?'pedestrian':'car');v.person=p.id;v.reason=p.name+(returning?' returning home':' commuting to '+f.name);}return v;
}
function detour(v){
 const start=v.path[v.segment],goal=fromEnd(v.path),net=graph();
 const queue=[start],parent=new Map([[start,-1]]),busy=new Set(traffic.filter(c=>c!==v&&c.wait>2).map(c=>c.path[c.segment]+'>'+c.path[c.segment+1]));
 for(let i=0;i<queue.length&&i<3200;i++){const at=queue[i];if(at===goal)break;for(const n of net.neighbors.get(at)||[]){if(parent.has(n)||busy.has(at+'>'+n))continue;parent.set(n,at);queue.push(n);}}
 if(!parent.has(goal))return false;
 const path=[];for(let at=goal;at!==-1;at=parent.get(at))path.push(at);path.reverse();
 if(path.length<2||path[1]===v.path[v.segment+1])return false;
 // Replanning happens only at a tile center, preserving continuous position.
 if(v.fraction>.001)return false;
 v.path=path;v.segment=0;v.wait=0;v.rerouted=(v.rerouted||0)+1;return true;
}
