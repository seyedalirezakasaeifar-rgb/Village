# Integration follow-up: clear map and independent teaching project

This work is reconciled on `cae1bf426b0b1b534319415e3eacaa25972fa916`, preserving the integrated renderer, private institution ownership/payments/escrow, cached service access, schema 7 and all daily/archive hooks. It lives on `codex/8-player-experience-integrated`; the original phase-two-only checkpoint remains on `codex/8-player-experience`.

Final assembled source SHA-256: `6a770b26dc99ece160a4ef9883730f92498f4c0fdd20bbf217e533a3f878a798`.

## Map hierarchy

The original newspaper, ambition panel and economy panel covered much of a small landscape map simultaneously. They now live inside one optional **Town signals** disclosure. Its collapsed view displays the current actionable economic headline, pause state and number of active civic projects. All original information and newspaper/economy links remain available, with their original elements and focus restoration.

The collapsed disclosure occupies 14.1% of the map at 568×320, 6.9% at 844×390 and 6.3% at 390×844. This is measured rectangle area in the test, not a subjective visibility score. It expands only on request, collapses with Escape/Android Back after higher UI layers close, and hides during construction, land surveying or an open report. Header updates reuse existing computed text and avoid another economic scan. Expanding/collapsing changes no game accounts, policies or progression.

Source: `src/98-status-deck.js`; styles append to the existing `assets/mayor8.css`, requiring no additional HTML link. It moves existing nodes rather than duplicating their controls. `tests/test_map_hierarchy.py` now explicitly opens the disclosure before using its retained newspaper/economy actions.

## Public and independent teaching are distinct project routes

The school-to-work project now offers a genuine independent route through the stable provider API in `docs/engineering/PRIVATE-SERVICES-8.md`:

- The named household must contain an eligible learner according to `privateEligiblePupil()`.
- Its explicit proposal button uses the existing `data-private-invite="school"` handler and `seekPrivateServiceInvestment()`; investors still assess demand, staffing, financing and price. No municipal construction grant is introduced.
- Licensing, tuition ceilings and targeted vouchers use the existing staged policy UI. Provider construction, escrow, ownership, fees, staff and defaults remain entirely in the lead’s private-service model.
- Independent completion requires **30 quality-adjusted purchased learner-days for the named household**, at least one actual fee-funded term in town, current purchased household teaching and a 20-day authorized spending reserve. This respects the model’s distinction between private learner equivalents and the public resident-based coverage index; it does not demand a private-only household satisfy a public 60% resident target.
- Public/network projects recognize real combined public/private completions using `programmeMetrics().training`. Older project archives without `trainingScope` retain their earlier public-only counter meaning. New scopes are explicit (`all` or `private`); unknown scopes are rejected.

Additive project fields: `trainingScope` and `learning`. No economic save schema change is required beyond the integration’s existing schema 7. The project remains a record of actual provision, not an independent ledger.

The controlled private-route test uses the lead’s viable starting affordability/qualification conditions, then real proposal controls, independently financed construction, escrow, qualified staffing, household purchases and private learning. It reserved $6,000 of private working capital, spent **$0 municipal capital at invitation**, and earned its record on simulated day 195 with 361.8 purchased learner-days and real fee-funded terms. This is a controlled integration demonstration, not a guarantee that every town can attract or sustain a school.

## Verification at the final source

Seventeen test invocations passed, recorded in `reports/civic-projects/acceptance.json`:

- Five civic project tests: actual capital/trade/control journey; real import restriction, map-tap bakery and public teaching recovery; 43-delivery observer overflow; independent teaching route; legacy counter meanings.
- Mayor journey, three direction-rule fixtures and scenario programme.
- Private-service matched controls, affordability/vouchers/learning/closure, and actual school and brigade entry/construction/payment controls.
- Compact status disclosure, map hierarchy, live-status update discipline, seven mobile layouts, regional freight/contracts and district choices.

The original phase-two tests pass after reconciliation with private ownership and graphics. Final map screenshots show the integrated art with the consolidated overlay. The new map test also verifies economic-state independence, action/focus retention and survey/placement clearance. Survey reviews support both direct commissioning and a cancelled/real map-tap build; successful manual placement is attached to its project without repeating the purchase.

Integration hooks for civic projects remain those in `CIVIC-PROJECTS-DEVELOPMENT.md`. Rebase conflicts were resolved by retaining `privateServiceInvestmentDay()` alongside `civicProjectsDay()`, and retaining `validatePrivateServices()` alongside project and journey validation. The generated bundle was reassembled from all integrated modules.

**Freight notification contract:** the project observer currently recognizes a tracked shipment removed by the existing successful-arrival settlement. If later logistics changes also remove cancelled/lost shipments, call `civicProjectRecordArrival(order)` explicitly only on successful delivery and remove the before/after inference. The observer never moves money or goods.

Remaining limits: no physical Android test or new APK; no assertion of a multi-hour human play session or universal district/provider balance. The default economy’s tendency toward very high long-run employment still needs difficulty work. These additions supply concrete commitments and a clearer map, not evidence that the entire game has reached studio quality.
