// Finite source operations; all mutations execute inside the shared paid root.
const transitFreightId={type:'integer',min:0,max:9007199254740991};
function transitFreightDone(ctx,ok,text){if(!ok)ctx.refuse(text);ctx.save();return {completed:true};}
registerWorkerRouteModule({version:1,id:'transit-freight',operations:{
 'routing':{mode:'command',fields:{value:{type:'enum',values:['automatic','interchange','depots','river']}},execute(p,ctx){const s=ensureRegionalTrade();if((s.routePreference||'automatic')===p.value)ctx.refuse('Routing preference is unchanged.');s.routePreference=p.value;ctx.save();return {value:p.value};}},
 'priority':{mode:'command',fields:{value:{type:'enum',values:['balanced','essentials','contracts']}},execute(p,ctx){const s=ensureRegionalTrade();if(s.priority===p.value)ctx.refuse('Dispatch priority is unchanged.');s.priority=p.value;ctx.save();return {value:p.value};}},
 'stop-relief':{mode:'command',fields:{},execute(p,ctx){const s=ensureRegionalTrade();if(!s.reliefUntil)ctx.refuse('No extra shift authorization remains.');s.reliefUntil=0;ctx.save();return {completed:true};}},
 'retire':{mode:'command',fields:{id:transitFreightId},execute(p,ctx){const result=transitFreightDone(ctx,deleteTransitRoute(p.id),'Route no longer exists.');ctx.notify('Route retired. Vehicles sold; stations and guideway retained.');return result;}},
 'remove-guideway':{mode:'command',fields:{},execute(p,ctx){const result=transitFreightDone(ctx,removeUnusedGuideway(),'No removable guideway remains.');ctx.notify('Unused guideway decommissioned. Used corridors were retained.');return result;}},
 'remove-site':{mode:'command',fields:{id:transitFreightId},execute(p,ctx){const result=transitFreightDone(ctx,removeTransitFacility(p.id),'Site is missing or in use.');ctx.notify('Unused site removed. Salvage returned to the treasury.');return result;}}
}});
