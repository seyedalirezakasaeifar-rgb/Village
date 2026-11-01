// Geometry follows committed span/bank cells only. No navigation/economic work.
export const BRIDGE_TOP=.46;
export function bridgeHeightAt(x,z,bridges,size){
 for(const b of bridges){const a={x:b.banks[0]%size,z:Math.floor(b.banks[0]/size)},e={x:b.banks[1]%size,z:Math.floor(b.banks[1]/size)},dx=Math.sign(e.x-a.x),dz=Math.sign(e.z-a.z),along=(x-a.x)*dx+(z-a.z)*dz,cross=(x-a.x)*dz-(z-a.z)*dx,len=b.cells.length+1;
  if(Math.abs(cross)>.48||along<-.5||along>len+.5)continue;
  if(along<.5)return .075+Math.max(0,along)*2*(BRIDGE_TOP-.075);
  if(along>len-.5)return .075+Math.max(0,len-along)*2*(BRIDGE_TOP-.075);
  return BRIDGE_TOP;
 }return .075;
}
export function bridgeGeometry(bridge,size,box,ramp){
 const a={x:bridge.banks[0]%size,z:Math.floor(bridge.banks[0]/size)},e={x:bridge.banks[1]%size,z:Math.floor(bridge.banks[1]/size)},dx=Math.sign(e.x-a.x),dz=Math.sign(e.z-a.z),len=bridge.cells.length+1;
 const part=(along,y,cross,l,h,w,color,id,semantic=false)=>box(a.x+along*dx+cross*dz,y,a.z+along*dz-cross*dx,dx?l:w,h,dx?w:l,color,.88,id,semantic);
 for(let k=0;k<bridge.cells.length;k++){const t=k+1,id=bridge.cells[k];part(t,BRIDGE_TOP-.09,0,1,.18,.88,'#a6aaa1',id);part(t,BRIDGE_TOP+.012,0,1,.024,.75,'#59696a',id);if(k%2===0){for(const side of [-1,1])part(t,.16,side*.36,.16,.32,.12,'#8a918b',id);}
  for(const side of [-1,1]){part(t,BRIDGE_TOP+.16,side*.42,1,.055,.045,'#c7c5b4',id);for(const off of [-.43,0,.43])part(t+off,BRIDGE_TOP+.08,side*.42,.035,.20,.04,'#9daba5',id);}part(t,BRIDGE_TOP+.027,0,.36,.006,.025,'#d2c6a0',id);
 }
 for(const [bank,t,direction] of [[bridge.banks[0],0,1],[bridge.banks[1],len,-1]]){
  part(t+direction*.48,.18,0,.16,.36,.95,'#9c9e90',bank);
  // Eight shallow ramp treads give a continuous profile at phone scale, with
  // both endpoints meeting the actual road and raised water-span deck.
  if(ramp)ramp({x:a.x+t*dx,z:a.z+t*dz,dx:dx*direction,dz:dz*direction,tile:bank});else for(let i=0;i<8;i++){const u=(i+.5)/16,h=.075+(BRIDGE_TOP-.075)*u*2;part(t+direction*u,h/2,0,1/16+.002,h,.78,'#667573',bank);}
  if(bridge.closed){part(t,.28,0,.065,.05,.76,'#b28a55',bank,true);for(const side of [-1,1])part(t,.18,side*.36,.05,.36,.05,'#a65143',bank,true);}
 }
}
