// Trusted routes only: all mutations join the registry's single paid root.
// Review stamps stay worker-local and participate in the registered graph rollback.
function landRouteReview(ctx,work,metadata){
 const previous=pendingEvent;ctx.review(work);
 if(!pendingEvent||pendingEvent===previous)ctx.refuse('No current proposal is available. Review the actual prerequisites.');
 pendingEvent.landRoute={...metadata,day:G.day,roads:roadsVersion};
 return {review:pendingEvent.workerId};
}
function landRouteSettle(review,ctx){
 const meta=review.event.landRoute,c=review.choice,q=c.command;
 if(meta?.custom){ctx.applyChoice(review,{validate:()=>review.index!==0||meta.validate(),verify:()=>review.index!==0||meta.verify()});return {settled:true,cancelled:review.index!==0};}
 if(!meta)ctx.refuse('This proposal has no current land review.');
 const cancel=q?.action==='cancel'||review.index===1;
 const current=()=>{
  if(cancel)return true;
  if(meta.day!==G.day||meta.roads!==roadsVersion)return false;
  if(meta.kind==='parcel'){const parcel=ANNEX_PARCELS.find(p=>p.id===meta.parcel);return !!parcel&&!G.charter.owned.includes(meta.parcel)&&parcelAdjacent(parcel)&&parcelSurvey(parcel).price===meta.price&&G.treasury>=meta.price;}
  if(meta.kind==='focus'){const old=G.districtProgrammes?.[meta.parcel];return G.charter.owned.includes(meta.parcel)&&owns(DISTRICT_FOCI,meta.focus)&&JSON.stringify(old||null)===meta.prior&&(!old||G.day-old.started>=30)&&old?.focus!==meta.focus&&G.treasury>=(old?1200:0);}
  if(meta.kind==='road'){const fresh=roadRemovalQuote(meta.x,meta.y);return fresh.ok&&fresh.key===meta.key&&G.treasury>=fresh.cost;}
  if(meta.kind==='bridge-repair'){const fresh=bridgeRepairQuote(meta.id);return fresh.ok&&fresh.cost>0&&fresh.key===meta.key&&G.treasury>=fresh.cost;}
  if(meta.kind==='bridge-remove'){const fresh=bridgeRemovalQuote(meta.id);return fresh.ok&&fresh.key===meta.key;}
  if(meta.kind==='bridge-build'){const fresh=bridgeCandidateFromBank(meta.bank);return fresh.ok&&fresh.key===meta.key&&G.treasury>=fresh.cost;}
  return false;
 };
 ctx.applyChoice(review,{validate:current,verify:()=>{
  if(cancel)return true;
  if(meta.kind==='parcel')return G.charter.owned.includes(meta.parcel)&&G.charter.deeds.some(d=>d.id===meta.parcel&&d.price===meta.price);
  if(meta.kind==='focus')return G.districtProgrammes?.[meta.parcel]?.focus===meta.focus&&G.districtProgrammes[meta.parcel].started===G.day;
  if(meta.kind==='road')return G.tiles[roadId(meta.x,meta.y)]===0;
  if(meta.kind==='bridge-repair')return G.bridges.some(b=>b.id===meta.id&&b.condition===100);
  if(meta.kind==='bridge-remove')return !G.bridges.some(b=>b.id===meta.id);
  if(meta.kind==='bridge-build')return G.bridges.some(b=>b.banks.includes(meta.bank)&&b.builtDay===G.day);
  return false;
 }});
 return {settled:true,cancelled:cancel};
}
function landRoutePaidReview(ctx,spec){
 const meta={custom:true,validate:spec.validate,verify:()=>meta.result?.ok===true&&(!spec.verify||spec.verify()),result:null};
 const result=landRouteReview(ctx,()=>showCustomEvent(spec.type,spec.title,spec.text,[{title:spec.confirm,cost:spec.cost||0,apply:()=>{meta.result=spec.work();if(meta.result?.ok!==true)ctx.refuse(meta.result?.reason||'The reviewed work could not be completed.');ctx.notify(meta.result.reason||'The reviewed work completed.');updateHeader();if(active)renderPanel(active);}},{title:spec.cancel||'Keep the current site',apply:()=>{}}]),meta);
 pendingEvent.landRoute=meta;return result;
}
function landRouteClearance(ctx,x,y){const q=urbanClearanceQuote(x,y);if(!q.ok)ctx.refuse(q.reason);const key=urbanClearanceQuoteKey(q),b=q.building&&readBuild(q.building),target=b?types[b.kind].n+' at grid ('+x+', '+y+')':'crop title at grid ('+x+', '+y+')';return landRoutePaidReview(ctx,{type:'LAND ASSEMBLY',title:'Clear '+target+'?',text:`Target: ${target}. ${q.reason} Owner/crop compensation ${money(q.compensation)}, clearance ${money(q.demolition)}, relocation ${money(q.relocation||0)}, severance ${money(q.severance||0)}. Total ${money(q.total)}. The land becomes vacant; fund its replacement separately.`,confirm:'Pay compensation and clear the site',cancel:'Keep this property',cost:q.total,validate:()=>{const fresh=urbanClearanceQuote(x,y);return fresh.ok&&urbanClearanceQuoteKey(fresh)===key&&G.treasury>=q.total;},work:()=>urbanClearance(x,y,q.total,urbanClearanceReviewKey(q)),verify:()=>!q.building||!readBuild(q.building)});}
const landExtraOperations={
 'urban-plan':{mode:'preview',fields:{building:{type:'integer',min:0,max:9007199254740991},plan:{type:'enum',values:Object.keys(URBAN_PLANS)}},execute(p,ctx){const b=readBuild(p.building);if(!b)ctx.refuse('The property no longer exists.');const {x,y}=b,key=urbanBlockKey(x,y),prior=JSON.stringify(ensureUrban().zones[key]||null),d=urbanDescriptor(x,y),cost=ensureUrban().zones[key]?1800:600;if(d.plan===p.plan)ctx.refuse('This plan is already recorded.');return landRoutePaidReview(ctx,{type:'URBAN PLANNING',title:URBAN_PLANS[p.plan],text:`Target ${d.name}, the 8 × 8 neighbourhood centered at grid (${x}, ${y}). Current plan: ${URBAN_PLANS[d.plan]}. Pay ${money(cost)} for this survey and public-register entry. Existing private property remains legal. Revisions require 90 days.`,confirm:'Record the neighbourhood plan',cost,validate:()=>readBuild(b.id)?.x===x&&readBuild(b.id)?.y===y&&JSON.stringify(ensureUrban().zones[key]||null)===prior&&G.treasury>=cost,work:()=>urbanPlanChange(x,y,p.plan),verify:()=>ensureUrban().zones[key]?.plan===p.plan});},settle:landRouteSettle},
 'urban-rehousing':{mode:'preview',fields:{},execute(p,ctx){const q=urbanRehousingQuote();if(!q.ok)ctx.refuse(q.reason);return landRoutePaidReview(ctx,{type:'URBAN PLANNING',title:'Commission a reserved replacement home?',text:q.reason+' Pay '+money(q.cost)+' for '+q.days+' funded workdays, subject to actual crew/material access. Occupied municipal replacement homes charge at most 25% of after-tax household income and require actual municipal upkeep.',confirm:'Commission the vacant home',cost:q.cost,validate:()=>G.treasury>=q.cost&&canPlace(q.x,q.y,true,'home'),work:()=>commissionUrbanRehousing(q),verify:()=>G.projects.some(v=>v.municipalRehousing&&readBuild(v.id)?.x===q.x&&readBuild(v.id)?.y===q.y)});},settle:landRouteSettle},
 'urban-clear':{mode:'preview',fields:{building:{type:'integer',min:0,max:9007199254740991}},execute(p,ctx){const b=readBuild(p.building);if(!b)ctx.refuse('The property no longer exists.');return landRouteClearance(ctx,b.x,b.y);},settle:landRouteSettle},
 'urban-clear-map':{mode:'preview',fields:{x:{type:'integer',min:0,max:T-1},y:{type:'integer',min:0,max:T-1}},execute(p,ctx){return landRouteClearance(ctx,p.x,p.y);},settle:landRouteSettle},
 'urban-clear-tool':{mode:'preview',fields:{},execute(p,ctx){ctx.present({kind:'build-tool',tool:'urban_clearance'});return {tool:'urban_clearance'};}},
 'urban-farm-renew':{mode:'preview',fields:{firm:{type:'integer',min:0,max:9007199254740991}},execute(p,ctx){const q=urbanFarmRenewalQuote(p.firm);if(!q.ok)ctx.refuse(q.reason);const old={...readBuild(q.building)},result=landRouteReview(ctx,()=>reviewUrbanFarmRenewal(p.firm),{});pendingEvent.landRoute={custom:true,validate:()=>{const fresh=urbanFarmRenewalQuote(p.firm);return fresh.ok&&fresh.reviewKey===q.reviewKey;},verify:()=>{const b=readBuild(q.building);return !!b&&b.x===q.destination.x&&b.y===q.destination.y&&G.firms[p.firm]?.building===b.id&&G.projects.some(v=>v.urbanRenewal&&readBuild(v.id)?.x===old.x&&readBuild(v.id)?.y===old.y);}};return result;},settle:landRouteSettle}
};

