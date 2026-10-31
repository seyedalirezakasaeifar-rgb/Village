# Root cause and scoped continuation fix

Base `03cb54675880a9b60c0c8d8de5dd0b671d0abff3`; no incoming urban trajectory or
private-proposal optimization was present on the remote integration head when
this patch was prepared. Production changes touch only the cache key at the top
of `src/27-urban-evolution.js` and the assembled bundle. Save validators, tenancy
repair, private proposals and economic equations are unchanged.

Paired instrumented seed-8142026 traces locate the first causal difference at
**day 103, `urbanRentMultiplier`, home 46**. The uninterrupted multiplier is
1.1138333333333332; restored is 1.1143333333333334. Every current enterprise job
count agrees, but cached local work is 1.2799999713897705 versus 1.340000033378601.
The immediately preceding `fundCivicServices` stage has identical financial state
checksum `bef5987e` and RNG `1043491905` in both runs. The rent function consumes no
randomness. Later bank, shop and inventory divergence follows the changed rent.

`urbanSpatial` was caching these economic inputs for a whole 30-day period even
though enterprise staffing changes every 14 days. Hydration correctly discarded
the derived cache and rebuilt it using current jobs, while uninterrupted play kept
stale jobs. This does not originate in reserved housing or missing RNG state.
Preserving public/private provision caches was independently tested and did not
resolve it.

The minimal fix keys the existing cache by simulation day instead of 30-day period.
It still reuses one spatial field throughout the day and retains graph, building
count and urban revision guards. It changes no balances, saved fields, thresholds,
RNG or archive schema. District hysteresis/review cadence remains unchanged.

Evidence under `docs/previews/save8/cache-fix/` includes the paired first call and
before/after regression. `tests/test_save_urban_cache.py` primes the spatial field,
uses actual `planEnterprise` to raise a shop's jobs from two to three, saves, and
compares every persisted field (excluding presentation traffic/visual state) after
three uninterrupted versus restored days. The old source fails with identical RNG;
the fixed source is exactly equal. No canonical assertion was weakened.

Fixed assembled SHA-256:
`d187f0cb9eca7d7eaa34b43dca354b9158eb68eb31336d889471095a73fb08e3`.
Core release gates and the urban migration/demolition/mall/two-1080-day gate pass.
The original randomized sequence now passes its formerly failing day-102 plus
nine-days replay. Eleven replay checks and eighteen cold reloads passed before a
later cold Continue timed out around day 183; that negative is retained separately
in `sequence-partial.json`. It is not called a three-minute or one-hour pass. The
newly reported reserved-tenancy bug is a candidate for that later rejection and
requires its own exact validator diagnosis.

A second HTTP-origin 2,000-resident performance check completed 317 days in 8.03s,
with RAF P99 66.7ms and all existing UI/render/throughput limits passing. The first
concurrent-test sample also passed but had RAF P99 466.6ms; both results are retained
rather than hiding contention. These are host measurements, not Android FPS.

The legacy fixture `v60-distressed-town.json` already contains six cottages with
two occupied households each (building IDs 86,85,58,64,70,113). Therefore simply
rejecting every duplicate cottage tenancy will reject an authentic currently
supported legacy archive. No tenancy validator has been changed in this patch.
A repair/rejection API needs to preserve those families and their wallets and
coordinate with the balance worker's live tenancy correction before editing
`src/90-archive-panels.js`.
