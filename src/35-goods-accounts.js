function stockTotals(){
 const totals=Object.fromEntries(Object.keys(goods).map(k=>[k,0]));
 for(const f of G.firms)for(const k of Object.keys(goods))totals[k]+=Number(f.stock[k])||0;
 for(const s of G.freight||[])totals[s.good]=(totals[s.good]||0)+s.qty;
 return totals;
}
function ensureGoodsAccounts(){
 if(!G.goodsAccounts){const opening=stockTotals();G.goodsAccounts=Object.fromEntries(Object.keys(goods).map(k=>[k,{opening:opening[k],produced:0,consumed:0,imports:0,exports:0}]));}
 G.goodsPrices=G.goodsPrices||{...goods};
}
function goodsEntry(good,category,qty){if(!(qty>0)||!G.goodsAccounts?.[good])return;G.goodsAccounts[good][category]+=qty;}
function marketPrice(good){return G?.goodsPrices?.[good]||goods[good]||1;}
function goodsBalance(){
 const stocks=stockTotals();
 return Object.entries(G.goodsAccounts||{}).map(([good,a])=>({good,...a,stock:stocks[good],error:stocks[good]-(a.opening+a.produced+a.imports-a.consumed-a.exports),price:marketPrice(good)}));
}
function commodityPriceReview(){
 if(G.day%30!==0)return;
 const stocks=stockTotals(),demand={grain:0,flour:0,food:G.stats.population*1.6,logs:0,timber:0,stone:G.projects.length*4,manufactures:G.stats.population*.12};
 for(const f of G.firms){if(f.closed)continue;const recipe=formulas[f.kind];if(recipe?.inp)demand[recipe.inp]+=(recipe.amount||0)*Math.max(.15,f.workers.length/Math.max(1,f.jobs));}
 for(const k of Object.keys(goods)){const cover=stocks[k]/Math.max(20,demand[k]),scarcity=clamp(1-cover/5,-1,1),target=goods[k]*(1+scarcity*.22)*Math.pow(clamp(G.regionalDemand,.4,1.3),.10);G.goodsPrices[k]=clamp(G.goodsPrices[k]*.88+target*.12,goods[k]*.65,goods[k]*1.55);}
}
