# Combined 128-atlas passenger network follow-up

Based on integrated `525e47d`; no earlier transit, urban or art commit is replayed. Production changes are limited to road-distance queries in `60-renderer.js` and their use in `assignJobs` in `20-world.js`. No renderer painting, public/private service economics, construction escrow/staff/wage fields, freight settlement ordering or passenger fares/capacity rules change.

## Profile finding and fix

The large all-owned-atlas profile identifies a separate simulation hitch: hiring calls reconstructed complete road paths for every applicant/workplace pair. The 3,000-pair cache periodically cleared, while the 96 source-path trees churned across applicants. A weekly hiring pass reached 156.8 ms near / 116.1 ms at overview zoom. `routeBetween` had about 797 ms self time in the eight-second near profile. This is not vehicle drawing or a cold elevated-route animation.

`roadDistancesFrom(start, net)` now caches exact BFS distance arrays on the current graph. A hiring pass obtains one destination tree per workplace and reads candidate distances directly. The generic `roadDistance(a,b)` also reuses an existing endpoint tree, with a repeated-origin preference when neither endpoint is cached. It never reconstructs a route merely to count its tiles. Actual visual/freight `routeBetween` paths, neighbour order and route selection are untouched.

The distance cache has an LRU bound of 32 arrays. At this 128 atlas, its arrays use signed 16-bit distances because the physical road graph has fewer than 32,768 nodes; larger graphs automatically use 32-bit distances. The additional cache is bounded to 1 MiB on the current atlas. New graph identity on street/footprint edits, demolition, construction, import or rollback drops the old distance arrays. It contains no accounts or saved state. No ownership boundary or passenger-only freight shortcut is introduced.

With the same profiling harness, hiring maxima fell to 5.3 / 6.9 ms; inclusive hiring totals fell from 812.9 ms in 99 calls to 64.0 ms in 106 calls near, and 771.6/99 to 70.0/108 at overview. `routeBetween` self time fell to about 62 ms. Actual passenger operation already peaked below 9 ms in the original profile and remains below that bound; no claim is made that the passenger algorithm caused the whole old stall.

## Exact and consequential verification

`test_road_distance_cache.py` retains the original distance and hiring functions as independent oracles. It compares every serialized economic/model field at monthly checkpoints over a normal 360-day replay and a dense/all-owned/networked 180-day replay, including wages, staff, fares, cargo, stocks, jobs and RNG. All fields match exactly. It also checks 72,000 sampled road pairs against the original path-based implementation across original and rebuilt/disconnected graphs, checks the cache bound and verifies queries do not write economic state.

`test_transit_combined_redevelopment.py` uses real existing people, firms, property and cash. It authors a long assignment by exchanging two existing workers, then funds an actual bus → elevated-rail transfer. The person buys exactly one $1.25 settled ticket. All 21 deed purchases preserve that paid network and cargo. A broken rail alignment suspends rail and visual trains; an interrupted save restores; paid street reopening restores service. A different bus street closure chooses a real alternate route and then returns to the original route after reopening.

The same case commissions a real reserved municipal dwelling, uses the actual inspector/confirmation clearance buttons to compensate and relocate a household, constructs a clinic on the acquired home plot, and verifies retained identities and exact 30-day save continuation. Routed and suspended stations and the depot resist generic demolition. Explicit route retirement, vehicle sale, unused station/depot salvage and guideway decommissioning work exactly once, conserving cash. Final town and goods accounts are valid.

Joint 56/80 → 128 migration, pre-/post-adoption atomic rejection, retained settled fares/IDs/offsets, existing transit capacity/transfer accounting and core release gates also pass on the final source. No new transport modes or free school/clinic reach were added.

## Cold and live UI measurements

`test_transit_cold_start.py` restores an operating three-route city with all deeds, then exercises 5,000 road/passenger queries. The cache fill changes no economic state and cannot settle fares twice. The near cold query pass measured 18.5 ms; overview 7.2 ms. The 32 road trees, 94 origin trees and 1,974 itinerary templates remain within their independent bounds. Real restore + Public Works + next-frame response measured 97.5 ms near and 69.9 ms at overview, with unchanged paid cash. Graph adoption occurs inside restore; its cost is included in the panel synchronous timing rather than the separately reported post-restore `graphMs`.

The unchanged live dense-network gate passes with requested 64×: near 313 days/8.05 s (about 64×), draw P95 21.1 ms, RAF P99 100 ms; overview 301 days/8.03 s (about 61.9×), draw P95 37.2 ms, RAF P99 183.3 ms. All three routes operate; all recorded UI next-frame responses are below 150 ms. The existing dense fixture begins with 2,000 resident accounts and constructs outer homes while authoring relocation, so its post-authoring population is 2,058; receipts record the actual population. It is a conserved stress fixture, not an unassisted playthrough or demand calibration.

**Remaining CPU hitch:** monthly private-service investment still takes roughly 130–197 ms in instrumented samples, mainly site/household forecast scans and associated planning work. This phase does not change that economic code; the lead should coordinate its optimization separately. Improved hiring and RAF P99 do not eliminate these worst monthly stalls. Graphics remains owned by the graphics worker, and these measurements do not assert device FPS.

## Reproduction and evidence

Final bundle SHA-256: `ad8161fcba0ea7c01ec5db58002025e5d2eb6a5ecd4e1d8d043de1e2d50fc29e`. Raw before/after phase profiles, actual live near/far receipts, cold UI results, complete-model oracle results and combined redevelopment/migration/core results are committed in `docs/previews/transit-combined8/`. The QA profiler is opt-in code under `tools/`, never loaded by the shipped application. The production bundle should be regenerated after cherry-picking the scoped source changes onto any newer lead checkpoint. No deployment, signing or APK action was taken.
