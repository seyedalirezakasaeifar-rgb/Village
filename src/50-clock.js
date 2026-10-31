function tick(){if(!G||pendingEvent)return;ensureSystems();ensureMarketModel();G.day++;if(G.day%30===0){G.month++;if(G.month>12){G.month=1;G.year++}};
 regionalFreightDay();freightDay();completeEquipmentOrders();completeDevelopmentProjects();dailyEconomy();urbanMunicipalHousingDay();bankDaily();metroOperatingDay();airfieldOperatingDay();incidents();investigateCases();extendedCivicDay();maintainRoads();finalizeMarketBooks();if(G.day%30===0&&G.debt>0){const interest=G.debt*((G.policy.policyRate||0)/100+.015)/12,paid=Math.min(G.treasury,interest);G.treasury-=paid;G.region+=paid;G.debt+=interest-paid;story('Interest on municipal borrowing: '+money(interest)+'.')}if(G.day%10===0)assignJobs();if(G.day%30===0)privateInvestmentAndHousing();

 if(G.day%30===0){outwardMigration();autonomousDevelopment();}
 if(G.day%45===0&&G.stats.population<2000){let success=G.stats.employment>88&&G.stats.hardship<35&&G.firms.some(f=>!f.closed&&f.workers.length<f.jobs);
   if(success&&G.homes.length>0&&random()<.5){let h=pick(G.households);if(h.people.length<4){let p={id:G.people.length,name:pick(first)+' '+h.name,age:Math.round(rn(18,42)),skill:rn(.3,1),health:rn(60,100),hh:h.id,job:-1,life:60,last:[]};G.people.push(p);h.people.push(p.id);story('A newcomer joined the '+h.name+' household.','good',h.home,h.id)}}
 }
 recompute();updateCouncilAndMissions();systemsDay();
 if(G.day%30===0)monthlyReview();
 if(G.day%360===0){yearlyDemographics();electionReview();}
 if(!pendingEvent&&G.day%45===0&&G.day-G.lastEventDay>=37)offerCouncilEvent();
 // Publish and save one canonical end-of-day snapshot after demographic and civic changes.
 recompute();G.stats.approval=Math.round(G.council.approval);G.rngState=rngState;
 privateServiceInvestmentDay();districtProgrammeDay();urbanEvolutionDay();updateScenarioProgramme();mayorJourneyDay();civicProjectsDay();G.rngState=rngState;if(G.day%10===0)recordObservation();
 G.history.push({day:G.day,employment:G.stats.employment,hardship:G.stats.hardship,unmetFood:G.market?.unmetFood||0,foodDisconnected:G.market?.foodDisconnected||0,foodNeed:G.market?.foodNeed||0,foodStaffCapacity:G.market?.foodStaffCapacity||0,foodSellableCapacity:G.market?.foodSellableCapacity||0,foodRetailStock:G.market?.foodRetailStock||0,safety:G.stats.safety,treasury:Math.round(G.treasury),businesses:G.stats.businesses,deposits:(G.banks||[]).reduce((n,b)=>n+bankDeposits(b.id),0),crime:G.stats.dailyCrime,approval:G.council.approval,education:G.education,health:G.health});if(G.history.length>240)G.history.shift();
 if(G.day%60===0){const signal=marketSignal();if(signal.kind!=='normal'&&signal.title!==G.lastEconomicSignal){story(signal.title+'. '+signal.description,signal.kind==='good'?'good':'bad');G.lastEconomicSignal=signal.title;}}
 // Autosaves are scheduled in wall time by the frame controller.
 dirty=true;
}

function resetTownTransientUI(){
 cancelTransitDraft();transitTopologyCache=null;transitDailyCache=null;
 clearTimeout(toastTimeout);toastTimeout=0;$('toast').style.display='none';pendingEvent=null;$('eventDialog').style.display='none';councilOpener=null;panelOpener=null;parcelFocus=null;selected=null;inspectedTrip=null;buildMode='';pointer.down=false;pointer.activeId=null;pointer.hover=null;touches.clear();roadPainted.clear();$('placementHint').style.display='none';$('hint').textContent='DRAG TO PAN · TAP TO INSPECT · PINCH TO ZOOM';
}
function toast(msg){const el=$('toast');el.textContent=msg;el.style.display='block';clearTimeout(toastTimeout);toastTimeout=setTimeout(()=>el.style.display='none',3300)}
