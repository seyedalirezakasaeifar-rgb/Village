# Fresh initialization and cold Continue coherence

Base `7500d878`, independent of experimental codec and capacity candidates. Native report `3447fe90da80319ff7020154e38b6d2684538cca` on f93a87ca found regionalTrade absent→object and roadMetrics object→null across process-death Continue. Its failed strict comparison remains valid evidence; no person fields differed and no financial loss was established.

A host reproduction on an actual HTTP origin saved a fresh town with four live traffic vehicles, reloaded the page and used the real Continue handler. It confirmed both native differences and an additional loss of all four restored vehicles. The test freezes simulation immediately after the real Continue body to compare a completed state, and compares EVERY canonical field, including visual/traffic snapshots. It does not delete fields from comparison.

Fresh seeding now initializes the existing regional-trade state before first save, making overview rendering idempotent with respect to this default. Continue now invalidates road caches without clearing restored traffic, then rebuilds only the road metrics it invalidated. A broad recompute here is unsuitable: it replaces the whole stats object and drops the separately hydrated approval field. The scoped cache rebuild preserves that field and avoids model-wide normalization.

Before source SHA `98ab6d44286d2d6300c4533d70e10819a5c102ebfc6e6a09be61b87115883388`: three strict differences; four vehicles→zero. Fixed source SHA `4a8c523a9dda013810784dc3b9a2a116c0992c0b143ed2990eba781e4173c9c6`: exact whole-state equality, four vehicles→four.

Passed `python tools/assemble.py`, `python tests/test_cold_continue_canonical.py` and default core release gates with `TOWNLEDGER_CORE_ONLY=1 TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter python tests/test_release.py`. Before evidence was produced with `NATIVE_CANONICAL_EXPECT_FAIL=1`. Reports contain only field differences and hashes, no complete saves.

Actual Android process-death revalidation on the integrated fix remains pending with the native owner. This host result does not certify physical-device latency. Native measured 8001-identity encode/decode times remain a separate experimental-codec activation concern. No codec is activated or modified by this patch.

Persistence contract: `regionalTrade` is authoritative model state (cargo, contracts, claims and accounting), initialized once by its existing versioned initializer during seeding and hydration of missing legacy state. Existing nonempty trade state is never replaced by a default. Missing legacy state is a documented normalization at initial adoption, before producing a new canonical save. The regression then enters overview without changing that initialized model.

`roadMetrics` is a persisted derived snapshot of the road topology, building/household access and authoritative `G.stats.roadCondition`; it is not a second account or source of truth. Continue rebuilds this invalidated snapshot deterministically before overview/save eligibility. Restored traffic vehicles, clocks and gates remain intact. The full canonical comparator retains roadMetrics and regionalTrade; no field is excluded. Core replay independently passed same-seed/render independence and 120-day continuation after the final initialization change.
