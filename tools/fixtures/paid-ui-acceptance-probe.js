// Test-only observer/fault gates injected inside the game closure. Never assembled.
window.__paidUiProbe=(function(){
 const writes=[],posted=[],heldReplies=[],heldWrites=[];let writerMode='normal',holdPaid=false,worker=null;
 const originalPersist=persistSnapshot;
 persistSnapshot=function(payload,epoch){
  const record={epoch,checksum:checksum(payload),bytes:new TextEncoder().encode(payload).length,started:performance.now(),settled:false,ok:null};writes.push(record);
  const publish=()=>Promise.resolve(originalPersist(payload,epoch)).then(ok=>{record.settled=true;record.ok=!!ok;return ok;});
  if(writerMode==='hold')return new Promise(resolve=>heldWrites.push({record,publish,resolve}));
  if(writerMode==='fail'){record.settled=true;record.ok=false;return Promise.resolve(false);}
  return publish();
 };
 const visible=el=>!!el&&getComputedStyle(el).visibility!=='hidden'&&getComputedStyle(el).opacity!=='0'&&[...el.getClientRects()].some(r=>r.right>0&&r.bottom>0&&r.left<innerWidth&&r.top<innerHeight);
 function busy(){const nodes=[...document.querySelectorAll('[aria-busy="true"],[role="status"],[aria-live],#workerRealStatus,#toast')].filter(visible);return nodes.filter(el=>el.getAttribute('aria-busy')==='true'||/applying|pending|working|waiting|saving|in progress/i.test(el.textContent)).map(el=>({tag:el.tagName,id:el.id,text:el.textContent.slice(0,300),ariaBusy:el.getAttribute('aria-busy'),rect:{left:el.getBoundingClientRect().left,top:el.getBoundingClientRect().top,width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height}}));}
 return {
  prepareOracle:()=>{if(window.__workerRealView?.active)throw Error('Main-thread fixture forbidden after worker adoption');chosenScenario='settlement';seed(42);paused=true;active='';for(let i=0;i<19;i++)tick();if(pendingEvent)throw Error('Fixture unexpectedly has a review');G.councilInbox=[{title:COUNCIL_EVENTS[0].title,day:G.day}];$('welcome').style.display='none';return archivePayload();},
  normalizeOracle:raw=>{if(window.__workerRealView?.active)throw Error('Oracle restore forbidden after worker adoption');paused=true;active='';if(!hydrateSave(raw))throw Error('Oracle normalization refused');G.rngState=rngState;return JSON.stringify(G);},
  showOraclePanel:tab=>{if(window.__workerRealView?.active)throw Error('Oracle panel forbidden after worker adoption');openPanel(tab);G.rngState=rngState;return JSON.stringify(G);},
  canonical:()=>{if(!Object.isFrozen(G))G.rngState=rngState;return JSON.stringify(G);},
  attach:w=>{if(worker===w)return;worker=w;const receive=w.onmessage;if(typeof receive!=='function')throw Error('Published Worker onmessage contract changed');const send=w.postMessage.bind(w);w.postMessage=function(m,...rest){posted.push({id:m.id,command:m.command,epoch:m.epoch,type:m.type,at:performance.now()});return send(m,...rest);};w.onmessage=e=>{if(holdPaid&&e.data.ok&&e.data.result?.paid?.committed){heldReplies.push({data:e.data,worker:w,receive});return;}receive.call(w,e);};},
  holdCommit:value=>{holdPaid=value;},
  releaseCommit:()=>{holdPaid=false;const rows=heldReplies.splice(0);for(const row of rows)row.receive.call(row.worker,{data:row.data});return rows.length;},
  writerMode:value=>{if(!['normal','hold','fail'].includes(value))throw Error('Unknown test writer mode');writerMode=value;},
  releaseWrites:ok=>{const rows=heldWrites.splice(0);for(const r of rows){if(ok)r.publish().then(r.resolve);else{r.record.settled=true;r.record.ok=false;r.resolve(false);}}return rows.length;},
  snapshot:()=>({heldReplies:heldReplies.length,heldWrites:heldWrites.length,busyMarkers:busy(),writes:writes.map(x=>({...x})),posted:posted.map(x=>({...x})),activePanel:active,frozen:!!G&&Object.isFrozen(G),modelDay:G?.day,treasury:G?.treasury,dialogVisible:visible($('eventDialog')),storage:localStorage.getItem('townledger-v6'),status:$('workerRealStatus')?.textContent||'',saveFlag:autoSaveOK}),
  decodedStored:()=>{const e=readSaveEnvelope(localStorage.getItem('townledger-v6'));return e?JSON.parse(e.payload):null;}
 };
})();
