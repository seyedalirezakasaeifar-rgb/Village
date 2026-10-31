// Shopping-centre labour bids use the same identities, commute limits and
// public-role reservations as actual employment. A forecast never hires people.
function urbanRetailLabour(site,offered=null){
 const net=graph(),port=net.portals.get(site.id)??roadOffsets.map(([dx,dy])=>roadId(site.x+dx,site.y+dy)).find(id=>net.parts[id]===net.mainPart),distances=privateServiceDistances(port),bids=[];
 if(port==null)return bids;
 for(const p of G.people){
  if(p.deceased||p.movedAway||p.age<16||p.age>70||p.publicWork||p.publicRole||p.previousPublicRole||(p.searchAfter||0)>G.day)continue;
  const home=readBuild(G.households[p.hh]?.home),distance=home?distances.get(net.portals.get(home.id))??Infinity:Infinity;if(distance>40)continue;
  const old=p.job>=0?G.firms[p.job]:null;if(old?.privateService||old&&!old.closed&&G.day-(p.privateJobChange||-90)<60)continue;
  const wage=old&&!old.closed?Math.max(G.policy.minWage,workerIncome(old)*1.121):Math.max(G.policy.minWage,28);
  if(offered!=null&&wage>offered+1e-7)continue;
  bids.push({person:p.id,wage,distance});
 }
 return bids.sort((a,b)=>a.wage-b.wage||a.distance-b.distance||a.person-b.person);
}
function urbanRetailPlan(site,customers,offers=null){
 const units=customers*1.6,staff=clamp(Math.ceil(units/65),2,8),bids=offers||urbanRetailLabour(site);if(bids.length<staff)return null;
 const wage=Math.ceil(bids[staff-1].wage*100)/100,price=G.market?.baseFoodPrice||5.2,cost=marketPrice('food')*1.12,margin=price-cost;
 const rates=220000*(G.policy.commercialRate||0)/100/360,overhead=2+staff*(.6+G.policy.businessRegulation*.035),profit=units*margin-staff*wage-overhead-rates,net=profit*(1-G.policy.profitTax/100);
 const atOffer=bids.filter(b=>b.wage<=wage+1e-7),jobseekers=atOffer.filter(b=>G.people[b.person]?.job<0).length;
 return {staff,wage,customers,units,price,cost,profit,net,eligibleAtOffer:atOffer.length,jobseekersAtOffer:jobseekers,employedPremiumAtOffer:atOffer.length-jobseekers};
}
function recruitUrbanRetailStaff(only=null){
 for(const f of only?[only]:G.firms.filter(f=>f.retailCentre&&!f.closed)){
  if(!f.retailCentre||f.closed||f.workers.length>=f.jobs||f.cash<workerIncome(f)*Math.max(1,f.jobs)*20)continue;const site=readBuild(f.building);if(!site)continue;
  // A vacant operator may revise a funded wage offer after a monthly review.
  // This uses actual reachable retail demand, costs and current labour bids.
  if(!f.workers.length&&G.day-(f.retailHiringReview||0)>=30){
   const bids=urbanRetailLabour(site),bid=bids[0],units=Math.max(1,reachableRetailDemand(f)),margin=f.price-(f.unitCost?.food||marketPrice('food'));
   if(bid&&units*margin-bid.wage-10>0&&f.cash>bid.wage*90){f.wage=Math.max(f.wage,Math.ceil(bid.wage*100)/100);f.retailHiringReview=G.day;}
  }
  for(const bid of urbanRetailLabour(site,workerIncome(f))){if(f.workers.length>=f.jobs)break;const p=G.people[bid.person];if(p.job===f.id)continue;const old=p.job>=0?G.firms[p.job]:null;
   if(old)old.workers=old.workers.filter(id=>id!==p.id);p.job=f.id;p.privateJobChange=G.day;p.commuteBlocked=false;p.commuteBlockedDays=0;f.workers.push(p.id);
  }
 }
}
function validateUrbanRetailLabour(data){
 const number=(n,lo,hi)=>Number.isFinite(n)&&n>=lo&&n<=hi;
 return (data.projects||[]).every(p=>p.retailStaff==null&&p.retailWage==null||p.retailCentre===true&&Number.isInteger(p.retailStaff)&&number(p.retailStaff,2,8)&&number(p.retailWage,10,120))&&data.firms.every(f=>f.retailHiringReview==null||f.retailCentre===true&&Number.isInteger(f.retailHiringReview)&&f.retailHiringReview>=0&&f.retailHiringReview<=data.day);
}
