# TownLedger 7.0 — The Working City

## Scope and release

Version 7.0.0, code 14, schema 5, package `org.townledger.vale`. Signed with the same development certificate as 6.0/6.1, prepared for an in-place update on Android 7+. Back up a valued town first. An actual Android installation/update has not been tested in this environment.

The game still uses an offline Java/WebView host and synchronous deterministic daily model. This release rebuilds the economy and authored starts; it is not a claim to a new native engine, calibrated real-world economics, commercial art parity, perfection or exhaustive bug removal.

## Changes addressing the wider failure

| Area | Change |
|---|---|
| Firms could fail despite apparently reasonable policy | Inventories carry weighted material cost. Purchases debit cash but no longer immediately count as operating losses. Sales, materials sold, payroll, other costs and tax reconcile in an operating statement. |
| Firms produced without labour | Output now requires workers and inputs. Capacity, orders, prices and inventories determine production. Standing external orders let producers rediscover funded demand after an illiquid period. |
| Arbitrary service income and staffing | Finite staffed service-contract pools replace one equal flat payment per firm. Hiring adjusts from sustained sales on a two-week cadence; investment clears a return hurdle and unpaid workers leave. |
| Cash hoarding created permanent depressions | Corporate treasuries retain operating, inventory and debt reserves, then distribute surplus to actual owners. Founding regional owners receive returns too. Property distributions and estate settlement also use real cash transfers. |
| Construction worsened unemployment by spawning adults | Completed housing is capacity, and can remain vacant. Migration needs jobs after considering existing jobseekers; household formation can use existing vacant homes. |
| Employment and household figures misled | Retirement releases employer slots. Funded pensions support older households. Wages, pensions, rent and dividends are distinguished. Hardship includes bank deposits as well as wallets. |
| Government interest control missing | Staged 0–20% annual benchmark in quarter-point steps; persistent in saves. It affects bank quotes, variable credit, municipal credit costs, saving preferences and investment hurdles. Legacy loans preserve fixed rates. |
| Starting towns inherited unviable staffing/demographics | Reauthored baseline firms and ages. Market Cross has matched staffing, age mix and explicit regional manufacturing/service/logistics/tourism access. This is authored fictional demand, not estimated national data. |
| Roads and animation | Connected named through roads, collectors and local streets; no concentric starting rings. Extensions create usable connected blocks. Sidewalks/crossings distinguish road classes. Walk cycles, heading-aware vehicles and a recognizable twin turboprop with a taxi/takeoff/approach/landing sequence. Runways are cleared of trees. |
| Contrast and use of screen space | One palette overrides inherited dark-on-dark and light-on-light styles, including active navigation, policy controls, construction icons, overview badges and council dialogs. More usable drawer height, larger targets and quarter-point display precision. |
| Policies lacked useful feedback | Economy flags food shortfalls, weak employment, inadequate road upkeep and low public reserves. Business inspection explains inventory cost, payroll, cash purchases and smoothed operating margins. |

Seasons/weather remain off by default. Existing towns retain their roads, buildings and residents; new street plans and starting populations require a new town. Old exports remain importable, but future economic outcomes change under the new rules. Older builds reject schema-5 archives.

## Executed evidence

The source hash was captured before the final economic runs and checked against the unchanged game afterward. Reported endurance and regression data below match the assembled script in this APK.

### Fresh starts

- Eight settlement seeds, sampled monthly for two simulated years: no automatic start-of-game employment collapse; validation and cash checks passed. The tests require employment to remain at least 65% throughout the sampled period, and no replacement/restart equity in those runs.
- All five scenarios across three seeds each, sampled quarterly for three years: 15 trajectories passed structural/cash checks and ended at 65% employment or higher. Frontier and Hard Times deliberately begin weaker than the default settlement.
- These are reproducible cases, not proof that every seed or policy remains prosperous. High initial employment does not establish deep realism by itself.

### Recovery of damaged states

- `corporate-liquidity-trap.json`: employment **78% → 100%**, firms **20 → 23** after five simulated years. Final population 200; cash drift 0.00001467.
- `v60-distressed-town.json`: employment **3% → 100%**, firms **2 → 51** after five simulated years. Final population 571; cash drift -0.00001374.

The first fixture captures the corporate-cash trap exposed during this rebuild. The second is the actual stranded year-50 6.0 town used in the earlier analysis. The recovery is gradual and depends on funded trade, retained assets, investment and hiring; it is not a reset of balances or a forced employment target.

