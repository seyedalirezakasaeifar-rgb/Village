const civicCandidateSets=new Map();
function qualifiedForService(p,kind){return !p.deceased&&!p.movedAway&&p.age>=18&&p.age<=70&&p.health>=60&&p.skill>=(kind==='health'?.7:.55)&&(!p.previousPublicRole||p.previousPublicRole===kind);}
function civicStaffCapacity(kind,authorized,access){
 const standard=CIVIC_STANDARDS[kind],wage=Math.max(24,G.policy.minWage),needed=G.stats.population*standard.staff/standard.capacity;
 const reachable=new Set(access.households.filter(h=>h.distance!=null).map(h=>h.id)),candidates=G.people.filter(p=>p.job<0&&qualifiedForService(p,kind)&&reachable.has(p.hh));civicCandidateSets.set(kind,new Set(candidates.map(p=>p.id)));
 const local=candidates.reduce((n,p)=>n+Math.max(0,1-(p.publicIncome||0)/wage),0);
 const demand=Math.min(needed*access.coverage,Math.max(0,authorized)*.65/wage),target=Math.max(0,demand-local);
 if(!G.civicStaffing)G.civicStaffing={};let contract=G.civicStaffing[kind];
 // Founding/migrated services inherit their operating arrangements. Subsequent
 // expansion must recruit, but regional contracts allow recovery without locals.
 if(!contract)contract=G.civicStaffing[kind]={ready:target,pending:null};
 if(contract.pending&&G.day>=contract.pending.day){contract.ready=contract.pending.target;contract.pending=null;}
 if(!contract.pending&&Math.abs(contract.ready-target)>.01)contract.pending={target,day:G.day+30};
 const available=Math.min(needed*access.coverage,local+contract.ready);
 return {local,regional:contract.ready,needed,coverage:needed?available/needed:0,pending:contract.pending?{...contract.pending}:null,qualification:kind==='health'?.7:.55};
}
function civicTrainingDay(coverage){
 if(G.civicTrainingLastDay===G.day)return;G.civicTrainingLastDay=G.day;
 if(!G.civicTraining)G.civicTraining=[];
 G.civicTraining=G.civicTraining.filter(c=>{const p=G.people[c.person];return p&&!p.deceased&&!p.movedAway&&p.age>=18&&p.age<=70;});
 const places=G.buildings.filter(b=>b.kind==='school'&&isPublicFacility(b)).length*2;
 if(coverage>0&&G.serviceProvision?.school?.paid>0){
  for(const course of G.civicTraining.slice(0,places)){course.days+=publicCivicCoverage('school',G.people[course.person].hh);if(course.days>=120){const p=G.people[course.person];p.skill=Math.min(1.3,p.skill+.1);course.complete=true;G.civicTrainingCompletions=(G.civicTrainingCompletions||0)+1;story(p.name+' completed a funded adult-training term. Qualification grows through sustained teaching, not an instant grant.','good',0,p.hh);}}
  G.civicTraining=G.civicTraining.filter(c=>!c.complete);
  const enrolled=new Set(G.civicTraining.map(c=>c.person));
  const access=serviceAccess('school'),reachable=new Set(access.households.filter(h=>h.served>0).map(h=>h.id));
  const candidates=G.people.filter(p=>reachable.has(p.hh)&&!p.deceased&&!p.movedAway&&p.age>=18&&p.age<=60&&p.skill<.7&&!enrolled.has(p.id)).sort((a,b)=>(a.job>=0)-(b.job>=0)||b.skill-a.skill||a.id-b.id);
  while(G.civicTraining.length<places&&candidates.length)G.civicTraining.push({person:candidates.shift().id,days:0,started:G.day});
 }
}
function validateCivicState(data){
 if(data.civicStaffing!=null){if(typeof data.civicStaffing!=='object'||Array.isArray(data.civicStaffing))return false;
  for(const [kind,c] of Object.entries(data.civicStaffing)){if(!['health','school'].includes(kind)||!c||!Number.isFinite(c.ready)||c.ready<0||c.ready>1000)return false;
   if(c.pending&&(!Number.isFinite(c.pending.target)||c.pending.target<0||c.pending.target>1000||!Number.isInteger(c.pending.day)||c.pending.day<1||c.pending.day>data.day+30))return false;}}
 if(data.civicTraining!=null){if(!Array.isArray(data.civicTraining)||data.civicTraining.length>data.people.length)return false;const seen=new Set();
  for(const c of data.civicTraining){if(!c||!Number.isInteger(c.person)||!data.people[c.person]||seen.has(c.person)||!Number.isFinite(c.days)||c.days<0||c.days>=120||!Number.isInteger(c.started)||c.started<1||c.started>data.day)return false;seen.add(c.person);}}
 if(data.civicTrainingLastDay!=null&&(!Number.isInteger(data.civicTrainingLastDay)||data.civicTrainingLastDay>data.day||data.civicTrainingLastDay<1))return false;
 return data.people.every(p=>[p.publicRole,p.previousPublicRole].every(role=>role==null||['','health','school'].includes(role)));
}
function civicTrainingPanel(){
 const courses=G.civicTraining||[];return head('Local qualifications and training')+tip('Each operating school offers two adult-training places. A term needs 120 equivalent funded teaching days and adds 10 skill points; partial coverage progresses more slowly. Regional staffing contracts provide a recovery path when no local qualified worker is available.')+(courses.length?courses.map(c=>{const p=G.people[c.person];return `<div class="entry"><strong>${esc(p.name)}</strong><small>${Math.floor(c.days)} / 120 funded days · Skill ${Math.round(p.skill*100)}/100</small><button data-house="${p.hh}">Inspect household</button></div>`;}).join(''):tip('No adult course is active. Fund reachable schools to open places.'));
}
