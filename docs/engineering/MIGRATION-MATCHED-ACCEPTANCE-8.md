# Combined migration acceptance

Tested production commit: `662ec6f3b0998ce3c3c560d5bef39e4e17a4bcc1`.

Assembled `assets/game.js` SHA-256: `abe9c4bbdd86f8c2b9a3776d2996e2c32803f4dd0521791d25ba90cf6c398882`.

This branch changes experiment tools and evidence only. It does not alter economic coefficients, migration rules, archive validation, transit, production assets, or integration history.

## Matched city histories

Twelve histories cover two seeds in both settlement and regional starts. Every arm begins from an identical archive after a natural one-year warmup, then continues three years. Opening archive hashes are retained per arm. Comparisons are passive policy, monthly service funding under existing operating standards, and the same service policy with one year of tight credit followed by two years at the opening credit settings.

The service arm authorizes schools, clinics, police, fire, and roads within legal policy ranges. It does not grant funds, force recruitment, guarantee coverage, or build free facilities. The tight-credit arm sets the legal benchmark to 18% and underwriting to 90, then restores 3%/35. Other policy stays the same as the funded-service arm. Ordinary stochastic decisions diverge after treatments; matched seeds do not make later random events identical.

Values below are three-year endpoints after warmup. Cash is town treasury, excluding public reserve. Education and health are model scores, not real-world calibrated measures.

| Start / seed | Policy | Opening → final residents | Treasury | Health | Education | Immigration / emigration |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Settlement / 42 | Passive | 179 → 241 | 495,333 | 73.2 | 65.4 | 36 / 3 |
| Settlement / 42 | Services | 179 → 230 | 43,795 | 99.0 | 92.7 | 26 / 0 |
| Settlement / 42 | Credit then restore | 179 → 258 | 63,270 | 99.0 | 92.5 | 50 / 3 |
| Settlement / 101 | Passive | 178 → 235 | 287,587 | 74.0 | 67.6 | 40 / 3 |
| Settlement / 101 | Services | 178 → 245 | 80,477 | 99.0 | 93.3 | 41 / 0 |
| Settlement / 101 | Credit then restore | 178 → 235 | 18,262 | 99.0 | 93.3 | 32 / 3 |
| Regional / 42 | Passive | 698 → 913 | 686,759 | 55.0 | 55.6 | 108 / 0 |
| Regional / 42 | Services | 698 → 1,020 | 313,517 | 96.0 | 87.9 | 186 / 0 |
| Regional / 42 | Credit then restore | 698 → 965 | 260,947 | 96.0 | 88.0 | 153 / 0 |
| Regional / 101 | Passive | 696 → 921 | 682,242 | 52.2 | 56.8 | 122 / 0 |
| Regional / 101 | Services | 696 → 977 | 382,936 | 93.2 | 88.6 | 162 / 0 |
| Regional / 101 | Credit then restore | 696 → 962 | 350,404 | 90.5 | 88.6 | 157 / 4 |

Findings:

- Growth is viable in all twelve histories; final employment is 99–100%, reported hardship is zero, and municipal debt is zero. This short window does **not** establish a challenging game or long-run solvency. Passive starts remain financially comfortable while allowing care and schooling to deteriorate. No arbitrary penalty was added to manufacture difficulty.
- Paying for service capacity has an actual fiscal cost and a delayed education benefit. For example, settlement seed 42 finishes with 451,538 less treasury cash under the service policy and a 27.3-point education advantage. All spending categories and taxes are reconciled in the exclusive cash-flow ledger; this difference is not solely a school bill.
- Service spending does not guarantee maximum growth. Settlement seed 42 grows less under services, while both regional cities grow more. Do not describe migration as a simple service-budget reward.
- Credit tightening does not produce a consistent recession across these four opening economies. Regional growth is lower than in the service arm; settlement effects differ by seed. Output shows policy restoration and continued growth, **not** proof that easing repairs a banking crisis. Loan-level principal/default status was not fully captured by this new summary probe; balances and arrears are retained, and the earlier credit lab remains the broader evidence.
- All city households have effectively redeemable deposits in these natural histories (locked amounts are floating-point residue). This is not evidence that deposits always equal spendable money; the controlled constrained-withdrawal regression checks that distinction.

Across 36 measured city-years, every tick reconciles births, immigration, deaths, emigration, and living population. The runtime UI observer's count deltas independently match the source-hook ledger in every arm. Missing homes, unregistered households, and capacity violations are zero. Maximum absolute cash drift is `0.000037374`, goods error `8.048e-9`, and exclusive treasury reconciliation error `0.000007299`. Every monthly town validation passes.