const landRouteId={type:'integer',min:0,max:9007199254740991},landRouteCoord={type:'integer',min:0,max:T-1},landRouteParcel={type:'enum',values:ANNEX_PARCELS.map(p=>p.id)};
registerWorkerRouteModule({version:1,id:'land-district',operations:{...landExtraOperations,
 'parcel-buy':{mode:'preview',fields:{parcel:landRouteParcel},execute(p,ctx){const parcel=ANNEX_PARCELS.find(v=>v.id===p.parcel);if(G.charter.owned.includes(p.parcel)||!parcelAdjacent(parcel))ctx.refuse('This adjoining deed is no longer available.');return landRouteReview(ctx,()=>requestParcelPurchase(p.parcel),{kind:'parcel',parcel:p.parcel,price:parcelSurvey(parcel).price});},settle:landRouteSettle},
 'district-focus':{mode:'preview',fields:{parcel:landRouteParcel,focus:{type:'enum',values:Object.keys(DISTRICT_FOCI)}},execute(p,ctx){const old=G.districtProgrammes?.[p.parcel];if(!G.charter.owned.includes(p.parcel)||old&&(old.focus===p.focus||G.day-old.started<30))ctx.refuse('The district charter is unchanged or still within its revision interval.');return landRouteReview(ctx,()=>showCustomEvent('DISTRICT PLANNING',DISTRICT_FOCI[p.focus].name,DISTRICT_FOCI[p.focus].description+' Existing properties remain legal. Revisions are available after30 days and cost$1,200.',[{title:'Record district charter',cost:0,apply:()=>chooseDistrictFocus(p.parcel,p.focus)}]),{kind:'focus',parcel:p.parcel,focus:p.focus,prior:JSON.stringify(old||null)});},settle:landRouteSettle},
 'district-budget':{mode:'preview',fields:{key:{type:'enum',values:['educationBudget','healthBudget']}},execute(p,ctx){ctx.openPanel('policies');ctx.present({kind:'focus-policy',key:p.key});return {policy:p.key};}},
 'civic-watch-project':{mode:'preview',fields:{project:landRouteId},execute(p,ctx){const project=G.civicProjects?.active.district;if(!project||project.id!==p.project)ctx.refuse('This district project is no longer current.');openCivicProjects('district');return {project:project.id};}},
 'road-remove-tool':{mode:'preview',fields:{},execute(p,ctx){ctx.present({kind:'build-tool',tool:'road_remove'});return {tool:'road_remove'};}},
 'road-remove-review':{mode:'preview',fields:{x:landRouteCoord,y:landRouteCoord},execute(p,ctx){const q=roadRemovalQuote(p.x,p.y);if(!q.ok)ctx.refuse(q.reason);return landRouteReview(ctx,()=>reviewRoadRemoval(p.x,p.y),{kind:'road',x:p.x,y:p.y,key:q.key});},settle:landRouteSettle},
 'bridge-repair':{mode:'preview',fields:{id:landRouteId},execute(p,ctx){const q=bridgeRepairQuote(p.id);if(!q.ok||q.cost<=0)ctx.refuse(q.reason||'This bridge is already structurally sound.');return landRouteReview(ctx,()=>reviewBridgeRepair(p.id),{kind:'bridge-repair',id:p.id,key:q.key});},settle:landRouteSettle},
 'bridge-remove':{mode:'preview',fields:{id:landRouteId},execute(p,ctx){const q=bridgeRemovalQuote(p.id);if(!q.ok)ctx.refuse(q.reason);return landRouteReview(ctx,()=>reviewBridgeRemoval(p.id),{kind:'bridge-remove',id:p.id,key:q.key});},settle:landRouteSettle},
 'bridge-build-tool':{mode:'preview',fields:{},execute(p,ctx){ctx.present({kind:'build-tool',tool:'road_bridge'});return {tool:'road_bridge'};}},
 'bridge-review':{mode:'preview',fields:{x:landRouteCoord,y:landRouteCoord},execute(p,ctx){const bank=roadId(p.x,p.y),q=bridgeCandidateFromBank(bank);if(!q.ok)ctx.refuse(q.reason);return landRouteReview(ctx,()=>reviewRoadBridge(bank),{kind:'bridge-build',bank,key:q.key});},settle:landRouteSettle}
}});
