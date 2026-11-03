// Named counterparties share the existing conserved external cash account.
// Orders own physical stock until arrival; graphics never settle a transaction.
const OUTSIDE_MARKETS=[
 {id:'upland',name:'Upland Cooperative',direction:'north',days:2,capacity:700,imports:{grain:.86,food:.94,logs:1.06},exports:{timber:1.10,manufactures:1.16,stone:1.04}},
 {id:'port',name:'Greyhaven Port',direction:'east',days:3,capacity:900,imports:{manufactures:.85,timber:.94,food:1.08},exports:{grain:1.07,flour:1.13,food:1.10}},
 {id:'ridge',name:'Ironridge Works',direction:'south',days:4,capacity:600,imports:{stone:.84,logs:.91,grain:1.06},exports:{timber:1.18,food:1.15,manufactures:1.03}}
];
function ensureRegionalTrade(){if(!G.regionalTrade)G.regionalTrade={version:1,serial:0,shipments:[],recent:[],contracts:[],delivered:0,late:0};return G.regionalTrade}
function regionalMarketQuote(m,good,side){const cycle=Math.sin(Math.floor(G.day/30)*.7+OUTSIDE_MARKETS.indexOf(m)*1.8+Object.keys(goods).indexOf(good));return marketPrice(good)*(m[side]?.[good]||1)*(1+cycle*.045)}
let regionalRouteCache=null;
function regionalGateway(m){
 const net=graph();if(regionalRouteCache?.net!==net){const nodes=[...net.neighbors.keys()].filter(id=>net.parts[id]===net.mainPart),gates={};for(const market of OUTSIDE_MARKETS){const score=id=>market.direction==='north'?-(id/T|0):market.direction==='south'?(id/T|0):id%T;gates[market.id]=nodes.sort((a,b)=>score(b)-score(a)||a-b)[0];}regionalRouteCache={net,gates};}return regionalRouteCache.gates[m.id];
}
function regionalRoadPath(f,m){const port=graph().portals.get(f.building),gate=regionalGateway(m);return port==null||gate==null?[]:routeBetween(port,gate)}
function regionalCapacity(m,good,direction){const s=ensureRegionalTrade();return Math.max(0,m.capacity*(.85+.15*Math.sin(Math.floor(G.day/30)*.6+OUTSIDE_MARKETS.indexOf(m)))-s.shipments.filter(o=>o.market===m.id&&o.started===G.day).reduce((n,o)=>n+o.qty,0))}
function regionalQuote(f,m,good,direction){const path=regionalRoadPath(f,m);if(!path.length)return null;const price=regionalMarketQuote(m,good,direction==='import'?'imports':'exports'),freight=.06+(path.length-1)*.003+m.days*.015;return {m,path,price,freight,days:m.days+Math.max(1,Math.ceil((path.length-1)/24)),capacity:Math.min(regionalCapacity(m,good,direction),regionalLoadingLeft())}}
function regionalExpense(f,cost){if(marketOpen)f.expenses+=cost;else f.pendingFreightExpense=(f.pendingFreightExpense||0)+cost;f.shippingToday=(f.shippingToday||0)+cost}
function dispatchRegional(f,good,requested,direction,quote,contract=null){
 const s=ensureRegionalTrade();if(!quote||s.shipments.length>=240||!f||f.closed||!(requested>0))return 0;const tariff=direction==='import'?G.policy.importTariff/100:0,unit=direction==='import'?quote.price*(1+tariff)+quote.freight:quote.freight;
 let qty=Math.min(requested,quote.capacity,direction==='export'?(f.stock[good]||0):Infinity,unit>0?f.cash/unit:Infinity);qty=Math.floor(qty*1000)/1000;if(qty<.001)return 0;
 const freight=qty*quote.freight,price=contract?.price||quote.price;let inventoryCost=0;
 if(direction==='import'){const total=qty*(quote.price*(1+tariff))+freight,levy=qty*quote.price*tariff;recordInventoryPurchase(f,good,qty,total);f.cash-=total;G.region+=total-levy;transferTreasury(levy,'tariffs');goodsEntry(good,'imports',qty);if(G.market)G.market.imports+=total-levy;}
 else{inventoryCost=takeInventory(f,good,qty,false);f.cash-=freight;G.region+=freight;regionalExpense(f,freight);}
 const path=direction==='import'?quote.path.slice().reverse():quote.path.slice();s.shipments.push({id:++s.serial,firm:f.id,market:quote.m.id,good,qty,direction,price,inventoryCost,freight,path,started:G.day,due:G.day+quote.days,travelDays:quote.days,status:'travelling',contract:contract?.id||null});return qty;
}
const instantaneousRegionalImport=regionImport;
regionImport=function(f,good,qty){if(!G.policy.imports)return 0;const quotes=OUTSIDE_MARKETS.map(m=>regionalQuote(f,m,good,'import')).filter(Boolean).sort((a,b)=>a.price+a.freight-b.price-b.freight);let left=qty,ordered=0;for(const q of quotes){const n=dispatchRegional(f,good,left,'import',q);ordered+=n;left-=n;if(left<.001)break}return ordered};
const localPendingGoods=pendingGoods;
pendingGoods=function(f,good){return localPendingGoods(f,good)+(G.regionalTrade?.shipments||[]).filter(o=>o.direction==='import'&&o.firm===f.id&&o.good===good).reduce((n,o)=>n+o.qty,0)};
const localStockTotals=stockTotals;
stockTotals=function(){const totals=localStockTotals();for(const o of G.regionalTrade?.shipments||[])totals[o.good]=(totals[o.good]||0)+o.qty;return totals};
function dispatchRoadExport(f,good,qty,ask){const quotes=OUTSIDE_MARKETS.map(m=>regionalQuote(f,m,good,'export')).filter(q=>q&&q.price>=ask*.88&&q.price>q.freight).sort((a,b)=>(b.price-b.freight)-(a.price-a.freight));let left=qty,sent=0;for(const q of quotes){const n=dispatchRegional(f,good,left,'export',q);sent+=n;left-=n;if(left<.001)break}return sent}
function regionalFreightDay(){
 const s=ensureRegionalTrade(),keep=[];for(const o of s.shipments){if(G.day<o.due){keep.push(o);continue}const f=G.firms[o.firm],m=OUTSIDE_MARKETS.find(m=>m.id===o.market),path=f&&regionalRoadPath(f,m);
  if(!f||!path?.length){o.status='Route interrupted';s.late++;keep.push(o);continue}
  if(o.direction==='export'&&G.region+1e-8<o.qty*o.price){o.status='Buyer awaiting liquidity';s.late++;keep.push(o);continue}
  if(o.direction==='import'){f.stock[o.good]=(f.stock[o.good]||0)+o.qty;}
  else{const gross=o.qty*o.price;G.region-=gross;enterpriseRevenue(f,gross);f.pendingCogs=(f.pendingCogs||0)+o.inventoryCost;f.pendingSalesQty=(f.pendingSalesQty||0)+o.qty;goodsEntry(o.good,'exports',o.qty);if(G.market)G.market.externalSales+=gross;const c=s.contracts.find(c=>c.id===o.contract);if(c)c.delivered+=o.qty;}
  s.delivered++;s.recent.unshift({...o,arrived:G.day,status:'Delivered'});if(s.recent.length>36)s.recent.length=36;
 }s.shipments=keep;
 for(const c of s.contracts){if(c.status!=='active')continue;const f=G.firms[c.firm];if(c.delivered+.001>=c.quantity&&G.day<=c.deadline){c.status='fulfilled';story('Trade agreement fulfilled: '+c.name+'. Payment reached '+f.name+'.','good',f.building);continue}if(G.day>c.deadline){c.status='missed';story('Trade agreement window missed: '+c.name+'. Paid cargo still travels; no invented fine. Review capacity before renewing.','bad',f?.building);continue}const reserved=s.shipments.filter(o=>o.contract===c.id).reduce((n,o)=>n+o.qty,0),need=c.quantity-c.delivered-reserved;if(need>.001&&f&&!f.closed){const m=OUTSIDE_MARKETS.find(m=>m.id===c.market),q=regionalQuote(f,m,c.good,'export'),buffer=c.good==='food'?Math.max(20,G.stats.population*.8):10;dispatchRegional(f,c.good,Math.max(0,Math.min(need,(f.stock[c.good]||0)-buffer)),'export',q,c);}}
}
function validateRegionalTrade(data){const s=data.regionalTrade;if(s==null)return true;if(!['delivered','late'].every(k=>Number.isSafeInteger(s[k])&&s[k]>=0)||s.version!==1||!Number.isSafeInteger(s.serial)||s.serial<0||!Array.isArray(s.shipments)||s.shipments.length>240||!Array.isArray(s.recent)||s.recent.length>36||!Array.isArray(s.contracts)||s.contracts.length>24)return false;const ids=new Set();if(s.recent.some(o=>!o||!data.firms[o.firm]||!OUTSIDE_MARKETS.some(m=>m.id===o.market)||!owns(goods,o.good)||!Number.isFinite(o.qty)||o.qty<=0||!Array.isArray(o.path)||o.path.length>T*T))return false;return s.shipments.every(o=>{if(!o||!Number.isInteger(o.id)||o.id<1||o.id>s.serial||ids.has(o.id)||!data.firms[o.firm]||!OUTSIDE_MARKETS.some(m=>m.id===o.market)||!owns(goods,o.good)||!['import','export'].includes(o.direction)||!['qty','price','freight','inventoryCost'].every(k=>Number.isFinite(o[k])&&o[k]>=0)||o.qty<=0||!Number.isInteger(o.due)||o.due<o.started||!Number.isInteger(o.started)||o.started<1||o.started>data.day||!Number.isInteger(o.travelDays)||o.travelDays<1||o.travelDays>T*T||typeof o.status!=='string'||o.status.length>80||!Array.isArray(o.path)||!o.path.length||o.path.length>T*T)return false;ids.add(o.id);return o.path.every((id,i)=>Number.isInteger(id)&&id>=0&&id<T*T&&(!i||Math.abs(id%T-o.path[i-1]%T)+Math.abs((id/T|0)-(o.path[i-1]/T|0))===1));})&&s.contracts.every(c=>c&&Number.isInteger(c.id)&&data.firms[c.firm]&&OUTSIDE_MARKETS.some(m=>m.id===c.market)&&owns(goods,c.good)&&['active','fulfilled','missed','cancelled'].includes(c.status)&&typeof c.name==='string'&&c.name.length<=200&&['quantity','delivered','price','deadline'].every(k=>Number.isFinite(c[k])&&c[k]>=0));}
