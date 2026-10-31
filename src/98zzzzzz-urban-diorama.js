// Urban descriptors control restrained material/maintenance differences. Art
// reads an already-built simulation spatial cache; it never triggers its scan.
function urbanArtState(b){
 const c=urbanCache,block=c?.town===G?c.blocks[urbanBlockKey(b.x,b.y)]:null;
 return {band:block?.incomeBand||'No resident income',rent:block?.rentBurden||0,condition:block?.condition||b.condition,agricultural:c?.town===G?(c.homes[roadId(b.x,b.y)]||0)<2.8:false};
}
function mallArtStatus(b){const f=G.firms[b.firm];return f?.closed?'closed':f&&workingStaff(f).length&&(f.stock?.food||0)>0?'stocked':'preparing';}
const urbanArtAppearanceBase=appearanceKey;
appearanceKey=function(b){const base=urbanArtAppearanceBase(b);if(b.retailCentre)return base+':market-hall:'+mallArtStatus(b);if(!['home','apartment','tower'].includes(b.kind))return base;const s=urbanArtState(b);return base+':'+s.band+':'+(s.condition<60)+':'+s.agricultural;};
function shoppingCentreArt(g,b,w,d){
 const state=mallArtStatus(b),closed=state==='closed',wall=closed?'#ada68c':'#d0c4a1',roof=visualMonth()>=10?'#d4dbcb':'#5e7f7d',u=-w*.41,v=-d*.35;
 slab(g,-w*.48,-d*.48,w*.96,d*.96,0,'#b8b295');
 // Rear receiving court stays inside the purchased six-tile title.
 slab(g,u,-d*.46,w*.81,d*.15,1,'#8d9b89');
 dioramaSurface(g,u,v,w*.82,d*.61,1,27,wall,'brick');
 for(let j=0;j<3;j++)gable(g,u+j*w*.275,v,w*.275,d*.61,29,8,roof);
 // Elevated glazed lantern gives the centre a distinct long-span silhouette.
 dioramaSurface(g,-w*.23,-d*.13,w*.46,d*.23,34,9,'#7fa69b');
 for(let j=0;j<6;j++)dioramaWindow(g,-w*.21+j*w*.071,d*.10+.01,35,'front',w*.046,5,nightMode&&!closed);
 dioramaHipRoof(g,-w*.25,-d*.15,w*.50,d*.27,45,5,roof);
 const front=v+d*.61;
 for(let j=0;j<6;j++){
  const x=u+.04+j*w*.133;dioramaSurface(g,x,front+.012,w*.115,.025,3,15,closed?'#7d897b':'#729991');
  for(const k of [0,.053,.11])segment(g,point(x+w*k,front+.045,3),point(x+w*k,front+.045,18),'#d4c8a4',1);
  if(j===1||j===4){door(g,x+w*.02,front+.06,1,w*.075);slab(g,x-.025,front+.06,w*.17,.14,2,'#d6c9a5');}
 }
 // Continuous pedestrian arcade, thin pillars, daylight bands and two doors.
 slab(g,u-.025,front-.01,w*.87,.22,21,'#8caa96');
 for(let j=0;j<7;j++){const x=u+j*w*.137;dioramaSurface(g,x,front+.17,.04,.04,1,20,'#d5c8a6');}
 const sign=point(0,front+.025,29);g.fillStyle='#496e62';g.fillRect(sign[0]-35,sign[1]-6,70,9);g.fillStyle='#f0dfb2';g.font='bold 6px Arial';g.textAlign='center';g.fillText('MARKET HALL',sign[0],sign[1]+1);
 for(const x of [-w*.30,w*.30]){slab(g,x-.12,d*.38,.24,.09,4,'#a68c62');for(const leg of [-.09,.09])segment(g,point(x+leg,d*.42,0),point(x+leg,d*.42,4),'#60765f');}
 // Equipment, rather than imaginary stock or customers, occupies the docks.
 for(const x of [-w*.27,w*.13]){dioramaSurface(g,x,v-.025,w*.14,.04,1,13,'#5a7668');slab(g,x-.02,v-.09,w*.18,.07,3,'#8c997f');}
 if(state!=='stocked'){const q=point(0,front+.08,8);g.fillStyle=closed?'#9b805d':'#bda978';g.fillRect(q[0]-12,q[1]-3,24,5);g.fillStyle='#ede1bc';g.font='bold 3px Arial';g.fillText(closed?'CLOSED':'PREPARING',q[0],q[1]+.5);}
 if(closed)for(const x of [-w*.22,w*.22]){const q=point(x,front+.07,10);segment(g,[q[0]-5,q[1]-4],[q[0]+5,q[1]+4],'#a68a5f',2);}
}
const urbanRetailArchitectureBase=architecture;
architecture=function(g,b,w,d){
 if(b.retailCentre&&b.kind!=='worksite'&&!b.redevelopment){shoppingCentreArt(g,b,w,d);return;}
 urbanRetailArchitectureBase(g,b,w,d);
 if(!['home','apartment','tower'].includes(b.kind)||b.redevelopment)return;
 const state=urbanArtState(b),front=d*.39;
 // Income bands affect a modest frontage material only. Condition remains the
 // source of wear; lower income never implies dirt, crime or disrepair.
 if(gameOptions.decor){const coping=state.band==='Higher income'?'#d0c9ac':state.band==='Lower income'?'#a3ae91':'#bcb69a';
  for(const side of [-1,1])slab(g,side*w*.34-.04,front,.08,.07,1,coping);
  if(state.agricultural){for(let j=0;j<3;j++)slab(g,-w*.38,front-.14+j*.06,w*.20,.025,1,j%2?'#8d985e':'#b6a476');}
  if(state.condition<60){const q=point(w*.25,front,6);segment(g,q,[q[0]+2,q[1]+4],'#8a89695f');}
 }
};
const urbanRetailParcelBase=parcelDetails,urbanRetailIdentityBase=architecturalIdentity;
parcelDetails=function(g,b,w,d){if(!b.retailCentre)urbanRetailParcelBase(g,b,w,d);};
architecturalIdentity=function(g,b,w,d){if(!b.retailCentre)urbanRetailIdentityBase(g,b,w,d);};
