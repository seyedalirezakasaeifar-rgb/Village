// A connected street hierarchy: through routes, collectors, and short local streets.
// No nested decorative rings. Imported towns retain their existing parcels and streets.
function foundingStreetPlan(){
 const classes={},names={};
 const line=(x1,y1,x2,y2,kind,name)=>{const dx=Math.sign(x2-x1),dy=Math.sign(y2-y1);let x=x1,y=y1;for(let i=0;i<100;i++){const id=y*T+x;classes[id]=kind;names[id]=name;if(x===x2&&y===y2)break;x+=dx;y+=dy;}};
 line(8,27,49,27,'arterial','High Street');line(27,7,27,49,'arterial','Station Road');
 line(15,9,15,45,'collector','River Road');line(43,13,43,48,'collector','County Road');
 line(9,13,43,13,'collector','North Avenue');line(15,21,47,21,'collector','Market Street');line(9,35,47,35,'collector','Orchard Avenue');line(15,43,47,43,'collector','South Avenue');
 line(21,13,21,35,'local','Church Lane');line(35,13,35,43,'local','Mill Street');
 line(15,31,27,31,'local','Garden Street');line(35,31,40,31,'local','Foundry Close');line(21,39,35,39,'local','School Street');line(21,35,21,43,'local','School Lane');
 return {classes,names};
}
