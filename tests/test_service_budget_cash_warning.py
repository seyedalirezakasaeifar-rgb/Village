"""The policy outlook explains actual preceding cash priorities without mutating a town."""
from pathlib import Path
import gzip, json
from test_mobile_rendering import ROOT, html
from playwright.sync_api import sync_playwright

FIXTURE = ROOT / 'docs/evidence/service-budget-warning8/fixtures/late-town-service-terminal.json.gz'
ARCHIVE = json.loads(gzip.open(FIXTURE, 'rt', encoding='utf-8').read())
SOURCE = (ROOT / 'assets/game.js').read_text()
PROBE = '''window.__cashWarn={pressure:serviceBudgetCashPressure,html:serviceBudgetOutlookHtml,range:serviceBudgetRange,policy:()=>G.policy,proposal:()=>draftPolicy,step:n=>__townTest.step(n),load:x=>__townTest.load(x),save:()=>__townTest.save(),state:()=>G,validate:()=>__townTest.validate(),money:totalMoney,pensionPaid:()=>G.households.reduce((n,h)=>n+(h.pension||0),0),watch:()=>{const original=fundCivicServices;window.__serviceBoundary=[];fundCivicServices=function(){window.__serviceBoundary.push(G.treasury);return original();};},enact:p=>{draftPolicy={...G.policy,...p};return enactPolicyPackage();}};'''
SCRIPT = SOURCE.replace('// SOURCE: 99-instrumentation.js', PROBE + '\n// SOURCE: 99-instrumentation.js')


