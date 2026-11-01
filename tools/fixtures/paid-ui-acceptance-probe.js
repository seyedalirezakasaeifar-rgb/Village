// Test-only observer/fault gates injected inside the game closure. Never assembled.
window.__paidUiProbe=(function(){
 const writes=[],posted=[],heldReplies=[],heldWrites=[];let writerMode='normal',holdPaid=false,worker=null,receive=null;
 const originalPersist=persistSnapshot;
 persistSnapshot=function(payload,epoch){
  const record={epoch,checksum:checksum(payload),bytes:new TextEncoder().encode(payload).length,started:performance.now(),settled:false,ok:null};writes.push(record);
  const publish=()=>Promise.resolve(originalPersist(payload,epoch)).then(ok=>{record.settled=true;record.ok=!!ok;return ok;});
  if(writerMode==='hold')return new Promise(resolve=>heldWrites.push({record,publish,resolve}));
  if(writerMode==='fail'){record.settled=true;record.ok=false;return Promise.resolve(false);}
  return publish();
 };
 const visible=el=>!!el&&el.getClientRects().length>0&&getComputedStyle(el).visibility!=='hidden';
 function busy(){const nodes=[...document.querySelectorAll('[aria-busy="true"],[role="status"],[aria-live],#workerRealStatus,#toast')].filter(visible);return nodes.filter(el=>el.getAttribute('aria-busy')==='true'||/applying|pending|working|waiting|saving|in progress/i.test(el.textContent)).map(el=>({tag:el.tagName,id:el.id,text:el.textContent.slice(0,300),ariaBusy:el.getAttribute('aria-busy')}));}
 return {
  prepareOracle:()=>{if(window.__workerRealView?.active)throw Error('Main-thread fixture forbidden after worker adoption');chosenScenario='settlement';seed(42);paused=true;active='';for(let i=0;i<19;i++)tick();if(pendingEvent)throw Error('Fixture unexpectedly has a review');G.councilInbox=[{title:COUNCIL_EVENTS[0].title,day:G.day}];$('welcome').style.display='none';return archivePayload();},
  canonical:()=>{if(!Object.isFrozen(G))G.rngState=rngState;return JSON.stringify(G);},
  attach:w=>{if(worker)throw Error('Attach once');worker=w;receive=w.onmessage;if(typeof receive!=='function')throw Error('Published Worker onmessage contract changed');const send=w.postMessage.bind(w);w.postMessage=function(m,...rest){posted.push({id:m.id,command:m.command,epoch:m.epoch,type:m.type,at:performance.now()});return send(m,...rest);};w.onmessage=e=>{if(holdPaid&&e.data.ok&&e.data.result?.paid?.committed){heldReplies.push(e.data);return;}receive.call(w,e);};},
  holdCommit:value=>{holdPaid=value;},
  releaseCommit:()=>{holdPaid=false;const rows=heldReplies.splice(0);for(const data of rows)receive.call(worker,{data});return rows.length;},
  writerMode:value=>{if(!['normal','hold','fail'].includes(value))throw Error('Unknown test writer mode');writerMode=value;},
  releaseWrites:ok=>{const rows=heldWrites.splice(0);for(const r of rows){if(ok)r.publish().then(r.resolve);else{r.record.settled=true;r.record.ok=false;r.resolve(false);}}return rows.length;},
  snapshot:()=>({heldReplies:heldReplies.length,heldWrites:heldWrites.length,busyMarkers:busy(),writes:writes.map(x=>({...x})),posted:posted.map(x=>({...x})),frozen:!!G&&Object.isFrozen(G),modelDay:G?.day,treasury:G?.treasury,dialogVisible:visible($('eventDialog')),storage:localStorage.getItem('townledger-v6'),status:$('workerRealStatus')?.textContent||'',saveFlag:autoSaveOK}),
  decodedStored:()=>{const e=readSaveEnvelope(localStorage.getItem('townledger-v6'));return e?JSON.parse(e.payload):null;}
 };
})();
