// Reconstruct only damaged pixels from the cached ground/shadow underlay.
// Re-stamping translucent foreground sprites onto their already composited
// pixels produced travelling dark rectangles and antialiased-edge ghosts.
function mapPaintTransform(g){g.setTransform(dpr,0,0,dpr,0,0);g.translate(cw/2,ch/2);g.scale(cam.zoom,cam.zoom);g.translate(-cam.x,-cam.y);}
function scenePaintBounds(a){
 if(a._paintBounds)return a._paintBounds;
 if(a.kind==='transitArt')return [a.x-90,a.y-42,a.x+90,a.y+48];
 if(a.kind==='boat')return [a.x-44,a.y-32,a.x+44,a.y+32];
 if(a.kind==='vehicle'||a.kind==='workday')return [a.x-25,a.y-32,a.x+31,a.y+20];
 if(a.kind==='guideway')return a._paintBounds=[a.x-30,a.y-22,a.x+30,a.y+22];
 if(a.kind==='transitPier')return a._paintBounds=[a.x-9,a.y-34,a.x+9,a.y+3];
 const side=a.b?Math.ceil((a.w+a.d)*18+20):36,top=a.b?(a.b.kind==='tower'?192:112):72,bottom=a.b?Math.ceil((a.w+a.d)*18+24):24;
 return a._paintBounds=[a.x-side,a.y-top,a.x+side,a.y+bottom];
}
function paintBoundsOverlap(a,b){return a[0]<b[2]&&a[2]>b[0]&&a[1]<b[3]&&a[3]>b[1];}
function sceneActorPaintY(a,bridges){
 let y=a.y;const bounds=scenePaintBounds(a),elevated=a.kind==='transitArt'&&a.mode==='elevated';
 // A deck at z28 occludes ground actors wherever their projected silhouettes
 // meet. Trains occupy the elevated plane and draw above their guideway.
 for(const deck of bridges)if(paintBoundsOverlap(bounds,deck.bounds))y=elevated?Math.max(y,deck.item.y+.001):Math.min(y,deck.item.y-.001);
 return y;
}
function paintSceneLayer(g,a){if(a.kind==='transitArt')paintTransitVehicle(g,a);else if(a.kind==='vehicle')vehiclePaint(g,a.v,a,frameClock);else if(a.kind==='boat')paintWaterBoat(g,a,frameClock);else if(a.kind==='workday')paintWorkdayScene(g,a,frameClock);else drawSceneSprite(g,a);}
const actorRepairRaster=document.createElement('canvas');
function paintSceneActors(g,actors,visible=()=>true){
 if(!actors.length)return;
 const damage=actors.map(scenePaintBounds),bridges=viewBuildings.filter(a=>a.kind==='guideway').map(item=>({item,bounds:scenePaintBounds(item)}));
 const layers=actors.map(a=>({a,y:sceneActorPaintY(a,bridges)}));
 for(const a of viewBuildings){const bounds=scenePaintBounds(a);if(damage.some(r=>paintBoundsOverlap(bounds,r)))layers.push({a,y:a.y});}
 layers.sort((a,b)=>a.y-b.y);
 g.save();g.setTransform(1,0,0,1,0,0);g.beginPath();
 // Integer backing-pixel clips prevent fractional clip-edge double blending.
 for(const r of damage){const x=Math.floor(((r[0]-cam.x)*cam.zoom+cw/2)*dpr),y=Math.floor(((r[1]-cam.y)*cam.zoom+ch/2)*dpr),right=Math.ceil(((r[2]-cam.x)*cam.zoom+cw/2)*dpr),bottom=Math.ceil(((r[3]-cam.y)*cam.zoom+ch/2)*dpr);g.rect(x,y,right-x,bottom-y);}
 g.clip();
 if(actorRepairRaster.width!==viewUnderlayRaster.width)actorRepairRaster.width=viewUnderlayRaster.width;if(actorRepairRaster.height!==viewUnderlayRaster.height)actorRepairRaster.height=viewUnderlayRaster.height;
 const repair=actorRepairRaster.getContext('2d',{alpha:false});repair.setTransform(1,0,0,1,0,0);repair.imageSmoothingEnabled=false;repair.drawImage(viewUnderlayRaster,0,0);mapPaintTransform(repair);drawWaterLife(repair,visible);drawWaterfrontPiers(repair,visible);drawRegionalGates(repair,visible);drawTransitInfrastructure(repair,visible);for(const layer of layers)paintSceneLayer(repair,layer.a);g.drawImage(actorRepairRaster,0,0);g.restore();
}
