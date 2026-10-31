function tick(){if(!G||pendingEvent)return;ensureSystems();ensureMarketModel();G.day++;if(G.day%30===0){G.month++;if(G.month>12){G.month=1;G.year++}};
 regionalFreightDay();freightDay();completeEquipmentOrders();completeDevelopmentProjects();dailyEconomy();urbanMunicipalHousingDay();bankDaily();metroOperatingDay();airfieldOperatingDay();incidents();investigateCases();extendedCivicDay();maintainRoads();finalizeMarketBooks();if(G.day%30===0&&G.debt>0){const interest=G.debt*((G.policy.policyRate||0)/100+.015)/12,paid=Math.min(G.treasury,interest);G.treasury-=paid;G.region+=paid;G.debt+=interest-paid;story('Interest on municipal borrowing: '+money(interest)+'.')}if(G.day%10===0)assignJobs();if(G.day%30===0)privateInvestmentAndHousing();

 if(G.day%30===0){outwardMigration();autonomousDevelopment();}
 migrationFamilyArrivalDay();

 recompute();updateCouncilAndMissions();systemsDay();
 if(G.day%30===0)monthlyReview();
 if(G.day%360===0){yearlyDemographics();electionReview();}
 if(!pendingEvent&&G.day%45===0&&G.day-G.lastEventDay>=37)offerCouncilEvent();
 // Publish and save one canonical end-of-day snapshot after demographic and civic changes.
 recompute();G.stats.approval=Math.round(G.council.approval);G.rngState=rngState;
 privateServiceInvestmentDay();districtProgrammeDay();urbanEvolutionDay();migrationTenancyDay();updateScenarioProgramme();mayorJourneyDay();civicProjectsDay();civicCampaignDay();G.rngState=rngState;if(G.day%10===0)recordObservation();
 G.history.push({day:G.day,employment:G.stats.employment,hardship:G.stats.hardship,safety:G.stats.safety,treasury:Math.round(G.treasury),businesses:G.stats.businesses,deposits:(G.banks||[]).reduce((n,b)=>n+bankDeposits(b.id),0),crime:G.stats.dailyCrime,approval:G.council.approval,education:G.education,health:G.health});if(G.history.length>240)G.history.shift();
 if(G.day%60===0){const signal=marketSignal();if(signal.kind!=='normal'&&signal.title!==G.lastEconomicSignal){story(signal.title+'. '+signal.description,signal.kind==='good'?'good':'bad');G.lastEconomicSignal=signal.title;}}
 // Autosaves are scheduled in wall time by the frame controller.
 dirty=true;
}

// Experimental continuation: tick above remains the unchanged synchronous oracle.
function* stagedTick(){if(!G||pendingEvent)return;ensureSystems();yield 'ensureSystems';ensureMarketModel();yield 'ensureMarketModel';G.day++;if(G.day%30===0){G.month++;if(G.month>12){G.month=1;G.year++}};
 regionalFreightDay();yield 'regionalFreightDay';freightDay();yield 'freightDay';completeEquipmentOrders();yield 'completeEquipmentOrders';completeDevelopmentProjects();yield 'completeDevelopmentProjects';dailyEconomy();yield 'dailyEconomy';urbanMunicipalHousingDay();yield 'urbanMunicipalHousingDay';bankDaily();yield 'bankDaily';metroOperatingDay();yield 'metroOperatingDay';airfieldOperatingDay();yield 'airfieldOperatingDay';incidents();yield 'incidents';investigateCases();yield 'investigateCases';extendedCivicDay();yield 'extendedCivicDay';maintainRoads();yield 'maintainRoads';finalizeMarketBooks();yield 'finalizeMarketBooks';if(G.day%30===0&&G.debt>0){const interest=G.debt*((G.policy.policyRate||0)/100+.015)/12,paid=Math.min(G.treasury,interest);G.treasury-=paid;G.region+=paid;G.debt+=interest-paid;story('Interest on municipal borrowing: '+money(interest)+'.')}if(G.day%10===0){assignJobs();yield 'assignJobs';}if(G.day%30===0){privateInvestmentAndHousing();yield 'privateInvestmentAndHousing';}

 if(G.day%30===0){yield* stagedOutwardMigration();yield 'outwardMigration';autonomousDevelopment();yield 'autonomousDevelopment';}
 migrationFamilyArrivalDay();yield 'migrationFamilyArrivalDay';

 recompute();yield 'recompute';updateCouncilAndMissions();yield 'updateCouncilAndMissions';systemsDay();yield 'systemsDay';
 if(G.day%30===0){monthlyReview();yield 'monthlyReview';}
 if(G.day%360===0){yearlyDemographics();yield 'yearlyDemographics';electionReview();yield 'electionReview';}
 if(!pendingEvent&&G.day%45===0&&G.day-G.lastEventDay>=37)offerCouncilEvent();
 // Publish and save one canonical end-of-day snapshot after demographic and civic changes.
 recompute();yield 'recompute';G.stats.approval=Math.round(G.council.approval);G.rngState=rngState;
 privateServiceInvestmentDay();yield 'privateServiceInvestmentDay';districtProgrammeDay();yield 'districtProgrammeDay';urbanEvolutionDay();yield 'urbanEvolutionDay';migrationTenancyDay();yield 'migrationTenancyDay';updateScenarioProgramme();yield 'updateScenarioProgramme';mayorJourneyDay();yield 'mayorJourneyDay';civicProjectsDay();yield 'civicProjectsDay';civicCampaignDay();yield 'civicCampaignDay';G.rngState=rngState;if(G.day%10===0){recordObservation();yield 'recordObservation';}
 G.history.push({day:G.day,employment:G.stats.employment,hardship:G.stats.hardship,safety:G.stats.safety,treasury:Math.round(G.treasury),businesses:G.stats.businesses,deposits:(G.banks||[]).reduce((n,b)=>n+bankDeposits(b.id),0),crime:G.stats.dailyCrime,approval:G.council.approval,education:G.education,health:G.health});if(G.history.length>240)G.history.shift();
 if(G.day%60===0){const signal=marketSignal();if(signal.kind!=='normal'&&signal.title!==G.lastEconomicSignal){story(signal.title+'. '+signal.description,signal.kind==='good'?'good':'bad');G.lastEconomicSignal=signal.title;}}
 // Autosaves are scheduled in wall time by the frame controller.
 dirty=true;
}

function resetTownTransientUI(){
 cancelTransitDraft();resetTransitForecasts();transitTopologyCache=null;transitDailyCache=null;
 clearTimeout(toastTimeout);toastTimeout=0;$('toast').style.display='none';pendingEvent=null;$('eventDialog').style.display='none';councilOpener=null;panelOpener=null;parcelFocus=null;selected=null;inspectedTrip=null;buildMode='';pointer.down=false;pointer.activeId=null;pointer.hover=null;touches.clear();roadPainted.clear();$('placementHint').style.display='none';$('hint').textContent='DRAG TO PAN · TAP TO INSPECT · PINCH TO ZOOM';
}
function toast(msg){const el=$('toast');el.textContent=msg;el.style.display='block';clearTimeout(toastTimeout);toastTimeout=setTimeout(()=>el.style.display='none',3300)}
