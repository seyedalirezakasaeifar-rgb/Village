// Read-only planning scaffold. Authorization and UI mounting await integration review.
function regionalProcurementPlan(input){
 const keys=['day','quantity','stock','reserve','production','existing','freight','cash','journeyDays','dailyCapacity'];
 if(!input||keys.some(k=>!Number.isFinite(input[k])||input[k]<0)||!Number.isInteger(input.day)||!Number.isInteger(input.quantity)||input.quantity<20)return {ok:false,reasons:['Invalid order planning inputs'],milestones:[]};
 const {day,quantity,stock,reserve,production,existing,freight,cash,journeyDays,dailyCapacity}=input;
 const free=Math.max(0,stock-reserve),handling=Math.min(120,dailyCapacity),affordable=freight>0?cash/freight:Infinity;
 const early=Math.floor(quantity/2),targets=[{due:day+15,quantity:early},{due:day+30,quantity:quantity-early}];
 let promised=0;const milestones=targets.map(target=>{
  const dispatchDays=Math.max(0,target.due-day-journeyDays-1),cumulativeSupply=Math.max(0,free+production*dispatchDays-existing),cumulativeCapacity=handling*dispatchDays;
  const cumulativeDeliverable=Math.max(0,Math.min(cumulativeSupply,cumulativeCapacity,affordable));
  const available=Math.max(0,cumulativeDeliverable-promised),forecast=Math.min(target.quantity,Math.floor(available));promised+=target.quantity;
  return {...target,dispatchDays,forecast,shortfall:target.quantity-forecast,freightOutlay:target.quantity*freight};
 });
 return {ok:true,quantity,milestones,totalFreight:quantity*freight,retainedStock:Math.min(stock,reserve),existingCommitments:existing,risk:milestones.some(m=>m.shortfall>0),note:'One shared stock, forecast output, handling allowance and freight wallet cover both milestones. Forecasts reserve nothing. Existing promises are deducted conservatively; future attendance, queues, input purchases and competing orders can reduce delivery.'};
}
function regionalProcurementPlanHtml(plan){
 if(!plan.ok)return '<p class="desc">This order has invalid planning inputs.</p>';
 return '<article class="council-card"><h3>Two deliveries, one supply promise</h3><p class="desc">The first half must arrive early. A large final delivery cannot repair a missed first milestone. Both compete with current local buyers and existing export promises.</p><table class="report-table"><tr><th>Arrival deadline</th><th>Required</th><th>Forecast</th><th>Freight outlay</th></tr>'+plan.milestones.map(m=>'<tr><td>Day '+m.due+'</td><td>'+m.quantity+'</td><td>'+m.forecast+(m.shortfall?' · short '+m.shortfall:'')+'</td><td>'+m.freightOutlay.toFixed(2)+'</td></tr>').join('')+'</table><p class="desc">'+(plan.risk?'At least one deadline exceeds this forecast.':'Both deadlines fit the current forecast; delivery remains uncertain.')+' Cancelling future dispatch does not recall travelling cargo or refund carriage already purchased.</p></article>';
}
