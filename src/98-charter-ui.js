function charterPlan(){return `<svg class="charter-plan" viewBox="0 0 130 130" role="img" aria-label="Original town and twenty-one adjoining regional districts"><rect x="0" y="0" width="56" height="56" fill="#78946b" stroke="#344f3d" stroke-width=".5"/>${ANNEX_PARCELS.map(p=>`<rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" fill="${G.charter.owned.includes(p.id)?'#78946b':p.id===parcelFocus?'#d4b873':'#d7d3b3'}" stroke="#536c4b" stroke-width=".5"/>`).join('')}<path d="M5 0 4 18 6 30 4 49 5 65 4 80" stroke="#7baba4" stroke-width="3" fill="none"/><ellipse cx="66" cy="22" rx="6" ry="8" fill="#7baba4"/><text x="18" y="29" font-size="4" fill="#fff3d5">ORIGINAL TOWN</text></svg>`;}
function charterPanel(){
 const area=CHARTER_BASE*CHARTER_BASE+ANNEX_PARCELS.filter(p=>G.charter.owned.includes(p.id)).reduce((n,p)=>n+p.w*p.h,0);
 return `<details id="charterOffice" class="charter-accordion"><summary>Expand the borough · ${ANNEX_PARCELS.length-G.charter.owned.length} districts available</summary>`+head('Expand the borough')+`<section class="charter-office"><h3>New land, a real civic commitment</h3><p class="desc">The original 56 × 56 town retains its rights. Twenty-one substantial outer districts extend this bounded region to 128 × 128, through successive purchases. A deed makes new land available for development; it does not create roads, workers, utilities or service coverage. Existing private property titles remain unchanged.</p>${charterPlan()}${strip('Chartered surface',fmt(area)+' regional tiles')}${strip('Outer districts acquired',G.charter.owned.length+' / '+ANNEX_PARCELS.length)}<div class="btnrow"><button data-charter-overview>View regional boundaries</button><button data-charter-home>Return to town</button></div></section>`+
 ANNEX_PARCELS.map(p=>{const q=parcelSurvey(p),owned=G.charter.owned.includes(p.id),near=parcelAdjacent(p),deed=G.charter.deeds.find(d=>d.id===p.id);return `<section class="charter-district ${p.id===parcelFocus?'selected':''}" data-parcel-card="${p.id}"><small>${owned?'DEED RECORDED':near?'REGIONAL LAND AVAILABLE':'ADJOINING DEED REQUIRED'}</small><h3 tabindex="-1">${esc(p.name)}</h3><p class="desc">${esc(p.description)}</p>${strip('District surface',q.area+' tiles · '+p.w+' × '+p.h)}${strip('Land / water',q.land+' / '+q.water+' tiles')}${strip(owned?'Price paid':'Development-rights price',money(owned?deed.price:q.price))}${owned?strip('Acquired','Day '+deed.day):tip(near?'A connection from existing streets is still required. New households and firms face the usual utility bills, paid staffing and local service catchments.':'Acquire an adjoining district before extending into this belt.')}<div class="btnrow"><button data-parcel-preview="${p.id}">Preview district</button>${owned?'':`<button data-parcel-buy="${p.id}" ${!near||G.treasury<q.price?'disabled':''}>Review purchase · ${money(q.price)}</button>`}</div>${owned?'':`<p class="desc" data-parcel-funds="${p.id}" ${G.treasury>=q.price?'hidden':''}>Treasury shortfall: ${money(Math.max(0,q.price-G.treasury))}. This is a one-time land outlay; retain funds for construction and recurring commitments.</p>`}</section>`;}).join('')+'</details>';
}
// The construction panel is intentionally not replaced during live simulation
// (to protect placement mode and keyboard focus). Refresh only deed quotes and
// affordability in place as treasury, ownership, roads or time change.
let charterAffordabilitySignature='';
function refreshCharterAffordability(){
 if(!G)return;const office=$('charterOffice');if(!office)return;const signature=JSON.stringify([G.day,G.treasury,G.charter?.revision,G.construction,G.buildings.length]);if(signature===charterAffordabilitySignature)return;charterAffordabilitySignature=signature;
 for(const card of office.querySelectorAll('[data-parcel-card]')){const id=card.dataset.parcelCard,p=ANNEX_PARCELS.find(v=>v.id===id);if(!p)continue;const q=parcelSurvey(p),owned=G.charter.owned.includes(id),button=card.querySelector('[data-parcel-buy]'),shortfall=card.querySelector('[data-parcel-funds]');if(button){button.disabled=owned||!parcelAdjacent(p)||G.treasury<q.price;button.textContent='Review purchase · '+money(q.price);}if(shortfall){shortfall.hidden=owned||G.treasury>=q.price;shortfall.textContent='Treasury shortfall: '+money(Math.max(0,q.price-G.treasury))+'. This is a one-time land outlay; retain funds for construction and recurring commitments.';}}
}
const charterHeaderBase=updateHeader;updateHeader=function(){charterHeaderBase();refreshCharterAffordability();};
function revealCharterOffice(){const office=$('charterOffice');if(office)office.open=true;}
function previewParcel(id){const p=ANNEX_PARCELS.find(p=>p.id===id);if(!p)return;parcelFocus=id;overlay='charter';const center=iso(p.x+p.w/2,p.y+p.h/2);cam={x:center[0],y:center[1]+18,zoom:clamp(Math.min((cw-50)/((p.w+p.h)*36),(ch-100)/((p.w+p.h)*18)),.025,.55)};cam.y+=38/cam.zoom;closePanel();dirty=true;toast(p.name+': '+(G.charter.owned.includes(id)?'chartered land':'regional land · review its deed in Public Works'));}
function requestParcelPurchase(id){const p=ANNEX_PARCELS.find(p=>p.id===id);if(!p||G.charter.owned.includes(id)||!parcelAdjacent(p))return;const q=parcelSurvey(p),town=G;if(G.treasury<q.price){toast('Insufficient treasury for this district.');return;}
 showCustomEvent('LAND PURCHASE','Acquire '+p.name+'?',q.area+' new regional tiles, including '+q.land+' land and '+q.water+' water tiles. Pay '+money(q.price)+' to the regional land authority. Existing private titles stay intact. Roads, utilities, buildings and service staffing are separate commitments.',[{title:'Acquire the district',desc:'One-time price '+money(q.price)+'. The deed expands municipal development rights.',cost:q.price,command:{type:'land-purchase',town,parcel:id,price:q.price},apply:()=>{if(G!==town||!purchaseParcel(id,q.price)){toast('The quote is no longer valid. Review the district again.');return;}parcelFocus=id;openPanel('construction');const publish=()=>{revealCharterOffice();const card=document.querySelector('[data-parcel-card="'+id+'"]');card?.scrollIntoView({block:'start'});card?.querySelector('h3')?.focus();};if(!window.__rootAdmission?.deferUI(publish))publish();}},{title:'Keep the current boundary',desc:'No payment and no change to ownership.',apply:()=>{}}]);
}
let surveySignature='';
function updateRegionSurvey(){
 const signature=JSON.stringify([parcelFocus,G.charter?.owned]);if(signature===surveySignature)return;surveySignature=signature;
 $('surveyReview').disabled=!parcelFocus;$('surveyDistrict').innerHTML='<option value="" disabled '+(!parcelFocus?'selected':'')+'>Choose a district…</option>'+ANNEX_PARCELS.map((p,i)=>`<option value="${p.id}" ${parcelFocus===p.id?'selected':''}>${i+1}. ${esc(p.name)}${G.charter.owned.includes(p.id)?' · Owned':''}</option>`).join('');
}
function reviewSurveyDistrict(id){if(!ANNEX_PARCELS.some(p=>p.id===id))return;parcelFocus=id;openPanel('construction');const publish=()=>{revealCharterOffice();const card=document.querySelector('[data-parcel-card="'+id+'"]');card?.scrollIntoView({block:'start'});card?.querySelector('h3')?.focus();};if(!window.__rootAdmission?.deferUI(publish))publish();}
function charterLabelLayout(){
 const occupied=[],labels=[];for(const p of ANNEX_PARCELS.slice().sort((a,b)=>(b.id===parcelFocus)-(a.id===parcelFocus))){const index=ANNEX_PARCELS.indexOf(p),q=iso(p.x+p.w/2,p.y+p.h/2),x=cw/2+(q[0]-cam.x)*cam.zoom,y=ch/2+(q[1]-cam.y)*cam.zoom;
  let compact=cam.zoom<.20||parcelFocus!==p.id,text=(index+1)+'. '+p.name+(G.charter.owned.includes(p.id)?' · OWNED':'');
  const width=text.length*6.1+14;let box={x:x-width/2,y:y-11,w:width,h:22};
  if(occupied.some(a=>box.x<a.x+a.w+6&&box.x+box.w>a.x-6&&box.y<a.y+a.h+5&&box.y+box.h>a.y-5))compact=true;
  if(compact){text=String(index+1);box={x:x-11,y:y-11,w:22,h:22};}
  if(box.x<0||box.y<0||box.x+box.w>cw||box.y+box.h>ch)continue;
  if(occupied.some(a=>box.x<a.x+a.w+6&&box.x+box.w>a.x-6&&box.y<a.y+a.h+5&&box.y+box.h>a.y-5))continue;
  occupied.push(box);labels.push({p,index,text,compact,x,y,box});
 }return labels;
}
function charterSurveyTap(sx,sy,x,y){
 const label=charterLabelLayout().filter(a=>Math.abs(sx-a.x)<=Math.max(22,a.box.w/2)&&Math.abs(sy-a.y)<=22).sort((a,b)=>Math.hypot(sx-a.x,sy-a.y)-Math.hypot(sx-b.x,sy-b.y))[0],p=label?.p||parcelForTile(x,y);if(!p)return false;
 if(parcelFocus===p.id)reviewSurveyDistrict(p.id);else previewParcel(p.id);dirty=true;return true;
}
function drawCharterBounds(g){
 if(!G.charter)return;g.save();g.lineJoin='round';
 for(const p of ANNEX_PARCELS){const owned=G.charter.owned.includes(p.id);if(owned&&overlay!=='charter'&&parcelFocus!==p.id)continue;
  const points=[[p.x-.5,p.y-.5],[p.x+p.w-.5,p.y-.5],[p.x+p.w-.5,p.y+p.h-.5],[p.x-.5,p.y+p.h-.5]].map(([x,y])=>{const q=iso(x,y);return[q[0],q[1]+18]});
  g.strokeStyle=owned?'#bfd2a4':'#d4b777';g.lineWidth=(parcelFocus===p.id?2.5:1.2)/cam.zoom;g.setLineDash(owned?[]:[7/cam.zoom,5/cam.zoom]);g.beginPath();points.forEach((q,i)=>i?g.lineTo(...q):g.moveTo(...q));g.closePath();g.stroke();
 }
 if(overlay==='charter'||parcelFocus)for(const label of charterLabelLayout()){if(overlay!=='charter'&&label.p.id!==parcelFocus)continue;const q=iso(label.p.x+label.p.w/2,label.p.y+label.p.h/2),w=label.box.w/cam.zoom;
  g.font=(11/cam.zoom)+'px Arial';g.fillStyle=label.p.id===parcelFocus?'#e9cc8bed':'#f1ead3ed';g.fillRect(q[0]-w/2,q[1]-11/cam.zoom,w,22/cam.zoom);g.strokeStyle='#536c4b';g.lineWidth=1/cam.zoom;g.strokeRect(q[0]-w/2,q[1]-11/cam.zoom,w,22/cam.zoom);g.fillStyle='#29422e';g.textAlign='center';g.textBaseline='middle';g.fillText(label.text,q[0],q[1]);
 }
 g.setLineDash([]);g.restore();
}
$('surveyDistrict').addEventListener('change',e=>previewParcel(e.target.value));$('surveyReview').onclick=()=>reviewSurveyDistrict(parcelFocus||$('surveyDistrict').value);
const charterConstructionBase=renderConstructionFull;renderConstructionFull=function(){return charterPanel()+charterConstructionBase();};
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b||!G)return;if(b.dataset.parcelPreview)previewParcel(b.dataset.parcelPreview);if(b.dataset.parcelBuy)requestParcelPurchase(b.dataset.parcelBuy);if(b.hasAttribute('data-charter-home')){overlay='none';parcelFocus=null;closePanel();centerTownCamera();}if(b.hasAttribute('data-charter-overview')){overlay='charter';parcelFocus=null;closePanel();const p=iso(T/2,T/2);cam={x:p[0],y:p[1]+18,zoom:Math.max(.025,Math.min((cw-24)/RW,(ch-100)/RH))};cam.y+=38/cam.zoom;dirty=true;}});

const charterBackBase=window.__townArchive.back;window.__townArchive.back=()=>{if(!active&&!pendingEvent&&$('helpDialog').style.display==='none'){if(buildMode){closeBuildTool();return true;}if(overlay==='charter'){overlay='none';parcelFocus=null;centerTownCamera();return true;}}return charterBackBase();};