def test_service_budget_cash_warning():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page(viewport={'width': 900, 'height': 900})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content(html)
        page.add_script_tag(content=SCRIPT)
        page.locator('#newTown').click()
        page.locator('#pause').click()
        assert page.evaluate('(archive)=>__cashWarn.load(archive)', ARCHIVE)

        # The read-only warning describes a completed state's actual shortfall.
        before = page.evaluate('''()=>({town:JSON.stringify(__cashWarn.state()),proposal:JSON.stringify(__cashWarn.proposal()),rng:__cashWarn.state().rngState,money:__cashWarn.money()})''')
        range_data = page.evaluate("()=>__cashWarn.range('educationBudget')")
        assert range_data['max'] > 500 and range_data['hardMax'] == 50000, range_data
        pressure = page.evaluate('__cashWarn.pressure()')
        after = page.evaluate('''()=>({town:JSON.stringify(__cashWarn.state()),proposal:JSON.stringify(__cashWarn.proposal()),rng:__cashWarn.state().rngState,money:__cashWarn.money()})''')
        assert before == after, 'Planning or rendering changed live simulation state'
        assert pressure is None, 'Cold-load planning should not invent a previous-day service record'

        # Record cash at the exact service boundary; positive closing cash must not hide zero cash then.
        page.evaluate('__cashWarn.watch()')
        page.evaluate('__cashWarn.step(1)')
        boundary = page.evaluate('window.__serviceBoundary[0]')
        before_warning = page.evaluate('''()=>({town:JSON.stringify(__cashWarn.state()),proposal:JSON.stringify(__cashWarn.proposal()),rng:__cashWarn.state().rngState,money:__cashWarn.money()})''')
        after_day = page.evaluate('__cashWarn.pressure()')
        html_text = page.evaluate('__cashWarn.html()')
        after_warning = page.evaluate('''()=>({town:JSON.stringify(__cashWarn.state()),proposal:JSON.stringify(__cashWarn.proposal()),rng:__cashWarn.state().rngState,money:__cashWarn.money()})''')
        assert boundary == 0, boundary
        assert after_day and after_day['endingCash'] > 0, after_day
        assert all(s['requested'] > s['paid'] for s in after_day['services']), after_day
        assert 'Recent cash shortfall' in html_text
        assert before_warning == after_warning, 'Warning or outlook changed live simulation state'
        page.locator('[data-panel=policies]').click()
        visible_warning = page.locator('#serviceBudgetOutlook').inner_text()
        assert 'Recent cash shortfall' in visible_warning and 'Health paid $0 of $70 requested' in visible_warning and 'School paid $0 of $90 requested' in visible_warning
        assert page.evaluate('__cashWarn.validate().ok')

        # A same-day policy edit must not rewrite payments already posted to the prior day's ledger.
        ledger_before = page.evaluate('''()=>JSON.stringify(__cashWarn.state().serviceCashEvidence)''')
        pension_receipt = page.evaluate('__cashWarn.pensionPaid()')
        assert abs(pension_receipt - after_day['pensionPaid']) < 1e-7, (pension_receipt, after_day)
        page.evaluate("__cashWarn.enact({pensionDaily:0})")
        unchanged_history = page.evaluate('''()=>({warning:__cashWarn.pressure(),ledger:JSON.stringify(__cashWarn.state().serviceCashEvidence),pension:__cashWarn.pensionPaid()})''')
        assert unchanged_history['ledger'] == ledger_before
        assert abs(unchanged_history['pension'] - pension_receipt) < 1e-7
        assert unchanged_history['warning']['pensionPaid'] == after_day['pensionPaid']

        # Current-format saves retain the evidence after serviceProvision's derived cache is cleared.
        current_save = page.evaluate('__cashWarn.save()')
        assert page.evaluate('(save)=>__cashWarn.load(save)', current_save)
        restored = page.evaluate('__cashWarn.pressure()')
        assert restored and restored['pensionPaid'] == after_day['pensionPaid']
        assert page.evaluate('()=>__cashWarn.state().serviceProvision===null')
        # A legacy archive with no immutable ledger omits the historical warning.
        legacy_save = page.evaluate('(save)=>{const a=JSON.parse(save);delete a.serviceCashEvidence;return JSON.stringify(a)}', current_save)
        assert page.evaluate('(save)=>__cashWarn.load(save)', legacy_save)
        assert page.evaluate('__cashWarn.pressure()') is None
        assert 'Recent cash shortfall' not in page.evaluate('__cashWarn.html()')
        assert page.evaluate('(save)=>__cashWarn.load(save)', current_save)

        # With an enacted, ordinary policy change releasing the earlier pension claim,
        # available pre-service cash funds the requested health and school purchases.
        replay = page.evaluate('''()=>{const start=__cashWarn.save();__cashWarn.step(1);const first=__cashWarn.save();__cashWarn.load(start);__cashWarn.step(1);const second=__cashWarn.save();return {same:first===second,first,second}}''')
        assert replay['same'], 'Saved service-cash evidence did not replay exactly'
        funded = page.evaluate('''()=>{const g=__cashWarn.state();return {cash:window.__serviceBoundary[window.__serviceBoundary.length-1],health:g.serviceProvision.health,school:g.serviceProvision.school,pressure:__cashWarn.pressure(),valid:__cashWarn.validate()}}''')
        assert funded['cash'] > 0, funded
        assert funded['health']['paid'] >= funded['health']['requested'] - .005, funded
        assert funded['school']['paid'] >= funded['school']['requested'] - .005, funded
        assert funded['pressure'] is None, funded
        assert funded['valid']['ok'], funded
        assert not errors, errors
        result = {
            'startDay': ARCHIVE['day'],
            'warningDay': after_day['day'],
            'serviceBoundaryCash': boundary,
            'warningDayClosingCash': after_day['endingCash'],
            'earlierSafetyOutreachPaid': after_day['publicPaid'],
            'pensionPaidBeforeServices': after_day['pensionPaid'],
            'unpaidRequests': [{'service': s['kind'], 'requested': s['requested'], 'paid': s['paid']} for s in after_day['services']],
            'scalableEducationSlider': range_data,
            'fundedIntervention': {'serviceBoundaryCash': funded['cash'], 'healthRequested': funded['health']['requested'], 'healthPaid': funded['health']['paid'], 'schoolRequested': funded['school']['requested'], 'schoolPaid': funded['school']['paid'], 'warningCleared': funded['pressure'] is None},
            'warningAndOutlookReadOnly': before_warning == after_warning,
            'visibleInPolicyPanelBeforeEnactment': True,
            'sameDayPolicyEditPreservesHistoricalPensions': unchanged_history['warning']['pensionPaid'] == after_day['pensionPaid'] and abs(unchanged_history['pension'] - pension_receipt) < 1e-7,
            'newSaveRetainsEvidenceAndLegacySaveOmitsWarning': bool(restored) and page.evaluate('()=>__cashWarn.state().serviceCashEvidence.version===1'),
            'exactSameDayLedgerReplay': replay['same'],
            'validTownAfterSteps': funded['valid']['ok'],
        }
        browser.close()
        return result


if __name__ == '__main__':
    print(json.dumps(test_service_budget_cash_warning(), indent=2))
