"""Matched real-inventory import interruption and recovery under connected roads."""
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright
import hashlib, json

source = (ROOT / 'assets/game.js').read_text()
probe = r'''
window.__foodShockBase=(scenario,seed)=>{__townTest.reset(scenario,seed);__townTest.step(60);return __townTest.save()};
window.__foodShockRun=(saved,mode)=>{
 if(!__townTest.load(saved))throw Error('Matched food-shock checkpoint rejected');
 const start=totalMoney(),startDay=G.day,homePopulation=G.stats.population,stockoutStart={},stockoutDurations=[],daily=[],errors=[];
 const measure=(phase,dayInPhase)=>{
  __townTest.step(1);const groceries=G.firms.filter(f=>f.kind==='grocer'&&!f.closed),shopsWithFood=groceries.filter(f=>(f.stock.food||0)>.01).length,grocerStock=groceries.reduce((n,f)=>n+(f.stock.food||0),0),prices=groceries.map(f=>f.price).filter(Number.isFinite),wages=G.firms.filter(f=>!f.closed&&f.workers.length).map(f=>workerIncome(f)),foodGoods=goodsBalance().filter(x=>['grain','flour','food'].includes(x.good)),households=G.households.filter(h=>h.people.length),wallets=households.map(h=>householdLiquidity(h)/Math.max(1,h.people.length)).sort((a,b)=>a-b),foodSpend=households.reduce((n,h)=>n+(h.food||0),0),essential=households.reduce((n,h)=>n+(h.essentialDue||0),0);
  for(const f of groceries){if((f.stock.food||0)<=.01){if(stockoutStart[f.id]==null)stockoutStart[f.id]=G.day;}else if(stockoutStart[f.id]!=null){stockoutDurations.push({firm:f.id,days:G.day-stockoutStart[f.id]});delete stockoutStart[f.id];}}
  const outCount=groceries.filter(f=>(f.stock.food||0)<=.01).length;
  const maxGoodsError=Math.max(...goodsBalance().map(x=>Math.abs(x.error||0)));if(maxGoodsError>.01)errors.push({day:G.day,kind:'goods',maxGoodsError});
  const statements=G.firms.filter(f=>!f.closed&&f.operating?.netProfit!=null).map(f=>{const o=f.operating;return Math.abs(o.sales+(o.otherIncome||0)-o.costOfGoods-o.payroll-o.otherCosts-o.profitTax-o.netProfit)});const maxStatementError=Math.max(0,...statements);if(maxStatementError>.001)errors.push({day:G.day,kind:'statement',maxStatementError});
  if(!validateTown().ok)errors.push({day:G.day,kind:'validation'});
  const imports=G.market.imports||0,shipments=(G.regionalTrade?.shipments||[]).filter(o=>o.direction==='import').reduce((n,o)=>n+o.qty,0),medianPrice=prices.length?prices.sort((a,b)=>a-b)[prices.length>>1]:null,upstream={grain:G.firms.filter(f=>!f.closed&&f.kind==='farm').reduce((n,f)=>n+(f.stock.grain||0),0),flour:G.firms.filter(f=>!f.closed&&f.kind==='mill').reduce((n,f)=>n+(f.stock.flour||0),0),bakeryFood:G.firms.filter(f=>!f.closed&&f.kind==='bakery').reduce((n,f)=>n+(f.stock.food||0),0)},retailProfit=groceries.reduce((n,f)=>n+(f.netProfit||0),0),retailPayroll=groceries.reduce((n,f)=>n+(f.payroll||0),0),retailRevenue=groceries.reduce((n,f)=>n+(f.operating?.sales||0),0);
  daily.push({day:G.day,phase,dayInPhase,importsEnabled:G.policy.imports,grocerStock,shops:groceries.length,shopsWithFood,stockoutStores:outCount,unmetFood:G.market.unmetFood||0,foodDisconnected:G.market.foodDisconnected||0,foodImportsValue:imports,foodCargo:shipments,foodWholesale:marketPrice('food'),grainWholesale:marketPrice('grain'),flourWholesale:marketPrice('flour'),retailPrice:medianPrice,cpi:G.market.cpi,inflation:G.market.inflation,employment:G.stats.employment,employed:G.stats.employed,wage:wages.length?wages.reduce((a,b)=>a+b,0)/wages.length:null,payroll:G.firms.reduce((n,f)=>n+(f.payroll||0),0),retailProfit,retailPayroll,retailRevenue,retailMargin:retailRevenue?retailProfit/retailRevenue:0,upstream,hardship:G.stats.hardship,population:G.stats.population,medianWallet:wallets.length?wallets[wallets.length>>1]:0,lowWallet:wallets[0]||0,householdFoodSpend:foodSpend,essentialCost:essential,foodToEssentials:essential?foodSpend/essential:0,stockFood:foodGoods.find(x=>x.good==='food')?.stock||0,goodsError:maxGoodsError,cash:totalMoney()});
 };
 for(let d=1;d<=240;d++){
  const recover=mode==='freeze-recover'&&d===121;if(recover)__townTest.set('imports',true);
  if(mode==='freeze-recover'&&d===1)__townTest.set('imports',false);
  measure(mode==='freeze-recover'?(d<=120?'supplier-interrupted':'recovery'):(d<=120?'connected':'connected-continuation'),d<=120?d:d-120);
 }
 for(const f of Object.keys(stockoutStart))stockoutDurations.push({firm:+f,days:G.day+1-stockoutStart[f],ongoing:true});
 const rows=daily,phase=(name)=>rows.filter(x=>x.phase===name),summarize=list=>{if(!list.length)return null;const last=list[list.length-1],max=(k)=>Math.max(...list.map(x=>x[k]||0)),min=(k)=>Math.min(...list.map(x=>x[k]||0)),mean=(k)=>list.reduce((n,x)=>n+(x[k]||0),0)/list.length;return{days:list.length,startDay:list[0].day,endDay:last.day,openingGrocerStock:list[0].grocerStock,endingGrocerStock:last.grocerStock,lowestGrocerStock:min('grocerStock'),stockoutStoreDays:list.reduce((n,x)=>n+x.stockoutStores,0),townStockoutDays:list.filter(x=>x.shopsWithFood===0).length,unmetFoodDays:list.filter(x=>x.unmetFood>.01).length,unmetFoodMax:max('unmetFood'),unmetFoodTotal:list.reduce((n,x)=>n+x.unmetFood,0),averageUnmetFood:mean('unmetFood'),foodDisconnectedDays:list.filter(x=>x.foodDisconnected>0).length,retailPriceStart:list[0].retailPrice,retailPriceEnd:last.retailPrice,foodWholesaleStart:list[0].foodWholesale,foodWholesaleEnd:last.foodWholesale,cpiStart:list[0].cpi,cpiEnd:last.cpi,averageWage:mean('wage'),wageStart:list[0].wage,wageEnd:last.wage,payrollStart:list[0].payroll,payrollEnd:last.payroll,retailMarginStart:list[0].retailMargin,retailMarginEnd:last.retailMargin,retailProfitAverage:mean('retailProfit'),retailPayrollAverage:mean('retailPayroll'),upstreamStart:list[0].upstream,upstreamEnd:last.upstream,employmentStart:list[0].employment,employmentEnd:last.employment,hardshipStart:list[0].hardship,hardshipEnd:last.hardship,populationStart:list[0].population,populationEnd:last.population,lowWalletStart:list[0].lowWallet,lowWalletEnd:last.lowWallet,foodToEssentialsStart:list[0].foodToEssentials,foodToEssentialsEnd:last.foodToEssentials,cashDrift:last.cash-list[0].cash,maxGoodsError:max('goodsError')};};
 return{mode,scenario:G.scenario,seed:G.worldSeed,startDay,startPopulation:homePopulation,phases:{connected:summarize(phase('connected')),connectedContinuation:summarize(phase('connected-continuation')),interrupted:summarize(phase('supplier-interrupted')),recovery:summarize(phase('recovery'))},stockoutDurations,points:daily.filter(x=>x.dayInPhase%15===0||x.dayInPhase===1),errors,valid:validateTown(),goods:goodsBalance(),cashDrift:totalMoney()-start,endingDay:G.day};
};'''

