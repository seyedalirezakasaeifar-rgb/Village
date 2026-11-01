// Actual reserved track cells only. Lane/beam geometry adds no service capacity.
export function transitGeometry(cells,size,box,bounds,lod){
 const tracks=new Set(cells),has=(x,z)=>x>=0&&z>=0&&x<size&&z<size&&tracks.has(z*size+x);
 for(const id of tracks){const x=id%size,z=Math.floor(id/size);if(x<bounds.minX||x>bounds.maxX||z<bounds.minZ||z>bounds.maxZ)continue;const alongX=has(x-1,z)||has(x+1,z),alongZ=has(x,z-1)||has(x,z+1),junction=alongX&&alongZ;
  box(x,1.10,z,junction?.96:.66,.16,junction?.96:.66,'#a2aaa3');
  for(const [dx,dz]of [[1,0],[0,1]])if(has(x+dx,z+dz)){
   box(x+dx*.5,1.10,z+dz*.5,dx?1:.66,.16,dz?1:.66,'#a2aaa3');
   if(lod!=='far')for(const lane of [-.15,.15])for(const gauge of [-.09,.09]){const side=lane+gauge;box(x+dx*.5+dz*side,1.205,z+dz*.5+dx*side,dx?1:.025,.025,dz?1:.025,'#56686b');}
  }
  // Portal frames stand at the reserved road verges, never in car lanes or
  // the central navigable water ribbon. Corners use adjacent straight spans.
  if(id%2===0&&!junction){const dx=alongX?1:0,dz=alongX?0:1;for(const side of [-1,1])box(x+dz*side*.47,.46,z+dx*side*.47,.045,.92,.045,'#8f9992');box(x,.97,z,dx?.13:.98,.10,dx?.98:.13,'#929c94');}
 }
}
