// A transport sample can be inspected without changing economic cargo or jobs.
let inspectedTrip=null;
function inspectTripAt(wx,wy){
 let nearest=null,distance=12/cam.zoom;
 for(const v of traffic){const p=vehiclePosition(v),d=Math.hypot(wx-p.x,wy-p.y);if(d<distance){nearest=v;distance=d;}}
 if(!nearest)return false;inspectedTrip={...nearest,path:nearest.path.slice()};openPanel('trip');dirty=true;return true;
}
function renderTripInspector(){
 if(!inspectedTrip)return tip('Tap a moving commuter or delivery on the map.');
 const live=traffic.find(v=>v.id===inspectedTrip.id),trip=live||inspectedTrip,from=readBuild(trip.from),to=readBuild(trip.to),shipment=(G.freight||[]).find(s=>s.id===trip.shipment);
 const label=b=>b?b.firm>=0?(G.firms[b.firm]?.name||types[b.kind].n):b.hh>=0?(G.households[b.hh]?.name+' household'):types[b.kind].n:'Former site';
 return head(trip.style==='truck'?'Delivery on the road':trip.style==='pedestrian'?'A resident on foot':'A resident’s journey')+tip(trip.reason||'Local service journey')+strip('Trip sample',live?'Travelling':'Completed or no longer sampled')+strip('Origin',label(from))+strip('Destination',label(to))+strip('Road segments',Math.max(0,trip.path.length-1))+(shipment?strip('Cargo in transit',fmt(shipment.qty)+' '+shipment.good)+strip('Delivery accounting',shipment.remaining+' simulated days remaining'):'')+tip('Visible trips sample real job assignments and paid cargo. The economy continues tracking residents and shipments when visual traffic is hidden.')+`<div class="btnrow">${from?`<button data-inspect="${from.id}">Inspect origin</button>`:''}${to?`<button data-inspect="${to.id}">Inspect destination</button>`:''}<button data-trip-close>Back to map</button></div>`;
}
function drawInspectedRoute(g){
 if(active!=='trip'||!inspectedTrip)return;const trip=traffic.find(v=>v.id===inspectedTrip.id)||inspectedTrip;
 g.save();g.strokeStyle='#f2d99c';g.lineWidth=3/cam.zoom;g.lineJoin='round';g.beginPath();trip.path.forEach((id,i)=>{const p=roadCenter(id);if(i)g.lineTo(...p);else g.moveTo(...p)});g.stroke();
 for(const id of [trip.path[0],fromEnd(trip.path)]){const p=roadCenter(id);g.fillStyle='#315e4b';g.beginPath();g.arc(...p,5/cam.zoom,0,Math.PI*2);g.fill();}g.restore();
}
document.addEventListener('click',e=>{if(e.target.closest('[data-trip-close]'))closePanel()});
