// Overlay keys live inside the existing Town Signals touch control so they
// never cover map controls or intercept a map inspection.
const MAP_OVERLAY_KEYS={
 roads:'ROAD · circle + direct street edge · square X no edge',
 business:'BUSINESS · circle + profitable · square = no profit · triangle X closed',
 hardship:'STRESS · triangle ! over 50 · circle dot 50 or lower',
 crime:'THEFT · counted markers show actual sites from the last 30 days',
 land:'LAND VALUE · triangle ^ over $90k · square = $45–90k · circle below $45k',
 transit:'TRANSIT · solid line/square stop bus · dashed line/circle metro',
 metro:'UNDERGROUND · dashed route · M station',
 healthAccess:'MEDICAL REACH · circle + everyone · ! some · X none',
 schoolAccess:'SCHOOL REACH · circle + everyone · ! some · X none',
 neighbourhoods:'DISTRICTS · A agriculture · C civic · M mixed · income band shown',
 charter:'LAND · solid boundary owned   dashed boundary available'
};
let mapOverlayKeyCache=null;
function updateMapOverlayKey(){const value=MAP_OVERLAY_KEYS[overlay]||'';if(value===mapOverlayKeyCache)return;mapOverlayKeyCache=value;const node=$('mapStatusOverlayKey');if(node&&node.textContent!==value)node.textContent=value;}
function overlayBadge(g,x,y,label,shape){
 const r=6.4;g.save();g.translate(x,y);g.beginPath();
 if(shape==='square')g.rect(-r,-r,r*2,r*2);
 else if(shape==='triangle'){g.moveTo(0,-r-1);g.lineTo(r+1,r);g.lineTo(-r-1,r);g.closePath();}
 else g.arc(0,0,r,0,Math.PI*2);
 g.fillStyle='#f5f0dc';g.strokeStyle='#172c28';g.lineWidth=2;g.fill();g.stroke();g.fillStyle='#172c28';g.font='bold 9px Arial,sans-serif';g.textAlign='center';g.textBaseline='middle';g.fillText(label,0,.3);g.restore();
}
function overlayScreenPoint(x,y){return [cw/2+(x-cam.x)*cam.zoom,ch/2+(y-cam.y)*cam.zoom];}
function drawOverlayStatusMarks(g){
 if(cam.zoom<.45||!['roads','business','hardship','crime','land'].includes(overlay))return;
 const crime=new Map();if(overlay==='crime')for(const event of G.cases||[])if(Number.isInteger(event.bid)&&G.day-event.day>=0&&G.day-event.day<30)crime.set(event.bid,(crime.get(event.bid)||0)+1);
 g.save();g.setTransform(dpr,0,0,dpr,0,0);g.textBaseline='middle';const items=viewBuildings,roadNetwork=overlay==='roads'?graph():null;
 if(overlay==='crime'){
  for(const [id,count] of crime){const item=buildingItemsById.get(id);if(!item)continue;const [x,y]=overlayScreenPoint(item.x,item.y+11);if(x<8||x>cw-8||y<8||y>ch-8)continue;overlayBadge(g,x,y,String(Math.min(9,count)),count>1?'square':'circle');}
 }else for(const item of items){if(item.kind!=='building'||!item.b)continue;const b=item.b,[x,y]=overlayScreenPoint(item.x,item.y+11);if(x<8||x>cw-8||y<8||y>ch-8)continue;let label,shape;
  if(overlay==='roads'){const connected=roadNetwork.portals.has(b.id);label=connected?'+':'X';shape=connected?'circle':'square';}
  else if(overlay==='business'){const f=G.firms[b.firm];if(!f)continue;if(f.closed){label='X';shape='triangle';}else if(f.profit>0){label='+';shape='circle';}else{label='=';shape='square';}}
  else if(overlay==='hardship'){const h=G.households[b.hh];if(!h)continue;label=h.stress>50?'!':'·';shape=h.stress>50?'triangle':'circle';}
  else{label=b.value>90000?'^':b.value>45000?'=':'·';shape=b.value>90000?'triangle':b.value>45000?'square':'circle';}
  overlayBadge(g,x,y,label,shape);
 }
 g.restore();
}
const overlayLegibilityDrawBase=draw;draw=function(){const needsPaint=!!G&&dirty;overlayLegibilityDrawBase();updateMapOverlayKey();if(needsPaint)drawOverlayStatusMarks(ctx);};
