# Active playability audit: two city strategies, first hour equivalent

Audited commit: `6255255ab034675ce899b1fee36be3b8f300d8eb`; production bundle SHA-256 `6a770b26dc99ece160a4ef9883730f92498f4c0fdd20bbf217e533a3f878a798`. **This precedes the staged logistics in `a98ab20`.** Findings below apply to the identified source; the final section separates known integration assumptions.

No production files changed. `tools/audit_active_play.py` founds fresh seed-42 towns and uses real menus, purchases, policy enactments, municipal borrowing/repayment and map taps. Browser-only probes read legal survey sites and metrics, move the camera, and advance the existing settlement function. They never grant cash, goods, staff, qualifications, buildings or project completion. They stop rather than choosing an unexpected council dialog. Ordinary coded achievements and autonomous investment remain enabled.

At 1× the engine advances one day per 1.65 seconds. “60 minutes equivalent” is day 2,183, approximately six game years; it is accelerated model time, not an hour of human playtesting. The trade route contains 23 major decisions / 98 actual button clicks; the community route contains 23 / 114. Reviews and interventions occur at the opening and approximately 10, 20, 30 and 45 minutes. Initial opening-only/hold rehearsals and an unsuccessful dock-recovery attempt are retained separately. They expose how much of the operating town runs without further decisions.

Replay: `python tools/audit_active_play.py --strategy both`. Evidence, daily contract/project traces and screenshots are in `reports/active-play-audit/`; full JSON is compressed there. No previous player save is loaded or overwritten.

## The two plausible routes

**Trade and later river expansion:** paid imported food; a 200-unit timber agreement; County Ridge trade park, gateway, factory and depot; later care/vouchers and independent teaching; a larger district agreement; then an actual working-waterfront investment and manual shore-road recovery. Income/profit tax remain 12%.

**Community and neighbourhood expansion:** local bakery; income/profit tax 18%; education $280/day, health $220/day and roads $80/day; Orchard Downs homes, shops, school and clinic financed partly with ordinary municipal debt; repay principal; then a second mixed neighbourhood at East Meadow. Later teaching/health authorization rises with the resident base.

Both routes encounter real capital commitments. Trade’s first district/pilots leave $27,395 and 24.4 authorized spending days on day 13. Community’s first complete neighbourhood leaves $22,795, $35,000 debt and 15.0 spending days on day 90. Its $35,000 principal is repaid through the actual Budget controls at the 20-minute review.

| Checkpoint | Trade: cash / debt | Community: cash / debt | Trade / community employment | Trade / community care | Trade / community school |
|---|---:|---:|---:|---:|---:|
| 10 min equivalent | $55,484 / $0 | $64,744 / $35,000 | 99% / 98% | 61.2% / 100% | 63.4% / 94.0% |
| 30 min equivalent, before new expansion | $161,539 / $0 | $331,234 / $0 | 100% / 100% | 76.1% / 97.6% | 37.8% / 80.0% |
| 60 min equivalent | $447,472 / $0 | $1,100,570 / $0 | 98% / 88% | 62.5% / 100% | 31.2% / 78.0% |

At the end, trade has 286 residents, no hardship and median household liquidity $5,569 per resident; community has 341 residents, 2% hardship and median liquidity $4,468. The community package is not a universal dominant strategy: it buys stronger public coverage and reserves while the final private buffers and employment are weaker. These are whole-strategy observations, not isolated policy effects. Regional demand also diverges to 0.88 versus 0.56 because actions consume different random draws; a shared starting seed does not hold subsequent external shocks constant.

## Highest-impact findings and exact reproductions

### 1. Waterfront gateway does not connect the businesses the project asks for — UI/planning

Trade route, day 1,092 (30-minute review): buy Lower River Reach, choose working waterfront, commission its interior gateway. This costs $35,136 in deed plus initial road work and leaves $126,403. Both **Survey fishery** and **Survey wharf** then return:

> No connected, legally vacant site fits this project. Build a street connection or choose a site manually in Public Works.

No further money is charged. A normal eight-tile, $1,200 road spur permits the fishery at `(6,59)`, but that fishery occupies the only served shore lot and the wharf survey still fails. One additional legal road tile at `(7,60)`, $150, permits the wharf at `(6,60)`.

This is recoverable through map construction; the project’s guided route is incomplete. A fresh player has to discover two purpose-specific connections after paying the advertised gateway. Proposed UI fix: survey and reserve two non-overlapping shore footprints and their complete street connection before quoting a waterfront gateway. Explain the actual blocked condition and show the missing road segment. Keep manual alternatives available.

### 2. A large agreement accepts a supplier with no uncommitted output — logistics/offer assessment

Trade route, day 365: the district-unlocked offer is **600 manufactures**, current stock **3.18**, arrival estimate six days, deadline day 395. The displayed inventory margin is approximately **$4,078**, with the stated exclusions for future payroll/tax/disruption. The actual firm produces **1,061 manufactures** during the following 31 recorded days, but its stock at the contract dispatch point never exceeds **4.37**. **Zero contract units dispatch or arrive**, and the agreement misses its window. Other sales/allocations consume output before it becomes available to this commitment.

