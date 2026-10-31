// Controlled stress-town authoring. Every fixture capital transfer conserves cash;
// household relocation is authored test data, not a claimed player playthrough.
window.__liveNetworkBuild=()=>{
 const before=totalMoney(),funds=Math.min(G.region,6000000);G.region-=funds;G.treasury+=funds;
 while(G.charter.owned.length<ANNEX_PARCELS.length){const p=ANNEX_PARCELS.find(p=>!G.charter.owned.includes(p.id)&&parcelAdjacent(p));if(!p||!purchaseParcel(p.id,parcelSurvey(p).price))throw Error('Live atlas purchase failed');}
 const corridor=[];for(let x=44;x<=55;x++)corridor.push([x,27]);for(let y=28;y<=32;y++)corridor.push([55,y]);for(let x=56;x<=120;x++)corridor.push([x,32]);
 for(const [x,y] of corridor)if(G.tiles[roadId(x,y)]!==1){construct('road',x,y,true);if(G.tiles[roadId(x,y)]!==1)throw Error('Live east road blocked at '+x+','+y);}invalidateRoads(false);roadBatchDirty=false;staticDirty=true;
 const relocated=[];for(let x=60;x<=116;x+=2){if(!canPlace(x,31,true,'home'))continue;const old=new Set(G.buildings.map(b=>b.id));construct('home',x,31);const home=G.buildings.find(b=>!old.has(b.id));if(!home)continue;const h=G.households[100+relocated.length],origin=readBuild(h.home);if(origin?.hh===h.id)origin.hh=-1;h.home=home.id;home.hh=h.id;relocated.push(h.id);}
 const depotLot=buildableCandidates('business').find(p=>canPlace(p.x,p.y,true,'transit_depot')),depot=depotLot&&buildTransitFacility('transit_depot',depotLot.x,depotLot.y);if(!depot)throw Error('Live depot missing');
 const drivers=G.people.filter(p=>p.job<0&&p.age>=18&&p.age<=70&&graph().portals.has(G.households[p.hh]?.home)&&roadDistance(graph().portals.get(G.households[p.hh].home),graph().portals.get(depot.id))<=20).slice(0,28);for(const p of drivers){if(G.firms[p.job])G.firms[p.job].workers=G.firms[p.job].workers.filter(id=>id!==p.id);p.job=-1;p.skill=.8;p.previousPublicRole='';p.searchAfter=G.day+1000;}
 const a=buildTransitFacility('elevated_station',59,31),b=buildTransitFacility('elevated_station',119,33);if(!a||!b)throw Error('Live rail platforms missing');
 const specs=[{mode:'bus',depot:depot.id,stops:[roadId(15,27),roadId(27,27),roadId(43,27)],level:2},{mode:'bus',depot:depot.id,stops:[roadId(15,27),roadId(35,27),roadId(55,27),roadId(75,32),roadId(95,32),roadId(119,32)],level:2},{mode:'elevated',depot:depot.id,stops:[a.id,b.id],level:2}];
 const routes=specs.map(spec=>{const quote=transitQuote(spec),r=buildTransitRoute(spec,quote);if(!r)throw Error('Live route failed: '+JSON.stringify(quote));return r.id;});
 invalidateUrban();invalidateBuildingIndex();invalidateRoads(false);recompute();if(Math.abs(totalMoney()-before)>.001)throw Error('Live authoring cash drift');
 return {grid:T,deeds:G.charter.owned.length,relocatedHouseholds:relocated.length,routes,capital:G.transit.capital,total:totalMoney()};
};

window.__liveNetworkStatus=()=>({routes:G.transit.routes.length,operating:G.transit.routes.filter(r=>r.stats.operating).length,rides:G.transit.daily.rides,fares:G.transit.fares,staff:G.transit.daily.staff,capacity:G.transit.routes.reduce((n,r)=>n+r.stats.capacity,0),musicPlaying:musicDecks.filter(d=>!d.audio.paused&&d.audio.currentTime>0).length,musicReferencedDecks:musicDecks.length});
