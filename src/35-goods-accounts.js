function stockTotals(){
 const totals=Object.fromEntries(Object.keys(goods).map(k=>[k,0]));
 for(const f of G.firms)for(const k of Object.keys(goods))totals[k]+=Number(f.stock[k])||0;
 for(const s of G.freight||[])totals[s.good]=(totals[s.good]||0)+s.qty;
 return totals;
}
function ensureGoodsAccounts(){
 if(!G.goodsAccounts){const opening=stockTotals();G.goodsAccounts=Object.fromEntries(Object.keys(goods).map(k=>[k,{opening:opening[k],produced:0,consumed:0,imports:0,exports:0}]));}
 const missing=Object.keys(goods).filter(k=>!G.goodsAccounts[k]);if(missing.length){const opening=stockTotals();for(const k of missing)G.goodsAccounts[k]={opening:opening[k],produced:0,consumed:0,imports:0,exports:0};}
 G.goodsPrices=G.goodsPrices||{...goods};
}
function goodsEntry(good,category,qty){if(!(qty>0)||!G.goodsAccounts?.[good])return;
 // Preserve low-order increments across decades of paid fractional deliveries.
 // This is numerical carry, never a balancing entry or a change to stock/cash.
 G.goodsCompensation=G.goodsCompensation||{};const carry=G.goodsCompensation[good]||(G.goodsCompensation[good]={}),a=G.goodsAccounts[good],adjusted=qty-(carry[category]||0),total=a[category]+adjusted;carry[category]=(total-a[category])-adjusted;a[category]=total;
}
function expectedCommodityStock(good,a){
 const c=G.goodsCompensation?.[good]||{},terms=[a.opening,a.produced,a.imports,-a.consumed,-a.exports,-(c.produced||0),-(c.imports||0),c.consumed||0,c.exports||0];let sum=0,carry=0;
 for(const value of terms){const next=sum+value;carry+=Math.abs(sum)>=Math.abs(value)?(sum-next)+value:(value-next)+sum;sum=next;}return sum+carry;
}
function validateGoodsAccounting(data){
 if(data.goodsAccounts!=null){if(typeof data.goodsAccounts!=='object'||Array.isArray(data.goodsAccounts))return false;for(const [good,a] of Object.entries(data.goodsAccounts)){if(!owns(goods,good)||!a||['opening','produced','consumed','imports','exports'].some(k=>!Number.isFinite(a[k])||a[k]<0))return false;}}
 if(data.goodsCompensation!=null){if(typeof data.goodsCompensation!=='object'||Array.isArray(data.goodsCompensation))return false;for(const [good,c] of Object.entries(data.goodsCompensation)){if(!owns(goods,good)||!data.goodsAccounts?.[good]||!c||typeof c!=='object'||Array.isArray(c))return false;for(const [category,value] of Object.entries(c))if(!['produced','consumed','imports','exports'].includes(category)||!Number.isFinite(value)||Math.abs(value)>Math.max(1,data.goodsAccounts[good][category])*Number.EPSILON*2)return false;}}
 return true;
}
function marketPrice(good){return G?.goodsPrices?.[good]||goods[good]||1;}
function goodsBalance(){
 const stocks=stockTotals();
 return Object.entries(G.goodsAccounts||{}).map(([good,a])=>({good,...a,stock:stocks[good],error:stocks[good]-expectedCommodityStock(good,a),price:marketPrice(good)}));
}
function commodityPriceReview(){
 if(G.day%30!==0)return;
 const stocks=stockTotals(),demand={grain:0,flour:0,food:G.stats.population*1.6,logs:0,timber:0,stone:G.projects.length*4,manufactures:G.stats.population*.12};
 for(const f of G.firms){if(f.closed)continue;const recipe=formulas[f.kind];if(recipe?.inp)demand[recipe.inp]+=(recipe.amount||0)*Math.max(.15,f.workers.length/Math.max(1,f.jobs));}
 for(const k of Object.keys(goods)){const cover=stocks[k]/Math.max(20,demand[k]),scarcity=clamp(1-cover/5,-1,1),target=goods[k]*(1+scarcity*.22)*Math.pow(clamp(G.regionalDemand,.4,1.3),.10);G.goodsPrices[k]=clamp(G.goodsPrices[k]*.88+target*.12,goods[k]*.65,goods[k]*1.55);}
}