## Deferral and causal recovery

Nine controlled comparisons cover seeds 42, 101, and 909. A cottage becomes vacant through a real departure. A producer's published capacity is enlarged solely to isolate the admission boundary; this is explicitly **not** evidence of organically created vacancies. Existing cash is moved into the finite external account and exactly restored, the same road tiles are removed and restored, or a temporary redevelopment marker is completed and removed.

Each blocked attempt creates zero residents and transfers zero capital. Funding, access, or construction repair restores eligibility. The first subsequent ordinary invitation succeeds in every case, with generated adult ages/skills, jobs at funded firms, exactly 2,500 transferred from the region, and actual next-day wages (62–72 per household). No RNG override is used for these subsequent invitations. Cash is conserved and resulting archives validate and round-trip.

Reasons are readable: an unfunded advertisement supplies no job; a disconnected home has no road gateway or reachable food shop; an unfinished unit is unavailable. Some secondary reasons cascade from the primary housing/access blocker. The UI should lead with the first reason rather than imply three independent problems must all be repaired.

The existing combined-build migration suite also passes banked-versus-wallet equivalence, finite bank/region withdrawal constraints, private-school fees and capacity, outside-price pull, estate release, legacy family/assets preservation, forbidden legacy roster growth, save-safe service forecasts, and municipal construction without invented residents.

An initial recovery fixture incorrectly put a municipal reservation marker on a privately titled cottage and correctly failed archive validation. It was replaced with a reversible construction boundary. The failed log is retained; no production validator was weakened.

## Food agreement versus retained stock

Two more paired comparisons use normal seed 42 settlement and regional cities. Each arm restores the same archive after 25 days and continues 35 days, either without a new commitment or by accepting the actual forecast-sized food offer through the exchange UI. Automatic local/regional trade continues in both arms; the stock-retention arm is not an embargo.

Both real agreements fulfill, with 200 food delivered to Greyhaven in each city. Each contract retains local working reserves rather than promising the entire buyer window. All four endpoints have zero reported hardship; matched final populations are 163 in the settlement and 657 in the regional start. Cash and goods remain conserved. The raw comparison includes quotes, price, supplier, inventory, freight review, deliveries, finite external cash, and both outcomes. This demonstrates a viable limited agreement without a guaranteed municipal reward; it does not establish that exporting dominates imports or retaining inventory.

The existing supplier-selection suite also passes cancellation, stale-review rejection, producer/commodity/buyer selection, first-day insufficient food forecast, and the paid fulfilled agreement after 25 days. Missing initial stock or an unavailable forecast must not be described as missing buyer demand.

Two navigation failures are retained: the harness first treated a closed drawer as a collapsed details problem, then correctly established that clicking the already-active Economy tab toggles its drawer closed. The final harness uses Escape before opening Economy and reveals the relevant details. No UI or economic code was changed to make the comparison pass.

## Public diagnostics contract

`migrationAssessment(home, profiles, capital, joining)` exposes eligibility reasons, funded reachable offers, route fares, itemized essentials, expected take-home pay, surplus, physical housing status, forecast care/learning coverage, and probabilistic local/outside pull. It is a forecast, not a reserved job or guaranteed future wage.

`migrationEmigrationAssessment(h)` exposes persistent budget shortfall, actual spendable bank liquidity, essentials runway, credible local vacancies, debt/property obligations, and the better outside reference. A bank claim without redeemable reserves is not treated as available cash.

`migrationDiagnostics()` supplies recent decisions, `observedSinceDay`, `sessionCounts`, `historyPersisted:false`, inherited crowded homes, and the labelled outside reference. Session counts reset on load and are not a reconstructed lifetime migration history. Outside wages/rents are founding-policy benchmarks with live regional food quotes, not a simulated foreign labor market or guaranteed job elsewhere.

## Reproduction and evidence

Run from the repository root with Python, Playwright, and Chromium installed:

```sh
python tools/acceptance_migration_matched.py
python tools/acceptance_migration_recovery.py
python tools/acceptance_trade_matched.py
python tests/test_migration_causality.py
python tests/test_supplier_selection.py
```

Evidence is in `docs/evidence/migration-matched8/`. Raw histories retain monthly snapshots, source hooks, failed admission attempts, finite external flows, distributions, loan balances/arrears, service provision, and independent treasury reconciliation. Archives are synthetic generated test towns and contain no personal saves or credentials. This does not certify physical Android performance, paid transit capacity, full foreign-city demography, or enjoyable long-term play.
