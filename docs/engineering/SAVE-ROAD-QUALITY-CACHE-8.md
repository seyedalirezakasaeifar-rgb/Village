# Second strict acceptance failure: cached road-quality metadata

The requested one-hour run on immutable `31987fcbe108e9d9cb8ed7ce4155f51cd234ba62`
(source `d90bb509173a803b75c3cdc432fea57ce2f1e2abbcb13b8886c56d8feaffe515`)
terminated FAILED at 78.45 seconds / 55 completed operations. It did not pass one
hour. Evidence is retained in `docs/previews/save8/road-cache/` and full generated
snapshots remain private under `/workspace/scratch/save-acceptance-31987fc`.

The exact replay failure is day 117 plus one day. The only changed exported field
is `roadMetrics.quality`: uninterrupted 96 versus restored 97. Every authoritative
record, `stats`, money and goods history agrees; there is no demonstrated economic
or monetary divergence. The archive entered the replay with `roadMetrics: null`
after ordinary topology invalidation. Hydration filled the cache immediately at
quality 97. Road maintenance then lowered the actual condition to 96. Uninterrupted
play first filled the absent cache after maintenance (96); restored play retained
the old scalar quality (97) because the expensive road metric refresh is periodic.

The scoped fix synchronizes only an existing cache's `quality` immediately when
`maintainRoads` publishes its new road condition. No graph rebuild, extra routing,
economic rule, RNG call, field removal or assertion change is introduced. It is
one O(1) assignment plus explanatory comment in `src/60-renderer.js`; draw code is
unchanged. `src/90-archive-panels.js` and legacy-tenancy policy remain untouched.

`tests/test_save_road_cache.py` advances a real seeded town to day 117, sets the
physical pavement just above a rounding boundary, invalidates the network cache,
and compares all exported fields except existing visual/traffic state after one
uninterrupted versus restored normal clock tick. The old source fails only the
quality field; the fix is exactly equal with identical RNG and conserved cash.
This is a source correction, not a relaxed canonical comparison.

Fixed assembled SHA-256:
`dabe130a976283b8db40d37f71c449f33b588b726d5695bcd11330251d7fe0b7`.
Core gates passed. The seed-8142026 bounded sequence terminated successfully
after 182.02 seconds: 132 operations, 40 cold reloads and 11 exact continuation
checks through day 332, with zero JavaScript/replay failures. All system-specific
archive validators, actual household capacities, cash/goods/ID invariants and
archive bounds passed. Final asset-manifest checks and process exit code 0 were
confirmed. Full trace, final source/driver/asset hashes and terminal receipt are
retained beside the negative evidence. This is a three-minute result, not a
one-hour pass. The lead's next immutable combined checkpoint is still required
for a fresh full one-hour gate.
