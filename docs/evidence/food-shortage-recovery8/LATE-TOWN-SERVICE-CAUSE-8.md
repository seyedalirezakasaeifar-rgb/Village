# Why public health and school coverage reached zero

## Scope and source

This is a separate current-source continuation of the retained synthetic QA archive from `codex/8-session-soak`, not the ordinary-hour performance soak. It starts from the same archive hash (`ad6256fd85d4146fda9eeac0b16d5b182ed352c23bbd96af3b320553c29ce786`, day 41,681, 778 residents) and advances 25 years with council choices suppressed. The service diagnostic uses the current bundle from `0ba258d9a27e29bbba3e20110bccbe217629c268` (bundle SHA-256 `2fceb86f38436e7698be260a22baf415421c84875389c13b94f99c961976cdbc`). Its independently evolved endpoint is preserved in `late-town-service-diagnosis.json`; the same terminal archive seeds all 60-day policy comparisons in `late-town-service-recovery.json`, `late-town-service-tax-intervention.json`, `late-town-service-high-tax.json`, and `late-town-service-pension-cut.json`.

This is also distinct from the prior allocator comparison report. That report's instrumentation produced a different 25-year endpoint; do not compare the population or treasury totals across those two harnesses as if they were one matched replay. The findings below are tied to the endpoint archive and matched 60-day runs documented here.

## Diagnosis at day 50,681

The town has 721 residents, eight public schools, six public clinics, and enough physical facility capacity for the whole population. There are also eight privately owned schools. Road-based facility catchments cover 649 residents (90.0%); 72 residents are outside both service catchments. The service network reaches at least some households in every occupied home group, but the 72 out-of-catchment residents still need closer provision or better road access.

Staffing and facility capacity are not causing the zero public coverage. The allocator reports approximately 241 local qualified staffing equivalents for health against a requirement of 10.3, and 243 for school against a requirement of 27.7. There are 247–249 qualified unemployed adults in the reachable households. Both public services have full nominal facility capacity and about 90% geographic access.

The operative blocker is municipal cash timing. The municipality has $673 at the end of the terminal day, but the next day's service purchase runs after public payroll and pension disbursement. At the service-purchase phase the treasury is already $0. The regional account is also nearly exhausted at $15.50, below the existing $5,000 municipal loan step. On the terminal day the 144 residents over 70 generate a nominal pension liability of $2,304/day at the $16/day policy. Only about $176/day of pension payments can actually be made (7.65% of the obligation), but that payment still consumes the remaining cash before health and education purchases. The existing service authorizations are $70/day for health and $90/day for school; both are requested but unpaid, leaving actual public coverage at zero. End-of-day treasury alone therefore overstates cash available when services are purchased.

The school field in `actualServiceFunding` is not the same as public school coverage: it includes private-school service in addition to public provision, and reads 4.4% here. The public service panel's `serviceProvision.school.coverage` and daily purchase records correctly show zero public coverage. This is a difference in scope, not a stale coverage cache.

## Matched mayor-policy experiments

Each experiment starts from the exact day-50,681 archive, uses the normal enacted-policy path, and runs 60 days. No people, cash, or goods are injected.

| Action | Public service result | Cost or tradeoff |
| --- | --- | --- |
| Control | Health and school purchases were both $0 on all 60 days; cash before the service phase was $0 every day. | Existing pension, safety, and care authorizations retained. |
| Reallocate $50/day each from police and fire to health and school, with the four-budget total unchanged | Still $0 health and school purchases on all 60 days. | Lower police and fire authorizations; not enough to clear the pension-first cash bottleneck. |
| Raise income tax from 12% to 18%, retaining existing care budgets | Still $0 service purchases on all 60 days. | Higher household tax burden without a service recovery in this state. |
| Raise income tax to the current 40% ceiling | Still $0 service purchases on all 60 days. | Severe household burden; service-phase cash remained zero. |
| Suspend the $16/day pension policy for 60 days, retaining the existing care budgets | Health paid $70/day and school paid $90/day on all 60 days. Coverage became about 15.9% for health and 7.6% for school; service-phase cash ranged from $136 to $308. | No pensions were paid during the intervention; this is a deliberately harsh austerity test, not a recommendation. |

The pension test confirms the causal path: removing the earlier treasury claim allows the already-authorized health and school purchases to run. It does not make the city broadly healthy in 60 days. Population ended at 715 in both control and pension-cut arms; hardship stayed at 77%, and the health/education indices remained at their floors (25/15). The tests therefore establish improved paid access, not a solved city crisis.

All intervention arms validate at each checkpoint. Cash drift is below `1.3e-7`, commodity error below `2.81e-8`, and no arm receives free cash or goods. The 25-year diagnostic itself validates at day 50,681, with cash drift `2.33e-5` and commodity error below `2.81e-8`.

## Conclusion

Zero public coverage is a real treasury-priority failure in this late-city state, not a missing school/clinic, unavailable staff pool, or stale public coverage measure. A legal policy action can restore the current service authorizations, but only by making a severe pension cut in the matched test. More than 10% of residents remain outside the measured road catchments, and the existing $70/$90 service authorizations are far below modeled full-town operating need ($444 health and $1,195 school/day at this population). The current policy sliders cap each at $500/day, so school funding alone cannot reach the modeled full-town requirement at this population even when cash is available. Full service would require a wider fiscal decision, a review of that authorization cap, and service coverage improvements; this evidence does not justify changing economic coefficients. The previous ordinary-hour soak remains a separate, longer run with player road/green actions and a different source receipt.
