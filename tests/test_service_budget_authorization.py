"""Exact staged service dollars, real regional recruitment and bounded cash purchases."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import gzip,json,hashlib
OUT=ROOT/'reports/service-budgets';OUT.mkdir(parents=True,exist_ok=True)
source=(ROOT/'assets/game.js').read_text()
probe='''window.__budget={town:()=>G,estimate:publicServiceBudgetEstimate,range:serviceBudgetRange,outlook:serviceBudgetOutlook,recommend:serviceBudgetRecommendation,parse:parseServiceBudget,money:totalMoney,draft:(k,v)=>{draftPolicy[k]=v;},enact:enactPolicyPackage,proposal:()=>draftPolicy,purchase:purchaseCivicService,refresh:()=>{recompute();serviceAccessCaches.clear();}};'''
script=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js')
result={'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
def open_policies(p):
 if p.locator('#panel').is_visible() and p.locator('[data-panel=policies]').evaluate("e=>e.classList.contains('active')"):p.locator('#panelClose').click()
 p.locator('[data-panel=policies]').click();p.locator('summary',has_text='Government services').click()
regional=gzip.open(ROOT/'docs/previews/urban8/trajectories/regional-42-planned.json.gz','rt').read()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':1280,'height':850});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click()
 result['smallTown']=p.evaluate('''()=>{__townTest.reset('settlement',42);const before=__townTest.save(),e=__budget.estimate('school'),r=__budget.range('educationBudget'),higher=__budget.estimate('school',{...__budget.town().policy,minWage:50});if(Math.abs(higher.full/e.full-50/28)>.000001)throw Error('Staged wages missing from estimate');for(let i=0;i<5;i++){__budget.outlook();__budget.recommend('educationBudget');}if(before!==__townTest.save())throw Error('Planning mutated town');if(r.max!==500||r.hardMax!==50000)throw Error('Small range');return {population:e.population,required:e.full,range:r,pure:true};}''')
 open_policies(p)
 field=p.locator('[data-service-budget-amount=educationBudget]');field.fill('1907.50');assert p.evaluate('__budget.proposal().educationBudget')==1907.5;assert p.evaluate('__townTest.get().policy.educationBudget')==90
 assert p.locator('#show-educationBudget').inner_text()=='$1,907.50'
 assert float(p.locator('[data-policy=educationBudget]').get_attribute('max'))>=1907.5
 p.locator('#resetPolicy').click();assert p.evaluate('__townTest.get().policy.educationBudget')==90
 p.locator('summary',has_text='Government services').click();field=p.locator('[data-service-budget-amount=educationBudget]')
 for invalid in ['','-1','50001','1e309']:
  field.fill(invalid);assert p.locator('#enactPolicy').is_disabled(),invalid
  assert p.evaluate('__townTest.get().policy.educationBudget')==90
  assert field.get_attribute('aria-invalid')=='true'
 field.fill('');p.locator('[data-policy=educationBudget]').fill('120');assert field.input_value()=='120' and field.get_attribute('aria-invalid')=='false'
 field.fill('120.25');p.locator('#enactPolicy').click();assert p.evaluate('__townTest.get().policy.educationBudget')==120.25
 result['validation']=p.evaluate('''()=>{let n=0;for(const key of ['educationBudget','healthBudget'])for(const value of [Infinity,NaN,-1,50000.01,null,true,'','Infinity','NaN',{},[]]){const before=__townTest.save();__budget.draft(key,value);__budget.enact();if(__townTest.save()!==before)throw Error('Invalid enact changed state '+value);__budget.draft(key,__budget.town().policy[key]);n++;}__budget.draft('educationBudget',__budget.town().policy.educationBudget);const before=__townTest.save();for(const key of ['educationBudget','healthBudget'])for(const value of [50001,-1,null,'Infinity','NaN',true,{},[]]){const g=JSON.parse(before);g.policy[key]=value;if(__townTest.load(g)||before!==__townTest.save())throw Error('Invalid archive accepted or mutated');}for(const value of [0,500,1907.5,'1907.5',50000]){const g=JSON.parse(before);g.policy.educationBudget=value;if(!__townTest.load(g)||__budget.town().policy.educationBudget!==Number(value))throw Error('Valid archive budget lost');}const legacy=JSON.parse(before);delete legacy.policy.educationBudget;if(!__townTest.load(legacy)||__budget.town().policy.educationBudget!==90)throw Error('Legacy default lost');return {invalidEnact:n,invalidArchives:16,legacyMissing:true,higherBudgetRoundtrip:true};}''')
 assert p.evaluate('(s)=>__townTest.load(s)',regional)
 result['regionalBefore']=p.evaluate("()=>({day:__budget.town().day,population:__budget.town().stats.population,treasury:__budget.town().treasury,school:__budget.estimate('school'),outlook:__budget.outlook()})".replace('G.', '__budget.town().'))
 # Actual presets, discard and enact. Funding takes existing recruitment time.
 open_policies(p)
 before=p.evaluate('__townTest.save()');p.locator('[data-service-budget-key=educationBudget][data-service-budget-preset=full]').click()
 assert p.evaluate('__budget.proposal().educationBudget')==1907
 assert p.evaluate('__townTest.save()')==before
 p.locator('#resetPolicy').click();assert p.evaluate('__townTest.save()')==before
 p.locator('summary',has_text='Government services').click();p.locator('[data-service-budget-key=educationBudget][data-service-budget-preset=full]').click();p.locator('#enactPolicy').click()
 assert p.evaluate('__townTest.get().policy.educationBudget')==1907
 assert p.evaluate("__budget.estimate('school').publicCoverage")<.27
 result['regionalTrajectory']=p.evaluate('''()=>{const total=__budget.money(),out=[];for(const days of [1,29,1,30,90]){__townTest.step(days);const g=__budget.town(),s=g.serviceProvision.school,e=__budget.estimate('school'),v=__townTest.validate();if(!v.ok||Math.abs(total-__budget.money())>.05)throw Error('Invalid conserved budget run '+v.issues.join(';'));if(s.paid>g.policy.educationBudget+.001||s.coverage>1.000001||s.coverage>s.accessCoverage+.001)throw Error('Unfunded benefit');if(Math.abs(e.combinedCoverage-Math.min(1,e.publicCoverage+e.privateCoverage))>.000001)throw Error('Combined metrics');out.push({day:g.day,population:g.stats.population,treasury:g.treasury,authorized:g.policy.educationBudget,required:s.required,paid:s.paid,publicCoverage:s.coverage,privateCoverage:e.privateCoverage,combined:e.combinedCoverage,staffing:s.staffing,education:g.education,cashError:__budget.money()-total});}return out;}''')
 assert result['regionalTrajectory'][0]['publicCoverage']<.5
 assert result['regionalTrajectory'][2]['publicCoverage']>.9
 result['cashConstraint']=p.evaluate('''()=>{__townTest.reset('settlement',42);const g=__budget.town(),total=__budget.money();g.region+=g.treasury;g.treasury=0;__budget.draft('educationBudget',50000);__budget.enact();for(const p of g.people){p.publicIncome=0;p.previousPublicRole='';}const ratio=__budget.purchase('school',50000),s=g.serviceProvision.school;if(ratio!==0||s.paid!==0||g.treasury!==0||Math.abs(total-__budget.money())>.001)throw Error('Empty treasury supplied free service');g.treasury=-100;g.region+=100;const negativeRecommendation=__budget.recommend('educationBudget').amount,negativeRatio=__budget.purchase('school',50000);if(negativeRatio!==0||g.treasury!==-100||negativeRecommendation!==0||Math.abs(total-__budget.money())>.001)throw Error('Negative cash budget fabricated provision');return {controlledCashFixture:true,authorized:s.authorized,paid:s.paid,coverage:s.coverage,unused:s.unspent,negativeCashPreserved:g.treasury,negativeRecommendation,conserved:true};}''')
 # Capture the actual regional budget controls at common screen widths.
 result['screens']=[]
 for w,h in [(1280,850),(390,844),(320,568)]:
  p.set_viewport_size({'width':w,'height':h});assert p.evaluate('(s)=>__townTest.load(s)',regional);p.evaluate('__townTest.step(1)');open_policies(p);p.locator('#serviceBudgetAmount-educationBudget').scroll_into_view_if_needed();p.screenshot(path=str(OUT/f'budget-{w}x{h}.png'))
  screen=p.evaluate('''()=>{const e=document.querySelector('[data-service-budget-control=educationBudget]'),r=e.getBoundingClientRect(),amount=e.querySelector('[data-service-budget-amount]').getBoundingClientRect(),buttons=[...e.querySelectorAll('button')].map(b=>b.getBoundingClientRect());return {width:innerWidth,control:{x:r.x,right:r.right},amountHeight:amount.height,minButtonHeight:Math.min(...buttons.map(r=>r.height)),overflow:e.scrollWidth>e.clientWidth+2};}''')
  assert not screen['overflow'] and screen['control']['x']>=0 and screen['control']['right']<=w+1 and screen['amountHeight']>=44 and screen['minButtonHeight']>=44,screen
  full=p.locator('[data-service-budget-key=educationBudget][data-service-budget-preset=full]');full.scroll_into_view_if_needed();p.screenshot(path=str(OUT/f'budget-estimate-{w}x{h}.png'));full.click();assert p.evaluate('__budget.proposal().educationBudget')==1907;p.locator('#enactPolicy').click();assert p.evaluate('__townTest.get().policy.educationBudget')==1907;screen['actualPresetAndEnact']=True
  result['screens'].append(screen)
 assert not errors,errors
 result['errors']=errors;b.close()
(OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
