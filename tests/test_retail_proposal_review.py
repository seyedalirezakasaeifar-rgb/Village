"""A mall offer is reviewed before regional investors reserve capital."""
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright
import gzip, json

source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__retailReview={
 setup:()=>{__townTest.reset('settlement',42);for(const h of G.households)for(let j=0;j<18;j++){const p={id:G.people.length,name:'Review fixture resident',age:29,skill:.7,health:90,hh:h.id,job:-1,life:70,last:[]};G.people.push(p);h.people.push(p.id);}G.stats.marketConfidence=75;return {total:totalMoney(),treasury:G.treasury,region:G.region,shops:G.firms.filter(f=>!f.closed&&f.kind==='grocer').length,households:G.households.map(h=>[h.id,h.home,h.people.slice()]),titles:G.buildings.map(b=>[b.id,b.owner,b.title?.kind,b.title?.id]),fields:Object.entries(G.fieldOwner||{}),closed:G.firms.filter(f=>f.closed).map(f=>f.id)};},
 preview:()=>urbanRetailProposal('preview'),authorize:key=>urbanRetailProposal(true,key),bumpDay:()=>G.day++,footprint:p=>p.footprint.map(id=>({id,land:G.landUse?.[id]||0,plan:urbanDescriptor(id%T,id/T|0).plan,why:urbanPlacementReason(id%T,id/T|0,'grocer')})),access:p=>roadOffsets.some(([dx,dy])=>graph().parts[roadId(p.x+dx,p.y+dy)]===graph().mainPart),
 snapshot:()=>({total:totalMoney(),treasury:G.treasury,region:G.region,shops:G.firms.filter(f=>!f.closed&&f.kind==='grocer').map(f=>[f.id,f.building,f.workers.slice()]),households:G.households.map(h=>[h.id,h.home,h.people.slice()]),titles:G.buildings.map(b=>[b.id,b.owner,b.title?.kind,b.title?.id]),fields:Object.entries(G.fieldOwner||{}),closed:G.firms.filter(f=>f.closed).map(f=>f.id),projects:G.projects.filter(p=>p.retailCentre).map(p=>({id:p.id,remaining:p.remaining,escrow:p.urbanEscrow,staff:p.retailStaff,wage:p.retailWage,x:G.buildings.find(b=>b.id===p.id)?.x,y:G.buildings.find(b=>b.id===p.id)?.y,footprint:G.buildings.find(b=>b.id===p.id)?.footprint.slice()})),valid:validateTown()})
};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1280,'height':850});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html);page.add_script_tag(content=script);page.locator('#newTown').click();page.locator('#pause').click()
    before=page.evaluate('__retailReview.setup()')
    page.locator('[data-panel=construction]').click();page.locator('#urbanPlanningOffice>summary').click();page.locator('[data-urban-retail]').click()
    text=page.locator('#eventText').inner_text()
    assert 'six-tile site' in text and '534 residents' in text and 'existing centres count double' in text and 'not a guarantee or new spending' in text and 'regional capital' in text,text
    assert 'Invite investors at this site' in page.locator('#eventChoices').inner_text()
    beforeReview=page.evaluate('__townTest.save()')
    pending=page.evaluate('__retailReview.snapshot()');assert not pending['projects'] and pending['total']==before['total'] and pending['region']==before['region']
    page.locator('#eventDefer').click();cancel=page.evaluate('__retailReview.snapshot()')
    assert cancel['projects']==[] and cancel['total']==before['total'] and cancel['households']==before['households'] and cancel['titles']==before['titles'] and cancel['fields']==before['fields'] and page.evaluate('__townTest.save()')==beforeReview
    quote=page.evaluate('__retailReview.preview()');assert quote['ok']
    page.evaluate('__retailReview.bumpDay()');staleResult=page.evaluate('q=>__retailReview.authorize(q.reviewKey)',quote)
    assert not staleResult['ok'] and 'changed since this proposal review' in staleResult['reason']
    stale=page.evaluate('__retailReview.snapshot()');assert not stale['projects']
    page.locator('[data-urban-retail]').click();page.locator('[data-event-choice="0"]').click()
    opened=page.evaluate('__retailReview.snapshot()');assert len(opened['projects'])==1 and opened['projects'][0]['escrow']==28000,opened
    project=opened['projects'][0];assert len(project['footprint'])==6 and page.evaluate('p=>__retailReview.access(p)',project)
    tiles=page.evaluate('p=>__retailReview.footprint(p)',project)
    assert all(t['land']==0 and t['plan']!='agriculture' and not t['why'] for t in tiles),tiles
    assert opened['shops'] and all(not row[0] in opened['closed'] for row in opened['shops'])
    existingTitles=[row for row in opened['titles'] if row[0]!=project['id']]
    assert opened['households']==stale['households'] and existingTitles==stale['titles'] and opened['fields']==stale['fields']
    assert opened['valid']['ok'] and abs(opened['total']-before['total'])<.1 and opened['treasury']==stale['treasury']
    archive=page.evaluate('__townTest.save()');page.evaluate('__townTest.step(2)');continuation=page.evaluate('__townTest.save()')
    assert page.evaluate('s=>__townTest.load(s)',archive);page.evaluate('__townTest.step(2)');assert page.evaluate('__townTest.save()')==continuation
    natural=gzip.decompress((ROOT/'tests/fixtures/urban-retail-unfunded-labour.json.gz').read_bytes()).decode();assert page.evaluate('s=>__townTest.load(s)',natural)
    page.evaluate('__townTest.step(40)');beforeForecast=page.evaluate('__townTest.save()');blocked=page.evaluate('__retailReview.preview()')
    assert not blocked['ok'] and 'Connected legal sites do not have 180 residents' in blocked['reason'],blocked
    afterForecast=page.evaluate('__townTest.save()');assert afterForecast==beforeForecast,(set(json.loads(afterForecast))^set(json.loads(beforeForecast)),[(k,json.loads(beforeForecast).get(k),json.loads(afterForecast).get(k)) for k in json.loads(beforeForecast) if json.loads(beforeForecast).get(k)!=json.loads(afterForecast).get(k)][:8])
    assert not errors,errors
    print(json.dumps({'reviewShownBeforeCapitalCommit':True,'cancelReadOnly':True,'staleQuoteRejected':True,'ordinaryInvestorCommit':opened['projects'][0], 'existingSmallGrocersPreserved':len(opened['shops']),'titlesHouseholdsFieldsPreserved':True,'footprintTiles':tiles,'cashConserved':True,'exactReplay':True,'naturalSixYearCityBlocker':blocked,'blockedForecastReadOnly':True,'errors':errors},indent=2))
    browser.close()
