"""District history commits the observed value and cached facts stay fresh."""
from pathlib import Path
import hashlib, json
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT, html

source=(ROOT/'assets/game.js').read_text()
probe=r'''window.__districtObservation={
 seed:(days)=>{__townTest.reset('settlement',42);if(days)__townTest.step(days);const c=urbanSpatial();return {day:G.day,blocks:c.blocks,profiles:c.profiles,valid:validateTown()};},
 transition:(key)=>{const u=ensureUrban(),old=u.districts[key],rngBefore=rngState;if(!old)throw Error('district missing');old.character='Residential neighbourhood';delete old.proposed;delete old.proposedSince;const dates=[721,751,781,811],rows=[];for(const day of dates){G.day=day;urbanDistrictReview();const d=u.districts[key];rows.push({day,character:d.character,proposed:d.proposed||null,proposedSince:d.proposedSince??null,observed:urbanSpatial().profiles[key]?.character||null});}return {rows,rngBefore,rngAfter:rngState};},
 bankDeposit:(key)=>{const c=urbanSpatial(),before=c.profiles[key]?.bankDeposits,building=G.buildings.find(b=>b.kind==='bank'&&urbanBlockKey(b.x,b.y)===key&&!G.banks[b.bankId]?.closed),bank=building&&G.banks[building.bankId],h=G.households.find(v=>v.people.length&&v.cash>=1);if(!bank||!h)return null;const moneyBefore=totalMoney(),rngBefore=rngState,amount=depositTransfer(h,bank,1),fresh=urbanSpatial().profiles[key];return {before,after:fresh.bankDeposits,amount,moneyBefore,moneyAfter:totalMoney(),rngBefore,rngAfter:rngState};},
 incomeBoundary:(key)=>{const cached=urbanSpatial(),before=cached.blocks[key]?.perPersonIncome,day=G.day;dailyEconomy();const fresh=urbanSpatial(),block=fresh.blocks[key],expected=block.households.reduce((n,id)=>{const h=G.households[id];return n+Math.max(0,(h.income||0)-(h.tax||0));},0)/Math.max(1,block.residents);return {dayBefore:day,dayAfter:G.day,before,after:block.perPersonIncome,expected,sameCache:cached===fresh,rng:rngState,valid:validateTown()};},
 snapshot:()=>__townTest.save(),state:()=>({money:totalMoney(),rng:rngState}),
};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
results={'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1280,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html);page.add_script_tag(content=script);page.locator('#newTown').click();page.locator('#pause').click()
 town=page.evaluate('__districtObservation.seed(720)',None);assert town['valid']['ok'],town['valid']
 key=next((p['key'] for p in town['profiles'].values() if 'Market centre' in p['observedTags']),None);assert key,key
 transition=page.evaluate('k=>__districtObservation.transition(k)',key);rows=transition['rows']
 assert [r['character'] for r in rows[:3]]==['Residential neighbourhood']*3,rows
 assert rows[0]['proposed']=='Market centre' and rows[0]['proposedSince']==721,rows[0]
 assert rows[3]['character']==rows[3]['observed']=='Market centre' and rows[3]['proposed'] is None,rows[3]
 assert transition['rngBefore']==transition['rngAfter'],transition
 # Restore an ordinary live town before checking current-book and current-income
 # readers; descriptor calls are observational, while writers invalidate O(1).
 page.evaluate("__townTest.reset('settlement',42);__townTest.step(720)")
 baseline=page.evaluate('s=>__districtObservation.seed(0)',None);key=next(p['key'] for p in baseline['profiles'].values() if p['openBankBranches']>=2)
 before=page.evaluate('__districtObservation.state()');deposit=page.evaluate('k=>__districtObservation.bankDeposit(k)',key)
 assert deposit and deposit['amount']==1 and abs(deposit['after']-deposit['before']-1)<1e-6,deposit
 assert abs(deposit['moneyAfter']-deposit['moneyBefore'])<.01 and deposit['rngAfter']==deposit['rngBefore'],deposit
 income=page.evaluate('k=>__districtObservation.incomeBoundary(k)',key)
 assert income['dayBefore']==income['dayAfter'] and income['sameCache'] is False, income
 assert abs(income['after']-income['expected'])<1e-7,income
 assert income['valid']['ok'],income['valid']
 saved=page.evaluate('__districtObservation.snapshot()');state=page.evaluate('__districtObservation.state()');
 page.evaluate('__districtObservation.seed(0)')
 assert page.evaluate('s=>__townTest.load(s)',saved)
 stateAfter=page.evaluate('__districtObservation.state()');assert state==stateAfter,(state,stateAfter)
 assert not errors,errors;results.update({'transition':rows,'bankDepositMutationRefresh':deposit,'sameDayIncomeRefresh':income,'readOnlyStateStable':True,'errors':errors});browser.close()
(ROOT/'docs/previews/urban8').mkdir(parents=True,exist_ok=True)
(ROOT/'docs/previews/urban8/profile-observation-contract.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS exact 90-day character transition and same-day bank/income observation freshness')
