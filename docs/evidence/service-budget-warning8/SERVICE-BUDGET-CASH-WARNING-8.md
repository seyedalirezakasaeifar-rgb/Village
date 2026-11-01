# Public-service cash warning and integrated-source check

## Scope and source

Verified against the 8.0 integration base `ca0c6d07af3cdd380aa42b624bb66d95645edfce`. The test resumes a generated 721-resident town archive at day 50,681 from `fixtures/late-town-service-terminal.json.gz`; it advances the town using the integrated economy code and records the exact treasury at the civic-purchase boundary. The imported archive is a synthetic QA state from an earlier study, not a live user save. The old study's service diagnosis was not treated as proof of current behavior.

The earlier report's claim that public-service sliders were capped at $500/day is stale for this integration. Here the education slider scales to $1,500/day for this town and its validation ceiling is $50,000/day. This run found no integrated $500 authorization cap.

## Integrated-source replay

On day 50,682, the exact service-purchase boundary had $0 in the municipal treasury. Recorded safety/outreach payroll had used $331.92 and pension payments another $194.51 before care purchases. Health requested $70 and school requested $90; both were paid $0. The treasury later closed that day at $327.90, so a closing-balance or slider-only view could make the already-missed purchases hard to understand.

The policies outlook now shows a short last-completed-day warning when health or school had a requested amount that was not fully paid. It reports the prior safety/outreach payroll, pensions, cash at the service-purchase boundary, requested and paid amounts for each affected service, and closing treasury. It explicitly warns that higher authorization by itself may not increase purchases while earlier cash commitments persist. It is a read-only diagnostic, not a forecast; it disappears after a fully funded day. It does not recommend a particular austerity policy.

As a controlled causality check, the test used the normal policy-enactment path to set pension authorization to $0 for one day. This released cash before the service phase: $236.17 was available, health paid its full $70 request, school paid its full $90 request, and the warning cleared. This deliberately severe one-day experiment demonstrates the cash-order mechanism; it is not a recommendation to suspend pensions.

## Historical-payment integrity follow-up

Review diagnostic `c0f4f6b10704ce0468e508082015ae78c48a3128` found that the first warning version reconstructed past pension payments using the current policy. Enacting `pensionDaily=0` on the same day therefore changed the displayed historical payment from $194.51 to $0 without advancing simulation time. That version is superseded by the follow-up, which records actual public-payroll cash deltas, pension payment, service-boundary cash, service requests/payments, and end-of-day treasury during the completed simulation day. Policy edits do not rewrite these recorded values. The record is included in saves; a legacy archive lacking the record simply has no historical warning until a new day is simulated.

The regression enacts the pension policy change without advancing time and verifies that both the household payment record and warning remain at $194.51. A save/load roundtrip preserves the evidence even though the derived `serviceProvision` cache is cleared; deleting the evidence to emulate an old save omits the warning rather than estimating historical amounts. Two continuations from the same saved day produce byte-identical saved archives, including the new record.

## Checks

`python tests/test_service_budget_cash_warning.py` passed on the integrated continuation. It checks the zero-cash service boundary despite positive closing cash, a positive-cash fully funded path, the large-town scalable slider range, warning visibility in the policy panel before enactment, disappearance after purchases recover, same-day policy-change fidelity, current and legacy save behavior, exact save replay, town validation, and byte-for-byte unchanged simulation/proposal/RNG state while planning and rendering the warning. No cash, people, or goods are injected.

Also passed `python tools/assemble.py`, `python -m py_compile tests/test_service_budget_cash_warning.py`, `node --check assets/game.js`, and `git diff --check`. No fiscal coefficients or spending priorities changed. The fixture is one generated late-town state; this test verifies warning accuracy and one causal recovery path, not long-run fiscal balance or general city solvency.
