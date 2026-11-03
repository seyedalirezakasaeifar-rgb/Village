# Road-quality cache integration

Applied `c20f33c` after the scalable-budget integration `09e1c3b`. The one scalar assignment follows actual pavement maintenance; it changes no routing topology, economic rules, saved fields or RNG calls.

The targeted regression reproduces on the preceding combined source: only `roadMetrics` differs, with96 uninterrupted versus97 restored. On the fixed combined source, both report96 and the complete compared archive is equal; RNG agrees and cash drift is below$0.000001. Core conservation, pause, continuation, cargo, invalid-import and legacy migration gates also pass on the final source.

Source SHA256: `a1b3c7f8bcbf4fab126b31e5180c7186ac8fa024f587e716d16644a7301a54f9`. Full before/after and core receipts are embedded in `reports/integration/8-road-cache-cohort.json`. Prior immutable soak results retain their original source hashes and failures. This checkpoint is ready for fresh strict save acceptance; no one-hour, APK or smoothness pass is claimed. Legacy tenancy and sustained performance remain separately pending.
