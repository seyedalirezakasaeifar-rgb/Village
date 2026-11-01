// Pure bounded view selection. No simulation/cache mutation.
export function viewLOD(zoom){return zoom<.85?'far':zoom<1.6?'mid':'near';}
export function selectView(corners,size,lod,margin=4){
 const xs=corners.map(p=>p.x),zs=corners.map(p=>p.z),step=8;
 const minX=Math.min(size-1,Math.max(0,Math.floor((Math.min(...xs)-margin)/step)*step)),minZ=Math.min(size-1,Math.max(0,Math.floor((Math.min(...zs)-margin)/step)*step)),maxX=Math.max(0,Math.min(size-1,Math.ceil((Math.max(...xs)+margin)/step)*step)),maxZ=Math.max(0,Math.min(size-1,Math.ceil((Math.max(...zs)+margin)/step)*step));
 return {minX,minZ,maxX,maxZ,lod,key:[minX,minZ,maxX,maxZ,lod].join(':')};
}
export function overviewZoom(width,height,size){return .92*Math.min(10*(width/height)/(size/Math.SQRT2),10/(size*(30/Math.hypot(30,26,26))/Math.SQRT2));}
