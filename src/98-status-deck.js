// One compact, optional map signal replaces three simultaneous opaque overlays.
const mapStatusDeck=document.createElement('section');mapStatusDeck.id='mapStatusDeck';mapStatusDeck.setAttribute('aria-label','Town signals');
mapStatusDeck.innerHTML='<button id="mapStatusToggle" type="button" aria-expanded="false" aria-controls="mapStatusDetails"><span class="map-status-caption">TOWN SIGNALS</span><strong id="mapStatusHeadline">Your next town decision</strong><span id="mapStatusContext"></span><span id="mapStatusOverlayKey" aria-live="polite"></span><svg viewBox="0 0 16 16" aria-hidden="true"><path d="m4 6 4 4 4-4"/></svg></button><div id="mapStatusDetails" hidden></div>';
const mapStatusDetails=mapStatusDeck.querySelector('#mapStatusDetails'),mapStatusToggle=mapStatusDeck.querySelector('#mapStatusToggle');
mapStatusDetails.appendChild(document.querySelector('.map-top-left'));mapStatusDetails.appendChild($('liveEconomy'));document.querySelector('.workspace').appendChild(mapStatusDeck);
function setMapStatusExpanded(expanded){
 mapStatusToggle.setAttribute('aria-expanded',String(expanded));mapStatusDetails.hidden=!expanded;
 if(!expanded&&mapStatusDetails.contains(document.activeElement))mapStatusToggle.focus();
}
function updateMapStatusDeck(){
 if(!G)return;headerText('mapStatusHeadline',G.day===1?'Choose the town’s next step':$('marketHeadline').textContent);
 const count=Object.values(G.civicProjects?.active||{}).filter(p=>p.status==='active').length;
 headerText('mapStatusContext',(paused?'Paused':'Town running')+(count?' · '+count+' civic project'+(count===1?'':'s'):'')+' · tap for detail');
}
mapStatusToggle.onclick=()=>setMapStatusExpanded(mapStatusToggle.getAttribute('aria-expanded')!=='true');
const statusDeckHeaderBase=updateHeader;updateHeader=function(){statusDeckHeaderBase();updateMapStatusDeck();};
const statusDeckBackBase=window.__townArchive.back;window.__townArchive.back=()=>{
 if(!active&&!pendingEvent&&!buildMode&&$('helpDialog').style.display==='none'&&!mapStatusDetails.hidden){setMapStatusExpanded(false);return true;}
 return statusDeckBackBase();
};
const statusDeckResetBase=resetTownTransientUI;resetTownTransientUI=function(){setMapStatusExpanded(false);statusDeckResetBase();};
