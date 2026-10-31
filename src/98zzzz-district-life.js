// Overview information replaces microscopic actors. One bounded consignment
// summary per daily shipment array; no resident/vehicle iteration at far zoom.
let overviewFreightCache=null;
function overviewFreight(){
 const orders=G.regionalTrade?.shipments,net=graph();
 if(overviewFreightCache?.orders===orders&&overviewFreightCache.net===net&&overviewFreightCache.count===(orders?.length||0)&&overviewFreightCache.revision===(G.regionalTrade?.routeRevision||0))return overviewFreightCache.rows;
 const rows=[];
 for(const market of OUTSIDE_MARKETS){let inbound=0,outbound=0,quantity=0,example=null;
  for(const order of orders||[]){if(order.market!==market.id)continue;const returning=['returning','return-outside'].includes(order.stage);if((order.direction==='import')!==returning)inbound++;else outbound++;quantity+=order.qty;example=example||order;}
  if(!example)continue;
  // Preserve the actual representative road route, reducing only straight runs.
  const path=example.path,points=[];for(let i=0;i<path.length;i++){const id=path[i],before=path[i-1],after=path[i+1];if(i&&i<path.length-1&&id-before===after-id)continue;points.push(roadCenter(id));}
  const gate=regionalGateway(market);if(gate==null)continue;
  rows.push({market:market.id,inbound,outbound,quantity,points,gate:roadCenter(gate)});
 }
 overviewFreightCache={orders,net,rows,count:orders?.length||0,revision:G.regionalTrade?.routeRevision||0};return rows;
}
function drawDistrictLife(g,visible){
 if(!gameOptions.decor)return;
 const z=cam.zoom;
 if(z<.45&&gameOptions.traffic){
  const rows=overviewFreight();g.save();
  for(const row of rows){g.strokeStyle='#f2ce83b3';g.lineWidth=1.2/z;g.setLineDash([4/z,5/z]);g.beginPath();row.points.forEach((p,i)=>i?g.lineTo(...p):g.moveTo(...p));g.stroke();g.setLineDash([]);
   const p=[clamp(row.gate[0],cam.x-(cw/2-45)/z,cam.x+(cw/2-45)/z),clamp(row.gate[1],cam.y-ch/(2*z)+78/z,cam.y+ch/(2*z)-18/z)];
   const text=row.market.toUpperCase()+' '+row.inbound+' IN · '+row.outbound+' OUT';g.font='bold '+(7/z)+'px Arial';const width=g.measureText(text).width+8/z;
   g.fillStyle='#344f45e8';g.fillRect(p[0]-width/2,p[1]-16/z,width,12/z);g.fillStyle='#f2dfaa';g.textAlign='center';g.fillText(text,p[0],p[1]-7/z);
  }
  // These are active consignments, not invented trucks or instantaneous sales.
  if(rows.length){g.setTransform(dpr,0,0,dpr,0,0);g.font='7px Arial';g.fillStyle='#e9dfbf';g.textAlign='center';g.fillText(rows.reduce((n,r)=>n+r.inbound+r.outbound,0)+' OWNED LOADS · queues/outside legs included',cw*.53,12);transform();}
  g.restore();
 }
 if(z>=.45&&z<1){
  let labels=0;g.save();
  for(const item of viewBuildings){const b=item.b;if(!b||!visible(item.x,item.y,0))continue;
   if(['school','fire'].includes(b.kind)&&labels++<6){const state=providerVisualState(b),q=[item.x,item.y+15],color=state.closed?'#a67f65':state.independent?'#cfb16b':'#8fb9a0';
    g.fillStyle='#354e45df';g.fillRect(q[0]-30/z,q[1],60/z,10/z);g.fillStyle=color;g.font='bold '+(6/z)+'px Arial';g.textAlign='center';g.fillText((state.independent?'PRIVATE ':'PUBLIC ')+(b.kind==='school'?'SCHOOL':'FIRE'),q[0],q[1]+7/z);
   }else if(b.condition<45){g.strokeStyle='#b97f55';g.lineWidth=1.5/z;const q=point(0,item.d*.40);segment(g,[item.x+q[0]-4/z,item.y+q[1]],[item.x+q[0]+4/z,item.y+q[1]],'#bb865e',2/z);}
  }g.restore();
 }
}
function neighbourhoodAmbient(items){
 if(!visualDetailBudget().people||!gameOptions.decor||gameOptions.quality==='low')return [];
 let parkSample=false;const result=[],cap=gameOptions.quality==='high'?7:4;
 for(const item of items){const b=item.b;if(!b||result.length>=cap)continue;
  if(!parkSample&&['park','square'].includes(b.kind)&&G.stats.population>0){const t=(1-Math.cos(frameClock*.35+b.id))/2,q=point(-item.w*.27+t*item.w*.54,0);result.push({kind:'vehicle',v:{id:900000+b.id,style:'pedestrian',color:'#829383',ambient:true},x:item.x+q[0],y:item.y+q[1],dx:1,dy:.5});parkSample=true;continue;}
  if(b.kind!=='home'||hash(b.id+G.worldSeed)%3!==0)continue;
  const h=G.households[b.hh],id=h?.people.find(id=>{const p=G.people[id];return p&&!p.deceased&&!p.movedAway&&p.age>=18;});if(id==null)continue;
  // Decorative doorstep/garden strolls stay inside the occupied legal parcel.
  // They do not claim a commute, paid service, purchase or scheduled location.
  const phase=(frameClock*.075+(hash(b.id)%101)/101)%1,t=(1-Math.cos(phase*Math.PI*2))/2;
  const a=point(-item.w*.22,item.d*.39),c=point(item.w*.22,item.d*.39),x=item.x+a[0]+(c[0]-a[0])*t,y=item.y+a[1]+(c[1]-a[1])*t,sign=phase<.5?1:-1;
  result.push({kind:'vehicle',v:{id,style:'pedestrian',color:['#ac8c64','#6d8c83','#8d7c91'][id%3],ambient:true},x,y,dx:(c[0]-a[0])*sign,dy:(c[1]-a[1])*sign});
 }
 return result;
}
