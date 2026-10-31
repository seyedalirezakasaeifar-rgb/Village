// Planning boundaries only: no authorization, account transfer or save mutation.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
vm.runInThisContext(fs.readFileSync('src/98-procurement-planner.js','utf8'));
const base={day:31,quantity:200,stock:100,reserve:20,production:10,existing:0,freight:1,cash:200,journeyDays:3,dailyCapacity:120};
let p=regionalProcurementPlan(base);assert(!p.risk);assert.equal(p.milestones.reduce((n,m)=>n+m.quantity,0),200);
// Both milestones share the same eighty available stock units, never eighty each.
p=regionalProcurementPlan({...base,production:0});assert.deepEqual(p.milestones.map(m=>m.forecast),[80,0]);
// Enough output by day thirty cannot make an impossible day-fifteen arrival timely.
p=regionalProcurementPlan({...base,stock:20,journeyDays:15});assert.equal(p.milestones[0].forecast,0);assert(p.milestones[1].forecast>0);
p=regionalProcurementPlan({...base,cash:100});assert.equal(p.milestones[1].forecast,0);
p=regionalProcurementPlan({...base,production:0,existing:80});assert.equal(p.milestones[0].forecast,0);
p=regionalProcurementPlan({...base,dailyCapacity:2});assert(p.milestones[0].forecast<=22);assert(p.milestones[1].forecast<=Math.max(0,52-100));
const before=JSON.stringify(base);assert.deepEqual(regionalProcurementPlan(base),regionalProcurementPlan(base));assert.equal(JSON.stringify(base),before);
assert(!regionalProcurementPlan({...base,quantity:NaN}).ok);assert(regionalProcurementPlanHtml(regionalProcurementPlan(base)).includes('Day 46'));
console.log('PASS shared stock/cash/capacity, early deadline, prior promises, pure replay and preview');
