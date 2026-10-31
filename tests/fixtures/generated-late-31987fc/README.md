# Generated late TownLedger test cities

These are **generated QA towns, not real user saves**. They contain only the game's simulated people, companies, financial history and map. The starting settlement uses shipped seed 42 and the existing synthetic 2,000-resident fixture. Actual region-funded deeds/routes/providers were added through the QA fixture, followed by the recorded 45-minute real-RAF session with automatic development, private entry, music, inputs, saves and current-town imports enabled. No real account, signer, credential, email, private correspondence or user save is included. The parent explicitly authorized sharing these generated fixtures as project test evidence.

`manifest.json` records the source commit/hash, uncompressed and compressed checksums, exact embedded day and workload dimensions. The terminal fixture is only about 510 KB compressed (3.66 MB uncompressed); the mid-session fixture is about 388 KB compressed. They are unmodified model snapshots, not simplified grids or financial rebalancing scenarios.

- `terminal.json.gz`: exact archived day **41,681**, population 778, 3,108 historical people, 876 households, 797 buildings, 81 firms, 48 total routes. The economy legitimately had only nine operating routes near the end; do not replenish those routes or disable growth to make the workload easier.
- `mid-session.json.gz`: archived day **15,561**, population 1,848, 2,346 people, 725 households, 750 buildings, 37 firms, 48 routes. This is close to the earlier bounded component trace.

The original recorder queried live day separately after serializing its terminal checkpoint, producing a metadata observation of 41,683. The payload itself is day 41,681; its original hash `ad6256fd85d4146fda9eeac0b16d5b182ed352c23bbd96af3b320553c29ce786` is unchanged. Use the manifest/payload day as authoritative.

## Reproduction

From a checkout containing source commit `31987fcbe108e9d9cb8ed7ce4155f51cd234ba62`:

```sh
python tools/trace_late_distance_cache.py
```

The tool verifies both compressed and raw hashes, extracts the approved synthetic archive into `/tmp`, imports it through the real archive entry point, and measures a bounded actual evolving session with audio/input/cargo/transit retained. It observes queries/cache behavior without replacing routing or model logic. `LATE_FIXTURE=mid-session` selects the other checkpoint; `LATE_SECONDS=24` controls the bounded minimum window. The shared runner emits full source/checkpoint-bound state and invariants. Derived caches are rebuilt by normal import; no historic in-memory cache object is falsely treated as persisted state.

For an ordinary retained-town CPU or timing profile, first extract the fixture to `/tmp`, then use `tools/profile_late_session_8.py` with `LATE_CHECKPOINT` pointing at it. This avoids committing raw working copies:

```sh
gzip -dc tests/fixtures/generated-late-31987fc/terminal.json.gz > /tmp/townledger-terminal-generated.json
LATE_CHECKPOINT=/tmp/townledger-terminal-generated.json LATE_CPU=1 LATE_SECONDS=30 python tools/profile_late_session_8.py
```

The cache counter probe is bound to the original 32-tree cache policy; if that policy/interface is changed, update its eviction accounting before treating it as a candidate-cache acceptance test. The fixture and ordinary profiler remain useful for exact-town comparisons on new sources.

## Actual late-workload evidence

`reports/session-performance/late-attribution/terminal-cache-summary.json` is the compact cache receipt. The full `terminal-cache.json` adds per-scope anchor IDs and bounded endpoint/query samples. The CPU trace and caller aggregation are in `terminal-cpu.cpuprofile.gz` / `road-distance-caller-attribution.json`.

The cache run records 1,698,185 distance queries, 1,698,244 tree accesses, **66,545 misses and 66,417 evictions**, with four graph populations. Transit operations alone use 82 distinct anchors, miss 34,544 times and spend about 8.54 seconds building missed trees. Worker commute queries use 68 anchors and miss 16,238 times (about 3.97 seconds); exports use 36 anchors and miss 6,999 times (about 1.82 seconds). The aggregate hit rate therefore hides expensive cross-consumer cache turnover.

Three explicit urban-evolution invalidations occurred in this diagnostic, with unchanged 5,666 road-node count. Equal node counts do not establish that an invalidation is unnecessary: building portals/footprints and network membership may still change. Preserve correctness and inspect the actual graph/consumer contracts before altering invalidation behavior. The economics/transit owners retain the fix; this evidence contains no routing production change or claimed Android smoothness result.