A smaller 200-flour agreement with Greyhaven subsequently succeeds on day 735. Recovery is possible by changing supplier/commodity, but the offer does not explain that production is already claimed. Proposed assessment: recent uncommitted surplus, existing demand/allocations, current stock and full handling/transport lag; offer adjustable volume or an explicit allocation decision. Inventory margin alone is insufficient evidence of deliverability. Replay this on the new staged logistics before concluding that its behavior is unchanged.

### 3. Completed project hides a meaningful later failure — UI/stewardship

The waterfront is certified on day 1,122 after 30 staffed days. Its wharf has earned only **$132.41 revenue** and lost **$2,102.93** over those first 30 days. The rule is satisfied, but the “working waterfront” result is commercially fragile.

On **day 1,473 (40.48 minutes equivalent)** that wharf closes at **$0 cash**. The project remains marked delivered, as historical evidence should. Its rendered card contains no closure information or recovery action. The town signal says **Care and learning need attention**; mayor pressures are **Places need people and access** and **Rebuild a trading reputation**. The completed waterfront’s lost cargo business receives no contextual priority.

Proposed UI fix: retain the dated certificate and add a current stewardship/watch line for required facilities. Surface the closed wharf once in Town signals, link to its account/route and give a reviewed recovery path. Distinguish staffed infrastructure from actual paid freight and operating sustainability when naming a commercial milestone.

### 4. Recovery succeeds but the reputation warning never clears — UI/feedback

The missed manufactures window occurs on day 396. The corrective flour agreement fulfils on day 735. At day 1,473 and through the end of the run, the old miss still produces **Rebuild a trading reputation** because the card counts every retained `missed` record. This source has no corresponding reputation state or clear recovery condition.

Proposed UI fix: put old misses in accessible history; prioritize current commitments at risk or a disclosed recent performance window. If reputation is intended to be persistent and buyer-specific, expose that real metric and an attainable repair condition. A permanent generic warning crowds out the later closed-wharf event.

### 5. The authored arc runs out of new decisions very early — content/pacing

The initial trade direction finishes on **day 73, 1.98 minutes equivalent**. The community direction finishes on **day 199, 5.45 minutes**. All three initial community civic projects are complete by day 142. In the opening-only rehearsals, remaining holdings continue accumulating cash without additional actions.

At 30 minutes the active trade actor deliberately chooses a river direction. Its first two stages complete on days 1,093 and 1,094 using the founding town’s existing fishery/wharf; the new district is still unfinished. Both actors then repeat district establishment, completing the second districts on day 1,122. After all three project kinds exist, `civicProjectOffers()` returns no new authored opportunity types; “Plan the next district” repeats the same three charter patterns.

There are real economic changes, and freeform construction can be enjoyable. The authored progression does not yet establish a multi-hour campaign. Do not fix this by increasing hold timers. Add later condition-driven decisions with genuinely different uses for surplus, regional relationships, operating failures, changing learner/workforce cohorts and contested capital. A new direction should acknowledge existing capability rather than presenting it as two new accomplishments.

### 6. Private-school churn merits economic review — operating model and explanatory feedback

No fixture alters the private model in this audit. Two independently owned schools repeatedly close and reopen under autonomous investment. Independent Learning House 30 closes on days **516, 890, 1,189, 1,489, 1,789 and 2,089**; Independent Learning House 33 on **732, 1,040, 1,339, 1,639 and 1,939**. The actor makes only one invitation attempt, which initially reports another site is already under construction. Some turnover may be intended, but repeated same-site cycles deserve review against multi-term learner demand and staffing costs. Current generic investment failure text does not identify the binding factor.

The independent teaching project itself earns valid purchased-learning evidence on day 408. Its name still promises “school-to-work” without requiring an employment outcome. Proposed content fix: name the measured result accurately, or track an actual named learner/employer transition. Preserve the distinctions between public resident-based coverage, private learner equivalents and completed qualifications in user-facing explanations.

## What worked

The strategies use distinguishable capital, taxation and operating commitments. Real debt and early reserve pressure appear, a risky trade promise can fail, a different supplier can recover, and manual street construction repairs the dock dead end. The map stays visible through the consolidated status disclosure. Neither run reports page errors; final town validation passes and total-cash drift stays below $0.00006 over 2,182 daily settlements. These are useful foundations, not certification of human enjoyment.

## Known staged-logistics adaptation, not a new-source test result

`a98ab20` and `docs/engineering/LOGISTICS-8.md` were read after this audit. That source caps `dispatchRegional` at **120 units per call**, adds actual handling stages and calls `civicProjectRecordArrival(order)` only on successful settlement. Its removal observer must be removed as the lead already plans.

The old actor/test assumes one accepted 180-unit bridge. On the new API one request may accept 120, leaving **60 genuinely uncommissioned units**. The next replay must use a second real reviewed order, show accepted/pending/remaining quantities, and test duplicate prevention only after all 180 are commissioned. Never credit requested units. A 120/180 project after one click is a partial-order state, not an impossible goal or a delivery failure. Old fixed-day arrival/contract expectations must be replaced with the displayed staged estimates and actual successful-delivery evidence. The new priority/routing/extra-shift decisions need their own active comparison after integration.

No production change or economic fix was made during this audit. Rebase onto the integrated lead before targeted UI/content revisions and staged replay.
