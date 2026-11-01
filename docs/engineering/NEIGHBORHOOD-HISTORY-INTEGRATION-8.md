# Neighbourhood history and coherent acceptance

Base: native correction `0c803faf08cff7ae6ec52c56d43d11465901df5f`, following creator-cap `6c5a154` and native async `0a6d217`. Reviewed history candidate: `9650b62c7dad3fb8088e908d69ea7355526bd8a0`.

Final game source SHA-256: `84ecbaef6b0ae999a9c5adcd49b9ba1678840cabfc36cf02b617c74a93d208a4` (100 modules, 1,152,722 characters). MainActivity SHA-256: `7283d9365de4efdf0633205c520c6c7b660f369420b3d4cb9e1612f9bcd2345d`.

## Independent corrections

* The original candidate accidentally moved automatic farm-renewal attempts from every 30 days to every 90 days. An executable dispatch oracle reproduced missing day-30/day-60 attempts. The corrected observer preserves the existing monthly renewal and quarterly retail cadence.
* The original history validator accepted arbitrarily long coordinate aliases and extra snapshot/row payloads. The corrected schema permits at most two records, each containing exactly `day` and `blocks`, at most 256 canonical block keys, and exactly four bounded integer counters per row. Malformed additions reject atomically; old archives may omit the ledger.
* An older schema-8 app can retain optional history without updating it. A real current -> older app -> current roundtrip left samples at 90/180, then the original recorder produced 180/360 and invalidated its own new save. A missing quarter now starts one fresh sample; the next consecutive quarter restores a valid comparison. Repeated same-day recording replaces its sample. The UI reports the actual latest sample rather than claiming that a late imported town first recorded on day 90.
* Independent phase observations caught a stale spatial membership snapshot at day 180: one block actually contained 25 residents in nine occupied buildings, while the cached snapshot supplied 23/eight. The recorder now counts authoritative buildings, household home assignments and firm staffing directly, without invalidating or recomputing the economic spatial cache. Existing economic decisions remain unchanged. The planning-review phase is the observation time; this is not a claim of an end-of-day census or policy causation.
* The inspector now includes working-age residents from age 16, consistent with the model, and separates recorded public crew employment from residents without a job record. Controlled record toggles are restored completely and pay no money or create jobs.

All earlier passes and these negative counterexamples are preserved. In particular, a passing owner UI test did not override the independently failing older-app archive or phase-count oracle.

## Data and cost contract

Snapshots contain residents, distinct occupied residential building IDs (`occupiedHomes`, not apartment-unit capacity), attending firm workers and job capacity. They contain no person identities, cash or goods and retain only the last two consecutive observations. The inspector derives current destinations and shop reach from existing records; reach is not a purchase, affordability or job promise. Medical/school buttons enter the existing read-only maps.

Two complete 256-block records with maximum admitted counters serialize to 51,630 UTF-8 bytes; canonical keys and exact numeric fields bound this ledger conservatively below 64 KiB. Twelve malformed cases reject without changing the live archive. This is not a total application byte/node budget or unlimited save-safety guarantee.

An independent algorithm captures actual quarter-phase records from the pre-history model. Fifteen complete-state comparisons across settlement, regional and industrial towns through 360 days match the entire expected model, including the explicitly constructed new ledger, with zero omitted fields. The four-scenario 180-day growth comparison and creator-cap 90-day comparison likewise include the independently expected optional ledger rather than dropping it from comparisons.

Across the three yearly journeys, four quarterly updates (each deliberately captured twice to check coalescing) consumed at most 1.6 ms total in diagnostic host timers and caused zero additional spatial-cache builds. One hundred inspector projections took 1.3 ms in that sample and preserved the complete archive/RNG. These are bounded host diagnostics under test load, not device/FPS guarantees. A separate seven-repeat alternating 90-day whole-step comparison against public `669c908` used the same 765-person archive and paused clock, including a quarterly capture: medians were 2,650.0 ms versus 2,641.1 ms (about -0.34%), with 107 cold spatial builds in both. This small difference sits within observed run variation; no optimization or device-performance improvement is claimed. Reproduce with `TOWNLEDGER_PROFILE_BASE=669c908706af997375680674390e46fd132a970a TOWNLEDGER_PROFILE_DAYS=90` and the documented HTTP adapter. Portrait and landscape controls were exercised, with stable screenshots after transient toast dismissal and usable map buttons. Existing Canvas art is not visually accepted by these checks.

## Full composed source

Forty functional scripts pass on the final game and native sources. The full release suite then passes separately with `TOWNLEDGER_CORE_ONLY` absent: **115 simulated years**, 885.52 seconds on this host, maximum recorded money drift **$0.000180323**, and no browser errors.

| Scenario | Years | Final population | Person records | Household records | Firm records | Archive UTF-8 bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Settlement | 50 | 1,028 | 1,252 | 366 | 129 | 2,537,623 |
| Frontier | 25 | 388 | 491 | 149 | 75 | 1,517,413 |
| Industrial | 25 | 418 | 479 | 148 | 49 | 1,413,270 |
| Hard times | 10 | 262 | 283 | 89 | 33 | 900,380 |
| Regional | 5 | 997 | 1,003 | 400 | 120 | 1,752,920 |

The terminal verifier adds a 42nd passing acceptance script. It executes real bounded `ArchiveIO` UTF-8 read/decode/encode/write roundtrips on all five generated towns and checks complete cold state plus warm-to-cold 30-day continuation. Actual history occupies only 2,113–5,558 bytes in these terminals.

Raw byte-identical cold state does not hold in two terminal towns because of the already documented tenancy projection. Settlement has two unit-list index reorderings. Regional has 15 unit-list index reorderings plus the apartment primary-tenant alias at building ID 214 changing from 288 to the minimum resident ID 120. Every household home assignment, member, owner/title, balance, cargo, service receipt, RNG and visual field is preserved. Both pre-history and current loaders produce the exact same full state; the archive module is byte-identical. An independent reconstruction predicts every projection value, with no ignored fields. Subsequent cold state is idempotent and warm/cold continuation matches completely under that same explicit contract. Exact paths/values are retained in `terminal-cold-transport.json`.

The five terminal archives are generated solely by the public seeded test driver, compressed reproducibly, and contain no user saves or credentials. See `evidence/neighborhood-history-integration/` for manifests, all final gate logs, full-release results, generated fixtures, schema/cost oracles and negative receipts.

## Remaining acceptance

No renderer, Worker/cooperative simulation, experimental codec or generic admission owner is enabled. Current APK build and actual provider/process-death verification remain required after the native Back correction; this environment has no SDK/device. The original async parser's duplicate nested-result limitation remains a separate endpoint-activation gate. No modern-WebView, physical-device, selected Newfoundland visual fidelity, interactive device performance, signing or release acceptance is claimed. Parent owns integration promotion.
