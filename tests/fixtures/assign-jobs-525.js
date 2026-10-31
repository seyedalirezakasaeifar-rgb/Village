function referenceAssignJobs(){
 if(!G||!G.people)return;
 const free=G.people.filter(p=>!p.deceased&&p.movedAway!==true&&p.age>=16&&p.age<=70&&p.job<0&&!p.publicWork&&!p.previousPublicRole&&(p.searchAfter||0)<=G.day);
 const net=graph(),maxJourney=60+(G.transit?.routes.length?0:(G.policy.transitBudget||0)/8);
 const vacancies=G.firms.filter(f=>!f.closed&&f.workers.length<f.jobs).sort((a,b)=>(b.wage-a.wage));
 for(const f of vacancies){let workplace=readBuild(f.building),port=net.portals.get(f.building);
  if(!workplace||port==null)continue;
  while(f.workers.length<f.jobs&&free.length){let best=-1,score=Infinity;
   for(let i=0;i<free.length;i++){const candidate=free[i],hh=G.households[candidate.hh],home=hh&&readBuild(hh.home);
    if(!home||f.privateService&&!privateQualified(candidate,f))continue;const hport=net.portals.get(home.id);if(hport==null||net.parts[hport]!==net.parts[port])continue;
    const distance=roadDistance(hport,port);
    if(distance>maxJourney&&!hasMetroCommute(home,workplace)&&!transitAccess(home,workplace))continue;
    const mismatch=Math.abs(candidate.skill-.7)*3,rank=distance*.74+mismatch+candidate.id*.00001;
    if(rank<score){score=rank;best=i}
   }
   if(best<0)break;const person=free.splice(best,1)[0];person.job=f.id;person.commuteBlockedDays=0;person.commuteBlocked=false;f.workers.push(person.id);
  }
 }
}
