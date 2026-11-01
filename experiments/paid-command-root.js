// Paid-command layer. Uses ONLY __capacityAdmissionProtocol.shared; no own root.
(function(){
 window.__installPaidCommandLayer=function(adapter=window.__gameCapacityRoot){
  const protocol=window.__capacityAdmissionProtocol,shared=protocol.shared;if(window.__paidRootPrototype)throw Error('Do not stack the old silent-refusal prototype');
  if(window.__rootAdmission){if(window.__rootAdmission.shared!==shared)throw Error('A competing root controller is already installed');return window.__rootAdmission;}
  if(shared.isActive()||shared.status().pendingSaveGenerations)throw Error('Attach paid operations while the shared root is idle and drained');protocol.installFences(shared);
  const game=adapter||{shared,metrics:()=>({last:null}),registerRuntime:()=>{throw Error('Use the selected owner runtime registry');}};if(game.shared!==shared)throw Error('Paid operations require the one shared controller');let last=null;const originalToast=toast,originalHeader=updateHeader,originalExport=exportSave;
  class PaidRefusal extends Error{}
  const refuse=reason=>shared.refuse(reason);
  function effect(fn){if(!shared.isActive())return false;shared.afterCommit(null,fn);return true;}
  function run(command,work){
   if(!command||typeof command.kind!=='string'||typeof work!=='function'||work.constructor?.name==='AsyncFunction')throw Error('A structured root command is required');
   const joined=shared.isActive(),start=performance.now();
   try{const result=shared.run(command.kind==='day'?'day':'command',()=>{try{return work();}catch(error){if(error instanceof PaidRefusal)shared.refuse(error.message);throw error;}},command);
    if(!joined){const m=game.metrics().last||{};last={...result,...m,command:command.kind,ms:performance.now()-start,code:result.ok?undefined:/capacity|budget|archive/.test(result.reason||'')?'capacity':'refused',publicationErrors:shared.status().last?.effectErrors||[]};}return result;
   }catch(error){if(!joined)last={ok:false,command:command.kind,reason:error.message,unexpected:true,ms:performance.now()-start};throw error;}
  }
  function safeRun(command,work){try{return run(command,work);}catch(error){if(shared.isActive())throw error;return {ok:false,reason:'The operation failed. No changes were committed.',detail:error.message};}}
  toast=function(){const args=arguments;if(effect(()=>originalToast.apply(this,args)))return;return originalToast.apply(this,args);};
  updateHeader=function(){const args=arguments;if(effect(()=>originalHeader.apply(this,args)))return;return originalHeader.apply(this,args);};
  exportSave=function(){const args=arguments;if(effect(()=>originalExport.apply(this,args)))return;return originalExport.apply(this,args);};
  const isEnabled=()=>shared.status().enabled||shared.isHalted();
  function notifyRefusal(result){if(!result.ok){if(shared.isActive())shared.refuse(result.reason);originalToast(result.reason);}}
  const originalConstruct=construct,originalCompletion=completeDevelopmentProjects;
  construct=function(kind,x,y,quiet=false){if(!isEnabled())return originalConstruct.apply(this,arguments);if(kind==='inspect'||kind==='urban_plan'){if(shared.isActive())shared.refuse('Map review cannot run inside model work');return originalConstruct.apply(this,arguments);}if(quiet&&!shared.isActive()){originalToast('Road-stroke admission is not integrated in this disabled prototype.');return false;}const args=arguments,r=safeRun({kind:'construction',buildingKind:kind,x,y,quiet},()=>{const before=G.construction,value=originalConstruct.apply(this,args);if(G.construction===before)shared.refuse('The construction site or funding is no longer available.');return value;});if(!r.ok&&!quiet)notifyRefusal(r);return r.ok?r.value:false;};
  completeDevelopmentProjects=function(){if(!isEnabled())return originalCompletion.apply(this,arguments);const args=arguments,r=safeRun({kind:'project-completion'},()=>originalCompletion.apply(this,args));if(!r.ok)notifyRefusal(r);return r.ok?r.value:false;};
 function dispatchCouncilChoice(evt,c){
  const builtin=COUNCIL_EVENTS.some(event=>event.title===evt.title&&event.type===evt.type&&event.choices.includes(c)),construction=c.command?.type==='construction',owned=['land-purchase','named-place'].includes(c.command?.type);
  if(!builtin&&!construction&&!owned){const reason='This reviewed operation has no transaction descriptor yet. No changes were made.';if(shared.isActive())refuse(reason);return last={ok:false,code:'unsupported',reason};}
  return safeRun({kind:construction?'reviewed-construction':'council-choice',eventType:evt.type,eventTitle:evt.title,choiceTitle:c.title,cost:c.cost||0,commandType:c.command?.type,parcel:c.command?.parcel,...construction?{buildingKind:c.command.kind,x:c.command.x,y:c.command.y,projectKind:c.command.projectKind,projectId:c.command.projectId,quotedPrice:c.command.price}:{}},()=>{
   if(pendingEvent!==evt||!evt.choices.includes(c))throw new PaidRefusal('The council review changed. Open a fresh review.');
   if(owned){const q=c.command;if(q.town!==G)throw new PaidRefusal('The reviewed town changed.');
    if(q.type==='land-purchase'){const parcel=ANNEX_PARCELS.find(p=>p.id===q.parcel);if(!parcel||G.charter.owned.includes(q.parcel)||!parcelAdjacent(parcel)||parcelSurvey(parcel).price!==q.price||c.cost!==q.price||G.treasury<q.price)throw new PaidRefusal('The district deed, price or funds changed. Review it again.');}
    else{const name=typeof q.readName==='function'?q.readName():null;if(!['square','warehouse'].includes(q.kind)||typeof name!=='string'||!name.trim()||name.trim().length>48||publicPlaceState().places.length>=24||q.price!==buildCost[q.kind]||!canPlace(q.x,q.y,true,q.kind)||G.treasury<q.price||c.cost)throw new PaidRefusal('The place name, retained place ledger, site or funds changed. Review the place again.');}
    closeCouncilDialog();c.apply();
    if(q.type==='land-purchase'){if(typeof civicCampaignSync==='function'&&civicCampaignSync())save();effect(()=>playSfx('coin'));return {committed:true};}
   }else if(construction){if(c.cost)throw new PaidRefusal('Construction quote contains an unexpected outer charge.');const q=c.command,p=G.civicProjects?.active[q.projectKind],bp=q.blueprintSignature&&p?civicDistrictBlueprint(p,true):null;
    if(q.town!==G||!p||p.id!==q.projectId||q.price!==buildCost[q.kind]||bp&&civicBlueprintSignature(bp)!==q.blueprintSignature||!canPlace(q.x,q.y,true,q.kind)||G.treasury<q.price)throw new PaidRefusal('The site, plan or funds changed. Review the project again.');
    closeCouncilDialog();if(bp)p.sitePlans=civicBlueprintSites(bp);const id=G.nextId;construct(q.kind,q.x,q.y);const building=G.buildings.find(b=>b.id>=id&&b.kind===q.kind&&b.x===q.x&&b.y===q.y);if(!building)throw new PaidRefusal('No building was commissioned.');p.building=building.id;if(q.projectKind==='food')p.firm=building.firm;openPanel('agenda');effect(()=>document.querySelector('[data-project-card="'+q.projectKind+'"]')?.scrollIntoView({block:'start'}));
   }else{
    const goodsBefore=stockTotals(),fundsBefore=totalMoney();if(c.cost){if(G.treasury<c.cost)throw new PaidRefusal('Treasury cannot fund this council choice.');G.treasury-=c.cost;G.region+=c.cost;G.cumulative.spending+=c.cost;}
    c.apply();const goodsAfter=stockTotals();for(const key of Object.keys(goods)){const delta=goodsAfter[key]-goodsBefore[key];goodsEntry(key,delta>=0?'imports':'consumed',Math.abs(delta));}
    const funding=totalMoney()-fundsBefore;G.region-=funding;if(Math.abs(funding)>.001)book(funding>0?'Regional capital':'Council settlement',funding>0?'Council decision beneficiaries':'Regional capital',Math.abs(funding),'Explicit council programme settlement');
    G.journal.push({day:G.day,name:evt.title,message:c.title+'. '+(c.desc||''),baseline:{...G.stats,treasury:G.treasury}});story('COUNCIL DECISION: '+c.title+' — '+evt.title,'neutral');G.councilInbox=(G.councilInbox||[]).filter(e=>e.title!==evt.title);closeCouncilDialog();
   }
   recompute();updateHeader();if(active)renderPanel(active);save();dirty=true;if(typeof civicCampaignSync==='function'&&civicCampaignSync())save();effect(()=>playSfx(c.cost?'coin':'click'));return {committed:true};
  });
 }
 function routePanelControl(event,work){
  if(!isEnabled())return false;const button=event.target.closest('button,[data-ambition]');if(!button)return false;
  const ids=['enactPolicy','borrow','repay','toggleDevelopment'];const control=ids.includes(button.id)?button.id:button.hasAttribute('data-ambition')?'ambition':button.hasAttribute('data-private-invite')?'private-provider':null;if(!control)return false;
  event.stopPropagation();const intent={kind:'panel-control',control,...control==='private-provider'?{providerKind:button.dataset.privateInvite}:control==='ambition'?{ambition:button.dataset.ambition}:control==='enactPolicy'?{policy:{...draftPolicy}}:{}},result=safeRun(intent,()=>{const value=control==='private-provider'?invitePrivateProvider(button.dataset.privateInvite):work();effect(()=>playSfx(['enactPolicy','borrow','repay'].includes(control)?'coin':'click'));return value;});notifyRefusal(result);return true;
 }
 return window.__rootAdmission=Object.freeze({shared,enable:value=>shared.setEnabled(value),enabled:isEnabled,active:shared.isActive,inModel:()=>shared.phase()==='work',deferUI:effect,run,refuse,registerRuntime:game.registerRuntime,dispatchCouncilChoice,notifyRefusal,routePanelControl,status:()=>({enabled:isEnabled(),active:shared.isActive(),halted:shared.isHalted(),last,protocol:shared.status(),metrics:game.metrics()})});
 };
})();
