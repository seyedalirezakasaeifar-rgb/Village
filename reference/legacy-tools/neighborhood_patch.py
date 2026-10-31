from pathlib import Path
f=Path(__file__).resolve().parent.parent/'assets'/'game.js';s=f.read_text()
a=""" for(let i=0;i<67&&slots.length;i++){
   const p=slots.shift();const b=add('home',...p,{value:Math.round(rn(35000,70000))});"""
b=""" // Neighbourhoods grow along existing roads, rather than a single wall of
 // identical cottages around the town hall. Preserve each household's address.
 const quarters=[[20,22],[34,22],[21,34],[35,34],[16,27],[39,27]];
 for(let i=0;i<67&&slots.length;i++){
   const q=quarters[i%quarters.length];let index=-1,best=Infinity;
   for(let k=0;k<slots.length;k++){
    const [sx,sy]=slots[k];if(!canPlace(sx,sy,true,'home'))continue;
    const d=Math.abs(sx-q[0])+Math.abs(sy-q[1]);
    let crowd=0;for(const building of G.buildings){const reach=Math.abs(sx-building.x)+Math.abs(sy-building.y);
      if(reach<=2)crowd+=building.kind==='home'?1.45:building.kind==='farm'?3.8:building.firm>=0?1.1:.45;
    }
    const score=d*1.7+crowd*1.5+Math.abs(sx-27)*.045+Math.random()*.5;
    if(score<best){best=score;index=k}
   }
   if(index<0)break;
   const p=slots.splice(index,1)[0];const b=add('home',...p,{value:Math.round(rn(35000,70000))});"""
assert a in s;s=s.replace(a,b);f.write_text(s)
