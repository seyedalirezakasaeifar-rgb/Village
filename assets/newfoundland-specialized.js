// Original regional adaptation of actual specialized uses. No people, parked
// fleets, sales or inventories are invented by these static architectural forms.
export function newfoundlandSpecialized(b,{state,box,tree}){
 const supported=['park','square','tower','quarry','forestry','transit_depot','elevated_station','metro_station','airport','watchtower'];if(!supported.includes(b.kind)&&!b.retailCentre)return false;
 const xs=b.footprint.map(i=>i%state.size),zs=b.footprint.map(i=>Math.floor(i/state.size)),minX=Math.min(...xs),minZ=Math.min(...zs),w=Math.max(...xs)-minX+1,d=Math.max(...zs)-minZ+1,x=minX+(w-1)/2,z=minZ+(d-1)/2;
 const part=(u,y,v,a,h,c,color)=>box(x+u,y,z+v,a,h,c,color);
 if(['park','square'].includes(b.kind)){
  for(const id of b.footprint){const xx=id%state.size,zz=Math.floor(id/state.size);box(xx,.015,zz,.98,.03,.98,b.kind==='park'?'#759363':'#b1ae99');box(xx,.04,zz,.18,.025,.94,'#b9b49c');box(xx,.041,zz,.94,.025,.18,'#b9b49c');for(const side of [-1,1]){box(xx+side*.29,.13,zz+.21,.28,.045,.085,'#a28862');box(xx+side*.29,.21,zz+.25,.28,.13,.025,'#9b835e');for(const u of [-.1,.1])box(xx+side*.29+u,.075,zz+.21,.025,.11,.04,'#5d7065');}if(b.kind==='square'&&b.gathering?.status==='active'&&b.gathering.attendance>0)for(const side of [-1,1]){box(xx+side*.29,.20,zz-.24,.29,.04,.23,'#a48961');box(xx+side*.29,.46,zz-.24,.34,.04,.27,side<0?'#b4814e':'#678777');for(const u of [-.13,.13])box(xx+side*.29+u,.33,zz-.24,.018,.30,.018,'#d5cbb0');}if(b.kind==='park')tree?.(xx,zz-.16,b.id,{small:true});else{box(xx,.13,zz-.29,.27,.22,.16,'#a5a38e');box(xx,.25,zz-.29,.25,.035,.14,'#739064');}}
  return true;
 }
 if(w*d!==b.footprint.length)return false;
 if(b.kind==='tower'){
  const H=4.65;part(0,H/2+.1,0,w*.78,H,d*.74,'#a49e8b');part(0,.24,0,w*.94,.4,d*.91,'#a29a83');for(let f=0;f<9;f++){const y=.42+f*.5;part(0,y+.18,d*.38,w*.83,.045,.05,'#d6d3bd');for(const u of [-w*.25,0,w*.25]){part(u,y,d*.38,.18,.28,.04,'#e2d9c1');part(u,y,d*.405,.135,.23,.02,'#547888');}for(const side of [-1,1])for(const v of [-d*.22,d*.22])part(side*w*.40,y,v,.04,.27,.17,'#587884');}part(0,H+.13,0,w*.85,.14,d*.82,'#49666c');part(0,.33,d*.47,.27,.5,.04,'#3f5a5c');return true;
 }
 if(b.retailCentre){
  part(0,.45,0,w*.9,.85,d*.76,'#aa7a64');part(0,.91,0,w*.96,.10,d*.82,'#4e666b');part(0,.58,d*.40,w*.94,.06,.20,'#d4d0b8');for(let j=0;j<Math.max(2,Math.floor(w/.45));j++){const u=-w*.36+j*w*.72/(Math.max(2,Math.floor(w/.45))-1);part(u,.34,d*.395,.29,.43,.035,'#d9d4bd');part(u,.36,d*.42,.23,.32,.02,'#527986');part(u,.29,d*.47,.035,.58,.04,'#d4d0b8');}return true;
 }
 if(['transit_depot','airport'].includes(b.kind)){
  part(0,.41,0,w*.90,.78,d*.76,'#a77964');part(0,.83,0,w*.94,.12,d*.81,'#455f65');for(const u of [-w*.25,w*.25]){part(u,.35,d*.39,w*.31,.61,.035,'#d6d2ba');part(u,.34,d*.415,w*.25,.52,.025,'#5c7979');for(const y of [.18,.31,.44,.57])part(u,y,d*.433,w*.25,.014,.01,'#a9b4a9');}if(b.kind==='airport'){part(-w*.30,.96,-d*.22,.20,.22,.20,'#b5af98');part(-w*.30,1.09,-d*.22,.25,.045,.25,'#456b76');}return true;
 }
 if(['elevated_station','metro_station'].includes(b.kind)){
  const y=b.kind==='elevated_station'?1.20:.08;part(0,y,0,w*.92,.14,d*.88,'#b5b39d');for(const u of [-w*.34,w*.34])for(const v of [-d*.29,d*.29])part(u,y+.30,v,.045,.56,.045,'#c8c9b5');part(0,y+.61,0,w*.96,.085,d*.92,'#4c6970');part(0,y+.20,-d*.31,w*.55,.27,.12,'#b1a589');if(y>1){for(const u of [-w*.34,w*.34])part(u,.58,-d*.24,.09,1.16,.09,'#929c94');part(-w*.23,.70,-d*.23,.29,1.40,.29,'#a9a994');part(-w*.23,.30,-d*.075,.20,.44,.025,'#4c6b72');part(-w*.23,1.37,-d*.23,.33,.065,.33,'#566f73');}return true;
 }
 if(b.kind==='watchtower'){
  for(const u of [-.25,.25])for(const v of [-.25,.25])part(u,.78,v,.065,1.56,.065,'#8a8e79');part(0,1.48,0,.70,.12,.70,'#a69b7b');part(0,1.75,0,.57,.44,.57,'#9d9f87');for(const side of [-1,1]){part(side*.30,1.80,0,.025,.16,.40,'#456b78');part(0,1.80,side*.30,.40,.16,.025,'#456b78');}part(0,2.02,0,.72,.09,.72,'#4e6669');return true;
 }
 if(b.kind==='quarry'){
  part(0,.012,0,w*.95,.025,d*.95,'#6c776f');for(const side of [-1,1]){part(side*w*.40,.10,0,w*.16,.20,d*.92,'#a5a48c');part(0,.07,side*d*.40,w*.64,.14,d*.13,'#9b9f89');}part(-w*.22,.19,-d*.16,w*.27,.36,d*.27,'#8a8a70');part(w*.22,.12,d*.05,w*.23,.23,d*.32,'#b3ad92');return true;
 }
 if(b.kind==='forestry'){
  part(0,.30,-d*.13,w*.64,.58,d*.53,'#8c8064');part(0,.63,-d*.13,w*.74,.10,d*.62,'#4d6767');const stock=b.firm?.stock?.logs||0;for(let i=0;i<Math.min(3,Math.ceil(stock/50));i++)part(-w*.22+i*w*.22,.09,d*.27,w*.15,.16,d*.25,'#b1976e');return true;
 }
 return false;
}
