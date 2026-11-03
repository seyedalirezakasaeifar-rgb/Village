# Bounded compact road-distance cache

## Cause and change

The representative late-session CPU trace on `31987fc` attributed 16.39 seconds of a 30-second trace to `roadDistancesFrom`, including passenger, commute and export callers. The former 32-tree cache stores a whole atlas-sized distance array per root. Repeated passes over more roots evict useful work despite unchanged roads.

The new cache indexes actual road nodes and runs BFS over pre-indexed adjacency with a reusable typed queue. Compact rows share a strict **4 MiB byte budget**. The existing tile-indexed API remains compatible, with its separate **32-row bound** (at most 1 MiB at 128²). Index/queue/adjacency storage is additional, bounded by road count; the 4 MiB figure is not a claim for total graph memory. Invalid roots are never retained. A new graph owns a new cache, so road edits, town replacement and building/topology invalidations cannot reuse another graph's distances.

No route ordering, route reconstruction, economic decisions, RNG, cargo timing or simulation frequency changes. Endpoint symmetry remains valid for the existing undirected road graph.

## Exact-source evidence

`assets/game.js`: `7f09488dc346be1a9dd1a08a03119fbcbd6fd211e2b47e963d6beae1fc5cf851`.

[Query receipt](../../reports/integration/adaptive-road-distance-8/queries.json): exact chain-distance oracle and repeated household/workplace queries rebuild 129 compact rows versus 257 original rows, with identical sums. A 512-root repeated sweep retains 512 rows in 2 MiB rather than thrashing the 32 expanded rows. The full-grid saturation case reaches exactly 4 MiB and evicts 32 rows; 1,000 invalid-root queries add no retained entries. Explicit topology invalidation drops the prior cache. These are constructed cache tests, not the retained late town.

[Regression receipt](../../reports/integration/adaptive-road-distance-8/regressions.json): 360 normal days and 180 dense-network days match the original distance/hiring model at every 30-day checkpoint, plus 72,000 exact distance comparisons including rebuilt/disconnected networks. Core release gates and composite cargo/transit/provider/mall save and atomic rejection checks pass on the same source.

## Required retained late-town repeat

The performance executor retains `/tmp/townledger-31987fc-late.json`, checkpoint SHA256 `ad6256fd85d4146fda9eeac0b16d5b182ed352c23bbd96af3b320553c29ce786`. That archive is **not present in this integration executor**. Do not publish it or substitute an early fixture while claiming late-town acceptance.

`tools/profile_distance_workload_8.py` derives from the performance worker's retained-town driver and adds cache hit/build/eviction/graph-count/byte counters. Both baseline and candidate smoke paths were exercised using a separate disposable generated town. Run sequentially without competing benchmarks in the executor holding the original checkpoint:

```sh
LATE_CHECKPOINT=/tmp/townledger-31987fc-late.json LATE_SECONDS=30 LATE_CPU=1 LATE_DISTANCE_BASELINE=1 LATE_LABEL=original-cache python tools/profile_distance_workload_8.py
LATE_CHECKPOINT=/tmp/townledger-31987fc-late.json LATE_SECONDS=30 LATE_CPU=1 LATE_LABEL=compact-cache python tools/profile_distance_workload_8.py
DISTANCE_CHECKPOINT=/tmp/townledger-31987fc-late.json python tests/test_road_distance_cache.py
```

The baseline flag replaces only distance functions with the original implementation from `cc86311`, leaving the latest model/rendering in place. Receipts explicitly mark that instrumentation; assembled-source hash alone does not identify the baseline override. Both performance runs must report the identical checkpoint hash. Compare cache counter differences between initial/end states (initial restore can warm caches), CPU attribution, actual simulation rate, RAF tails and trusted-input latency. The last command compares 180 days of full model continuation from the same retained archive against the original distance/hiring oracle. It also runs distance/island checks afterward.

Until those results arrive, this is an exact-equivalent bounded candidate, **not proof that long-session frame pacing is solved**. Cooperative scheduling remains independent and disabled here. Current-source Android acceptance remains required.
