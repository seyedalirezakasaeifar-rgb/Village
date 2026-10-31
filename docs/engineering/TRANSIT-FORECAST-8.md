# Route demand and public-funding review

Based on integrated `4e9248c`. The transit API/report owns this change; the campaign and wider dashboard remain with their UI owner. No fare, subsidy payment, wage, service-budget authorization, passenger-capacity rule, teaching coverage or migration schema changes.

## Stable integration API

- `transitProposalReport(spec, editing = -1)` returns a frozen on-demand snapshot report. `spec` uses the existing `{mode,depot,stops,level}` contract. For edits, supply the current route ID. A report has `ok`, `stamp`, `day`, `status`, `catchment`, `service`, `opportunities`, `demand`, `fares`, `publicFunding`, `options`, `actions`, `observed` and `assumptions`.
- `transitReviewedQuote(spec, editing = -1)` returns the ordinary capital quote plus `forecast` and `forecastStamp`. Public Works uses it for proposal/fleet-investment review. The existing authorizer rejects a reviewed quote if jobs, homes, affordability, staffing, policy, inventories/prices, street wear, capital, topology or day changed. A stale click refreshes the review and requires another explicit authorization. Legacy programmatic capital quotes retain their existing price/topology safeguards.
- `transitForecastFresh(stamp)` tests the full snapshot context. Restore/new-town graph ownership invalidates old stamps. Forecasts and stamps are ephemeral and never enter town archives.
- `transitRouteReport(routeId)` adds the existing route's observed boardings, denied riders and operating costs, alongside a proposal under current circumstances. Paused routes are explicitly labelled as a resumption estimate using the owned fleet.
- `renderTransitForecast(report)` returns the scoped report markup. `showTransitDemandReport(routeId, opener)` opens Public Works at an expanded report; dashboard/UI links can call this directly. Existing panel-body buttons can use `data-transit-action="report" data-route="ID"`. Destination/first-mile action targets carry actual building/firm/household IDs and worker counts, and use the existing property-inspection controls.

`status` is one of `not-operating`, `capacity-limited`, `no-useful-trips`, `public-funding-needed`, or `fare-scenario-covers-operations`; the last is explicitly conditional, not a profit promise.

## What is counted

Catchments use actual connected street walks of at most five tiles, not geometric circles or district labels. Distinct households, residents, current business positions/filled jobs, stocked grocers and teaching sites are counted once. Teaching activity is descriptive: it creates no paid student trips or extra school/clinic service benefits.

An independent service plan uses the same route order, vehicle bays, local driver qualifications, previous public roles, walking access to the depot, actual treasury after capital, gross wages, tax returns, maintenance and road-wear reliability as the live model. Existing drivers and cash are not cloned into the actual town. It reports available/required/assignable drivers, feasible capacity/headway, actual feasible operating cost and the requested authorized operating ceiling. Enacted service budgets are read explicitly; pending budget drafts are not treated as paid service.

The forecast shares the real routing, transfer and capacity-reservation functions through an isolated topology/context. Its local slots and wallets cannot alter the live graph's passenger reservations, driver roles or treasury. All current employed residents compete for seats, including those whose preferred route is an existing corridor; overflow can use the proposal, just as in live service. The requested-frequency opportunity count is shown separately from feasible current staffing and capacity.

The scenario band compares current affordable work trips with work plus one currently stocked shopping outing per household. The shopping scenario uses current staff, food inventory, prices, travel costs, capacity and household wallets; it does not invent tomorrow's production, rent, wages or withdrawals. Future jobs, income, prices and construction can change actual results. Transfer fares are shared equally between the unique routes in a journey for planning attribution, while the actual city still collects one integrated fare. This allocation is not a new monetary account. Observed fare receipts are labelled as **network-wide**, rather than assigning all network revenue to every route.

`fares.low/high` are those snapshot scenario shares; `publicFunding.low/high` are feasible operating cost less those fares, floored at zero. Public service may reasonably need subsidy. Increasing fares or guaranteeing a return is not a recovery rule. Frequency options report actual driver/capacity/headway/cost standards and tell the player to review demand at the chosen level.

Recommendations explain recorded constraints: job-only stops with no residential origins, home-only catchments without business destinations, current workplaces beyond the stops, homes six to eight street steps away, short/walkable journeys, overlapping service, slow headways, missing drivers/cash, or genuinely denied riders. No arbitrary development/demand bonus is added.

## UI and invalidation cost

Reviewing an investment pauses the simulation so a human can read a stable report. Resuming the clock or changing the city makes the old review stale; it cannot quietly authorize against old demand. Report expansion persists across ordinary drawer renders. Calculation is on explicit review/report requests only; rendering a stored report never scans the population. The cache holds at most sixteen frozen reports/input snapshots, and the routing contexts retain their existing 512-origin/4,096-itinerary limits. Returned reports contain copied values, never live account objects.

The only engine refactor adds optional independent routing/reservation contexts. Calls without that context follow the original live path. No renderer, campaign, new transport mode or automatic capital action was introduced.

## Acceptance evidence

Source bundle SHA256 `27ae071ac52278a51b3388c0a50e8107f9a28a3f34ef01a35396ea3dd9be0c92`. Receipts and a 390×844 screenshot are in `docs/previews/transit-forecast8/`. Tests ran in host Chromium; this is not physical Android timing.

- `tests/test_transit_forecast.py`: actual map selection, running-clock review, authorization, stale review refresh/re-authorization, real destination replan, inspector expansion and mobile overflow. No resource grants, resident/job injection or fare increase. The original short corridor carried zero riders and incurred operations; replan connected four actual workers, collected $2.60 at the unchanged $0.65 fare and incurred $137.87 operations. Its snapshot correctly showed the $135.27 public-funding requirement. It did not promise profitable transit. Cash/staff absence produces zero service/fares. A same-day wallet change rejects the reviewed quote without spending capital. Viewing reports daily preserves exact fifteen-day economic continuation. Repeated rendering performs zero forecast calls.
- `tests/test_transit_forecast_network.py`: controlled capacity fixture predicts 199 boardings/101 denied, $248.75 fares and $157 operations, matching actual service. For 300 two-leg riders, two reports attribute $187.50 each, totaling the single actual $375 receipt. Forecasts leave actual seats/accounts unchanged.
- `tests/test_transit_forecast_scale.py`: synthetic size fixture with 2,000 residents, mostly unemployed, 12/48 built bus routes. Full report calls took 11.9/19.3ms; repeated calls took 1.7/1.8ms. The fixture explicitly funds construction for scale testing, separate from the unassisted player acceptance. It is not a 2,000-employed-commuter or Android frame-rate claim.
- Existing network, pure remap, urban migration and scalable-service-budget authorization regressions passed. The previous-engine exact-equivalence suite passed unchanged live accounting/tickets/capacity across 8/12/48 routes, 2,000 controlled riders and twelve closure/timetable/funding/capacity transitions.

Forecasts remain current-state scenarios: tomorrow's hiring, enterprise wages/production, bank withdrawals, rent, new buildings and preferences can change actual shopping demand. School activity is context; the current paid trip model covers work and groceries. No migration or public-budget workflow changes are included.
