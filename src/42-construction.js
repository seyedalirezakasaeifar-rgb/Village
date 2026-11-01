// A day of work requires a crew and materials; elapsed time alone cannot finish a site.
let crewDay=-1,crewsUsed=new Map(),regionalCrews=0;
function constructionWork(project){
 if(project.kind==='fields')return true;
 if(crewDay!==G.day){crewDay=G.day;crewsUsed=new Map();regionalCrews=0;}
 const builders=G.firms.filter(f=>f.kind==='contractor'&&!f.closed&&f.workers.length>=2&&f.cash>50);
 const builder=builders.find(f=>(crewsUsed.get(f.id)||0)<Math.max(1,Math.floor(f.workers.length/2)));
 if(!builder){
  // External crews are part of the already-paid regional construction contract.
  if(!G.policy.imports||regionalCrews>=2){project.stalledDays=(project.stalledDays||0)+1;project.reason='No funded construction crew available';return false;}
  regionalCrews++;project.builder='Regional construction service';project.workedDay=G.day;project.reason='Paid external crew working';return true;
 }
 crewsUsed.set(builder.id,(crewsUsed.get(builder.id)||0)+1);
 const scale=project.kind==='airport'?5:project.target==='tower'?3:project.kind==='redevelop'?2:1;
 const timber=.6*scale,stone=.35*scale;
 if((builder.stock.timber||0)<timber*4)trade(builder,'timber',timber*10-(builder.stock.timber||0));
 if((builder.stock.stone||0)<stone*4)trade(builder,'stone',stone*10-(builder.stock.stone||0));
 project.builder=builder.name;
 if((builder.stock.timber||0)<timber||(builder.stock.stone||0)<stone){project.stalledDays=(project.stalledDays||0)+1;project.reason='Waiting for paid timber or stone deliveries';return false;}
 builder.pendingCogs=(builder.pendingCogs||0)+takeInventory(builder,'timber',timber)+takeInventory(builder,'stone',stone);goodsEntry('timber','consumed',timber);goodsEntry('stone','consumed',stone);
 project.workedDay=G.day;project.reason='Crew and materials available';return true;
}
function birthsAndGenerations(){
 if(G.day%90!==0||G.stats.population>=2000)return;
 let count=0;
 for(const h of G.households){
  if(creatorCapacityReason(1))break;
  if(!h.people.length||h.people.length>=6||h.stress>48||G.day-(h.lastBirth||-720)<720)continue;
  const people=h.people.map(id=>G.people[id]).filter(p=>!p.deceased&&!p.movedAway),adults=people.filter(p=>p.age>=20&&p.age<=42);
  if(!adults.length||people.filter(p=>p.age<16).length>=2||!people.some(p=>p.job>=0))continue;
  const savings=h.cash+Object.values(h.deposits||{}).reduce((n,a)=>n+a,0);
  const security=clamp((savings/Math.max(1,h.people.length)-400)/3500,0,1),cost=clamp(1-(G.housingMarket.rentIndex-1)*.5,.35,1.15);
  if(random()>.085*security*cost)continue;
  const id=G.people.length,p={id,name:pick(first)+' '+h.name,age:0,skill:.05,health:94,hh:h.id,job:-1,life:80,last:[]};
  G.people.push(p);h.people.push(id);migrationRecord('birth',{household:h.id,person:id,people:1});h.lastBirth=G.day;count++;if(G.stats.population+count>=2000)break;
 }
 if(count)story(count+' '+(count===1?'child was':'children were')+' born in local households. Family finances, housing and confidence influence household formation.','good');
}
