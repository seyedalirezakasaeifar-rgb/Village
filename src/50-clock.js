function tick(){if(!G||pendingEvent)return;ensureSystems();ensureMarketModel();G.day++;if(G.day%30===0){G.month++;if(G.month>12){G.month=1;G.year++}};
 freightDay();completeEquipmentOrders();completeDevelopmentProjects();dailyEconomy();bankDaily();metroOperatingDay();airfieldOperatingDay();incidents();investigateCases();extendedCivicDay();maintainRoads();finalizeMarketBooks();if(G.day%30===0&&G.debt>0){const interest=G.debt*((G.policy.policyRate||0)/100+.015)/12,paid=Math.min(G.treasury,interest);G.treasury-=paid;G.region+=paid;G.debt+=interest-paid;story('Interest on municipal borrowing: '+money(interest)+'.')}if(G.day%10===0)assignJobs();if(G.day%30===0)privateInvestmentAndHousing();

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
 updateScenarioProgramme();if(G.day%10===0)recordObservation();
 G.history.push({day:G.day,employment:G.stats.employment,hardship:G.stats.hardship,safety:G.stats.safety,treasury:Math.round(G.treasury),businesses:G.stats.businesses,deposits:(G.banks||[]).reduce((n,b)=>n+bankDeposits(b.id),0),crime:G.stats.dailyCrime,approval:G.council.approval,education:G.education,health:G.health});if(G.history.length>240)G.history.shift();
 if(G.day%60===0){const signal=marketSignal();if(signal.kind!=='normal'&&signal.title!==G.lastEconomicSignal){story(signal.title+'. '+signal.description,signal.kind==='good'?'good':'bad');G.lastEconomicSignal=signal.title;}}
 // Autosaves are scheduled in wall time by the frame controller.
 dirty=true;
}

function save(){if(!G||simulationBusy)return;let payload;try{payload=archivePayload()}catch(e){autoSaveOK=false;return}try{const key='townledger-v6';const prev=localStorage.getItem(key);if(prev){let valid=false;try{const e=JSON.parse(prev);valid=e.checksum===checksum(e.payload)}catch(_){}if(valid){localStorage.removeItem('townledger-village-founder-3');localStorage.setItem(key+'-backup',prev);}}localStorage.setItem(key,JSON.stringify({checksum:checksum(payload),payload}));localStorage.removeItem('townledger-village-founder-3');autoSaveOK=true;}catch(e){autoSaveOK=false;}if(window.indexedDB)writeIndexedDB(payload);}
function load(){try{for(const key of ['townledger-v6','townledger-v6-backup']){try{const e=JSON.parse(localStorage.getItem(key)||'null');if(e&&e.checksum===checksum(e.payload)&&hydrateSave(e.payload))return true;}catch(_){}}let s=localStorage.getItem('townledger-village-founder-3')||localStorage.getItem('townledger-village-civic-2');if(!s)return false;return hydrateSave(s)}catch(e){return false}}
function resetTownTransientUI(){
 clearTimeout(toastTimeout);toastTimeout=0;$('toast').style.display='none';pendingEvent=null;$('eventDialog').style.display='none';councilOpener=null;panelOpener=null;selected=null;inspectedTrip=null;buildMode='';pointer.down=false;pointer.activeId=null;pointer.hover=null;touches.clear();roadPainted.clear();$('placementHint').style.display='none';$('hint').textContent='DRAG TO PAN · TAP TO INSPECT · PINCH TO ZOOM';
}
function toast(msg){const el=$('toast');el.textContent=msg;el.style.display='block';clearTimeout(toastTimeout);toastTimeout=setTimeout(()=>el.style.display='none',3300)}
