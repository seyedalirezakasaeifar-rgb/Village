# Scalable public-service authorizations

Base: `98a6f99618e27e7d30306a7f4c890ac019ef004a`, already containing the integrated urban, freight, transit and private-provider engine. Cherry-pick this change after that commit; do not replay older urban branches. No release/schema bump or new authoritative state is necessary: the existing `policy.healthBudget` and `policy.educationBudget` remain daily currency amounts.

## Behavior

The old immutable $500/day maximum made adequate public schools mathematically impossible in the naturally evolved 1,151-person regional town: the existing staffing standard costs $1,906.98/day. Both health and education now accept exact dollars and cents. A contextual slider stays at $500 for the initial 169-person town, grows with population-priced operating need, and includes any larger existing/proposed amount. The exact amount field supports $0–$50,000/day regardless of town size. The safety limit covers the existing maximum validated save population (8,000) at maximum legal wage ($90): schools need approximately $42,604/day. Shrinking population never cuts an authorization.

The mayor can draft the full public standard, the remaining school equivalent with today's actual private purchases, or the reachable public standard bounded by a 30-day cash plan. Every action stages the ordinary policy package; the mayor still reviews, enacts or discards it. Nothing automatically raises spending, credits the treasury, recruits workers, grants access or promises full coverage. The teaching-project shortcut uses the same authorization limit and continues to draft rather than enact.

Estimates price the existing five clinic staff per 350 / ten school staff per 260 resident standards, the current or staged wage floor and the existing 65% payroll share. Geographic/capacity access limits the reachable cost. Actual public purchases still use `purchaseCivicService()`, its qualified local staff, delayed regional recruitment, facility/road access and real cash. That engine and payment ordering are unchanged. Typing a large ceiling cannot charge more than genuine requested service need. Unused authorization remains municipal cash. A negative treasury remains a negative treasury, without free purchases.

The policy cash plan shows the full authorization ceiling, its bound at currently reachable health/school need, historical receipts and cash runway. It includes existing programme authorizations, pensions, wage subsidies, debt interest, relief, municipal replacement-home maintenance and active transit operating commitments. Receipts include the existing taxes, permits, transit fares and municipal housing rent. A staged minimum wage also reprices transit driver positions. The 30-day proposal uses historical daily receipts plus current positive cash / 30 minus other current-need commitments. This is explicitly an estimate, not a hard affordability guarantee: receipts, growth, recruitment, access and prices change. The mayor may still authorize a larger amount.

Public provision and the purchased-private-plus-public learning index are labelled separately; neither claims that all pupils are enrolled. A combined-gap proposal assumes today's private purchases persist, which they need not after public investment. When loading/enacting invalidates cached provision, the UI says no current purchase has been measured instead of reporting an observed zero. Live measurements resume on the next simulated purchase.

## Shared interfaces / UI coordination

`17-service-budget-plan.js` supplies:

- `PUBLIC_SERVICE_BUDGET_LIMIT` in foundation; `isServiceBudgetKey(key)`.
- `publicServiceBudgetEstimate(kind, policy)` for `health` or `school`: population, wage, full/reachable cost, remaining combined school gap, public facilities/access, measured public/private/combined equivalents, observed flag and pending recruitment day. Reads do not create staffing contracts or change cash.
- `serviceBudgetRange(key, policy)` → `{min,max,step,hardMax}`. Context max is presentation, never a cap applied to saved/current authorizations.
- `serviceBudgetOutlook(policy)` → full authorization `ceiling`, `currentNeed` bound, `dailyReceipts`, nonnegative cash available, deficit, runway and both service estimates.
- `serviceBudgetRecommendation(key, policy)` → proposal amount, 30-day cash envelope and source estimates/outlook.
- Strict `parseServiceBudget`, `validateServiceBudgetArchive` and `prepareServiceBudgetEnactment` block non-finite, negative, malformed and >$50,000 values before authoritative enactment/adoption. Missing legacy keys retain defaults; finite old amounts and numeric strings survive load. Higher authorizations round-trip without the old $500 clamp.

`98-service-budget-ui.js` supplies `serviceBudgetControlHtml`, `serviceBudgetEstimateHtml`, `serviceBudgetOutlookHtml`, `updateServiceBudgetControls` and `serviceBudgetMoney`. Preserve existing `input[type=range][data-policy=healthBudget|educationBudget]` hooks used by shared policy/service navigation. Exact numeric fields use `data-service-budget-amount`, separate from the old range listener. Proposal buttons use `data-service-budget-key` and `data-service-budget-preset=full|combined|cash`. The standard `enactPolicy`, `resetPolicy`, `draftSummary` and `draftPolicy` remain authoritative. CSS is isolated in `assets/service-budget.css` and linked after mayor8.css.

Hooks touch foundation policy bounds, early archive validation, the two service controls and package review card, the enactment guard/currency journal label, and the teaching-project shortcut's cap. Preserve the guard if redesigning package enactment. No changes to private-provider fields, freight dispatch ordering, transit topology, payroll or simulation prices.

## Evidence and practical limits

Source-bound output and actual-control screenshots: `docs/previews/service-budgets/` (manifest includes hashes). Reproduce with:

```
TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter python tests/test_service_budget_authorization.py
```

The exact existing regional checkpoint is loaded from `docs/previews/urban8/trajectories/regional-42-planned.json.gz`; no residents, funds, facilities or private clients are injected into this replay. The mayor drafts $1,907/day, discards it, drafts it again and enacts it through real controls. Enactment changes neither cash nor immediate service quality.

| Day | Population | School standard/day | Actual paid/day | Public equivalent | Private equivalent |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2162 | 1,151 | $1,906.98 | $500.00 | 26.22% | 9.30% |
| 2191 | 1,151 | $1,906.98 | $500.00 | 26.22% | 9.04% |
| 2192 | 1,151 | $1,906.98 | $1,906.98 | 100.00% | 0.00% |
| 2222 | 1,151 | $1,906.98 | $1,906.98 | 100.00% | 0.00% |
| 2312 | 1,168 | $1,935.15 | $1,907.00 | 98.55% | 0.17% |

Regional recruitment takes the existing 30 days. Private demand falls as funded public provision increases rather than remaining as a free additive bonus. Growth eventually exceeds the unchanged authorization; the game does not silently increase it. Treasury ends at $640,121.87 versus $689,121.08 at the checkpoint, with maximum conservation error under $0.000001. This is one intervention replay, not a guarantee that every future regional town can fund the standard.

The focused regression also verifies exact $1,907.50 staging/labels, discard and cent amounts, pure planning, staged wage cost, 22 invalid enactment attempts, 16 invalid archives with atomic rejection, old/missing keys and larger amount round-trips. Separate controlled conserved fixtures authorize $50,000 with zero and negative cash: no purchases or coverage are created. Actual preset/enact flows run at 1280×850, 390×844 and 320×568; number fields and buttons meet 44px height and controls have no horizontal overflow. Screenshots are inspected at desktop and 320px.

Existing catchment/recruitment/training, service-provision funding, private-market viability, archive schema and review-workflow tests pass. The existing three-seed policy experiment suite also passes with the source frozen; its full outputs retain the recession, recovery and restrictive-policy negative outcomes. No rendering, transport-performance or APK claims are made by this budget change.