rows = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page()
    page.set_default_timeout(180000)
    page_errors=[]
    page.on('pageerror',lambda e:page_errors.append(str(e)))
    page.set_content(html)
    page.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'))
    page.locator('#newTown').click();page.locator('#pause').click()
    for scenario,seed in [('settlement',42),('regional',909)]:
        saved=page.evaluate('o=>__foodShockBase(o.scenario,o.seed)',{'scenario':scenario,'seed':seed})
        baseline=page.evaluate('s=>__foodShockRun(s,"connected")',saved)
        shock=page.evaluate('s=>__foodShockRun(s,"freeze-recover")',saved)
        replay=page.evaluate('s=>__foodShockRun(s,"freeze-recover")',saved)
        assert json.dumps(shock,sort_keys=True)==json.dumps(replay,sort_keys=True), 'Shock/recovery replay differed'
        assert not baseline['errors'] and not shock['errors'] and baseline['valid']['ok'] and shock['valid']['ok']
        assert abs(baseline['cashDrift'])<.1 and abs(shock['cashDrift'])<.1
        assert max(abs(x['error']) for x in shock['goods'])<.01
        rows.append({'scenario':scenario,'seed':seed,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'baseline':baseline,'shockRecovery':shock})
        print(scenario,seed,'stockout-days',shock['phases']['interrupted']['townStockoutDays'],'unmet-days',shock['phases']['interrupted']['unmetFoodDays'],'retail',shock['phases']['interrupted']['retailPriceStart'],shock['phases']['interrupted']['retailPriceEnd'],'recovery unmet',shock['phases']['recovery']['unmetFoodDays'],flush=True)
    assert not page_errors,page_errors
    browser.close()

out=ROOT/'reports/food-shortage-recovery';out.mkdir(exist_ok=True)
(out/'results.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'rows':rows,'browserErrors':page_errors},indent=2)+'\n')
print('PASS matched connected/import-interrupted/recovery histories, daily cash/goods/statements, town validity and exact replay')
