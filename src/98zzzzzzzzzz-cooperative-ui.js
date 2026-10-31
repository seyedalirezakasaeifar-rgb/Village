// Final wrappers encompass the existing renderer/UI decorators. Off by default.
for(const name of ['draw','updateHeader','renderPanel','refreshAmbience','toast']){
 const original=eval(name);eval(name+'=function(...args){return cooperativeEffect("'+name+'",original,args);}');
}
const cooperativeOriginalSave=save;
save=function(){return cooperativeDayBusy()?afterCommittedDay(()=>cooperativeOriginalSave()):cooperativeOriginalSave();};
const cooperativeOriginalArchive=archivePayload;
archivePayload=function(){finishCooperativeDaySync('synchronous export');return cooperativeOriginalArchive();};
const cooperativeOriginalHydrate=hydrateSave;
hydrateSave=function(...args){finishCooperativeDaySync('import');cooperativeToken++;return cooperativeOriginalHydrate(...args);};
const cooperativeOriginalSeed=seed;
seed=function(...args){finishCooperativeDaySync('founding');cooperativeToken++;return cooperativeOriginalSeed(...args);};
const cooperativeOriginalSuspend=window.__townArchive.suspend,cooperativeOriginalPrepareExit=window.__townArchive.prepareExit,cooperativeOriginalBack=window.__townArchive.back;
window.__townArchive.suspend=function(){finishCooperativeDaySync('native suspension');return cooperativeOriginalSuspend();};
window.__townArchive.prepareExit=function(){if(!cooperativeDayBusy())return cooperativeOriginalPrepareExit();hostSuspended=true;return afterCommittedDay(()=>cooperativeOriginalPrepareExit());};
window.__townArchive.back=function(){finishCooperativeDaySync('native Back');return cooperativeOriginalBack();};
window.addEventListener('beforeunload',()=>finishCooperativeDaySync('document unload'),{capture:true});
function cooperativeResolveTarget(record){
 if(record.target.isConnected)return record.target;if(record.id){const el=$(record.id);if(el)return el;}
 if(Object.keys(record.data).length)for(const el of document.querySelectorAll('button,input,select,[data-house],[data-firm],[data-inspect],[data-panel]'))if(el.tagName===record.tag&&Object.keys(record.data).every(k=>el.dataset[k]===record.data[k]))return el;
 throw Error('The control changed while the day completed. Select the current control again.');
}
let cooperativePanPreview=null;
function cooperativeClearPreview(){cv.style.transform='';cooperativePanPreview=null;for(const el of document.querySelectorAll('[data-cooperative-pending]')){el.removeAttribute('data-cooperative-pending');el.removeAttribute('aria-busy');}}
function cooperativePreviewInput(e,target){
 if(target===cv&&!buildMode&&!transitDraft){
  if(e.type==='pointerdown'&&!cooperativePanPreview)cooperativePanPreview={id:e.pointerId,x:e.clientX,y:e.clientY};
  if(e.type==='pointermove'&&cooperativePanPreview?.id===e.pointerId){const dx=e.clientX-cooperativePanPreview.x,dy=e.clientY-cooperativePanPreview.y;if(Math.abs(dx)>7||Math.abs(dy)>7)cv.style.transform='translate('+dx+'px,'+dy+'px)';}
 }
 if(target.tagName==='BUTTON'){target.setAttribute('data-cooperative-pending','true');target.setAttribute('aria-busy','true');}
}
function cooperativeCaptureInput(e){
 if(!cooperativeDayBusy()||cooperativeReplaying)return;
 const target=e.target.closest?.('button,input,select,textarea,a,canvas')||e.target;if(!(target instanceof Element))return;
 if(e.type==='keydown'&&e.key!=='Escape')return;
 // Native focus, typing, slider and button activation stay functional. Their
 // model-facing input/change/click handlers are fenced below.
 if(target!==cv&&/^(pointer|touch)/.test(e.type))return;
 if(e.type==='click'&&e.isTrusted){handleMusicGesture(e);if(['musicToggle','musicNext','musicRetry'].includes(target.id)){e.preventDefault();e.stopImmediatePropagation();return;}}
 if(e.type==='click'&&target.id==='pause'){
  e.preventDefault();e.stopImmediatePropagation();paused=!paused;const el=$('pause');renderPauseIcon();el.setAttribute('aria-label',paused?'Resume simulation':'Pause simulation');el.title=paused?'Resume':'Pause';$('pauseBanner').style.display=paused?'block':'none';if(paused)afterCommittedDay(()=>save());cooperativeBanner();return;
 }
 cooperativePreviewInput(e,target);if(e.type==='input'&&target.dataset.policy){const button=$('enactPolicy');if(button)button.disabled=false;}e.preventDefault();e.stopImmediatePropagation();
 const record={target,id:target.id,tag:target.tagName,data:{...target.dataset},value:target.value,checked:target.checked},type=e.type;
 let init={bubbles:true,cancelable:true,composed:true,clientX:e.clientX,clientY:e.clientY,screenX:e.screenX,screenY:e.screenY,button:e.button,buttons:e.buttons,ctrlKey:e.ctrlKey,shiftKey:e.shiftKey,altKey:e.altKey,metaKey:e.metaKey,pointerId:e.pointerId,pointerType:e.pointerType,isPrimary:e.isPrimary,pressure:e.pressure,key:e.key,code:e.code,repeat:e.repeat,deltaX:e.deltaX,deltaY:e.deltaY,deltaMode:e.deltaMode,touches:e.touches?Array.from(e.touches):undefined,targetTouches:e.targetTouches?Array.from(e.targetTouches):undefined,changedTouches:e.changedTouches?Array.from(e.changedTouches):undefined};
 const Constructor=e.constructor;
 cooperativeQueueCommand({coalesce:type==='pointermove'&&target===cv&&!buildMode&&!transitDraft?String(e.pointerId):null,label:type+' '+(record.id||record.tag.toLowerCase()),run:()=>{const el=cooperativeResolveTarget(record);if(el.disabled)throw Error('This action is no longer available with the current town state.');if(type==='input'||type==='change'){el.value=record.value;if(record.checked!==undefined)el.checked=record.checked;}el.dispatchEvent(new Constructor(type,init));}});
}
for(const type of ['click','input','change','keydown','pointerdown','pointermove','pointerup','pointercancel','pointerleave','touchstart','touchmove','touchend','touchcancel','wheel'])window.addEventListener(type,cooperativeCaptureInput,{capture:true,passive:false});
window.__cooperativeSimulation={
 enable:setCooperativeSimulation,
 status:()=>({enabled:cooperativeEnabled,busy:cooperativeDayBusy(),displayedDay:Number($('date')?.textContent.match(/DAY (\d+)$/)?.[1]||cooperativeLastCommittedDay()),committedDay:cooperativeLastCommittedDay(),workingDay:cooperativeJob?cooperativeJob.day+1:null,stage:cooperativeJob?.stage||null,queued:cooperativeCommands.length,token:cooperativeToken}),
 afterCommit:afterCommittedDay,
 command:(label,fn)=>cooperativeDayBusy()?new Promise((resolve,reject)=>cooperativeQueueCommand({label,reject,run:()=>{try{resolve(fn());}catch(e){reject(e);throw e;}}})):afterCommittedDay(fn),
 finish:finishCooperativeDaySync,
 samples:()=>JSON.parse(JSON.stringify(cooperativeSamples))
};
