// Daily service purchases include paid allocations and an exactly-once guard.
// Preserve validated same-day receipts; invalidate older observations, not cash.
function normalizeServiceReceiptArchive(data){
 const object=v=>v!=null&&typeof v==='object'&&!Array.isArray(v),nonnegative=v=>Number.isFinite(v)&&v>=0;
 const day=v=>Number.isSafeInteger(v)&&v>=1&&v<=data.day,close=(a,b)=>Math.abs(a-b)<=.005+Math.max(Math.abs(a),Math.abs(b))*1e-9;
 const ownedEntries=(map,owners)=>object(map)&&Object.keys(map).length<=owners.length&&Object.entries(map).every(([id])=>/^\d+$/.test(id)&&String(+id)===id&&owners[+id]);
 const validPublic=state=>object(state)&&Object.keys(state).every(kind=>{
  if(!['health','school'].includes(kind))return false;const r=state[kind];
  if(!object(r)||!day(r.day)||!['authorized','required','requested','paid','population','coverage','wage'].every(k=>nonnegative(r[k])))return false;
  if(r.paid>r.requested+.005||r.requested>Math.min(r.authorized,r.required)+.005||r.coverage>1.000001||r.population>data.people.length)return false;
  for(const k of ['unspent','facilities','facilityCoverage','accessCoverage','accessLimit','accessibleResidents'])if(r[k]!=null&&!nonnegative(r[k]))return false;
  if(r.unspent!=null&&!close(r.unspent,r.authorized-r.paid)||['facilityCoverage','accessCoverage'].some(k=>r[k]!=null&&r[k]>1.000001))return false;
  const s=r.staffing;if(s!=null&&(!object(s)||!['local','regional','needed','coverage','qualification'].every(k=>nonnegative(s[k]))||s.coverage>1.000001||s.pending!=null&&(!object(s.pending)||!nonnegative(s.pending.target)||!Number.isSafeInteger(s.pending.day)||s.pending.day<1)))return false;
  return true;
 });
 const validPrivate=state=>{
  if(!object(state)||state.version!==1||!day(state.day)||!['tuition','memberships','vouchers','pupils','fireMembers'].every(k=>nonnegative(state[k])))return false;
  if(!['school','fire'].every(kind=>ownedEntries(state[kind],data.households)&&Object.values(state[kind]).every(v=>nonnegative(v)&&v<=1.000001))||!ownedEntries(state.allocations,data.firms))return false;
  const totals={tuition:0,memberships:0,vouchers:0,pupils:0,fireMembers:0};
  for(const [id,allocations] of Object.entries(state.allocations)){
   const kind=data.firms[+id].privateService;if(!['school','fire'].includes(kind)||!ownedEntries(allocations,data.households))return false;
   for(const row of Object.values(allocations)){
    if(!object(row)||!['served','paid','subsidy'].every(k=>nonnegative(row[k])))return false;
    totals[kind==='school'?'tuition':'memberships']+=row.paid;totals[kind==='school'?'pupils':'fireMembers']+=row.served;totals.vouchers+=row.subsidy;
   }
  }
  return Object.keys(totals).every(k=>Number.isFinite(totals[k])&&close(totals[k],state[k]));
 };
 for(const [key,validate] of [['serviceProvision',validPublic],['privateServiceProvision',validPrivate]]){
  const state=data[key];if(state==null)continue;
  if(!validate(state)){if(data.schema!=null&&data.schema>=8)return false;data[key]=null;continue;}
  if(key==='serviceProvision'?Object.values(state).some(row=>row.day!==data.day):state.day!==data.day)data[key]=null;
 }
 return true;
}