### Mechanism checks

- A retailer bought 677.03 of stock while recognizing 386.96 of goods sold; its operating statement reconciled. The purchase was not all treated as a loss.
- Removing all private workers produced zero new goods in the test day.
- A resident ageing past 70 left the employer roster and received a funded pension.
- Interest policy was staged, enacted at 2.25%, displayed with quarter-point precision and retained in an archive.
- A legacy fixed contract preserved its rate; new variable credit repriced through the benchmark.
- With otherwise identical funded credit, the low/high benchmark cases ended with loan rates 7.16% / 19.49% and repayments 1030.97 / 1135.10. The money stock was conserved.
- Three paired-seed policy experiments record high-cost conditions, subsequent reform and unchanged-policy comparisons. Returns, investment, employment and hardship can respond differently. A business-friendly package is not coded as an automatic increase to an employment percentage.
- Exact seeded replay, 120-day continuation, rendering-independent economic RNG, malformed/future-save rejection, authentic 5.6 migration, blocked-cargo ownership and accounting, pause and extended traffic progression passed.
- Touch placement/cost, inspection, pinch, staged policy, speed slider, nonblocking elections, corrupted-primary save recovery and 20 varied road-network simulations passed.
- The synthetic 2,000-resident account test completed 120 days in 0.924 seconds on this host, about 7.7 ms/day. That is a scale test, not Android FPS or proof of a prosperous 2,000-person town.

### Long-run towns

| Start | Seed | Simulated years | Final residents | Open firms | Bank failures |
|---|---:|---:|---:|---:|---:|
| settlement | 42 | 50 | 1082 | 104 | 0 |
| regional | 42 | 10 | 1294 | 127 | 0 |
| industrial | 909 | 20 | 395 | 40 | 0 |

Cash, commodity, occupancy, workforce and footprint checks passed. Government budgets do not automatically scale with growth; maintenance and service needs can exceed unchanged starting appropriations. The Economy screen flags those pressures. Bank failures remain possible even though these particular final runs did not trigger one.

### Interface and visual review

All scrolled normal panels, the opening menu and a real council dialog were exercised at 844×390. The computed text-contrast scan reported zero failures across the 14 exercised surfaces, using 4.5:1 for ordinary text and 3:1 for large text. This is not a complete accessibility certification; native Android dialogs, every hover/focus combination and all possible future generated content were not exhaustively tested. Renderer captures were visually inspected, including parked, takeoff and landing stages. The model and artwork remain stylized.

### Live speed on the host

| Loaded town | Residents | Requested | Completed rate | Economy-panel click |
|---|---:|---:|---:|---:|
| settlement | 1082 | 64× | 63.8× | 84 ms |
| regional | 1294 | 64× | 63.8× | 156 ms |

Each measured run lasted about ten wall-clock seconds. Timings describe this host browser only. Physical-phone FPS, thermal throttling, battery, system file pickers, background/resume behaviour and a 30-minute Android memory run remain untested. Individual expensive synchronous days can still hitch; the engine has not moved to an independent worker.

## Package and provenance

Real Java compilation, DEX checksums, exact source-asset bytes, package/version/API metadata, no requested permissions, icon resources, ZIP alignment and APK v2/v3 signatures passed. The certificate is the same development signer used for the delivered 6.0 build. The APK targets API 36, minimum 24; it is compiled against the available older platform jar using APIs already supported there.

## Model boundaries

The monetary base is finite, loans transfer existing funds, and deposits are liabilities. This is not modern bank deposit creation. The outside economy is aggregate; valuations, pricing, skills, fertility, pensions and demand are authored behavioural rules rather than empirical estimates. Material inventory is capitalized while payroll is expensed in the current period. Screen traffic is representative of economic activity; cargo has its own authoritative daily route/delivery state. Rail and aviation are simplified. The transaction journal is bounded and is not a complete double-entry audit of all history. Remaining limits are disclosed instead of treating conservation tests as proof of a perfect game.

APK SHA-256: `b02d4545cccccccec60878e57bdabb1b7c9eba12b5d6781a480e8a6ca2fe196d`

Assembled script SHA-256: `7871e14e0c2d6a8897c97d1e49285a7b7bf3a412442550d717cab51970df1cc9`
