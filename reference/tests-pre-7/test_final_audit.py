"""Additional defect-specific tests for the final audited Android build."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from statistics import median
root=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True, executable_path=__import__('os').environ.get('TOWNLEDGER_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':960,'height':560})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content((root/'assets/index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'assets/style.css').read_text()+'</style>').replace('<script src="game.js"></script>',''))
    page.add_script_tag(content=(root/'assets/game.js').read_text())
    page.locator('#newTown').click()
    # Malformed loads do not replace running town or leave it unusable.
    validated=page.evaluate('''()=>{
      const raw=__townTest.save(),g=JSON.parse(raw),before=__townTest.get().total;
      const attempt=(mutate,why)=>{const copy=JSON.parse(raw);mutate(copy);if(__townTest.load(copy)!==false)throw Error('Accepted invalid '+why);if(__townTest.get().total!==before||__townTest.get().day!==g.day)throw Error('Damaged live town after '+why);};
      attempt(g=>g.buildings[0].x=-9,'plot');
      attempt(g=>g.buildings.push({...g.buildings[0],id:600}), 'duplicate plot');
      attempt(g=>g.households[1].people.push(g.households[0].people[0]), 'duplicate citizen');
      attempt(g=>g.banks[1].id=0,'bank collision');
      attempt(g=>g.firms[0].workers.push(999999),'worker reference');
      attempt(g=>g.people[0].hh=999999,'orphaned resident');
      __townTest.step(5);if(!Number.isFinite(__townTest.get().total))throw Error('town broke after rejected save');
      return ['invalid lot','duplicate building','duplicate resident','duplicate bank','bad worker','orphaned resident'];
    }''')
    print('ATOMIC SAVE IMPORT / REJECTION',validated,flush=True)
    # Both household and firm depositors receive their contract interest claims.
    bank=page.evaluate('''()=>{
      __townTest.reset();const state=JSON.parse(__townTest.save());let b=state.banks[0],f=state.firms[0];
      f.deposits={[b.id]:2000};f.cash-=2000;b.cash+=2000;
      if(!__townTest.load(state))throw Error('Could not load funded company deposit');
      const orig=JSON.parse(__townTest.save()),before=orig.firms[0].deposits[0];
      const totalBefore=__townTest.get().total;
      __townTest.step(1);
      const now=JSON.parse(__townTest.save()),after=now.firms[0].deposits[0];
      if(after<=before)throw Error('Firm savings did not earn interest');
      if(Math.abs(__townTest.get().total-totalBefore)>.01)throw Error('Interest minted money');
      return {depositBefore:before,depositAfter:after,received:after-before};
    }''')
    print('CORPORATE DEPOSITOR INTEREST',bank,flush=True)
    # Condition values should be pavement measurements, not the road-budget control.
    condition=page.evaluate('''()=>{
      const s=JSON.parse(__townTest.save());s.stats.roadCondition=39;s.policy.roadBudget=250;
      if(!__townTest.load(s))throw Error('Could not load pavement scenario');
      if(__townTest.road().quality!==39)throw Error('Dashboard substitutes road budget for condition');
      return __townTest.road().quality;
    }''')
    print('MEASURED ROAD QUALITY',condition,flush=True)
    # A long-running town must not accumulate an unbounded number of retired credit records.
    archive=page.evaluate('''()=>{
      __townTest.reset();let g=JSON.parse(__townTest.save());g.loans=[];
      for(let i=0;i<2600;i++)g.loans.push({id:i,bankId:0,ownerType:'firm',ownerId:0,original:200,balance:0,rate:.06,term:100,created:0,arrears:0,status:'repaid',paid:200});
      if(!__townTest.load(g))throw Error('Could not restore archival loans');
      __townTest.step(1);let state=JSON.parse(__townTest.save());
      if(state.loans.length>1800)throw Error('Retired loans not capped');
      const latest=__townTest.takeLoan('firm',1,2500,360);if(!latest)throw Error('Could not issue subsequent loan');
      state=JSON.parse(__townTest.save());if(new Set(state.loans.map(l=>l.id)).size!==state.loans.length)throw Error('Loan ID collision');
      return {before:2600,after:state.loans.length,newLoanId:latest.id};
    }''')
    print('BOUNDED CREDIT HISTORY',archive,flush=True)
    # Steady-state render cost before independent 2,000-resident test.
    page.evaluate('__townTest.reset()')
    render=[page.evaluate('__townTest.renderBench(25)') for _ in range(3)]
    print('960x560 MAP RENDER milliseconds per draw:',render,'median',median(render),flush=True)
    assert not errors,errors
    browser.close()
print('PASS new adversarial save, banking, road reporting, long-run memory and rendering checks')
